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
    variance = round(actual_credits - est, 2)
    entry = {
        "at": _now_iso(),
        "estimated_credits": est,
        "actual_credits": actual_credits,
        "variance_credits": variance,
        "note": note,
        "job_id": job_id,
        "shot_id": shot_id,
    }
    recon["entries"].append(entry)
    recon["entries"] = recon["entries"][-100:]
    recon["estimated_total"] = round(recon["estimated_total"] + est, 2)
    recon["actual_total"] = round(recon["actual_total"] + actual_credits, 2)
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


def reconcile_from_jobs(state: dict[str, Any] | None = None) -> dict[str, Any]:
    """Rebuild reconciliation totals from imagine jobs and quota history."""
    if state is None:
        state = load_project_state()

    recon = ensure_reconciliation(state)
    recon["estimated_total"] = 0.0
    recon["actual_total"] = 0.0
    recon["entries"] = []

    jobs_state = state.get("imagine_jobs", {}).get("jobs", {})
    for job in jobs_state.values():
        meta = job.get("metadata") or {}
        est = meta.get("estimated_credits") or job.get("estimated_credits")
        actual = meta.get("actual_credits") or job.get("actual_credits")
        if est is None and actual is None:
            continue
        est_f = float(est or actual or 0)
        act_f = float(actual or est or 0)
        recon["entries"].append({
            "at": job.get("updated_at", _now_iso()),
            "estimated_credits": est_f,
            "actual_credits": act_f,
            "variance_credits": round(act_f - est_f, 2),
            "note": f"job:{job.get('job_id')}",
            "job_id": job.get("job_id"),
            "shot_id": job.get("shot_id"),
        })
        recon["estimated_total"] += est_f
        recon["actual_total"] += act_f

    for hist in state.get("quota", {}).get("history", []):
        note = hist.get("note", "")
        if "est:" in note:
            m = re.search(r"est:(\d+\.?\d*)", note)
            if m:
                est_f = float(m.group(1))
                act_f = float(hist.get("credits", 0))
                if not any(e.get("note") == note for e in recon["entries"]):
                    recon["entries"].append({
                        "at": hist.get("at", _now_iso()),
                        "estimated_credits": est_f,
                        "actual_credits": act_f,
                        "variance_credits": round(act_f - est_f, 2),
                        "note": note,
                    })
                    recon["estimated_total"] += est_f
                    recon["actual_total"] += act_f

    recon["estimated_total"] = round(recon["estimated_total"], 2)
    recon["actual_total"] = round(recon["actual_total"], 2)
    _recompute_burn_rate(recon)
    recon["updated_at"] = _now_iso()
    save_project_state(state)
    return recon


def quota_sync_summary(state: dict[str, Any] | None = None) -> dict[str, Any]:
    if state is None:
        state = load_project_state()
    recon = ensure_reconciliation(state)
    quota = state.get("quota", {})
    return {
        "session_spent": quota.get("session_spent", 0),
        "estimated_total": recon.get("estimated_total", 0),
        "actual_total": recon.get("actual_total", 0),
        "variance_pct": recon.get("variance_pct", 0),
        "burn_rate_multiplier": recon.get("burn_rate_multiplier", 1.0),
        "risk_level": recon.get("risk_level", "low"),
        "entry_count": len(recon.get("entries", [])),
        "updated_at": recon.get("updated_at"),
    }