#!/usr/bin/env python3
"""
Identity drift scorer for long-form extend/stitch (roadmap #1).

Returns a structured report. Higher drift_score = more drift (0–10).
Pass when drift_score < threshold (default 2.5, Identity Lock convention).
v1: metadata heuristics; optional still paths for hybrid mode via soft PIL import.
"""

from __future__ import annotations

import re
from typing import Any

DEFAULT_DRIFT_THRESHOLD = 2.5

_TOKEN_RE = re.compile(r"[a-z0-9']+")


def _tokens(text: str) -> set[str]:
    return {t for t in _TOKEN_RE.findall((text or "").lower()) if len(t) > 2}


def _clamp(score: float, lo: float = 0.0, hi: float = 10.0) -> float:
    return round(max(lo, min(hi, score)), 2)


def _dna_corpus(dna: dict[str, Any]) -> str:
    parts = [
        dna.get("character_name", ""),
        dna.get("core_identity", ""),
        dna.get("facial_dna", ""),
        dna.get("hair_grooming", ""),
        dna.get("clothing_style", ""),
        dna.get("movement_posture", ""),
        " ".join(dna.get("key_consistency_anchors") or []),
    ]
    return " ".join(str(p) for p in parts if p)


def _anchor_hit(anchor: str, clip_text_lower: str, clip_toks: set[str]) -> bool:
    """True if full phrase appears or any distinctive token from the anchor is present."""
    a = anchor.strip().lower()
    if not a:
        return False
    if a in clip_text_lower:
        return True
    a_toks = _tokens(a)
    return bool(a_toks) and any(t in clip_toks for t in a_toks)


def score_identity_drift(
    clip: dict[str, Any],
    *,
    dna: dict[str, Any] | None = None,
    previous_clip: dict[str, Any] | None = None,
    threshold: float = DEFAULT_DRIFT_THRESHOLD,
    reference_still_path: str | None = None,
    clip_still_path: str | None = None,
) -> dict[str, Any]:
    """
    Score identity drift for a clip against Character DNA and chain context.

    Optional still paths enable hybrid mode when PIL can load both images.
    """
    factors: list[str] = []
    penalties: list[float] = []

    prompt = (clip.get("prompt") or "").strip()
    recap = (clip.get("last_frame_recap") or "").strip()
    ref_id = (clip.get("reference_image_id") or "").strip()
    clip_text = f"{prompt} {recap}"
    clip_text_lower = clip_text.lower()
    clip_toks = _tokens(clip_text)

    if not dna:
        penalties.append(4.0)
        factors.append("No DNA profile — high identity risk")
        if len(prompt.split()) < 4:
            penalties.append(0.5)
            factors.append("Thin prompt without DNA")
    else:
        if dna.get("identity_lock_status") != "locked":
            penalties.append(1.0)
            factors.append(
                f"identity_lock_status={dna.get('identity_lock_status', 'pending')}"
            )

        corpus = _dna_corpus(dna)
        dna_toks = _tokens(corpus)
        anchors = [
            str(a) for a in (dna.get("key_consistency_anchors") or []) if str(a).strip()
        ]

        if not dna_toks:
            penalties.append(2.5)
            factors.append("DNA fields empty")
        elif not clip_toks:
            penalties.append(3.0)
            factors.append("Clip prompt/recap empty — cannot verify identity")
        else:
            # Coverage: fraction of DNA tokens found in clip text (identity recall)
            overlap = len(dna_toks & clip_toks) / max(1, len(dna_toks))
            # Soft lexical penalty so strong anchor locks stay under threshold
            lex_penalty = _clamp((1.0 - overlap) * 2.5, 0.0, 4.0)
            penalties.append(lex_penalty)
            factors.append(f"DNA token overlap={overlap:.0%} (lex_penalty={lex_penalty})")

            if anchors:
                hit = sum(
                    1 for a in anchors if _anchor_hit(a, clip_text_lower, clip_toks)
                )
                miss = len(anchors) - hit
                if miss:
                    ap = min(3.0, float(miss))
                    penalties.append(ap)
                    factors.append(f"Anchors missed={miss}/{len(anchors)}")
                else:
                    # Credit full anchor lock — counters residual lexical gap
                    penalties.append(-0.75)
                    factors.append(f"All {len(anchors)} anchors present in prompt/recap")

        dna_refs = [str(r) for r in (dna.get("reference_image_ids") or []) if r]
        if dna_refs:
            if not ref_id:
                penalties.append(1.5)
                factors.append(
                    "DNA has reference_image_ids but clip has no reference_image_id"
                )
            elif ref_id not in dna_refs:
                penalties.append(2.0)
                factors.append(f"reference_image_id={ref_id} not in DNA refs {dna_refs}")
            else:
                factors.append(f"reference_image_id matches DNA ({ref_id})")
        elif ref_id:
            factors.append(f"reference_image_id={ref_id} (no DNA ref list)")

    if previous_clip is not None:
        prev_ref = (previous_clip.get("reference_image_id") or "").strip()
        if prev_ref and ref_id and prev_ref == ref_id:
            penalties.append(-0.5)
            factors.append("reference_image_id propagated from previous clip")
        elif prev_ref and ref_id and prev_ref != ref_id:
            penalties.append(1.5)
            factors.append(
                f"reference_image_id changed {prev_ref} → {ref_id} (ok if scene change)"
            )
        elif prev_ref and not ref_id:
            penalties.append(1.0)
            factors.append("Previous clip had reference_image_id; current missing")

    mode = "metadata"
    if reference_still_path and clip_still_path:
        frame_score = _optional_still_drift(reference_still_path, clip_still_path)
        if frame_score is not None:
            mode = "hybrid"
            penalties.append(frame_score)
            factors.append(f"still_compare_penalty={frame_score}")

    raw = sum(penalties)
    drift_score = _clamp(raw if raw > 0 else 0.0)
    if not prompt and not recap and not dna:
        drift_score = max(drift_score, 6.0)

    passed = drift_score < threshold
    return {
        "clip_id": clip.get("clip_id"),
        "drift_score": drift_score,
        "threshold": threshold,
        "pass": passed,
        "mode": mode,
        "factors": factors,
        "suggested_character_drift_boundary": _drift_to_qa_score(drift_score),
        "fixes": []
        if passed
        else [
            "Reinforce DNA anchors in prompt",
            "Restore reference_image_id from DNA / previous clip",
            "Re-lock identity before extend",
        ],
    }


def _drift_to_qa_score(drift_score: float) -> float:
    """Map drift 0–10 to chain QA character_drift_boundary 1–10 (higher=better)."""
    return round(max(1.0, min(10.0, 10.0 - drift_score)), 1)


def _optional_still_drift(ref_path: str, clip_path: str) -> float | None:
    """Return extra drift penalty 0–3 from mean abs pixel diff, or None if unavailable."""
    try:
        from PIL import Image
    except ImportError:
        return None
    try:
        a = Image.open(ref_path).convert("RGB").resize((64, 64))
        b = Image.open(clip_path).convert("RGB").resize((64, 64))
    except OSError:
        return None

    px_a = list(a.getdata())
    px_b = list(b.getdata())
    if not px_a or len(px_a) != len(px_b):
        return None

    mad = sum(abs(pa[i] - pb[i]) for pa, pb in zip(px_a, px_b) for i in range(3)) / (
        len(px_a) * 3 * 255.0
    )
    return round(min(3.0, mad * 6.0), 2)
