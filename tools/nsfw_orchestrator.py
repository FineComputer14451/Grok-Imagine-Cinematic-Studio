#!/usr/bin/env python3
"""
NSFW Quota Orchestrator — batch planning, i2v decisions, retry strategies, daily reports.

Integrates with workflow-quota-optimizer (quota_optimizer.py) and ErosForge protocols.
"""

from __future__ import annotations

import json
import re
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from models import (
    DEFAULT_IMAGINE_IMAGE_MODEL,
    DEFAULT_IMAGINE_VIDEO_MODEL,
    IMAGINE_IMAGE_MODELS,
    IMAGINE_VIDEO_MODELS,
    usd_to_credits,
)
from project_state import load_project_state, save_project_state
from quota_optimizer import (
    SUBSCRIPTION_TIERS,
    assess_budget_risk,
    estimate_clip_cost,
    ensure_quota_state,
    load_pricing_config,
    record_spend,
)
from studio_paths import NSFW_BATCHES_DIR as BATCHES_DIR

SCHEMA_VERSION = "1.0"

SHOT_TIERS: dict[str, dict[str, Any]] = {
    "hero": {
        "priority": 1,
        "budget_share": 0.25,
        "label": "Hero Frame",
        "description": "Cover shots, primary deliverables, highest visual impact",
    },
    "consistency_anchor": {
        "priority": 2,
        "budget_share": 0.15,
        "label": "Consistency Anchor",
        "description": "Identity lock reference frames — generate before dependent shots",
    },
    "key_explicit": {
        "priority": 3,
        "budget_share": 0.35,
        "label": "Key Explicit Moment",
        "description": "Narrative-critical intimate beats with explicit intent",
    },
    "support": {
        "priority": 4,
        "budget_share": 0.15,
        "label": "Support Shot",
        "description": "Transitions, establishing frames, emotional B-roll",
    },
    "filler": {
        "priority": 5,
        "budget_share": 0.10,
        "label": "Atmosphere Filler",
        "description": "Optional mood shots — skip first when quota is tight",
    },
}

GENERATION_MODES = ("image_prompt", "image_to_video", "video_prompt")

RETRY_STRATEGIES: dict[str, dict[str, Any]] = {
    "identity_drift": {
        "label": "Identity Drift",
        "actions": [
            "Regenerate consistency_anchor with tightened Character DNA inject",
            "Switch to image_to_video from locked anchor still",
            "Reduce face motion; hold close-up with minimal head turn",
        ],
        "max_retries": 2,
        "cost_multiplier": 1.3,
    },
    "physics_failure": {
        "label": "Physics / Motion Failure",
        "actions": [
            "Simplify motion prompt to one primary beat",
            "Shorten clip to 6–8s sweet spot",
            "Use Fast mode draft, then quality pass on passable take",
        ],
        "max_retries": 2,
        "cost_multiplier": 1.2,
    },
    "emotional_flat": {
        "label": "Emotional Flatness",
        "actions": [
            "Add micro-expression timing beats at t=2s and t=5s",
            "Adjust motivated lighting (rim + practical warmth)",
            "Inject Performance & Emotion Director subtext layer",
        ],
        "max_retries": 1,
        "cost_multiplier": 1.0,
    },
    "explicit_uncanny": {
        "label": "Uncanny Explicit Detail",
        "actions": [
            "Pull back to suggestive framing; imply rather than depict",
            "Regen still with image_prompt, then i2v with subtle motion",
            "Reduce simultaneous body-part focus in prompt",
        ],
        "max_retries": 2,
        "cost_multiplier": 1.15,
    },
    "audio_sync_fail": {
        "label": "Audio Sync Failure",
        "actions": [
            "Shorten dialogue to one line under 3s",
            "SFX + ambience only pass (no lip-sync)",
            "Split into two clips at breath pause",
        ],
        "max_retries": 1,
        "cost_multiplier": 1.25,
    },
    "quota_pressure": {
        "label": "Quota Pressure",
        "actions": [
            "Downgrade to image_prompt for exploration",
            "Defer filler and support tiers",
            "Batch hero + anchor only; resume tomorrow",
        ],
        "max_retries": 0,
        "cost_multiplier": 0.5,
    },
}

QUALITY_THRESHOLD_PASS = 7.0
QUALITY_THRESHOLD_HERO = 8.0

