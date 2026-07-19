"""Textual screens for studio TUI."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, VerticalScroll
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Markdown,
    Static,
)

from cli.tui.catalog import LAUNCHER_CATALOG, LauncherEntry
from cli.tui.forms import (
    COCKPIT_ORDER,
    COCKPIT_WORKFLOWS,
    answers_to_argv,
    default_answers,
    summarize_action,
    validate_answers,
)
from cli.tui.runner import CommandResult, run_cli_command
from cli.tui.widgets import format_error_panel, format_form_errors, format_home_markdown


class HomeScreen(Screen[None]):
    """Live dashboard home."""

    BINDINGS = [
        Binding("r", "refresh", "Refresh"),
        Binding("l", "launcher", "Launcher"),
        Binding("c", "cockpit", "Cockpit"),
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

    def action_cockpit(self) -> None:
        self.app.push_screen(CockpitMenuScreen())

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


class CockpitMenuScreen(Screen[None]):
    """Production workflows: Bible / DNA / Sequence / Quota / Models."""

    BINDINGS = [
        Binding("escape", "close", "Back"),
        Binding("h", "close", "Home"),
        Binding("q", "quit_app", "Quit"),
        Binding("question_mark", "help", "Help"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(
            "Cockpit — production workflows · Enter to open · Esc back",
            id="cockpit-hint",
        )
        yield ListView(
            *[
                ListItem(
                    Label(
                        f"{COCKPIT_WORKFLOWS[wid].label}  "
                        f"[dim]{COCKPIT_WORKFLOWS[wid].description}[/dim]"
                    ),
                    id=f"wf-{wid}",
                )
                for wid in COCKPIT_ORDER
            ],
            id="cockpit-list",
        )
        yield Footer()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id or ""
        wid = item_id.removeprefix("wf-")
        spec = COCKPIT_WORKFLOWS.get(wid)
        if spec is None:
            return
        if not spec.fields and not spec.needs_confirm:
            argv = answers_to_argv(wid, {})
            result = run_cli_command(argv)
            self.app.push_screen(
                CommandOutputScreen(result=result, label=spec.label, argv=argv)
            )
            return
        self.app.push_screen(FormScreen(workflow_id=wid))

    def action_close(self) -> None:
        self.app.pop_screen()

    def action_help(self) -> None:
        self.app.push_screen(HelpScreen())

    def action_quit_app(self) -> None:
        self.app.exit()


class FormScreen(Screen[None]):
    """Collect answers for a cockpit workflow."""

    BINDINGS = [
        Binding("escape", "close", "Back"),
        Binding("q", "quit_app", "Quit"),
    ]

    def __init__(self, workflow_id: str) -> None:
        super().__init__()
        self.workflow_id = workflow_id
        self.spec = COCKPIT_WORKFLOWS[workflow_id]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(f"{self.spec.label}", id="form-title")
        yield Label(self.spec.description, id="form-desc")
        yield Static("", id="form-errors")
        with VerticalScroll(id="form-fields"):
            answers = default_answers(self.workflow_id)
            for field in self.spec.fields:
                yield Label(f"{field.label}" + (" *" if field.required else ""))
                yield Input(
                    value=answers.get(field.key, field.default),
                    placeholder=field.help or field.key,
                    id=f"field-{field.key}",
                )
        yield Button("Submit", id="form-submit", variant="primary")
        yield Button("Cancel", id="form-cancel")
        yield Footer()

    def _collect(self) -> dict[str, str]:
        out: dict[str, str] = {}
        for field in self.spec.fields:
            widget = self.query_one(f"#field-{field.key}", Input)
            out[field.key] = widget.value
        return out

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "form-cancel":
            self.action_close()
            return
        if event.button.id == "form-submit":
            answers = self._collect()
            errors = validate_answers(self.workflow_id, answers)
            err_widget = self.query_one("#form-errors", Static)
            if errors:
                err_widget.update(format_form_errors(errors))
                return
            err_widget.update("")
            self.app.push_screen(
                ConfirmScreen(workflow_id=self.workflow_id, answers=answers)
            )

    def action_close(self) -> None:
        self.app.pop_screen()

    def action_quit_app(self) -> None:
        self.app.exit()


class ConfirmScreen(Screen[None]):
    """Confirm argv before running a mutating cockpit workflow."""

    BINDINGS = [
        Binding("y", "confirm", "Run"),
        Binding("n", "close", "Cancel"),
        Binding("escape", "close", "Cancel"),
        Binding("enter", "confirm", "Run"),
        Binding("q", "quit_app", "Quit"),
    ]

    def __init__(self, workflow_id: str, answers: dict[str, str]) -> None:
        super().__init__()
        self.workflow_id = workflow_id
        self.answers = answers
        self.spec = COCKPIT_WORKFLOWS[workflow_id]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(summarize_action(self.workflow_id, self.answers), id="confirm-body")
        yield Label("y / Enter = run · n / Esc = cancel", id="confirm-hint")
        yield Button("Run", id="confirm-run", variant="primary")
        yield Button("Cancel", id="confirm-cancel")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-cancel":
            self.action_close()
        elif event.button.id == "confirm-run":
            self.action_confirm()

    def action_confirm(self) -> None:
        argv = answers_to_argv(self.workflow_id, self.answers)
        result = run_cli_command(argv)
        self.app.push_screen(
            CommandOutputScreen(
                result=result,
                label=self.spec.label,
                argv=argv,
            )
        )

    def action_close(self) -> None:
        self.app.pop_screen()

    def action_quit_app(self) -> None:
        self.app.exit()


class CommandOutputScreen(Screen[None]):
    """Show captured CLI output."""

    BINDINGS = [
        Binding("escape", "close", "Back"),
        Binding("q", "quit_app", "Quit"),
    ]

    def __init__(
        self,
        result: CommandResult,
        *,
        label: str | None = None,
        argv: list[str] | None = None,
        entry: LauncherEntry | None = None,
    ) -> None:
        super().__init__()
        if entry is not None:
            label = entry.label
            argv = list(entry.argv)
        self.entry = entry
        self.label = label or "Command"
        self.argv = list(argv or result.argv)
        self.result = result

    def compose(self) -> ComposeResult:
        yield Header()
        code = self.result.returncode
        status = "OK" if code == 0 and not self.result.timed_out else f"FAIL ({code})"
        title = f"{self.label} · {status} · `{' '.join(self.argv)}`"
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
                        "c  Open cockpit (Bible / DNA / Sequence / Quota / Models)",
                        "h  Home / back",
                        "Esc  Back",
                        "?  This help",
                        "q  Quit",
                        "",
                        "Launcher runs safe read-only CLI commands only.",
                        "Cockpit forms confirm before write. No spend / wizard in TUI.",
                        "y/n on confirm run/cancel.",
                        "Wizards and spend flows stay on the classic CLI.",
                    ]
                ),
                id="help-body",
            ),
            id="help-dialog",
        )

    def action_close(self) -> None:
        self.app.pop_screen()
