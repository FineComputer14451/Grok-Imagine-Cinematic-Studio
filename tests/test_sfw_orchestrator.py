"""Tests for SFW batch orchestrator."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from sfw_config import SFW_ASSET_MODEL_MAP, SHOT_TIERS  # noqa: E402
from sfw_decisions import decide_generation_mode  # noqa: E402
from sfw_orchestrator import enrich_shot_for_batch, plan_batch  # noqa: E402
from sfw_shots import apply_reference_curator_models, build_shot_context  # noqa: E402


def test_sfw_shot_tiers() -> None:
    assert "story_beat" in SHOT_TIERS
    assert SHOT_TIERS["hero"]["priority"] < SHOT_TIERS["filler"]["priority"]


def test_sfw_model_routing() -> None:
    shot = build_shot_context("shot_hero_001", tier="hero", has_ref=True, motion="high")
    shot = apply_reference_curator_models(shot)
    assert shot["image_model"] == SFW_ASSET_MODEL_MAP["hero"]["image_model"]
    assert shot["video_model"] == SFW_ASSET_MODEL_MAP["hero"]["video_model"]


def test_sfw_plan_batch_prioritizes_hero() -> None:
    shots = [
        {"tier": "filler", "description": "Mood"},
        {"tier": "hero", "description": "Cover"},
        {"tier": "story_beat", "description": "Beat"},
    ]
    batch = plan_batch("Test Session", shots, budget_credits=500)
    scheduled = [s for s in batch["shots"] if s["status"] == "scheduled"]
    assert scheduled[0]["tier"] == "hero"
    assert batch["shots_scheduled"] >= 2


def test_sfw_decide_i2v_with_ref() -> None:
    shot = build_shot_context("s1", tier="story_beat", has_ref=True, motion="medium")
    decision = decide_generation_mode(shot, risk_level="low")
    assert decision["mode"] == "image_to_video"


if __name__ == "__main__":
    test_sfw_shot_tiers()
    test_sfw_model_routing()
    test_sfw_plan_batch_prioritizes_hero()
    test_sfw_decide_i2v_with_ref()
    print("All SFW orchestrator tests passed")