"""Tests for nested wardrobe_lock helpers (Costume & Wardrobe Continuity P1)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from wardrobe_lock import (  # noqa: E402
    build_clip_wardrobe_state,
    build_wardrobe_handoff_section,
    build_wardrobe_inject,
    clothing_style_summary,
    create_wardrobe_lock,
    lock_wardrobe,
    set_active_look,
    sync_clothing_style,
    validate_wardrobe_lock,
)


def test_create_wardrobe_lock_defaults() -> None:
    w = create_wardrobe_lock(
        label="Hero trench",
        silhouette="long overcoat",
        garments=[
            {
                "id": "coat",
                "name": "brown trench",
                "category": "outerwear",
                "colors": ["brown"],
                "materials": ["cotton twill"],
                "details": "frayed cuffs",
                "layer_index": 2,
            }
        ],
        accessories=[{"id": "ring", "name": "silver ring", "hand": "left", "details": ""}],
        layer_order=["shirt", "coat"],
        condition_default="worn",
        inject_anchors=["frayed cuffs", "silver ring"],
    )
    assert w["schema_version"] == "1.0"
    assert w["status"] == "pending"
    assert w["active_look_id"] == "look_default"
    assert len(w["looks"]) == 1
    assert w["looks"][0]["garments"][0]["name"] == "brown trench"
    assert validate_wardrobe_lock(w) == []


def test_validate_rejects_bad_condition_and_status() -> None:
    w = create_wardrobe_lock()
    w["status"] = "nope"
    w["looks"][0]["condition_default"] = "filthy"
    issues = validate_wardrobe_lock(w)
    assert any("status" in i for i in issues)
    assert any("condition" in i for i in issues)


def test_validate_active_look_must_exist() -> None:
    w = create_wardrobe_lock()
    w["active_look_id"] = "missing"
    issues = validate_wardrobe_lock(w)
    assert any("active_look" in i.lower() or "active_look_id" in i for i in issues)


def test_lock_and_summary_and_inject() -> None:
    w = create_wardrobe_lock(
        label="Hero trench",
        silhouette="long overcoat",
        garments=[
            {
                "id": "coat",
                "name": "brown trench",
                "category": "outerwear",
                "colors": ["brown"],
                "materials": ["twill"],
                "details": "water stains",
                "layer_index": 1,
            }
        ],
        layer_order=["coat"],
        condition_default="worn",
        inject_anchors=["water stains"],
    )
    lock_wardrobe(w)
    assert w["status"] == "locked"
    assert w.get("locked_at")
    summary = clothing_style_summary(w)
    assert "trench" in summary.lower() or "overcoat" in summary.lower()
    inject = build_wardrobe_inject(w, slug="marcus")
    assert inject["compact"].startswith("[WARDROBE_LOCK:marcus:look_default]")
    assert "trench" in inject["full"].lower() or "coat" in inject["full"].lower()
    assert inject["video"]  # non-empty fabric/motion cue line


def test_handoff_section_only_when_locked() -> None:
    w = create_wardrobe_lock(
        garments=[{"id": "coat", "name": "coat", "category": "outerwear", "colors": ["grey"], "materials": [], "details": "", "layer_index": 0}],
        layer_order=["coat"],
    )
    assert build_wardrobe_handoff_section(w, slug="marcus") is None
    lock_wardrobe(w)
    section = build_wardrobe_handoff_section(w, slug="marcus", condition="wet")
    assert section is not None
    assert section["status"] == "locked"
    assert section["active_look_id"] == "look_default"
    assert "compact" in section["inject"]
    assert section["condition"] == "wet"


def test_clip_wardrobe_state() -> None:
    state = build_clip_wardrobe_state(
        character_slug="marcus",
        look_id="look_default",
        condition="wet",
        delta="coat darker from rain",
        layer_order=["shirt", "coat"],
        updated_from_clip="02",
    )
    assert state["condition"] == "wet"
    assert state["delta"] == "coat darker from rain"
    assert state["updated_from_clip"] == "02"


def test_clip_state_rejects_bad_condition() -> None:
    try:
        build_clip_wardrobe_state(
            character_slug="marcus",
            look_id="look_default",
            condition="soaked",
        )
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "condition" in str(exc).lower()


def test_set_active_look() -> None:
    w = create_wardrobe_lock(look_id="look_a", label="A")
    w["looks"].append(
        {
            "look_id": "look_b",
            "label": "B",
            "silhouette": "",
            "garments": [],
            "accessories": [],
            "layer_order_bottom_to_top": [],
            "condition_default": "clean",
            "inject_anchors": [],
        }
    )
    set_active_look(w, "look_b")
    assert w["active_look_id"] == "look_b"
    try:
        set_active_look(w, "look_z")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


def test_sync_clothing_style_when_locked() -> None:
    dna = {
        "character_name": "Marcus",
        "slug": "marcus",
        "clothing_style": "old wrong text",
        "wardrobe_lock": create_wardrobe_lock(
            label="Night coat",
            silhouette="long coat",
            garments=[
                {
                    "id": "coat",
                    "name": "black coat",
                    "category": "outerwear",
                    "colors": ["black"],
                    "materials": ["wool"],
                    "details": "",
                    "layer_index": 0,
                }
            ],
            layer_order=["coat"],
        ),
    }
    # pending: do not overwrite unless we choose to — design: sync when locked
    before = dna["clothing_style"]
    sync_clothing_style(dna)
    assert dna["clothing_style"] == before  # still pending
    lock_wardrobe(dna["wardrobe_lock"])
    sync_clothing_style(dna)
    assert "coat" in dna["clothing_style"].lower() or "night" in dna["clothing_style"].lower()
