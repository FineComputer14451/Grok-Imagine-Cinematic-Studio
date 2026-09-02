#!/usr/bin/env python3
"""
NSFW Quota Orchestrator — batch planning, persistence, and daily reports.

Domain split:
  nsfw_config.py    — tiers, retries, model routing constants
  nsfw_shots.py     — shot parsing, enrichment, create_shot
  nsfw_decisions.py — mode decisions, cost estimates, retry strategies
  nsfw_orchestrator.py — batch lifecycle (this module)
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from project_state import load_project_state, save_project_state
from quota_optimizer import (
    SUBSCRIPTION_TIERS,
    assess_budget_risk,
    ensure_quota_state,
)
from studio_paths import NSFW_BATCHES_DIR as BATCHES_DIR

from nsfw_config import (  # noqa: F401 — re-exported
    EXPLICIT_OPTIONS,
    GENERATION_MODES,
    HEAVY_DAILY_SOFT_CAP,
    MOTION_OPTIONS,
    NSFW_ASSET_MODEL_MAP,
    QUALITY_THRESHOLD_HERO,
    QUALITY_THRESHOLD_PASS,
    RETRY_REASON_OPTIONS,
    RETRY_RESERVE_PCT,
    RETRY_STRATEGIES,
    SCHEMA_VERSION,
    SHOT_TIER_OPTIONS,
    SHOT_TIERS,
)
from nsfw_decisions import (  # noqa: F401 — re-exported
    decide_generation_mode,
    estimate_shot_cost,
    suggest_retry,
)
from nsfw_shots import (  # noqa: F401 — re-exported
    apply_reference_curator_models,
    build_shot_context,
    create_shot,
    enrich_shot_for_batch,
    normalize_shot_input,
    parse_inline_shot,
)
from aspect_presets import plan_social_variants
from quality_pass_scheduler import (
    apply_quality_pass_promotion,
    get_pending_quality_passes,
    plan_two_pass_batch,
    promote_after_qa,
)
from nsfw_util import now_iso, slugify, today_iso

__all__ = [
    "EXPLICIT_OPTIONS",
    "GENERATION_MODES",
    "HEAVY_DAILY_SOFT_CAP",
    "MOTION_OPTIONS",
    "NSFW_ASSET_MODEL_MAP",
    "QUALITY_THRESHOLD_HERO",
    "QUALITY_THRESHOLD_PASS",
    "RETRY_REASON_OPTIONS",
    "RETRY_RESERVE_PCT",
    "RETRY_STRATEGIES",
    "SCHEMA_VERSION",
    "SHOT_TIER_OPTIONS",
    "SHOT_TIERS",
    "apply_reference_curator_models",
    "batch_to_markdown",
    "build_shot_context",
    "create_shot",
    "decide_generation_mode",
    "enrich_shot_for_batch",
    "estimate_shot_cost",
    "generate_daily_report",
    "get_next_shots",
    "list_batches",
    "load_batch",
    "normalize_shot_input",
    "parse_inline_shot",
    "plan_batch",
    "record_shot_result",
    "save_batch",
    "suggest_retry",
]


def _default_orchestrator_state() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "active_batch_id": None,
        "batches": {},
        "daily_log": {},
        "updated_at": now_iso(),
    }


def ensure_orchestrator_state(state: dict[str, Any]) -> dict[str, Any]:
    if "nsfw_orchestrator" not in state or not state["nsfw_orchestrator"]:
        state["nsfw_orchestrator"] = _default_orchestrator_state()
    orch = state["nsfw_orchestrator"]
    orch.setdefault("batches", {})
    orch.setdefault("daily_log", {})
    return orch


def plan_batch(
    title: str,
    shots: list[dict[str, Any]],
    *,
    tier: str = "supergrok_heavy",
    budget_credits: float | None = None,
    retry_reserve_pct: float = RETRY_RESERVE_PCT,
    fast_mode: bool = False,
    two_pass: bool = False,
) -> dict[str, Any]:
    """Plan an NSFW batch prioritized for Heavy subscription efficiency."""
    tier_info = SUBSCRIPTION_TIERS.get(tier, SUBSCRIPTION_TIERS["supergrok_heavy"])
    if budget_credits is None:
        daily = tier_info.get("daily_soft_cap") or 2500
        budget_credits = daily * 0.4

    usable = budget_credits * (1 - retry_reserve_pct)
    retry_reserve = budget_credits * retry_reserve_pct

    enriched = [
        enrich_shot_for_batch(normalize_shot_input(item), fast_mode=fast_mode)
        for item in shots
    ]
    if two_pass:
        enriched = plan_two_pass_batch(enriched, enabled=True)
    enriched.sort(key=lambda s: SHOT_TIERS.get(s.get("tier", "filler"), {}).get("priority", 99))

    scheduled: list[dict[str, Any]] = []
    deferred: list[dict[str, Any]] = []
    spent = 0.0

    for shot in enriched:
        est = shot.get("estimated_credits", 10)
        if spent + est <= usable:
            shot["batch_order"] = len(scheduled) + 1
            shot["status"] = "scheduled"
            scheduled.append(shot)
            spent += est
        else:
            shot["status"] = "deferred"
            shot["defer_reason"] = "Exceeds batch budget — run in next session or reduce tiers"
            deferred.append(shot)

    total_scheduled = sum(s.get("estimated_credits", 0) for s in scheduled)
    estimate_dict = {
        "credits_low": total_scheduled,
        "credits_high": total_scheduled + retry_reserve,
    }
    risk = assess_budget_risk(
        estimate_dict,
        tier=tier,
        budget_remaining=budget_credits,
    )

    batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    slug = slugify(title)
    return {
        "batch_id": batch_id,
        "slug": slug,
        "title": title,
        "tier": tier,
        "budget_credits": budget_credits,
        "retry_reserve_credits": round(retry_reserve, 1),
        "usable_credits": round(usable, 1),
        "scheduled_credits": round(total_scheduled, 1),
        "fast_mode": fast_mode,
        "two_pass": two_pass,
        "social_variants": plan_social_variants(enriched),
        "risk": risk,
        "shots_total": len(enriched),
        "shots_scheduled": len(scheduled),
        "shots_deferred": len(deferred),
        "execution_order": [s["shot_id"] for s in scheduled],
        "shots": scheduled + deferred,
        "status": "planned",
        "created_at": now_iso(),
    }


def save_batch(batch: dict[str, Any], batches_dir: Path | None = None) -> Path:
    root = batches_dir or BATCHES_DIR
    root.mkdir(parents=True, exist_ok=True)
    path = root / batch["slug"] / "batch.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(batch, indent=2))

    state = load_project_state()
    orch = ensure_orchestrator_state(state)
    orch["batches"][batch["batch_id"]] = {
        "slug": batch["slug"],
        "title": batch["title"],
        "path": str(path),
        "status": batch["status"],
        "created_at": batch["created_at"],
    }
    orch["active_batch_id"] = batch["batch_id"]
    orch["updated_at"] = now_iso()
    save_project_state(state)
    return path


def load_batch(slug_or_id: str, batches_dir: Path | None = None) -> dict[str, Any]:
    root = batches_dir or BATCHES_DIR
    state = load_project_state()
    orch = ensure_orchestrator_state(state)

    for bid, meta in orch.get("batches", {}).items():
        if slug_or_id in (bid, meta.get("slug")):
            path = Path(meta["path"])
            if path.exists():
                return json.loads(path.read_text())

    if root.exists():
        for path in root.glob("*/batch.json"):
            batch = json.loads(path.read_text())
            if slug_or_id in (batch.get("slug"), batch.get("batch_id"), path.parent.name):
                return batch

    raise FileNotFoundError(f"Batch not found: {slug_or_id}")


def list_batches() -> list[dict[str, Any]]:
    state = load_project_state()
    orch = ensure_orchestrator_state(state)
    return [
        {"batch_id": bid, **meta}
        for bid, meta in orch.get("batches", {}).items()
    ]


def get_next_shots(batch: dict[str, Any], count: int = 3) -> list[dict[str, Any]]:
    """Return next pending/scheduled shots in priority order."""
    pending = [
        s for s in batch.get("shots", [])
        if s.get("status") in ("scheduled", "pending", "qa_fail")
    ]
    pending.sort(key=lambda s: s.get("batch_order", SHOT_TIERS.get(s.get("tier", "filler"), {}).get("priority", 99)))
    results = []
    for shot in pending[:count]:
        decision = decide_generation_mode(shot)
        cost = estimate_shot_cost(
            {**shot, "recommended_mode": decision["mode"]},
            fast_mode=batch.get("fast_mode", False),
        )
        results.append({**shot, "decision": decision, "cost_estimate": cost})
    return results


def record_shot_result(
    batch: dict[str, Any],
    shot_id: str,
    *,
    quality_score: float,
    credits_spent: float,
    status: str = "generated",
    failure_reason: str | None = None,
    notes: str = "",
    record_quota: bool = True,
) -> dict[str, Any]:
    """Record generation outcome and update daily log."""
    shot = None
    for s in batch.get("shots", []):
        if s["shot_id"] == shot_id:
            shot = s
            break
    if not shot:
        raise ValueError(f"Shot not found: {shot_id}")

    tier = shot.get("tier", "support")
    threshold = QUALITY_THRESHOLD_HERO if tier in ("hero", "consistency_anchor") else QUALITY_THRESHOLD_PASS
    qa_pass = quality_score >= threshold

    attempt = {
        "at": now_iso(),
        "quality_score": quality_score,
        "credits_spent": credits_spent,
        "mode": shot.get("recommended_mode"),
        "qa_pass": qa_pass,
        "failure_reason": failure_reason,
        "notes": notes,
    }
    shot.setdefault("attempts", []).append(attempt)
    shot["quality_score"] = quality_score
    shot["status"] = "qa_pass" if qa_pass else "qa_fail"

    if not qa_pass and failure_reason:
        shot["retry_plan"] = suggest_retry(
            shot,
            failure_reason=failure_reason,
            quality_score=quality_score,
            attempts=len(shot["attempts"]),
        )

    today = today_iso()
    state = load_project_state()
    orch = ensure_orchestrator_state(state)
    daily = orch["daily_log"].setdefault(today, {
        "date": today,
        "sessions": [],
        "total_credits": 0,
        "shots_completed": 0,
        "shots_passed": 0,
        "shots_failed": 0,
        "quality_scores": [],
        "tier_breakdown": {},
    })
    daily["total_credits"] = round(daily["total_credits"] + credits_spent, 1)
    daily["shots_completed"] += 1
    if qa_pass:
        daily["shots_passed"] += 1
    else:
        daily["shots_failed"] += 1
    daily["quality_scores"].append(quality_score)
    tier_key = shot.get("tier", "unknown")
    daily["tier_breakdown"][tier_key] = daily["tier_breakdown"].get(tier_key, 0) + 1
    daily["sessions"].append({
        "shot_id": shot_id,
        "batch_id": batch.get("batch_id"),
        "quality_score": quality_score,
        "credits_spent": credits_spent,
        "qa_pass": qa_pass,
        "at": now_iso(),
    })

    orch["updated_at"] = now_iso()
    save_project_state(state)

    if qa_pass and shot.get("two_pass") and shot.get("pass_number", 1) == 1:
        promote_after_qa(shot, quality_score=quality_score, threshold=threshold)

    if record_quota:
        from quota_sync import record_generation_spend
        record_generation_spend(
            credits_spent,
            estimated_credits=shot.get("estimated_credits"),
            note=f"nsfw:{shot_id} est:{shot.get('estimated_credits')} {batch.get('title', '')}",
            shot_id=shot_id,
        )

    path = save_batch(batch)
    return {"shot": shot, "qa_pass": qa_pass, "saved_to": str(path)}


def generate_daily_report(
    report_date: str | None = None,
    *,
    output_path: Path | None = None,
) -> dict[str, Any]:
    """Build daily NSFW production report with quota vs quality analysis."""
    today = report_date or today_iso()
    state = load_project_state()
    orch = ensure_orchestrator_state(state)
    quota = ensure_quota_state(state)
    daily = orch["daily_log"].get(today, {
        "date": today,
        "total_credits": 0,
        "shots_completed": 0,
        "shots_passed": 0,
        "shots_failed": 0,
        "quality_scores": [],
        "tier_breakdown": {},
        "sessions": [],
    })

    scores = daily.get("quality_scores", [])
    avg_quality = round(sum(scores) / len(scores), 2) if scores else 0
    pass_rate = round(daily["shots_passed"] / daily["shots_completed"] * 100, 1) if daily.get("shots_completed") else 0

    tier_info = SUBSCRIPTION_TIERS.get(quota.get("tier", "supergrok_heavy"), SUBSCRIPTION_TIERS["supergrok_heavy"])
    daily_cap = tier_info.get("daily_soft_cap", HEAVY_DAILY_SOFT_CAP)
    pct_daily = round(daily["total_credits"] / daily_cap * 100, 1) if daily_cap else 0

    efficiency = round(avg_quality / max(daily["total_credits"], 1) * 100, 2) if daily["total_credits"] else 0

    recommendations: list[str] = []
    if pct_daily > 80:
        recommendations.append("Daily cap nearly exhausted — defer filler/support to tomorrow")
    if pass_rate < 60:
        recommendations.append("Low pass rate — increase consistency_anchor shots before key_intimate")
    if avg_quality < 7:
        recommendations.append("Avg quality below 7 — activate ErosForge + Identity Lock before next batch")
    if efficiency < 0.5:
        recommendations.append("Low quality-per-credit — favor image_prompt exploration before video")
    if not recommendations:
        recommendations.append("Session within efficient range — proceed with scheduled batch")

    report = {
        "report_date": today,
        "subscription_tier": quota.get("tier", "supergrok_heavy"),
        "tier_label": tier_info["label"],
        "daily_soft_cap": daily_cap,
        "credits_used_today": daily["total_credits"],
        "daily_cap_pct": pct_daily,
        "session_spent_total": quota.get("session_spent", 0),
        "budget_remaining": quota.get("budget_remaining"),
        "shots_completed": daily.get("shots_completed", 0),
        "shots_passed": daily.get("shots_passed", 0),
        "shots_failed": daily.get("shots_failed", 0),
        "pass_rate_pct": pass_rate,
        "avg_quality_score": avg_quality,
        "quality_per_credit": efficiency,
        "tier_breakdown": daily.get("tier_breakdown", {}),
        "recommendations": recommendations,
        "sessions": daily.get("sessions", []),
        "generated_at": now_iso(),
    }

    orch["daily_log"].setdefault(today, daily)["report"] = report
    save_project_state(state)

    if output_path:
        lines = [
            f"# NSFW Production Report — {today}",
            "",
            f"**Tier:** {report['tier_label']}",
            f"**Credits today:** {report['credits_used_today']} / {daily_cap} ({pct_daily}%)",
            f"**Shots:** {report['shots_completed']} completed | {report['shots_passed']} passed | {report['shots_failed']} failed",
            f"**Pass rate:** {pass_rate}%",
            f"**Avg quality:** {avg_quality}/10",
            f"**Quality per credit:** {efficiency}",
            "",
            "## Tier Breakdown",
        ]
        for t, n in report.get("tier_breakdown", {}).items():
            lines.append(f"- {t}: {n} shots")
        lines.extend(["", "## Recommendations"])
        for r in recommendations:
            lines.append(f"- {r}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n".join(lines) + "\n")
        report["output_path"] = str(output_path)

    return report


def batch_to_markdown(batch: dict[str, Any]) -> str:
    """Render batch plan as markdown for agent handoff."""
    lines = [
        f"# NSFW Batch Plan — {batch['title']}",
        "",
        f"**Batch ID:** {batch['batch_id']}",
        f"**Budget:** {batch['budget_credits']} credits (reserve {batch['retry_reserve_credits']} for retries)",
        f"**Scheduled:** {batch['shots_scheduled']} shots ({batch['scheduled_credits']} credits)",
        f"**Deferred:** {batch['shots_deferred']} shots",
        f"**Risk:** {batch['risk']['risk_level']}",
        "",
        "## Execution Order (priority)",
        "",
        "| # | Shot | Tier | Mode | Est. Credits | Status |",
        "|---|------|------|------|--------------|--------|",
    ]
    for shot in batch.get("shots", []):
        if shot.get("status") == "deferred":
            continue
        lines.append(
            f"| {shot.get('batch_order', '-')} | {shot['shot_id']} | {shot['tier']} | "
            f"{shot.get('recommended_mode', '?')} | {shot.get('estimated_credits', '?')} | {shot.get('status', '?')} |"
        )
    if batch.get("shots_deferred", 0) > 0:
        lines.extend(["", "## Deferred (quota)", ""])
        for shot in batch.get("shots", []):
            if shot.get("status") == "deferred":
                lines.append(f"- **{shot['shot_id']}** ({shot['tier']}): {shot.get('defer_reason', '')}")
    return "\n".join(lines) + "\n"