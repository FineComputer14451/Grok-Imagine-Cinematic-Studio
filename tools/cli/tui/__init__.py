"""Interactive Textual TUI for cinematic-studio."""

from __future__ import annotations

__all__ = ["run_tui"]


def __getattr__(name: str):
    if name == "run_tui":
        from cli.tui.app import run_tui

        return run_tui
    raise AttributeError(name)
