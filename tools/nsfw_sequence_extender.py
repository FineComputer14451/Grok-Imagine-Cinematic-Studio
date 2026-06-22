#!/usr/bin/env python3
"""
NSFW Sequence Extender — sensual long-form extension from reference frame or short clip.

Integrates with:
  - sequence_chain.py (1.5 extend/stitch, chain QA)
  - nsfw_orchestrator.py (quota planning)
  - ErosForge protocols (intimacy physics, post-scene state)
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from models import DEFAULT_IMAGINE_VIDEO_MODEL
from nsfw_orchestrator import estimate_shot_cost
from quota_optimizer import estimate_sequence_cost
from sequence_chain import (
    DEFAULT_PIPELINE,
    build_extend_prompt,
    build_handoff_from_clip,
    create_clip,
    create_sequence_scaffold,
    save_sequence,
    slugify,
)

SCHEMA_VERSION = "1.0"
NSFW_SEQUENCES_TAG = "nsfw_erotic_extension"

TENSION_PROFILES: dict[str, dict[str, Any]] = {
    "slow_burn": {
        "label": "Slow Burn",
        "clip_duration_range": (10, 14),
        "phase_weights": {
            "anticipation": 0.25,
            "approach": 0.20,
            "contact": 0.20,
            "escalation": 0.15,
            "peak": 0.12,
            "afterglow": 0.08,
        },
        "camera_style": "lingering holds, shallow DOF, minimal camera movement",
    },
    "passionate": {
        "label": "Passionate",
        "clip_duration_range": (8, 12),
        "phase_weights": {
            "anticipation": 0.15,
            "approach": 0.18,
            "contact": 0.22,
            "escalation": 0.22,
            "peak": 0.15,
            "afterglow": 0.08,
        },
        "camera_style": "push-ins on breath beats, orbit on contact, match cuts",
    },
    "intense": {
        "label": "Intense",
        "clip_duration_range": (6, 10),
        "phase_weights": {
            "anticipation": 0.10,
            "approach": 0.15,
            "contact": 0.25,
            "escalation": 0.25,
            "peak": 0.18,
            "afterglow": 0.07,
        },
        "camera_style": "handheld intimacy, whip-free closeups, rhythmic dolly pulses",
    },
}

EROTIC_PHASES: dict[str, dict[str, Any]] = {
    "anticipation": {
        "label": "Anticipation",
        "tension": 0.2,
        "motion_intensity": "low",
        "description": "Establish desire, proximity building, held breath",
    },
    "approach": {
        "label": "Approach",
        "tension": 0.4,
        "motion_intensity": "low-medium",
        "description": "First touch approaching, eye contact, micro-expressions",
    },
    "contact": {
        "label": "Contact",
        "tension": 0.55,
        "motion_intensity": "medium",
        "description": "Skin contact, fabric displacement begins, breath sync",
    },
    "escalation": {
        "label": "Escalation",
        "tension": 0.75,
        "motion_intensity": "medium-high",
        "description": "Intimate movement intensifies, weight transfer, momentum",
    },
    "peak": {
        "label": "Peak",
        "tension": 0.95,
        "motion_intensity": "high",
        "description": "Key explicit narrative beat — hero moment of sequence",
    },
    "afterglow": {
        "label": "Afterglow",
        "tension": 0.35,
        "motion_intensity": "low",
        "description": "Deceleration, emotional residue, soft resolution",
    },
}

CAMERA_MOVES: dict[str, dict[str, Any]] = {
    "anticipation": {
        "primary": "static_hold",
        "options": ["slow_dolly_in", "subtle_crane_down", "rack_focus_eyes"],
        "lens": "50mm f/1.4",
        "framing": "medium close-up, negative space between bodies",
        "pacing_note": "Hold 3–4s before any camera move — let tension breathe",
    },
    "approach": {
        "primary": "slow_dolly_in",
        "options": ["orbit_15deg", "over_shoulder_intimate", "low_angle_up"],
        "lens": "35mm f/1.8",
        "framing": "over-shoulder or profile two-shot, shrinking distance",
        "pacing_note": "Dolly speed: 2cm/s — weighty, deliberate approach",
    },
    "contact": {
        "primary": "orbit_slow",
        "options": ["handheld_subtle", "macro_skin_detail", "match_cut_hands"],
        "lens": "85mm f/1.4",
        "framing": "close on contact point — hands, lips, collarbone",
        "pacing_note": "One primary contact per clip; avoid multi-focus",
    },
    "escalation": {
        "primary": "tracking_medium",
        "options": ["dolly_push_weight_transfer", "crane_reveal", "dutch_subtle"],
        "lens": "40mm anamorphic feel",
        "framing": "medium full, body lines visible, motivated shadows",
        "pacing_note": "Camera follows momentum vector — never fights body physics",
    },
    "peak": {
        "primary": "hero_push_in",
        "options": ["slow_motion_80pct", "extreme_close_texture", "silhouette_rim"],
        "lens": "50mm or 85mm — hero lens choice locked",
        "framing": "hero framing — single body focus or intimate two-shot",
        "pacing_note": "One unbroken 8–12s beat; no camera cuts within clip",
    },
    "afterglow": {
        "primary": "static_pull_back",
        "options": ["slow_dolly_out", "soft_focus_bloom", "window_light_shift"],
        "lens": "35mm f/2",
        "framing": "wider than peak — context returns, bodies at rest",
        "pacing_note": "Decelerate motion 40%; hold final 2s on emotional residue",
    },
}

NSFW_CHAIN_QA_CHECKS: tuple[tuple[str, str, float], ...] = (
    ("hand_finger_integrity", "Hands/fingers — no extra digits, natural pose", 1.4),
    ("skin_texture_consistency", "Skin detail — pores, tone, marks consistent at stitch", 1.3),
    ("fabric_cloth_physics", "Fabric interaction — drape, tension, displacement realistic", 1.2),
    ("explicit_area_artifact_risk", "Explicit zones — no morphing, duplication, uncanny detail", 1.5),
    ("body_proportion_stability", "Body proportions stable across stitch boundary", 1.3),
    ("intimate_physics_fidelity", "Weight transfer, skin deformation, momentum realistic", 1.4),
    ("erotic_tension_carryover", "Sensual tension curve maintained across boundary", 1.1),
    ("lighting_skin_modeling", "Motivated rim/practical light flatters skin at stitch", 1.0),
)

NSFW_QA_CRITICAL = frozenset({
    "hand_finger_integrity",
    "explicit_area_artifact_risk",
    "body_proportion_stability",
    "intimate_physics_fidelity",
})

ARTIFACT_AVOIDANCE_PROMPT_BLOCK = """Artifact Guard (explicit zones):
- Hands: single natural pose, fingers visible and anatomically correct, no merging
- Skin: consistent pore texture, no plastic sheen, no duplicate features
- Fabric: one primary tension point per clip, realistic drape and pull
- Bodies: stable proportions, no limb morphing at stitch boundary
- Physics: weighty momentum, skin compression on contact, hair response to movement"""


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def create_nsfw_sequence_scaffold(
    sequence_name: str,
    *,
    target_duration: int = 90,
    source_type: str = "reference_frame",
    reference_description: str = "",
    tension_profile: str = "passionate",
    character_names: list[str] | None = None,
    color_grade: str = "warm amber intimacy, soft highlight roll-off, lifted shadows",
    atmosphere: str = "candlelit interior, haze, practical warmth",
) -> dict[str, Any]:
    """Create NSFW sequence scaffold extending cinematic sequence_chain."""
    profile = TENSION_PROFILES.get(tension_profile, TENSION_PROFILES["passionate"])
    seq = create_sequence_scaffold(
        sequence_name,
        target_duration=target_duration,
        genre="nsfw_erotic",
        pipeline={
            **DEFAULT_PIPELINE,
            "model": DEFAULT_IMAGINE_VIDEO_MODEL,
            "extend_protocol": "LAST_FRAME + MOTION_VECTOR + AUDIO_CUE + EROSFORGE_STATE",
            "clip_length_preferred": f"{profile['clip_duration_range'][0]}-{profile['clip_duration_range'][1]}s",
        },
    )
    seq["nsfw_extension"] = {
        "schema_version": SCHEMA_VERSION,
        "tag": NSFW_SEQUENCES_TAG,
        "source_type": source_type,
        "reference_description": reference_description,
        "tension_profile": tension_profile,
        "character_names": character_names or [],
        "color_grade": color_grade,
        "atmosphere": atmosphere,
        "erosforge_active": True,
        "intimacy_physics_state": {},
        "post_scene_state": {},
        "clothing_displacement_log": [],
        "emotional_residue": "",
        "tension_curve": [],
        "created_at": _now_iso(),
    }
    return seq


def _allocate_clips_by_phase(
    target_duration: int,
    profile: dict[str, Any],
) -> list[dict[str, Any]]:
    """Distribute clips across erotic phases by profile weights."""
    lo, hi = profile["clip_duration_range"]
    avg_dur = (lo + hi) / 2
    clip_count = max(3, min(15, int(math.ceil(target_duration / avg_dur))))

    weights = profile["phase_weights"]
    allocations: list[tuple[str, int]] = []
    remaining = clip_count
    phases = list(weights.keys())

    for i, phase in enumerate(phases):
        if i == len(phases) - 1:
            count = remaining
        else:
            count = max(1 if weights[phase] >= 0.12 else 0, round(clip_count * weights[phase]))
            count = min(count, remaining - (len(phases) - i - 1))
            remaining -= count
        if count > 0:
            allocations.append((phase, count))

    beats: list[dict[str, Any]] = []
    clip_idx = 0
    for phase, count in allocations:
        phase_info = EROTIC_PHASES[phase]
        cam = CAMERA_MOVES[phase]
        for j in range(count):
            dur = lo if phase in ("peak", "escalation") and profile == TENSION_PROFILES["intense"] else hi
            if phase == "afterglow":
                dur = lo + 2
            beats.append({
                "beat_index": clip_idx,
                "phase": phase,
                "phase_label": phase_info["label"],
                "tension_level": phase_info["tension"],
                "motion_intensity": phase_info["motion_intensity"],
                "duration_seconds": dur,
                "camera": cam,
                "beat_summary": phase_info["description"],
            })
            clip_idx += 1
    return beats


def build_erotic_beat_sheet(
    *,
    target_duration: int = 90,
    tension_profile: str = "passionate",
    reference_description: str = "",
    custom_beats: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Generate beat sheet with tension curve, camera, and pacing."""
    profile = TENSION_PROFILES.get(tension_profile, TENSION_PROFILES["passionate"])
    beats = _allocate_clips_by_phase(target_duration, profile)

    if custom_beats:
        for i, beat_text in enumerate(custom_beats):
            if i < len(beats):
                beats[i]["beat_summary"] = beat_text
                beats[i]["custom"] = True

    if reference_description and beats:
        beats[0]["beat_summary"] = f"From reference: {reference_description}. {beats[0]['beat_summary']}"
        beats[0]["source_anchor"] = True

    cumulative = 0.0
    for b in beats:
        b["t_start"] = round(cumulative, 1)
        cumulative += b["duration_seconds"]
        b["t_end"] = round(cumulative, 1)
    return beats


