"""Long-form sequence health dashboard (roadmap #10).

Pure aggregator: reads stored clip/sequence evidence fields without re-scoring.
CLI should call ``update_sequence_health`` before ``build_longform_health`` when
a refreshed health score is desired.
"""

from __future__ import annotations

from datetime import datetime, timezone
from statistics import mean
from typing import Any

from quota_optimizer import estimate_sequence_cost

# Align with identity_drift default threshold used for alerts
DEFAULT_DRIFT_ALERT_THRESHOLD = 2.5

APPROVED_STATUSES = frozenset({"approved"})


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _avg(values: list[float]) -> float | None:
    if not values:
        return None
    return round(mean(values), 4)


def build_longform_health(seq: dict[str, Any]) -> dict[str, Any]:
    """Aggregate long-form health metrics from an existing sequence dict.

    Does **not** call ``update_sequence_health`` — reads whatever scores are
    already present on the sequence and its clips.
    """
    clips: list[dict[str, Any]] = list(seq.get("clips") or [])

    chain_go = chain_no_go = chain_conditional = chain_pending = 0
    weighted_scores: list[float] = []

    drift_scores: list[float] = []
    drift_trend: list[float] = []
    drift_fail = 0

    seam_risks: list[float] = []
    seam_fail = 0

    amv_scores: list[float] = []
    amv_fail = 0

    regen_total = 0
    regen_clips_with = 0
    regen_budget_exhausted = 0

    temp_samples = 0
    temp_fail = 0
    temp_warn = 0

    cont_clips = 0
    cont_total_changes = 0

    clips_approved = 0
    clips_qa_hold = 0
    clips_pending = 0

    clip_rows: list[dict[str, Any]] = []
    alerts: list[str] = []

    for clip in clips:
        status = str(clip.get("status") or "pending")
        if status == "approved":
            clips_approved += 1
        elif status == "qa_hold":
            clips_qa_hold += 1
        else:
            clips_pending += 1

        qa = _as_dict(clip.get("chain_qa"))
        decision = qa.get("decision")
        if decision == "go":
            chain_go += 1
        elif decision == "no_go":
            chain_no_go += 1
        elif decision in ("conditional_go", "conditional"):
            chain_conditional += 1
        else:
            chain_pending += 1

        w = _safe_float(qa.get("weighted_score"))
        if w is not None:
            weighted_scores.append(w)

        drift = _as_dict(clip.get("identity_drift"))
        ds = _safe_float(drift.get("drift_score"))
        if ds is not None:
            drift_scores.append(ds)
            drift_trend.append(ds)
        if drift and drift.get("pass") is False:
            drift_fail += 1

        seam = _as_dict(clip.get("seam_report"))
        sr = _safe_float(seam.get("seam_risk"))
        if sr is not None:
            seam_risks.append(sr)
        if seam and seam.get("pass") is False:
            seam_fail += 1

        amv = _as_dict(clip.get("audio_momentum_report"))
        ai = _safe_float(amv.get("integrity_score"))
        if ai is not None:
            amv_scores.append(ai)
        if amv and amv.get("pass") is False:
            amv_fail += 1

        regen = _as_dict(clip.get("regen"))
        attempts = _safe_int(regen.get("attempts"), 0) if regen else 0
        if attempts > 0:
            regen_clips_with += 1
            regen_total += attempts
        max_attempts = regen.get("max_attempts") if regen else None
        if max_attempts is not None and attempts >= _safe_int(max_attempts, 0):
            regen_budget_exhausted += 1

        temp = _as_dict(clip.get("temperature_gate"))
        if temp:
            temp_samples += 1
            severity = str(temp.get("severity") or "").lower()
            if temp.get("pass") is False or severity == "fail":
                temp_fail += 1
            elif severity in ("warn", "warning"):
                temp_warn += 1

        cdiff = _as_dict(clip.get("continuity_diff"))
        summary = _as_dict(cdiff.get("summary"))
        cont_total: int | None = None
        if summary and "total" in summary:
            cont_total = _safe_int(summary.get("total"), 0)
            cont_clips += 1
            cont_total_changes += cont_total

        clip_rows.append(
            {
                "clip_id": clip.get("clip_id") or f"clip_{clip.get('index', 0) + 1:03d}",
                "index": _safe_int(clip.get("index"), 0),
                "status": status,
                "qa_decision": decision if decision is not None else None,
                "weighted_score": w,
                "drift_score": ds,
                "seam_risk": sr,
                "amv_integrity": ai,
                "regen_attempts": attempts,
                "temp_severity": (str(temp.get("severity")) if temp.get("severity") is not None else None)
                if temp
                else None,
                "cont_diff_total": cont_total,
            }
        )

    budget = _as_dict(seq.get("regen_budget"))
    sequence_attempts_used = _safe_int(budget.get("sequence_attempts_used"), 0)

    # Alerts (human one-liners)
    if chain_no_go > 0:
        alerts.append(f"{chain_no_go} clip(s) with chain QA no_go")
    if drift_scores:
        max_drift = max(drift_scores)
        if max_drift >= DEFAULT_DRIFT_ALERT_THRESHOLD:
            alerts.append(f"High identity drift (max {max_drift})")
    if drift_fail > 0:
        alerts.append(f"{drift_fail} clip(s) failed identity drift")
    if seam_fail > 0:
        alerts.append(f"{seam_fail} clip(s) failed seam risk")
    if amv_fail > 0:
        alerts.append(f"{amv_fail} clip(s) failed audio momentum integrity")
    if regen_budget_exhausted > 0:
        alerts.append(f"{regen_budget_exhausted} clip(s) with regen budget exhausted")
    max_seq = budget.get("max_sequence_attempts")
    if (
        max_seq is not None
        and sequence_attempts_used >= _safe_int(max_seq, 0)
        and _safe_int(max_seq, 0) > 0
    ):
        alerts.append(
            f"Sequence regen budget exhausted "
            f"({sequence_attempts_used}/{max_seq})"
        )
    if temp_fail > 0:
        alerts.append(f"{temp_fail} clip(s) failed temperature gate")

    remaining = [c for c in clips if str(c.get("status") or "") not in APPROVED_STATUSES]
    remaining_duration = sum(_safe_int(c.get("duration_seconds"), 10) for c in remaining)

    cost_estimate: dict[str, Any] | None = None
    credits_low = credits_high = usd_low = usd_high = None
    if remaining:
        cost_estimate = estimate_sequence_cost(remaining)
        credits_low = cost_estimate.get("credits_low")
        credits_high = cost_estimate.get("credits_high")
        usd_low = cost_estimate.get("usd_low")
        usd_high = cost_estimate.get("usd_high")

    health_raw = seq.get("sequence_health_score")
    health_score = _safe_float(health_raw)

    return {
        "sequence_name": seq.get("sequence_name") or "",
        "slug": seq.get("slug") or "",
        "generated_at": _now_iso(),
        "health_score": health_score,
        "chain_qa_status": seq.get("chain_qa_status") or "pending",
        "clip_count": len(clips),
        "target_duration_seconds": _safe_int(seq.get("target_duration_seconds"), 0),
        "clips_approved": clips_approved,
        "clips_qa_hold": clips_qa_hold,
        "clips_pending": clips_pending,
        "chain_qa": {
            "go": chain_go,
            "no_go": chain_no_go,
            "conditional_go": chain_conditional,
            "pending": chain_pending,
            "avg_weighted_score": _avg(weighted_scores),
        },
        "drift": {
            "samples": len(drift_scores),
            "avg_score": _avg(drift_scores),
            "max_score": max(drift_scores) if drift_scores else None,
            "fail_count": drift_fail,
            "trend": drift_trend,
        },
        "seam": {
            "samples": len(seam_risks),
            "avg_risk": _avg(seam_risks),
            "max_risk": max(seam_risks) if seam_risks else None,
            "fail_count": seam_fail,
        },
        "audio_momentum": {
            "samples": len(amv_scores),
            "avg_integrity": _avg(amv_scores),
            "fail_count": amv_fail,
        },
        "regen": {
            "clips_with_attempts": regen_clips_with,
            "total_attempts": regen_total,
            "sequence_attempts_used": sequence_attempts_used,
            "budget_exhausted_clips": regen_budget_exhausted,
        },
        "temperature": {
            "samples": temp_samples,
            "fail_count": temp_fail,
            "warn_count": temp_warn,
        },
        "continuity_diff": {
            "clips_with_diff": cont_clips,
            "total_changes": cont_total_changes,
        },
        "cost": {
            "estimate": cost_estimate,
            "remaining_clips": len(remaining),
            "remaining_duration_seconds": remaining_duration,
            "credits_low": credits_low,
            "credits_high": credits_high,
            "usd_low": usd_low,
            "usd_high": usd_high,
        },
        "clip_rows": clip_rows,
        "alerts": alerts,
    }


