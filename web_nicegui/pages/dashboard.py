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


def build_dashboard_page(ui: Any, *, get_mode: Callable[[], str], set_mode: Callable[[str], None]) -> None:
    """Compose the dashboard into the current NiceGUI page context."""
    fmt = _formatters()
    state: dict[str, Any] = {"snap": None, "error": None, "ready": False}

    with ui.row().classes("w-full items-center justify-between q-mb-md"):
        with ui.column():
            title_label = ui.label("Cinematic Studio Dashboard").classes("text-h5 text-weight-bold")
            caption = ui.label("").classes("text-caption text-grey-7")
        with ui.row().classes("items-center gap-2"):
            mode_toggle = ui.toggle(
                {"compact": "Compact", "ops": "Ops", "full": "Full"},
                value=normalize_dashboard_mode(get_mode()),
            ).props("no-caps dense")
            refresh_btn = ui.button("Refresh", icon="refresh").props("outline dense")

    with ui.card().classes("w-full q-mb-sm"):
        status_pre = ui.markdown("")
        sev_badge = ui.badge("").props("outline")

    with ui.card().classes("w-full q-mb-sm"):
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
                # Prefer plain markdown fenced block for preformatted panel text
                ui.markdown(f"```\n{body}\n```")

    def refresh() -> None:
        try:
            mode = normalize_dashboard_mode(getattr(mode_toggle, "value", None) or get_mode())
            set_mode(mode)
            try:
                snap = load_snapshot()
                state["snap"] = snap
                state["error"] = None
            except Exception as exc:  # noqa: BLE001
                state["snap"] = None
                state["error"] = str(exc)
                _set_text(status_pre, f"**Error loading snapshot:** `{exc}`")
                sev_badge.set_text("ERROR") if hasattr(sev_badge, "set_text") else setattr(sev_badge, "text", "ERROR")
                sev_badge.props("color=negative")
                _set_text(kpi_pre, "")
                _set_text(attention_pre, "")
                _clear_panels()
                return

            snap = state["snap"]
            assert snap is not None
            ver = studio_version(snap)
            sev = severity(snap)
            title_label.set_text(f"Cinematic Studio v{ver}") if hasattr(title_label, "set_text") else setattr(
                title_label, "text", f"Cinematic Studio v{ver}"
            )
            caption.set_text(
                f"View {mode} · Grok 4.5 · read-only NiceGUI shell · "
                "TUI twin: cinematic-studio ui · Streamlit: web_ui/"
            ) if hasattr(caption, "set_text") else setattr(
                caption,
                "text",
                f"View {mode} · Grok 4.5 · read-only NiceGUI shell · "
                "TUI twin: cinematic-studio ui · Streamlit: web_ui/",
            )
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
                        ui.label("Snapshot JSON").classes("text-subtitle2 text-weight-medium")
                        ui.code(json.dumps(snap, indent=2, default=str)[:12000]).classes("w-full")
            state["ready"] = True
        except Exception as exc:  # noqa: BLE001 — keep UI alive on refresh errors
            _set_text(status_pre, f"**Refresh failed:** `{exc}`")

    mode_toggle.on_value_change(lambda _e: refresh())
    refresh_btn.on_click(lambda: refresh())
    # Defer first paint slightly so the client socket is ready
    ui.timer(0.05, refresh, once=True)
    ui.timer(8.0, refresh)
