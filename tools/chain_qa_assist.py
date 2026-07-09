#!/usr/bin/env python3
"""
Rule-based chain QA assist — pre-fills SFW 10-point and NSFW 8-point scores.

Vision/heuristic checklist from clip metadata, handoffs, and recap quality.
Human confirms or applies via --apply on CLI.

v2: blends identity_drift + seam_report evidence into SFW scores.
v3: overlays audio_momentum integrity into audio_momentum_sync.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from audio_momentum import build_audio_momentum_report
from identity_drift import score_identity_drift
from nsfw_chain_qa import evaluate_nsfw_chain_qa
from seam_report import build_seam_report
from sequence_chain import run_chain_qa

AssistResult = dict[str, Any]

_EVIDENCE_PATH_KEYS = frozenset({
    "previous_last_frame_path",
    "current_first_frame_path",
    "reference_still_path",
    "clip_still_path",
})


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
    dna: dict[str, Any] | None = None,
    previous_last_frame_path: str | None = None,
    current_first_frame_path: str | None = None,
    reference_still_path: str | None = None,
    clip_still_path: str | None = None,
) -> AssistResult:
    """Suggest SFW 10-point chain QA scores from metadata heuristics + evidence."""
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

    # --- Evidence loop v2/v3: identity drift + seam + audio momentum ---
    drift = score_identity_drift(
        clip,
        dna=dna,
        previous_clip=previous_clip,
        reference_still_path=reference_still_path,
        clip_still_path=clip_still_path,
    )
    seam = build_seam_report(
        clip,
        previous_clip=previous_clip,
        previous_last_frame_path=previous_last_frame_path,
        current_first_frame_path=current_first_frame_path,
    )
    amv_report = build_audio_momentum_report(
        clip,
        previous_clip=previous_clip,
        memory_bank=(sequence or {}).get("memory_bank"),
    )

    scores["character_drift_boundary"] = drift["suggested_character_drift_boundary"]
    reasons["character_drift_boundary"] = (
        f"drift_score={drift['drift_score']} (threshold={drift['threshold']}); "
        + "; ".join(drift["factors"][:2])
    )

    for key, val in seam.get("suggested_scores", {}).items():
        if key in scores:
            blended = round((scores[key] + float(val)) / 2.0, 1)
            scores[key] = _clamp(blended)
            seam_note = seam["factors"][0] if seam.get("factors") else "n/a"
            reasons[key] = f"{reasons.get(key, '')}; seam:{seam_note}"[:200]

    scores["audio_momentum_sync"] = amv_report["suggested_audio_momentum_sync"]
    amv_note = amv_report["factors"][0] if amv_report.get("factors") else "n/a"
    reasons["audio_momentum_sync"] = (
        f"integrity={amv_report['integrity_score']} pass={amv_report['pass']}; {amv_note}"
    )[:200]

    # If drift failed hard, ensure critical identity stays low enough to matter
    if not drift["pass"]:
        scores["character_drift_boundary"] = min(
            scores["character_drift_boundary"],
            drift["suggested_character_drift_boundary"],
        )

    qa = run_chain_qa(clip, previous_clip=previous_clip, scores=scores)
    if not drift["pass"]:
        qa.setdefault("fixes", []).extend(drift.get("fixes") or [])
    if not seam["pass"]:
        qa.setdefault("fixes", []).extend(seam.get("fixes") or [])
    if not amv_report["pass"]:
        qa.setdefault("fixes", []).extend(amv_report.get("fixes") or [])

    return {
        "mode": "sfw",
        "clip_id": clip["clip_id"],
        "evaluated_at": _now_iso(),
        "suggested_scores": scores,
        "reasons": reasons,
        "evaluation": qa,
        "confidence": _assist_confidence_v2(scores, reasons, drift, seam),
        "sequence_slug": (sequence or {}).get("slug"),
        "evidence": {
            "identity_drift": drift,
            "seam_report": seam,
            "audio_momentum": amv_report,
        },
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


def _assist_confidence_v2(
    scores: dict[str, float],
    reasons: dict[str, str],
    drift: dict[str, Any],
    seam: dict[str, Any],
) -> str:
    """Confidence with evidence-loop dampening (metadata-only cannot claim high)."""
    base = _assist_confidence(scores, reasons)
    if not drift.get("pass") or not seam.get("pass"):
        return "low"
    if drift.get("mode") == "metadata" and seam.get("mode") == "metadata":
        if base == "high":
            return "medium"
    return base


def assist_chain_qa(
    clip: dict[str, Any],
    *,
    previous_clip: dict[str, Any] | None = None,
    sequence: dict[str, Any] | None = None,
    nsfw: bool = False,
    dna: dict[str, Any] | None = None,
    **evidence_paths: Any,
) -> AssistResult:
    if nsfw or (sequence or {}).get("nsfw_extension"):
        # NSFW path: keep existing score heuristics; attach evidence only
        result = assist_nsfw_chain_qa(clip, previous_clip=previous_clip, sequence=sequence)
        drift = score_identity_drift(
            clip,
            dna=dna,
            previous_clip=previous_clip,
            reference_still_path=evidence_paths.get("reference_still_path"),
            clip_still_path=evidence_paths.get("clip_still_path"),
        )
        seam = build_seam_report(
            clip,
            previous_clip=previous_clip,
            previous_last_frame_path=evidence_paths.get("previous_last_frame_path"),
            current_first_frame_path=evidence_paths.get("current_first_frame_path"),
        )
        amv_report = build_audio_momentum_report(
            clip,
            previous_clip=previous_clip,
            memory_bank=(sequence or {}).get("memory_bank"),
        )
        result["evidence"] = {
            "identity_drift": drift,
            "seam_report": seam,
            "audio_momentum": amv_report,
        }
        return result
    return assist_sfw_chain_qa(
        clip,
        previous_clip=previous_clip,
        sequence=sequence,
        dna=dna,
        **{k: v for k, v in evidence_paths.items() if k in _EVIDENCE_PATH_KEYS},
    )


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
    dna: dict[str, Any] | None = None,
    **evidence_paths: Any,
) -> dict[str, Any]:
    """Run assist, store on clip, and evaluate official chain QA."""
    assist = assist_chain_qa(
        clip,
        previous_clip=previous_clip,
        sequence=seq,
        nsfw=nsfw,
        dna=dna,
        **{k: v for k, v in evidence_paths.items() if k in _EVIDENCE_PATH_KEYS},
    )
    clip["chain_qa_assist"] = assist
    clip["identity_drift"] = assist.get("evidence", {}).get("identity_drift")
    clip["seam_report"] = assist.get("evidence", {}).get("seam_report")
    clip["audio_momentum_report"] = assist.get("evidence", {}).get("audio_momentum")

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
