"""Tests for CLI studio dashboard."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from cli.dashboard import build_studio_dashboard  # noqa: E402

CLI = ROOT / "tools" / "cinematic_studio_cli.py"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )


def test_build_studio_dashboard_shape() -> None:
    snap = build_studio_dashboard()
    assert snap["studio_version"]
    assert "studio" in snap
    assert "quota" in snap
    assert "production" in snap
    assert "sequences" in snap
    assert "characters" in snap
    assert snap["studio"]["core_agents"] >= 23
    recon = snap["quota"].get("reconciliation") or {}
    assert "cascade_source" in recon
    assert "entry_count" in recon


def test_quota_table_shows_cascade() -> None:
    from cli.dashboard import _quota_table
    from rich.console import Console

    snap = {
        "quota": {
            "tier_label": "Test",
            "session_spent": 1,
            "session_generations": 1,
            "risk_level": "low",
            "burn_rate_risk": "medium",
            "reconciliation": {
                "cascade_source": "generation_ledger",
                "estimated_total": 10.0,
                "actual_total": 12.0,
                "variance_pct": 20.0,
                "entry_count": 2,
                "burn_rate_multiplier": 1.2,
                "risk_level": "medium",
            },
        }
    }
    table = _quota_table(snap)
    console = Console(record=True, width=80)
    console.print(table)
    text = console.export_text()
    assert "Cascade" in text
    assert "ledger" in text.lower()
    assert "Burn Rate" in text


def test_dashboard_command_runs() -> None:
    result = run_cli("dashboard", "--compact")
    assert result.returncode == 0, result.stderr
    assert "Studio Dashboard" in result.stdout
    assert "Quota" in result.stdout


def test_dashboard_json_output() -> None:
    result = run_cli("dashboard", "--json", "--compact")
    assert result.returncode == 0, result.stderr
    assert '"studio_version"' in result.stdout
    assert '"quota"' in result.stdout


if __name__ == "__main__":
    test_build_studio_dashboard_shape()
    test_dashboard_command_runs()
    test_dashboard_json_output()
    print("All CLI dashboard tests passed")