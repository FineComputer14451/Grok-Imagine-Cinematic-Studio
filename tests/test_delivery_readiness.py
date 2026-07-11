"""Delivery pipeline readiness (polish / deliver order gates)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from delivery_readiness import (  # noqa: E402
    clip_eligible_for_assembly,
    evaluate_delivery_pipeline_readiness,
)


def _seq(clips, slug="demo"):
    return {
        "sequence_name": "Demo",
        "slug": slug,
        "clips": clips,
    }


def _go_clip(cid="clip_001", **extra):
    c = {
        "clip_id": cid,
        "status": "approved",
        "duration_seconds": 8,
        "chain_qa": {"decision": "go"},
    }
    c.update(extra)
    return c


def test_polish_blocks_when_no_eligible_clips() -> None:
    seq = _seq(
        [
            {
                "clip_id": "clip_001",
                "status": "pending",
                "chain_qa": {"decision": "no_go"},
            }
        ]
    )
    r = evaluate_delivery_pipeline_readiness(seq, stage="polish", approved_only=True)
    assert r["pass"] is False
    assert any(
        "eligible" in b.lower() or "approved" in b.lower() or "go" in b.lower()
        for b in r["blockers"]
    )


def test_polish_passes_with_go_clip() -> None:
    seq = _seq([_go_clip()])
    r = evaluate_delivery_pipeline_readiness(seq, stage="polish", approved_only=True)
    assert r["pass"] is True


def test_deliver_blocks_without_polished_media(tmp_path, monkeypatch) -> None:
    import delivery_readiness as dr

    monkeypatch.setattr(dr, "POLISHED_DIR", tmp_path / "polished")
    (tmp_path / "polished" / "demo").mkdir(parents=True)
    seq = _seq([_go_clip()], slug="demo")
    r = evaluate_delivery_pipeline_readiness(seq, stage="deliver", approved_only=True)
    assert r["pass"] is False
    assert any("polish" in b.lower() for b in r["blockers"])


def test_deliver_passes_with_polished_mp4(tmp_path, monkeypatch) -> None:
    import delivery_readiness as dr

    monkeypatch.setattr(dr, "POLISHED_DIR", tmp_path / "polished")
    d = tmp_path / "polished" / "demo"
    d.mkdir(parents=True)
    (d / "clip_001.mp4").write_bytes(b"fake")
    seq = _seq([_go_clip()], slug="demo")
    r = evaluate_delivery_pipeline_readiness(seq, stage="deliver", approved_only=True)
    assert r["pass"] is True


def test_clip_eligible_helper() -> None:
    assert clip_eligible_for_assembly(_go_clip()) is True
    assert (
        clip_eligible_for_assembly(
            {"clip_id": "x", "status": "pending", "chain_qa": {}}
        )
        is False
    )


def test_edl_missing_is_warning_not_blocker() -> None:
    seq = _seq([_go_clip()], slug="no-edl-here")
    r = evaluate_delivery_pipeline_readiness(seq, stage="polish", approved_only=True)
    assert r["pass"] is True
    assert any("edl" in w.lower() for w in r["warnings"])
