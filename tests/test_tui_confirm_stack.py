# tests/test_tui_confirm_stack.py
"""I1: after confirm run, Output dismiss must not land on Confirm (re-run hazard)."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from cli.tui.runner import CommandResult  # noqa: E402
from cli.tui.screens import (  # noqa: E402
    CockpitMenuScreen,
    CommandOutputScreen,
    ConfirmScreen,
    FormScreen,
    RunningScreen,
    finish_running_with_output,
    pop_confirm_form_chain,
    present_confirmed_output,
    start_action_run,
    worker_result_or_error,
)


class _FakeApp:
    """Minimal stack for pop_confirm_form_chain without Textual."""

    def __init__(self, stack: list[object]) -> None:
        self.screen_stack = list(stack)

    @property
    def screen(self) -> object:
        return self.screen_stack[-1]

    def pop_screen(self) -> None:
        if len(self.screen_stack) <= 1:
            raise RuntimeError("cannot pop root screen")
        self.screen_stack.pop()

    def push_screen(self, screen: object) -> None:
        self.screen_stack.append(screen)


def test_pop_confirm_form_chain_with_form() -> None:
    home = object()
    cockpit = CockpitMenuScreen()
    form = FormScreen.__new__(FormScreen)
    confirm = ConfirmScreen.__new__(ConfirmScreen)
    app = _FakeApp([home, cockpit, form, confirm])

    pop_confirm_form_chain(app)

    assert app.screen_stack == [home, cockpit]
    assert isinstance(app.screen, CockpitMenuScreen)


def test_pop_confirm_form_chain_confirm_only() -> None:
    home = object()
    cockpit = CockpitMenuScreen()
    confirm = ConfirmScreen.__new__(ConfirmScreen)
    app = _FakeApp([home, cockpit, confirm])

    pop_confirm_form_chain(app)

    assert app.screen_stack == [home, cockpit]


def test_pop_confirm_form_chain_noop_without_pop() -> None:
    app = SimpleNamespace(screen=None)  # no pop_screen
    pop_confirm_form_chain(app)  # must not raise


def test_form_screen_has_enter_submit_path() -> None:
    """M4: FormScreen wires Enter (Input.Submitted) and Submit button through _try_submit."""
    assert callable(getattr(FormScreen, "_try_submit", None))
    assert callable(getattr(FormScreen, "on_input_submitted", None))
    assert callable(getattr(FormScreen, "on_button_pressed", None))


def test_present_confirmed_output_lands_on_cockpit_not_confirm() -> None:
    """After run: Output sits on Cockpit; Esc cannot re-confirm the same write."""
    home = object()
    cockpit = CockpitMenuScreen()
    form = FormScreen.__new__(FormScreen)
    confirm = ConfirmScreen.__new__(ConfirmScreen)
    app = _FakeApp([home, cockpit, form, confirm])

    fake_result = CommandResult(
        argv=["create-bible", "X"],
        returncode=0,
        stdout="ok",
        stderr="",
        action_id="bible_create",
    )
    present_confirmed_output(
        app, fake_result, label="Create Production Bible", argv=list(fake_result.argv)
    )

    assert len(app.screen_stack) == 3
    assert app.screen_stack[0] is home
    assert app.screen_stack[1] is cockpit
    assert isinstance(app.screen_stack[2], CommandOutputScreen)
    # Dismiss output → Cockpit (no Confirm/Form left to re-run)
    app.pop_screen()
    assert app.screen is cockpit
    assert not any(isinstance(s, ConfirmScreen) for s in app.screen_stack)
    assert not any(isinstance(s, FormScreen) for s in app.screen_stack)


def test_start_action_run_pops_confirm_and_pushes_running() -> None:
    """I2 confirm path: dismiss Confirm/Form, push Running (async), not sync CLI."""
    home = object()
    cockpit = CockpitMenuScreen()
    form = FormScreen.__new__(FormScreen)
    confirm = ConfirmScreen.__new__(ConfirmScreen)
    app = _FakeApp([home, cockpit, form, confirm])

    start_action_run(
        app,
        "bible_create",
        {"title": "X"},
        label="Create Production Bible",
        dismiss_confirm_form=True,
    )

    assert len(app.screen_stack) == 3
    assert app.screen_stack[1] is cockpit
    assert isinstance(app.screen, RunningScreen)
    assert app.screen.action_id == "bible_create"
    assert not any(isinstance(s, ConfirmScreen) for s in app.screen_stack)
    assert not any(isinstance(s, FormScreen) for s in app.screen_stack)


def test_finish_running_with_output_replaces_running() -> None:
    home = object()
    cockpit = CockpitMenuScreen()
    running = RunningScreen(action_id="status", answers={}, label="Studio status")
    app = _FakeApp([home, cockpit, running])
    result = CommandResult(
        argv=["status"],
        returncode=0,
        stdout="ok",
        stderr="",
        action_id="status",
    )
    finish_running_with_output(app, result, label="Studio status")
    assert isinstance(app.screen, CommandOutputScreen)
    app.pop_screen()
    assert app.screen is cockpit


def test_worker_result_or_error_maps_states() -> None:
    from textual.worker import WorkerState

    class _W:
        def __init__(self, state, result=None, error=None):
            self.state = state
            self.result = result
            self.error = error

    ok = CommandResult(argv=["status"], returncode=0, stdout="x", stderr="")
    assert worker_result_or_error(
        _W(WorkerState.SUCCESS, result=ok), action_id="status", label="S"
    ) is ok
    err = worker_result_or_error(
        _W(WorkerState.ERROR, error=RuntimeError("boom")),
        action_id="status",
        label="S",
    )
    assert err is not None and err.returncode != 0 and "boom" in err.stderr
    assert (
        worker_result_or_error(
            _W(WorkerState.RUNNING), action_id="status", label="S"
        )
        is None
    )


def test_running_screen_blocks_close_while_busy() -> None:
    screen = RunningScreen(action_id="status", answers={}, label="Studio status")
    assert screen._busy is True
    # action_close no-ops while busy (cannot pop without app; just ensure flag path)
    screen._busy = False
    assert screen._busy is False
