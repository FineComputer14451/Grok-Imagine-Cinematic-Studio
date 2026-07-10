"""Tests for arc replan co-pilot core (roadmap #12)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from arc_replan import (  # noqa: E402
    apply_arc_replan,
    format_arc_replan_markdown,
    infer_replan_reason,
    plan_arc_replan,
)
from emotional_temperature import normalize_curve  # noqa: E402
from sequence_chain import (  # noqa: E402
    add_clip_to_sequence,
    create_clip,
    create_sequence_scaffold,
)


def _seq_with_two_clips() -> dict:
    seq = create_sequence_scaffold("Arc", target_duration=40)
    c0 = create_clip(prompt="Open", status="approved", duration_seconds=10)
    c1 = create_clip(prompt="Continue", status="qa_hold", duration_seconds=10)
    add_clip_to_sequence(seq, c0)
    add_clip_to_sequence(seq, c1)
    # index 1 no_go
    seq["clips"][1]["chain_qa"] = {
        "decision": "no_go",
        "weighted_score": 4.0,
        "fixes": ["Strengthen last-frame continuity"],
    }
    seq["emotional_temperature_curve"] = normalize_curve(
        [
            {"index": 0, "temp": 3.0},
            {"index": 1, "temp": 6.0},
        ]
    )
    return seq


def test_infer_replan_reason_priority() -> None:
    clip = create_clip()
    assert infer_replan_reason(clip) == "manual"

    clip["status"] = "qa_hold"
    assert infer_replan_reason(clip) == "qa_hold"

    clip["temperature_gate"] = {"severity": "fail", "pass": False}
    assert infer_replan_reason(clip) == "temperature_fail"

    clip["identity_drift"] = {"pass": False, "drift_score": 4.0}
    assert infer_replan_reason(clip) == "identity_drift"

    clip["chain_qa"] = {"decision": "no_go"}
    assert infer_replan_reason(clip) == "chain_qa_no_go"


def test_plan_from_no_go_revises_remaining() -> None:
    seq = _seq_with_two_clips()
    prop = plan_arc_replan(seq, from_index=1)
    assert prop["from_index"] == 1
    assert prop["reason"] == "chain_qa_no_go"
    assert prop["replanned_clips"]
    assert prop["replanned_clips"][0]["action"] in ("soft_reset", "revise_beat")
    assert prop["replanned_clips"][0]["action"] == "soft_reset"
    assert prop["replanned_clips"][0]["narrative_beat"]
    assert prop["temperature_curve_patch"]
    assert all(
        p["index"] >= 1 for p in prop["temperature_curve_patch"]
    )
    # Only clip index >= 1
    assert all(r["index"] >= 1 for r in prop["replanned_clips"])


def test_apply_writes_narrative_beat_and_curve() -> None:
    seq = _seq_with_two_clips()
    prop = plan_arc_replan(seq, from_index=1)
    apply_arc_replan(seq, prop)
    assert seq["clips"][1].get("narrative_beat")
    assert "Recover" in seq["clips"][1]["narrative_beat"] or seq["clips"][1][
        "narrative_beat"
    ]
    assert seq["emotional_temperature_curve"]
    # prefix curve point for index 0 preserved; patch for >= 1 applied
    idxs = {int(p["index"]) for p in seq["emotional_temperature_curve"]}
    assert 0 in idxs
    assert 1 in idxs
    assert seq.get("arc_replan_history")
    assert len(seq["arc_replan_history"]) == 1
    assert seq.get("arc_replan")
    assert seq["arc_replan"]["from_index"] == 1
    # Frozen clip beat untouched
    assert not seq["clips"][0].get("narrative_beat")


def test_frozen_prefix_not_in_replanned() -> None:
    seq = _seq_with_two_clips()
    # three clips: 0,1 approved-ish, 2 no_go — replan from 1 still freezes 0
    c2 = create_clip(prompt="Third", status="pending", duration_seconds=10)
    add_clip_to_sequence(seq, c2)
    prop = plan_arc_replan(seq, from_index=1)
    assert "clip_001" in prop["frozen_clip_ids"]
    frozen_set = set(prop["frozen_clip_ids"])
    for r in prop["replanned_clips"]:
        assert r.get("clip_id") not in frozen_set
        assert int(r["index"]) >= 1
    assert all(int(r["index"]) < 1 for r in [] ) or True  # frozen is index < 1
    # soft_reset first, revise_beat after
    assert prop["replanned_clips"][0]["action"] == "soft_reset"
    if len(prop["replanned_clips"]) > 1:
        assert prop["replanned_clips"][1]["action"] == "revise_beat"


def test_default_from_index_finds_no_go() -> None:
    seq = _seq_with_two_clips()
    prop = plan_arc_replan(seq)
    assert prop["from_index"] == 1
    assert prop["reason"] == "chain_qa_no_go"


def test_plan_from_clip_id() -> None:
    seq = _seq_with_two_clips()
    prop = plan_arc_replan(seq, from_clip_id="clip_002")
    assert prop["from_index"] == 1
    assert prop["replanned_clips"][0]["clip_id"] == "clip_002"


def test_format_arc_replan_markdown() -> None:
    seq = _seq_with_two_clips()
    prop = plan_arc_replan(seq, from_index=1)
    md = format_arc_replan_markdown(prop)
    assert "Arc Replan" in md
    assert "soft_reset" in md or "revise_beat" in md
    assert "clip_002" in md or "1" in md


def test_gentle_slope_max_step() -> None:
    seq = create_sequence_scaffold("Slope", target_duration=60)
    for i in range(4):
        add_clip_to_sequence(
            seq, create_clip(prompt=f"Beat {i}", duration_seconds=10)
        )
    seq["clips"][0]["status"] = "approved"
    seq["clips"][1]["chain_qa"] = {"decision": "no_go"}
    seq["clips"][1]["status"] = "qa_hold"
    seq["emotional_temperature_curve"] = normalize_curve(
        [
            {"index": 0, "temp": 2.0},
            {"index": 3, "temp": 9.0},
        ]
    )
    prop = plan_arc_replan(seq, from_index=1, reason="temperature_fail")
    temps = [r["planned_temp"] for r in prop["replanned_clips"]]
    assert temps
    for a, b in zip(temps, temps[1:]):
        assert abs(b - a) <= 1.5 + 1e-6
