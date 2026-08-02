"""Read-only NiceGUI dashboard — TUI/Streamlit snapshot parity (PR4)."""

from __future__ import annotations

from typing import Any, Callable

from web_nicegui.lib.snapshot import (
    load_snapshot,
    normalize_dashboard_mode,
    section_visible,
    severity,
    severity_label,
    studio_version,
)


def _formatters():
    from studio_core.pathutil import ensure_import_paths

    ensure_import_paths()
    from cli.tui.widgets import (
        format_attention_panel,
        format_chain_qa_panel,
        format_characters_panel,
        format_convergence_panel,
        format_delivery_panel,
        format_jobs_panel,
        format_kpi_bar,
        format_orient_brief,
        format_parallel_briefs_panel,
        format_quota_panel,
        format_readiness_panel,
        format_sequences_panel,
        format_status_strip,
        format_studio_panel,
    )

    return {
        "status": format_status_strip,
        "kpi": format_kpi_bar,
        "orient": format_orient_brief,
        "attention": format_attention_panel,
        "readiness": format_readiness_panel,
        "convergence": format_convergence_panel,
        "delivery": format_delivery_panel,
        "briefs": format_parallel_briefs_panel,
        "quota": format_quota_panel,
        "studio": format_studio_panel,
        "sequences": format_sequences_panel,
        "chain_qa": format_chain_qa_panel,
        "characters": format_characters_panel,
        "jobs": format_jobs_panel,
    }


def _sev_color(sev: str) -> str:
    return {"ok": "positive", "warn": "warning", "critical": "negative"}.get(sev, "primary")


def build_dashboard_page(ui: Any, *, get_mode: Callable[[], str], set_mode: Callable[[str], None]) -> None:
    """Compose the dashboard into the current NiceGUI page context."""
    fmt = _formatters()
    state: dict[str, Any] = {"snap": None, "error": None}

    header = ui.row().classes("w-full items-center justify-between q-mb-md")
    with header:
        title_col = ui.column()
        with title_col:
            title_label = ui.label("Cinematic Studio Dashboard").classes("text-h5 text-weight-bold")
            caption = ui.label("").classes("text-caption text-grey-7")
        controls = ui.row().classes("items-center gap-2")
        with controls:
            mode_toggle = ui.toggle(
                {"compact": "Compact", "ops": "Ops", "full": "Full"},
                value=normalize_dashboard_mode(get_mode()),
            ).props("no-caps dense")
            refresh_btn = ui.button("Refresh", icon="refresh").props("outline dense")

    status_card = ui.card().classes("w-full q-mb-sm")
    with status_card:
        status_pre = ui.markdown("").classes("w-full")
        sev_badge = ui.badge("").props("outline")

    kpi_card = ui.card().classes("w-full q-mb-sm")
    with kpi_card:
        kpi_pre = ui.markdown("")

    attention_card = ui.card().classes("w-full q-mb-sm")
    with attention_card:
        ui.label("Attention").classes("text-subtitle2 text-weight-medium")
        attention_pre = ui.markdown("")

    panels_col = ui.column().classes("w-full gap-sm")

    def _clear_panels() -> None:
        panels_col.clear()

    def _add_panel(title: str, body: str | None) -> None:
        if not body:
            return
        with panels_col:
            with ui.card().classes("w-full"):
                ui.label(title).classes("text-subtitle2 text-weight-medium")
                ui.markdown(f"```\n{body}\n```" if not body.strip().startswith("#") else body)

    def refresh() -> None:
        mode = normalize_dashboard_mode(mode_toggle.value or get_mode())
        set_mode(mode)
        try:
            snap = load_snapshot()
            state["snap"] = snap
            state["error"] = None
        except Exception as exc:  # noqa: BLE001
            state["snap"] = None
            state["error"] = str(exc)
            status_pre.content = f"**Error loading snapshot:** `{exc}`"
            sev_badge.text = "ERROR"
            sev_badge.props("color=negative")
            kpi_pre.content = ""
            attention_pre.content = ""
            _clear_panels()
            return

        snap = state["snap"]
        assert snap is not None
        ver = studio_version(snap)
        sev = severity(snap)
        title_label.text = f"Cinematic Studio v{ver}"
        caption.text = (
            f"View **{mode}** · Grok 4.5 · read-only NiceGUI shell · "
            f"TUI twin: `cinematic-studio ui` · Streamlit: `web_ui/`"
        )
        status_pre.content = f"```\n{fmt['status'](snap)}\n```"
        sev_badge.text = severity_label(sev)
        sev_badge.props(f"color={_sev_color(sev)}")

        if mode == "compact":
            kpi_pre.content = f"```\n{fmt['orient'](snap)}\n```"
        else:
            kpi_pre.content = f"```\n{fmt['kpi'](snap)}\n```"

        attention_pre.content = f"```\n{fmt['attention'](snap)}\n```"

        _clear_panels()
        section_map = [
            ("readiness", "Readiness", "readiness"),
            ("convergence", "Convergence", "convergence"),
            ("delivery", "Delivery", "delivery"),
            ("briefs", "Parallel briefs", "briefs"),
            ("studio_quota", "Quota", "quota"),
            ("stack", "Studio health", "studio"),
            ("sequences", "Sequences", "sequences"),
            ("chain_qa", "Chain QA", "chain_qa"),
            ("characters", "Characters", "characters"),
            ("jobs", "Imagine jobs", "jobs"),
        ]
        for section, title, key in section_map:
            if not section_visible(mode, section):
                continue
            formatter = fmt.get(key)
            if not formatter:
                continue
            body = formatter(snap)
            if body is None:
                continue
            _add_panel(title, body)

        if section_visible(mode, "json"):
            import json

            with panels_col:
                with ui.card().classes("w-full"):
                    ui.label("Snapshot JSON").classes("text-subtitle2 text-weight-medium")
                    ui.code(json.dumps(snap, indent=2, default=str)[:12000]).classes("w-full")

    mode_toggle.on_value_change(lambda _: refresh())
    refresh_btn.on_click(lambda: refresh())
    ui.timer(8.0, refresh)
    refresh()
