"""Tests for two-pass quality pass scheduler."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from models import DEFAULT_IMAGINE_VIDEO_MODEL  # noqa: E402
from quality_pass_scheduler import (  # noqa: E402
    PASS_1_VIDEO_MODEL,
    apply_quality_pass_promotion,
    configure_two_pass_shot,
    get_pending_quality_passes,
    plan_two_pass_batch,
    promote_after_qa,
)


def test_configure_two_pass() -> None:
    shot = configure_two_pass_shot({"shot_id": "s1", "tier": "hero"})
    assert shot["two_pass"] is True
    assert shot["video_model"] == PASS_1_VIDEO_MODEL
    assert shot["fast_mode"] is True


def test_plan_two_pass_batch() -> None:
    shots = plan_two_pass_batch([{"shot_id": "a"}, {"shot_id": "b"}])
    assert all(s["two_pass"] for s in shots)


def test_promote_after_qa_pass() -> None:
    shot = configure_two_pass_shot({"shot_id": "s1"})
    plan = promote_after_qa(shot, quality_score=8.0)
    assert plan is not None
    assert plan["action"] == "quality_pass"
    assert shot["quality_pass_status"] == "quality_pass_pending"


def test_promote_after_qa_hold() -> None:
    shot = configure_two_pass_shot({"shot_id": "s1"})
    plan = promote_after_qa(shot, quality_score=5.0)
    assert plan is not None
    assert plan["action"] == "hold"


def test_apply_quality_pass_promotion() -> None:
    shot = configure_two_pass_shot({"shot_id": "s1"})
    promote_after_qa(shot, quality_score=8.0)
    apply_quality_pass_promotion(shot)
    assert shot["pass_number"] == 2
    assert shot["video_model"] == DEFAULT_IMAGINE_VIDEO_MODEL
    assert shot["fast_mode"] is False


def test_get_pending_quality_passes() -> None:
    shots = plan_two_pass_batch([{"shot_id": "a"}, {"shot_id": "b"}])
    promote_after_qa(shots[0], quality_score=8.0)
    batch = {"shots": shots}
    pending = get_pending_quality_passes(batch)
    assert len(pending) == 1
    assert pending[0]["shot_id"] == "a"


if __name__ == "__main__":
    test_configure_two_pass()
    test_plan_two_pass_batch()
    test_promote_after_qa_pass()
    test_promote_after_qa_hold()
    test_apply_quality_pass_promotion()
    test_get_pending_quality_passes()
    print("All quality pass scheduler tests passed")