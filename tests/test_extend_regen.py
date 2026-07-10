"""Tests for extend re-gen loop (roadmap #5)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from extend_regen import (  # noqa: E402
    DEFAULT_MAX_ATTEMPTS_PER_CLIP,
    apply_regen_plan,
    build_regen_fix_prompt,
    can_regen,
    ensure_regen_budget,
    ensure_clip_regen,
    plan_regen,
    prepare_regen_run,
)
from sequence_chain import create_clip, create_sequence_scaffold  # noqa: E402


def test_default_max_attempts() -> None:
    assert DEFAULT_MAX_ATTEMPTS_PER_CLIP == 2


def test_ensure_budget_on_sequence() -> None:
    seq = create_sequence_scaffold("Regen Seq")
    ensure_regen_budget(seq)
    assert seq["regen_budget"]["max_attempts_per_clip"] == 2
    assert seq["regen_budget"]["sequence_attempts_used"] == 0


def test_can_regen_false_when_attempts_exhausted() -> None:
    seq = create_sequence_scaffold("R")
    ensure_regen_budget(seq)
    clip = create_clip(prompt="old")
    clip["clip_id"] = "clip_001"
    ensure_clip_regen(clip, seq)
    clip["regen"]["attempts"] = 2
    ok, reason = can_regen(seq, clip)
    assert ok is False
    assert "budget" in reason.lower() or "attempt" in reason.lower()


def test_can_regen_true_with_no_go() -> None:
    seq = create_sequence_scaffold("R")
    ensure_regen_budget(seq)
    clip = create_clip(prompt="bad stitch")
    clip["clip_id"] = "clip_002"
    clip["status"] = "qa_hold"
    clip["chain_qa"] = {
        "decision": "no_go",
        "fixes": ["Strengthen LAST_FRAME_RECAP", "Critical chain QA failure"],
        "critical_failures": ["last_frame_continuity"],
        "weighted_score": 4.0,
    }
    ensure_clip_regen(clip, seq)
    ok, reason = can_regen(seq, clip)
    assert ok is True


def test_build_fix_prompt_includes_fixes_and_memory() -> None:
    seq = create_sequence_scaffold("R")
    seq["memory_bank"]["environment"]["location"] = "Neon alley"
    seq["memory_bank"]["lighting"]["state"] = "wet neon"
    clip = create_clip(
        prompt="Continue run",
        last_frame_recap="Hero mid-stride",
        reference_image_id="ref_1",
    )
    clip["clip_id"] = "clip_002"
    clip["chain_qa"] = {
        "decision": "no_go",
        "fixes": ["Character drift at stitch", "regenerate clip"],
        "critical_failures": ["character_drift_boundary"],
    }
    clip["identity_drift"] = {
        "drift_score": 4.0,
        "factors": ["Anchors missed=2/3"],
        "fixes": ["Reinforce DNA anchors in prompt"],
    }
    clip["seam_report"] = {
        "seam_risk": 6.5,
        "factors": ["Previous LAST_FRAME_RECAP missing"],
        "fixes": ["Capture LAST_FRAME_RECAP"],
    }
    prev = create_clip(last_frame_recap="End of alley, coat wet")
    text = build_regen_fix_prompt(seq, clip, previous_clip=prev, next_beat="Continue the chase")
    assert "REGEN_FIX" in text or "RE-GEN" in text or "FIX:" in text
    assert "Character drift" in text or "drift" in text.lower()
    assert "Neon alley" in text or "SEQUENCE_MEMORY_BANK" in text
    assert "Continue the chase" in text or "chase" in text.lower()
    # Lexicon-expanded NEGATIVES (default/high-risk pack includes flicker or morph)
    assert "NEGATIVES" in text
    assert "flicker" in text.lower() or "morph" in text.lower()


def test_plan_regen_returns_structured_result() -> None:
    seq = create_sequence_scaffold("R")
    ensure_regen_budget(seq)
    clip = create_clip(prompt="x")
    clip["clip_id"] = "clip_001"
    clip["chain_qa"] = {"decision": "no_go", "fixes": ["Fix A"], "critical_failures": []}
    plan = plan_regen(seq, clip)
    assert plan["allowed"] is True
    assert plan["fix_prompt"]
    assert "Fix A" in plan["fix_prompt"] or "Fix A" in str(plan.get("fixes"))


def test_apply_regen_plan_sets_prompt() -> None:
    seq = create_sequence_scaffold("R")
    ensure_regen_budget(seq)
    clip = create_clip(prompt="original")
    clip["clip_id"] = "clip_001"
    clip["chain_qa"] = {"decision": "no_go", "fixes": ["Add lighting continuity"], "critical_failures": []}
    plan = plan_regen(seq, clip)
    apply_regen_plan(seq, clip, plan)
    assert clip["prompt"] == plan["fix_prompt"]
    assert clip.get("regen_fix_prompt") == plan["fix_prompt"]
    assert clip["status"] in ("pending", "qa_hold", "regen_ready")


def test_prepare_regen_run_consumes_attempt() -> None:
    seq = create_sequence_scaffold("R")
    ensure_regen_budget(seq)
    clip = create_clip(prompt="original")
    clip["clip_id"] = "clip_001"
    clip["chain_qa"] = {
        "decision": "no_go",
        "fixes": ["Strengthen LAST_FRAME_RECAP"],
        "critical_failures": ["last_frame_continuity"],
    }
    ensure_clip_regen(clip, seq)
    assert clip["regen"]["attempts"] == 0
    assert seq["regen_budget"]["sequence_attempts_used"] == 0

    plan = prepare_regen_run(seq, clip)
    assert plan["allowed"] is True
    assert clip["regen"]["attempts"] == 1
    assert seq["regen_budget"]["sequence_attempts_used"] == 1
    assert clip["prompt"] == plan["fix_prompt"]
    assert clip["status"] == "regen_ready"
