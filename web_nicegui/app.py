"""NiceGUI application entry — cinematic-studio web."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Ensure repo root + tools/ are importable when launched as a script.
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_TOOLS = _ROOT / "tools"
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))


def _require_nicegui() -> Any:
    try:
        from nicegui import ui
    except ImportError as exc:  # pragma: no cover
        raise SystemExit(
            "NiceGUI is required for the web shell.\n"
            "Install with:\n"
            "  pip install -r requirements-nicegui.txt\n"
            "or:\n"
            "  pip install 'nicegui>=2.0.0'\n"
        ) from exc
    return ui


def create_app() -> Any:
    """Register pages on the NiceGUI ``ui`` module; return ui."""
    ui = _require_nicegui()
    from web_nicegui.pages.dashboard import build_dashboard_page

    # Simple session mode storage on the ui module (per-process default).
    app_state: dict[str, str] = {"mode": "ops"}

    @ui.page("/")
    def index_page() -> None:
        ui.colors(primary="#7c3aed", secondary="#22d3ee", accent="#f59e0b")
        with ui.header().classes("items-center justify-between bg-primary"):
            ui.label("🎥 Grok Imagine Cinematic Studio").classes("text-h6")
            with ui.row().classes("items-center gap-3"):
                ui.link("Dashboard", "/").classes("text-white")
                ui.label("PR4 · read-only").classes("text-caption text-white")
        with ui.column().classes("w-full max-w-6xl mx-auto q-pa-md"):
            build_dashboard_page(
                ui,
                get_mode=lambda: app_state.get("mode", "ops"),
                set_mode=lambda m: app_state.__setitem__("mode", m),
            )
        with ui.footer().classes("bg-grey-2"):
            ui.label(
                "Independent community project — not affiliated with xAI. "
                "Core: studio_core.services.dashboard · CLI: cinematic-studio"
            ).classes("text-caption text-grey-8 q-pa-sm")

    return ui


def run_web(
    *,
    host: str = "127.0.0.1",
    port: int = 8088,
    reload: bool = False,
    show: bool = False,
    title: str = "Grok Imagine Cinematic Studio",
) -> None:
    """Start the NiceGUI server (blocking)."""
    ui = create_app()
    ui.run(
        host=host,
        port=port,
        reload=reload,
        show=show,
        title=title,
        favicon="🎥",
    )


if __name__ == "__main__":
    run_web()
