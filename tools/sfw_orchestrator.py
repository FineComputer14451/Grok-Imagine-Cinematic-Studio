#!/usr/bin/env python3
"""
SFW Batch Orchestrator — batch planning, persistence, and shot tracking.

Domain split:
  sfw_config.py     — tiers, retries, model routing constants
  sfw_shots.py      — shot parsing, enrichment, create_shot
  sfw_decisions.py  — mode decisions, cost estimates, retry strategies
  sfw_orchestrator.py — batch lifecycle (this module)
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from project_state import load_project_state, save_project_state
from quota_optimizer import SUBSCRIPTION_TIERS, assess_budget_risk
from studio_paths import SFW_BATCHES_DIR as BATCHES_DIR

from sfw_config import (  # noqa: F401 — re-exported
    GENERATION_MODES,
    MOTION_OPTIONS,
    PRO_DAILY_SOFT_CAP,
    QUALITY_THRESHOLD_HERO,
    QUALITY_THRESHOLD_PASS,
    RETRY_REASON_OPTIONS,
    RETRY_RESERVE_PCT,
    RETRY_STRATEGIES,
    SCHEMA_VERSION,
    SFW_ASSET_MODEL_MAP,
    SHOT_TIER_OPTIONS,
    SHOT_TIERS,
)
from sfw_decisions import (  # noqa: F401 — re-exported
    decide_generation_mode,
    estimate_shot_cost,
    suggest_retry,
)
from sfw_shots import (  # noqa: F401 — re-exported
    apply_reference_curator_models,
    build_shot_context,
    create_shot,
    enrich_shot_for_batch,
    normalize_shot_input,
    parse_inline_shot,
)
from aspect_presets import plan_social_variants
from quality_pass_scheduler import get_pending_quality_passes, plan_two_pass_batch, promote_after_qa, apply_quality_pass_promotion
from nsfw_util import now_iso, slugify

__all__ = [
    "GENERATION_MODES",
    "MOTION_OPTIONS",
    "PRO_DAILY_SOFT_CAP",
    "QUALITY_THRESHOLD_HERO",
    "QUALITY_THRESHOLD_PASS",
    "RETRY_REASON_OPTIONS",
    "RETRY_RESERVE_PCT",
    "RETRY_STRATEGIES",
    "SCHEMA_VERSION",
    "SFW_ASSET_MODEL_MAP",
    "SHOT_TIER_OPTIONS",
    "SHOT_TIERS",
    "apply_reference_curator_models",
    "batch_to_markdown",
    "build_shot_context",
    "create_shot",
    "decide_generation_mode",
    "enrich_shot_for_batch",
    "estimate_shot_cost",
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
        "updated_at": now_iso(),
    }


def ensure_orchestrator_state(state: dict[str, Any]) -> dict[str, Any]:
    if "sfw_orchestrator" not in state or not state["sfw_orchestrator"]:
        state["sfw_orchestrator"] = _default_orchestrator_state()
    orch = state["sfw_orchestrator"]
    orch.setdefault("batches", {})
    return orch


def plan_batch(
    title: str,
    shots: list[dict[str, Any]],
    *,
    tier: str = "supergrok_pro",
    budget_credits: float | None = None,
    retry_reserve_pct: float = RETRY_RESERVE_PCT,
    fast_mode: bool = False,
    two_pass: bool = False,
) -> dict[str, Any]:
    tier_info = SUBSCRIPTION_TIERS.get(tier, SUBSCRIPTION_TIERS["supergrok_pro"])
    if budget_credits is None:
        daily = tier_info.get("daily_soft_cap") or PRO_DAILY_SOFT_CAP
        budget_credits = daily * 0.5

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

    batch_id = f"sfw_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
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

    raise FileNotFoundError(f"SFW batch not found: {slug_or_id}")


def list_batches() -> list[dict[str, Any]]:
    state = load_project_state()
    orch = ensure_orchestrator_state(state)
    return [{"batch_id": bid, **meta} for bid, meta in orch.get("batches", {}).items()]


def get_next_shots(batch: dict[str, Any], count: int = 3) -> list[dict[str, Any]]:
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
    failure_reason: str | None = None,
    notes: str = "",
    record_quota: bool = True,
) -> dict[str, Any]:
    shot = None
    for s in batch.get("shots", []):
        if s["shot_id"] == shot_id:
            shot = s
            break
    if not shot:
        raise ValueError(f"Shot not found: {shot_id}")

    tier = shot.get("tier", "coverage")
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

    state = load_project_state()
    orch = ensure_orchestrator_state(state)
    orch["updated_at"] = now_iso()
    save_project_state(state)

    if qa_pass and shot.get("two_pass") and shot.get("pass_number", 1) == 1:
        promote_after_qa(shot, quality_score=quality_score, threshold=threshold)

    if record_quota:
        from quota_sync import record_generation_spend
        record_generation_spend(
            credits_spent,
            estimated_credits=shot.get("estimated_credits"),
            note=f"sfw:{shot_id} est:{shot.get('estimated_credits')} {batch.get('title', '')}",
            shot_id=shot_id,
        )

    path = save_batch(batch)
    return {"shot": shot, "qa_pass": qa_pass, "saved_to": str(path)}


def batch_to_markdown(batch: dict[str, Any]) -> str:
    lines = [
        f"# SFW Batch Plan — {batch['title']}",
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