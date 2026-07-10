"""Tests for long-form health dashboard (roadmap #10)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from sequence_chain import (  # noqa: E402
    add_clip_to_sequence,
    create_clip,
    create_sequence_scaffold,
    update_sequence_health,
)
from sequence_health_dashboard import (  # noqa: E402
    build_longform_health,
    format_longform_health_markdown,
)


def test_empty_sequence_dashboard() -> None:
    seq = create_sequence_scaffold("Empty Dash")
    report = build_longform_health(seq)
    assert report["clip_count"] == 0
    assert report["chain_qa"]["pending"] == 0
    assert report["slug"] == seq["slug"]


def test_aggregates_drift_seam_regen() -> None:
    seq = create_sequence_scaffold("Health Seq")
    c0 = create_clip(prompt="open", last_frame_recap="wide")
    c0["status"] = "approved"
    c0["chain_qa"] = {"decision": "go", "weighted_score": 8.5}
    c0["identity_drift"] = {"drift_score": 1.0, "pass": True}
    c0["seam_report"] = {"seam_risk": 2.0, "pass": True}
    add_clip_to_sequence(seq, c0)

    c1 = create_clip(prompt="extend", last_frame_recap="close")
    c1["status"] = "qa_hold"
    c1["chain_qa"] = {"decision": "no_go", "weighted_score": 4.0}
    c1["identity_drift"] = {"drift_score": 3.5, "pass": False}
    c1["seam_report"] = {"seam_risk": 6.0, "pass": False}
    c1["regen"] = {"attempts": 1, "max_attempts": 2}
    c1["audio_momentum_report"] = {"integrity_score": 5.0, "pass": False}
    c1["temperature_gate"] = {"severity": "fail", "pass": False}
    c1["continuity_diff"] = {"summary": {"total": 3}}
    add_clip_to_sequence(seq, c1)

    seq["regen_budget"] = {"sequence_attempts_used": 1, "max_attempts_per_clip": 2}
    update_sequence_health(seq)

    report = build_longform_health(seq)
    assert report["clip_count"] == 2
    assert report["chain_qa"]["no_go"] >= 1
    assert report["drift"]["fail_count"] >= 1
    assert report["drift"]["max_score"] == 3.5
    assert report["seam"]["fail_count"] >= 1
    assert report["regen"]["total_attempts"] >= 1
    assert report["audio_momentum"]["fail_count"] >= 1
    assert report["temperature"]["fail_count"] >= 1
    assert report["continuity_diff"]["total_changes"] >= 3
    assert len(report["clip_rows"]) == 2
    assert any("no_go" in a.lower() or "drift" in a.lower() for a in report["alerts"])
    assert report["cost"]["remaining_clips"] >= 1


def test_markdown_includes_title() -> None:
    seq = create_sequence_scaffold("MD Seq")
    md = format_longform_health_markdown(build_longform_health(seq))
    assert "MD Seq" in md or "Health" in md
