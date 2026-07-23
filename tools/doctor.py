"""
Grok Doctor — canonical health-check registry for Grok Build + Cinematic Studio.

Single source of truth used by:
  cinematic-studio doctor
  grok-doctor  (thin shell shim)
  python tools/cinematic_studio_cli.py doctor

Reuses models.verify_model_compatibility, studio_health, and plugin_catalog
instead of reimplementing version/config/plugin logic in bash.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Literal

from models import (
    DEFAULT_XAI_CHAT_MODEL,
    GROK_BUILD_FORK_MODEL,
    RECOMMENDED_GROK_BUILD_CLI_VERSION,
    model_stack_summary,
    probe_grok_cli_version,
    verify_model_compatibility,
)
from plugin_catalog import check_plugin_artifacts
from studio_health import (
    count_skills,
    skills_missing_model_compatibility,
    studio_version,
    user_skill_names,
    user_studio_skill_dupes,
)
from studio_paths import PLUGIN_MARKETPLACE_PATH, STUDIO_ROOT

Status = Literal["PASS", "FAIL", "WARN"]

# Heuristic: user-skill clutter above this with no studio dupes is still informational.
_USER_SKILLS_INFO_OK = 15


def _version_tuple(version: str) -> tuple[int, ...]:
    """Parse dotted numeric version for ordering (matches models._version_tuple)."""
    return tuple(int(p) for p in version.split("."))


@dataclass(frozen=True)
class CheckResult:
    status: Status
    name: str
    detail: str
    section: str = ""


@dataclass
class DoctorReport:
    checks: list[CheckResult] = field(default_factory=list)
    repo_version: str = "?"
    project_version: str = "?"
    repo_root: str = ""
    project_dir: str = ""
    quick: bool = False
    started_at: str = ""

    @property
    def pass_count(self) -> int:
        return sum(1 for c in self.checks if c.status == "PASS")

    @property
    def fail_count(self) -> int:
        return sum(1 for c in self.checks if c.status == "FAIL")

    @property
    def warn_count(self) -> int:
        return sum(1 for c in self.checks if c.status == "WARN")

    @property
    def healthy(self) -> bool:
        return self.fail_count == 0


def exit_code(report: DoctorReport, *, strict: bool = False) -> int:
    """Return process exit code for a doctor report."""
    if report.fail_count > 0:
        return 1
    if strict and report.warn_count > 0:
        return 1
    return 0


def report_to_dict(report: DoctorReport) -> dict[str, Any]:
    """Machine-readable summary (stable keys for scripts/CI)."""
    return {
        "pass": report.pass_count,
        "fail": report.fail_count,
        "warn": report.warn_count,
        "repo_version": report.repo_version,
        "project_version": report.project_version,
        "repo_root": report.repo_root,
        "project_dir": report.project_dir,
        "quick": report.quick,
        "started_at": report.started_at,
        "healthy": report.healthy,
        "checks": [
            {"status": c.status, "name": c.name, "detail": c.detail, "section": c.section}
            for c in report.checks
        ],
    }


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


def _default_project_dir(home: Path) -> Path:
    env = os.environ.get("CINEMATIC_PROJECT_DIR", "").strip()
    if env:
        return Path(env).expanduser()
    return home / "Grok-Cinematic-Projects"


def resolve_repo_root(
    *,
    explicit: Path | str | None = None,
    studio_root: Path | None = None,
) -> Path:
    """Prefer explicit env/arg, else the installed tools tree (STUDIO_ROOT)."""
    if explicit:
        return Path(explicit).expanduser().resolve()
    env = os.environ.get("CINEMATIC_REPO_ROOT", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    return (studio_root or STUDIO_ROOT).resolve()


# ---------------------------------------------------------------------------
# Individual checks (return 0+ results)
# ---------------------------------------------------------------------------


def check_grok_cli(*, min_version: str = RECOMMENDED_GROK_BUILD_CLI_VERSION) -> list[CheckResult]:
    section = "1. Grok Build CLI"
    path = _which("grok")
    if not path:
        return [CheckResult("FAIL", "grok binary", "not on PATH", section)]

    results: list[CheckResult] = []
    try:
        proc = _run(["grok", "--version"], timeout=8)
        blob = ((proc.stdout or "") + (proc.stderr or "")).strip()
        line = blob.splitlines()[0] if blob else "found"
    except (OSError, subprocess.TimeoutExpired):
        line = "found (version probe failed)"
        blob = ""

    results.append(CheckResult("PASS", "grok binary", f"{line} ({path})", section))

    installed = probe_grok_cli_version()
    if installed is None:
        # Binary exists but version unparsable — do not silent-skip.
        results.append(
            CheckResult(
                "FAIL",
                "grok CLI min version",
                f"could not parse version from {blob!r}; need ≥ {min_version}",
                section,
            )
        )
        return results

    try:
        ok = _version_tuple(installed) >= _version_tuple(min_version)
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


def check_cinematic_studio_path() -> list[CheckResult]:
    section = "1. Grok Build CLI"
    path = _which("cinematic-studio")
    if not path:
        return [
            CheckResult(
                "WARN",
                "cinematic-studio",
                "not on PATH (run install or add ~/.grok/bin)",
                section,
            )
        ]
    try:
        proc = _run(["cinematic-studio", "version"], timeout=15)
        line = (proc.stdout or proc.stderr or "found").strip().splitlines()
        detail = line[0] if line else "found"
    except (OSError, subprocess.TimeoutExpired):
        detail = "found (version probe failed)"
    return [CheckResult("PASS", "cinematic-studio", detail, section)]


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

    if default == expected_default:
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

    if fork == expected_fork:
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
    section = "4. Model stack"
    results: list[CheckResult] = []
    try:
        result = verify_model_compatibility()
    except Exception as exc:  # pragma: no cover — defensive
        return [CheckResult("FAIL", "models verify", f"exception: {exc}", section)]

    if result.get("compatible"):
        results.append(
            CheckResult(
                "PASS",
                "models verify",
                (
                    f"compatible (studio {result.get('studio_version')}; "
                    f"CLI {result.get('installed_grok_cli_version') or 'n/a'})"
                ),
                section,
            )
        )
    else:
        issues = result.get("issues") or []
        detail = "; ".join(str(i) for i in issues[:4]) or "incompatible"
        if len(issues) > 4:
            detail += f" (+{len(issues) - 4} more)"
        results.append(CheckResult("FAIL", "models verify", detail, section))

    # Surface operational CLI warnings only — intentional stack notes (unified
    # cinematic+build) stay out so --strict remains meaningful.
    warnings = [
        w
        for w in (result.get("warnings") or [])
        if "Grok Build CLI" in str(w) or "not found on PATH" in str(w)
    ]
    for warning in warnings[:3]:
        results.append(CheckResult("WARN", "models CLI probe", str(warning), section))

    # Compact stack line for human readers (also useful in JSON detail consumers)
    stack = result.get("model_stack") or model_stack_summary()
    results.append(
        CheckResult(
            "PASS",
            "model stack summary",
            (
                f"chat={stack.get('xai_chat')} build={stack.get('xai_build')} "
                f"video={stack.get('imagine_video')} image={stack.get('imagine_image')}"
            ),
            section,
        )
    )
    return results


def check_plugin_installed(*, expected_version: str | None) -> list[CheckResult]:
    section = "5. Cinematic plugin"
    if not _which("grok"):
        return [CheckResult("WARN", "plugin", "skipped (no grok)", section)]

    try:
        listed = _run(["grok", "plugin", "list"], timeout=30)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return [CheckResult("WARN", "plugin installed", f"probe failed: {exc}", section)]

    blob = (listed.stdout or "") + (listed.stderr or "")
    if "grok-imagine-cinematic-studio" not in blob.lower():
        return [
            CheckResult(
                "FAIL",
                "plugin installed",
                "not found — grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio --trust",
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

    if expected_version:
        # Accept "3.8.6" or "v3.8.6" anywhere in details.
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
        elif detail.strip():
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

    errors = check_plugin_artifacts(marketplace, require_release_pin=require_release)
    if not errors:
        return [
            CheckResult(
                "PASS",
                "catalog pin",
                "release check green" if require_release else "artifacts up to date",
                section,
            )
        ]
    # Match prior doctor behavior: catalog/pin drift is WARN so mid-work trees stay usable.
    return [
        CheckResult(
            "WARN",
            "catalog pin",
            "; ".join(errors[:3]) + (f" (+{len(errors) - 3} more)" if len(errors) > 3 else ""),
            section,
        )
    ]


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
    dupes = user_studio_skill_dupes(home, skills_root if skills_root.is_dir() else None)
    if dupes:
        results.append(
            CheckResult(
                "WARN",
                "user ~/.grok/skills",
                (
                    f"{user_n} dirs; {len(dupes)} studio skill dupe(s) "
                    f"(run cinematic-studio declutter --apply)"
                ),
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
    results: list[CheckResult] = []
    try:
        branch = _run(["git", "status", "-sb"], cwd=repo_root, timeout=15)
        describe = _run(["git", "describe", "--tags", "--always"], cwd=repo_root, timeout=15)
        porcelain = _run(["git", "status", "--porcelain"], cwd=repo_root, timeout=15)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return [CheckResult("WARN", "git", f"probe failed: {exc}", section)]

    branch_line = (branch.stdout or "").strip().splitlines()
    tag = (describe.stdout or "").strip()
    summary = f"{branch_line[0] if branch_line else '?'} · {tag or '?'}"
    results.append(CheckResult("PASS", "git", summary, section))
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


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def run_doctor(
    *,
    quick: bool = False,
    home: Path | None = None,
    repo_root: Path | str | None = None,
    project_dir: Path | str | None = None,
    skip_external: bool = False,
    include_release_pin: bool = True,
) -> DoctorReport:
    """
    Run the full doctor check registry.

    skip_external: when True, skip subprocess checks that need grok/gh/pytest/verify
                   (used by pure unit tests). Still runs models/catalog/skills when possible.
    """
    home_path = Path(home) if home is not None else Path.home()
    root = resolve_repo_root(explicit=repo_root)
    proj = (
        Path(project_dir).expanduser().resolve()
        if project_dir
        else _default_project_dir(home_path).resolve()
    )

    report = DoctorReport(
        repo_root=str(root),
        project_dir=str(proj),
        quick=quick,
        started_at=datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
    )

    def add(items: Iterable[CheckResult]) -> None:
        report.checks.extend(items)

    if not skip_external:
        add(check_grok_cli())
        add(check_cinematic_studio_path())
    else:
        add(
            [
                CheckResult(
                    "PASS",
                    "grok binary",
                    "skipped (skip_external)",
                    "1. Grok Build CLI",
                )
            ]
        )

    add(check_auth_and_config(home=home_path))
    version_checks, repo_v, proj_v = check_versions(repo_root=root, project_dir=proj)
    report.repo_version = repo_v
    report.project_version = proj_v
    add(version_checks)

    add(check_model_stack())

    if not skip_external:
        add(check_plugin_installed(expected_version=repo_v if repo_v != "?" else None))
    add(check_catalog_pin(require_release=include_release_pin))
    add(check_skills_layout(home=home_path, repo_root=root))

    if not quick and not skip_external:
        add(check_verify_plugin(repo_root=root))

    add(check_git(repo_root=root))
    add(check_api_keys(home=home_path))
    if not skip_external:
        add(check_github_cli())

    if not quick and not skip_external:
        add(check_pytest(repo_root=root))

    return report


def format_human_report(report: DoctorReport) -> str:
    """Render the classic Grok Doctor human summary."""
    lines: list[str] = []
    lines.append("════════════════════════════════════════")
    lines.append(f" GROK DOCTOR · {report.started_at or datetime.now().isoformat(timespec='seconds')}")
    lines.append(" Studio doctor for Grok Build + Cinematic Studio")
    lines.append("════════════════════════════════════════")

    current_section = ""
    icons = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️ "}
    for check in report.checks:
        if check.section and check.section != current_section:
            current_section = check.section
            lines.append("")
            lines.append(f"── {current_section} ──")
        icon = icons.get(check.status, "•")
        lines.append(f"  {icon} {check.name} — {check.detail}")

    lines.append("")
    lines.append("════════════════════════════════════════")
    lines.append(" SUMMARY")
    lines.append("════════════════════════════════════════")
    lines.append(
        f"  ✅ pass: {report.pass_count}   ❌ fail: {report.fail_count}   "
        f"⚠️  warn: {report.warn_count}"
    )
    if report.healthy:
        lines.append("  Verdict: HEALTHY")
        ver = report.repo_version if report.repo_version != "?" else "3.8.x"
        lines.append(f"  Activate: Activate Grok Imagine Cinematic Studio v{ver}")
    else:
        lines.append("  Verdict: NEEDS ATTENTION")
    lines.append("════════════════════════════════════════")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """CLI entry for `python -m doctor` / direct execution."""
    import argparse

    parser = argparse.ArgumentParser(description="Grok Doctor health check")
    parser.add_argument("--quick", "-q", action="store_true")
    parser.add_argument("--json", action="store_true", dest="json_out")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)

    report = run_doctor(quick=args.quick)
    if args.json_out:
        print(json.dumps(report_to_dict(report), indent=2))
    else:
        print(format_human_report(report))
    return exit_code(report, strict=args.strict)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
