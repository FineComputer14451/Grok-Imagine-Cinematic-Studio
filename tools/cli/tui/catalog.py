"""Launcher catalog (compat re-exports from unified actions registry)."""

from __future__ import annotations

from cli.tui.actions import (  # noqa: F401
    FORBIDDEN_ARGV_TOKENS,
    LAUNCHER_CATALOG,
    LAUNCHER_ORDER,
    LauncherEntry,
)

__all__ = [
    "FORBIDDEN_ARGV_TOKENS",
    "LAUNCHER_CATALOG",
    "LAUNCHER_ORDER",
    "LauncherEntry",
]
