"""Tests for NSFW Reference Curator model routing."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from nsfw_decisions import decide_generation_mode  # noqa: E402
from nsfw_orchestrator import (  # noqa: E402
    NSFW_ASSET_MODEL_MAP,
    RETRY_REASON_OPTIONS,
    SHOT_TIER_OPTIONS,
    apply_reference_curator_models,
    build_shot_context,
    create_shot,
    enrich_shot_for_batch,
    parse_inline_shot,
    plan_batch,
)


def test_hero_tier_routes_image_quality() -> None:
    shot = apply_reference_curator_models({"tier": "hero", "description": "Cover"})
    assert shot["asset_tier"] == "hero"
    assert shot["image_model"] == "grok-imagine-image-quality"
    assert shot["video_model"] == "grok-imagine-video-1.5"
    assert shot["image_quality"] is True


def test_key_explicit_matches_hero_routing() -> None:
    shot = apply_reference_curator_models({"tier": "key_explicit", "description": "Beat"})
    mapping = NSFW_ASSET_MODEL_MAP["key_explicit"]
    assert shot["image_model"] == mapping["image_model"]
    assert shot["video_model"] == mapping["video_model"]


def test_filler_uses_draft_video() -> None:
    shot = apply_reference_curator_models({"tier": "filler", "description": "Mood"})
    assert shot["asset_tier"] == "draft"
    assert shot["video_model"] == "grok-imagine-video"
    assert shot["image_quality"] is False


def test_parse_inline_shot_three_part() -> None:
    parsed = parse_inline_shot("key_explicit:high:Primary beat")
    assert parsed["tier"] == "key_explicit"
    assert parsed["motion_complexity"] == "high"
    assert parsed["description"] == "Primary beat"


def test_create_shot_includes_models() -> None:
    shot = create_shot("Anchor close-up", tier="consistency_anchor")
    assert shot["image_model"] == "grok-imagine-image-quality"
    assert shot["asset_tier"] == "hero"


def test_build_shot_context_canonical_fields() -> None:
    shot = build_shot_context(
        "shot_001",
        tier="key_explicit",
        motion="high",
        has_ref=True,
        explicit="explicit",
        duration=12.0,
    )
    assert shot["shot_id"] == "shot_001"
    assert shot["tier"] == "key_explicit"
    assert shot["motion_complexity"] == "high"
    assert shot["has_reference"] is True
    assert shot["consistency_required"] is True


def test_shot_tier_options_follow_priority() -> None:
    assert SHOT_TIER_OPTIONS[0] == "hero"
    assert "filler" in SHOT_TIER_OPTIONS
    assert "identity_drift" in RETRY_REASON_OPTIONS


def test_decide_generation_mode_anchor_without_ref() -> None:
    shot = build_shot_context("shot_001", tier="consistency_anchor", has_ref=False)
    decision = decide_generation_mode(shot)
    assert decision["mode"] == "image_prompt"
    assert decision["confidence"] >= 0.9


def test_decide_generation_mode_i2v_with_ref_and_motion() -> None:
    shot = build_shot_context("shot_002", tier="key_explicit", motion="high", has_ref=True)
    decision = decide_generation_mode(shot)
    assert decision["mode"] == "image_to_video"


def test_decide_budget_override() -> None:
    shot = build_shot_context("shot_003", tier="key_explicit", motion="high", has_ref=True)
    decision = decide_generation_mode(shot, budget_remaining=50)
    assert decision["mode"] == "image_prompt"
    assert any("Budget remaining" in r for r in decision["reasons"])


def test_enrich_shot_for_batch_single_routing_pass() -> None:
    shot = enrich_shot_for_batch({"tier": "hero", "description": "Cover"})
    assert shot["image_model"] == "grok-imagine-image-quality"
    assert shot["recommended_mode"]
    assert shot["estimated_credits"]


def test_plan_batch_applies_routing() -> None:
    batch = plan_batch(
        "Test Session",
        ["hero:Cover", "filler:Atmosphere"],
        budget_credits=5000,
    )
    scheduled = {s["tier"]: s for s in batch["shots"] if s["status"] == "scheduled"}
    assert scheduled["hero"]["image_model"] == "grok-imagine-image-quality"
    assert scheduled["filler"]["video_model"] == "grok-imagine-video"


if __name__ == "__main__":
    test_hero_tier_routes_image_quality()
    test_key_explicit_matches_hero_routing()
    test_filler_uses_draft_video()
    test_parse_inline_shot_three_part()
    test_create_shot_includes_models()
    test_build_shot_context_canonical_fields()
    test_shot_tier_options_follow_priority()
    test_decide_generation_mode_anchor_without_ref()
    test_decide_generation_mode_i2v_with_ref_and_motion()
    test_decide_budget_override()
    test_enrich_shot_for_batch_single_routing_pass()
    test_plan_batch_applies_routing()
    print("All NSFW asset model tests passed")