def suggest_camera_pacing(beat: dict[str, Any]) -> dict[str, Any]:
    """Return camera movement and pacing recommendation for maximum erotic impact."""
    phase = beat.get("phase", "contact")
    cam = beat.get("camera") or CAMERA_MOVES.get(phase, CAMERA_MOVES["contact"])
    phase_info = EROTIC_PHASES.get(phase, EROTIC_PHASES["contact"])

    return {
        "phase": phase,
        "primary_move": cam["primary"],
        "alternate_moves": cam["options"],
        "lens": cam["lens"],
        "framing": cam["framing"],
        "pacing_note": cam["pacing_note"],
        "tension_level": phase_info["tension"],
        "motion_intensity": phase_info["motion_intensity"],
        "timing_beats": _timing_beats_for_phase(phase, beat.get("duration_seconds", 10)),
    }


def _timing_beats_for_phase(phase: str, duration: float) -> list[dict[str, Any]]:
    """Frame-accurate timing beats for 1.5 native audio sync."""
    if phase == "anticipation":
        return [
            {"t": 0.0, "action": "hold stillness, eye contact locks"},
            {"t": duration * 0.4, "action": "subtle breath rise, fabric shift"},
            {"t": duration * 0.8, "action": "micro lean forward, anticipation peak"},
        ]
    if phase == "approach":
        return [
            {"t": 0.0, "action": "hand enters frame slowly"},
            {"t": duration * 0.35, "action": "first skin contact, breath catch"},
            {"t": duration * 0.7, "action": "eyes close halfway, tension release begins"},
        ]
    if phase == "contact":
        return [
            {"t": 0.0, "action": "contact point holds, pressure increases"},
            {"t": duration * 0.5, "action": "fabric displacement visible, skin compression"},
            {"t": duration * 0.85, "action": "momentum vector established for next clip"},
        ]
    if phase in ("escalation", "peak"):
        return [
            {"t": 0.0, "action": "continue momentum from LAST_FRAME_RECAP"},
            {"t": duration * 0.45, "action": "primary intimate motion beat"},
            {"t": duration * 0.9, "action": "decelerate into hold for stitch"},
        ]
    return [
        {"t": 0.0, "action": "motion decelerates 40%"},
        {"t": duration * 0.5, "action": "bodies settle, emotional residue visible"},
        {"t": duration * 0.95, "action": "hold final frame for extend handoff"},
    ]


