"""Plate lock readiness — video modes require approved/locked plate_status."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from plate_readiness import (  # noqa: E402
    PLATE_OK,
    evaluate_plate_lock_readiness,
    normalize_plate_status,
)


def test_normalize_plate_status() -> None:
    assert normalize_plate_status("LOCKED") == "locked"
    assert normalize_plate_status("  Approved ") == "approved"
    assert normalize_plate_status("nope") is None
    assert normalize_plate_status(None) is None


def test_image_prompt_skips_plate() -> None:
    r = evaluate_plate_lock_readiness({}, execution_mode="image_prompt")
    assert r["pass"] is True
    assert r["blockers"] == []
    assert r.get("skipped") is True


def test_i2v_missing_status_blocks() -> None:
    r = evaluate_plate_lock_readiness(
        {"shot_id": "s1", "has_reference": True},
        execution_mode="image_to_video",
    )
    assert r["pass"] is False
    assert any("PL-01" in b for b in r["blockers"])


def test_i2v_draft_blocks() -> None:
    r = evaluate_plate_lock_readiness(
        {"plate_status": "draft"},
        execution_mode="image_to_video",
    )
    assert r["pass"] is False
    assert any("PL-02" in b for b in r["blockers"])


def test_i2v_approved_passes() -> None:
    r = evaluate_plate_lock_readiness(
        {
            "plate_status": "approved",
            "reference_image_id": "plate_001",
        },
        execution_mode="image_to_video",
    )
    assert r["pass"] is True
    assert r["blockers"] == []


def test_i2v_locked_without_path_warns() -> None:
    r = evaluate_plate_lock_readiness(
        {"plate_status": "locked"},
        execution_mode="image_to_video",
    )
    assert r["pass"] is True
    assert any("PL-03" in w for w in r["warnings"])


def test_reference_to_video_requires_plate() -> None:
    r = evaluate_plate_lock_readiness(
        {"plate_status": "draft"},
        execution_mode="reference_to_video",
    )
    assert r["pass"] is False


def test_video_prompt_draft_warns_only() -> None:
    r = evaluate_plate_lock_readiness(
        {"plate_status": "draft"},
        execution_mode="video_prompt",
    )
    assert r["pass"] is True
    assert any("PL-04" in w for w in r["warnings"])


def test_mode_from_subject_recommended_mode() -> None:
    r = evaluate_plate_lock_readiness(
        {"recommended_mode": "image_to_video", "plate_status": "locked", "plate_path": "a.png"},
        execution_mode=None,
    )
    assert r["pass"] is True
    assert "locked" in PLATE_OK


def test_mode_alias_i2v_from_recommended_mode_blocks_draft() -> None:
    """Shorthand recommended_mode=i2v must not skip still→video plate gates."""
    r = evaluate_plate_lock_readiness(
        {"recommended_mode": "i2v", "plate_status": "draft"},
        execution_mode=None,
    )
    assert r["pass"] is False
    assert r.get("execution_mode") == "image_to_video"
    assert any("PL-02" in b for b in r["blockers"])
