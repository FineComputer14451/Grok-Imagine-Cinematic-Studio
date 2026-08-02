"""NiceGUI Production page — bible create + health checks via execute_action."""

from __future__ import annotations

from typing import Any

from web_nicegui.lib.actions_ui import (
    _format_result,
    _set_md,
    build_action_form,
    run_registered,
)


def build_production_page(ui: Any) -> None:
    ui.label("Production").classes("text-h5 text-weight-bold")
    ui.label(
        "Production bible + studio health via ActionSpec / execute_action (in-process). "
        "Full multi-stage Streamlit wizard remains in web_ui/pages/production.py."
    ).classes("text-caption text-grey-7 q-mb-md")

    with ui.card().classes("w-full q-mb-md"):
        ui.label("Studio health").classes("text-subtitle1 text-weight-medium")
        health_box = ui.markdown("_Run status / validate / stack / doctor below._")

    def _show(result) -> None:
        _set_md(health_box, _format_result(result, limit=12000))

    with ui.row().classes("q-mb-md gap-2 flex-wrap"):
        ui.button(
            "Status",
            icon="info",
            on_click=lambda: _show(run_registered("status")),
        ).props("outline")
        ui.button(
            "Validate",
            icon="verified",
            on_click=lambda: _show(run_registered("validate")),
        ).props("outline")
        ui.button(
            "Stack",
            icon="layers",
            on_click=lambda: _show(run_registered("stack")),
        ).props("outline")
        ui.button(
            "Doctor (quick)",
            icon="medical_services",
            on_click=lambda: _show(run_registered("doctor_quick")),
        ).props("outline")
        ui.button(
            "Models verify",
            icon="smart_toy",
            on_click=lambda: _show(run_registered("models_verify")),
        ).props("outline")
        ui.button(
            "Models list",
            icon="list",
            on_click=lambda: _show(run_registered("models_list")),
        ).props("outline")

    with ui.tabs().classes("w-full") as tabs:
        tab_bible = ui.tab("Create bible")
        tab_handoff = ui.tab("Handoff validate")
    with ui.tab_panels(tabs, value=tab_bible).classes("w-full"):
        with ui.tab_panel(tab_bible):
            build_action_form(ui, "bible_create")
        with ui.tab_panel(tab_handoff):
            build_action_form(ui, "handoff_validate", force_confirm=False)

    ui.timer(0.05, lambda: _show(run_registered("status")), once=True)