def format_longform_health_markdown(report: dict[str, Any]) -> str:
    """Render a long-form health report as Markdown."""
    name = report.get("sequence_name") or report.get("slug") or "Sequence"
    health = report.get("health_score")
    health_disp = health if health is not None else "—"
    lines = [
        f"# Long-Form Health — {name}",
        "",
        f"**Generated:** {report.get('generated_at', '—')}  ",
        f"**Slug:** `{report.get('slug', '')}`  ",
        f"**Health Score:** {health_disp}  ",
        f"**Chain QA Status:** {report.get('chain_qa_status', 'pending')}  ",
        f"**Clips:** {report.get('clip_count', 0)} "
        f"(approved {report.get('clips_approved', 0)}, "
        f"qa_hold {report.get('clips_qa_hold', 0)}, "
        f"pending {report.get('clips_pending', 0)})  ",
        f"**Target Duration:** {report.get('target_duration_seconds', 0)}s",
        "",
    ]

    alerts = report.get("alerts") or []
    if alerts:
        lines.append("## Alerts")
        for a in alerts:
            lines.append(f"- ⚠ {a}")
        lines.append("")
    else:
        lines += ["## Alerts", "- None", ""]

    cq = report.get("chain_qa") or {}
    lines += [
        "## Chain QA",
        f"- go: {cq.get('go', 0)} | no_go: {cq.get('no_go', 0)} | "
        f"conditional: {cq.get('conditional_go', 0)} | pending: {cq.get('pending', 0)}",
        f"- avg weighted score: {cq.get('avg_weighted_score', '—')}",
        "",
    ]

    drift = report.get("drift") or {}
    lines += [
        "## Identity Drift",
        f"- samples: {drift.get('samples', 0)} | avg: {drift.get('avg_score', '—')} | "
        f"max: {drift.get('max_score', '—')} | fails: {drift.get('fail_count', 0)}",
        "",
    ]

    seam = report.get("seam") or {}
    lines += [
        "## Seam Risk",
        f"- samples: {seam.get('samples', 0)} | avg: {seam.get('avg_risk', '—')} | "
        f"max: {seam.get('max_risk', '—')} | fails: {seam.get('fail_count', 0)}",
        "",
    ]

    amv = report.get("audio_momentum") or {}
    lines += [
        "## Audio Momentum",
        f"- samples: {amv.get('samples', 0)} | avg integrity: {amv.get('avg_integrity', '—')} | "
        f"fails: {amv.get('fail_count', 0)}",
        "",
    ]

    regen = report.get("regen") or {}
    lines += [
        "## Re-gen",
        f"- clips with attempts: {regen.get('clips_with_attempts', 0)} | "
        f"total attempts: {regen.get('total_attempts', 0)}",
        f"- sequence attempts used: {regen.get('sequence_attempts_used', 0)} | "
        f"budget exhausted clips: {regen.get('budget_exhausted_clips', 0)}",
        "",
    ]

    temp = report.get("temperature") or {}
    lines += [
        "## Temperature Gate",
        f"- samples: {temp.get('samples', 0)} | fails: {temp.get('fail_count', 0)} | "
        f"warns: {temp.get('warn_count', 0)}",
        "",
    ]

    cdiff = report.get("continuity_diff") or {}
    lines += [
        "## Continuity Diff",
        f"- clips with diff: {cdiff.get('clips_with_diff', 0)} | "
        f"total changes: {cdiff.get('total_changes', 0)}",
        "",
    ]

    cost = report.get("cost") or {}
    lines += [
        "## Remaining Cost",
        f"- remaining clips: {cost.get('remaining_clips', 0)} "
        f"({cost.get('remaining_duration_seconds', 0)}s)",
        f"- credits: {cost.get('credits_low', '—')} – {cost.get('credits_high', '—')}",
        f"- USD: ${cost.get('usd_low', '—')} – ${cost.get('usd_high', '—')}",
        "",
    ]

    rows = report.get("clip_rows") or []
    lines.append("## Clips")
    if not rows:
        lines.append("_No clips._")
    else:
        lines.append(
            "| Clip | Status | QA | Score | Drift | Seam | AMV | Regen | Temp | ContDiff |"
        )
        lines.append("|------|--------|----|-------|-------|------|-----|-------|------|----------|")
        for r in rows:
            lines.append(
                f"| {r.get('clip_id', '—')} | {r.get('status', '—')} | "
                f"{r.get('qa_decision') or '—'} | {r.get('weighted_score') if r.get('weighted_score') is not None else '—'} | "
                f"{r.get('drift_score') if r.get('drift_score') is not None else '—'} | "
                f"{r.get('seam_risk') if r.get('seam_risk') is not None else '—'} | "
                f"{r.get('amv_integrity') if r.get('amv_integrity') is not None else '—'} | "
                f"{r.get('regen_attempts', 0)} | {r.get('temp_severity') or '—'} | "
                f"{r.get('cont_diff_total') if r.get('cont_diff_total') is not None else '—'} |"
            )
    lines.append("")
    return "\n".join(lines)
