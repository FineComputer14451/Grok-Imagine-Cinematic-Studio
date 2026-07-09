"""sequence_chain integration with memory bank."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from sequence_chain import (  # noqa: E402
    SCHEMA_VERSION,
    build_extend_prompt,
    build_handoff_from_clip,
    create_clip,
    create_sequence_scaffold,
    load_sequence,
    validate_sequence,
)


def test_scaffold_includes_memory_bank() -> None:
    seq = create_sequence_scaffold("Memory Test")
    assert "memory_bank" in seq
    assert "cast" in seq["memory_bank"]
    # New scaffolds may be 1.1; 1.0 still valid for legacy
    assert seq["schema_version"] in ("1.0", "1.1")
    assert SCHEMA_VERSION == "1.1"


def test_validate_accepts_1_0_and_1_1() -> None:
    seq = create_sequence_scaffold("V")
    seq["schema_version"] = "1.0"
    assert validate_sequence(seq) == [] or all(
        "schema" not in i.lower() for i in validate_sequence(seq)
    )
    seq["schema_version"] = "1.1"
    issues = validate_sequence(seq)
    assert not any("schema_version" in i for i in issues)


def test_load_migrates_missing_memory_bank(tmp_path: Path) -> None:
    legacy = create_sequence_scaffold("Legacy")
    legacy.pop("memory_bank", None)
    legacy["schema_version"] = "1.0"
    path = tmp_path / "sequence.json"
    # save without going through ensure if needed — write raw
    path.write_text(json.dumps(legacy))
    loaded = load_sequence(path)
    assert "memory_bank" in loaded
    assert "environment" in loaded["memory_bank"]


def test_handoff_includes_memory_bank_when_provided() -> None:
    clip = create_clip(prompt="x", last_frame_recap="end")
    bank = {
        "cast": {},
        "environment": {
            "location": "Pier",
            "props": [],
            "time_of_day": "",
            "weather": "",
        },
        "lighting": {"state": "dusk", "motifs": []},
        "emotion": {"sequence_temperature": "", "last_emotional_state": ""},
        "audio": {
            "dialogue_state": "",
            "sfx_timing": "",
            "emotional_tone_audio": "",
            "music_cue_points": [],
            "lip_sync_state": "",
        },
        "notes": [],
        "version": "1.0",
    }
    handoff = build_handoff_from_clip(clip, memory_bank=bank)
    assert handoff.get("memory_bank") is not None
    assert handoff["memory_bank"]["environment"]["location"] == "Pier"


def test_extend_prompt_includes_memory_block() -> None:
    seq = create_sequence_scaffold("Ext")
    seq["memory_bank"]["environment"]["location"] = "Train car"
    seq["memory_bank"]["lighting"]["state"] = "flicker fluorescent"
    prev = create_clip(last_frame_recap="Door opens", prompt="Open")
    text = build_extend_prompt(seq, prev, "She steps inside")
    assert "SEQUENCE_MEMORY_BANK" in text
    assert "Train car" in text


def test_extend_prompt_includes_planned_emotional_temperature() -> None:
    seq = create_sequence_scaffold("Temp Ext")
    seq["emotional_temperature_curve"] = [
        {"index": 0, "temp": 2.0},
        {"index": 1, "temp": 7.5, "label": "tense"},
    ]
    prev = create_clip(index=0, last_frame_recap="Still night", prompt="Open")
    text = build_extend_prompt(seq, prev, "Tension rises")
    assert "PLANNED_EMOTIONAL_TEMPERATURE: 7.5/10" in text
