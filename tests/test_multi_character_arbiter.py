"""Tests for multi-character identity arbiter (roadmap #8)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from multi_character_arbiter import (  # noqa: E402
    arbitrate_cast,
    build_multi_inject,
)


def _dna(name: str, slug: str, *, locked: bool = True, ref: str = "", anchors: list | None = None):
    return {
        "character_name": name,
        "slug": slug,
        "core_identity": f"{name} core look",
        "facial_dna": f"{name} face signature unique",
        "hair_grooming": f"{name} hair",
        "clothing_style": f"{name} wardrobe",
        "key_consistency_anchors": anchors or [f"{name}-anchor"],
        "reference_image_ids": [ref] if ref else [],
        "identity_lock_status": "locked" if locked else "pending",
        "reference_weights": {"primary_ref_weight": 0.85},
        "version": 1,
        "schema_version": "1.0",
    }


def test_two_char_primary_first() -> None:
    plan = arbitrate_cast(
        [_dna("Liora", "liora", ref="ref_l"), _dna("Detective", "the-detective", ref="ref_d")],
        primary_slug="liora",
    )
    assert plan["pass"] is True
    assert plan["primary_slug"] == "liora"
    assert plan["cast"][0]["role"] == "primary"
    assert plan["cast"][0]["ref_weight"] >= plan["cast"][1]["ref_weight"]
    assert "MULTI_CHARACTER_LOCK" in plan["inject_block"]
    assert plan["inject_block"].index("Liora") < plan["inject_block"].index("Detective") or "Primary" in plan["inject_block"]


def test_missing_dna_error() -> None:
    plan = arbitrate_cast(
        [_dna("Liora", "liora")],
        primary_slug="the-detective",
    )
    assert plan["pass"] is False
    assert any(c["code"] == "no_primary" for c in plan["conflicts"])


def test_shared_ref_warns() -> None:
    plan = arbitrate_cast(
        [
            _dna("A", "a", ref="same_ref"),
            _dna("B", "b", ref="same_ref"),
        ],
        primary_slug="a",
    )
    assert any(c["code"] == "shared_ref_id" for c in plan["conflicts"])


def test_unlocked_warns() -> None:
    plan = arbitrate_cast(
        [_dna("A", "a", locked=False), _dna("B", "b", locked=True)],
        primary_slug="b",
    )
    assert any(c["code"] == "not_locked" for c in plan["conflicts"])
    assert plan["pass"] is True  # warn only


def test_single_cast_info() -> None:
    plan = arbitrate_cast([_dna("Solo", "solo")], primary_slug="solo")
    assert plan["pass"] is True
    assert any(c["code"] == "single_cast" for c in plan["conflicts"])


def test_build_multi_inject_contains_anti_merge() -> None:
    dnas = [_dna("Liora", "liora"), _dna("Detective", "the-detective")]
    plan = arbitrate_cast(dnas, primary_slug="liora")
    text = plan["inject_block"]
    assert "Anti-merge" in text or "anti-merge" in text.lower() or "blend" in text.lower()


def test_empty_cast_error() -> None:
    plan = arbitrate_cast([])
    assert plan["pass"] is False
    assert any(c["code"] == "empty_cast" for c in plan["conflicts"])


def test_explicit_weights_sum_warn() -> None:
    plan = arbitrate_cast(
        [_dna("A", "a"), _dna("B", "b")],
        primary_slug="a",
        weights={"a": 0.5, "b": 0.2},
    )
    assert any(c["code"] == "weight_sum" for c in plan["conflicts"])
    assert plan["pass"] is True


def test_default_primary_is_first_dna() -> None:
    plan = arbitrate_cast(
        [_dna("First", "first"), _dna("Second", "second")],
    )
    assert plan["primary_slug"] == "first"
    assert plan["cast"][0]["slug"] == "first"


def test_three_char_primary_weight() -> None:
    plan = arbitrate_cast(
        [_dna("A", "a"), _dna("B", "b"), _dna("C", "c")],
        primary_slug="a",
    )
    assert plan["cast"][0]["ref_weight"] == 0.70
    secondaries = [c for c in plan["cast"] if c["role"] == "secondary"]
    assert len(secondaries) == 2
    total = sum(c["ref_weight"] for c in plan["cast"])
    assert abs(total - 1.0) < 0.02


def test_build_multi_inject_standalone() -> None:
    dnas = [_dna("Liora", "liora"), _dna("Detective", "the-detective")]
    plan = arbitrate_cast(dnas, primary_slug="liora")
    text = build_multi_inject(plan["cast"], plan["primary_slug"])
    assert "MULTI_CHARACTER_LOCK" in text
    assert "blend" in text.lower() or "Anti-merge" in text
