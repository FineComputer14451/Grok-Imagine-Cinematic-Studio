"""NiceGUI Imagine page — jobs list + bridge + Files via execute_action."""

from __future__ import annotations

from typing import Any

from files_client import FilesAPIError, save_inbox_file
from web_nicegui.lib.actions_ui import (
    _format_result,
    _set_md,
    build_action_form,
    run_registered,
)


def build_imagine_page(ui: Any) -> None:
    ui.label("Imagine").classes("text-h5 text-weight-bold")
    ui.label(
        "Job queue + Files API + agent-handoff bridge via execute_action. "
        "Image 2.0 is hero/Quality Mode; Video 1.0 cost default / 1.5 native audio "
        "(there is no Video 2.0). Live xAI generation stays on Streamlit or `imagine submit`."
    ).classes("text-caption text-grey-7 q-mb-md")

    with ui.card().classes("w-full q-mb-md"):
        ui.label("Imagine jobs").classes("text-subtitle1 text-weight-medium")
        list_box = ui.markdown("_Loading imagine list…_")

    def refresh() -> None:
        result = run_registered("imagine_list")
        _set_md(list_box, _format_result(result, limit=12000))

    with ui.row().classes("q-mb-md gap-2"):
        ui.button("Refresh jobs", icon="refresh", on_click=refresh).props("outline")

    with ui.tabs().classes("w-full") as tabs:
        tab_bridge = ui.tab("Bridge")
        tab_poll = ui.tab("Poll")
        tab_files = ui.tab("Files")
        tab_seq_handoff = ui.tab("Sequence handoff")
        tab_dna_handoff = ui.tab("DNA handoff")
    with ui.tab_panels(tabs, value=tab_bridge).classes("w-full"):
        with ui.tab_panel(tab_bridge):
            build_action_form(ui, "imagine_bridge", force_confirm=False, on_done=lambda _r: refresh())
        with ui.tab_panel(tab_poll):
            build_action_form(ui, "imagine_poll", force_confirm=False, on_done=lambda _r: refresh())
        with ui.tab_panel(tab_files):
            files_box = ui.markdown("_Loading files list…_")

            def refresh_files() -> None:
                result = run_registered("files_list")
                _set_md(files_box, _format_result(result, limit=12000))

            def _on_drop(event: Any) -> None:
                name = getattr(event, "name", None) or "upload.bin"
                content = getattr(event, "content", None)
                try:
                    data = content.read() if content is not None else b""
                    dest = save_inbox_file(str(name), data)
                except (FilesAPIError, OSError) as exc:
                    ui.notify(str(exc), type="negative")
                    return
                ui.notify(f"Saved {dest} — paste into Upload path", type="positive")

            with ui.row().classes("q-mb-sm gap-2"):
                ui.button("Refresh files", icon="refresh", on_click=refresh_files).props("outline")
            ui.upload(
                label="Drop plate → artifacts/files_inbox (then paste path into Upload)",
                on_upload=_on_drop,
                auto_upload=True,
            ).classes("w-full q-mb-md")
            build_action_form(ui, "files_get", force_confirm=False, on_done=lambda _r: refresh_files())
            build_action_form(ui, "files_upload", on_done=lambda _r: refresh_files())
            build_action_form(ui, "files_delete", on_done=lambda _r: refresh_files())
            ui.timer(0.05, refresh_files, once=True)
        with ui.tab_panel(tab_seq_handoff):
            build_action_form(ui, "sequence_handoff", on_done=lambda _r: refresh())
        with ui.tab_panel(tab_dna_handoff):
            build_action_form(ui, "dna_handoff", on_done=lambda _r: refresh())

    ui.timer(0.05, refresh, once=True)
