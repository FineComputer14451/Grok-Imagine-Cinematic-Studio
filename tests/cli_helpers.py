"""Shared CLI subprocess helpers for tests (ANSI-safe help output).

Rich/Typer help on CI may emit SGR sequences that split option flags
(e.g. ``\\x1b[1m-\\x1b[0m\\x1b[1m-json\\x1b[0m``), so ``"--json" in stdout``
fails even when the option is present. These helpers force plain output and
strip residual ANSI before assertions.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "tools" / "cinematic_studio_cli.py"

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(text: str) -> str:
    return _ANSI_RE.sub("", text or "")


def cli_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    env = {
        **os.environ,
        "NO_COLOR": "1",
        "FORCE_COLOR": "0",
        "TERM": "dumb",
        "COLUMNS": "120",
    }
    if extra:
        env.update(extra)
    return env


def run_cli(
    *args: str,
    stdin: str | None = None,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run cinematic_studio_cli.py and return ANSI-stripped stdout/stderr."""
    result = subprocess.run(
        [sys.executable, str(CLI), *args],
        capture_output=True,
        text=True,
        cwd=str(cwd or ROOT),
        input=stdin,
        env=env or cli_env(),
    )
    return subprocess.CompletedProcess(
        args=result.args,
        returncode=result.returncode,
        stdout=strip_ansi(result.stdout),
        stderr=strip_ansi(result.stderr),
    )
