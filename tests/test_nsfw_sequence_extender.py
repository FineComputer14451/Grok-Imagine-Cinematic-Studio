"""Tests for NSFW sequence extender module split."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from nsfw_chain_qa import evaluate_nsfw_chain_qa  # noqa: E402
from nsfw_extension_config import TENSION_PROFILES  # noqa: E402
from nsfw_sequence_extender import (  # noqa: E402
    build_erotic_beat_sheet,
    plan_nsfw_extension,
    run_nsfw_chain_qa_scaffold,
)


def test_tension_profiles_available() -> None:
    assert "passionate" in TENSION_PROFILES
    assert "slow_burn" in TENSION_PROFILES


def test_plan_nsfw_extension_builds_clips() -> None:
    seq = plan_nsfw_extension("Module Split Test", target_duration=60)
    assert len(seq["clips"]) >= 3
    assert seq["prompt_chain"]
    assert seq["cost_estimate"]


def test_beat_sheet_timing() -> None:
    beats = build_erotic_beat_sheet(target_duration=90, tension_profile="intense")
    assert beats[-1]["t_end"] > beats[0]["t_start"]


def test_chain_qa_go_decision() -> None:
    clip = {"clip_id": "clip_001"}
    scaffold = run_nsfw_chain_qa_scaffold(clip)
    assert scaffold["decision"] == "awaiting_scores"
    from nsfw_extension_config import NSFW_CHAIN_QA_CHECKS

    scores = {key: 8.0 for key, _, _ in NSFW_CHAIN_QA_CHECKS}
    result = evaluate_nsfw_chain_qa(clip, scores)
    assert result["decision"] == "go"


if __name__ == "__main__":
    test_tension_profiles_available()
    test_plan_nsfw_extension_builds_clips()
    test_beat_sheet_timing()
    test_chain_qa_go_decision()
    print("All NSFW sequence extender tests passed")