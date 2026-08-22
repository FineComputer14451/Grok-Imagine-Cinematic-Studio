"""Unit tests for the Grok Doctor Python check registry."""

from __future__ import annotations

import json
import os
import stat
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from doctor import (  # noqa: E402
    REGISTRY,
    CheckResult,
    DoctorReport,
    check_auth_and_config,
    check_grok_cli,
    exit_code,
    format_human_report,
    report_to_dict,
    run_doctor,
)
from doctor_checks import (  # noqa: E402
    METHOD_A_CORE_SKILLS,
    check_catalog_pin,
    check_model_stack,
    check_plugin_installed,
    check_skills_layout,
    method_a_core_installed,
)
from studio_health import (  # noqa: E402
    count_skills,
    skills_missing_model_compatibility,
    user_studio_skill_dupes,
)


def test_exit_code_fail_and_strict() -> None:
    healthy = DoctorReport(
        checks=[CheckResult("PASS", "a", "ok"), CheckResult("WARN", "b", "meh")]
    )
    assert exit_code(healthy) == 0
    assert exit_code(healthy, strict=True) == 1

    broken = DoctorReport(checks=[CheckResult("FAIL", "a", "nope")])
    assert exit_code(broken) == 1
    assert exit_code(broken, strict=True) == 1


def test_report_to_dict_schema() -> None:
    report = DoctorReport(
        checks=[
            CheckResult("PASS", "grok binary", "0.2.111", "1. Grok Build CLI"),
            CheckResult("WARN", "working tree", "dirty", "9. Git"),
        ],
        repo_version="3.8.7",
        project_version="3.8.7",
        repo_root=str(ROOT),
        project_dir="/tmp/proj",
        quick=True,
        started_at="2026-01-01T00:00:00+00:00",
    )
    payload = report_to_dict(report)
    assert payload["pass"] == 1
    assert payload["fail"] == 0
    assert payload["warn"] == 1
    assert payload["healthy"] is True
    assert payload["quick"] is True
    assert payload["repo_version"] == "3.8.7"
    assert isinstance(payload["checks"], list)
    assert payload["checks"][0]["status"] == "PASS"
    assert payload["checks"][0]["name"] == "grok binary"
    assert "section" in payload["checks"][0]


def test_format_human_includes_summary() -> None:
    report = DoctorReport(
        checks=[CheckResult("PASS", "auth.json", "present", "2. Auth & config")],
        repo_version="3.8.7",
        started_at="now",
    )
    text = format_human_report(report)
    assert "GROK DOCTOR" in text
    assert "SUMMARY" in text
    assert "HEALTHY" in text
    assert "auth.json" in text


def test_auth_config_reads_toml(tmp_path: Path) -> None:
    home = tmp_path / "home"
    grok = home / ".grok"
    grok.mkdir(parents=True)
    (grok / "auth.json").write_text("{}", encoding="utf-8")
    (grok / "config.toml").write_text(
        '[models]\ndefault = "grok-4.5"\n\n[ui]\nfork_secondary_model = "grok-build"\n',
        encoding="utf-8",
    )
    results = check_auth_and_config(home=home)
    by_name = {r.name: r for r in results}
    assert by_name["auth.json"].status == "PASS"
    assert by_name["models.default"].status == "PASS"
    assert by_name["fork_secondary_model"].status == "PASS"


def test_auth_config_warns_on_wrong_default(tmp_path: Path) -> None:
    home = tmp_path / "home"
    grok = home / ".grok"
    grok.mkdir(parents=True)
    (grok / "auth.json").write_text("{}", encoding="utf-8")
    (grok / "config.toml").write_text(
        '[models]\ndefault = "grok-4.3"\n\n[ui]\nfork_secondary_model = "other"\n',
        encoding="utf-8",
    )
    results = check_auth_and_config(home=home)
    by_name = {r.name: r for r in results}
    assert by_name["models.default"].status == "WARN"
    assert by_name["fork_secondary_model"].status == "WARN"


def test_auth_missing_fails(tmp_path: Path) -> None:
    home = tmp_path / "home"
    home.mkdir()
    results = check_auth_and_config(home=home)
    assert any(r.name == "auth.json" and r.status == "FAIL" for r in results)


def test_studio_health_helpers() -> None:
    n = count_skills()
    assert n >= 40
    missing = skills_missing_model_compatibility()
    assert isinstance(missing, list)
    assert isinstance(user_studio_skill_dupes(), list)


def test_registry_has_expected_ids() -> None:
    ids = [s.id for s in REGISTRY]
    assert "grok_cli" in ids
    assert "pytest" in ids
    assert "verify_plugin" in ids
    assert "quota_recon" in ids
    assert "control_plane" in ids
    # full_only flags present on slow checks
    by_id = {s.id: s for s in REGISTRY}
    assert by_id["pytest"].full_only and by_id["pytest"].external
    assert by_id["verify_plugin"].full_only and by_id["verify_plugin"].external
    assert not by_id["model_stack"].external
    assert not by_id["quota_recon"].external
    assert not by_id["quota_recon"].full_only
    assert not by_id["control_plane"].external
    assert not by_id["control_plane"].full_only