def _erosforge_state_block(seq: dict[str, Any], beat: dict[str, Any]) -> str:
    ext = seq.get("nsfw_extension", {})
    lines = [
        "EROSFORGE_STATE:",
        f"  intimacy_physics_state: weight transfer active, skin response enabled, cloth dynamics on",
        f"  phase: {beat.get('phase', 'contact')} (tension {beat.get('tension_level', 0.5):.2f})",
        f"  post_scene_state: carry forward from previous clip — clothing, position, emotional residue",
        f"  clothing_displacement_log: propagate fabric tension from LAST_FRAME_RECAP",
        f"  color_grade: {ext.get('color_grade', '')}",
        f"  atmosphere: {ext.get('atmosphere', '')}",
    ]
    return "\n".join(lines)


def build_nsfw_clip_prompt(
    seq: dict[str, Any],
    beat: dict[str, Any],
    *,
    character_injection: str = "",
    is_first_clip: bool = False,
) -> str:
    """Build a single Grok Imagine prompt for a beat (first clip or extend)."""
    ext = seq.get("nsfw_extension", {})
    cam = suggest_camera_pacing(beat)
    timing = cam["timing_beats"]

    lines = []
    if character_injection:
        lines.append(character_injection.strip())
        lines.append("")

    pipeline = seq.get("video_pipeline_spec", DEFAULT_PIPELINE)
    lines += [
        f"[VIDEO_PIPELINE_SPEC: model=\"{pipeline.get('model')}\", resolution=\"720p\", "
        f"native_audio=true, extend_from_last={str(not is_first_clip).lower()}, "
        f"stitch_to_previous={str(not is_first_clip).lower()}]",
        "",
        f"Scene: {beat.get('beat_summary', '')}",
        f"Phase: {beat.get('phase_label', '')} | Tension: {beat.get('tension_level', 0):.0%}",
        "",
        "Camera:",
        f"  move: {cam['primary_move']}",
        f"  lens: {cam['lens']}",
        f"  framing: {cam['framing']}",
        f"  pacing: {cam['pacing_note']}",
        "",
        "Timing beats:",
    ]
    for tb in timing:
        lines.append(f"  t={tb['t']:.1f}s: {tb['action']}")
    lines += [
        "",
        _erosforge_state_block(seq, beat),
        "",
        ARTIFACT_AVOIDANCE_PROMPT_BLOCK,
        "",
        "Sound Layer: breath-synced ambience, subtle fabric SFX, no dialogue unless specified",
        "Physics: weighty skin contact, realistic cloth pull, hair micro-movement, no morphing",
    ]

    if is_first_clip and ext.get("reference_description"):
        lines += [
            "",
            f"Reference anchor: {ext['reference_description']}",
            "reference_image_fidelity=high",
        ]
    return "\n".join(lines)


