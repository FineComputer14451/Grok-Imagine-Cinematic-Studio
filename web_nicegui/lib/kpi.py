"""Extract live KPI tiles from studio dashboard snapshot (P2)."""

from __future__ import annotations

from typing import Any


def _sev_from_snap(snap: dict[str, Any]) -> str:
    try:
        from web_nicegui.lib.snapshot import severity

        return severity(snap)
    except Exception:
        return "ok"


def extract_kpi_tiles(snap: dict[str, Any]) -> list[dict[str, str]]:
    """Return up to 4 KPI dicts: label, value, hint, sev (ok|warn|critical|info).

    Safe against missing keys — never raises on incomplete snapshots.
    """
    project = snap.get("project") or {}
    production = snap.get("production") or {}
    quota = snap.get("quota") or {}
    readiness = snap.get("readiness") or {}
    identity = readiness.get("identity") or {}
    studio = snap.get("studio") or {}

    sev = _sev_from_snap(snap)
    sev_label = {"ok": "OK", "warn": "WARN", "critical": "CRITICAL"}.get(sev, sev.upper())

    # Tile 1 — Studio health / severity
    models_ok = studio.get("models_compatible")
    model_hint = "models ok" if models_ok else "model issues"
    if models_ok is None:
        model_hint = "stack unknown"
    tile_health = {
        "label": "Studio health",
        "value": sev_label,
        "hint": model_hint,
        "sev": sev if sev in {"ok", "warn", "critical"} else "info",
    }

    # Tile 2 — Identity lock
    locked = identity.get("locked")
    if locked is None:
        locked = production.get("identity_locked", 0)
    total = identity.get("total")
    if total is None:
        total = production.get("characters", 0)
    try:
        locked_i = int(locked or 0)
        total_i = int(total or 0)
    except (TypeError, ValueError):
        locked_i, total_i = 0, 0
    id_sev = "ok" if total_i == 0 or locked_i == total_i else ("warn" if locked_i else "critical")
    tile_identity = {
        "label": "Identity",
        "value": f"{locked_i}/{total_i} locked",
        "hint": identity.get("label") or ("ready" if id_sev == "ok" and total_i else "pending lock"),
        "sev": id_sev,
    }

    # Tile 3 — Sequences / production pulse
    seq_n = production.get("sequences", 0)
    try:
        seq_n = int(seq_n or 0)
    except (TypeError, ValueError):
        seq_n = 0
    jobs = production.get("imagine_jobs", 0)
    try:
        jobs = int(jobs or 0)
    except (TypeError, ValueError):
        jobs = 0
    chain = readiness.get("chain_qa") or {}
    chain_label = chain.get("label") or "—"
    tile_seq = {
        "label": "Sequences",
        "value": f"{seq_n} active",
        "hint": f"jobs {jobs} · QA {chain_label}",
        "sev": "ok" if seq_n else "info",
    }

    # Tile 4 — Quota / risk
    spent = quota.get("session_spent", 0)
    remaining = quota.get("budget_remaining")
    tier = quota.get("tier") or "—"
    risk = str(quota.get("risk_level") or "unknown").lower()
    risk_sev = {
        "low": "ok",
        "ok": "ok",
        "medium": "warn",
        "moderate": "warn",
        "elevated": "warn",
        "high": "critical",
        "critical": "critical",
    }.get(risk, "info")
    try:
        spent_f = float(spent or 0)
    except (TypeError, ValueError):
        spent_f = 0.0
    if remaining is not None:
        try:
            rem_f = float(remaining)
            rem_s = f"{rem_f:,.0f} left"
        except (TypeError, ValueError):
            rem_s = "budget n/a"
    else:
        rem_s = "budget n/a"
    tile_quota = {
        "label": "Quota",
        "value": f"{spent_f:,.0f} spent",
        "hint": f"{tier} · {rem_s} · risk {risk}",
        "sev": risk_sev,
    }

    # Optional project title as context (not a 5th tile — folded into identity hint if empty)
    title = project.get("title") or ""
    if title and title != "Untitled" and tile_identity["hint"] in {"pending lock", "ready"}:
        tile_identity["hint"] = title[:40]

    return [tile_health, tile_identity, tile_seq, tile_quota]
