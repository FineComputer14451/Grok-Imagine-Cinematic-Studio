"""Tests for stitch artifact lexicon (roadmap #11)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from stitch_artifact_lexicon import (  # noqa: E402
    DEFAULT_PACK_IDS,
    build_negative_pack,
    build_positive_guards,
    format_lexicon_markdown,
    get_entry,
    list_entries,
    suggest_entries_from_chain_qa,
    suggest_entries_from_seam,
)


CORE_IDS = {
    "flicker",
    "morph",
    "halo",
    "identity_melt",
    "wardrobe_teleport",
    "lighting_pop",
    "prop_pop",
    "lip_desync",
    "motion_hitch",
    "resolution_swim",
}


def test_catalog_has_core_entries() -> None:
    ids = {e["id"] for e in list_entries()}
    assert {"flicker", "morph", "halo", "identity_melt"}.issubset(ids)
    assert CORE_IDS.issubset(ids)


def test_entry_contract_fields() -> None:
    for entry in list_entries():
        for key in (
            "id",
            "name",
            "aliases",
            "category",
            "description",
            "symptoms",
            "negative_phrases",
            "positive_guards",
            "qa_hooks",
        ):
            assert key in entry, f"missing {key} on {entry.get('id')}"
        assert isinstance(entry["negative_phrases"], list)
        assert len(entry["negative_phrases"]) >= 1
        assert isinstance(entry["positive_guards"], list)
        assert len(entry["positive_guards"]) >= 1


def test_get_entry_and_category_filter() -> None:
    assert get_entry("morph") is not None
    assert get_entry("morph")["category"] == "identity"
    assert get_entry("nope") is None
    temporal = list_entries(category="temporal")
    assert {e["id"] for e in temporal} >= {"flicker", "motion_hitch", "resolution_swim"}
    assert all(e["category"] == "temporal" for e in temporal)


def test_negative_pack_contains_phrases() -> None:
    pack = build_negative_pack(["flicker", "morph"])
    assert "flicker" in pack.lower() or "temporal" in pack.lower()
    assert "morph" in pack.lower() or "face" in pack.lower()
    assert len(pack) > 20


def test_default_pack_nonempty() -> None:
    pack = build_negative_pack(all_default=True)
    assert pack
    assert len(pack) > 40
    # Default ids should contribute recognizable phrases
    lower = pack.lower()
    assert "flicker" in lower or "strobe" in lower
    assert "morph" in lower or "melt" in lower


def test_default_pack_ids_match_plan() -> None:
    assert tuple(DEFAULT_PACK_IDS) == (
        "flicker",
        "morph",
        "halo",
        "identity_melt",
        "wardrobe_teleport",
        "lighting_pop",
        "motion_hitch",
    )


def test_positive_guards_nonempty() -> None:
    guards = build_positive_guards(["halo", "lighting_pop"])
    assert guards
    assert "halo" in guards.lower() or "silhouette" in guards.lower() or "edge" in guards.lower()


def test_suggest_from_seam_morph_factor() -> None:
    ids = suggest_entries_from_seam(
        {"factors": ["morph risk at boundary"], "seam_risk": 7}
    )
    assert "morph" in ids or "flicker" in ids
    # High seam_risk should pull default pack coverage
    assert "halo" in ids or "motion_hitch" in ids or "identity_melt" in ids


def test_suggest_from_seam_keyword_only() -> None:
    ids = suggest_entries_from_seam(
        {"factors": ["edge glow and double contour"], "seam_risk": 3}
    )
    assert "halo" in ids


def test_suggest_from_seam_none() -> None:
    assert suggest_entries_from_seam(None) == []
    assert suggest_entries_from_seam({}) == []


def test_suggest_from_chain_qa_drift() -> None:
    ids = suggest_entries_from_chain_qa(
        {"critical": ["character_drift_boundary"], "scores": {"stitch_artifact_risk": 5}}
    )
    assert "identity_melt" in ids or "morph" in ids
    assert "flicker" in ids or "halo" in ids or "motion_hitch" in ids


def test_format_lexicon_markdown() -> None:
    md = format_lexicon_markdown(["flicker"])
    assert "# Stitch Artifact Lexicon" in md
    assert "`flicker`" in md
    assert "Temporal flicker" in md
    full = format_lexicon_markdown()
    assert "identity_melt" in full
    assert len(full) > len(md)
