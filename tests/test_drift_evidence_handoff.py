"""drift_evidence on sequence_extend_handoff (identity continuity wiring)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from identity_drift import report_to_drift_evidence  # noqa: E402
from sequence_chain import build_handoff_from_clip, create_clip  # noqa: E402


def test_handoff_includes_drift_evidence_from_clip() -> None:
    clip = create_clip(prompt="hero locked face coat", last_frame_recap="same face")
    clip["clip_id"] = "clip_001"
    clip["identity_drift"] = {
        "clip_id": "clip_001",
        "drift_score": 1.2,
        "threshold": 2.5,
        "pass": True,
        "factors": ["All anchors present"],
        "fixes": [],
    }
    handoff = build_handoff_from_clip(
        clip,
        character_slug="liora",
    )
    assert handoff["packet_type"] == "sequence_extend_handoff"
    assert "drift_evidence" in handoff
    ev = handoff["drift_evidence"]
    assert isinstance(ev, dict)
    assert ev["status"] == "pass"
    assert ev["score"] == 1.2
    assert ev["character_slug"] == "liora"
    assert any(
        "drift" in str(x).lower() for x in (handoff.get("extend_instructions") or [])
    )


def test_handoff_omits_drift_evidence_when_not_scored() -> None:
    clip = create_clip(prompt="unscored", last_frame_recap="recap")
    clip["clip_id"] = "clip_002"
    handoff = build_handoff_from_clip(clip)
    assert "drift_evidence" not in handoff or handoff.get("drift_evidence") is None
