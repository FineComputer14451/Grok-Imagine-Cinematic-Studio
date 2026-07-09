"""Tests for sequence memory bank (roadmap #4)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from sequence_memory import (  # noqa: E402
    MEMORY_BANK_VERSION,
    apply_clip_to_memory_bank,
    empty_memory_bank,
    ensure_memory_bank,
    memory_bank_to_prompt_block,
    mirror_bank_to_continuity_state,
)
from sequence_chain import create_clip  # noqa: E402


def test_empty_bank_has_required_keys() -> None:
    bank = empty_memory_bank()
    assert bank["version"] == MEMORY_BANK_VERSION
    for key in ("cast", "environment", "lighting", "emotion", "audio", "notes"):
        assert key in bank
    assert bank["environment"]["props"] == []
    assert bank["cast"] == {}


def test_ensure_fills_missing_on_legacy_dict() -> None:
    partial = {"cast": {"liora": {"name": "Liora"}}}
    bank = ensure_memory_bank(partial)
    assert "environment" in bank
    assert bank["cast"]["liora"]["name"] == "Liora"
    assert bank["version"] == MEMORY_BANK_VERSION


def test_ensure_none_returns_empty() -> None:
    bank = ensure_memory_bank(None)
    assert bank["cast"] == {}


def test_apply_clip_updates_lighting_emotion_audio() -> None:
    bank = empty_memory_bank()
    clip = create_clip(
        prompt="Walk",
        last_frame_recap="Neon alley",
        reference_image_id="ref_a1",
    )
    clip["clip_id"] = "clip_001"
    clip["momentum_vector"]["lighting_state"] = "neon rain"
    clip["momentum_vector"]["emotional_state"] = "tense"
    clip["audio_momentum_vector"]["dialogue_state"] = "whisper mid-line"
    clip["continuity_state"] = {
        "location": "Neon alley",
        "props": ["umbrella", "briefcase"],
        "wardrobe": "charcoal coat",
    }
    out = apply_clip_to_memory_bank(
        bank, clip, character_slug="liora", character_name="Liora"
    )
    assert out["lighting"]["state"] == "neon rain"
    assert out["emotion"]["last_emotional_state"] == "tense"
    assert out["audio"]["dialogue_state"] == "whisper mid-line"
    assert out["environment"]["location"] == "Neon alley"
    assert "umbrella" in out["environment"]["props"]
    assert out["cast"]["liora"]["reference_image_id"] == "ref_a1"
    assert out["cast"]["liora"]["wardrobe"] == "charcoal coat"
    assert out["updated_from_clip_id"] == "clip_001"


def test_apply_does_not_wipe_prior_props() -> None:
    bank = empty_memory_bank()
    bank["environment"]["props"] = ["key"]
    clip = create_clip()
    clip["clip_id"] = "clip_002"
    clip["continuity_state"] = {"props": ["key", "phone"]}
    out = apply_clip_to_memory_bank(bank, clip)
    assert set(out["environment"]["props"]) >= {"key", "phone"}


def test_prompt_block_includes_location_and_cast() -> None:
    bank = empty_memory_bank()
    bank["environment"]["location"] = "Rooftop"
    bank["lighting"]["state"] = "golden hour"
    bank["cast"]["liora"] = {
        "name": "Liora",
        "wardrobe": "coat",
        "emotional_state": "calm",
        "reference_image_id": "ref_1",
        "last_seen_clip_id": "clip_001",
    }
    block = memory_bank_to_prompt_block(bank)
    assert "SEQUENCE_MEMORY_BANK" in block
    assert "Rooftop" in block
    assert "Liora" in block or "liora" in block.lower()


def test_mirror_to_continuity_state() -> None:
    bank = empty_memory_bank()
    bank["environment"]["location"] = "Dock"
    bank["environment"]["props"] = ["crate"]
    bank["lighting"]["state"] = "fog"
    cont = mirror_bank_to_continuity_state(bank)
    assert cont.get("location") == "Dock"
    assert "crate" in (cont.get("props") or [])
