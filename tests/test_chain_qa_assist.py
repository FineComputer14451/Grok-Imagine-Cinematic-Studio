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


def test_assist_v2_includes_evidence_block() -> None:
    dna = {
        "character_name": "Liora",
        "slug": "liora",
        "core_identity": "East Asian woman mid-20s",
        "facial_dna": "almond eyes scar left brow",
        "hair_grooming": "black bob",
        "clothing_style": "charcoal coat",
        "key_consistency_anchors": ["scar left brow", "charcoal coat"],
        "reference_image_ids": ["ref_a1"],
        "identity_lock_status": "locked",
    }
    prev = create_clip(
        prompt="Liora charcoal coat black bob scar left brow walks",
        last_frame_recap="Coat wet, bob dripping, scar visible, tracking shot",
        reference_image_id="ref_a1",
    )
    prev["index"] = 0
    prev["momentum_vector"] = {
        "last_action": "walks forward",
        "emotional_state": "tense",
        "camera_velocity": "track",
        "lighting_state": "neon",
        "physics_state": "weighty",
    }
    clip = create_clip(
        prompt="Liora charcoal coat black bob scar left brow continues",
        last_frame_recap="Same coat and bob, scar visible",
        reference_image_id="ref_a1",
    )
    clip["index"] = 1
    clip["momentum_vector"] = dict(prev["momentum_vector"])
    clip["momentum_vector"]["last_action"] = "continues walking"

    assist = assist_sfw_chain_qa(clip, previous_clip=prev, dna=dna)
    assert "evidence" in assist
    assert "identity_drift" in assist["evidence"]
    assert "seam_report" in assist["evidence"]
    assert assist["evidence"]["identity_drift"]["drift_score"] is not None
    assert assist["suggested_scores"]["character_drift_boundary"] == (
        assist["evidence"]["identity_drift"]["suggested_character_drift_boundary"]
    )


def test_assist_v2_without_dna_still_works() -> None:
    clip = create_clip(prompt="Wide shot of city", last_frame_recap="Skyline")
    assist = assist_sfw_chain_qa(clip)
    assert assist["evidence"]["identity_drift"]["pass"] in (True, False)
    assert "suggested_scores" in assist


def test_assist_includes_audio_momentum_evidence() -> None:
    prev = create_clip()
    prev["index"] = 0
    prev["audio_momentum_vector"]["dialogue_state"] = "Hello—"
    prev["audio_momentum_vector"]["sfx_timing"] = "rain"
    clip = create_clip(prompt="Continue", last_frame_recap="Same room")
    clip["index"] = 1
    clip["audio_momentum_vector"]["dialogue_state"] = ""
    assist = assist_sfw_chain_qa(clip, previous_clip=prev)
    assert "audio_momentum" in assist["evidence"]
    assert assist["suggested_scores"]["audio_momentum_sync"] == (
        assist["evidence"]["audio_momentum"]["suggested_audio_momentum_sync"]
    )


if __name__ == "__main__":
    test_assist_prefills_sfw_scores()
    test_apply_assisted_qa_updates_clip()
    test_assist_v2_includes_evidence_block()
    test_assist_v2_without_dna_still_works()
    test_assist_includes_audio_momentum_evidence()
    print("Chain QA assist tests passed")
