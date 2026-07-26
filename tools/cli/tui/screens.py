"""Textual screens for studio TUI."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, VerticalScroll
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Static,
)
from textual.worker import Worker, WorkerState

from cli.tui.actions import (
    ActionSpec,
    default_answers,
    get_action,
    menu_rows,
    summarize_action,
    validate_answers,
)
from cli.tui.runner import CommandResult, run_action
from cli.tui.widgets import (
    HOME_MODE_PANELS,
    HOME_VIEW_MODES,
    format_attention_panel,
    format_chain_qa_panel,
    format_characters_panel,
    format_convergence_panel,
    format_delivery_panel,
    format_form_errors,
    format_home_error,
    format_home_hints,
    format_jobs_panel,
    format_parallel_briefs_panel,
    format_produce_gate_next_steps,
    format_quota_panel,
    format_readiness_panel,
    format_sequences_panel,
    format_status_strip,
    format_studio_panel,
    next_home_mode,
    strip_severity,
)


def pop_confirm_form_chain(app: object) -> None:
    """Pop Confirm (+ Form if present) so Output dismiss lands on Cockpit/Launcher.

    Call while Confirm is the active screen, before pushing CommandOutput.
    Prevents Esc → Confirm re-running the same mutating argv (I1).
    """
    pop = getattr(app, "pop_screen", None)
    if not callable(pop):
        return
    pop()  # leave Confirm
    screen = getattr(app, "screen", None)
    if isinstance(screen, FormScreen):
        pop()  # leave Form → CockpitMenu or Launcher


def present_confirmed_output(
    app: object,
    result: CommandResult,
    *,
    label: str,
    argv: list[str],
) -> None:
    """After a confirm run: drop Confirm/Form, then show CommandOutput on the menu."""
    pop_confirm_form_chain(app)
    push = getattr(app, "push_screen", None)
    if not callable(push):
        return
    push(CommandOutputScreen(result=result, label=label, argv=list(argv)))


def start_action_run(
    app: object,
    action_id: str,
    answers: dict[str, str] | None = None,
    *,
    label: str,
    dismiss_confirm_form: bool = False,
) -> None:
    """Push RunningScreen (async worker). Optionally drop Confirm/Form first (I1+I2)."""
    if dismiss_confirm_form:
        pop_confirm_form_chain(app)
    push = getattr(app, "push_screen", None)
    if not callable(push):
        return
    push(
        RunningScreen(
            action_id=action_id,
            answers=dict(answers or {}),
            label=label,
        )
    )


def finish_running_with_output(
    app: object,
    result: CommandResult,
    *,
    label: str,
) -> None:
    """Pop RunningScreen and push CommandOutput (call while Running is active)."""
    pop = getattr(app, "pop_screen", None)
    push = getattr(app, "push_screen", None)
    if not callable(pop) or not callable(push):
        return
    pop()
    push(
        CommandOutputScreen(
            result=result,
            label=label,
            argv=list(result.argv),
        )
    )


def worker_result_or_error(
    worker: Worker[CommandResult],
    *,
    action_id: str,
    label: str,
) -> CommandResult | None:
    """Map a finished worker to CommandResult; None if still running / cancelled."""
    if worker.state is WorkerState.SUCCESS:
        result = worker.result
        if isinstance(result, CommandResult):
            return result
        return CommandResult(
            argv=[],
            returncode=1,
            stdout="",
            stderr=f"Unexpected worker result for {label}",
            action_id=action_id,
        )
    if worker.state is WorkerState.ERROR:
        err = getattr(worker, "error", None)
        msg = f"{type(err).__name__}: {err}" if err else "Worker failed"
        return CommandResult(
            argv=[],
            returncode=1,
            stdout="",
            stderr=msg,
            action_id=action_id,
        )
    return None


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
        """Launch CLI on a worker thread (I2 — does not block the UI loop)."""
        spec = get_action(action_id)
        start_action_run(
            self.app,
            action_id,
            answers,
            label=spec.label,
            dismiss_confirm_form=False,
        )


class HomeScreen(Screen[None]):
    """Live multi-panel ops dashboard home."""

    BINDINGS = [
        Binding("r", "refresh", "Refresh"),
        Binding("s", "quota_sync", "Quota sync"),
        Binding("d", "doctor", "Doctor"),
        Binding("v", "validate", "Validate"),
        Binding("m", "models_verify", "Models"),
        Binding("k", "stack", "Stack"),
        Binding("l", "launcher", "Launcher"),
        Binding("c", "cockpit", "Cockpit"),
        Binding("1", "view_compact", "Compact"),
        Binding("2", "view_ops", "Ops"),
        Binding("3", "view_full", "Full"),
        Binding("tab", "view_cycle", "Cycle view"),
        Binding("p", "toggle_pause", "Pause"),
        Binding("q", "quit_app", "Quit"),
        Binding("question_mark", "help", "Help"),
    ]

    _STRIP_SEV_CLASSES = ("sev-ok", "sev-warn", "sev-critical")
    _ALL_PANELS = (
        "panel-readiness",
        "panel-convergence",
        "panel-briefs",
        "panel-delivery",
        "panel-quota",
        "panel-studio",
        "panel-sequences",
        "panel-chain-qa",
        "panel-characters",
        "panel-jobs",
        "home-mid",
        "home-row-gate",
    )

    def __init__(self) -> None:
        super().__init__()
        self.view_mode: str = "ops"
        self.auto_refresh_paused: bool = False
        self._last_snap: dict | None = None
        self._jobs_available: bool = False
        self._briefs_available: bool = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with VerticalScroll(id="home-scroll"):
            yield Static("", id="home-error", classes="home-error hidden")
            yield Static("", id="status-strip", classes="home-strip sev-ok")
            yield Static("", id="panel-attention", classes="home-panel home-attention")
            with Horizontal(id="home-row-gate", classes="home-row"):
                yield Static("", id="panel-readiness", classes="home-panel")
                yield Static("", id="panel-convergence", classes="home-panel")
            yield Static("", id="panel-briefs", classes="home-panel")
            yield Static("", id="panel-delivery", classes="home-panel")
            with Horizontal(id="home-mid", classes="home-mid"):
                yield Static("", id="panel-quota", classes="home-panel")
                yield Static("", id="panel-studio", classes="home-panel")
            yield Static("", id="panel-sequences", classes="home-panel")
            yield Static("", id="panel-chain-qa", classes="home-panel")
            yield Static("", id="panel-characters", classes="home-panel")
            yield Static("", id="panel-jobs", classes="home-panel hidden")
            yield Static(
                format_home_hints(mode="ops", paused=False),
                id="home-hints",
                classes="home-hints",
            )
        yield Footer()

    def on_mount(self) -> None:
        self.action_refresh()

    def _set_panel(self, widget_id: str, text: str, *, hide: bool = False) -> None:
        w = self.query_one(f"#{widget_id}", Static)
        w.update(text)
        if hide:
            w.add_class("hidden")
        else:
            w.remove_class("hidden")

    def _set_strip_severity(self, severity: str) -> None:
        strip = self.query_one("#status-strip", Static)
        for cls in self._STRIP_SEV_CLASSES:
            strip.remove_class(cls)
        strip.add_class(f"sev-{severity}" if severity in ("ok", "warn", "critical") else "sev-ok")
        attention = self.query_one("#panel-attention", Static)
        for cls in self._STRIP_SEV_CLASSES:
            attention.remove_class(cls)
        attention.add_class(
            f"sev-{severity}" if severity in ("ok", "warn", "critical") else "sev-ok"
        )

    def _apply_view_mode(self) -> None:
        """Show/hide panels based on view_mode + empty content flags."""
        mode = self.view_mode if self.view_mode in HOME_VIEW_MODES else "ops"
        allowed = set(HOME_MODE_PANELS.get(mode, HOME_MODE_PANELS["ops"]))
        # Row containers: show if either child is allowed
        if "panel-quota" in allowed or "panel-studio" in allowed:
            allowed.add("home-mid")
        if "panel-readiness" in allowed or "panel-convergence" in allowed:
            allowed.add("home-row-gate")
        # Collapse empty optional panels even in full mode
        if not self._jobs_available:
            allowed.discard("panel-jobs")
        if not self._briefs_available and mode != "full":
            allowed.discard("panel-briefs")
        if mode == "full" and not self._briefs_available:
            # keep briefs visible with empty state in full mode
            allowed.add("panel-briefs")

        for wid in self._ALL_PANELS:
            try:
                w = self.query_one(f"#{wid}")
            except Exception:
                continue
            if wid in allowed:
                w.remove_class("hidden")
            else:
                w.add_class("hidden")

        # Individual children of mid/gate still need hide if not allowed
        for child in ("panel-quota", "panel-studio", "panel-readiness", "panel-convergence"):
            try:
                w = self.query_one(f"#{child}")
            except Exception:
                continue
            if child in allowed:
                w.remove_class("hidden")
            else:
                w.add_class("hidden")

        self._set_panel(
            "home-hints",
            format_home_hints(mode=mode, paused=self.auto_refresh_paused),
        )
        pause = " · paused" if self.auto_refresh_paused else ""
        try:
            self.app.sub_title = f"Home [{mode}]{pause} · Launcher · Cockpit"
        except Exception:
            pass

    def action_view_compact(self) -> None:
        self.view_mode = "compact"
        self._apply_view_mode()

    def action_view_ops(self) -> None:
        self.view_mode = "ops"
        self._apply_view_mode()

    def action_view_full(self) -> None:
        self.view_mode = "full"
        self._apply_view_mode()

    def action_view_cycle(self) -> None:
        self.view_mode = next_home_mode(self.view_mode)
        self._apply_view_mode()

    def action_toggle_pause(self) -> None:
        self.auto_refresh_paused = not self.auto_refresh_paused
        self._apply_view_mode()

    def action_refresh(self) -> None:
        try:
            from cli.dashboard import build_studio_dashboard

            snap = build_studio_dashboard()
            try:
                from quota_sync import ledger_recon_alignment

                snap["quota_alignment"] = ledger_recon_alignment()
            except Exception:
                pass

            self._last_snap = snap
            pb = snap.get("parallel_briefs") or {}
            self._briefs_available = int(pb.get("count") or 0) > 0 or bool(pb.get("logs"))
            jobs = format_jobs_panel(snap)
            self._jobs_available = jobs is not None

            self._set_panel("home-error", "", hide=True)
            self._set_panel("status-strip", format_status_strip(snap))
            self._set_strip_severity(strip_severity(snap))
            self._set_panel("panel-attention", format_attention_panel(snap))
            self._set_panel("panel-readiness", format_readiness_panel(snap))
            self._set_panel("panel-convergence", format_convergence_panel(snap))
            self._set_panel("panel-briefs", format_parallel_briefs_panel(snap))
            self._set_panel("panel-delivery", format_delivery_panel(snap))
            self._set_panel("panel-quota", format_quota_panel(snap))
            self._set_panel("panel-studio", format_studio_panel(snap))
            self._set_panel("panel-sequences", format_sequences_panel(snap))
            self._set_panel("panel-chain-qa", format_chain_qa_panel(snap))
            self._set_panel("panel-characters", format_characters_panel(snap))
            if jobs:
                self._set_panel("panel-jobs", jobs, hide=False)
            else:
                self._set_panel("panel-jobs", "", hide=True)
            self._apply_view_mode()
        except Exception as exc:  # noqa: BLE001 — surface any snapshot failure
            self._set_panel("home-error", format_home_error(str(exc)), hide=False)
            for wid in (
                "status-strip",
                "panel-attention",
                "panel-readiness",
                "panel-convergence",
                "panel-briefs",
                "panel-delivery",
                "panel-quota",
                "panel-studio",
                "panel-sequences",
                "panel-chain-qa",
                "panel-characters",
                "panel-jobs",
            ):
                self._set_panel(wid, "", hide=True)

    def action_quota_sync(self) -> None:
        """Run exclusive-cascade recon from home (no Imagine spend)."""
        start_action_run(
            self.app,
            "quota_sync",
            {},
            label="Quota sync",
            dismiss_confirm_form=False,
        )

    def action_doctor(self) -> None:
        """Quick Grok Doctor health check from home."""
        start_action_run(
            self.app,
            "doctor_quick",
            {},
            label="Grok Doctor (quick)",
            dismiss_confirm_form=False,
        )

    def action_validate(self) -> None:
        """Studio validate from home."""
        start_action_run(
            self.app,
            "validate",
            {},
            label="Studio validate",
            dismiss_confirm_form=False,
        )

    def action_models_verify(self) -> None:
        """Models verify from home (J1 health shortcut)."""
        start_action_run(
            self.app,
            "models_verify",
            {},
            label="Models Verify",
            dismiss_confirm_form=False,
        )

    def action_stack(self) -> None:
        """Model stack summary from home (J1 health shortcut)."""
        start_action_run(
            self.app,
            "stack",
            {},
            label="Model stack",
            dismiss_confirm_form=False,
        )

    def action_launcher(self) -> None:
        self.app.push_screen(LauncherScreen())

    def action_cockpit(self) -> None:
        self.app.push_screen(CockpitMenuScreen())

    def action_help(self) -> None:
        self.app.push_screen(HelpScreen())

    def action_quit_app(self) -> None:
        self.app.exit()


class ActionListScreen(StudioScreen):
    """Pick an action from a surface (launcher or cockpit), with type-to-filter."""

    surface: str = "launcher"
    list_id: str = "action-list"
    hint_id: str = "list-hint"
    hint_text: str = ""

    def __init__(self) -> None:
        super().__init__()
        self._filter: str = ""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(self.hint_text, id=self.hint_id)
        yield Input(
            placeholder="Filter actions… (type to narrow list)",
            id="filter-input",
        )
        yield ListView(*self._build_items(""), id=self.list_id)
        yield Footer()

    def on_mount(self) -> None:
        try:
            self.query_one("#filter-input", Input).focus()
        except Exception:
            pass

    def _subtitle(self, spec: ActionSpec) -> str:
        if spec.has_form:
            return spec.description
        return " ".join(spec.base_argv)

    def _build_items(self, query: str) -> list[ListItem]:
        q = (query or "").strip().lower()
        items: list[ListItem] = []
        for kind, payload in menu_rows(self.surface):
            if kind == "group":
                assert isinstance(payload, str)
                # Always show group headers when any following actions match;
                # if filtering, only show groups that have at least one match later.
                if q:
                    # defer group until we know a match exists — include always for simplicity
                    # when any action under this group matches
                    continue
                items.append(
                    ListItem(
                        Label(f"[bold]── {payload} ──[/bold]"),
                        id=f"grp-{payload.lower().replace(' ', '-')}",
                        disabled=True,
                    )
                )
                continue
            assert isinstance(payload, ActionSpec)
            spec = payload
            hay = f"{spec.label} {spec.description} {spec.id} {' '.join(spec.base_argv)}".lower()
            if q and q not in hay:
                continue
            items.append(
                ListItem(
                    Label(f"{spec.label}  [dim]{self._subtitle(spec)}[/dim]"),
                    id=f"act-{spec.id}",
                )
            )
        # When filtering: re-add group headers for matching actions only
        if q:
            filtered: list[ListItem] = []
            last_group = ""
            for kind, payload in menu_rows(self.surface):
                if kind == "group":
                    assert isinstance(payload, str)
                    last_group = payload
                    continue
                assert isinstance(payload, ActionSpec)
                spec = payload
                hay = f"{spec.label} {spec.description} {spec.id} {' '.join(spec.base_argv)}".lower()
                if q not in hay:
                    continue
                if last_group:
                    gid = f"grp-{last_group.lower().replace(' ', '-')}-f"
                    if not any(i.id == gid for i in filtered):
                        filtered.append(
                            ListItem(
                                Label(f"[bold]── {last_group} ──[/bold]"),
                                id=gid,
                                disabled=True,
                            )
                        )
                filtered.append(
                    ListItem(
                        Label(f"{spec.label}  [dim]{self._subtitle(spec)}[/dim]"),
                        id=f"act-{spec.id}",
                    )
                )
            return filtered or [
                ListItem(Label("[dim]No matching actions[/dim]"), id="grp-empty", disabled=True)
            ]
        if not items:
            items.append(
                ListItem(Label("[dim]No actions[/dim]"), id="grp-empty", disabled=True)
            )
        return items

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id != "filter-input":
            return
        self._filter = event.value or ""
        try:
            lv = self.query_one(f"#{self.list_id}", ListView)
        except Exception:
            return
        lv.clear()
        for item in self._build_items(self._filter):
            lv.append(item)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id or ""
        if item_id.startswith("grp-"):
            return
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
    hint_text = "Launcher — filter · Enter run · Esc back · h home"


class CockpitMenuScreen(ActionListScreen):
    """Production workflows: Bible / DNA / Sequence / Quota / Models."""

    surface = "cockpit"
    list_id = "cockpit-list"
    hint_id = "cockpit-hint"
    hint_text = (
        "Cockpit — filter · scaffold Bible/DNA/Sequence/Quota/Delivery · Enter · Esc · h home"
    )


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

    def _try_submit(self) -> None:
        """Validate then Confirm (mutating) or run immediately (read-only forms)."""
        answers = self._collect()
        errors = validate_answers(self.action_id, answers)
        err_widget = self.query_one("#form-errors", Static)
        if errors:
            err_widget.update(format_form_errors(errors))
            return
        err_widget.update("")
        if self.spec.needs_confirm:
            self.app.push_screen(
                ConfirmScreen(action_id=self.action_id, answers=answers)
            )
            return
        # Read-only form (e.g. dna show) — skip Confirm, run async.
        start_action_run(
            self.app,
            self.action_id,
            answers,
            label=self.spec.label,
            dismiss_confirm_form=False,
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "form-cancel":
            self.action_close()
            return
        if event.button.id == "form-submit":
            self._try_submit()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Enter in any field submits the form (M4)."""
        event.stop()
        self._try_submit()


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
        self._started = False

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
        if self._started:
            return
        self._started = True
        # Drop Confirm (+ Form) then run async so UI stays responsive (I1 + I2).
        start_action_run(
            self.app,
            self.action_id,
            self.answers,
            label=self.spec.label,
            dismiss_confirm_form=True,
        )


