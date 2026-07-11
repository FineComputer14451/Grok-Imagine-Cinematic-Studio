"""SFW batch orchestrator configuration — tiers, retries, model routing."""

from __future__ import annotations

from typing import Any

from models import DEFAULT_IMAGINE_IMAGE_MODEL, DEFAULT_IMAGINE_VIDEO_MODEL
from quota_optimizer import SUBSCRIPTION_TIERS

SCHEMA_VERSION = "1.0"
STUDIO_AGENT_VERSION = "v3.7.1"

SHOT_TIERS: dict[str, dict[str, Any]] = {
    "hero": {
        "priority": 1,
        "budget_share": 0.30,
        "label": "Hero Frame",
        "description": "Cover shots, primary deliverables, highest visual impact",
    },
    "consistency_anchor": {
        "priority": 2,
        "budget_share": 0.20,
        "label": "Consistency Anchor",
        "description": "Identity lock reference frames — generate before dependent shots",
    },
    "story_beat": {
        "priority": 3,
        "budget_share": 0.30,
        "label": "Story Beat",
        "description": "Narrative-critical story moments and emotional peaks",
    },
    "coverage": {
        "priority": 4,
        "budget_share": 0.15,
        "label": "Coverage",
        "description": "Transitions, establishing frames, emotional B-roll",
    },
    "filler": {
        "priority": 5,
        "budget_share": 0.05,
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
            "Defer filler and coverage tiers",
            "Batch hero + anchor only; resume tomorrow",
        ],
        "max_retries": 0,
        "cost_multiplier": 0.5,
    },
}

QUALITY_THRESHOLD_PASS = 7.0
QUALITY_THRESHOLD_HERO = 8.0

PRO_DAILY_SOFT_CAP = SUBSCRIPTION_TIERS["supergrok_pro"]["daily_soft_cap"]
RETRY_RESERVE_PCT = 0.15

DEFAULT_IMAGE_QUALITY_MODEL = "grok-imagine-image-quality"
DEFAULT_VIDEO_DRAFT_MODEL = "grok-imagine-video"

SFW_ASSET_MODEL_MAP: dict[str, dict[str, Any]] = {
    "hero": {
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
    "story_beat": {
        "asset_tier": "standard",
        "image_model": DEFAULT_IMAGINE_IMAGE_MODEL,
        "video_model": DEFAULT_IMAGINE_VIDEO_MODEL,
        "image_quality": False,
    },
    "coverage": {
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

SHOT_TIER_OPTIONS = tuple(SHOT_TIERS.keys())
MOTION_OPTIONS = ("low", "medium", "high")
RETRY_REASON_OPTIONS = tuple(RETRY_STRATEGIES.keys())