"""Specialist-order checklist (DNA→Lock→Curator→Prompt→I2V)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from handoff_readiness import evaluate_imagine_handoff_readiness  # noqa: E402
from handoff_schema import PACKET_TYPE_IMAGINE_AGENT_MODE  # noqa: E402
from specialist_order import (  # noqa: E402
    evaluate_specialist_order,
    normalize_specialist_checklist,
    parse_checklist_csv,
    required_specialists,
)


def test_required_specialists_image_vs_video() -> None:
    img = required_specialists("image_prompt")
    assert "i2v" not in img
    assert "dna" in img
    vid = required_specialists("image_to_video")
    assert vid[-1] == "i2v"


def test_parse_checklist_csv() -> None:
    cl = parse_checklist_csv("dna,lock,curator,prompt")
    assert cl["dna"] is True
    assert cl["identity_lock"] is True
    assert cl["reference_curator"] is True
    assert cl["prompt_master"] is True
    assert cl["i2v"] is False


def test_normalize_aliases() -> None:
    cl = normalize_specialist_checklist({"lock": True, "curator": "yes", "i2v": 0})
    assert cl["identity_lock"] is True
    assert cl["reference_curator"] is True
    assert cl["i2v"] is False


def test_missing_checklist_is_soft_warning() -> None:
    r = evaluate_specialist_order(
        {"execution_mode": "image_prompt"},
    )
    assert r["pass"] is True
    assert any("GHR-09" in w for w in r["warnings"])
    assert r["blockers"] == []


def test_incomplete_checklist_blocks() -> None:
    r = evaluate_specialist_order(
        {
            "execution_mode": "image_to_video",
            "specialist_checklist": {
                "dna": True,
                "identity_lock": True,
                "reference_curator": False,
                "prompt_master": True,
                "i2v": True,
            },
        }
    )
    assert r["pass"] is False
    assert any("reference_curator" in b for b in r["blockers"])


def test_complete_video_checklist_passes() -> None:
    r = evaluate_specialist_order(
        {
            "execution_mode": "image_to_video",
            "specialist_checklist": parse_checklist_csv(
                "dna,lock,curator,prompt,i2v"
            ),
        }
    )
    assert r["pass"] is True
    assert r["blockers"] == []


def test_readiness_includes_specialist_blockers() -> None:
    packet = {
        "packet_type": PACKET_TYPE_IMAGINE_AGENT_MODE,
        "protocol_version": "3.7.1",
        "studio_version": "3.8.2",
        "target_surface": "grok_build_tools",
        "execution_mode": "image_prompt",
        "subject_id": "shot_001",
        "prompt": "Hero still",
        "reference_hints": [],
        "model_stack": {"chat": "grok-4.5"},
        "quota_note": "1 still",
        "return_path": "sfw record + QA",
        "handoff_steps": ["1. gen", "2. save"],
        "specialist_checklist": {"dna": True},  # incomplete
    }
    r = evaluate_imagine_handoff_readiness(packet)
    assert r["pass"] is False
    assert any("GHR-10" in b for b in r["blockers"])