def build_nsfw_extend_prompt(
    seq: dict[str, Any],
    previous_clip: dict[str, Any],
    beat: dict[str, Any],
    *,
    character_injection: str = "",
) -> str:
    """Build extend-from-frame prompt with ErosForge + artifact guard."""
    base = build_extend_prompt(
        seq,
        previous_clip,
        beat.get("beat_summary", "Continue intimate sequence"),
        character_injection=character_injection,
    )
    cam = suggest_camera_pacing(beat)
    timing = cam["timing_beats"]
    ext = seq.get("nsfw_extension", {})

    extra = [
        "",
        "── NSFW Extension Layer (ErosForge) ──",
        _erosforge_state_block(seq, beat),
        "",
        "Camera (next beat):",
        f"  move: {cam['primary_move']} | lens: {cam['lens']}",
        f"  framing: {cam['framing']}",
        f"  pacing: {cam['pacing_note']}",
        "",
        "Timing beats:",
    ]
    for tb in timing:
        extra.append(f"  t={tb['t']:.1f}s: {tb['action']}")
    extra += [
        "",
        ARTIFACT_AVOIDANCE_PROMPT_BLOCK,
        "",
        f"Color grade continuity: {ext.get('color_grade', '')}",
        f"Atmosphere: {ext.get('atmosphere', '')}",
        "intimacy_physics_state: continue weight transfer and skin deformation from recap",
        "post_scene_state: update clothing displacement and body position for next handoff",
    ]
    return base + "\n".join(extra)


