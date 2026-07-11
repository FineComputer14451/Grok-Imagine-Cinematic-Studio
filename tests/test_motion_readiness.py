"""Motion brief readiness — structured MOTION_VECTOR triple."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from motion_readiness import (  # noqa: E402
    extract_motion_vector,
    evaluate_motion_brief_readiness,
    is_complete_motion_triple,
)


def test_image_mode_skips() -> None:
    r = evaluate_motion_brief_readiness({}, execution_mode="image_prompt")
    assert r["pass"] is True
    assert r.get("skipped") is True


def test_complete_triple_passes() -> None:
    r = evaluate_motion_brief_readiness(
        {
            "motion_vector": {
                "action": "coat flutters as she turns",
                "camera": "slow dolly in",
                "emotion": "resolve under pressure",
            },
            "motion_tier": "medium",
        },
        execution_mode="image_to_video",
    )
    assert r["pass"] is True
    assert r["complete_triple"] is True
    assert r["blockers"] == []


def test_free_text_only_soft_pass_with_warning() -> None:
    r = evaluate_motion_brief_readiness(
        {"prompt": "Slow dolly push-in, first frame lock, coat motion"},
        execution_mode="video_prompt",
        strict=False,
    )
    assert r["pass"] is True
    assert any("MB-01" in w for w in r["warnings"])


def test_free_text_only_strict_blocks() -> None:
    r = evaluate_motion_brief_readiness(
        {"prompt": "Slow dolly push-in, first frame lock"},
        execution_mode="image_to_video",
        strict=True,
    )
    assert r["pass"] is False
    assert any("MB-02" in b for b in r["blockers"])


def test_neither_blocks() -> None:
    r = evaluate_motion_brief_readiness(
        {"prompt": "A person stands outside"},
        execution_mode="video_prompt",
        strict=False,
    )
    assert r["pass"] is False
    assert any("MB-03" in b for b in r["blockers"])


def test_partial_triple_with_free_text_soft() -> None:
    r = evaluate_motion_brief_readiness(
        {
            "prompt": "dolly and motion on hair",
            "motion_vector": {"action": "hair moves", "camera": "", "emotion": ""},
        },
        execution_mode="image_to_video",
        strict=False,
    )
    assert r["pass"] is True
    assert any("MB-01" in w for w in r["warnings"])


def test_extract_canonical_block_keys_only() -> None:
    # Sequence momentum aliases must NOT silently map into i2v brief
    mv = extract_motion_vector(
        {
            "i2v_motion_block": {
                "last_action": "walk",
                "camera_velocity": "orbit",
                "emotional_state": "calm",
            }
        }
    )
    assert not is_complete_motion_triple(mv)
    mv2 = extract_motion_vector(
        {
            "motion_vector": {
                "action": "walk",
                "camera": "orbit",
                "emotion": "calm",
            }
        }
    )
    assert is_complete_motion_triple(mv2)
