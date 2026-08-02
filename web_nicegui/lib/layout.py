"""Shared NiceGUI chrome (header / nav / footer)."""

from __future__ import annotations

from typing import Any

NAV = (
    ("/", "Dashboard"),
    ("/dna", "DNA"),
    ("/sequences", "Sequences"),
    ("/quota", "Quota"),
)


def page_shell(ui: Any, *, active: str, badge: str = "PR5") -> None:
    """Apply colors, header nav, and footer once per page."""
    ui.colors(primary="#7c3aed", secondary="#22d3ee", accent="#f59e0b")
    with ui.header().classes("items-center justify-between bg-primary"):
        ui.label("Grok Imagine Cinematic Studio").classes("text-h6 text-white")
        with ui.row().classes("items-center gap-3"):
            for path, label in NAV:
                cls = "text-white text-weight-bold" if path == active else "text-white"
                ui.link(label, path).classes(cls)
            ui.label(badge).classes("text-caption text-white")
    with ui.footer().classes("bg-grey-2"):
        ui.label(
            "Independent community project — not affiliated with xAI. "
            "Core: studio_core.services · CLI: cinematic-studio"
        ).classes("text-caption text-grey-8 q-pa-sm")