HEAVY_DAILY_SOFT_CAP = SUBSCRIPTION_TIERS["supergrok_heavy"]["daily_soft_cap"]
RETRY_RESERVE_PCT = 0.15

DEFAULT_IMAGE_QUALITY_MODEL = "grok-imagine-image-quality"
DEFAULT_VIDEO_DRAFT_MODEL = "grok-imagine-video"

# Reference & Asset Curator routing for NSFW shot tiers
NSFW_ASSET_MODEL_MAP: dict[str, dict[str, Any]] = {
    "hero": {
        "asset_tier": "hero",
        "image_model": DEFAULT_IMAGE_QUALITY_MODEL,
        "video_model": DEFAULT_IMAGINE_VIDEO_MODEL,
        "image_quality": True,
    },
    "key_explicit": {
        "asset_tier": "hero",
        "image_model": DEFAULT_IMAGE_QUALITY_MODEL,
        "video_model": DEFAULT_IMAGINE_VIDEO_MODEL,
        "image_quality": True,
    },
    "consistency_anchor": {
        "asset_tier": "hero",
        "image_model": DEFAULT_IMAGE_QUALITY_MODEL,
        "video_model": DEFAULT_IMAGINE_VIDEO_MODEL,
        "image_quality": True,
    },
    "support": {
        "asset_tier": "standard",
        "image_model": DEFAULT_IMAGINE_IMAGE_MODEL,
        "video_model": DEFAULT_IMAGINE_VIDEO_MODEL,
        "image_quality": False,
    },
    "filler": {
        "asset_tier": "draft",
        "image_model": DEFAULT_IMAGINE_IMAGE_MODEL,
        "video_model": DEFAULT_VIDEO_DRAFT_MODEL,
        "image_quality": False,
    },
}


SHOT_TIER_OPTIONS: tuple[str, ...] = tuple(
    sorted(SHOT_TIERS.keys(), key=lambda t: SHOT_TIERS[t]["priority"])
)
RETRY_REASON_OPTIONS: tuple[str, ...] = tuple(RETRY_STRATEGIES.keys())
MOTION_OPTIONS: tuple[str, ...] = ("low", "medium", "high")
EXPLICIT_OPTIONS: tuple[str, ...] = ("suggestive", "moderate", "explicit")


def build_shot_context(
    shot_id: str,
    *,
    tier: str = "support",
    motion: str = "medium",
    has_ref: bool = False,
    explicit: str = "moderate",
    duration: float = 10.0,
    consistency_required: bool = True,
    recommended_mode: str | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    """Canonical shot dict for decide/retry flows (CLI + Web UI)."""
    ctx: dict[str, Any] = {
        "shot_id": shot_id,
        "tier": tier if tier in SHOT_TIERS else "support",
        "motion_complexity": motion,
        "has_reference": has_ref,
        "explicit_level": explicit,
        "duration_seconds": duration,
        "consistency_required": consistency_required,
    }
    if recommended_mode is not None:
        ctx["recommended_mode"] = recommended_mode
    if description is not None:
        ctx["description"] = description
    return ctx


def parse_inline_shot(spec: str) -> dict[str, Any]:
    """Parse tier:description or tier:motion:description."""
    parts = spec.split(":", 2)
    if len(parts) == 2:
        tier, desc = parts
        motion = "medium"
    elif len(parts) == 3:
        tier, motion, desc = parts
    else:
        tier, motion, desc = "support", "medium", spec
    return {
        "tier": tier.strip(),
        "description": desc.strip(),
        "motion_complexity": motion.strip(),
    }


def apply_reference_curator_models(shot: dict[str, Any]) -> dict[str, Any]:
    """Assign image/video model slugs per Reference & Asset Curator NSFW tier map."""
    tier = shot.get("tier", "support")
    mapping = NSFW_ASSET_MODEL_MAP.get(tier, NSFW_ASSET_MODEL_MAP["support"])
    shot["asset_tier"] = mapping["asset_tier"]
    shot["image_model"] = mapping["image_model"]
    shot["video_model"] = mapping["video_model"]
    shot["image_quality"] = mapping["image_quality"]
    if shot["image_model"] not in IMAGINE_IMAGE_MODELS:
        shot["image_model"] = DEFAULT_IMAGINE_IMAGE_MODEL
    if shot["video_model"] not in IMAGINE_VIDEO_MODELS:
        shot["video_model"] = DEFAULT_IMAGINE_VIDEO_MODEL
    return shot


def normalize_shot_input(raw: str | dict[str, Any]) -> dict[str, Any]:
    """Accept dict or inline tier:description string."""
    if isinstance(raw, str):
        return parse_inline_shot(raw)
    return dict(raw)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _today() -> str:
    return date.today().isoformat()


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "untitled-batch"


def _default_orchestrator_state() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "active_batch_id": None,
        "batches": {},
        "daily_log": {},
        "updated_at": _now_iso(),
    }