def plan_nsfw_extension(
    sequence_name: str,
    *,
    target_duration: int = 90,
    source_type: str = "reference_frame",
    reference_description: str = "",
    tension_profile: str = "passionate",
    character_names: list[str] | None = None,
    custom_beats: list[str] | None = None,
    color_grade: str = "warm amber intimacy, soft highlight roll-off, lifted shadows",
    atmosphere: str = "candlelit interior, haze, practical warmth",
    character_injection: str = "",
) -> dict[str, Any]:
    """
    Plan full NSFW extension from reference frame or short clip to 30–120+ seconds.
    Returns sequence with pre-built clips, prompt chain, and cost estimate.
    """
    seq = create_nsfw_sequence_scaffold(
        sequence_name,
        target_duration=target_duration,
        source_type=source_type,
        reference_description=reference_description,
        tension_profile=tension_profile,
        character_names=character_names,
        color_grade=color_grade,
        atmosphere=atmosphere,
    )

    beats = build_erotic_beat_sheet(
        target_duration=target_duration,
        tension_profile=tension_profile,
        reference_description=reference_description,
        custom_beats=custom_beats,
    )

    seq["nsfw_extension"]["tension_curve"] = [
        {"t": b["t_end"], "tension": b["tension_level"], "phase": b["phase"]}
        for b in beats
    ]

    prompt_chain: list[dict[str, Any]] = []
    clips: list[dict[str, Any]] = []
    prev_clip: dict[str, Any] | None = None

    for i, beat in enumerate(beats):
        cam = suggest_camera_pacing(beat)
        if i == 0:
            prompt = build_nsfw_clip_prompt(seq, beat, character_injection=character_injection, is_first_clip=True)
            extend_mode = "reference_to_video" if source_type == "reference_frame" else "extend_from_clip"
        else:
            prompt = build_nsfw_extend_prompt(seq, prev_clip, beat, character_injection=character_injection)
            extend_mode = "extend_from_last_frame"

        clip = create_clip(
            index=i,
            duration_seconds=int(beat["duration_seconds"]),
            prompt=prompt,
            status="planned",
            last_frame_recap=_default_recap_for_beat(beat, reference_description if i == 0 else ""),
            momentum_vector={
                "last_action": beat["beat_summary"],
                "emotional_state": f"{beat['phase_label']} — tension {beat['tension_level']:.0%}",
                "camera_velocity": cam["primary_move"],
                "lighting_state": color_grade,
                "physics_state": f"intimacy_{beat['motion_intensity']}",
                "visual_motifs": [atmosphere, beat["phase"]],
            },
            audio_momentum_vector={
                "dialogue_state": "minimal or breath-only",
                "lip_sync_state": "breath-sync at contact beats" if beat["phase"] in ("contact", "peak") else "none",
                "sfx_timing": "fabric rustle, skin contact, ambient room tone",
                "emotional_tone_audio": beat["phase_label"].lower(),
                "music_cue_points": [f"t={beat['duration_seconds'] * 0.5:.1f}s subtle swell"],
            },
            continuity_state={
                "phase": beat["phase"],
                "tension_level": beat["tension_level"],
                "clothing_state": "propagate from ErosForge log",
                "body_position": "from LAST_FRAME_RECAP",
            },
            transition_to_next="invisible_edit" if beat["phase"] != "afterglow" else "dissolve",
        )
        clip["nsfw_beat"] = beat
        clip["extend_mode"] = extend_mode
        clip["camera_pacing"] = cam
        clip["extend_instructions"] = _extend_instructions(extend_mode, i == 0, source_type)

        cost = estimate_shot_cost({
            "recommended_mode": "image_to_video" if i == 0 and source_type == "reference_frame" else "video_prompt",
            "duration_seconds": beat["duration_seconds"],
        })

        prompt_chain.append({
            "clip_id": clip["clip_id"],
            "phase": beat["phase"],
            "extend_mode": extend_mode,
            "prompt": prompt,
            "camera_pacing": cam,
            "extend_instructions": clip["extend_instructions"],
            "estimated_credits": cost.get("credits", 0),
        })

        clips.append(clip)
        prev_clip = clip

    seq["clips"] = clips
    seq["prompt_chain"] = prompt_chain

    clip_specs = [{"clip_id": c["clip_id"], "index": c["index"], "duration_seconds": c["duration_seconds"]} for c in clips]
    seq["cost_estimate"] = estimate_sequence_cost(clip_specs)

    return seq


