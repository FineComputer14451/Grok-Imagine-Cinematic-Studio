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
        prompt="Opening wide shot, dawn mist over lake, cinematic 35mm",
        reference_image_id="ref_001",
        last_frame_recap=(
            "Wide lake at dawn, hero silhouette on shore, mist rolling, "
            "camera static low angle, cool blue grade, water still"
        ),
    )
    clip["momentum_vector"]["last_action"] = "Stands at shore"
    clip["momentum_vector"]["emotional_state"] = "Contemplative"
    clip["momentum_vector"]["lighting_state"] = "Cool dawn sidelight"
    add_clip_to_sequence(seq, clip)

    seq_dir = tmp_path / "sequences"
    save_sequence(seq, root=seq_dir)

    result = run_sequence_clip(seq, "clip_001", dry_run=True, record_quota=False)
    assert result["dry_run"] is True
    assert result["result_url"]
    assert result["clip_id"] == "clip_001"
    assert result["chain_qa"]["decision"] in ("go", "conditional_go")
    assert seq["clips"][0]["status"] == "approved"


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        test_sequence_run_dry_run(Path(tmp))
    print("Sequence runner test passed")