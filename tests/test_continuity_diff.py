"""Tests for continuity diff (roadmap #9)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from continuity_diff import (  # noqa: E402
    diff_clip_pair,
    diff_clip_vs_bank,
    format_continuity_diff_markdown,
)
from sequence_chain import create_clip  # noqa: E402
from sequence_memory import empty_memory_bank  # noqa: E402


def test_clip_pair_detects_location_change() -> None:
    prev = create_clip()
    prev["clip_id"] = "clip_001"
    prev["continuity_state"] = {"location": "Alley", "props": ["umbrella"]}
    prev["momentum_vector"]["lighting_state"] = "neon"
    curr = create_clip()
    curr["clip_id"] = "clip_002"
    curr["continuity_state"] = {"location": "Rooftop", "props": ["umbrella", "phone"]}
    curr["momentum_vector"]["lighting_state"] = "neon"
    report = diff_clip_pair(prev, curr)
    assert report["mode"] == "clip_pair"
    assert report["summary"]["total"] >= 1
    paths = {c["path"] for c in report["changes"]}
    assert any("location" in p for p in paths)
    assert any("props" in p for p in paths)


def test_no_changes_empty_summary() -> None:
    a = create_clip()
    a["continuity_state"] = {"location": "Dock"}
    b = create_clip()
    b["continuity_state"] = {"location": "Dock"}
    report = diff_clip_pair(a, b)
    assert report["summary"]["changed"] == 0 or report["summary"]["total"] == 0


def test_markdown_contains_headers() -> None:
    prev = create_clip()
    prev["clip_id"] = "clip_001"
    prev["continuity_state"] = {"location": "A"}
    curr = create_clip()
    curr["clip_id"] = "clip_002"
    curr["continuity_state"] = {"location": "B"}
    md = format_continuity_diff_markdown(diff_clip_pair(prev, curr))
    assert "Continuity Diff" in md or "continuity" in md.lower()
    assert "location" in md.lower()


def test_clip_vs_bank_prop_gap() -> None:
    bank = empty_memory_bank()
    bank["environment"]["location"] = "Neon alley"
    bank["environment"]["props"] = ["key", "coat"]
    clip = create_clip()
    clip["clip_id"] = "clip_003"
    clip["continuity_state"] = {"location": "Neon alley", "props": ["key"]}
    report = diff_clip_vs_bank(clip, bank)
    assert report["mode"] == "clip_vs_bank"
    assert report["summary"]["total"] >= 1
