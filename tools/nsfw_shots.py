"""NSFW shot parsing, model routing, and shot scaffold creation."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from models import (
    DEFAULT_IMAGINE_IMAGE_MODEL,
    DEFAULT_IMAGINE_VIDEO_MODEL,
    IMAGINE_IMAGE_MODELS,
    IMAGINE_VIDEO_MODELS,
)

from aspect_presets import apply_aspect_to_shot, default_aspect_for_tier, normalize_aspect, parse_aspect_from_spec
from nsfw_config import NSFW_ASSET_MODEL_MAP, SHOT_TIERS, canonical_explicit_level, canonical_tier
from nsfw_decisions import decide_generation_mode, estimate_shot_cost
from nsfw_util import now_iso


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
        "tier": canonical_tier(tier),
        "motion_complexity": motion,
        "has_reference": has_ref,
        "explicit_level": canonical_explicit_level(explicit),
        "duration_seconds": duration,
        "consistency_required": consistency_required,
    }
    if recommended_mode is not None:
        ctx["recommended_mode"] = recommended_mode
    if description is not None:
        ctx["description"] = description
    return ctx


def parse_inline_shot(spec: str) -> dict[str, Any]:
    """Parse tier:description, tier:motion:description, or aspect:tier:description."""
    aspect_hint, remainder = parse_aspect_from_spec(spec)
    spec = remainder
    parts = spec.split(":", 2)
    if len(parts) == 2:
        tier, desc = parts
        motion = "medium"
    elif len(parts) == 3:
        tier, motion, desc = parts
    else:
        tier, motion, desc = "support", "medium", spec
    shot = {
        "tier": canonical_tier(tier),
        "description": desc.strip(),
        "motion_complexity": motion.strip(),
    }
    aspect = aspect_hint or default_aspect_for_tier(shot["tier"])
    return apply_aspect_to_shot(shot, aspect)


def apply_reference_curator_models(shot: dict[str, Any]) -> dict[str, Any]:
    """Assign image/video model slugs per Reference & Asset Curator NSFW tier map."""
    tier = canonical_tier(shot.get("tier", "support"))
    shot["tier"] = tier
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
    tier = canonical_tier(tier)
    sid = shot_id or f"shot_{tier[:3]}_{datetime.now().strftime('%H%M%S')}"
    shot = {
        "shot_id": sid,
        "tier": tier,
        "description": description,
        "duration_seconds": duration_seconds,
        "has_reference": has_reference,
        "consistency_required": consistency_required,
        "motion_complexity": motion_complexity,
        "explicit_level": canonical_explicit_level(explicit_level),
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
    shot = apply_reference_curator_models(shot)
    if "aspect_ratio" not in shot:
        apply_aspect_to_shot(shot, default_aspect_for_tier(shot.get("tier", "support")))
    return shot


def enrich_shot_for_batch(raw: dict[str, Any], *, fast_mode: bool = False) -> dict[str, Any]:
    """Normalize, decide mode, estimate cost, and apply model routing once."""
    if "shot_id" not in raw:
        return create_shot(
            raw.get("description", "Shot"),
            tier=raw.get("tier", "support"),
            duration_seconds=raw.get("duration_seconds", 10),
            has_reference=raw.get("has_reference", False),
            consistency_required=raw.get("consistency_required", True),
            motion_complexity=raw.get("motion_complexity", "medium"),
            explicit_level=canonical_explicit_level(raw.get("explicit_level", "moderate")),
            image_quality=raw.get("image_quality", False),
        )
    decision = decide_generation_mode(raw)
    cost = estimate_shot_cost({**raw, "recommended_mode": decision["mode"]}, fast_mode=fast_mode)
    raw["recommended_mode"] = decision["mode"]
    raw["estimated_credits"] = cost["credits"]
    shot = apply_reference_curator_models(raw)
    if "aspect_ratio" not in shot:
        apply_aspect_to_shot(shot, default_aspect_for_tier(shot.get("tier", "support")))
    return shot