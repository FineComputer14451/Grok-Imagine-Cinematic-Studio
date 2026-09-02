"""NSFW generation mode decisions, cost estimates, and retry strategies."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

ModeRule = tuple[Callable[[dict[str, Any], str], bool], str, str, float]

from models import (
    DEFAULT_IMAGINE_IMAGE_MODEL,
    DEFAULT_IMAGINE_VIDEO_MODEL,
    HERO_IMAGINE_IMAGE_MODEL,
    usd_to_credits,
)
from quota_optimizer import estimate_clip_cost, load_pricing_config
from quota_sync import get_burn_rate_risk

from nsfw_config import (
    QUALITY_THRESHOLD_HERO,
    QUALITY_THRESHOLD_PASS,
    RETRY_STRATEGIES,
    canonical_tier,
)


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
            q_slug = HERO_IMAGINE_IMAGE_MODEL
            usd = img_rates.get(q_slug, {}).get("usd_per_image", 0.04)
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


def _tier(shot: dict[str, Any]) -> str:
    return canonical_tier(shot.get("tier", "support"))


def _has_ref(shot: dict[str, Any]) -> bool:
    return bool(shot.get("has_reference", False))


def _motion(shot: dict[str, Any]) -> str:
    return shot.get("motion_complexity", "medium")


GENERATION_MODE_RULES: tuple[ModeRule, ...] = (
    (
        lambda s, r: r in ("high", "critical") and _tier(s) not in ("hero", "consistency_anchor"),
        "image_prompt",
        "Quota pressure — explore with still before video spend",
        0.9,
    ),
    (
        lambda s, _: _tier(s) == "consistency_anchor" and not _has_ref(s),
        "image_prompt",
        "Anchor frame must be locked as still before dependent video",
        0.95,
    ),
    (
        lambda s, _: _has_ref(s) and _motion(s) in ("medium", "high"),
        "image_to_video",
        "Approved reference + motion intent — i2v preserves identity",
        0.92,
    ),
    (
        lambda s, _: _tier(s) in ("hero", "key_intimate") and _has_ref(s),
        "image_to_video",
        "High-impact shot with reference — i2v for fidelity",
        0.88,
    ),
    (
        lambda s, _: _motion(s) == "low" and s.get("explicit_level", "moderate") in ("suggestive", "moderate"),
        "image_prompt",
        "Low motion intimate still — image is quota-efficient",
        0.85,
    ),
    (
        lambda s, _: _motion(s) == "high" and not _has_ref(s),
        "image_prompt",
        "High motion without anchor — generate still first, then i2v",
        0.8,
    ),
    (
        lambda s, _: s.get("duration_seconds", 10) >= 10 and s.get("consistency_required", True) and _has_ref(s),
        "image_to_video",
        "Long consistent clip — extend from locked still",
        0.87,
    ),
    (
        lambda s, _: _tier(s) == "filler",
        "image_prompt",
        "Filler tier — still exploration unless budget surplus",
        0.75,
    ),
)


def decide_generation_mode(
    shot: dict[str, Any],
    *,
    budget_remaining: float | None = None,
    risk_level: str | None = None,
) -> dict[str, Any]:
    """Recommend image_prompt vs image_to_video vs video_prompt via priority rule table."""
    if risk_level is None:
        risk_level = get_burn_rate_risk()
    reasons: list[str] = []
    mode = "video_prompt"
    confidence = 0.65

    for predicate, rule_mode, reason, rule_confidence in GENERATION_MODE_RULES:
        if predicate(shot, risk_level):
            mode = rule_mode
            reasons.append(reason)
            confidence = rule_confidence
            break
    else:
        reasons.append("No reference; direct video prompt for atmospheric motion")

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