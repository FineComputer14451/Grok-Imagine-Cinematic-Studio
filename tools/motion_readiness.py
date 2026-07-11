#!/usr/bin/env python3
"""Motion brief readiness — structured MOTION_VECTOR before video spend."""

from __future__ import annotations

from typing import Any

from handoff_schema import is_video_execution_mode
from plate_readiness import resolve_execution_mode

# Shared free-text cues (GHR-03 fallback). Canonical list lives here.
MOTION_CUES = (
    "motion",
    "camera",
    "dolly",
    "pan",
    "tilt",
    "track",
    "ken burns",
    "first frame",
    "i2v",
    "extend",
    "momentum",
    "lip-sync",
    "lip sync",
    "physics",
)

MOTION_TRIPLE_KEYS: tuple[str, ...] = ("action", "camera", "emotion")
MOTION_TIERS = frozenset({"micro", "medium", "kinetic"})
MOTION_BLOCK_KEYS = ("motion_vector", "i2v_motion_block", "motion_block")


def _has_cue(text: str, cues: tuple[str, ...] = MOTION_CUES) -> bool:
    low = (text or "").lower()
    return any(c in low for c in cues)


def normalize_motion_tier(raw: Any) -> str | None:
    if raw is None:
        return None
    s = str(raw).strip().lower()
    if s in MOTION_TIERS:
        return s
    aliases = {
        "low": "micro",
        "subtle": "micro",
        "high": "kinetic",
        "aggressive": "kinetic",
        "med": "medium",
    }
    return aliases.get(s)


def extract_motion_vector(subject: dict[str, Any] | None) -> dict[str, str]:
    """Return normalized action/camera/emotion strings (may be empty)."""
    subj = subject if isinstance(subject, dict) else {}
    out = {k: "" for k in MOTION_TRIPLE_KEYS}
    for key in MOTION_BLOCK_KEYS:
        val = subj.get(key)
        if not isinstance(val, dict):
            continue
        for k in MOTION_TRIPLE_KEYS:
            # accept common aliases inside dict
            raw = val.get(k)
            if raw is None and k == "action":
                raw = val.get("last_action") or val.get("subject")
            if raw is None and k == "camera":
                raw = val.get("camera_velocity") or val.get("camera_move")
            if raw is None and k == "emotion":
                raw = val.get("emotional_state") or val.get("emotion_state")
            if raw is not None and str(raw).strip():
                out[k] = str(raw).strip()
        if any(out.values()):
            break
    return out


def is_complete_motion_triple(motion_vector: dict[str, str] | None) -> bool:
    if not isinstance(motion_vector, dict):
        return False
    return all(str(motion_vector.get(k) or "").strip() for k in MOTION_TRIPLE_KEYS)


def has_free_text_motion(subject: dict[str, Any] | None) -> bool:
    subj = subject if isinstance(subject, dict) else {}
    text = " ".join(
        str(subj.get(k) or "")
        for k in ("prompt", "description", "last_prompt", "i2v_prompt")
    )
    return _has_cue(text)


def build_motion_vector(
    *,
    action: str,
    camera: str,
    emotion: str,
    motion_tier: str | None = None,
) -> dict[str, Any]:
    """Build a canonical motion_vector (+ optional tier wrapper fields)."""
    mv = {
        "action": (action or "").strip(),
        "camera": (camera or "").strip(),
        "emotion": (emotion or "").strip(),
    }
    tier = normalize_motion_tier(motion_tier)
    if tier:
        return {"motion_vector": mv, "motion_tier": tier}
    return {"motion_vector": mv}


def evaluate_motion_brief_readiness(
    subject: dict[str, Any] | None,
    *,
    execution_mode: str | None = None,
    strict: bool = False,
) -> dict[str, Any]:
    """
    Structured motion brief readiness for video spend.

    Soft (strict=False):
      - complete triple → pass
      - free-text cues only → pass + warning MB-01
      - neither → blocker MB-03
    Strict (strict=True):
      - complete triple required; free-text alone → blocker MB-02
    """
    subj = subject if isinstance(subject, dict) else {}
    mode = resolve_execution_mode(subj, execution_mode=execution_mode)
    warnings: list[str] = []
    blockers: list[str] = []
    fixes: list[str] = []
    checks: list[dict[str, Any]] = []

    mv = extract_motion_vector(subj)
    complete = is_complete_motion_triple(mv)
    free_text = has_free_text_motion(subj)
    tier = normalize_motion_tier(subj.get("motion_tier"))

    checks.append(
        {
            "id": "motion_vector",
            "complete_triple": complete,
            "free_text": free_text,
            "fields": mv,
            "motion_tier": tier,
            "mode": mode,
            "strict": strict,
        }
    )

    if not is_video_execution_mode(mode):
        return {
            "pass": True,
            "strict": strict,
            "skipped": True,
            "warnings": warnings,
            "blockers": blockers,
            "fixes": fixes,
            "checks": checks,
            "motion_vector": mv,
            "complete_triple": complete,
            "execution_mode": mode,
        }

    if complete:
        if not tier:
            warnings.append(
                "MB-04: motion_tier unset (optional micro|medium|kinetic)"
            )
        return {
            "pass": True,
            "strict": strict,
            "skipped": False,
            "warnings": warnings,
            "blockers": blockers,
            "fixes": fixes,
            "checks": checks,
            "motion_vector": mv,
            "complete_triple": True,
            "execution_mode": mode,
        }

    missing = [k for k in MOTION_TRIPLE_KEYS if not mv.get(k)]
    fix_cli = (
        'sfw motion set <batch> <shot> --action "…" --camera "…" --emotion "…"'
    )

    if free_text and not strict:
        warnings.append(
            "MB-01: motion brief unstructured — free-text cues only; "
            f"prefer full MOTION_VECTOR (missing: {', '.join(missing) or 'all'})"
        )
        fixes.append(fix_cli)
        return {
            "pass": True,
            "strict": strict,
            "skipped": False,
            "warnings": warnings,
            "blockers": blockers,
            "fixes": fixes,
            "checks": checks,
            "motion_vector": mv,
            "complete_triple": False,
            "execution_mode": mode,
        }

    if free_text and strict:
        blockers.append(
            "MB-02: --strict-motion requires complete motion_vector "
            f"{{action, camera, emotion}} (missing: {', '.join(missing)}); "
            "free-text cues are not enough"
        )
        fixes.append(fix_cli)
    else:
        blockers.append(
            "MB-03: video mode lacks structured motion_vector and free-text "
            "motion/I2V cues (e.g. dolly, first frame, momentum)"
        )
        fixes.append(
            f"Activate I2V Specialist; {fix_cli} "
            "or add MOTION_VECTOR language to prompt"
        )

    return {
        "pass": len(blockers) == 0,
        "strict": strict,
        "skipped": False,
        "warnings": warnings,
        "blockers": blockers,
        "fixes": fixes,
        "checks": checks,
        "motion_vector": mv,
        "complete_triple": False,
        "execution_mode": mode,
    }
