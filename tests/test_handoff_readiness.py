"""Semantic readiness for imagine_agent_mode_handoff packets."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from handoff_readiness import evaluate_imagine_handoff_readiness  # noqa: E402
from handoff_schema import PACKET_TYPE_IMAGINE_AGENT_MODE  # noqa: E402


def _base(**overrides):
    p = {
        "packet_type": PACKET_TYPE_IMAGINE_AGENT_MODE,
        "protocol_version": "3.7.1",
        "studio_version": "3.8.1",
        "target_surface": "grok_build_tools",
        "execution_mode": "image_prompt",
        "subject_id": "shot_001",
        "prompt": "Hero stands in rain, charcoal coat, soft key light",
        "reference_hints": [],
        "model_stack": {"chat": "grok-4.5", "imagine_image": "grok-imagine-image"},
        "quota_note": "Prefer Fast mode; 1 still budgeted",
        "return_path": "sfw record + QA Guardian",
        "handoff_steps": ["1. image_gen", "2. save artifact"],
    }
    p.update(overrides)
    return p


def test_image_prompt_ready_passes() -> None:
    r = evaluate_imagine_handoff_readiness(_base())
    assert r["pass"] is True
    assert r["blockers"] == []


def test_i2v_empty_references_blocks() -> None:
    r = evaluate_imagine_handoff_readiness(
        _base(
            execution_mode="image_to_video",
            prompt="Slow dolly push-in, first frame locked, motion on coat",
            video_pipeline_spec='[VIDEO_PIPELINE_SPEC: model="grok-imagine-video"]',
            sound_layer="ambience rain",
            reference_hints=[],
            return_path="chain QA then sequence record",
            handoff_steps=["1. image_to_video", "2. QA"],
        )
    )
    assert r["pass"] is False
    assert any("reference" in b.lower() for b in r["blockers"])


def test_video_without_motion_cues_blocks() -> None:
    r = evaluate_imagine_handoff_readiness(
        _base(
            execution_mode="video_prompt",
            prompt="A person stands outside",
            video_pipeline_spec='[VIDEO_PIPELINE_SPEC: model="grok-imagine-video"]',
            sound_layer="room tone",
            reference_hints=["plate_1"],
            return_path="run QA Guardian",
            handoff_steps=["1. generate", "2. record"],
        )
    )
    assert r["pass"] is False
    assert any("motion" in b.lower() or "i2v" in b.lower() for b in r["blockers"])


def test_video_with_motion_and_refs_passes() -> None:
    r = evaluate_imagine_handoff_readiness(
        _base(
            execution_mode="image_to_video",
            prompt="Slow dolly on hero, first frame lock, coat motion, lip-sync soft",
            video_pipeline_spec='[VIDEO_PIPELINE_SPEC: model="grok-imagine-video-1.5"]',
            sound_layer="Sound Layer: breath, rain",
            reference_hints=["reference_image_id: plate_001"],
            return_path="sfw record + chain QA",
            handoff_steps=["1. image_to_video", "2. save", "3. QA"],
        )
    )
    assert r["pass"] is True


def test_weak_return_path_blocks() -> None:
    r = evaluate_imagine_handoff_readiness(_base(return_path="done"))
    assert r["pass"] is False
    assert any("return_path" in b.lower() for b in r["blockers"])


def test_placeholder_quota_warns_but_passes() -> None:
    r = evaluate_imagine_handoff_readiness(_base(quota_note="tbd"))
    assert r["pass"] is True
    assert any("quota" in w.lower() for w in r["warnings"])


def test_wrong_packet_type_is_pass_noop() -> None:
    r = evaluate_imagine_handoff_readiness({"packet_type": "sequence_extend_handoff"})
    assert r["pass"] is True
    assert r.get("skipped") is True or not r["blockers"]