def _default_recap_for_beat(beat: dict[str, Any], ref: str) -> str:
    if ref and beat.get("source_anchor"):
        return f"Reference state: {ref}. Phase {beat['phase_label']}, tension {beat['tension_level']:.0%}."
    return (
        f"End state: {beat['beat_summary']}. Camera: {beat.get('camera', {}).get('primary', 'hold')}. "
        f"Bodies positioned for {EROTIC_PHASES.get(beat['phase'], {}).get('label', 'next')} phase."
    )


def _extend_instructions(extend_mode: str, is_first: bool, source_type: str) -> list[str]:
    if is_first and source_type == "reference_frame":
        return [
            "Use high-quality reference still as reference_image_id",
            "image_to_video with native_audio=true",
            "Lock identity from reference before any extend",
            "Run NSFW chain QA before clip_002 extend",
        ]
    if is_first and source_type == "short_clip":
        return [
            "Use approved short clip last frame as extend anchor",
            "Capture LAST_FRAME_RECAP from clip end before planning clip_002",
            "Verify hand_finger_integrity and skin_texture at clip end",
        ]
    return [
        "extend_from_last=true",
        "stitch_to_previous=true",
        "Propagate EROSFORGE_STATE: intimacy_physics, clothing_displacement, post_scene",
        "Run NSFW chain QA — critical: hand_finger_integrity, explicit_area_artifact_risk",
        "Do not extend if previous clip QA decision is no_go",
    ]


def build_prompt_chain(seq: dict[str, Any]) -> list[dict[str, Any]]:
    """Return or rebuild ready-to-use prompt chain from sequence."""
    if seq.get("prompt_chain"):
        return seq["prompt_chain"]
    chain = []
    clips = seq.get("clips", [])
    for i, clip in enumerate(clips):
        beat = clip.get("nsfw_beat", {})
        if i == 0:
            prompt = clip.get("prompt") or build_nsfw_clip_prompt(seq, beat, is_first_clip=True)
            mode = clip.get("extend_mode", "reference_to_video")
        else:
            prompt = clip.get("prompt") or build_nsfw_extend_prompt(seq, clips[i - 1], beat)
            mode = "extend_from_last_frame"
        chain.append({
            "clip_id": clip["clip_id"],
            "phase": beat.get("phase", ""),
            "extend_mode": mode,
            "prompt": prompt,
            "camera_pacing": clip.get("camera_pacing") or suggest_camera_pacing(beat),
            "extend_instructions": clip.get("extend_instructions", []),
        })
    return chain


