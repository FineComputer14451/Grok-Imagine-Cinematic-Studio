"""Unit tests for evaluate_identity_strict_gate (opt-in CLI hard fail)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from identity_drift import (  # noqa: E402
    DEFAULT_DRIFT_THRESHOLD,
    evaluate_identity_strict_gate,
    report_to_drift_evidence,
)
from sequence_chain import create_clip  # noqa: E402


def test_missing_evidence_fails() -> None:
    clip = create_clip(prompt="no score", last_frame_recap="x")
    clip["clip_id"] = "clip_001"
    result = evaluate_identity_strict_gate(clip=clip)
    assert result["pass"] is False
    assert result["strict"] is True
    assert result["status"] == "missing"
    assert result["reasons"]
    assert result["fixes"]
    assert result["threshold"] == DEFAULT_DRIFT_THRESHOLD


def test_clip_identity_drift_pass() -> None:
    clip = create_clip(prompt="hero locked", last_frame_recap="same")
    clip["clip_id"] = "clip_002"
    clip["identity_drift"] = {
        "clip_id": "clip_002",
        "drift_score": 1.0,
        "threshold": 2.5,
        "pass": True,
        "factors": ["ok"],
        "fixes": [],
    }
    result = evaluate_identity_strict_gate(clip=clip, threshold=2.5)
    assert result["pass"] is True
    assert result["status"] == "pass"
    assert result["score"] == 1.0


def test_clip_identity_drift_risk() -> None:
    clip = create_clip(prompt="drifted", last_frame_recap="x")
    clip["clip_id"] = "clip_003"
    clip["identity_drift"] = {
        "clip_id": "clip_003",
        "drift_score": 4.0,
        "threshold": 2.5,
        "pass": False,
        "factors": ["bad"],
        "fixes": ["Reinforce DNA"],
    }
    result = evaluate_identity_strict_gate(clip=clip)
    assert result["pass"] is False
    assert result["status"] == "risk"
    assert result["reasons"] or result["fixes"]


def test_explicit_drift_evidence_pass() -> None:
    clip = create_clip(prompt="x", last_frame_recap="y")
    clip["clip_id"] = "clip_004"
    evidence = report_to_drift_evidence(
        {
            "clip_id": "clip_004",
            "drift_score": 0.5,
            "threshold": 2.5,
            "pass": True,
            "factors": [],
        },
        character_slug="liora",
    )
    result = evaluate_identity_strict_gate(clip=clip, drift_evidence=evidence)
    assert result["pass"] is True
    assert result["status"] == "pass"


def test_skipped_fails_under_strict() -> None:
    clip = create_clip(prompt="x", last_frame_recap="y")
    clip["clip_id"] = "clip_005"
    evidence = {
        "schema_version": "1.0",
        "protocol": "IDENTITY_CONTINUITY_PROTOCOL",
        "protocol_version": "1.0",
        "clip_id": "clip_005",
        "character_slug": "liora",
        "scored_at": "2026-07-11T00:00:00+00:00",
        "tool": "sequence drift-score",
        "score": 0.0,
        "threshold": 2.5,
        "status": "skipped",
        "skipped_reason": "Director waiver",
        "attempt": 1,
        "baseline": {"dna_slug": "liora", "dna_version": 1},
    }
    result = evaluate_identity_strict_gate(clip=clip, drift_evidence=evidence)
    assert result["pass"] is False
    assert result["status"] == "skipped"


def test_multi_cast_any_risk_fails() -> None:
    clip = create_clip(prompt="x", last_frame_recap="y")
    clip["clip_id"] = "clip_006"
    good = report_to_drift_evidence(
        {
            "clip_id": "clip_006",
            "drift_score": 1.0,
            "threshold": 2.5,
            "pass": True,
            "factors": [],
        },
        character_slug="a",
    )
    bad = report_to_drift_evidence(
        {
            "clip_id": "clip_006",
            "drift_score": 5.0,
            "threshold": 2.5,
            "pass": False,
            "factors": [],
        },
        character_slug="b",
    )
    result = evaluate_identity_strict_gate(clip=clip, drift_evidence=[good, bad])
    assert result["pass"] is False
    assert result["status"] == "risk"


def test_incomplete_status_fails() -> None:
    clip = create_clip(prompt="x", last_frame_recap="y")
    clip["clip_id"] = "clip_007"
    evidence = {
        "schema_version": "1.0",
        "protocol": "IDENTITY_CONTINUITY_PROTOCOL",
        "protocol_version": "1.0",
        "clip_id": "clip_007",
        "character_slug": "liora",
        "scored_at": "2026-07-11T00:00:00+00:00",
        "tool": "sequence drift-score",
        "score": 0.0,
        "threshold": 2.5,
        "status": "incomplete",
        "attempt": 1,
        "baseline": {"dna_slug": "liora", "dna_version": 1},
    }
    result = evaluate_identity_strict_gate(clip=clip, drift_evidence=evidence)
    assert result["pass"] is False
    assert result["status"] == "incomplete"
