"""Tests for animatic orchestrator."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from animatic_orchestrator import plan_animatic, promote_frame  # noqa: E402


def test_plan_and_promote() -> None:
    board = plan_animatic("Previs", ["hero:Opening wide:8", "coverage:Insert:4"], target_duration=60)
    assert board["frame_count"] == 2
    assert board["frames"][0]["tier"] == "hero"
    promote_frame(board, board["frames"][1]["frame_id"], to_tier="standard", qa_score=7.5)
    assert board["frames"][1]["tier"] == "standard"
    assert board["cost_estimate"]["animatic_credits"] > 0


if __name__ == "__main__":
    test_plan_and_promote()
    print("Animatic orchestrator tests passed")