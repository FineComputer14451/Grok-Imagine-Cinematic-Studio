#!/usr/bin/env python3
"""Readiness checks for sequence polish / deliver pipeline order."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Literal

from studio_paths import EDL_DIR, POLISHED_DIR, SEQUENCES_DIR

Stage = Literal["polish", "deliver"]


def clip_eligible_for_assembly(clip: dict[str, Any]) -> bool:
    """Match assembly_editor approved_only spirit."""
    status = clip.get("status", "pending")
    if status in ("approved", "qa_pass"):
        return True
    qa = clip.get("chain_qa") or clip.get("nsfw_chain_qa") or {}
    return qa.get("decision") == "go"


def _eligible_clips(seq: dict[str, Any], *, approved_only: bool) -> list[dict[str, Any]]:
    clips = seq.get("clips") or []
    if not approved_only:
        return list(clips)
    return [c for c in clips if clip_eligible_for_assembly(c)]


def _edl_exists(slug: str) -> bool:
    primary = EDL_DIR / slug / "assembly_edl.json"
    if primary.is_file():
        return True
    alt = SEQUENCES_DIR / slug / "assembly_edl.json"
    return alt.is_file()


def _has_polished_media(slug: str) -> bool:
    d = POLISHED_DIR / slug
    if not d.is_dir():
        return False
    return any(d.glob("*.mp4"))


def evaluate_delivery_pipeline_readiness(
    seq: dict[str, Any],
    *,
    stage: Stage,
    approved_only: bool = True,
) -> dict[str, Any]:
    """
    pass=False only when blockers present.
    Soft by default at CLI; --strict-delivery exits 1 on blockers.
    """
    slug = str(seq.get("slug") or "sequence")
    name = str(seq.get("sequence_name") or slug)
    blockers: list[str] = []
    warnings: list[str] = []
    fixes: list[str] = []

    eligible = _eligible_clips(seq, approved_only=approved_only)

    if not _edl_exists(slug):
        warnings.append(
            f"EDL missing for slug={slug!r} — recommend: sequence edl \"{name}\""
        )
        fixes.append(
            f'Run: python tools/cinematic_studio_cli.py sequence edl "{name}"'
        )

    if stage == "polish":
        if approved_only and not eligible:
            blockers.append(
                "No Go/approved clips eligible for polish (approved_only=True)"
            )
            fixes.append(
                "Run chain QA to Go, or pass explicit --clip list after approval"
            )
        if (
            seq.get("color_grade") is None
            and not (seq.get("grade_notes") or seq.get("lut"))
        ):
            warnings.append(
                "No color_grade/grade_notes/lut on sequence — "
                "color pass recommended before hero polish"
            )

    elif stage == "deliver":
        if not _has_polished_media(slug):
            blockers.append(
                f"No polished mp4 under polished/{slug}/ — run sequence polish first"
            )
            fixes.append(
                f'Run: python tools/cinematic_studio_cli.py sequence polish "{name}"'
            )
        if approved_only and not eligible:
            blockers.append(
                "No Go/approved clips for delivery assembly (approved_only=True)"
            )
        if shutil.which("ffmpeg") is None:
            warnings.append("ffmpeg not on PATH — deliver may be manifest-only")

    else:
        blockers.append(f"Unknown stage: {stage!r}")

    return {
        "pass": len(blockers) == 0,
        "strict": True,
        "stage": stage,
        "slug": slug,
        "eligible_count": len(eligible),
        "blockers": blockers,
        "warnings": warnings,
        "fixes": fixes,
    }
