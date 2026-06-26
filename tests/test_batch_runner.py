"""Tests for SFW batch shot runner."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from batch_runner import execute_sfw_shot  # noqa: E402
from sfw_orchestrator import plan_batch, save_batch  # noqa: E402


def test_execute_shot_dry_run_image() -> None:
    batch = plan_batch(
        "Bridge Test",
        [{"tier": "filler", "description": "Mood atmosphere"}],
        budget_credits=200,
    )
    shot_id = batch["shots"][0]["shot_id"]
    noop = lambda *args, **kwargs: None
    with patch("quota_optimizer.save_project_state", noop), patch(
        "project_state.save_project_state", noop
    ):
        result = execute_sfw_shot(batch, shot_id, dry_run=True, record_quota=False)
    assert result["dry_run"] is True
    assert result["job_id"]
    assert result["result_url"]
    assert result["shot_id"] == shot_id


def test_execute_shot_not_found() -> None:
    batch = plan_batch("Empty", [{"tier": "filler", "description": "x"}], budget_credits=50)
    try:
        execute_sfw_shot(batch, "missing_shot", dry_run=True, record_quota=False)
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "not found" in str(exc).lower()


if __name__ == "__main__":
    test_execute_shot_dry_run_image()
    test_execute_shot_not_found()
    print("All batch runner tests passed")