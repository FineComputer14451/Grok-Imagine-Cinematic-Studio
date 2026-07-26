# tests/test_tui_print.py
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from cli.tui_commands import _print_orient_dashboard  # noqa: E402


def test_print_orient_dashboard_ok() -> None:
    code = _print_orient_dashboard(write_artifact=False)
    assert code == 0
