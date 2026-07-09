#!/usr/bin/env python3
"""
Audio momentum integrity scorer for extend/stitch boundaries (roadmap #6).

Diffs structured AUDIO_MOMENTUM_VECTOR fields between previous and current
clips (+ optional sequence memory bank audio). Metadata only — no waveform.

integrity_score: 1–10 higher = better continuity.
pass: integrity_score >= AMV_PASS_THRESHOLD (7.0).
"""

from __future__ import annotations

import re
from typing import Any

AMV_PASS_THRESHOLD = 7.0
AMV_KEYS = (
    "dialogue_state",
    "sfx_timing",
    "emotional_tone_audio",
    "music_cue_points",
    "lip_sync_state",
)

_TOKEN_RE = re.compile(r"[a-z0-9']+")

# Penalties (subtract from 10.0 on extend)
_PENALTY_DIALOGUE_DROPPED = 2.5
_PENALTY_SFX_GAP = 1.5
_PENALTY_TONE_DROP = 1.0
_PENALTY_MUSIC_CLEARED = 1.5
_PENALTY_LIP_SYNC = 1.0
_PENALTY_AMV_EMPTY_EXTEND = 2.0
_PENALTY_DIALOGUE_WEAK_OVERLAP = 0.5
_PENALTY_BANK_DIALOGUE = 1.0


def _tokens(text: str) -> set[str]:
    return {t for t in _TOKEN_RE.findall((text or "").lower()) if len(t) > 2}


def _clamp(score: float, lo: float = 1.0, hi: float = 10.0) -> float:
    return round(max(lo, min(hi, score)), 2)


def _filled(val: Any) -> bool:
    if isinstance(val, list):
        return any(str(x).strip() for x in val)
    return bool(str(val or "").strip())


def _amv(clip: dict[str, Any] | None) -> dict[str, Any]:
    if not clip:
        return {k: ([] if k == "music_cue_points" else "") for k in AMV_KEYS}
    raw = clip.get("audio_momentum_vector") or {}
    return {
        "dialogue_state": raw.get("dialogue_state", "") or "",
        "sfx_timing": raw.get("sfx_timing", "") or "",
        "emotional_tone_audio": raw.get("emotional_tone_audio", "") or "",
        "music_cue_points": list(raw.get("music_cue_points") or []),
        "lip_sync_state": raw.get("lip_sync_state", "") or "",
    }


def _amv_entirely_empty(amv: dict[str, Any]) -> bool:
    return all(not _filled(amv.get(k)) for k in AMV_KEYS)


def _any_amv_filled(amv: dict[str, Any]) -> bool:
    return any(_filled(amv.get(k)) for k in AMV_KEYS)


def _field_status_str(prev_val: Any, curr_val: Any) -> str:
    pf, cf = _filled(prev_val), _filled(curr_val)
    if not pf and not cf:
        return "empty"
    if pf and not cf:
        return "dropped"
    if not pf and cf:
        return "ok"
    # both filled
    if isinstance(prev_val, list) or isinstance(curr_val, list):
        prev_norm = sorted(str(x).strip().lower() for x in (prev_val or []) if str(x).strip())
        curr_norm = sorted(str(x).strip().lower() for x in (curr_val or []) if str(x).strip())
        return "ok" if prev_norm == curr_norm else "changed"
    a = str(prev_val).strip().lower()
    b = str(curr_val).strip().lower()
    if a == b:
        return "ok"
    at, bt = _tokens(a), _tokens(b)
    if at and bt and (at & bt or a in b or b in a):
        return "ok"
    return "changed"


def _music_field_status(prev_cues: list, curr_cues: list) -> str:
    pf, cf = _filled(prev_cues), _filled(curr_cues)
    if not pf and not cf:
        return "empty"
    if pf and not cf:
        return "cleared"
    if not pf and cf:
        return "ok"
    prev_norm = sorted(str(x).strip().lower() for x in prev_cues if str(x).strip())
    curr_norm = sorted(str(x).strip().lower() for x in curr_cues if str(x).strip())
    return "ok" if prev_norm == curr_norm else "changed"


