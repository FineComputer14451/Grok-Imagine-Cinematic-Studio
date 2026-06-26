"""SFW shot parsing, model routing, and shot scaffold creation."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from models import (
    DEFAULT_IMAGINE_IMAGE_MODEL,
    DEFAULT_IMAGINE_VIDEO_MODEL,
    IMAGINE_IMAGE_MODELS,
    IMAGINE_VIDEO_MODELS,
)

from sfw_config import SFW_ASSET_MODEL_MAP, SHOT_TIERS
from sfw_decisions import decide_generation_mode, estimate_shot_cost
from nsfw_util import now_iso


def build_shot_context(
    shot_id: str,
    *,
    tier: str = "coverage",
    motion: str = "medium",
    has_ref: bool = False,
    duration: float = 10.0,
    consistency_required: bool = True,
    recommended_mode: str | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    ctx: dict[str, Any] = {
        "shot_id": shot_id,
        "tier": tier if tier in SHOT_TIERS else "coverage",
        "motion_complexity": motion,
        "has_reference": has_ref,
        "duration_seconds": duration,
        "consistency_required": consistency_required,
    }
    if recommended_mode is not None:
        ctx["recommended_mode"] = recommended_mode
    if description is not None:
        ctx["description"] = description
    return ctx


def parse_inline_shot(spec: str) -> dict[str, Any]:
    parts = spec.split(":", 2)
    if len(parts) == 2:
        tier, desc = parts
        motion = "medium"
    elif len(parts) == 3:
        tier, motion, desc = parts
    else:
        tier, motion, desc = "coverage", "medium", spec
    return {
        "tier": tier.strip(),
        "description": desc.strip(),
        "motion_complexity": motion.strip(),
    }


def apply_reference_curator_models(shot: dict[str, Any]) -> dict[str, Any]:
    tier = shot.get("tier", "coverage")
    mapping = SFW_ASSET_MODEL_MAP.get(tier, SFW_ASSET_MODEL_MAP["coverage"])
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
    if isinstance(raw, str):
        return parse_inline_shot(raw)
    return dict(raw)


def create_shot(
    description: str,
    *,
    tier: str = "coverage",
    shot_id: str | None = None,
    duration_seconds: float = 10,
    has_reference: bool = False,
    consistency_required: bool = True,
    motion_complexity: str = "medium",
    image_quality: bool = False,
) -> dict[str, Any]:
    if tier not in SHOT_TIERS:
        tier = "coverage"
    sid = shot_id or f"shot_{tier[:3]}_{datetime.now().strftime('%H%M%S')}"
    shot = {
        "shot_id": sid,
        "tier": tier,
        "description": description,
        "duration_seconds": duration_seconds,
        "has_reference": has_reference,
        "consistency_required": consistency_required,
        "motion_complexity": motion_complexity,
        "image_quality": image_quality,
        "status": "pending",
        "attempts": [],
        "quality_score": None,
        "recommended_mode": None,
        "estimated_credits": None,
        "created_at": now_iso(),
    }
    decision = decide_generation_mode(shot)
    cost = estimate_shot_cost({**shot, "recommended_mode": decision["mode"]})
    shot["recommended_mode"] = decision["mode"]
    shot["estimated_credits"] = cost["credits"]
    return apply_reference_curator_models(shot)


def enrich_shot_for_batch(raw: dict[str, Any], *, fast_mode: bool = False) -> dict[str, Any]:
    if "shot_id" not in raw:
        return create_shot(
            raw.get("description", "Shot"),
            tier=raw.get("tier", "coverage"),
            duration_seconds=raw.get("duration_seconds", 10),
            has_reference=raw.get("has_reference", False),
            consistency_required=raw.get("consistency_required", True),
            motion_complexity=raw.get("motion_complexity", "medium"),
            image_quality=raw.get("image_quality", False),
        )
    decision = decide_generation_mode(raw)
    cost = estimate_shot_cost({**raw, "recommended_mode": decision["mode"]}, fast_mode=fast_mode)
    raw["recommended_mode"] = decision["mode"]
    raw["estimated_credits"] = cost["credits"]
    return apply_reference_curator_models(raw)