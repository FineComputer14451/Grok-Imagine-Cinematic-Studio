#!/usr/bin/env python3
"""
Quota reconciliation — estimated vs actual spend, burn-rate risk adjustment.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from project_state import load_project_state, save_project_state

RECON_SCHEMA_VERSION = "1.0"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def default_reconciliation() -> dict[str, Any]:
    return {
        "schema_version": RECON_SCHEMA_VERSION,
        "estimated_total": 0.0,
        "actual_total": 0.0,
        "variance_credits": 0.0,
        "variance_pct": 0.0,
        "burn_rate_multiplier": 1.0,
        "risk_level": "low",
        "entries": [],
        "updated_at": _now_iso(),
    }


def ensure_reconciliation(state: dict[str, Any]) -> dict[str, Any]:
    quota = state.setdefault("quota", {})
    if "reconciliation" not in quota or not isinstance(quota.get("reconciliation"), dict):
        quota["reconciliation"] = default_reconciliation()
    recon = quota["reconciliation"]
    for key, val in default_reconciliation().items():
        recon.setdefault(key, val)
    return recon


def _recon_entry(
    *,
    estimated_credits: float,
    actual_credits: float,
    note: str = "",
    source: str,
    at: str | None = None,
    job_id: str | None = None,
    shot_id: str | None = None,
) -> dict[str, Any]:
    est_f = round(float(estimated_credits), 2)
    act_f = round(float(actual_credits), 2)
    return {
        "at": at or _now_iso(),
        "estimated_credits": est_f,
        "actual_credits": act_f,
        "variance_credits": round(act_f - est_f, 2),
        "note": note,
        "job_id": job_id,
        "shot_id": shot_id,
        "source": source,
    }


def _fold_entries(recon: dict[str, Any], entries: list[dict[str, Any]], source: str) -> None:
    recon["entries"] = list(entries)
    recon["estimated_total"] = round(
        sum(float(e["estimated_credits"]) for e in entries), 2
    )
    recon["actual_total"] = round(sum(float(e["actual_credits"]) for e in entries), 2)
    recon["sources"] = [source]


def _safe_float(value: Any, default: float | None = None) -> float | None:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def record_generation_spend(
    actual_credits: float,
    *,
    estimated_credits: float | None = None,
    note: str = "",
    job_id: str | None = None,
    shot_id: str | None = None,
    state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Record actual spend with optional estimate for reconciliation."""
    from quota_optimizer import record_spend

    if state is None:
        state = load_project_state()

    quota = record_spend(actual_credits, note=note, state=state)
    recon = ensure_reconciliation(state)

    est = estimated_credits if estimated_credits is not None else actual_credits
    entry = _recon_entry(
        estimated_credits=est,
        actual_credits=actual_credits,
        note=note,
        source="record_spend",
        job_id=job_id,
        shot_id=shot_id,
    )
    recon["entries"].append(entry)
    recon["entries"] = recon["entries"][-100:]
    recon["estimated_total"] = round(recon["estimated_total"] + entry["estimated_credits"], 2)
    recon["actual_total"] = round(recon["actual_total"] + entry["actual_credits"], 2)
    _recompute_burn_rate(recon)
    recon["updated_at"] = _now_iso()
    save_project_state(state)
    return {"quota": quota, "reconciliation": recon, "entry": entry}


def _recompute_burn_rate(recon: dict[str, Any]) -> None:
    est = recon.get("estimated_total", 0)
    actual = recon.get("actual_total", 0)
    if est > 0:
        recon["burn_rate_multiplier"] = round(actual / est, 3)
        recon["variance_credits"] = round(actual - est, 2)
        recon["variance_pct"] = round((actual - est) / est * 100, 1)
    else:
        recon["burn_rate_multiplier"] = 1.0
        recon["variance_credits"] = 0.0
        recon["variance_pct"] = 0.0
    recon["risk_level"] = burn_rate_risk_level(recon["burn_rate_multiplier"])


def burn_rate_risk_level(multiplier: float) -> str:
    if multiplier >= 1.35:
        return "critical"
    if multiplier >= 1.15:
        return "high"
    if multiplier >= 1.05:
        return "medium"
    return "low"


def get_burn_rate_risk(state: dict[str, Any] | None = None) -> str:
    if state is None:
        state = load_project_state()
    recon = ensure_reconciliation(state)
    return recon.get("risk_level", "low")