def run_nsfw_chain_qa_scaffold(clip: dict[str, Any]) -> dict[str, Any]:
    """Return NSFW-specific chain QA scaffold (standard + intimate checks)."""
    result: dict[str, Any] = {
        "clip_id": clip["clip_id"],
        "evaluated_at": _now_iso(),
        "nsfw_checks": {},
        "decision": "awaiting_scores",
        "critical_failures": [],
        "artifact_fixes": [],
    }
    for key, label, weight in NSFW_CHAIN_QA_CHECKS:
        result["nsfw_checks"][key] = {
            "label": label,
            "score": None,
            "pass": None,
            "weight": weight,
            "critical": key in NSFW_QA_CRITICAL,
        }
    result["artifact_fixes"] = [
        "If hand_finger_integrity < 7: regenerate with hands out of frame or single-hand pose",
        "If explicit_area_artifact_risk < 7: pull back framing, reduce simultaneous body focus",
        "If skin_texture_consistency < 7: tighten Character DNA inject, match color grade",
        "If fabric_cloth_physics < 7: specify one fabric tension point in prompt",
    ]
    return result


def evaluate_nsfw_chain_qa(clip: dict[str, Any], scores: dict[str, float]) -> dict[str, Any]:
    """Evaluate NSFW chain QA scores."""
    result = run_nsfw_chain_qa_scaffold(clip)
    total_weight = 0.0
    weighted_sum = 0.0
    critical_failures: list[str] = []

    for key, label, weight in NSFW_CHAIN_QA_CHECKS:
        score = scores.get(key)
        if score is None:
            continue
        passed = score >= 7.0
        result["nsfw_checks"][key] = {
            "label": label,
            "score": score,
            "pass": passed,
            "weight": weight,
            "critical": key in NSFW_QA_CRITICAL,
        }
        weighted_sum += score * weight
        total_weight += weight
        if not passed and key in NSFW_QA_CRITICAL:
            critical_failures.append(key)

    result["weighted_score"] = round(weighted_sum / total_weight, 2) if total_weight else None
    result["critical_failures"] = critical_failures

    if critical_failures:
        result["decision"] = "no_go"
    elif result["weighted_score"] is not None and result["weighted_score"] >= 7.0:
        result["decision"] = "go"
    elif result["weighted_score"] is not None and result["weighted_score"] >= 5.5:
        result["decision"] = "conditional_go"
    else:
        result["decision"] = "no_go"

    return result


def nsfw_sequence_to_markdown(seq: dict[str, Any]) -> str:
    """Export full NSFW extension plan with prompt chain."""
    ext = seq.get("nsfw_extension", {})
    lines = [
        f"# NSFW Sequence Extension — {seq['sequence_name']}",
        "",
        f"**Target:** {seq.get('target_duration_seconds', 0)}s | **Profile:** {ext.get('tension_profile', '')} | **Source:** {ext.get('source_type', '')}",
        f"**Clips:** {len(seq.get('clips', []))} | **Est. Credits:** {seq.get('cost_estimate', {}).get('credits_high', 'N/A')}",
        "",
        f"**Reference:** {ext.get('reference_description', '')}",
        f"**Color Grade:** {ext.get('color_grade', '')}",
        f"**Atmosphere:** {ext.get('atmosphere', '')}",
        "",
        "## Tension Curve",
        "",
    ]
    for point in ext.get("tension_curve", []):
        lines.append(f"- t={point['t']}s — {point['phase']} (tension {point['tension']:.0%})")
    lines.extend(["", "## Prompt Chain", ""])

    for item in build_prompt_chain(seq):
        lines += [
            f"### {item['clip_id']} — {item.get('phase', '')} ({item.get('extend_mode', '')})",
            "",
            "**Extend instructions:**",
        ]
        for instr in item.get("extend_instructions", []):
            lines.append(f"- {instr}")
        cam = item.get("camera_pacing", {})
        lines += [
            "",
            f"**Camera:** {cam.get('primary_move', '')} | {cam.get('lens', '')} | {cam.get('pacing_note', '')}",
            "",
            "```",
            item.get("prompt", ""),
            "```",
            "",
        ]
    return "\n".join(lines)


def save_nsfw_sequence(seq: dict[str, Any]) -> Path:
    """Persist NSFW sequence to sequences/ directory."""
    path = save_sequence(seq)
    handoff_path = path.parent / "prompt_chain.json"
    handoff_path.write_text(json.dumps(build_prompt_chain(seq), indent=2))
    md_path = path.parent / "extension_plan.md"
    md_path.write_text(nsfw_sequence_to_markdown(seq))
    return path