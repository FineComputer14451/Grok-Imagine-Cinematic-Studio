"""Ensure repo-root and tools/ are importable for studio_core consumers."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_TOOLS = _ROOT / "tools"


def ensure_import_paths() -> Path:
    """Insert repo root + tools/ on sys.path (idempotent). Return studio root."""
    tools_s = str(_TOOLS)
    root_s = str(_ROOT)
    if tools_s not in sys.path:
        sys.path.insert(0, tools_s)
    if root_s not in sys.path:
        sys.path.insert(0, root_s)
    return _ROOT


STUDIO_ROOT = _ROOT
