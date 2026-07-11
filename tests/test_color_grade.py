"""Color grade → polish handoff helpers."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from color_grade import (  # noqa: E402
    apply_color_grade,
    color_grade_is_usable,
    color_grade_summary,
    extract_color_grade,
    normalize_color_grade,
)
from delivery_readiness import evaluate_delivery_pipeline_readiness  # noqa: E402


def test_normalize_string_grade() -> None:
    g = normalize_color_grade("teal shadows, warm skin")
    assert g is not None
    assert g["notes"] == "teal shadows, warm skin"
    assert color_grade_is_usable(g)


def test_legacy_fields() -> None:
    seq = {"grade_notes": "soft roll-off", "lut": "Kodak 2383"}
    g = extract_color_grade(seq)
    assert g is not None
    assert g["lut"] == "Kodak 2383"
    assert color_grade_is_usable(g)


def test_pending_empty_not_usable() -> None:
    g = normalize_color_grade({"status": "pending", "notes": ""})
    assert color_grade_is_usable(g) is False


def test_waived_is_usable() -> None:
    seq: dict = {}
    g = apply_color_grade(seq, waive=True)
    assert g["status"] == "waived"
    assert color_grade_is_usable(g)
    assert seq["color_grade"]["status"] == "waived"


def test_apply_sets_legacy_mirrors() -> None:
    seq: dict = {"slug": "demo", "sequence_name": "Demo", "clips": []}
    apply_color_grade(
        seq,
        notes="cold night",
        lut="TealOrange_Soft",
        emotional_temperature="cool",
        status="approved",
    )
    assert seq["grade_notes"] == "cold night"
    assert seq["lut"] == "TealOrange_Soft"
    assert "LUT=TealOrange_Soft" in color_grade_summary(seq["color_grade"])


def test_polish_readiness_warns_without_grade() -> None:
    seq = {
        "slug": "demo",
        "sequence_name": "Demo",
        "clips": [
            {
                "clip_id": "clip_001",
                "status": "approved",
                "chain_qa": {"decision": "go"},
            }
        ],
    }
    r = evaluate_delivery_pipeline_readiness(seq, stage="polish", approved_only=True)
    assert r["pass"] is True
    assert r["color_grade_usable"] is False
    assert any("CG-01" in w for w in r["warnings"])


def test_require_color_grade_blocks() -> None:
    seq = {
        "slug": "demo",
        "sequence_name": "Demo",
        "clips": [
            {
                "clip_id": "clip_001",
                "status": "approved",
                "chain_qa": {"decision": "go"},
            }
        ],
    }
    r = evaluate_delivery_pipeline_readiness(
        seq, stage="polish", approved_only=True, require_color_grade=True
    )
    assert r["pass"] is False
    assert any("CG-01" in b for b in r["blockers"])


def test_usable_grade_no_cg01_blocker() -> None:
    seq = {
        "slug": "demo",
        "sequence_name": "Demo",
        "clips": [
            {
                "clip_id": "clip_001",
                "status": "approved",
                "chain_qa": {"decision": "go"},
            }
        ],
    }
    apply_color_grade(seq, notes="warm amber", lut="FilmPrint", status="approved")
    r = evaluate_delivery_pipeline_readiness(
        seq, stage="polish", approved_only=True, require_color_grade=True
    )
    assert r["pass"] is True
    assert r["color_grade_usable"] is True
