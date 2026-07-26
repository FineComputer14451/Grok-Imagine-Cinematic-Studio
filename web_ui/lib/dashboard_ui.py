"""Dense Dashboard helpers for Streamlit — reuses pure TUI snapshot formatters."""

from __future__ import annotations

from typing import Any

# tools/ is on sys.path via lib.runtime import order; dashboard pages import runtime first.
try:
    from cli.tui.widgets import (
        collect_home_alerts,
        strip_severity,
    )
except ImportError:  # pragma: no cover — fallback if TUI package missing
    collect_home_alerts = None  # type: ignore[assignment]
    strip_severity = None  # type: ignore[assignment]


def attach_quota_alignment(snap: dict[str, Any]) -> dict[str, Any]:
    """Attach ledger alignment when available (same as TUI Home refresh)."""
    if "quota_alignment" in snap:
        return snap
    try:
        from quota_sync import ledger_recon_alignment

        snap["quota_alignment"] = ledger_recon_alignment()
    except Exception:
        pass
    return snap


def severity(snap: dict[str, Any]) -> str:
    if callable(strip_severity):
        return strip_severity(snap)
    return "ok"


def alerts(snap: dict[str, Any]) -> list[str]:
    if callable(collect_home_alerts):
        return list(collect_home_alerts(snap))
    return []


def severity_label(sev: str) -> str:
    return {
        "ok": "OK",
        "warn": "WARN",
        "critical": "CRITICAL",
    }.get(sev, sev.upper() or "OK")


def status_strip_html(snap: dict[str, Any], *, studio_version: str) -> str:
    """HTML status strip with severity class."""
    project = snap.get("project") or {}
    studio = snap.get("studio") or {}
    quota = snap.get("quota") or {}
    production = snap.get("production") or {}
    sev = severity(snap)
    title = project.get("title") or "Untitled"
    bible = "bible:loaded" if project.get("has_bible") else "bible:none"
    models = "models:OK" if studio.get("models_compatible") else "models:ISSUES"
    risk = f"risk:{(quota.get('risk_level') or 'unknown')}"
    locked = production.get("identity_locked", 0)
    chars = production.get("characters", 0)
    go = 0
    no_go = 0
    for r in snap.get("chain_qa") or []:
        if isinstance(r, dict):
            go += int(r.get("go_count") or 0)
            no_go += int(r.get("no_go_count") or 0)
    qa = f"QA {go} go · {no_go} no-go" if snap.get("chain_qa") else "QA —"
    when = snap.get("generated_at") or ""
    chips = " · ".join(
        [
            title,
            bible,
            models,
            risk,
            f"DNA {locked}/{chars} locked",
            qa,
        ]
    )
    return (
        f'<div class="ops-strip sev-{sev}">'
        f'<div class="ops-strip-title">Cinematic Studio v{studio_version} '
        f'<span class="sev-pill sev-{sev}">{severity_label(sev)}</span>'
        f'{" · " + when if when else ""}</div>'
        f'<div class="ops-strip-chips">{chips}</div>'
        f"</div>"
    )


def attention_rows(snap: dict[str, Any]) -> list[str]:
    return alerts(snap)


def chain_qa_table_rows(snap: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for r in snap.get("chain_qa") or []:
        if not isinstance(r, dict):
            continue
        rows.append(
            {
                "Sequence": r.get("sequence_name") or r.get("slug") or "?",
                "Go": r.get("go_count", 0),
                "No-Go": r.get("no_go_count", 0),
                "Status": r.get("chain_qa_status") or "—",
                "Clips": r.get("clip_count", "—"),
            }
        )
    return rows


def sequences_table_rows(snap: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for s in snap.get("sequences") or []:
        if not isinstance(s, dict):
            continue
        rows.append(
            {
                "Name": s.get("name") or s.get("slug") or "?",
                "Clips": s.get("clips", 0),
                "Target": f"{s.get('target_duration', '—')}s",
                "Health": str(s.get("health") or "—"),
            }
        )
    return rows


def characters_table_rows(snap: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for c in snap.get("characters") or []:
        if not isinstance(c, dict):
            continue
        rows.append(
            {
                "Name": c.get("name") or "?",
                "Slug": c.get("slug") or "",
                "Lock": c.get("status") or "pending",
            }
        )
    return rows


def jobs_table_rows(snap: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for j in snap.get("recent_jobs") or []:
        if not isinstance(j, dict):
            continue
        rows.append(
            {
                "Job": j.get("job_id") or "?",
                "Type": j.get("job_type") or "—",
                "Status": j.get("status") or "—",
                "Model": j.get("model") or "—",
            }
        )
    return rows