def _entries_from_generation_ledger() -> list[dict[str, Any]]:
    """Map billable ledger rows into recon entries (canonical load via generation_tracker).

    Only rows with an explicit ``credits_actual`` and non-failed status participate
    so failed/est-only rows do not dilute burn-rate.
    """
    from generation_tracker import load_ledger

    data = load_ledger()
    out: list[dict[str, Any]] = []
    for e in data.get("entries") or []:
        if not isinstance(e, dict):
            continue
        if e.get("status") == "failed":
            continue
        actual = _safe_float(e.get("credits_actual"))
        if actual is None:
            continue
        est = _safe_float(e.get("credits_estimate"), actual)
        if est is None:
            est = actual
        proj = e.get("project") or "(none)"
        eid = e.get("entry_id") or ""
        note = f"ledger:{proj}" + (f" {eid}" if eid else "")
        out.append(
            _recon_entry(
                estimated_credits=est,
                actual_credits=actual,
                note=note,
                source="generation_ledger",
                at=e.get("updated_at") or e.get("created_at"),
                job_id=e.get("job_id"),
                shot_id=e.get("shot_id"),
            )
        )
    return out


def _entries_from_imagine_jobs(state: dict[str, Any]) -> list[dict[str, Any]]:
    """Jobs with explicit actual_credits only (est-only seeds skipped)."""
    out: list[dict[str, Any]] = []
    jobs_state = state.get("imagine_jobs", {}).get("jobs", {})
    for job in jobs_state.values():
        if not isinstance(job, dict):
            continue
        meta = job.get("metadata") or {}
        actual = meta.get("actual_credits")
        if actual is None:
            actual = job.get("actual_credits")
        act_f = _safe_float(actual)
        if act_f is None:
            continue
        est = meta.get("estimated_credits")
        if est is None:
            est = job.get("estimated_credits")
        est_f = _safe_float(est, act_f)
        if est_f is None:
            est_f = act_f
        out.append(
            _recon_entry(
                estimated_credits=est_f,
                actual_credits=act_f,
                note=f"job:{job.get('job_id')}",
                source="imagine_job",
                at=job.get("updated_at"),
                job_id=job.get("job_id"),
                shot_id=job.get("shot_id"),
            )
        )
    return out


def _entries_from_history(state: dict[str, Any]) -> list[dict[str, Any]]:
    """Manual session history pairs via note ``est:N``."""
    out: list[dict[str, Any]] = []
    for hist in state.get("quota", {}).get("history", []):
        if not isinstance(hist, dict):
            continue
        note = hist.get("note", "") or ""
        if "est:" not in note:
            continue
        m = re.search(r"est:(\d+\.?\d*)", note)
        if not m:
            continue
        est_f = float(m.group(1))
        act_f = _safe_float(hist.get("credits"), 0.0) or 0.0
        out.append(
            _recon_entry(
                estimated_credits=est_f,
                actual_credits=act_f,
                note=note,
                source="history",
                at=hist.get("at"),
            )
        )
    return out


def reconcile_from_jobs(state: dict[str, Any] | None = None) -> dict[str, Any]:
    """Rebuild reconciliation using exclusive cascade (no multi-source sum).

    Exactly one source contributes:

    1. ``generation_ledger`` — billable rows (explicit actual, not failed)
    2. else imagine jobs with explicit ``actual_credits``
    3. else session history notes containing ``est:N``
    """
    if state is None:
        state = load_project_state()

    recon = ensure_reconciliation(state)
    recon["estimated_total"] = 0.0
    recon["actual_total"] = 0.0
    recon["entries"] = []
    recon["sources"] = []

    ledger_entries = _entries_from_generation_ledger()
    if ledger_entries:
        _fold_entries(recon, ledger_entries, "generation_ledger")
    else:
        job_entries = _entries_from_imagine_jobs(state)
        if job_entries:
            _fold_entries(recon, job_entries, "imagine_jobs_actuals")
        else:
            hist_entries = _entries_from_history(state)
            if hist_entries:
                _fold_entries(recon, hist_entries, "history_est")
            else:
                recon["sources"] = []

    _recompute_burn_rate(recon)
    recon["updated_at"] = _now_iso()
    save_project_state(state)
    return recon


def quota_sync_summary(state: dict[str, Any] | None = None) -> dict[str, Any]:
    if state is None:
        state = load_project_state()
    recon = ensure_reconciliation(state)
    quota = state.get("quota", {})
    sources = list(recon.get("sources") or [])
    cascade = sources[0] if sources else "none"
    return {
        "session_spent": quota.get("session_spent", 0),
        "estimated_total": recon.get("estimated_total", 0),
        "actual_total": recon.get("actual_total", 0),
        "variance_pct": recon.get("variance_pct", 0),
        "burn_rate_multiplier": recon.get("burn_rate_multiplier", 1.0),
        "risk_level": recon.get("risk_level", "low"),
        "entry_count": len(recon.get("entries", [])),
        "sources": sources,
        "cascade_source": cascade,
        "updated_at": recon.get("updated_at"),
    }
