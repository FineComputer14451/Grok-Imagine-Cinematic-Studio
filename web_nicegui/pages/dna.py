"""NiceGUI DNA page — list / init / lock / show via execute_action."""

from __future__ import annotations

from typing import Any

from web_nicegui.lib.actions_ui import (
    _format_result,
    _set_md,
    build_action_form,
    run_registered,
)


def build_dna_page(ui: Any) -> None:
    ui.label("Character DNA").classes("text-h5 text-weight-bold")
    ui.label(
        "Identity profiles via studio_core.services.execute (in-process). "
        "Same ActionSpec catalog as the Textual cockpit."
    ).classes("text-caption text-grey-7 q-mb-md")

    with ui.card().classes("w-full q-mb-md"):
        ui.label("Profiles").classes("text-subtitle1 text-weight-medium")
        list_box = ui.markdown("_Loading DNA list…_")

    def refresh_list() -> None:
        result = run_registered("dna_list")
        _set_md(list_box, _format_result(result, limit=12000))

    with ui.row().classes("q-mb-md gap-2"):
        ui.button("Refresh list", icon="refresh", on_click=refresh_list).props("outline")

    with ui.tabs().classes("w-full") as tabs:
        tab_init = ui.tab("Init DNA")
        tab_lock = ui.tab("Lock")
        tab_show = ui.tab("Show")
        tab_handoff = ui.tab("Handoff")
    with ui.tab_panels(tabs, value=tab_init).classes("w-full"):
        with ui.tab_panel(tab_init):
            build_action_form(ui, "dna_init", on_done=lambda _r: refresh_list())
        with ui.tab_panel(tab_lock):
            build_action_form(ui, "dna_lock", on_done=lambda _r: refresh_list())
        with ui.tab_panel(tab_show):
            build_action_form(ui, "dna_show", force_confirm=False)
        with ui.tab_panel(tab_handoff):
            build_action_form(ui, "dna_handoff")

    ui.timer(0.05, refresh_list, once=True)
