"""Subprocess runner for safe CLI actions from the TUI.

Screens should call ``run_action(action_id, answers)`` only.
``run_cli_command`` is reserved for static allowlisted argv (no free-form).
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from cli.tui.actions import (
    answers_to_argv,
    reject_forbidden_argv,
    static_allowed_argvs,
    validate_answers,
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
    """Project root containing tools/cinematic_studio_cli.py.

    Walks up from this file; falls back to parents[3] (tools/cli/tui → root).
    Honors CINEMATIC_PROJECT_DIR when set and valid.
    """
    import os

    env = os.environ.get("CINEMATIC_PROJECT_DIR")
    if env:
        candidate = Path(env).expanduser().resolve()
        if (candidate / "tools" / "cinematic_studio_cli.py").is_file():
            return candidate

    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "tools" / "cinematic_studio_cli.py").is_file():
            return parent
    # tools/cli/tui/runner.py → parents[3] == project root in normal layout
    return here.parents[3]


def cli_script_path() -> Path:
    return repo_root() / "tools" / "cinematic_studio_cli.py"


def _deny_result(argv: list[str], message: str, *, action_id: str | None = None) -> CommandResult:
    return CommandResult(
        argv=list(argv),
        returncode=2,
        stdout="",
        stderr=message,
        timed_out=False,
        action_id=action_id,
    )


def _subprocess_run(
    argv: list[str],
    *,
    timeout: float,
    cwd: Path | None,
    action_id: str | None = None,
) -> CommandResult:
    if not argv:
        return _deny_result([], "No command argv provided.", action_id=action_id)

    try:
        reject_forbidden_argv(argv)
    except ValueError as exc:
        return _deny_result(argv, str(exc), action_id=action_id)

    script = cli_script_path()
    if not script.is_file():
        return _deny_result(
            argv,
            f"CLI script not found: {script}",
            action_id=action_id,
        )

    cmd = [sys.executable, str(script), *argv]
    workdir = cwd or repo_root()
    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(workdir),
            timeout=max(1.0, float(timeout)),
        )
        return CommandResult(
            argv=list(argv),
            returncode=int(completed.returncode),
            stdout=completed.stdout or "",
            stderr=completed.stderr or "",
            timed_out=False,
            action_id=action_id,
        )
    except subprocess.TimeoutExpired as exc:
        out = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
        err = (exc.stderr or "") if isinstance(exc.stderr, str) else ""
        msg = f"Command timed out after {timeout}s: {' '.join(argv)}"
        return CommandResult(
            argv=list(argv),
            returncode=124,
            stdout=out,
            stderr=(err + "\n" + msg).strip(),
            timed_out=True,
            action_id=action_id,
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
    if not argv:
        return _deny_result([], "No command argv provided.")

    key = tuple(argv)
    if key not in static_allowed_argvs():
        return _deny_result(
            argv,
            "argv not in TUI static allowlist; use run_action(action_id, answers).",
        )
    return _subprocess_run(argv, timeout=timeout, cwd=cwd)


def run_action(
    action_id: str,
    answers: dict[str, str] | None = None,
    *,
    timeout: float = 60.0,
    cwd: Path | None = None,
) -> CommandResult:
    """Build argv from a registered action and execute (only safe entrypoint)."""
    ans = answers or {}
    errors = validate_answers(action_id, ans)
    if errors:
        return _deny_result(
            [],
            "Validation failed: " + "; ".join(errors),
            action_id=action_id,
        )
    try:
        argv = answers_to_argv(action_id, ans)
    except (ValueError, KeyError) as exc:
        return _deny_result([], str(exc), action_id=action_id)
    return _subprocess_run(argv, timeout=timeout, cwd=cwd, action_id=action_id)
