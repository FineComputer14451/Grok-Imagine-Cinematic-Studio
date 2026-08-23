"""Smoke tests for cinematic_studio_cli wiring."""

from __future__ import annotations

from pathlib import Path

from cli_helpers import CLI, ROOT, run_cli


def test_main_help() -> None:
    result = run_cli("--help")
    assert result.returncode == 0
    assert "dna" in result.stdout
    assert "sequence" in result.stdout
    assert "quota" in result.stdout
    assert "dashboard" in result.stdout
    assert "memory" in result.stdout
    assert "ui" in result.stdout
    assert "Grok 4.6" in result.stdout or "4.6" in result.stdout
    ver = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    assert ver in result.stdout


def test_ui_help() -> None:
    result = run_cli("ui", "--help")
    assert result.returncode == 0, result.stderr
    assert (
        "interactive" in result.stdout.lower()
        or "tui" in result.stdout.lower()
        or "terminal" in result.stdout.lower()
    )


def test_main_help_lists_ui() -> None:
    result = run_cli("--help")
    assert result.returncode == 0
    assert "ui" in result.stdout


def test_status_and_stack_show_grok_46() -> None:
    status = run_cli("status")
    assert status.returncode == 0
    ver = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    assert ver in status.stdout
    assert "grok-4.6" in status.stdout
    stack = run_cli("stack")
    assert stack.returncode == 0
    assert "grok-4.6" in stack.stdout
    assert "VIDEO_PIPELINE_SPEC" in stack.stdout or "video" in stack.stdout.lower()
    ver = run_cli("version")
    assert ver.returncode == 0
    assert "4.6" in ver.stdout
    models_stack = run_cli("models", "stack")
    assert models_stack.returncode == 0
    assert "grok-4.6" in models_stack.stdout

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
    assert len(lines) <= 100, f"cinematic_studio_cli.py should be wiring-only, got {len(lines)} lines"


def test_sequence_continuity_commands_registered() -> None:
    result = run_cli("sequence", "--help")
    assert result.returncode == 0
    assert "drift-score" in result.stdout
    assert "seam-report" in result.stdout
    assert "qa-assist" in result.stdout
    assert "health" in result.stdout


def test_sequence_health_options_registered() -> None:
    result = run_cli("sequence", "health", "--help")
    assert result.returncode == 0
    assert "--json" in result.stdout
    assert "--markdown" in result.stdout
    assert "--output" in result.stdout


def test_sequence_amv_check_registered() -> None:
    result = run_cli("sequence", "--help")
    assert "amv-check" in result.stdout


def test_sequence_continuity_diff_registered() -> None:
    result = run_cli("sequence", "--help")
    assert "continuity-diff" in result.stdout


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


def test_sequence_artifact_lexicon_registered() -> None:
    r = run_cli("sequence", "artifact-lexicon", "--help")
    assert r.returncode == 0
    out = r.stdout.lower()
    assert "list" in out
    assert "pack" in out
    assert "suggest" in out


def test_sequence_replan_commands_registered() -> None:
    r = run_cli("sequence", "replan", "--help")
    assert r.returncode == 0
    out = r.stdout.lower()
    assert "plan" in out
    assert "apply" in out


if __name__ == "__main__":
    test_main_file_is_small()
    test_main_help()
    test_subcommand_groups()
    test_validate_passes()
    test_cost_simulate_and_quota_estimate()
    test_sequence_continuity_commands_registered()
    test_sequence_health_options_registered()
    test_sequence_amv_check_registered()
    test_sequence_continuity_diff_registered()
    test_sequence_memory_commands_registered()
    test_sequence_regen_commands_registered()
    test_sequence_temp_commands_registered()
    test_sequence_artifact_lexicon_registered()
    test_sequence_cast_commands_registered()
    test_sequence_replan_commands_registered()
    print("All CLI smoke tests passed")
