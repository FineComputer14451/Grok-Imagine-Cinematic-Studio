"""Wave A P1 packet builders + handoff validator registration."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
VALIDATOR = ROOT / ".grok/skills/handoff-packet-validator/scripts/validate_handoff.py"
sys.path.insert(0, str(TOOLS))

from wave_a_packets import (  # noqa: E402
    PACKET_PLATE_MOTION,
    attach_wave_a_to_imagine,
    build_brief_dispatch_log,
    build_contact_brief,
    build_crop_plan,
    build_dialogue_block,
    build_hmu_lock,
    build_plate_motion_readiness,
    build_score_block,
    build_title_brief,
    validate_optional_wave_a_fields,
    wave_a_packet_schemas,
)


def run_validator(data: dict, *extra: str) -> subprocess.CompletedProcess[str]:
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        path = f.name
    return subprocess.run(
        [sys.executable, str(VALIDATOR), path, *extra],
        capture_output=True,
        text=True,
    )


def test_wave_a_schemas_registered() -> None:
    schemas = wave_a_packet_schemas()
    assert len(schemas) == 8
    assert PACKET_PLATE_MOTION in schemas


def test_build_and_validate_plate_motion() -> None:
    pkt = build_plate_motion_readiness(
        subject_id="shot_001",
        plate_status="locked",
        action="coat hem lifts",
        camera="slow dolly in",
        emotion="tense resolve",
    )
    r = run_validator(pkt)
    assert r.returncode == 0, r.stdout + r.stderr


def test_plate_motion_incomplete_motion_fails() -> None:
    pkt = build_plate_motion_readiness(
        subject_id="shot_001",
        plate_status="approved",
        action="walk",
        camera="",
        emotion="calm",
    )
    r = run_validator(pkt)
    assert r.returncode == 1


def test_contact_dialogue_score_hmu_title_crop_brief() -> None:
    packets = [
        build_contact_brief(
            subject_id="s1",
            contact_brief="hand grips wet railing",
            hands="right grip rail",
            cloth="coat sleeve wet",
        ),
        build_hmu_lock(
            character_slug="hero",
            active_look_id="look_a",
            hair="wet strands forehead",
            makeup="smudged mascara lower lid",
            condition="wet",
        ),
        build_dialogue_block(
            subject_id="s1",
            lines=["I stayed."],
            lip_sync_cues="soft jaw open",
        ),
        build_score_block(
            subject_id="s1",
            music_cues=["low strings swell"],
            emotional_tone_audio="melancholy mid",
        ),
        build_title_brief(deliverable_id="main_open", title_cards=[{"text": "RAIN"}]),
        build_crop_plan(subject_id="s1"),
        build_brief_dispatch_log(session_id="sess-1"),
    ]
    for pkt in packets:
        r = run_validator(pkt)
        assert r.returncode == 0, f"{pkt['packet_type']}: {r.stdout}{r.stderr}"


def test_optional_fields_wave_a_owned_only() -> None:
    """Plate/motion are not Wave A-owned — optional validator ignores them."""
    issues, warnings = validate_optional_wave_a_fields(
        {"motion_vector": {"action": "x", "camera": "", "emotion": "y"}}
    )
    assert not issues
    assert not any("motion" in w for w in warnings)

    issues, warnings = validate_optional_wave_a_fields(
        {"hmu_lock": {"hair": "", "makeup": "", "condition": "clean"}}
    )
    assert not issues
    assert any("hair and makeup" in w for w in warnings)

    issues, _ = validate_optional_wave_a_fields(
        {"hmu_lock": {"hair": "wet", "makeup": "smudge", "condition": "not-a-cond"}}
    )
    assert any("condition" in i for i in issues)


def test_strict_wave_a_i2v_requires_plate_and_motion() -> None:
    pkt = {
        "packet_type": "imagine_agent_mode_handoff",
        "protocol_version": "3.8.9",
        "studio_version": "3.8.9",
        "target_surface": "grok_build_tools",
        "execution_mode": "image_to_video",
        "subject_id": "shot_001",
        "prompt": "Slow dolly push-in, first frame lock, coat motion",
        "video_pipeline_spec": '[VIDEO_PIPELINE_SPEC: model="grok-imagine-video"]',
        "sound_layer": "rain ambience",
        "reference_hints": ["plate_001"],
        "model_stack": {"chat": "grok-4.5", "imagine_video": "grok-imagine-video"},
        "quota_note": "1 i2v hero",
        "return_path": "chain QA then sequence record",
        "handoff_steps": ["1. image_to_video", "2. QA"],
        # missing plate_status + motion_vector
    }
    r = run_validator(pkt, "--strict-wave-a")
    assert r.returncode == 1
    out = r.stdout + r.stderr
    assert "plate_status" in out or "strict-wave-a" in out or "motion" in out.lower()


def test_attach_wave_a_lifts_plate_motion() -> None:
    base = {
        "packet_type": "imagine_agent_mode_handoff",
        "protocol_version": "3.8.9",
        "studio_version": "3.8.9",
        "target_surface": "grok_build_tools",
        "execution_mode": "image_to_video",
        "subject_id": "shot_001",
        "prompt": "Slow dolly push-in, first frame lock, coat motion, lip-sync soft",
        "video_pipeline_spec": '[VIDEO_PIPELINE_SPEC: model="grok-imagine-video"]',
        "sound_layer": "rain",
        "reference_hints": ["plate_001"],
        "model_stack": {"chat": "grok-4.5", "imagine_video": "grok-imagine-video"},
        "quota_note": "1 i2v",
        "return_path": "QA Guardian then sfw record",
        "handoff_steps": ["1. generate", "2. record"],
    }
    pm = build_plate_motion_readiness(
        subject_id="shot_001",
        plate_status="locked",
        action="coat lifts",
        camera="dolly in",
        emotion="tense",
        plate_path="artifacts/plates/hero.png",
    )
    out = attach_wave_a_to_imagine(base, plate_motion=pm)
    assert out["plate_status"] == "locked"
    assert out["motion_vector"]["action"] == "coat lifts"
    assert "wave_a" in out
    r = run_validator(out, "--strict-wave-a")
    assert r.returncode == 0, r.stdout + r.stderr


def test_builders_fail_closed_on_enums() -> None:
    with pytest.raises(ValueError, match="plate_status"):
        build_plate_motion_readiness(
            subject_id="s1",
            plate_status="frozen-maybe",
            action="a",
            camera="c",
            emotion="e",
        )
    with pytest.raises(ValueError, match="condition"):
        build_hmu_lock(
            character_slug="hero",
            active_look_id="look_a",
            hair="wet",
            makeup="smudge",
            condition="neon-goo",
        )


def test_attach_rejects_wrong_packet_type() -> None:
    base = {
        "packet_type": "imagine_agent_mode_handoff",
        "subject_id": "shot_001",
        "execution_mode": "image_to_video",
    }
    # Score packet mis-attached as plate_motion
    score = build_score_block(subject_id="shot_001", music_cues=["strings"])
    with pytest.raises(ValueError, match="plate_motion"):
        attach_wave_a_to_imagine(base, plate_motion=score)

    # Contact mis-attached as hmu
    contact = build_contact_brief(
        subject_id="s1", contact_brief="hand on rail"
    )
    with pytest.raises(ValueError, match="hmu"):
        attach_wave_a_to_imagine(base, hmu=contact)

    # Missing packet_type
    with pytest.raises(ValueError, match="packet_type"):
        attach_wave_a_to_imagine(
            base,
            crop={"subject_id": "s1", "crop_plan": [{"aspect": "16:9"}]},
        )
