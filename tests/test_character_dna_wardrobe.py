"""Character DNA handoff attaches optional wardrobe section when locked."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from character_dna import build_handoff_packet, create_dna_scaffold, dna_to_markdown  # noqa: E402
from wardrobe_lock import create_wardrobe_lock, lock_wardrobe, sync_clothing_style  # noqa: E402


def test_handoff_omits_wardrobe_when_absent() -> None:
    dna = create_dna_scaffold("Marcus", core_identity="detective", facial_dna="tired hazel eyes")
    packet = build_handoff_packet(dna)
    assert packet["packet_type"] == "identity_lock_handoff"
    assert "wardrobe" not in packet or packet.get("wardrobe") is None


def test_handoff_omits_wardrobe_when_pending() -> None:
    dna = create_dna_scaffold(
        "Marcus",
        core_identity="detective",
        facial_dna="tired hazel eyes",
        clothing_style="placeholder",
    )
    dna["wardrobe_lock"] = create_wardrobe_lock(
        label="Trench",
        silhouette="long coat",
        garments=[
            {
                "id": "coat",
                "name": "brown trench",
                "category": "outerwear",
                "colors": ["brown"],
                "materials": ["twill"],
                "details": "frayed cuffs",
                "layer_index": 1,
            }
        ],
        layer_order=["coat"],
        condition_default="worn",
    )
    assert dna["wardrobe_lock"]["status"] == "pending"
    packet = build_handoff_packet(dna)
    assert "wardrobe" not in packet or packet.get("wardrobe") is None


def test_handoff_includes_wardrobe_when_locked() -> None:
    dna = create_dna_scaffold(
        "Marcus",
        core_identity="detective",
        facial_dna="tired hazel eyes",
        clothing_style="placeholder",
    )
    w = create_wardrobe_lock(
        label="Trench",
        silhouette="long coat",
        garments=[
            {
                "id": "coat",
                "name": "brown trench",
                "category": "outerwear",
                "colors": ["brown"],
                "materials": ["twill"],
                "details": "frayed cuffs",
                "layer_index": 1,
            }
        ],
        layer_order=["coat"],
        condition_default="worn",
    )
    lock_wardrobe(w)
    dna["wardrobe_lock"] = w
    sync_clothing_style(dna)
    packet = build_handoff_packet(dna)
    assert packet["wardrobe"]["status"] == "locked"
    assert "WARDROBE_LOCK" in packet["wardrobe"]["inject"]["compact"]
    assert "trench" in dna["clothing_style"].lower() or "coat" in dna["clothing_style"].lower()


def test_markdown_includes_wardrobe_section_when_present() -> None:
    dna = create_dna_scaffold("Marcus", core_identity="x", facial_dna="y")
    w = create_wardrobe_lock(
        garments=[
            {
                "id": "coat",
                "name": "grey coat",
                "category": "outerwear",
                "colors": ["grey"],
                "materials": [],
                "details": "",
                "layer_index": 0,
            }
        ],
        layer_order=["coat"],
    )
    lock_wardrobe(w)
    dna["wardrobe_lock"] = w
    md = dna_to_markdown(dna)
    assert "Wardrobe Lock" in md
    assert "locked" in md.lower()


def test_markdown_serializes_structured_nsfw_notes() -> None:
    dna = create_dna_scaffold("Mara", core_identity="pi", facial_dna="scar")
    dna["nsfw_notes"] = {
        "mode": "r_rated_intimate_opt_in",
        "forbidden_always": ["minors"],
    }
    md = dna_to_markdown(dna)
    assert "## NSFW Consistency Notes" in md
    assert "r_rated_intimate_opt_in" in md
    assert "minors" in md
    # join-safe: structured notes must not be raw dict repr only
    assert '"mode"' in md


def test_markdown_keeps_string_nsfw_notes() -> None:
    dna = create_dna_scaffold("Mara", core_identity="pi", facial_dna="scar")
    dna["nsfw_notes"] = "clinical note only"
    md = dna_to_markdown(dna)
    assert "## NSFW Consistency Notes" in md
    assert "clinical note only" in md
