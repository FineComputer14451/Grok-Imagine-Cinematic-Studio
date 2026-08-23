"""Read-only NiceGUI dashboard — KPI tiles (P2) + TUI snapshot parity."""

from __future__ import annotations

from typing import Any, Callable

from web_nicegui.lib.kpi import extract_kpi_tiles
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
    return {"ok": "positive", "warn": "warning", "critical": "negative", "info": "info"}.get(
        (sev or "ok").lower(), "primary"
    )


def _sev_border(sev: str) -> str:
    return {
        "ok": "border-positive",
        "warn": "border-warning",
        "critical": "border-negative",
        "info": "border-info",
    }.get((sev or "ok").lower(), "border-grey-7")


def _set_text(el: Any, value: str) -> None:
    """Update element text/content across NiceGUI versions."""
    value = value or ""
    if hasattr(el, "set_content"):
        try:
            el.set_content(value)
            return
        except Exception:
            pass
    if hasattr(el, "content"):
        try:
            el.content = value
            return
        except Exception:
            pass
    if hasattr(el, "set_text"):
        el.set_text(value)
    elif hasattr(el, "text"):
        el.text = value


def build_dashboard_page(
    ui: Any, *, get_mode: Callable[[], str], set_mode: Callable[[str], None]
) -> None:
    """Compose the dashboard: KPI tile row + detail panels."""
    fmt = _formatters()
    state: dict[str, Any] = {"snap": None, "error": None, "ready": False}

    with ui.row().classes("w-full items-center justify-between q-mb-md flex-wrap gap-2"):
        with ui.column().classes("gap-0"):
            title_label = ui.label("Cinematic Studio Dashboard").classes(
                "text-h5 text-weight-bold"
            )
            caption = ui.label("").classes("text-caption text-grey-7")
        with ui.row().classes("items-center gap-2"):
            mode_toggle = ui.toggle(
                {"compact": "Compact", "ops": "Ops", "full": "Full"},
                value=normalize_dashboard_mode(get_mode()),
            ).props("no-caps dense")
            refresh_btn = ui.button("Refresh", icon="refresh").props("outline dense no-caps")

    # —— P2: live KPI tiles (4 cards) ——
    kpi_row = ui.row().classes("w-full q-mb-md gap-3 flex-wrap")
    kpi_refs: list[dict[str, Any]] = []
    with kpi_row:
        for _ in range(4):
            with ui.card().classes(
                "col-grow q-pa-md"
            ).style("min-width:10.5rem; flex:1 1 10.5rem; max-width:100%") as card:
                label_el = ui.label("—").classes(
                    "text-caption text-uppercase text-grey-6"
                ).style("letter-spacing:0.06em; font-size:0.7rem")
                value_el = ui.label("—").classes("text-h5 text-weight-bold q-mt-xs")
                hint_el = ui.label("").classes("text-caption text-grey-7 q-mt-xs")
                kpi_refs.append(
                    {"card": card, "label": label_el, "value": value_el, "hint": hint_el}
                )

    with ui.card().classes("w-full q-mb-sm"):
        with ui.row().classes("w-full items-center justify-between"):
            ui.label("Status").classes("text-subtitle2 text-weight-medium")
            sev_badge = ui.badge("—").props("outline")
        status_pre = ui.markdown("")

    with ui.card().classes("w-full q-mb-sm"):
        ui.label("KPIs / Orient (detail)").classes("text-subtitle2 text-weight-medium")
        kpi_pre = ui.markdown("")

    with ui.card().classes("w-full q-mb-sm"):
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
                ui.markdown(f"```\n{body}\n```")

    def _paint_kpi(snap: dict[str, Any]) -> None:
        tiles = extract_kpi_tiles(snap)
        for i, ref in enumerate(kpi_refs):
            if i >= len(tiles):
                _set_text(ref["label"], "")
                _set_text(ref["value"], "—")
                _set_text(ref["hint"], "")
                continue
            t = tiles[i]
            _set_text(ref["label"], t["label"])
            _set_text(ref["value"], t["value"])
            _set_text(ref["hint"], t["hint"])
            # Left border via Quasar color class on value
            color = _sev_color(t["sev"])
            try:
                ref["value"].classes(replace=f"text-h5 text-weight-bold q-mt-xs text-{color}")
            except Exception:
                pass

    def refresh() -> None:
        try:
            mode = normalize_dashboard_mode(
                getattr(mode_toggle, "value", None) or get_mode()
            )
            set_mode(mode)
            try:
                snap = load_snapshot()
                state["snap"] = snap
                state["error"] = None
            except Exception as exc:  # noqa: BLE001
                state["snap"] = None
                state["error"] = str(exc)
                _set_text(status_pre, f"**Error loading snapshot:** `{exc}`")
                if hasattr(sev_badge, "set_text"):
                    sev_badge.set_text("ERROR")
                else:
                    sev_badge.text = "ERROR"
                sev_badge.props("color=negative")
                _set_text(kpi_pre, "")
                _set_text(attention_pre, "")
                for ref in kpi_refs:
                    _set_text(ref["value"], "—")
                    _set_text(ref["hint"], "snapshot error")
                _clear_panels()
                return

            snap = state["snap"]
            assert snap is not None
            ver = studio_version(snap)
            sev = severity(snap)
            if hasattr(title_label, "set_text"):
                title_label.set_text(f"Cinematic Studio v{ver}")
            else:
                title_label.text = f"Cinematic Studio v{ver}"
            cap = (
                f"View {mode} · Grok 4.6 · KPI tiles + detail panels · "
                "TUI twin: cinematic-studio ui"
            )
            if hasattr(caption, "set_text"):
                caption.set_text(cap)
            else:
                caption.text = cap

            _paint_kpi(snap)

            _set_text(status_pre, f"```\n{fmt['status'](snap)}\n```")
            badge_text = severity_label(sev)
            if hasattr(sev_badge, "set_text"):
                sev_badge.set_text(badge_text)
            else:
                sev_badge.text = badge_text
            sev_badge.props(f"color={_sev_color(sev)}")

            if mode == "compact":
                _set_text(kpi_pre, f"```\n{fmt['orient'](snap)}\n```")
            else:
                _set_text(kpi_pre, f"```\n{fmt['kpi'](snap)}\n```")

            _set_text(attention_pre, f"```\n{fmt['attention'](snap)}\n```")

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
                        ui.label("Snapshot JSON").classes(
                            "text-subtitle2 text-weight-medium"
                        )
                        ui.code(
                            json.dumps(snap, indent=2, default=str)[:12000]
                        ).classes("w-full")
            state["ready"] = True
        except Exception as exc:  # noqa: BLE001
            _set_text(status_pre, f"**Refresh failed:** `{exc}`")

    mode_toggle.on_value_change(lambda _e: refresh())
    refresh_btn.on_click(lambda: refresh())
    ui.timer(0.05, refresh, once=True)
    # On-demand friendly interval (was 8s); still auto-refreshes ops view
    ui.timer(15.0, refresh)
