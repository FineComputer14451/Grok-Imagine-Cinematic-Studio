"""Still path resolve + hybrid still compare (evidence quality)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from identity_drift import (  # noqa: E402
    compare_stills_soft,
    report_to_drift_evidence,
    resolve_still_paths,
    score_identity_drift,
)
from sequence_chain import create_clip  # noqa: E402

PIL = pytest.importorskip("PIL.Image", reason="Pillow optional for hybrid tests")


def _write_solid_png(path: Path, rgb: tuple[int, int, int], size: int = 32) -> None:
    from PIL import Image

    Image.new("RGB", (size, size), rgb).save(path)


def test_resolve_flags_override_clip_fields(tmp_path: Path) -> None:
    ref_flag = tmp_path / "flag_ref.png"
    clip_flag = tmp_path / "flag_clip.png"
    ref_clip = tmp_path / "clip_ref.png"
    clip_clip = tmp_path / "clip_clip.png"
    for p, c in [
        (ref_flag, (10, 10, 10)),
        (clip_flag, (20, 20, 20)),
        (ref_clip, (30, 30, 30)),
        (clip_clip, (40, 40, 40)),
    ]:
        _write_solid_png(p, c)
    clip = create_clip(prompt="x")
    clip["reference_still_path"] = str(ref_clip)
    clip["last_frame_path"] = str(clip_clip)
    r, c = resolve_still_paths(
        clip, ref_still=str(ref_flag), clip_still=str(clip_flag)
    )
    assert r == str(ref_flag)
    assert c == str(clip_flag)


def test_resolve_clip_fields_when_no_flags(tmp_path: Path) -> None:
    ref = tmp_path / "hero.png"
    cur = tmp_path / "last.png"
    _write_solid_png(ref, (1, 2, 3))
    _write_solid_png(cur, (4, 5, 6))
    clip = create_clip(prompt="x")
    clip["hero_plate_path"] = str(ref)
    clip["last_frame_path"] = str(cur)
    r, c = resolve_still_paths(clip)
    assert r == str(ref)
    assert c == str(cur)


def test_resolve_missing_file_returns_none(tmp_path: Path) -> None:
    clip = create_clip(prompt="x")
    clip["reference_still_path"] = str(tmp_path / "nope.png")
    r, c = resolve_still_paths(clip)
    assert r is None
    assert c is None


def test_compare_identical_stills_low_penalty(tmp_path: Path) -> None:
    a = tmp_path / "a.png"
    b = tmp_path / "b.png"
    _write_solid_png(a, (100, 120, 140))
    _write_solid_png(b, (100, 120, 140))
    result = compare_stills_soft(str(a), str(b))
    assert result is not None
    penalty, signals = result
    assert 0.0 <= penalty <= 0.5
    assert signals["size"] == 128
    assert "luma_mae" in signals


def test_compare_different_stills_higher_penalty(tmp_path: Path) -> None:
    a = tmp_path / "a.png"
    b = tmp_path / "b.png"
    _write_solid_png(a, (0, 0, 0))
    _write_solid_png(b, (255, 255, 255))
    result = compare_stills_soft(str(a), str(b))
    assert result is not None
    same = compare_stills_soft(str(a), str(a))
    assert same is not None
    penalty_same, _ = same
    penalty_diff, signals = result
    assert penalty_diff > penalty_same
    assert penalty_diff <= 3.0
    assert signals["hist_l1"] >= 0


def test_score_hybrid_mode_with_stills(tmp_path: Path) -> None:
    ref = tmp_path / "ref.png"
    cur = tmp_path / "cur.png"
    _write_solid_png(ref, (50, 50, 50))
    _write_solid_png(cur, (50, 50, 50))
    clip = create_clip(
        prompt="Liora charcoal coat black bob scar left brow",
        reference_image_id="ref_liora_a1",
        last_frame_recap="same face coat bob scar",
    )
    dna = {
        "character_name": "Liora",
        "slug": "liora",
        "core_identity": "East Asian woman mid-20s",
        "facial_dna": "almond eyes high cheekbones scar left brow",
        "hair_grooming": "black bob",
        "clothing_style": "charcoal coat",
        "key_consistency_anchors": ["scar left brow", "charcoal coat", "black bob"],
        "reference_image_ids": ["ref_liora_a1"],
        "identity_lock_status": "locked",
    }
    report = score_identity_drift(
        clip,
        dna=dna,
        reference_still_path=str(ref),
        clip_still_path=str(cur),
    )
    assert report["mode"] == "hybrid"
    assert report["still_signals"] is not None
    assert report["still_paths"]["ref"] == str(ref)
    assert report["still_paths"]["clip"] == str(cur)
    evidence = report_to_drift_evidence(report, character_slug="liora")
    assert "hybrid_still" in evidence["signals"]["flags"]


def test_facial_dna_miss_increases_drift() -> None:
    dna = {
        "character_name": "Liora",
        "slug": "liora",
        "core_identity": "East Asian woman mid-20s sharp jaw",
        "facial_dna": "unique violet heterochromia freckle constellation",
        "hair_grooming": "black bob straight",
        "clothing_style": "long charcoal coat",
        "key_consistency_anchors": ["scar left brow", "charcoal coat", "black bob"],
        "reference_image_ids": ["ref_liora_a1"],
        "identity_lock_status": "locked",
    }
    good = create_clip(
        prompt=(
            "Liora charcoal coat black bob scar left brow "
            "violet heterochromia freckle constellation"
        ),
        reference_image_id="ref_liora_a1",
        last_frame_recap="scar coat bob violet eyes freckle",
    )
    bad = create_clip(
        prompt="Liora charcoal coat black bob scar left brow",
        reference_image_id="ref_liora_a1",
        last_frame_recap="coat bob scar",
    )
    r_good = score_identity_drift(good, dna=dna)
    r_bad = score_identity_drift(bad, dna=dna)
    assert r_bad["drift_score"] >= r_good["drift_score"]
