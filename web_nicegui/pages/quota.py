"""NiceGUI Quota page — dashboard / budget / sequence estimate."""

from __future__ import annotations

from typing import Any

from web_nicegui.lib.actions_ui import (
    _format_result,
    _set_md,
    build_action_form,
    run_registered,
)


def build_quota_page(ui: Any) -> None:
    ui.label("Quota").classes("text-h5 text-weight-bold")
    ui.label(
        "Session spend, budget, and sequence estimates via execute_action."
    ).classes("text-caption text-grey-7 q-mb-md")

    with ui.card().classes("w-full q-mb-md"):
        ui.label("Quota dashboard").classes("text-subtitle1 text-weight-medium")
        dash_box = ui.markdown("_Loading quota dashboard…_")

    def refresh() -> None:
        result = run_registered("quota_dashboard")
        _set_md(dash_box, _format_result(result, limit=12000))

    def sync() -> None:
        result = run_registered("quota_sync")
        _set_md(dash_box, _format_result(result, limit=12000))

    with ui.row().classes("q-mb-md gap-2"):
        ui.button("Refresh", icon="refresh", on_click=refresh).props("outline")
        ui.button("Quota sync", icon="sync", on_click=sync).props("outline")

    with ui.tabs().classes("w-full") as tabs:
        tab_budget = ui.tab("Set budget")
        tab_est = ui.tab("Sequence estimate")
    with ui.tab_panels(tabs, value=tab_budget).classes("w-full"):
        with ui.tab_panel(tab_budget):
            build_action_form(ui, "quota_budget", on_done=lambda _r: refresh())
        with ui.tab_panel(tab_est):
            build_action_form(ui, "quota_sequence_estimate", force_confirm=False)

    ui.timer(0.05, refresh, once=True)
