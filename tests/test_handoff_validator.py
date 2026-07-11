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
    combined = result.stdout + result.stderr
    assert "video_pipeline_spec" in combined or "video modes require" in combined


def test_invalid_imagine_agent_mode_enum() -> None:
    result = run_validator({
        "packet_type": "imagine_agent_mode_handoff",
        "protocol_version": "3.7.1",
        "studio_version": "3.7.1",
        "target_surface": "not_a_surface",
        "execution_mode": "image_prompt",
        "subject_id": "shot_001",
        "prompt": "Still",
        "reference_hints": [],
        "model_stack": {"chat": "grok-4.5"},
        "quota_note": "ok",
        "return_path": "record",
        "handoff_steps": ["1. image_gen"],
    })
    assert result.returncode == 1
    assert "target_surface" in (result.stdout + result.stderr)


def test_valid_imagine_agent_mode_image_no_video_fields() -> None:
    """Image modes do not require video_pipeline_spec / sound_layer."""
    result = run_validator({
        "packet_type": "imagine_agent_mode_handoff",
        "protocol_version": "3.7.1",
        "studio_version": "3.7.1",
        "target_surface": "grok_build_tools",
        "execution_mode": "image_prompt",
        "subject_id": "shot_still",
        "prompt": "Hero key art",
        "reference_hints": [],
        "model_stack": {"imagine_image": "grok-imagine-image"},
        "quota_note": "still only",
        "return_path": "plate lock",
        "handoff_steps": ["1. image_gen"],
    })
    assert result.returncode == 0, result.stdout + result.stderr


def test_apply_schema_rules_unit() -> None:
    """Engine is importable and data-driven without special-casing packet types."""
    sys.path.insert(0, str(ROOT / "tools"))
    sys.path.insert(0, str(VALIDATOR.parent))
    # load module by path
    import importlib.util

    spec = importlib.util.spec_from_file_location("validate_handoff", VALIDATOR)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    schema = {
        "required": ("a",),
        "nonempty": ("b",),
        "enums": {"c": frozenset({"x", "y"})},
        "typed": {"d": {"list_min": 1}},
        "when": ({"field": "c", "in": frozenset({"x"}), "nonempty": ("e",)},),
    }
    issues = mod.apply_schema_rules({"a": 1, "b": "ok", "c": "x", "d": ["1"], "e": "yes"}, schema)
    assert issues == []
    issues = mod.apply_schema_rules({"a": 1, "b": "", "c": "z", "d": []}, schema)
    assert any("empty required field: b" in i for i in issues)
    assert any("invalid c" in i for i in issues)
    assert any("d:" in i for i in issues)


if __name__ == "__main__":
    test_valid_sequence_handoff()
    test_invalid_missing_recap()
    test_valid_asset_manifest()
    test_valid_intimacy_state_handoff()
    test_invalid_intimacy_missing_residue()
    test_valid_imagine_agent_mode_handoff()
    test_invalid_imagine_agent_mode_missing_pipeline()
    test_invalid_imagine_agent_mode_enum()
    test_valid_imagine_agent_mode_image_no_video_fields()
    test_apply_schema_rules_unit()
    print("All handoff validator tests passed")