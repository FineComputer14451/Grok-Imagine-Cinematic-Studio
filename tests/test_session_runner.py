"""Tests for automated batch session runner."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from session_runner import run_batch_session  # noqa: E402
from sfw_orchestrator import plan_batch, save_batch  # noqa: E402


def test_run_batch_session_dry_run() -> None:
    batch = plan_batch(
        "Session Test",
        [{"tier": "filler", "description": "Atmosphere"}],
        budget_credits=100,
    )
    save_batch(batch)
    slug = batch["slug"]
    noop = lambda *args, **kwargs: None
    with patch("quota_optimizer.save_project_state", noop), patch(
        "project_state.save_project_state", noop
    ):
        summary = run_batch_session(slug, pipeline="sfw", count=1, dry_run=True)
    assert summary["executed"] >= 1
    assert summary["results"][0].get("job_id")


if __name__ == "__main__":
    test_run_batch_session_dry_run()
    print("All session runner tests passed")