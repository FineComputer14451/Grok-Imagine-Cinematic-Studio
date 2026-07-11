"""Tests for identity drift scorer (roadmap #1)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from identity_drift import (  # noqa: E402
    DEFAULT_DRIFT_THRESHOLD,
    score_identity_drift,
    report_to_drift_evidence,
    normalize_drift_evidence,
    DRIFT_EVIDENCE_REQUIRED_FIELDS,
)
from sequence_chain import create_clip  # noqa: E402


def _dna(**overrides):
    base = {
        "character_name": "Liora",
        "slug": "liora",
        "core_identity": "East Asian woman, mid-20s, sharp jaw",
        "facial_dna": "almond eyes, high cheekbones, small scar left brow",
        "hair_grooming": "black bob, straight",
        "clothing_style": "long charcoal coat",
        "key_consistency_anchors": ["scar left brow", "charcoal coat", "black bob"],
        "reference_image_ids": ["ref_liora_a1"],
        "identity_lock_status": "locked",
    }
    base.update(overrides)
    return base


def test_default_threshold_is_2_5() -> None:
    assert DEFAULT_DRIFT_THRESHOLD == 2.5


def test_strong_lock_low_drift() -> None:
    dna = _dna()
    clip = create_clip(
        prompt="Liora in charcoal coat, black bob, scar left brow, rain alley",
        reference_image_id="ref_liora_a1",
        last_frame_recap="Coat collar up, bob wet, scar visible, same face",
    )
    clip["momentum_vector"]["emotional_state"] = "tense"
    report = score_identity_drift(clip, dna=dna)
    assert report["drift_score"] < DEFAULT_DRIFT_THRESHOLD
    assert report["pass"] is True
    assert report["mode"] in ("metadata", "hybrid", "frame")
    assert "factors" in report
    assert report["threshold"] == DEFAULT_DRIFT_THRESHOLD


def test_missing_dna_and_thin_prompt_high_drift() -> None:
    clip = create_clip(prompt="person walks", reference_image_id="")
    report = score_identity_drift(clip, dna=None)
    assert report["drift_score"] >= DEFAULT_DRIFT_THRESHOLD
    assert report["pass"] is False
    assert any("dna" in f.lower() or "prompt" in f.lower() for f in report["factors"])


def test_ref_id_mismatch_increases_drift() -> None:
    dna = _dna()
    good = create_clip(
        prompt="Liora charcoal coat black bob scar left brow",
        reference_image_id="ref_liora_a1",
    )
    bad = create_clip(
        prompt="Liora charcoal coat black bob scar left brow",
        reference_image_id="ref_someone_else",
    )
    r_good = score_identity_drift(good, dna=dna)
    r_bad = score_identity_drift(bad, dna=dna)
    assert r_bad["drift_score"] > r_good["drift_score"]


def test_previous_clip_ref_propagation() -> None:
    dna = _dna()
    prev = create_clip(reference_image_id="ref_liora_a1", prompt="Liora coat bob scar")
    prev["index"] = 0
    curr = create_clip(reference_image_id="ref_liora_a1", prompt="Liora coat bob scar continue")
    curr["index"] = 1
    report = score_identity_drift(curr, dna=dna, previous_clip=prev)
    assert report["pass"] is True
    assert "reference" in " ".join(report["factors"]).lower() or report["drift_score"] < 2.5


def test_report_to_drift_evidence_pass() -> None:
    dna = _dna()
    clip = create_clip(
        prompt="Liora charcoal coat black bob scar left brow",
        reference_image_id="ref_liora_a1",
        last_frame_recap="same face coat bob scar",
    )
    clip["clip_id"] = "clip_002"
    report = score_identity_drift(clip, dna=dna)
    evidence = report_to_drift_evidence(
        report,
        character_slug="liora",
        dna_version=1,
        attempt=1,
    )
    assert evidence["status"] == "pass"
    assert evidence["score"] == report["drift_score"]
    assert evidence["threshold"] == DEFAULT_DRIFT_THRESHOLD
    assert evidence["clip_id"] == "clip_002"
    assert evidence["character_slug"] == "liora"
    assert evidence["protocol"] == "IDENTITY_CONTINUITY_PROTOCOL"
    assert evidence["tool"] == "sequence drift-score"
    assert evidence["baseline"]["dna_slug"] == "liora"
    for key in DRIFT_EVIDENCE_REQUIRED_FIELDS:
        assert key in evidence, f"missing {key}"
    assert evidence["baseline"]["dna_slug"]


def test_report_to_drift_evidence_risk() -> None:
    report = {
        "clip_id": "clip_003",
        "drift_score": 4.0,
        "threshold": 2.5,
        "pass": False,
        "mode": "metadata",
        "factors": ["DNA token overlap=10%"],
        "fixes": ["Reinforce DNA anchors in prompt"],
    }
    evidence = report_to_drift_evidence(report, character_slug="liora")
    assert evidence["status"] == "risk"
    assert evidence["score"] == 4.0
    assert "DNA" in evidence["signals"]["summary"] or evidence["signals"]["flags"]


def test_normalize_drift_evidence_object_and_list() -> None:
    one = report_to_drift_evidence(
        {"clip_id": "c1", "drift_score": 1.0, "threshold": 2.5, "pass": True, "factors": []},
        character_slug="a",
    )
    assert len(normalize_drift_evidence(one)) == 1
    assert len(normalize_drift_evidence([one, one])) == 2
    assert normalize_drift_evidence(None) == []
