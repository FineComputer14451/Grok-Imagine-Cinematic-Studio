"""NiceGUI helpers for ActionSpec forms + execute_action."""

from __future__ import annotations

from typing import Any, Callable

from studio_core.services.actions import ActionSpec, default_answers, get_action
from studio_core.services.execute import ActionResult, execute_action


def run_registered(
    action_id: str,
    answers: dict[str, str] | None = None,
    *,
    timeout: float = 90.0,
) -> ActionResult:
    """Execute a registered action in-process (web default)."""
    try:
        return execute_action(
            action_id,
            answers or {},
            mode="inprocess",
            timeout=timeout,
        )
    except Exception as exc:  # noqa: BLE001 — never crash the web shell
        return ActionResult(
            ok=False,
            argv=[],
            returncode=1,
            stdout="",
            stderr=f"{type(exc).__name__}: {exc}",
            errors=[str(exc)],
            timed_out=False,
            action_id=action_id,
            mode="inprocess",
        )


def _set_md(el: Any, value: str) -> None:
    value = value or ""
    if hasattr(el, "set_content"):
        try:
            el.set_content(value)
            return
        except Exception:
            pass
    if hasattr(el, "content"):
        el.content = value


def _format_result(result: ActionResult, *, limit: int = 8000) -> str:
    body = result.stdout or result.stderr or "(no output)"
    if len(body) > limit:
        body = body[:limit] + "\n…(truncated)"
    status = "OK" if result.ok else "FAILED"
    cmd = " ".join(result.argv) if result.argv else result.action_id or ""
    return (
        f"**{status}** · exit `{result.returncode}` · `cinematic-studio {cmd}`\n\n"
        f"```\n{body}\n```"
    )


def build_action_form(
    ui: Any,
    action_id: str,
    *,
    on_done: Callable[[ActionResult], None] | None = None,
    submit_label: str | None = None,
    force_confirm: bool | None = None,
) -> None:
    """Render a form for an ActionSpec and execute on submit."""
    spec: ActionSpec = get_action(action_id)
    answers = default_answers(action_id)
    fields: dict[str, Any] = {}

    with ui.card().classes("w-full q-mb-md"):
        ui.label(spec.label).classes("text-subtitle1 text-weight-medium")
        ui.label(spec.description).classes("text-caption text-grey-7 q-mb-sm")

        for field in spec.fields:
            default = answers.get(field.key, field.default or "")
            if field.choices:
                opts = {c: c for c in sorted(field.choices)}
                initial = default if default in field.choices else next(iter(opts))
                fields[field.key] = ui.select(opts, value=initial, label=field.label).classes(
                    "w-full"
                )
            elif field.coerce in {"int", "float"}:
                num_val = None
                if str(default).strip():
                    try:
                        num_val = float(default)
                    except ValueError:
                        num_val = None
                if field.coerce == "int":
                    fields[field.key] = ui.number(
                        label=field.label,
                        value=num_val,
                        format="%.0f",
                    ).classes("w-full")
                else:
                    fields[field.key] = ui.number(
                        label=field.label,
                        value=num_val,
                    ).classes("w-full")
            elif field.key in {"prompt", "core", "facial", "recap", "dialogue"}:
                fields[field.key] = (
                    ui.textarea(label=field.label, value=default)
                    .classes("w-full")
                    .props("autogrow")
                )
            else:
                fields[field.key] = ui.input(label=field.label, value=default).classes("w-full")

        result_box = ui.markdown("")
        needs_confirm = spec.needs_confirm if force_confirm is None else force_confirm

        def _collect() -> dict[str, str]:
            out: dict[str, str] = {}
            for key, el in fields.items():
                val = getattr(el, "value", None)
                if val is None:
                    out[key] = ""
                elif isinstance(val, float):
                    out[key] = str(int(val)) if val.is_integer() else str(val)
                else:
                    out[key] = str(val).strip()
            return out

        def _execute(ans: dict[str, str]) -> None:
            _set_md(result_box, "_Running…_")
            result = run_registered(action_id, ans)
            _set_md(result_box, _format_result(result))
            if on_done:
                on_done(result)

        def _submit() -> None:
            ans = _collect()
            if not needs_confirm:
                _execute(ans)
                return
            with ui.dialog() as dialog, ui.card().classes("min-w-[20rem]"):
                ui.label(f"Confirm: {spec.label}").classes("text-subtitle1")
                ui.label(spec.description).classes("text-caption")
                with ui.row().classes("q-mt-md"):
                    ui.button("Cancel", on_click=dialog.close).props("flat")

                    def _go() -> None:
                        dialog.close()
                        _execute(ans)

                    ui.button("Run", on_click=_go).props("color=primary")
            dialog.open()

        ui.button(
            submit_label or ("Run (confirm)" if needs_confirm else "Run"),
            on_click=_submit,
            icon="play_arrow",
        ).props("color=primary")


def quick_action_button(
    ui: Any,
    action_id: str,
    answers: dict[str, str] | None = None,
    *,
    label: str | None = None,
    on_done: Callable[[ActionResult], None] | None = None,
) -> None:
    """Button that runs a registered action (optional fixed answers)."""
    spec = get_action(action_id)
    result_box = ui.markdown("")

    def _click() -> None:
        _set_md(result_box, "_Running…_")
        result = run_registered(action_id, answers or {})
        _set_md(result_box, _format_result(result, limit=6000))
        if on_done:
            on_done(result)

    ui.button(label or spec.label, on_click=_click).props("outline")
