"""Textual screens for studio TUI."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, VerticalScroll
from textual.screen import ModalScreen, Screen
from textual.widgets import Footer, Header, Label, ListItem, ListView, Markdown, Static

from cli.tui.catalog import LAUNCHER_CATALOG, LauncherEntry
from cli.tui.runner import CommandResult, run_cli_command
from cli.tui.widgets import format_error_panel, format_home_markdown


class HomeScreen(Screen[None]):
    """Live dashboard home."""

    BINDINGS = [
        Binding("r", "refresh", "Refresh"),
        Binding("l", "launcher", "Launcher"),
        Binding("q", "quit_app", "Quit"),
        Binding("question_mark", "help", "Help"),
        Binding("h", "home", "Home"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with VerticalScroll(id="home-scroll"):
            yield Markdown("", id="home-body")
        yield Footer()

    def on_mount(self) -> None:
        self.action_refresh()

    def action_refresh(self) -> None:
        body = self.query_one("#home-body", Markdown)
        try:
            from cli.dashboard import build_studio_dashboard

            snap = build_studio_dashboard()
            body.update(format_home_markdown(snap))
        except Exception as exc:  # noqa: BLE001 — surface any snapshot failure
            body.update(format_error_panel(str(exc)))

    def action_launcher(self) -> None:
        self.app.push_screen(LauncherScreen())

    def action_help(self) -> None:
        self.app.push_screen(HelpScreen())

    def action_home(self) -> None:
        pass  # already home

    def action_quit_app(self) -> None:
        self.app.exit()


class LauncherScreen(Screen[None]):
    """Pick a safe CLI command."""

    BINDINGS = [
        Binding("escape", "close", "Back"),
        Binding("h", "close", "Home"),
        Binding("q", "quit_app", "Quit"),
        Binding("question_mark", "help", "Help"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Launcher — Enter to run · Esc back", id="launcher-hint")
        yield ListView(
            *[
                ListItem(
                    Label(f"{e.label}  [dim]{' '.join(e.argv)}[/dim]"),
                    id=f"entry-{e.id}",
                )
                for e in LAUNCHER_CATALOG
            ],
            id="launcher-list",
        )
        yield Footer()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id or ""
        entry_id = item_id.removeprefix("entry-")
        entry = next((e for e in LAUNCHER_CATALOG if e.id == entry_id), None)
        if entry is None:
            return
        self._run_entry(entry)

    def _run_entry(self, entry: LauncherEntry) -> None:
        result = run_cli_command(list(entry.argv))
        self.app.push_screen(CommandOutputScreen(entry=entry, result=result))

    def action_close(self) -> None:
        self.app.pop_screen()

    def action_help(self) -> None:
        self.app.push_screen(HelpScreen())

    def action_quit_app(self) -> None:
        self.app.exit()


class CommandOutputScreen(Screen[None]):
    """Show captured CLI output."""

    BINDINGS = [
        Binding("escape", "close", "Back"),
        Binding("q", "quit_app", "Quit"),
    ]

    def __init__(self, entry: LauncherEntry, result: CommandResult) -> None:
        super().__init__()
        self.entry = entry
        self.result = result

    def compose(self) -> ComposeResult:
        yield Header()
        code = self.result.returncode
        status = "OK" if code == 0 and not self.result.timed_out else f"FAIL ({code})"
        title = f"{self.entry.label} · {status} · `{' '.join(self.entry.argv)}`"
        body = self.result.stdout
        if self.result.stderr:
            body = (body + "\n\n--- stderr ---\n" + self.result.stderr).strip()
        if not body:
            body = "(no output)"
        with VerticalScroll():
            yield Static(title, id="out-title")
            yield Static(body, id="out-body")
        yield Footer()

    def action_close(self) -> None:
        self.app.pop_screen()

    def action_quit_app(self) -> None:
        self.app.exit()


class HelpScreen(ModalScreen[None]):
    """Keybinding help."""

    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("q", "close", "Close"),
    ]

    def compose(self) -> ComposeResult:
        yield Container(
            Static(
                "\n".join(
                    [
                        "Studio TUI Help",
                        "",
                        "r  Refresh dashboard",
                        "l  Open launcher",
                        "h  Home / back",
                        "Esc  Back",
                        "?  This help",
                        "q  Quit",
                        "",
                        "Launcher runs safe read-only CLI commands only.",
                        "Wizards and spend flows stay on the classic CLI.",
                    ]
                ),
                id="help-body",
            ),
            id="help-dialog",
        )

    def action_close(self) -> None:
        self.app.pop_screen()
