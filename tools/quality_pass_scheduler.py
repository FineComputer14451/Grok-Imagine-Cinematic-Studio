#!/usr/bin/env python3
"""
Fast mode → quality pass two-pass scheduler for SFW and NSFW batches.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from models import DEFAULT_IMAGINE_IMAGE_MODEL, DEFAULT_IMAGINE_VIDEO_MODEL, HERO_IMAGINE_IMAGE_MODEL

PASS_1_VIDEO_MODEL = "grok-imagine-video"
PASS_2_VIDEO_MODEL = DEFAULT_IMAGINE_VIDEO_MODEL
PASS_1_IMAGE_MODEL = DEFAULT_IMAGINE_IMAGE_MODEL
PASS_2_IMAGE_MODEL = HERO_IMAGINE_IMAGE_MODEL

QUALITY_PASS_STATUSES = ("pass_1_complete", "quality_pass_pending", "quality_pass_complete")


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def configure_two_pass_shot(shot: dict[str, Any], *, enabled: bool = True) -> dict[str, Any]:
    """Mark shot for two-pass fast → hero workflow."""
    shot["two_pass"] = enabled
    if enabled:
        shot["pass_number"] = 1
        shot["video_model"] = PASS_1_VIDEO_MODEL
        shot["image_model"] = PASS_1_IMAGE_MODEL
        shot["fast_mode"] = True
        shot["quality_pass_status"] = "pass_1_pending"
    return shot


def plan_two_pass_batch(shots: list[dict[str, Any]], *, enabled: bool = True) -> list[dict[str, Any]]:
    return [configure_two_pass_shot(s, enabled=enabled) for s in shots]


def promote_after_qa(
    shot: dict[str, Any],
    *,
    quality_score: float,
    threshold: float = 7.0,
) -> dict[str, Any] | None:
    """
    After pass 1 QA pass, schedule pass 2 hero quality generation.
    Returns promotion plan or None if not eligible.
    """
    if not shot.get("two_pass"):
        return None
    if shot.get("pass_number", 1) != 1:
        return None
    if quality_score < threshold:
        return {
            "action": "hold",
            "reason": f"Score {quality_score} below threshold {threshold} for quality pass",
        }

    plan = {
        "action": "quality_pass",
        "pass_number": 2,
        "status": "quality_pass_pending",
        "video_model": PASS_2_VIDEO_MODEL,
        "image_model": PASS_2_IMAGE_MODEL,
        "recommended_mode": "image_to_video" if shot.get("has_reference") else "video_prompt",
        "fast_mode": False,
        "use_reference_from_pass_1": True,
        "estimated_extra_credits": shot.get("estimated_credits", 10) * 1.8,
        "scheduled_at": _now_iso(),
        "reasons": [
            "Pass 1 QA approved — schedule 1.5 hero quality pass",
            f"Upgrade {PASS_1_VIDEO_MODEL} → {PASS_2_VIDEO_MODEL}",
        ],
    }
    shot["quality_pass_plan"] = plan
    shot["quality_pass_status"] = "quality_pass_pending"
    return plan


def apply_quality_pass_promotion(shot: dict[str, Any]) -> dict[str, Any]:
    """Apply pending quality pass plan to shot for next generation."""
    plan = shot.get("quality_pass_plan")
    if not plan or plan.get("action") != "quality_pass":
        raise ValueError(f"No quality pass plan for {shot.get('shot_id')}")

    shot["pass_number"] = 2
    shot["video_model"] = plan["video_model"]
    shot["image_model"] = plan["image_model"]
    shot["recommended_mode"] = plan["recommended_mode"]
    shot["fast_mode"] = False
    shot["image_quality"] = True
    shot["asset_tier"] = "hero"
    shot["status"] = "scheduled"
    shot["quality_pass_status"] = "pass_2_running"
    return shot


def get_pending_quality_passes(batch: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        s for s in batch.get("shots", [])
        if s.get("quality_pass_status") == "quality_pass_pending"
    ]


def complete_quality_pass(shot: dict[str, Any], *, quality_score: float) -> dict[str, Any]:
    shot["pass_number"] = 2
    shot["quality_pass_status"] = "quality_pass_complete"
    shot["quality_score"] = quality_score
    return shot