def test_run_doctor_skip_external_omits_without_fake_pass(tmp_path: Path) -> None:
    home = tmp_path / "home"
    grok = home / ".grok"
    grok.mkdir(parents=True)
    (grok / "auth.json").write_text("{}", encoding="utf-8")
    (grok / "config.toml").write_text(
        '[models]\ndefault = "grok-4.5"\n\n[ui]\nfork_secondary_model = "grok-build"\n',
        encoding="utf-8",
    )
    report = run_doctor(
        quick=True,
        home=home,
        repo_root=ROOT,
        project_dir=tmp_path / "no-project",
        skip_external=True,
    )
    names = [c.name for c in report.checks]
    # External checks omitted — no synthetic PASS for grok binary
    assert "grok binary" not in names
    assert "gh auth" not in names
    assert "gh" not in names
    assert any(c.name == "models verify" for c in report.checks)
    assert any(c.name == "repo skill dirs" for c in report.checks)
    # quick skips full_only even if not external-only... verify/pytest are external+full
    assert "verify --plugin" not in names
    assert "pytest packs/agents" not in names
    payload = report_to_dict(report)
    assert payload["repo_version"] == (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    json.dumps(payload)


def test_quick_skips_full_only_ids() -> None:
    full_only_ids = {s.id for s in REGISTRY if s.full_only}
    assert full_only_ids == {"verify_plugin", "pytest"}


def test_check_control_plane_runs() -> None:
    from doctor_checks import check_control_plane

    results = check_control_plane()
    assert results
    assert results[0].name == "control plane"
    assert results[0].status in {"PASS", "WARN", "FAIL"}
    assert "severity=" in (results[0].detail or "")


def test_check_quota_recon_aligned(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from doctor_checks import check_quota_recon
    from generation_tracker import LEDGER_PATH  # noqa: F401 — patch target
    from quota_sync import default_reconciliation, ledger_recon_alignment

    ledger_path = tmp_path / "generation_ledger.json"
    ledger_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "entries": [
                    {
                        "entry_id": "g1",
                        "project": "p",
                        "status": "completed",
                        "credits_estimate": 10.0,
                        "credits_actual": 12.0,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr("generation_tracker.LEDGER_PATH", ledger_path)

    recon = default_reconciliation()
    recon["estimated_total"] = 10.0
    recon["actual_total"] = 12.0
    recon["entries"] = [
        {
            "estimated_credits": 10.0,
            "actual_credits": 12.0,
            "source": "generation_ledger",
            "note": "ledger:p g1",
        }
    ]
    recon["sources"] = ["generation_ledger"]
    state = {"quota": {"reconciliation": recon}}

    align = ledger_recon_alignment(state)
    assert align["status"] == "aligned"

    monkeypatch.setattr(
        "quota_sync.load_project_state",
        lambda *a, **k: state,
    )
    # ledger_recon_alignment inside check imports load via quota_sync.recon_snapshot
    monkeypatch.setattr(
        "project_state.load_project_state",
        lambda *a, **k: state,
    )
    results = check_quota_recon()
    assert len(results) == 1
    assert results[0].status == "PASS"
    assert results[0].name == "quota recon"
    assert "aligned" in results[0].detail.lower() or "n=" in results[0].detail


def test_check_quota_recon_mismatch_warns(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from doctor_checks import check_quota_recon
    from quota_sync import default_reconciliation, ledger_recon_alignment

    ledger_path = tmp_path / "generation_ledger.json"
    ledger_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "entries": [
                    {
                        "entry_id": "g1",
                        "status": "completed",
                        "credits_estimate": 5.0,
                        "credits_actual": 5.0,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr("generation_tracker.LEDGER_PATH", ledger_path)

    recon = default_reconciliation()
    recon["estimated_total"] = 99.0
    recon["actual_total"] = 99.0
    recon["entries"] = [{"estimated_credits": 99.0, "actual_credits": 99.0}]
    recon["sources"] = ["generation_ledger"]
    state = {"quota": {"reconciliation": recon}}

    assert ledger_recon_alignment(state)["status"] == "mismatch"
    monkeypatch.setattr("project_state.load_project_state", lambda *a, **k: state)
    monkeypatch.setattr("quota_sync.load_project_state", lambda *a, **k: state)
    results = check_quota_recon()
    assert results[0].status == "WARN"
    assert "quota sync" in results[0].detail


def test_ledger_recon_stale_and_idle(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from quota_sync import default_reconciliation, ledger_recon_alignment

    empty = tmp_path / "empty_ledger.json"
    empty.write_text(json.dumps({"schema_version": "1.0", "entries": []}), encoding="utf-8")
    monkeypatch.setattr("generation_tracker.LEDGER_PATH", empty)

    idle = ledger_recon_alignment(
        {"quota": {"reconciliation": default_reconciliation()}}
    )
    assert idle["status"] == "idle"

    ledger_path = tmp_path / "generation_ledger.json"
    ledger_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "entries": [
                    {
                        "entry_id": "g1",
                        "status": "completed",
                        "credits_estimate": 1.0,
                        "credits_actual": 1.0,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr("generation_tracker.LEDGER_PATH", ledger_path)
    stale = ledger_recon_alignment(
        {
            "quota": {
                "reconciliation": {
                    **default_reconciliation(),
                    "sources": ["history_est"],
                    "estimated_total": 1.0,
                    "actual_total": 1.0,
                }
            }
        }
    )
    assert stale["status"] == "stale"


def test_cli_doctor_json_smoke() -> None:
    import subprocess

    proc = subprocess.run(
        [sys.executable, str(TOOLS / "cinematic_studio_cli.py"), "doctor", "--quick", "--json"],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False,
    )
    assert proc.returncode in (0, 1), proc.stderr
    data = json.loads(proc.stdout)
    assert "healthy" in data
    assert "checks" in data
    assert isinstance(data["pass"], int)


def test_grok_cli_min_version_unparsable(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unparsable version must FAIL (no silent skip); single probe path."""
    monkeypatch.setattr(
        "doctor_checks.probe_grok_cli",
        lambda: {
            "path": "/usr/bin/grok",
            "version": None,
            "display": "grok weird-build",
            "raw": "grok weird-build",
        },
    )
    results = check_grok_cli(min_version="0.2.93")
    by_name = {r.name: r for r in results}
    assert by_name["grok binary"].status == "PASS"
    assert by_name["grok CLI min version"].status == "FAIL"


def test_model_stack_no_free_pass_on_fail(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "doctor_checks.verify_model_compatibility",
        lambda: {
            "compatible": False,
            "issues": ["ROLE_DEFAULTS drifted"],
            "warnings": [],
            "notes": ["unified stack"],
            "studio_version": "3.8.7",
            "installed_grok_cli_version": "0.2.111",
            "model_stack": {
                "xai_chat": "grok-4.5",
                "xai_build": "grok-4.5",
                "imagine_video": "grok-imagine-video",
                "imagine_image": "grok-imagine-image",
            },
        },
    )
    results = check_model_stack()
    names = [r.name for r in results]
    assert "model stack summary" not in names
    assert any(r.name == "models verify" and r.status == "FAIL" for r in results)
    # notes must not become WARN
    assert not any(r.status == "WARN" for r in results)


def test_shim_has_no_hardcoded_clone_path() -> None:
    body = (ROOT / "scripts" / "grok_doctor.sh").read_text(encoding="utf-8")
    assert "Grok-Imagine-Cinematic-Studio/tools/doctor.py" not in body
    assert "CINEMATIC_PROJECT_DIR" in body


def test_cmd_doctor_delegates_to_shim() -> None:
    body = (ROOT / "scripts" / "cinematic_studio.sh").read_text(encoding="utf-8")
    assert "grok_doctor.sh" in body
    # No multi-path CLI hunt in cmd_doctor
    assert 'for cli in' not in body


def _write_method_a_core(home: Path) -> None:
    skills = home / ".grok" / "skills"
    for slug in METHOD_A_CORE_SKILLS:
        d = skills / slug
        d.mkdir(parents=True, exist_ok=True)
        (d / "SKILL.md").write_text(f"# {slug}\n", encoding="utf-8")


def test_method_a_core_installed(tmp_path: Path) -> None:
    home = tmp_path / "home"
    assert method_a_core_installed(home) is False
    _write_method_a_core(home)
    assert method_a_core_installed(home) is True


def test_plugin_absent_method_a_is_pass(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    home = tmp_path / "home"
    _write_method_a_core(home)
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    grok = fake_bin / "grok"
    grok.write_text(
        "#!/usr/bin/env bash\necho 'No plugins installed.'\n",
        encoding="utf-8",
    )
    grok.chmod(grok.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setenv("PATH", f"{fake_bin}{os.pathsep}{os.environ.get('PATH', '')}")
    results = check_plugin_installed(expected_version="3.9.1", home=home)
    assert results[0].status == "PASS"
    assert "Method A" in results[0].detail


def test_plugin_absent_without_method_a_is_fail(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    home = tmp_path / "home"
    home.mkdir()
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    grok = fake_bin / "grok"
    grok.write_text(
        "#!/usr/bin/env bash\necho 'No plugins installed.'\n",
        encoding="utf-8",
    )
    grok.chmod(grok.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setenv("PATH", f"{fake_bin}{os.pathsep}{os.environ.get('PATH', '')}")
    results = check_plugin_installed(expected_version="3.9.1", home=home)
    assert results[0].status == "FAIL"
    assert "plugin install" in results[0].detail


def test_skills_layout_method_a_is_not_high_warn(tmp_path: Path) -> None:
    home = tmp_path / "home"
    _write_method_a_core(home)
    # Extra dirs so count is above the clutter heuristic
    for i in range(20):
        (home / ".grok" / "skills" / f"extra-{i}").mkdir(parents=True, exist_ok=True)
    repo = tmp_path / "not-a-checkout"
    repo.mkdir()
    results = check_skills_layout(home=home, repo_root=repo)
    by_name = {r.name: r for r in results}
    assert by_name["user ~/.grok/skills"].status == "PASS"
    assert "Method A" in by_name["user ~/.grok/skills"].detail
