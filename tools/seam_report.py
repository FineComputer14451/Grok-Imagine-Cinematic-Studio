#!/usr/bin/env python3
"""
Last-frame seam report for extend/stitch (roadmap #2).

seam_risk: 0–10 higher = worse seam.
pass: seam_risk < 5.0 (moderate gate; chain QA still final).
v1: metadata heuristics; optional frame paths for hybrid mode via soft PIL import.
"""

from __future__ import annotations

import re
from typing import Any

_TOKEN_RE = re.compile(r"[a-z0-9']+")
SEAM_PASS_THRESHOLD = 5.0

_MOMENTUM_KEYS = (
    "last_action",
    "emotional_state",
    "camera_velocity",
    "lighting_state",
    "physics_state",
)


def _tokens(text: str) -> set[str]:
    return {t for t in _TOKEN_RE.findall((text or "").lower()) if len(t) > 2}


def _clamp(x: float, lo: float = 0.0, hi: float = 10.0) -> float:
    return round(max(lo, min(hi, x)), 2)


def build_seam_report(
    clip: dict[str, Any],
    *,
    previous_clip: dict[str, Any] | None = None,
    previous_last_frame_path: str | None = None,
    current_first_frame_path: str | None = None,
) -> dict[str, Any]:
    """
    Score stitch-boundary seam risk for a clip against the previous clip.

    Optional frame paths enable hybrid mode when PIL can load both images
    (64×64 mean absolute difference).
    """
    factors: list[str] = []
    risk_parts: list[float] = []
    fixes: list[str] = []
    idx = int(clip.get("index") or 0)
    is_extend = idx > 0 or previous_clip is not None

    if not is_extend or previous_clip is None:
        factors.append("Opening clip — no stitch boundary")
        return {
            "clip_id": clip.get("clip_id"),
            "seam_risk": 2.0,
            "pass": True,
            "mode": "metadata",
            "factors": factors,
            "fixes": [],
            "suggested_scores": {
                "last_frame_continuity": 8.5,
                "physics_realism": 8.0,
                "stitch_artifact_risk": 8.5,
                "lighting_color_match": 8.0,
            },
        }

    prev_recap = (previous_clip.get("last_frame_recap") or "").strip()
    curr_recap = (clip.get("last_frame_recap") or "").strip()
    prev_mv = previous_clip.get("momentum_vector") or {}
    curr_mv = clip.get("momentum_vector") or {}

    if not prev_recap:
        risk_parts.append(3.5)
        factors.append("Previous LAST_FRAME_RECAP missing")
        fixes.append("Capture LAST_FRAME_RECAP on previous clip before extend")
    else:
        factors.append(f"Previous recap length={len(prev_recap)}")

    if not curr_recap and is_extend:
        risk_parts.append(1.5)
        factors.append("Current clip recap empty")
        fixes.append("Document expected end state on current clip")

    if prev_recap and curr_recap:
        pt, ct = _tokens(prev_recap), _tokens(curr_recap)
        if pt and ct:
            overlap = len(pt & ct) / max(1, len(pt))
            # Low overlap between prev end and current end-state → higher risk
            risk_parts.append(_clamp((1.0 - overlap) * 2.5, 0.0, 2.5))
            factors.append(f"Recap token overlap vs previous={overlap:.0%}")
        prompt_toks = _tokens(clip.get("prompt") or "")
        if pt and prompt_toks:
            po = len(pt & prompt_toks) / max(1, len(pt))
            # Secondary signal: prompt should pick up from prev end
            risk_parts.append(_clamp((1.0 - po) * 1.0, 0.0, 1.0))
            factors.append(f"Prompt vs prev recap overlap={po:.0%}")

    filled_prev = sum(1 for k in _MOMENTUM_KEYS if str(prev_mv.get(k, "")).strip())
    filled_curr = sum(1 for k in _MOMENTUM_KEYS if str(curr_mv.get(k, "")).strip())
    if filled_prev < 3:
        risk_parts.append(1.5)
        factors.append(f"Previous momentum sparse ({filled_prev}/5)")
        fixes.append("Fill momentum_vector on previous clip")
    if filled_curr < 3:
        risk_parts.append(1.0)
        factors.append(f"Current momentum sparse ({filled_curr}/5)")

    matches = 0
    compared = 0
    for k in _MOMENTUM_KEYS:
        a = str(prev_mv.get(k, "")).strip().lower()
        b = str(curr_mv.get(k, "")).strip().lower()
        if a and b:
            compared += 1
            at, bt = _tokens(a), _tokens(b)
            if at & bt or a in b or b in a:
                matches += 1
    if compared:
        match_ratio = matches / compared
        if match_ratio >= 0.8:
            # Strong carry-over reduces seam risk (credit)
            credit = -2.0 if match_ratio >= 1.0 else -1.5
            risk_parts.append(credit)
            factors.append(
                f"Momentum field agreement={match_ratio:.0%} ({matches}/{compared})"
            )
        else:
            risk_parts.append(_clamp((1.0 - match_ratio) * 3.0, 0.0, 3.0))
            factors.append(
                f"Momentum field agreement={match_ratio:.0%} ({matches}/{compared})"
            )
    else:
        risk_parts.append(1.0)
        factors.append("No paired momentum fields to compare")

    transition = (
        clip.get("transition_to_next")
        or previous_clip.get("transition_to_next")
        or "invisible_edit"
    )
    if transition == "invisible_edit":
        risk_parts.append(0.8)
        factors.append("invisible_edit — higher morph risk at boundary")
    elif transition in ("dissolve", "hard_cut"):
        risk_parts.append(-0.5)
        factors.append(f"{transition} masks boundary")

    mode = "metadata"
    if previous_last_frame_path and current_first_frame_path:
        fr = _optional_frame_seam(previous_last_frame_path, current_first_frame_path)
        if fr is not None:
            mode = "hybrid"
            risk_parts.append(fr)
            factors.append(f"frame_mad_penalty={fr}")

    seam_risk = _clamp(sum(risk_parts))
    passed = seam_risk < SEAM_PASS_THRESHOLD

    # Map to QA score suggestions (higher = better)
    cont = _clamp(10.0 - seam_risk, 1.0, 10.0)
    stitch = _clamp(10.0 - seam_risk * 0.9, 1.0, 10.0)
    physics = _clamp(9.0 - max(0.0, seam_risk - 2.0) * 0.5, 1.0, 10.0)
    lighting = (
        8.0
        if str(prev_mv.get("lighting_state", "")).strip()
        and str(curr_mv.get("lighting_state", "")).strip()
        else 6.5
    )

    if not passed and not fixes:
        fixes.append("Strengthen LAST_FRAME_RECAP and momentum carry-over before re-gen")

    return {
        "clip_id": clip.get("clip_id"),
        "previous_clip_id": previous_clip.get("clip_id"),
        "seam_risk": seam_risk,
        "pass": passed,
        "mode": mode,
        "factors": factors,
        "fixes": fixes,
        "suggested_scores": {
            "last_frame_continuity": round(cont, 1),
            "physics_realism": round(physics, 1),
            "stitch_artifact_risk": round(stitch, 1),
            "lighting_color_match": round(lighting, 1),
        },
    }


def _optional_frame_seam(prev_path: str, curr_path: str) -> float | None:
    """Return extra seam penalty 0–4 from mean abs pixel diff, or None if unavailable."""
    try:
        from PIL import Image
    except ImportError:
        return None
    try:
        a = Image.open(prev_path).convert("RGB").resize((64, 64))
        b = Image.open(curr_path).convert("RGB").resize((64, 64))
    except OSError:
        return None
    px_a, px_b = list(a.getdata()), list(b.getdata())
    if len(px_a) != len(px_b) or not px_a:
        return None
    mad = sum(abs(pa[i] - pb[i]) for pa, pb in zip(px_a, px_b) for i in range(3)) / (
        len(px_a) * 3 * 255.0
    )
    return round(min(4.0, mad * 8.0), 2)
