"""NSFW extension prompt and camera pacing builders."""

from __future__ import annotations

from typing import Any

from aup_gate import gate_nsfw_extension_text
from sequence_chain import DEFAULT_PIPELINE, build_extend_prompt

from nsfw_extension_config import (
    ARTIFACT_AVOIDANCE_PROMPT_BLOCK,
    CAMERA_MOVES,
    EROTIC_PHASES,
)


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
    return "\n".join([
        "EROSFORGE_STATE:",
        "  intimacy_physics_state: weight transfer active, skin response enabled, cloth dynamics on",
        f"  phase: {beat.get('phase', 'contact')} (tension {beat.get('tension_level', 0.5):.2f})",
        "  post_scene_state: carry forward from previous clip — clothing, position, emotional residue",
        "  clothing_displacement_log: propagate fabric tension from LAST_FRAME_RECAP",
        f"  color_grade: {ext.get('color_grade', '')}",
        f"  atmosphere: {ext.get('atmosphere', '')}",
    ])


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

    lines: list[str] = []
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
    prompt = "\n".join(lines)
    gate_nsfw_extension_text(
        prompt,
        source_type=str(ext.get("source_type") or ""),
    )
    return prompt


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
    prompt = base + "\n".join(extra)
    gate_nsfw_extension_text(
        prompt,
        source_type=str(ext.get("source_type") or ""),
    )
    return prompt


def default_recap_for_beat(beat: dict[str, Any], ref: str) -> str:
    if ref and beat.get("source_anchor"):
        return f"Reference state: {ref}. Phase {beat['phase_label']}, tension {beat['tension_level']:.0%}."
    return (
        f"End state: {beat['beat_summary']}. Camera: {beat.get('camera', {}).get('primary', 'hold')}. "
        f"Bodies positioned for {EROTIC_PHASES.get(beat['phase'], {}).get('label', 'next')} phase."
    )


def extend_instructions(extend_mode: str, is_first: bool, source_type: str) -> list[str]:
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