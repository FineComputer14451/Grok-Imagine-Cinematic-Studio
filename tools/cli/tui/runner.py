"""Subprocess runner for safe CLI actions from the TUI.

Screens should call ``run_action(action_id, answers)`` only.
``run_cli_command`` is reserved for static allowlisted argv (no free-form).

PR3: execution is delegated to ``studio_core.services.execute`` (subprocess mode)
so Web/API can share validation + argv building with ``mode="inprocess"``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

# Repo root for studio_core (tools/cli/tui → parents[3])
_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from studio_core.services.execute import (
    ActionResult,
    cli_script_path as _core_cli_script_path,
    execute_action,
    execute_argv,
    resolve_repo_root,
)


@dataclass(frozen=True)
class CommandResult:
    argv: list[str]
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False
    action_id: str | None = None


def repo_root() -> Path:
    """Project root containing tools/cinematic_studio_cli.py."""
    return resolve_repo_root()


def cli_script_path() -> Path:
    return _core_cli_script_path()


def _from_action_result(result: ActionResult) -> CommandResult:
    return CommandResult(
        argv=list(result.argv),
        returncode=int(result.returncode),
        stdout=result.stdout or "",
        stderr=result.stderr or "",
        timed_out=bool(result.timed_out),
        action_id=result.action_id,
    )


def run_cli_command(
    argv: list[str],
    *,
    timeout: float = 60.0,
    cwd: Path | None = None,
) -> CommandResult:
    """Run a **static** allowlisted argv (field-less actions only).

    For form-built commands use :func:`run_action`. Free-form argv is rejected.
    """
    result = execute_argv(
        list(argv),
        mode="subprocess",
        timeout=timeout,
        cwd=cwd,
        require_static_allowlist=True,
    )
    return _from_action_result(result)


def run_action(
    action_id: str,
    answers: dict[str, str] | None = None,
    *,
    timeout: float = 60.0,
    cwd: Path | None = None,
) -> CommandResult:
    """Build argv from a registered action and execute via subprocess (TUI safe)."""
    result = execute_action(
        action_id,
        answers,
        mode="subprocess",
        timeout=timeout,
        cwd=cwd,
    )
    return _from_action_result(result)