def ensure_orchestrator_state(state: dict[str, Any]) -> dict[str, Any]:
    if "nsfw_orchestrator" not in state or not state["nsfw_orchestrator"]:
        state["nsfw_orchestrator"] = _default_orchestrator_state()
    orch = state["nsfw_orchestrator"]
    orch.setdefault("batches", {})
    orch.setdefault("daily_log", {})
    return orch


def estimate_shot_cost(
    shot: dict[str, Any],
    *,
    fast_mode: bool = False,
    pricing: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Estimate credits for a single shot based on recommended modality."""
    p = pricing or load_pricing_config()
    mode = shot.get("recommended_mode") or decide_generation_mode(shot).get("mode", "image_prompt")
    img_slug = shot.get("image_model", p.get("default_image_model", DEFAULT_IMAGINE_IMAGE_MODEL))
    vid_slug = shot.get("video_model", p.get("default_video_model", DEFAULT_IMAGINE_VIDEO_MODEL))

    if mode == "image_prompt":
        img_rates = p.get("imagine_image", {})
        usd = img_rates.get(img_slug, {}).get("usd_per_image", 0.02)
        if shot.get("image_quality"):
            q_slug = "grok-imagine-image-quality"
            usd = img_rates.get(q_slug, {}).get("usd_per_image", 0.05)
        credits = usd_to_credits(usd)
        return {"mode": mode, "credits": credits, "usd": round(usd, 2)}

    if mode == "image_to_video":
        img_rates = p.get("imagine_image", {})
        img_usd = img_rates.get(img_slug, {}).get("usd_per_image", 0.02)
        dur = shot.get("duration_seconds", 10)
        clip = estimate_clip_cost(dur, video_model=vid_slug, fast_mode=fast_mode, pricing=p)
        total_usd = img_usd + clip["usd_high"]
        return {
            "mode": mode,
            "credits": usd_to_credits(total_usd),
            "usd": round(total_usd, 2),
            "breakdown": {"image_usd": img_usd, "video": clip},
        }

    dur = shot.get("duration_seconds", 10)
    clip = estimate_clip_cost(dur, video_model=vid_slug, fast_mode=fast_mode, pricing=p)
    return {"mode": mode, "credits": clip["credits_high"], "usd": clip["usd_high"], "breakdown": clip}


def decide_generation_mode(
    shot: dict[str, Any],
    *,
    budget_remaining: float | None = None,
    risk_level: str = "low",
) -> dict[str, Any]:
    """
    Recommend image_prompt vs image_to_video vs video_prompt.

    Rules (priority order):
    1. Quota critical → image_prompt for non-hero shots
    2. Consistency anchor / hero with no ref → image_prompt first
    3. Has approved reference + motion → image_to_video
    4. High motion complexity without ref → image_prompt then i2v
    5. Static portrait / pose → image_prompt
    6. Key explicit with locked anchor → image_to_video
    """
    tier = shot.get("tier", "support")
    has_ref = shot.get("has_reference", False)
    consistency = shot.get("consistency_required", True)
    motion = shot.get("motion_complexity", "medium")
    explicit = shot.get("explicit_level", "moderate")
    duration = shot.get("duration_seconds", 10)

    reasons: list[str] = []
    mode = "image_prompt"
    confidence = 0.7

    if risk_level in ("high", "critical") and tier not in ("hero", "consistency_anchor"):
        mode = "image_prompt"
        reasons.append("Quota pressure — explore with still before video spend")
        confidence = 0.9
    elif tier == "consistency_anchor" and not has_ref:
        mode = "image_prompt"
        reasons.append("Anchor frame must be locked as still before dependent video")
        confidence = 0.95
    elif has_ref and motion in ("medium", "high"):
        mode = "image_to_video"
        reasons.append("Approved reference + motion intent — i2v preserves identity")
        confidence = 0.92
    elif tier in ("hero", "key_explicit") and has_ref:
        mode = "image_to_video"
        reasons.append("High-impact shot with reference — i2v for fidelity")
        confidence = 0.88
    elif motion == "low" and explicit in ("suggestive", "moderate"):
        mode = "image_prompt"
        reasons.append("Low motion intimate still — image is quota-efficient")
        confidence = 0.85
    elif motion == "high" and not has_ref:
        mode = "image_prompt"
        reasons.append("High motion without anchor — generate still first, then i2v")
        confidence = 0.8
    elif duration >= 10 and consistency and has_ref:
        mode = "image_to_video"
        reasons.append("Long consistent clip — extend from locked still")
        confidence = 0.87
    elif tier == "filler":
        mode = "image_prompt"
        reasons.append("Filler tier — still exploration unless budget surplus")
        confidence = 0.75
    else:
        mode = "video_prompt"
        reasons.append("No reference; direct video prompt for atmospheric motion")
        confidence = 0.65

    if budget_remaining is not None and budget_remaining < 100 and mode != "image_prompt":
        mode = "image_prompt"
        reasons.append(f"Budget remaining {budget_remaining:.0f} credits — defer video")
        confidence = 0.95

    return {
        "shot_id": shot.get("shot_id"),
        "mode": mode,
        "confidence": confidence,
        "reasons": reasons,
        "follow_up": _follow_up_action(mode, shot),
    }


def _follow_up_action(mode: str, shot: dict[str, Any]) -> str | None:
    if mode == "image_prompt" and shot.get("motion_complexity") in ("medium", "high"):
        return "On QA pass ≥7, promote to image_to_video using this still as reference"
    if mode == "video_prompt" and shot.get("consistency_required"):
        return "Consider generating consistency_anchor first if identity drifts"
    return None


def suggest_retry(
    shot: dict[str, Any],
    *,
    failure_reason: str,
    quality_score: float | None = None,
    attempts: int = 0,
) -> dict[str, Any]:
    """Return retry strategy for a failed or under-threshold shot."""
    reason_key = failure_reason.lower().replace(" ", "_").replace("-", "_")
    if reason_key not in RETRY_STRATEGIES:
        for key in RETRY_STRATEGIES:
            if key in reason_key or reason_key in key:
                reason_key = key
                break
        else:
            reason_key = "physics_failure"

    strategy = RETRY_STRATEGIES[reason_key]
    max_retries = strategy["max_retries"]
    tier = shot.get("tier", "support")
    threshold = QUALITY_THRESHOLD_HERO if tier in ("hero", "consistency_anchor") else QUALITY_THRESHOLD_PASS

    if attempts >= max_retries:
        return {
            "action": "skip_or_defer",
            "reason": f"Max retries ({max_retries}) reached for {strategy['label']}",
            "suggestions": strategy["actions"] + ["Defer to next session or downgrade tier"],
            "estimated_extra_credits": 0,
        }

    base_cost = estimate_shot_cost(shot).get("credits", 10)
    extra = round(base_cost * strategy["cost_multiplier"], 1)

    variation_hints = []
    if quality_score and quality_score < threshold:
        variation_hints.append(f"Score {quality_score}/10 below threshold {threshold} for {tier}")
    variation_hints.extend([
        f"Attempt {attempts + 1}/{max_retries}",
        "Vary seed: adjust lighting ratio ±15%, camera height ±10cm",
        "Inject ErosForge post_scene_state from previous attempt",
    ])

    return {
        "action": "retry",
        "failure_reason": strategy["label"],
        "suggestions": strategy["actions"],
        "variation_hints": variation_hints,
        "estimated_extra_credits": extra,
        "promote_mode": decide_generation_mode(shot).get("mode"),
    }


def create_shot(
    description: str,
    *,
    tier: str = "support",
    shot_id: str | None = None,
    duration_seconds: float = 10,
    has_reference: bool = False,
    consistency_required: bool = True,
    motion_complexity: str = "medium",
    explicit_level: str = "moderate",
    image_quality: bool = False,
) -> dict[str, Any]:
    if tier not in SHOT_TIERS:
        tier = "support"
    sid = shot_id or f"shot_{tier[:3]}_{datetime.now().strftime('%H%M%S')}"
    shot = {
        "shot_id": sid,
        "tier": tier,
        "description": description,
        "duration_seconds": duration_seconds,
        "has_reference": has_reference,
        "consistency_required": consistency_required,
        "motion_complexity": motion_complexity,
        "explicit_level": explicit_level,
        "image_quality": image_quality,
        "status": "pending",
        "attempts": [],
        "quality_score": None,
        "recommended_mode": None,
        "estimated_credits": None,
        "created_at": _now_iso(),
    }
    decision = decide_generation_mode(shot)
    cost = estimate_shot_cost({**shot, "recommended_mode": decision["mode"]})
    shot["recommended_mode"] = decision["mode"]
    shot["estimated_credits"] = cost["credits"]
    return apply_reference_curator_models(shot)


def plan_batch(
    title: str,
    shots: list[dict[str, Any]],
    *,
    tier: str = "supergrok_heavy",
    budget_credits: float | None = None,
    retry_reserve_pct: float = RETRY_RESERVE_PCT,
    fast_mode: bool = False,
) -> dict[str, Any]:
    """Plan an NSFW batch prioritized for Heavy subscription efficiency."""
    tier_info = SUBSCRIPTION_TIERS.get(tier, SUBSCRIPTION_TIERS["supergrok_heavy"])
    if budget_credits is None:
        daily = tier_info.get("daily_soft_cap") or 2500
        budget_credits = daily * 0.4

    usable = budget_credits * (1 - retry_reserve_pct)
    retry_reserve = budget_credits * retry_reserve_pct

    enriched: list[dict[str, Any]] = []
    for i, item in enumerate(shots):
        raw = normalize_shot_input(item)
        apply_reference_curator_models(raw)
        if "shot_id" not in raw:
            raw = create_shot(
                raw.get("description", f"Shot {i + 1}"),
                tier=raw.get("tier", "support"),
                duration_seconds=raw.get("duration_seconds", 10),
                has_reference=raw.get("has_reference", False),
                consistency_required=raw.get("consistency_required", True),
                motion_complexity=raw.get("motion_complexity", "medium"),
                explicit_level=raw.get("explicit_level", "moderate"),
                image_quality=raw.get("image_quality", False),
            )
        else:
            decision = decide_generation_mode(raw)
            cost = estimate_shot_cost({**raw, "recommended_mode": decision["mode"]}, fast_mode=fast_mode)
            raw["recommended_mode"] = decision["mode"]
            raw["estimated_credits"] = cost["credits"]
            apply_reference_curator_models(raw)
        enriched.append(raw)

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
    slug = _slugify(title)
    batch = {
        "batch_id": batch_id,
        "slug": slug,
        "title": title,
        "tier": tier,
        "budget_credits": budget_credits,
        "retry_reserve_credits": round(retry_reserve, 1),
        "usable_credits": round(usable, 1),
        "scheduled_credits": round(total_scheduled, 1),
        "fast_mode": fast_mode,
        "risk": risk,
        "shots_total": len(enriched),
        "shots_scheduled": len(scheduled),
        "shots_deferred": len(deferred),
        "execution_order": [s["shot_id"] for s in scheduled],
        "shots": scheduled + deferred,
        "status": "planned",
        "created_at": _now_iso(),
    }
    return batch


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
    orch["updated_at"] = _now_iso()
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
        cost = estimate_shot_cost({**shot, "recommended_mode": decision["mode"]}, fast_mode=batch.get("fast_mode", False))
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
        "at": _now_iso(),
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
        shot["retry_plan"] = suggest_retry(shot, failure_reason=failure_reason, quality_score=quality_score, attempts=len(shot["attempts"]))

    today = _today()
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
        "at": _now_iso(),
    })

    orch["updated_at"] = _now_iso()
    save_project_state(state)

    if record_quota:
        record_spend(credits_spent, note=f"nsfw:{shot_id} {batch.get('title', '')}")

    path = save_batch(batch)
    return {"shot": shot, "qa_pass": qa_pass, "saved_to": str(path)}


def generate_daily_report(
    report_date: str | None = None,
    *,
    output_path: Path | None = None,
) -> dict[str, Any]:
    """Build daily NSFW production report with quota vs quality analysis."""
    today = report_date or _today()
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
        recommendations.append("Low pass rate — increase consistency_anchor shots before key_explicit")
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
        "generated_at": _now_iso(),
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