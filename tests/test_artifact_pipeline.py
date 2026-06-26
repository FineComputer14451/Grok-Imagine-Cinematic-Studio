"""Tests for artifact pipeline."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from artifact_pipeline import artifacts_summary, register_artifact_from_result  # noqa: E402


def test_register_artifact_manifest() -> None:
    noop = lambda *args, **kwargs: None
    with patch("project_state.save_project_state", noop):
        entry = register_artifact_from_result(
            {
                "job_id": "job_test_001",
                "shot_id": "shot_a",
                "result_url": "https://dry-run.x.ai/images/test.png",
                "dry_run": True,
            },
            batch_slug="test-batch",
            pipeline="sfw",
        )
    assert entry["job_id"] == "job_test_001"
    assert entry["local_path"].endswith(".png")
    assert Path(entry["local_path"] + ".manifest.json").exists()


def test_artifacts_summary_shape() -> None:
    summary = artifacts_summary()
    assert "total" in summary
    assert "generations_dir" in summary


if __name__ == "__main__":
    test_register_artifact_manifest()
    test_artifacts_summary_shape()
    print("All artifact pipeline tests passed")