"""Smoke tests for cinematic_studio_cli wiring."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "tools" / "cinematic_studio_cli.py"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )


def test_main_help() -> None:
    result = run_cli("--help")
    assert result.returncode == 0
    assert "dna" in result.stdout
    assert "sequence" in result.stdout
    assert "quota" in result.stdout
    assert "dashboard" in result.stdout
    assert "memory" in result.stdout


def test_subcommand_groups() -> None:
    for group in ("dna", "sequence", "quota", "models", "nsfw", "sfw", "imagine", "animatic", "memory", "plugin"):
        result = run_cli(group, "--help")
        assert result.returncode == 0, result.stderr


def test_plugin_catalog_check() -> None:
    result = run_cli("plugin", "catalog", "check")
    assert result.returncode == 0, result.stderr
    assert "up to date" in result.stdout.lower()


def test_validate_passes() -> None:
    result = run_cli("validate")
    assert result.returncode == 0
    assert "Validation passed" in result.stdout
    assert "skills" in result.stdout.lower()
    assert "Model stack compatible" in result.stdout


def test_cost_simulate_and_quota_estimate() -> None:
    cost = run_cli("cost-simulate", "--duration", "30")
    quota = run_cli("quota", "estimate", "--duration", "30")
    assert cost.returncode == 0
    assert quota.returncode == 0
    assert "Credits" in cost.stdout
    assert "Credits" in quota.stdout


def test_main_file_is_small() -> None:
    lines = CLI.read_text().splitlines()
    assert len(lines) < 80, f"cinematic_studio_cli.py should be wiring-only, got {len(lines)} lines"


def test_sequence_continuity_commands_registered() -> None:
    result = run_cli("sequence", "--help")
    assert result.returncode == 0
    assert "drift-score" in result.stdout
    assert "seam-report" in result.stdout
    assert "qa-assist" in result.stdout


def test_sequence_amv_check_registered() -> None:
    result = run_cli("sequence", "--help")
    assert "amv-check" in result.stdout


def test_sequence_memory_commands_registered() -> None:
    result = run_cli("sequence", "--help")
    assert result.returncode == 0
    assert "memory" in result.stdout.lower()
    result2 = run_cli("sequence", "memory", "--help")
    assert result2.returncode == 0
    assert "show" in result2.stdout.lower()
    assert "sync" in result2.stdout.lower()


def test_sequence_regen_commands_registered() -> None:
    result = run_cli("sequence", "regen", "--help")
    assert result.returncode == 0
    out = result.stdout.lower()
    assert "plan" in out
    assert "apply" in out
    assert "run" in out


def test_sequence_temp_commands_registered() -> None:
    r = run_cli("sequence", "temp", "--help")
    assert r.returncode == 0
    assert "set" in r.stdout.lower()
    assert "show" in r.stdout.lower()
    assert "gate" in r.stdout.lower()


def test_sequence_cast_commands_registered() -> None:
    r = run_cli("sequence", "cast", "--help")
    assert r.returncode == 0
    assert "arbitrate" in r.stdout.lower()
    assert "inject" in r.stdout.lower()


if __name__ == "__main__":
    test_main_file_is_small()
    test_main_help()
    test_subcommand_groups()
    test_validate_passes()
    test_cost_simulate_and_quota_estimate()
    test_sequence_continuity_commands_registered()
    test_sequence_amv_check_registered()
    test_sequence_memory_commands_registered()
    test_sequence_regen_commands_registered()
    test_sequence_temp_commands_registered()
    test_sequence_cast_commands_registered()
    print("All CLI smoke tests passed")
