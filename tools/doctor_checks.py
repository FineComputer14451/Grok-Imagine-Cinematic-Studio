"""Individual Grok Doctor checks (pure-ish functions returning CheckResult lists)."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from doctor_aup import check_aup as check_aup
from doctor_types import CheckResult
from models import (
    DEFAULT_XAI_CHAT_MODEL,
    GROK_BUILD_FORK_MODEL,
    RECOMMENDED_GROK_BUILD_CLI_VERSION,
    cli_version_at_least,
    known_chat_model,
    model_stack_summary,
    probe_grok_cli,
    resolve_chat_model,
    verify_model_compatibility,
)
from plugin_catalog import check_plugin_artifacts, validate_release_pin
from studio_health import (
    count_skills,
    skills_missing_model_compatibility,
    studio_version,
    user_skill_names,
    user_studio_skill_dupes,
)
from studio_paths import PLUGIN_MARKETPLACE_PATH, STUDIO_ROOT

# Heuristic: user-skill clutter above this with no studio dupes is still informational.
_USER_SKILLS_INFO_OK = 15

# Method A core (verify tier) — present in ~/.grok/skills after meta install/update.
METHOD_A_CORE_SKILLS = (
    "grok-imagine-cinematic-studio",
    "ai-video-upscaler",
    "cinematic-sequence-extender",
    "studio-director",
    "quality-assurance-guardian",
    "identity-lock-specialist",
    "workflow-quota-optimizer",
)


def method_a_core_installed(home: Path | None = None) -> bool:
    """True when Method A copied the seven core skills into ~/.grok/skills."""
    base = (home if home is not None else Path.home()) / ".grok" / "skills"
    return all((base / slug / "SKILL.md").is_file() for slug in METHOD_A_CORE_SKILLS)


def cinematic_plugin_listed() -> bool:
    """True when `grok plugin list` includes grok-imagine-cinematic-studio."""
    if not _which("grok"):
        return False
    try:
        listed = _run(["grok", "plugin", "list"], timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return False
    blob = f"{listed.stdout or ''}{listed.stderr or ''}".lower()
    return "grok-imagine-cinematic-studio" in blob

# Catalog errors that are "mid-work pin drift" (WARN) vs hard artifact breakage (FAIL).
_PIN_DRIFT_MARKERS = (
    "content changed after marketplace pin",
    "is not an ancestor of head",
    "re-run: cinematic-studio plugin catalog pin",
)


def _which(cmd: str) -> str | None:
    return shutil.which(cmd)


def _run(
    argv: list[str],
    *,
    cwd: Path | None = None,
    timeout: float = 120,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd else None,
        timeout=timeout,
        check=False,
        env=env,
    )


def _load_toml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        import tomllib

        with path.open("rb") as fh:
            data = tomllib.load(fh)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _is_pin_drift_error(message: str) -> bool:
    lower = message.lower()
    return any(marker in lower for marker in _PIN_DRIFT_MARKERS)


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


def check_grok_cli(*, min_version: str = RECOMMENDED_GROK_BUILD_CLI_VERSION) -> list[CheckResult]:
    """Probe grok binary once; enforce min version from the model registry."""
    section = "1. Grok Build CLI"
    probe = probe_grok_cli()
    path = probe.get("path")
    if not path:
        return [CheckResult("FAIL", "grok binary", "not on PATH", section)]

    display = probe.get("display") or "found"
    results = [CheckResult("PASS", "grok binary", f"{display} ({path})", section)]

    installed = probe.get("version")
    if not isinstance(installed, str):
        results.append(
            CheckResult(
                "FAIL",
                "grok CLI min version",
                f"could not parse version from {probe.get('raw')!r}; need ≥ {min_version}",
                section,
            )
        )
        return results

    try:
        ok = cli_version_at_least(installed, min_version)
    except ValueError:
        results.append(
            CheckResult(
                "FAIL",
                "grok CLI min version",
                f"invalid version {installed!r}; need ≥ {min_version}",
                section,
            )
        )
        return results

    if ok:
        results.append(
            CheckResult("PASS", "grok CLI min version", f"{installed} ≥ {min_version}", section)
        )
    else:
        results.append(
            CheckResult(
                "FAIL",
                "grok CLI min version",
                f"{installed} < {min_version} (upgrade Grok Build)",
                section,
            )
        )
    return results


def check_cinematic_studio_path(*, repo_root: Path | None = None) -> list[CheckResult]:
    """PATH presence + in-process VERSION (no nested cinematic-studio spawn)."""
    section = "1. Grok Build CLI"
    path = _which("cinematic-studio")
    root = repo_root if repo_root is not None else STUDIO_ROOT
    ver = studio_version(root) or "?"
    if not path:
        return [
            CheckResult(
                "WARN",
                "cinematic-studio",
                f"not on PATH (studio v{ver}; run install or add ~/.grok/bin)",
                section,
            )
        ]
    return [
        CheckResult(
            "PASS",
            "cinematic-studio",
            f"on PATH ({path}) · studio v{ver}",
            section,
        )
    ]


def check_auth_and_config(
    *,
    home: Path,
    expected_default: str = DEFAULT_XAI_CHAT_MODEL,
    expected_fork: str = GROK_BUILD_FORK_MODEL,
) -> list[CheckResult]:
    section = "2. Auth & config"
    results: list[CheckResult] = []
    auth = home / ".grok" / "auth.json"
    if auth.is_file():
        results.append(CheckResult("PASS", "auth.json", "present", section))
    else:
        results.append(
            CheckResult("FAIL", "auth.json", "missing — run grok login / authenticate", section)
        )

    cfg_path = home / ".grok" / "config.toml"
    if not cfg_path.is_file():
        results.append(
            CheckResult(
                "WARN",
                "config.toml",
                "missing — optional; copy config/grok-build.example.toml",
                section,
            )
        )
        return results

    results.append(CheckResult("PASS", "config.toml", "present", section))
    cfg = _load_toml(cfg_path)
    models = cfg.get("models") if isinstance(cfg.get("models"), dict) else {}
    ui = cfg.get("ui") if isinstance(cfg.get("ui"), dict) else {}
    default = models.get("default")
    fork = ui.get("fork_secondary_model")

    default_ok = default == expected_default
    if not default_ok and default:
        try:
            default_ok = (
                known_chat_model(str(default))
                and resolve_chat_model(str(default)) == expected_default
            )
        except Exception:
            default_ok = False
    if default_ok:
        results.append(CheckResult("PASS", "models.default", str(default), section))
    elif default is None:
        results.append(
            CheckResult(
                "WARN",
                "models.default",
                f"not set (expected {expected_default})",
                section,
            )
        )
    else:
        results.append(
            CheckResult(
                "WARN",
                "models.default",
                f"{default!r} (expected {expected_default})",
                section,
            )
        )

    acceptable_forks = {expected_fork, expected_default, "grok-4.6", "grok-build"}
    if fork in acceptable_forks:
        results.append(CheckResult("PASS", "fork_secondary_model", str(fork), section))
    elif fork is None:
        results.append(
            CheckResult(
                "WARN",
                "fork_secondary_model",
                f"not set (expected {expected_fork})",
                section,
            )
        )
    else:
        results.append(
            CheckResult(
                "WARN",
                "fork_secondary_model",
                f"{fork!r} (expected {expected_fork})",
                section,
            )
        )
    return results


def check_versions(
    *,
    repo_root: Path,
    project_dir: Path,
) -> tuple[list[CheckResult], str, str]:
    section = "3. Studio VERSION"
    results: list[CheckResult] = []
    repo_v = studio_version(repo_root) or "?"
    proj_v = studio_version(project_dir) or "?"

    if repo_v != "?":
        results.append(CheckResult("PASS", "repo VERSION", f"{repo_v} ({repo_root})", section))
    else:
        results.append(
            CheckResult(
                "WARN",
                "repo VERSION",
                "checkout not found (set CINEMATIC_REPO_ROOT)",
                section,
            )
        )

    if proj_v != "?":
        results.append(
            CheckResult("PASS", "PROJECT_DIR VERSION", f"{proj_v} ({project_dir})", section)
        )
        if repo_v != "?" and repo_v != proj_v:
            results.append(
                CheckResult(
                    "WARN",
                    "VERSION drift",
                    f"repo={repo_v} project={proj_v} — run cinematic-studio update",
                    section,
                )
            )
    else:
        results.append(
            CheckResult(
                "WARN",
                "PROJECT_DIR VERSION",
                "Method A project missing — optional if plugin-only",
                section,
            )
        )
    return results, repo_v, proj_v


def check_model_stack() -> list[CheckResult]:
    """Use verify_model_compatibility; operational warnings only (not notes)."""
    section = "4. Model stack"
    try:
        result = verify_model_compatibility()
    except Exception as exc:  # pragma: no cover — defensive
        return [CheckResult("FAIL", "models verify", f"exception: {exc}", section)]

    stack = result.get("model_stack") or model_stack_summary()
    stack_detail = (
        f"chat={stack.get('xai_chat')} build={stack.get('xai_build')} "
        f"video={stack.get('imagine_video')} image={stack.get('imagine_image')}"
    )

    results: list[CheckResult] = []
    if result.get("compatible"):
        results.append(
            CheckResult(
                "PASS",
                "models verify",
                (
                    f"compatible (studio {result.get('studio_version')}; "
                    f"CLI {result.get('installed_grok_cli_version') or 'n/a'}) · {stack_detail}"
                ),
                section,
            )
        )
    else:
        issues = result.get("issues") or []
        detail = "; ".join(str(i) for i in issues[:4]) or "incompatible"
        if len(issues) > 4:
            detail += f" (+{len(issues) - 4} more)"
        results.append(
            CheckResult(
                "FAIL",
                "models verify",
                f"{detail} · {stack_detail}",
                section,
            )
        )

    for warning in (result.get("warnings") or [])[:3]:
        results.append(CheckResult("WARN", "models CLI probe", str(warning), section))

    return results


def check_plugin_installed(
    *,
    expected_version: str | None,
    home: Path | None = None,
) -> list[CheckResult]:
    section = "5. Cinematic plugin"
    method_a = method_a_core_installed(home)

    if not _which("grok"):
        if method_a:
            return [
                CheckResult(
                    "PASS",
                    "plugin installed",
                    "Method A skills present (plugin optional; grok not on PATH)",
                    section,
                )
            ]
        return [CheckResult("WARN", "plugin", "skipped (no grok)", section)]

    try:
        listed = _run(["grok", "plugin", "list"], timeout=30)
    except (OSError, subprocess.TimeoutExpired) as exc:
        if method_a:
            return [
                CheckResult(
                    "PASS",
                    "plugin installed",
                    f"Method A skills present (plugin probe failed: {exc})",
                    section,
                )
            ]
        return [CheckResult("WARN", "plugin installed", f"probe failed: {exc}", section)]

    blob = (listed.stdout or "") + (listed.stderr or "")
    if "grok-imagine-cinematic-studio" not in blob.lower():
        if method_a:
            return [
                CheckResult(
                    "PASS",
                    "plugin installed",
                    "Method A skills present (plugin optional)",
                    section,
                )
            ]
        return [
            CheckResult(
                "FAIL",
                "plugin installed",
                "not found — grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio --trust "
                "(or Method A: bash scripts/cinematic_studio.sh install)",
                section,
            )
        ]

    results = [
        CheckResult("PASS", "plugin installed", "grok-imagine-cinematic-studio listed", section)
    ]
    try:
        detail_proc = _run(
            ["grok", "plugin", "details", "grok-imagine-cinematic-studio"],
            timeout=30,
        )
        detail = (detail_proc.stdout or "") + (detail_proc.stderr or "")
    except (OSError, subprocess.TimeoutExpired):
        detail = ""

    skill_match = re.search(r"(\d+)\s+skill dir", detail, re.I)
    if skill_match:
        results.append(
            CheckResult("PASS", "plugin components", f"{skill_match.group(1)} skill dir", section)
        )
    elif detail.strip():
        results.append(CheckResult("PASS", "plugin components", "details available", section))

    if expected_version and detail.strip():
        stamp_ok = (
            expected_version in detail
            or f"v{expected_version}" in detail
            or f"V{expected_version}" in detail
        )
        if stamp_ok:
            results.append(
                CheckResult(
                    "PASS",
                    "plugin version stamp",
                    f"v{expected_version.lstrip('v')}",
                    section,
                )
            )
        else:
            results.append(
                CheckResult(
                    "WARN",
                    "plugin version stamp",
                    f"expected v{expected_version.lstrip('v')} not found in plugin details",
                    section,
                )
            )
    return results


def check_catalog_pin(*, require_release: bool = True) -> list[CheckResult]:
    """
    Hard artifact errors FAIL; pin-drift (content after pin) WARN so mid-work trees work.
    """
    section = "6. Plugin catalog pin"
    if not PLUGIN_MARKETPLACE_PATH.is_file():
        return [
            CheckResult(
                "WARN",
                "catalog pin",
                "skipped (no marketplace.json — not a full checkout)",
                section,
            )
        ]
    try:
        marketplace = json.loads(PLUGIN_MARKETPLACE_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        return [CheckResult("FAIL", "catalog pin", f"cannot read marketplace: {exc}", section)]

    # Split: base artifacts vs release-pin drift
    base_errors = check_plugin_artifacts(marketplace, require_release_pin=False)
    release_errors: list[str] = []
    if require_release:
        release_errors = validate_release_pin(marketplace)

    hard = [e for e in base_errors if not _is_pin_drift_error(e)]
    # Release pin messages are almost always mid-work WARN
    soft = [e for e in base_errors if _is_pin_drift_error(e)] + list(release_errors)

    results: list[CheckResult] = []
    if not hard and not soft:
        results.append(
            CheckResult(
                "PASS",
                "catalog pin",
                "release check green" if require_release else "artifacts up to date",
                section,
            )
        )
        return results

    if hard:
        results.append(
            CheckResult(
                "FAIL",
                "catalog artifacts",
                "; ".join(hard[:3])
                + (f" (+{len(hard) - 3} more)" if len(hard) > 3 else ""),
                section,
            )
        )
    if soft:
        results.append(
            CheckResult(
                "WARN",
                "catalog pin",
                "; ".join(soft[:3])
                + (f" (+{len(soft) - 3} more)" if len(soft) > 3 else ""),
                section,
            )
        )
    return results


def check_skills_layout(*, home: Path, repo_root: Path) -> list[CheckResult]:
    section = "7. Skills layout"
    results: list[CheckResult] = []
    skills_root = repo_root / ".grok" / "skills"
    n = count_skills(skills_root)
    if skills_root.is_dir():
        results.append(CheckResult("PASS", "repo skill dirs", str(n), section))
        missing = skills_missing_model_compatibility(skills_root)
        if not missing:
            results.append(
                CheckResult("PASS", "model_compatibility", "all SKILL.md present", section)
            )
        else:
            results.append(
                CheckResult(
                    "WARN",
                    "model_compatibility",
                    f"{len(missing)} skill(s) missing YAML block",
                    section,
                )
            )
    else:
        results.append(
            CheckResult("WARN", "repo skill dirs", "no .grok/skills in repo root", section)
        )

    user_n = len(user_skill_names(home))
    # Overlap with the repo skill tree is Method A, not dual-install debt, unless
    # the marketplace plugin is also listed (declutter target).
    dupes = user_studio_skill_dupes(home, skills_root) if skills_root.is_dir() else []
    if dupes and cinematic_plugin_listed():
        results.append(
            CheckResult(
                "WARN",
                "user ~/.grok/skills",
                (
                    f"{user_n} dirs; {len(dupes)} studio skill dupe(s) "
                    f"(run cinematic-studio plugin declutter --apply)"
                ),
                section,
            )
        )
    elif method_a_core_installed(home):
        results.append(
            CheckResult(
                "PASS",
                "user ~/.grok/skills",
                f"{user_n} dirs (Method A)",
                section,
            )
        )
    elif user_n > _USER_SKILLS_INFO_OK:
        results.append(
            CheckResult(
                "WARN",
                "user ~/.grok/skills",
                f"{user_n} dirs (high; studio skills should live in plugin after declutter)",
                section,
            )
        )
    else:
        results.append(
            CheckResult(
                "PASS",
                "user ~/.grok/skills",
                f"{user_n} dirs (studio skills should live in plugin after declutter)",
                section,
            )
        )
    return results


def check_verify_plugin(*, repo_root: Path) -> list[CheckResult]:
    section = "8. verify --plugin"
    script = repo_root / "scripts" / "cinematic_studio.sh"
    if not script.is_file():
        return [CheckResult("WARN", "verify --plugin", "skipped (no scripts)", section)]
    try:
        proc = _run(
            ["bash", str(script), "verify", "--plugin"],
            cwd=repo_root,
            timeout=300,
            env={**os.environ, "CINEMATIC_REPO_ROOT": str(repo_root)},
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return [CheckResult("FAIL", "verify --plugin", f"failed: {exc}", section)]
    if proc.returncode == 0:
        return [CheckResult("PASS", "verify --plugin", "passed", section)]
    tail = ((proc.stdout or "") + (proc.stderr or "")).strip().splitlines()
    detail = tail[-1] if tail else f"exit {proc.returncode}"
    return [CheckResult("FAIL", "verify --plugin", detail, section)]


def check_git(*, repo_root: Path) -> list[CheckResult]:
    section = "9. Git"
    if not (repo_root / ".git").exists():
        return [CheckResult("WARN", "git", "not a git checkout", section)]
    try:
        branch = _run(["git", "status", "-sb"], cwd=repo_root, timeout=15)
        describe = _run(["git", "describe", "--tags", "--always"], cwd=repo_root, timeout=15)
        porcelain = _run(["git", "status", "--porcelain"], cwd=repo_root, timeout=15)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return [CheckResult("WARN", "git", f"probe failed: {exc}", section)]

    branch_line = (branch.stdout or "").strip().splitlines()
    tag = (describe.stdout or "").strip()
    summary = f"{branch_line[0] if branch_line else '?'} · {tag or '?'}"
    results = [CheckResult("PASS", "git", summary, section)]
    if (porcelain.stdout or "").strip():
        results.append(
            CheckResult("WARN", "working tree", "dirty (local changes present)", section)
        )
    else:
        results.append(CheckResult("PASS", "working tree", "clean", section))
    return results


def check_api_keys(*, home: Path) -> list[CheckResult]:
    section = "10. API keys (presence only)"
    results: list[CheckResult] = []
    if os.environ.get("XAI_API_KEY"):
        results.append(CheckResult("PASS", "XAI_API_KEY", "set in environment", section))
    else:
        results.append(
            CheckResult(
                "WARN",
                "XAI_API_KEY",
                "unset (API Imagine CLI spend may fail; Build may use auth.json)",
                section,
            )
        )
    secrets = home / ".grok" / "secrets.env"
    if secrets.is_file():
        results.append(CheckResult("PASS", "secrets.env", "present", section))
    else:
        results.append(CheckResult("WARN", "secrets.env", "absent (optional)", section))
    return results


def check_github_cli() -> list[CheckResult]:
    section = "11. GitHub CLI"
    if not _which("gh"):
        return [CheckResult("WARN", "gh", "not installed", section)]
    try:
        status = _run(["gh", "auth", "status"], timeout=15)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return [CheckResult("WARN", "gh auth", f"probe failed: {exc}", section)]
    if status.returncode != 0:
        return [CheckResult("WARN", "gh auth", "not logged in", section)]
    who = "authenticated"
    try:
        user = _run(["gh", "api", "user", "--jq", ".login"], timeout=15)
        if user.returncode == 0 and (user.stdout or "").strip():
            who = user.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return [CheckResult("PASS", "gh auth", who, section)]


def check_control_plane() -> list[CheckResult]:
    """Echo Operator UX control-plane severity + attention count (J1 Orient)."""
    section = "12b. Control plane"
    try:
        from cli.dashboard import build_studio_dashboard
        from cli.tui.widgets import collect_home_alerts, strip_severity
    except Exception as exc:
        return [
            CheckResult(
                "WARN",
                "control plane",
                f"unable to import snapshot helpers: {exc}",
                section,
            )
        ]

    try:
        snap = build_studio_dashboard()
        try:
            from quota_sync import ledger_recon_alignment

            snap["quota_alignment"] = ledger_recon_alignment()
        except Exception:
            pass
        sev = strip_severity(snap)
        alerts = collect_home_alerts(snap)
    except Exception as exc:
        return [
            CheckResult(
                "WARN",
                "control plane",
                f"snapshot failed: {exc}",
                section,
            )
        ]

    n = len(alerts)
    detail = f"severity={sev} · attention={n}"
    if alerts:
        detail += " · " + "; ".join(alerts[:2])
        if n > 2:
            detail += f" (+{n - 2} more)"

    if sev == "critical":
        return [CheckResult("FAIL", "control plane", detail, section)]
    if sev == "warn":
        return [CheckResult("WARN", "control plane", detail, section)]
    return [CheckResult("PASS", "control plane", detail or "severity=ok", section)]


def check_quota_recon() -> list[CheckResult]:
    """Read-only: billable generation ledger totals vs stored reconciliation."""
    section = "13. Quota recon"
    try:
        from quota_sync import ledger_recon_alignment
    except Exception as exc:
        return [
            CheckResult(
                "WARN",
                "quota recon",
                f"unable to import alignment helper: {exc}",
                section,
            )
        ]

    try:
        align = ledger_recon_alignment()
    except Exception as exc:
        return [
            CheckResult(
                "WARN",
                "quota recon",
                f"alignment probe failed: {exc}",
                section,
            )
        ]

    status = align.get("status") or "idle"
    hint = align.get("hint") or ""
    ledger = align.get("ledger") or {}
    snap = align.get("recon") or {}

    if status == "idle":
        return [
            CheckResult(
                "PASS",
                "quota recon",
                hint or "no billable ledger / ledger recon",
                section,
            )
        ]
    if status == "aligned":
        return [
            CheckResult(
                "PASS",
                "quota recon",
                hint
                or (
                    f"aligned cascade={snap.get('cascade_source')} "
                    f"n={ledger.get('entry_count')}"
                ),
                section,
            )
        ]
    if status == "mismatch":
        return [
            CheckResult(
                "WARN",
                "quota recon",
                hint or "ledger totals disagree with stored recon",
                section,
            )
        ]
    if status == "stale":
        return [
            CheckResult(
                "WARN",
                "quota recon",
                hint
                or (
                    f"ledger billable n={ledger.get('entry_count')} but cascade="
                    f"{snap.get('cascade_source')}"
                ),
                section,
            )
        ]
    if status == "orphan_recon":
        return [
            CheckResult(
                "WARN",
                "quota recon",
                hint or "recon claims generation_ledger but ledger has no billable rows",
                section,
            )
        ]
    if status == "mixed":
        return [
            CheckResult(
                "WARN",
                "quota recon",
                hint or "mixed cascade (record_spend over ledger); run quota sync",
                section,
            )
        ]
    return [
        CheckResult(
            "WARN",
            "quota recon",
            f"unknown alignment status {status!r}: {hint}",
            section,
        )
    ]


def check_pytest(*, repo_root: Path) -> list[CheckResult]:
    section = "12. Quick tests"
    tests = repo_root / "tests"
    if not tests.is_dir():
        return [CheckResult("WARN", "pytest packs/agents", "no tests/ directory", section)]
    try:
        proc = _run(
            [
                "python3",
                "-m",
                "pytest",
                "tests/test_plugin_packs.py",
                "tests/test_agents_registry.py",
                "-q",
                "--tb=no",
            ],
            cwd=repo_root,
            timeout=180,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return [CheckResult("FAIL", "pytest packs/agents", f"failed: {exc}", section)]
    tail = (proc.stdout or proc.stderr or "").strip().splitlines()
    detail = tail[-1] if tail else ("passed" if proc.returncode == 0 else "failed")
    if proc.returncode == 0:
        return [CheckResult("PASS", "pytest packs/agents", detail, section)]
    return [CheckResult("FAIL", "pytest packs/agents", detail, section)]
