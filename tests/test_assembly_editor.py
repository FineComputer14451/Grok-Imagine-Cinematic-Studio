"""Tests for Assembly Editor EDL export."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from assembly_editor import build_edl, edl_to_markdown  # noqa: E402
from sequence_chain import add_clip_to_sequence, create_clip, create_sequence_scaffold  # noqa: E402


def test_build_edl_from_approved_clips() -> None:
    seq = create_sequence_scaffold("EDL Test", target_duration=30)
    c1 = create_clip(duration_seconds=10, prompt="Open", status="approved")
    c1["chain_qa"] = {"decision": "go", "weighted_score": 8.2}
    c2 = create_clip(duration_seconds=10, prompt="Continue", last_frame_recap="Hero at door")
    c2["status"] = "pending"
    add_clip_to_sequence(seq, c1)
    add_clip_to_sequence(seq, c2)

    edl = build_edl(seq, approved_only=True)
    assert edl["clip_count"] == 1
    assert edl["entries"][0]["clip_id"] == "clip_001"
    assert "EDL Test" in edl_to_markdown(edl)


if __name__ == "__main__":
    test_build_edl_from_approved_clips()
    print("Assembly editor tests passed")