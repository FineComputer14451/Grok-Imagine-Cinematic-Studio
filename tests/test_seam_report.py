"""Tests for last-frame seam report (roadmap #2)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from seam_report import build_seam_report  # noqa: E402
from sequence_chain import create_clip  # noqa: E402


def test_opening_clip_low_seam_risk() -> None:
    clip = create_clip(prompt="Wide establishing", last_frame_recap="Skyline dusk")
    clip["index"] = 0
    report = build_seam_report(clip, previous_clip=None)
    assert report["seam_risk"] <= 4.0
    assert report["mode"] == "metadata"
    assert "suggested_scores" in report


def test_extend_missing_prev_recap_high_risk() -> None:
    prev = create_clip(prompt="Prev", last_frame_recap="")
    prev["index"] = 0
    curr = create_clip(prompt="Next", last_frame_recap="something")
    curr["index"] = 1
    report = build_seam_report(curr, previous_clip=prev)
    assert report["seam_risk"] >= 5.0
    assert report["pass"] is False or any("recap" in f.lower() for f in report["factors"])


def test_aligned_momentum_reduces_risk() -> None:
    prev = create_clip(
        prompt="Run",
        last_frame_recap="Hero mid-stride left to right, neon rain, camera tracking",
    )
    prev["index"] = 0
    prev["momentum_vector"] = {
        "last_action": "mid-stride run",
        "emotional_state": "urgent",
        "camera_velocity": "tracking right",
        "lighting_state": "neon rain",
        "physics_state": "weighty forward",
    }
    curr = create_clip(
        prompt="Continue run",
        last_frame_recap="Same alley, still tracking, rain continuous",
    )
    curr["index"] = 1
    curr["momentum_vector"] = {
        "last_action": "continues mid-stride run",
        "emotional_state": "urgent",
        "camera_velocity": "tracking right",
        "lighting_state": "neon rain",
        "physics_state": "weighty forward",
    }
    curr["transition_to_next"] = "invisible_edit"
    report = build_seam_report(curr, previous_clip=prev)
    assert report["seam_risk"] < 5.0
    assert report["suggested_scores"]["last_frame_continuity"] >= 7.0


def test_report_includes_fixes_list() -> None:
    prev = create_clip(last_frame_recap="")
    prev["index"] = 0
    curr = create_clip(prompt="Next beat")
    curr["index"] = 1
    report = build_seam_report(curr, previous_clip=prev)
    assert isinstance(report["fixes"], list)
