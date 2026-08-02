"""PR3: studio_core execute_action (inprocess + subprocess)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))

from studio_core.services.execute import (  # noqa: E402
    ActionResult,
    execute_action,
    execute_argv,
)


def test_execute_action_status_inprocess() -> None:
    result = execute_action("status", mode="inprocess", timeout=60.0)
    assert isinstance(result, ActionResult)
    assert result.mode == "inprocess"
    assert result.timed_out is False
    assert result.returncode == 0
    assert result.ok is True
    assert result.action_id == "status"
    assert result.argv == ["status"]
    assert result.stdout
    assert "4.5" in result.stdout or "Studio" in result.stdout or "Grok" in result.stdout


def test_execute_action_status_subprocess() -> None:
    result = execute_action("status", mode="subprocess", timeout=60.0)
    assert result.mode == "subprocess"
    assert result.returncode == 0
    assert result.ok is True
    assert result.argv == ["status"]
    assert result.stdout


def test_execute_action_validation_failure() -> None:
    result = execute_action("bible_create", {"title": ""}, mode="inprocess")
    assert result.ok is False
    assert result.returncode != 0
    assert result.errors
    assert "required" in result.stderr.lower() or "validation" in result.stderr.lower()


def test_execute_action_stack_inprocess() -> None:
    result = execute_action("stack", mode="inprocess", timeout=60.0)
    assert result.returncode == 0
    assert "grok-4.5" in result.stdout or "VIDEO_PIPELINE" in result.stdout or "Model" in result.stdout


def test_execute_argv_static_allowlist_rejects_freeform() -> None:
    result = execute_argv(
        ["create-bible", "Hacked", "--wizard"],
        mode="subprocess",
        require_static_allowlist=True,
    )
    assert result.ok is False
    assert "allowlist" in result.stderr.lower() or "forbidden" in result.stderr.lower()


def test_execute_argv_forbidden_token_without_allowlist() -> None:
    result = execute_argv(["create-bible", "X", "--wizard"], mode="inprocess")
    assert result.ok is False
    assert "forbidden" in result.stderr.lower() or "wizard" in result.stderr.lower()


def test_tui_runner_delegates_to_execute() -> None:
    from cli.tui.runner import run_action

    r = run_action("status", timeout=30.0)
    assert r.returncode == 0
    assert r.action_id == "status"
    assert r.argv == ["status"]


if __name__ == "__main__":
    test_execute_action_status_inprocess()
    test_execute_action_status_subprocess()
    test_execute_action_validation_failure()
    test_execute_action_stack_inprocess()
    test_execute_argv_static_allowlist_rejects_freeform()
    test_execute_argv_forbidden_token_without_allowlist()
    test_tui_runner_delegates_to_execute()
    print("studio_core execute tests passed")