def build_audio_momentum_report(
    clip: dict[str, Any],
    *,
    previous_clip: dict[str, Any] | None = None,
    memory_bank: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Score AMV integrity for a clip against previous stitch + optional bank audio.

    Returns integrity_score (1–10), pass, factors, fixes, field_status,
    and suggested_audio_momentum_sync for Chain QA Assist.
    """
    curr = _amv(clip)
    factors: list[str] = []
    fixes: list[str] = []
    field_status: dict[str, str] = {}

    # --- Opening (no previous) ---
    if previous_clip is None:
        factors.append("Opening clip — no prior AMV stitch")
        for k in AMV_KEYS:
            if k == "music_cue_points":
                field_status[k] = "ok" if _filled(curr.get(k)) else "empty"
            else:
                field_status[k] = "ok" if _filled(curr.get(k)) else "empty"
        score = 8.0 if _any_amv_filled(curr) else 7.0
        score = _clamp(score)
        return {
            "clip_id": clip.get("clip_id"),
            "previous_clip_id": None,
            "integrity_score": score,
            "pass": score >= AMV_PASS_THRESHOLD,
            "mode": "metadata",
            "factors": factors,
            "fixes": fixes,
            "field_status": field_status,
            "suggested_audio_momentum_sync": score,
        }

    # --- Extend (previous present) ---
    prev = _amv(previous_clip)
    score = 10.0

    # dialogue_state
    if _filled(prev.get("dialogue_state")) and not _filled(curr.get("dialogue_state")):
        score -= _PENALTY_DIALOGUE_DROPPED
        factors.append("dialogue_state dropped")
        fixes.append("Restore dialogue_state from previous clip / bank")
        field_status["dialogue_state"] = "dropped"
    else:
        field_status["dialogue_state"] = _field_status_str(
            prev.get("dialogue_state"), curr.get("dialogue_state")
        )
        if (
            _filled(prev.get("dialogue_state"))
            and _filled(curr.get("dialogue_state"))
        ):
            pt = _tokens(str(prev.get("dialogue_state")))
            ct = _tokens(str(curr.get("dialogue_state")))
            if pt and ct and not (pt & ct):
                # both long enough to imply weak continuity
                if len(pt) >= 2 and len(ct) >= 2:
                    score -= _PENALTY_DIALOGUE_WEAK_OVERLAP
                    factors.append("weak dialogue continuity (no shared tokens)")

    # sfx_timing
    if _filled(prev.get("sfx_timing")) and not _filled(curr.get("sfx_timing")):
        score -= _PENALTY_SFX_GAP
        factors.append("sfx_timing gap")
        fixes.append("Carry sfx_timing across stitch boundary")
        field_status["sfx_timing"] = "dropped"
    else:
        field_status["sfx_timing"] = _field_status_str(
            prev.get("sfx_timing"), curr.get("sfx_timing")
        )

    # emotional_tone_audio
    if _filled(prev.get("emotional_tone_audio")) and not _filled(
        curr.get("emotional_tone_audio")
    ):
        score -= _PENALTY_TONE_DROP
        factors.append("emotional_tone_audio dropped")
        fixes.append("Preserve emotional_tone_audio from previous clip")
        field_status["emotional_tone_audio"] = "dropped"
    else:
        field_status["emotional_tone_audio"] = _field_status_str(
            prev.get("emotional_tone_audio"), curr.get("emotional_tone_audio")
        )

    # music_cue_points
    prev_music = prev.get("music_cue_points") or []
    curr_music = curr.get("music_cue_points") or []
    if _filled(prev_music) and not _filled(curr_music):
        score -= _PENALTY_MUSIC_CLEARED
        factors.append("music_cue_points cleared")
        fixes.append("Propagate music_cue_points or mark intentional silence")
        field_status["music_cue_points"] = "cleared"
    else:
        field_status["music_cue_points"] = _music_field_status(prev_music, curr_music)

    # lip_sync_state
    if _filled(prev.get("lip_sync_state")) and not _filled(curr.get("lip_sync_state")):
        score -= _PENALTY_LIP_SYNC
        factors.append("lip_sync_state dropped")
        fixes.append("Carry lip_sync_state for dialogue continuity")
        field_status["lip_sync_state"] = "dropped"
    else:
        field_status["lip_sync_state"] = _field_status_str(
            prev.get("lip_sync_state"), curr.get("lip_sync_state")
        )

    # Entire AMV empty on extend
    if _amv_entirely_empty(curr):
        score -= _PENALTY_AMV_EMPTY_EXTEND
        factors.append("AMV empty on extend clip")
        fixes.append("Fill AUDIO_MOMENTUM_VECTOR on extend clip before stitch")

    # Memory bank dialogue
    bank_audio: dict[str, Any] = {}
    if memory_bank and isinstance(memory_bank, dict):
        bank_audio = memory_bank.get("audio") or {}
    bank_dialogue = (bank_audio.get("dialogue_state") or "") if isinstance(bank_audio, dict) else ""
    if _filled(bank_dialogue) and not _filled(curr.get("dialogue_state")):
        score -= _PENALTY_BANK_DIALOGUE
        factors.append("bank dialogue not on clip")
        fixes.append("Inject memory bank dialogue_state onto current clip AMV")
        if field_status.get("dialogue_state") not in ("dropped",):
            field_status["dialogue_state"] = "empty"

    if not factors:
        factors.append("AMV fields preserved across stitch")

    score = _clamp(score)
    passed = score >= AMV_PASS_THRESHOLD

    if not passed and not fixes:
        fixes.append("Restore dropped AMV fields from previous clip before re-gen")

    return {
        "clip_id": clip.get("clip_id"),
        "previous_clip_id": previous_clip.get("clip_id"),
        "integrity_score": score,
        "pass": passed,
        "mode": "metadata",
        "factors": factors,
        "fixes": fixes,
        "field_status": field_status,
        "suggested_audio_momentum_sync": score,
    }
