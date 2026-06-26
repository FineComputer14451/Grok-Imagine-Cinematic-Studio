"""Tests for handoff packet validator script."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = ROOT / ".grok/skills/handoff-packet-validator/scripts/validate_handoff.py"


def run_validator(data: dict) -> subprocess.CompletedProcess[str]:
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        path = f.name
    return subprocess.run(
        [sys.executable, str(VALIDATOR), path],
        capture_output=True,
        text=True,
    )


def test_valid_sequence_handoff() -> None:
    result = run_validator({
        "packet_type": "sequence_extend_handoff",
        "source_clip_id": "clip_001",
        "last_frame_recap": "Wide shot, hero mid-stride",
        "momentum_vector": {"action": "walking", "camera": "dolly in", "emotion": "tense"},
        "audio_momentum_vector": {"dialogue": "none", "sfx": "rain"},
    })
    assert result.returncode == 0, result.stdout + result.stderr


def test_invalid_missing_recap() -> None:
    result = run_validator({
        "packet_type": "sequence_extend_handoff",
        "source_clip_id": "clip_001",
        "last_frame_recap": "",
        "momentum_vector": {"action": "walk", "camera": "static", "emotion": "calm"},
        "audio_momentum_vector": {},
    })
    assert result.returncode == 1


def test_valid_asset_manifest() -> None:
    result = run_validator({
        "packet_type": "asset_manifest_entry",
        "asset_id": "HERO_001",
        "tier": "hero",
        "image_model": "grok-imagine-image-quality",
        "video_model": "grok-imagine-video-1.5",
        "status": "locked",
    })
    assert result.returncode == 0, result.stdout + result.stderr


if __name__ == "__main__":
    test_valid_sequence_handoff()
    test_invalid_missing_recap()
    test_valid_asset_manifest()
    print("All handoff validator tests passed")