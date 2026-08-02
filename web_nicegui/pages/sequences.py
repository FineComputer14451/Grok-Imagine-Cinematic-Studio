"""NiceGUI Sequences page — list / init / add-clip / show via execute_action."""

from __future__ import annotations

from typing import Any

from web_nicegui.lib.actions_ui import (
    _format_result,
    _set_md,
    build_action_form,
    run_registered,
)


def build_sequences_page(ui: Any) -> None:
    ui.label("Sequences").classes("text-h5 text-weight-bold")
    ui.label(
        "Long-form chain planning via ActionSpec + execute_action (in-process). "
        "Mutating actions keep the same confirm gates as the TUI cockpit."
    ).classes("text-caption text-grey-7 q-mb-md")

    with ui.card().classes("w-full q-mb-md"):
        ui.label("Sequences").classes("text-subtitle1 text-weight-medium")
        list_box = ui.markdown("_Loading sequences…_")

    def refresh_list() -> None:
        result = run_registered("sequence_list")
        _set_md(list_box, _format_result(result, limit=12000))

    with ui.row().classes("q-mb-md gap-2"):
        ui.button("Refresh list", icon="refresh", on_click=refresh_list).props("outline")

    with ui.tabs().classes("w-full") as tabs:
        tab_init = ui.tab("Init")
        tab_clip = ui.tab("Add clip")
        tab_show = ui.tab("Show")
        tab_handoff = ui.tab("Handoff")
        tab_estimate = ui.tab("Quota estimate")
    with ui.tab_panels(tabs, value=tab_init).classes("w-full"):
        with ui.tab_panel(tab_init):
            build_action_form(ui, "sequence_init", on_done=lambda _r: refresh_list())
        with ui.tab_panel(tab_clip):
            build_action_form(ui, "sequence_add_clip", on_done=lambda _r: refresh_list())
        with ui.tab_panel(tab_show):
            build_action_form(ui, "sequence_show", force_confirm=False)
        with ui.tab_panel(tab_handoff):
            build_action_form(ui, "sequence_handoff")
        with ui.tab_panel(tab_estimate):
            build_action_form(ui, "quota_sequence_estimate", force_confirm=False)

    ui.timer(0.05, refresh_list, once=True)
