"""Tests for emotional temperature gate (roadmap #7)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from emotional_temperature import (  # noqa: E402
    evaluate_temperature_gate,
    infer_observed_temp,
    normalize_curve,
    planned_temp_at,
)
from sequence_chain import create_clip, create_sequence_scaffold  # noqa: E402


def test_normalize_bare_numbers() -> None:
    curve = normalize_curve([2, 5, 8])
    assert len(curve) == 3
    assert curve[0]["index"] == 0 and curve[0]["temp"] == 2.0
    assert curve[2]["temp"] == 8.0


def test_normalize_dicts() -> None:
    curve = normalize_curve([
        {"index": 1, "temp": 4, "label": "wary"},
        {"index": 0, "temp": 2, "beat": "open"},
    ])
    assert curve[0]["index"] == 0
    assert curve[1]["label"] == "wary"


def test_planned_temp_exact_and_interp() -> None:
    curve = normalize_curve([
        {"index": 0, "temp": 2},
        {"index": 2, "temp": 8},
    ])
    assert planned_temp_at(curve, 0) == 2.0
    assert planned_temp_at(curve, 2) == 8.0
    mid = planned_temp_at(curve, 1)
    assert mid is not None and 4.5 <= mid <= 5.5


def test_infer_observed_from_momentum() -> None:
    clip = create_clip()
    clip["momentum_vector"]["emotional_state"] = "rising dread"
    t = infer_observed_temp(clip)
    assert t is not None and t >= 6.0


def test_gate_missing_curve_warns() -> None:
    seq = create_sequence_scaffold("Emo")
    clip = create_clip()
    clip["index"] = 0
    report = evaluate_temperature_gate(seq, clip)
    assert report["severity"] in ("warn", "ok")
    assert "missing_curve" in report["flags"] or report["curve_length"] == 0


def test_gate_unplanned_spike_fails() -> None:
    seq = create_sequence_scaffold("Spike")
    seq["emotional_temperature_curve"] = normalize_curve([
        {"index": 0, "temp": 3},
        {"index": 1, "temp": 3.5},  # planned nearly flat
    ])
    prev = create_clip()
    prev["index"] = 0
    prev["momentum_vector"]["emotional_state"] = "calm"
    clip = create_clip()
    clip["index"] = 1
    clip["clip_id"] = "clip_002"
    clip["momentum_vector"]["emotional_state"] = "panicked rage"
    report = evaluate_temperature_gate(seq, clip, previous_clip=prev)
    assert report["severity"] == "fail"
    assert "unplanned_spike" in report["flags"]
    assert report["pass"] is False


def test_gate_on_plan_passes() -> None:
    seq = create_sequence_scaffold("Ok")
    seq["emotional_temperature_curve"] = normalize_curve([
        {"index": 0, "temp": 3},
        {"index": 1, "temp": 7},
    ])
    prev = create_clip()
    prev["index"] = 0
    prev["momentum_vector"]["emotional_state"] = "wary"
    clip = create_clip()
    clip["index"] = 1
    clip["momentum_vector"]["emotional_state"] = "dread"
    report = evaluate_temperature_gate(seq, clip, previous_clip=prev)
    assert report["pass"] is True
    assert report["severity"] in ("ok", "warn")
