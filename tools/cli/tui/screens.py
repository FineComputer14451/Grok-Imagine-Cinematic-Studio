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

from cli.tui.actions import (
    ActionSpec,
    actions_for,
    default_answers,
    get_action,
    summarize_action,
    validate_answers,
)
from cli.tui.runner import CommandResult, run_action
from cli.tui.widgets import format_error_panel, format_form_errors, format_home_markdown


class StudioScreen(Screen[None]):
    """Shared back / quit / help bindings for nested TUI screens."""

    BINDINGS = [
        Binding("escape", "close", "Back"),
        Binding("h", "pop_home", "Home"),
        Binding("q", "quit_app", "Quit"),
        Binding("question_mark", "help", "Help"),
    ]

    def action_close(self) -> None:
        self.app.pop_screen()

    def action_pop_home(self) -> None:
        """Pop until HomeScreen (or root)."""
        while len(self.app.screen_stack) > 1 and not isinstance(
            self.app.screen, HomeScreen
        ):
            self.app.pop_screen()

    def action_quit_app(self) -> None:
        self.app.exit()

    def action_help(self) -> None:
        self.app.push_screen(HelpScreen())

    def _show_result(self, result: CommandResult, *, label: str, argv: list[str]) -> None:
        self.app.push_screen(CommandOutputScreen(result=result, label=label, argv=argv))

    def _run_action(self, action_id: str, answers: dict[str, str] | None = None) -> None:
        spec = get_action(action_id)
        result = run_action(action_id, answers)
        self._show_result(result, label=spec.label, argv=list(result.argv))


class HomeScreen(Screen[None]):
    """Live dashboard home."""

    BINDINGS = [
        Binding("r", "refresh", "Refresh"),
        Binding("l", "launcher", "Launcher"),
        Binding("c", "cockpit", "Cockpit"),
        Binding("q", "quit_app", "Quit"),
        Binding("question_mark", "help", "Help"),
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

    def action_quit_app(self) -> None:
        self.app.exit()


class ActionListScreen(StudioScreen):
    """Pick an action from a surface (launcher or cockpit)."""

    surface: str = "launcher"
    list_id: str = "action-list"
    hint_id: str = "list-hint"
    hint_text: str = ""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(self.hint_text, id=self.hint_id)
        yield ListView(
            *[
                ListItem(
                    Label(
                        f"{spec.label}  [dim]{self._subtitle(spec)}[/dim]"
                    ),
                    id=f"act-{spec.id}",
                )
                for spec in actions_for(self.surface)
            ],
            id=self.list_id,
        )
        yield Footer()

    def _subtitle(self, spec: ActionSpec) -> str:
        if spec.has_form:
            return spec.description
        return " ".join(spec.base_argv)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id or ""
        action_id = item_id.removeprefix("act-")
        try:
            spec = get_action(action_id)
        except KeyError:
            return
        if self.surface not in spec.surfaces:
            return
        if not spec.has_form and not spec.needs_confirm:
            self._run_action(action_id, {})
            return
        if not spec.has_form and spec.needs_confirm:
            self.app.push_screen(ConfirmScreen(action_id=action_id, answers={}))
            return
        self.app.push_screen(FormScreen(action_id=action_id))


class LauncherScreen(ActionListScreen):
    """Pick a safe read-only CLI command."""

    surface = "launcher"
    list_id = "launcher-list"
    hint_id = "launcher-hint"
    hint_text = "Launcher — Enter to run · Esc back · h home"


class CockpitMenuScreen(ActionListScreen):
    """Production workflows: Bible / DNA / Sequence / Quota / Models."""

    surface = "cockpit"
    list_id = "cockpit-list"
    hint_id = "cockpit-hint"
    hint_text = "Cockpit — production workflows · Enter to open · Esc back · h home"


class FormScreen(StudioScreen):
    """Collect answers for a cockpit workflow."""

    BINDINGS = [
        Binding("escape", "close", "Back"),
        Binding("q", "quit_app", "Quit"),
    ]

    def __init__(self, action_id: str) -> None:
        super().__init__()
        self.action_id = action_id
        self.spec = get_action(action_id)

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(f"{self.spec.label}", id="form-title")
        yield Label(self.spec.description, id="form-desc")
        yield Static("", id="form-errors")
        with VerticalScroll(id="form-fields"):
            answers = default_answers(self.action_id)
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
            errors = validate_answers(self.action_id, answers)
            err_widget = self.query_one("#form-errors", Static)
            if errors:
                err_widget.update(format_form_errors(errors))
                return
            err_widget.update("")
            self.app.push_screen(
                ConfirmScreen(action_id=self.action_id, answers=answers)
            )


class ConfirmScreen(StudioScreen):
    """Confirm argv before running a mutating cockpit workflow."""

    BINDINGS = [
        Binding("y", "confirm", "Run"),
        Binding("n", "close", "Cancel"),
        Binding("escape", "close", "Cancel"),
        Binding("enter", "confirm", "Run"),
        Binding("q", "quit_app", "Quit"),
    ]

    def __init__(self, action_id: str, answers: dict[str, str]) -> None:
        super().__init__()
        self.action_id = action_id
        self.answers = answers
        self.spec = get_action(action_id)

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(summarize_action(self.action_id, self.answers), id="confirm-body")
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
        result = run_action(self.action_id, self.answers)
        self._show_result(
            result, label=self.spec.label, argv=list(result.argv)
        )


class CommandOutputScreen(StudioScreen):
    """Show captured CLI output."""

    BINDINGS = [
        Binding("escape", "close", "Back"),
        Binding("h", "pop_home", "Home"),
        Binding("q", "quit_app", "Quit"),
    ]

    def __init__(
        self,
        result: CommandResult,
        *,
        label: str,
        argv: list[str],
    ) -> None:
        super().__init__()
        self.label = label
        self.argv = list(argv)
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
                        "h  Pop to home",
                        "Esc  Back",
                        "?  This help",
                        "q  Quit",
                        "",
                        "Launcher runs safe read-only CLI commands only.",
                        "Cockpit forms confirm before write. No spend / wizard in TUI.",
                        "y/n on confirm run/cancel.",
                        "All runs go through the action allowlist (no free-form argv).",
                        "Wizards and spend flows stay on the classic CLI.",
                    ]
                ),
                id="help-body",
            ),
            id="help-dialog",
        )

    def action_close(self) -> None:
        self.app.pop_screen()
