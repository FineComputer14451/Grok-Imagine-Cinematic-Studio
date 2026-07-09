"""Tests for audio momentum integrity (roadmap #6)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from audio_momentum import (  # noqa: E402
    AMV_PASS_THRESHOLD,
    build_audio_momentum_report,
)
from sequence_chain import create_clip  # noqa: E402


def test_threshold_is_7() -> None:
    assert AMV_PASS_THRESHOLD == 7.0


def test_opening_clip_passes() -> None:
    clip = create_clip(prompt="Open")
    clip["index"] = 0
    clip["audio_momentum_vector"]["sfx_timing"] = "soft rain bed"
    report = build_audio_momentum_report(clip, previous_clip=None)
    assert report["pass"] is True
    assert report["integrity_score"] >= 7.0
    assert report["mode"] == "metadata"


def test_dropped_dialogue_fails() -> None:
    prev = create_clip()
    prev["index"] = 0
    prev["clip_id"] = "clip_001"
    prev["audio_momentum_vector"] = {
        "dialogue_state": "mid-sentence: I never said—",
        "sfx_timing": "rain on glass",
        "emotional_tone_audio": "tense whisper",
        "music_cue_points": ["low drone"],
        "lip_sync_state": "mouth open mid-word",
    }
    curr = create_clip()
    curr["index"] = 1
    curr["clip_id"] = "clip_002"
    curr["audio_momentum_vector"] = {
        "dialogue_state": "",
        "sfx_timing": "",
        "emotional_tone_audio": "",
        "music_cue_points": [],
        "lip_sync_state": "",
    }
    report = build_audio_momentum_report(curr, previous_clip=prev)
    assert report["pass"] is False
    assert report["integrity_score"] < 7.0
    assert report["field_status"]["dialogue_state"] == "dropped"
    assert any("dialogue" in f.lower() for f in report["factors"])
    assert report["suggested_audio_momentum_sync"] == report["integrity_score"]


def test_preserved_amv_passes() -> None:
    prev = create_clip()
    prev["index"] = 0
    prev["audio_momentum_vector"] = {
        "dialogue_state": "whisper continues",
        "sfx_timing": "rain continuous",
        "emotional_tone_audio": "intimate low",
        "music_cue_points": ["drone holds"],
        "lip_sync_state": "subtle lip motion",
    }
    curr = create_clip()
    curr["index"] = 1
    curr["audio_momentum_vector"] = {
        "dialogue_state": "whisper continues into next line",
        "sfx_timing": "rain continuous, glass tick",
        "emotional_tone_audio": "intimate low",
        "music_cue_points": ["drone holds"],
        "lip_sync_state": "subtle lip motion",
    }
    report = build_audio_momentum_report(curr, previous_clip=prev)
    assert report["pass"] is True
    assert report["integrity_score"] >= 7.0


def test_music_cues_cleared_penalized() -> None:
    prev = create_clip()
    prev["audio_momentum_vector"]["music_cue_points"] = ["theme swell t=3"]
    prev["audio_momentum_vector"]["dialogue_state"] = "ok"
    curr = create_clip()
    curr["index"] = 1
    curr["audio_momentum_vector"]["dialogue_state"] = "ok"
    curr["audio_momentum_vector"]["music_cue_points"] = []
    report = build_audio_momentum_report(curr, previous_clip=prev)
    assert any("music" in f.lower() for f in report["factors"])
    assert report["field_status"]["music_cue_points"] in ("dropped", "cleared", "empty")


def test_memory_bank_dialogue_mismatch() -> None:
    curr = create_clip()
    curr["index"] = 1
    curr["audio_momentum_vector"]["dialogue_state"] = ""
    prev = create_clip()
    prev["audio_momentum_vector"]["dialogue_state"] = "line"
    bank = {"audio": {"dialogue_state": "important bank line"}}
    report = build_audio_momentum_report(curr, previous_clip=prev, memory_bank=bank)
    assert any("bank" in f.lower() or "dialogue" in f.lower() for f in report["factors"])
