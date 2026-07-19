"""Subprocess runner for safe CLI commands from the TUI."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CommandResult:
    argv: list[str]
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False


def repo_root() -> Path:
    # tools/cli/tui/runner.py → parents[0]=tui, [1]=cli, [2]=tools, [3]=repo
    return Path(__file__).resolve().parents[3]


def cli_script_path() -> Path:
    return repo_root() / "tools" / "cinematic_studio_cli.py"


def run_cli_command(
    argv: list[str],
    *,
    timeout: float = 60.0,
    cwd: Path | None = None,
) -> CommandResult:
    if not argv:
        return CommandResult(
            argv=[],
            returncode=2,
            stdout="",
            stderr="No command argv provided.",
            timed_out=False,
        )
    script = cli_script_path()
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
        )