class RunningScreen(StudioScreen):
    """Show 'Running…' while CLI executes on a worker thread (I2)."""

    BINDINGS = [
        Binding("escape", "close", "Back"),
        Binding("q", "quit_app", "Quit"),
    ]

    def __init__(
        self,
        action_id: str,
        answers: dict[str, str] | None = None,
        *,
        label: str,
    ) -> None:
        super().__init__()
        self.action_id = action_id
        self.answers = dict(answers or {})
        self.label = label
        self._busy = True
        self._worker: Worker[CommandResult] | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(f"Running: {self.label}…", id="running-title")
        yield Label(
            "CLI is running in the background — UI stays responsive.\n"
            "Please wait (Esc/q disabled until finished).",
            id="running-hint",
        )
        yield Footer()

    def on_mount(self) -> None:
        self._worker = self.run_worker(
            self._work,
            name=f"cli-{self.action_id}",
            group="cli-action",
            description=self.label,
            exclusive=True,
            thread=True,
            exit_on_error=False,
        )

    def _work(self) -> CommandResult:
        return run_action(self.action_id, self.answers)

    def action_close(self) -> None:
        if self._busy:
            return
        super().action_close()

    def action_quit_app(self) -> None:
        if self._busy:
            return
        super().action_quit_app()

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if self._worker is not None and event.worker is not self._worker:
            return
        if event.worker.name != f"cli-{self.action_id}":
            return
        result = worker_result_or_error(
            event.worker,
            action_id=self.action_id,
            label=self.label,
        )
        if result is None:
            return
        self._busy = False
        finish_running_with_output(self.app, result, label=self.label)


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
        ok = code == 0 and not self.result.timed_out
        status = "OK" if ok else f"FAIL ({code})"
        title = f"{self.label} · {status} · `{' '.join(self.argv)}`"
        body = self.result.stdout
        if self.result.stderr:
            body = (body + "\n\n--- stderr ---\n" + self.result.stderr).strip()
        if not body:
            body = "(no output)"
        # Phase 2 produce-gate coaching after DNA / sequence / handoff steps
        action_id = getattr(self.result, "action_id", "") or ""
        tip = format_produce_gate_next_steps(action_id, ok=ok)
        if tip:
            body = f"{body}\n\n── Next ──\n{tip}"
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
                        "Home views",
                        "  1  Compact (strip + attention + readiness)",
                        "  2  Ops (default — gates + quota + chain QA)",
                        "  3  Full (all panels)",
                        "  Tab  Cycle views · p  Pause/resume auto-refresh",
                        "",
                        "Health / nav",
                        "  r  Refresh · s  Quota sync · d  Doctor · v  Validate",
                        "  m  Models · k  Stack · l  Launcher · c  Cockpit",
                        "  h  Home · Esc  Back · ?  Help · q  Quit",
                        "",
                        "Launcher / Cockpit: type in filter box to narrow actions.",
                        "Mutating forms confirm before write. No Imagine spend / wizard.",
                        "Polish/deliver cockpit entries use --dry-run only.",
                        "CLI runs on a background worker; Esc from output skips re-confirm.",
                    ]
                ),
                id="help-body",
            ),
            id="help-dialog",
        )

    def action_close(self) -> None:
        self.app.pop_screen()
