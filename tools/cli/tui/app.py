"""Textual application entry for cinematic-studio ui."""

from __future__ import annotations

from textual.app import App

from cli.tui.screens import HomeScreen


class StudioTUI(App[None]):
    """Grok Imagine Cinematic Studio terminal UI."""

    TITLE = "Cinematic Studio"
    SUB_TITLE = "Dashboard · Launcher · Cockpit"
    CSS = """
    #home-scroll { height: 1fr; padding: 0 1 1 1; }
    .home-strip {
        padding: 1 1 0 1;
        text-style: bold;
        color: $text;
        border: solid $accent;
        margin: 0 0 1 0;
    }
    .home-strip.sev-ok { border: solid $success; color: $text; }
    .home-strip.sev-warn { border: solid $warning; color: $warning; }
    .home-strip.sev-critical { border: heavy $error; color: $error; text-style: bold; }
    .home-attention.sev-ok { border: solid $success; }
    .home-attention.sev-warn { border: solid $warning; }
    .home-attention.sev-critical { border: heavy $error; }
    .home-mid { height: auto; margin-bottom: 1; }
    .home-panel {
        width: 1fr;
        padding: 0 1 1 1;
        border: solid $panel;
        margin: 0 0 1 0;
        color: $text;
    }
    #panel-quota { margin-right: 1; }
    .home-hints {
        padding: 0 1 1 1;
        color: $text-muted;
    }
    .home-error {
        padding: 1;
        border: heavy $error;
        color: $error;
        margin-bottom: 1;
    }
    .hidden { display: none; }
    #launcher-hint { padding: 1 2; color: $text-muted; }
    #out-title { padding: 1 2; text-style: bold; }
    #out-body { padding: 0 2 1 2; }
    #cockpit-hint, #launcher-hint, #form-title, #form-desc, #form-errors,
    #confirm-body, #confirm-hint, #running-title, #running-hint {
        padding: 0 2;
    }
    #running-title { text-style: bold; padding-top: 1; }
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
