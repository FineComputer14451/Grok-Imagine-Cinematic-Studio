"""Textual application entry for cinematic-studio ui."""

from __future__ import annotations

from textual.app import App

from cli.tui.screens import HomeScreen


class StudioTUI(App[None]):
    """Grok Imagine Cinematic Studio terminal UI."""

    TITLE = "Cinematic Studio"
    SUB_TITLE = "Dashboard · Launcher · Cockpit"
    CSS = """
    #home-scroll { height: 1fr; }
    #launcher-hint { padding: 1 2; color: $text-muted; }
    #out-title { padding: 1 2; text-style: bold; }
    #out-body { padding: 0 2 1 2; }
    #cockpit-hint, #form-title, #form-errors, #confirm-body, #confirm-hint {
        padding: 0 2;
    }
    #form-fields { height: 1fr; padding: 0 2; }
    #help-dialog {
        width: 60;
        height: auto;
        border: heavy $accent;
        background: $surface;
        padding: 1 2;
        align: center middle;
    }
    HelpScreen { align: center middle; }
    """

    def __init__(self, interval: float = 5.0) -> None:
        super().__init__()
        self.refresh_interval = max(1.0, float(interval))

    def on_mount(self) -> None:
        self.push_screen(HomeScreen())
        self.set_interval(self.refresh_interval, self._auto_refresh)

    def _auto_refresh(self) -> None:
        screen = self.screen
        if isinstance(screen, HomeScreen):
            screen.action_refresh()


def run_tui(*, interval: float = 5.0) -> None:
    """Run the studio TUI (blocking). Caller must ensure TTY + Textual installed."""
    StudioTUI(interval=interval).run()
