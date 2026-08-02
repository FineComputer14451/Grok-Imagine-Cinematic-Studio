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
    from web_nicegui.lib.layout import page_shell
    from web_nicegui.pages.dashboard import build_dashboard_page
    from web_nicegui.pages.dna import build_dna_page
    from web_nicegui.pages.quota import build_quota_page
    from web_nicegui.pages.sequences import build_sequences_page

    app_state: dict[str, str] = {"mode": "ops"}

    @ui.page("/")
    def index_page() -> None:
        page_shell(ui, active="/")
        with ui.column().classes("w-full max-w-6xl mx-auto q-pa-md"):
            build_dashboard_page(
                ui,
                get_mode=lambda: app_state.get("mode", "ops"),
                set_mode=lambda m: app_state.__setitem__("mode", m),
            )

    @ui.page("/dna")
    def dna_page() -> None:
        page_shell(ui, active="/dna")
        with ui.column().classes("w-full max-w-6xl mx-auto q-pa-md"):
            build_dna_page(ui)

    @ui.page("/sequences")
    def sequences_page() -> None:
        page_shell(ui, active="/sequences")
        with ui.column().classes("w-full max-w-6xl mx-auto q-pa-md"):
            build_sequences_page(ui)

    @ui.page("/quota")
    def quota_page() -> None:
        page_shell(ui, active="/quota")
        with ui.column().classes("w-full max-w-6xl mx-auto q-pa-md"):
            build_quota_page(ui)

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
    )


if __name__ == "__main__":
    run_web()
