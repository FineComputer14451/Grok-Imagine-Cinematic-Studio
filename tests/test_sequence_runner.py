"""Tests for sequence clip runner."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from sequence_chain import add_clip_to_sequence, create_clip, create_sequence_scaffold, save_sequence  # noqa: E402
from sequence_runner import run_sequence_clip  # noqa: E402


def test_sequence_run_dry_run(tmp_path) -> None:
    seq = create_sequence_scaffold("Runner Test", target_duration=20)
    clip = create_clip(
        duration_seconds=8,
        prompt="Opening wide shot, dawn mist over lake",
        reference_image_id="ref_001",
    )
    add_clip_to_sequence(seq, clip)

    seq_dir = tmp_path / "sequences"
    save_sequence(seq, root=seq_dir)

    result = run_sequence_clip(seq, "clip_001", dry_run=True, record_quota=False)
    assert result["dry_run"] is True
    assert result["result_url"]
    assert result["clip_id"] == "clip_001"
    assert result["chain_qa"]["decision"] == "go"
    assert seq["clips"][0]["status"] == "approved"


if __name__ == "__main__":
    test_sequence_run_dry_run(Path("/tmp"))
    print("Sequence runner test passed")