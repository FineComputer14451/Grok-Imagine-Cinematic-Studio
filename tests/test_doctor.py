"""Unit tests for the Grok Doctor Python check registry."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from doctor import (  # noqa: E402
    CheckResult,
    DoctorReport,
    check_auth_and_config,
    check_grok_cli,
    exit_code,
    format_human_report,
    report_to_dict,
    run_doctor,
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
        repo_version="3.8.6",
        project_version="3.8.6",
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
    assert payload["repo_version"] == "3.8.6"
    assert isinstance(payload["checks"], list)
    assert payload["checks"][0]["status"] == "PASS"
    assert payload["checks"][0]["name"] == "grok binary"
    assert "section" in payload["checks"][0]


def test_format_human_includes_summary() -> None:
    report = DoctorReport(
        checks=[CheckResult("PASS", "auth.json", "present", "2. Auth & config")],
        repo_version="3.8.6",
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
    # No crash; dupes may or may not exist on the host
    assert isinstance(user_studio_skill_dupes(), list)


def test_run_doctor_skip_external_json_contract(tmp_path: Path) -> None:
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
    payload = report_to_dict(report)
    assert "checks" in payload
    assert payload["repo_version"] == (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    # models verify runs in-process without external binaries
    assert any(c.name == "models verify" for c in report.checks)
    assert any(c.name == "repo skill dirs" for c in report.checks)
    # JSON serializable
    json.dumps(payload)


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
    # stdout should be JSON even when warnings/fails exist
    data = json.loads(proc.stdout)
    assert "healthy" in data
    assert "checks" in data
    assert isinstance(data["pass"], int)


def test_grok_cli_min_version_uses_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unparsable version must FAIL (no silent skip)."""
    monkeypatch.setattr("doctor._which", lambda cmd: "/usr/bin/grok" if cmd == "grok" else None)
    monkeypatch.setattr(
        "doctor._run",
        lambda *a, **k: type(
            "P",
            (),
            {"stdout": "grok weird-build", "stderr": "", "returncode": 0},
        )(),
    )
    monkeypatch.setattr("doctor.probe_grok_cli_version", lambda: None)
    results = check_grok_cli(min_version="0.2.93")
    by_name = {r.name: r for r in results}
    assert by_name["grok binary"].status == "PASS"
    assert by_name["grok CLI min version"].status == "FAIL"
