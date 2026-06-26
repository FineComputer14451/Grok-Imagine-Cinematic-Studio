"""Tests for chain QA assist heuristics."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from chain_qa_assist import apply_assisted_qa, assist_sfw_chain_qa  # noqa: E402
from sequence_chain import create_clip, create_sequence_scaffold, add_clip_to_sequence  # noqa: E402


def test_assist_prefills_sfw_scores() -> None:
    clip = create_clip(
        prompt="Hero walks through rain",
        last_frame_recap="Rain on shoulders, neon reflection in puddle, camera low angle",
        reference_image_id="ref_hero_001",
    )
    clip["momentum_vector"]["last_action"] = "Steps forward"
    clip["momentum_vector"]["emotional_state"] = "Determined"
    assist = assist_sfw_chain_qa(clip)
    assert len(assist["suggested_scores"]) == 10
    assert assist["confidence"] in ("low", "medium", "high")
    assert assist["evaluation"]["weighted_score"] is not None


def test_apply_assisted_qa_updates_clip() -> None:
    seq = create_sequence_scaffold("Assist Test")
    clip = create_clip(
        prompt="Opening",
        last_frame_recap="Wide lake at dawn",
        reference_image_id="ref_1",
    )
    add_clip_to_sequence(seq, clip)
    result = apply_assisted_qa(seq, seq["clips"][0])
    assert result["chain_qa"]["decision"] in ("go", "conditional_go", "no_go")
    assert seq["clips"][0].get("chain_qa_assist")


if __name__ == "__main__":
    test_assist_prefills_sfw_scores()
    test_apply_assisted_qa_updates_clip()
    print("Chain QA assist tests passed")