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


def test_valid_intimacy_state_handoff() -> None:
    result = run_validator({
        "packet_type": "intimacy_state_handoff",
        "source_clip_id": "clip_001",
        "intimacy_physics_state": {"weight_transfer": "balanced", "skin_response": "natural"},
        "post_scene_state": {"clothing": "partially displaced", "position": "embrace"},
        "clothing_displacement_log": ["strap slipped left shoulder"],
        "emotional_residue": "tender vulnerability, slowed breath",
    })
    assert result.returncode == 0, result.stdout + result.stderr


def test_invalid_intimacy_missing_residue() -> None:
    result = run_validator({
        "packet_type": "intimacy_state_handoff",
        "source_clip_id": "clip_001",
        "intimacy_physics_state": {},
        "post_scene_state": {},
        "clothing_displacement_log": [],
        "emotional_residue": "",
    })
    assert result.returncode == 1


def test_valid_imagine_agent_mode_handoff() -> None:
    result = run_validator({
        "packet_type": "imagine_agent_mode_handoff",
        "protocol_version": "3.7.1",
        "studio_version": "3.7.1",
        "target_surface": "grok_build_tools",
        "execution_mode": "image_to_video",
        "subject_id": "shot_hero_001",
        "prompt": "Slow dolly on rain-soaked alley",
        "video_pipeline_spec": '[VIDEO_PIPELINE_SPEC: model="grok-imagine-video-1.5"]',
        "sound_layer": "Sound Layer: ambience rain, music cue soft",
        "reference_hints": ["reference_image_id: plate_001"],
        "model_stack": {
            "chat": "grok-4.5",
            "build": "grok-4.5",
            "imagine_image": "grok-imagine-image",
            "imagine_video": "grok-imagine-video-1.5",
        },
        "quota_note": "Prefer Fast mode; ~10s video budget reserved",
        "return_path": "sfw record + QA Guardian",
        "handoff_steps": ["1. Call image_to_video", "2. Save artifacts/"],
    })
    assert result.returncode == 0, result.stdout + result.stderr


def test_invalid_imagine_agent_mode_missing_pipeline() -> None:
    result = run_validator({
        "packet_type": "imagine_agent_mode_handoff",
        "protocol_version": "3.7.1",
        "studio_version": "3.7.1",
        "target_surface": "grok_build_tools",
        "execution_mode": "video_prompt",
        "subject_id": "shot_001",
        "prompt": "Wide establishing",
        "video_pipeline_spec": "",
        "sound_layer": "",
        "reference_hints": [],
        "model_stack": {"imagine_video": "grok-imagine-video"},
        "quota_note": "ok",
        "return_path": "record",
        "handoff_steps": ["1. generate"],
    })
    assert result.returncode == 1


if __name__ == "__main__":
    test_valid_sequence_handoff()
    test_invalid_missing_recap()
    test_valid_asset_manifest()
    test_valid_intimacy_state_handoff()
    test_invalid_intimacy_missing_residue()
    test_valid_imagine_agent_mode_handoff()
    test_invalid_imagine_agent_mode_missing_pipeline()
    print("All handoff validator tests passed")