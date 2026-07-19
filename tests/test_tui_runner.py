# tests/test_tui_runner.py
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from cli.tui.runner import (  # noqa: E402
    cli_script_path,
    repo_root,
    run_action,
    run_cli_command,
)


def test_repo_root_and_cli_script_exist() -> None:
    root = repo_root()
    assert (root / "VERSION").is_file()
    script = cli_script_path()
    assert script.is_file()
    assert script.name == "cinematic_studio_cli.py"


def test_run_cli_command_status_succeeds() -> None:
    result = run_cli_command(["status"], timeout=30.0)
    assert result.timed_out is False
    assert result.returncode == 0
    assert result.stdout
    assert "Grok" in result.stdout or "4.5" in result.stdout or "Studio" in result.stdout


def test_run_cli_command_timeout_sets_flag() -> None:
    import subprocess as sp

    with patch(
        "cli.tui.runner.subprocess.run",
        side_effect=sp.TimeoutExpired(cmd=["x"], timeout=0.01),
    ):
        result = run_cli_command(["status"], timeout=0.01)
    assert result.timed_out is True
    assert result.returncode != 0
    assert "timed out" in result.stderr.lower() or "timed out" in result.stdout.lower()


def test_run_cli_command_rejects_freeform_argv() -> None:
    result = run_cli_command(["create-bible", "Hacked", "--wizard"])
    assert result.returncode != 0
    assert "allowlist" in result.stderr.lower() or "forbidden" in result.stderr.lower()


def test_run_cli_command_rejects_mutating_dynamic_argv() -> None:
    # Even without forbidden tokens, non-static argv is denied.
    result = run_cli_command(["dna", "list", "extra"])
    assert result.returncode != 0
    assert "allowlist" in result.stderr.lower()


def test_run_action_status_succeeds() -> None:
    result = run_action("status", timeout=30.0)
    assert result.timed_out is False
    assert result.returncode == 0
    assert result.action_id == "status"
    assert result.argv == ["status"]
    assert result.stdout


def test_run_action_validation_failure() -> None:
    result = run_action("bible_create", {"title": ""})
    assert result.returncode != 0
    assert "required" in result.stderr.lower() or "validation" in result.stderr.lower()
