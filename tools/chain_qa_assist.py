#!/usr/bin/env python3
"""
Rule-based chain QA assist — pre-fills SFW 10-point and NSFW 8-point scores.

Vision/heuristic checklist from clip metadata, handoffs, and recap quality.
Human confirms or applies via --apply on CLI.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from nsfw_chain_qa import evaluate_nsfw_chain_qa
from sequence_chain import run_chain_qa

AssistResult = dict[str, Any]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _clamp(score: float) -> float:
    return round(max(1.0, min(10.0, score)), 1)


def _field_fill_ratio(data: dict[str, Any], keys: tuple[str, ...]) -> float:
    if not keys:
        return 1.0
    filled = sum(1 for k in keys if str(data.get(k, "")).strip())
    return filled / len(keys)


def _recap_score(recap: str, *, is_extend: bool) -> tuple[float, str]:
    text = (recap or "").strip()
    if not text:
        return (4.0 if is_extend else 6.0, "LAST_FRAME_RECAP missing" if is_extend else "Opening clip — recap optional")
    length = len(text)
    if length >= 80:
        return (9.0, f"Strong recap ({length} chars)")
    if length >= 40:
        return (7.5, f"Adequate recap ({length} chars)")
    return (5.5, f"Short recap ({length} chars) — add stitch detail")


def assist_sfw_chain_qa(
    clip: dict[str, Any],
    *,
    previous_clip: dict[str, Any] | None = None,
    sequence: dict[str, Any] | None = None,
) -> AssistResult:
    """Suggest SFW 10-point chain QA scores from metadata heuristics."""
    idx = clip.get("index", 0)
    is_extend = idx > 0
    recap = clip.get("last_frame_recap", "")
    mv = clip.get("momentum_vector") or {}
    amv = clip.get("audio_momentum_vector") or {}
    prompt = (clip.get("prompt") or "").strip()
    ref_id = (clip.get("reference_image_id") or "").strip()
    duration = clip.get("duration_seconds", 10)

    reasons: dict[str, str] = {}
    scores: dict[str, float] = {}

    recap_s, recap_r = _recap_score(recap, is_extend=is_extend)
    scores["last_frame_continuity"] = _clamp(recap_s + (1.0 if previous_clip and previous_clip.get("result_url") else 0))
    reasons["last_frame_continuity"] = recap_r

    mv_ratio = _field_fill_ratio(mv, ("last_action", "emotional_state", "camera_velocity", "lighting_state"))
    scores["momentum_carryover"] = _clamp(5.0 + mv_ratio * 5.0)
    reasons["momentum_carryover"] = f"Momentum vector {int(mv_ratio * 100)}% populated"

    amv_ratio = _field_fill_ratio(amv, ("dialogue_state", "sfx_timing", "emotional_tone_audio"))
    if amv_ratio == 0 and not is_extend:
        scores["audio_momentum_sync"] = 7.5
        reasons["audio_momentum_sync"] = "Opening clip — ambient/SFX seed optional"
    else:
        scores["audio_momentum_sync"] = _clamp(5.0 + amv_ratio * 4.5)
        reasons["audio_momentum_sync"] = f"Audio momentum {int(amv_ratio * 100)}% populated"

    if 6 <= duration <= 12:
        scores["physics_realism"] = 8.5
        reasons["physics_realism"] = f"Duration {duration}s in 1.5 sweet spot"
    elif duration < 6:
        scores["physics_realism"] = 6.5
        reasons["physics_realism"] = f"Duration {duration}s — very short, physics may compress"
    else:
        scores["physics_realism"] = 7.0
        reasons["physics_realism"] = f"Duration {duration}s — acceptable, watch stitch fatigue"

    if ref_id:
        scores["reference_propagation"] = 8.5
        reasons["reference_propagation"] = f"reference_image_id={ref_id}"
    else:
        scores["reference_propagation"] = 6.0 if is_extend else 7.0
        reasons["reference_propagation"] = "No reference_image_id — OK if deliberate scene change"

    if ref_id and mv.get("emotional_state"):
        scores["character_drift_boundary"] = 8.0
        reasons["character_drift_boundary"] = "Reference + emotional state locked"
    elif prompt:
        scores["character_drift_boundary"] = 7.0
        reasons["character_drift_boundary"] = "Prompt present — verify identity at stitch"
    else:
        scores["character_drift_boundary"] = 5.0
        reasons["character_drift_boundary"] = "Thin prompt — identity drift risk"

    if mv.get("lighting_state"):
        scores["lighting_color_match"] = 8.0
        reasons["lighting_color_match"] = "Lighting state documented in momentum"
    else:
        scores["lighting_color_match"] = 6.5
        reasons["lighting_color_match"] = "Add lighting_state to momentum vector"

    cont = clip.get("continuity_state") or {}
    if cont or recap:
        scores["prop_environment_state"] = 7.5
        reasons["prop_environment_state"] = "Continuity state or recap documents environment"
    else:
        scores["prop_environment_state"] = 6.0
        reasons["prop_environment_state"] = "continuity_state empty — verify props at boundary"

    if previous_clip:
        prev_qa = (previous_clip.get("chain_qa") or {}).get("decision")
        prev_status = previous_clip.get("status")
        if prev_qa == "go" or prev_status == "approved":
            scores["transition_readiness"] = 9.0
            reasons["transition_readiness"] = f"Previous {previous_clip['clip_id']} approved"
        elif prev_status in ("qa_pending", "generating"):
            scores["transition_readiness"] = 5.0
            reasons["transition_readiness"] = "Previous clip not yet approved"
        else:
            scores["transition_readiness"] = 6.0
            reasons["transition_readiness"] = f"Previous status={prev_status}"
    else:
        scores["transition_readiness"] = 8.0
        reasons["transition_readiness"] = "Opening clip — no prior transition"

    transition = clip.get("transition_to_next", "invisible_edit")
    if transition == "invisible_edit" and is_extend:
        scores["stitch_artifact_risk"] = 7.5
        reasons["stitch_artifact_risk"] = "Invisible edit extend — moderate morph risk"
    elif transition in ("dissolve", "hard_cut"):
        scores["stitch_artifact_risk"] = 8.5
        reasons["stitch_artifact_risk"] = f"{transition} masks boundary artifacts"
    else:
        scores["stitch_artifact_risk"] = 7.0
        reasons["stitch_artifact_risk"] = "Default stitch risk — review last frames"

    qa = run_chain_qa(clip, previous_clip=previous_clip, scores=scores)
    return {
        "mode": "sfw",
        "clip_id": clip["clip_id"],
        "evaluated_at": _now_iso(),
        "suggested_scores": scores,
        "reasons": reasons,
        "evaluation": qa,
        "confidence": _assist_confidence(scores, reasons),
        "sequence_slug": (sequence or {}).get("slug"),
    }


def assist_nsfw_chain_qa(
    clip: dict[str, Any],
    *,
    previous_clip: dict[str, Any] | None = None,
    sequence: dict[str, Any] | None = None,
) -> AssistResult:
    """Suggest NSFW 8-point artifact-aware scores from metadata heuristics."""
    prompt = (clip.get("prompt") or "").lower()
    recap = (clip.get("last_frame_recap") or "").strip()
    has_hands = any(w in prompt for w in ("hand", "finger", "touch", "grip"))
    close_body = any(w in prompt for w in ("close", "intimate", "skin", "explicit", "nude"))

    reasons: dict[str, str] = {}
    scores: dict[str, float] = {}

    if has_hands:
        scores["hand_finger_integrity"] = 6.0
        reasons["hand_finger_integrity"] = "Prompt mentions hands — verify digit integrity"
    else:
        scores["hand_finger_integrity"] = 8.5
        reasons["hand_finger_integrity"] = "No hand focus in prompt — lower artifact risk"

    scores["skin_texture_consistency"] = 8.0 if recap else 6.5
    reasons["skin_texture_consistency"] = "Recap documents skin state" if recap else "Add skin state to recap"

    if "fabric" in prompt or "cloth" in prompt:
        scores["fabric_cloth_physics"] = 7.0
        reasons["fabric_cloth_physics"] = "Fabric mentioned — verify drape at stitch"
    else:
        scores["fabric_cloth_physics"] = 8.0
        reasons["fabric_cloth_physics"] = "No fabric focus — default pass band"

    scores["explicit_area_artifact_risk"] = 6.0 if close_body else 8.0
    reasons["explicit_area_artifact_risk"] = (
        "Close body framing — pull back if morphing" if close_body else "Suggestive/moderate framing"
    )

    scores["body_proportion_stability"] = 7.5 if previous_clip else 8.0
    reasons["body_proportion_stability"] = "Check proportions at stitch boundary"

    beat = clip.get("nsfw_beat") or {}
    if beat.get("phase"):
        scores["intimate_physics_fidelity"] = 8.0
        reasons["intimate_physics_fidelity"] = f"Beat phase={beat.get('phase')} documented"
    else:
        scores["intimate_physics_fidelity"] = 6.5
        reasons["intimate_physics_fidelity"] = "Missing nsfw_beat phase metadata"

    if sequence and sequence.get("nsfw_extension", {}).get("tension_curve"):
        scores["erotic_tension_carryover"] = 8.0
        reasons["erotic_tension_carryover"] = "Tension curve present in sequence"
    else:
        scores["erotic_tension_carryover"] = 7.0
        reasons["erotic_tension_carryover"] = "Verify tension curve at boundary"

    if "rim" in prompt or "candle" in prompt or "warm" in prompt:
        scores["lighting_skin_modeling"] = 8.5
        reasons["lighting_skin_modeling"] = "Motivated warmth/rim in prompt"
    else:
        scores["lighting_skin_modeling"] = 7.0
        reasons["lighting_skin_modeling"] = "Add practical/rim warmth for skin"

    qa = evaluate_nsfw_chain_qa(clip, scores)
    return {
        "mode": "nsfw",
        "clip_id": clip["clip_id"],
        "evaluated_at": _now_iso(),
        "suggested_scores": scores,
        "reasons": reasons,
        "evaluation": qa,
        "confidence": _assist_confidence(scores, reasons),
        "sequence_slug": (sequence or {}).get("slug"),
    }


def _assist_confidence(scores: dict[str, float], reasons: dict[str, str]) -> str:
    low = sum(1 for s in scores.values() if s < 6.5)
    if low >= 3:
        return "low"
    if low >= 1:
        return "medium"
    return "high"


def assist_chain_qa(
    clip: dict[str, Any],
    *,
    previous_clip: dict[str, Any] | None = None,
    sequence: dict[str, Any] | None = None,
    nsfw: bool = False,
) -> AssistResult:
    if nsfw or (sequence or {}).get("nsfw_extension"):
        return assist_nsfw_chain_qa(clip, previous_clip=previous_clip, sequence=sequence)
    return assist_sfw_chain_qa(clip, previous_clip=previous_clip, sequence=sequence)


def summarize_sequence_qa(seq: dict[str, Any]) -> dict[str, Any]:
    """Unified SFW/NSFW chain QA summary for dashboard."""
    is_nsfw = bool(seq.get("nsfw_extension"))
    clips = seq.get("clips", [])
    rows: list[dict[str, Any]] = []
    for clip in clips:
        qa = clip.get("chain_qa") or clip.get("nsfw_chain_qa")
        assist = clip.get("chain_qa_assist")
        rows.append({
            "clip_id": clip["clip_id"],
            "status": clip.get("status"),
            "decision": (qa or {}).get("decision", "pending"),
            "weighted_score": (qa or {}).get("weighted_score"),
            "assist_confidence": (assist or {}).get("confidence"),
            "mode": "nsfw" if is_nsfw else "sfw",
        })
    decisions = [r["decision"] for r in rows if r["decision"] not in ("pending", "awaiting_scores")]
    return {
        "sequence_name": seq.get("sequence_name"),
        "slug": seq.get("slug"),
        "mode": "nsfw" if is_nsfw else "sfw",
        "clip_count": len(clips),
        "health": seq.get("sequence_health_score"),
        "chain_qa_status": seq.get("chain_qa_status"),
        "clips": rows,
        "go_count": sum(1 for d in decisions if d == "go"),
        "no_go_count": sum(1 for d in decisions if d == "no_go"),
    }


def apply_assisted_qa(
    seq: dict[str, Any],
    clip: dict[str, Any],
    *,
    previous_clip: dict[str, Any] | None = None,
    nsfw: bool = False,
) -> dict[str, Any]:
    """Run assist, store on clip, and evaluate official chain QA."""
    assist = assist_chain_qa(clip, previous_clip=previous_clip, sequence=seq, nsfw=nsfw)
    clip["chain_qa_assist"] = assist

    if nsfw or seq.get("nsfw_extension"):
        from nsfw_chain_qa import evaluate_nsfw_chain_qa
        qa = evaluate_nsfw_chain_qa(clip, assist["suggested_scores"])
        clip["nsfw_chain_qa"] = qa
        clip["chain_qa"] = qa
    else:
        qa = run_chain_qa(clip, previous_clip=previous_clip, scores=assist["suggested_scores"])
        clip["chain_qa"] = qa

    if qa["decision"] == "go":
        clip["status"] = "approved"
    elif qa["decision"] == "no_go":
        clip["status"] = "qa_hold"

    return {"assist": assist, "chain_qa": qa}