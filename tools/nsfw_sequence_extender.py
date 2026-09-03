#!/usr/bin/env python3
"""
NSFW Sequence Extender — sensual long-form extension from reference frame or short clip.

Domain split:
  nsfw_extension_config.py  — tension profiles, phases, camera, chain QA constants
  nsfw_extension_beats.py   — beat sheet allocation, sequence scaffold
  nsfw_extension_prompts.py — prompt and camera pacing builders
  nsfw_chain_qa.py          — artifact-aware chain QA gate
  nsfw_sequence_extender.py — planning and persistence (this module)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aup_gate import gate_text, require_attestation
from nsfw_orchestrator import estimate_shot_cost
from quota_optimizer import estimate_sequence_cost
from sequence_chain import create_clip, save_sequence

from nsfw_chain_qa import (  # noqa: F401 — re-exported
    evaluate_nsfw_chain_qa,
    run_nsfw_chain_qa_scaffold,
)
from nsfw_extension_beats import (  # noqa: F401 — re-exported
    build_erotic_beat_sheet,
    create_nsfw_sequence_scaffold,
)
from nsfw_extension_config import (  # noqa: F401 — re-exported
    ARTIFACT_AVOIDANCE_PROMPT_BLOCK,
    CAMERA_MOVES,
    EROTIC_PHASES,
    NSFW_CHAIN_QA_CHECKS,
    NSFW_QA_CRITICAL,
    NSFW_SEQUENCES_TAG,
    SCHEMA_VERSION,
    TENSION_PROFILES,
)
from nsfw_extension_prompts import (  # noqa: F401 — re-exported
    build_nsfw_clip_prompt,
    build_nsfw_extend_prompt,
    default_recap_for_beat,
    extend_instructions,
    suggest_camera_pacing,
)

__all__ = [
    "ARTIFACT_AVOIDANCE_PROMPT_BLOCK",
    "CAMERA_MOVES",
    "EROTIC_PHASES",
    "NSFW_CHAIN_QA_CHECKS",
    "NSFW_QA_CRITICAL",
    "NSFW_SEQUENCES_TAG",
    "SCHEMA_VERSION",
    "TENSION_PROFILES",
    "build_erotic_beat_sheet",
    "build_nsfw_clip_prompt",
    "build_nsfw_extend_prompt",
    "build_prompt_chain",
    "create_nsfw_sequence_scaffold",
    "evaluate_nsfw_chain_qa",
    "nsfw_sequence_to_markdown",
    "plan_nsfw_extension",
    "run_nsfw_chain_qa_scaffold",
    "save_nsfw_sequence",
    "suggest_camera_pacing",
]


def _gate_nsfw_extension_text(*parts: Any) -> None:
    """Attestation + R-rated text gate for NSFW extend planning."""
    require_attestation()
    blob = "\n".join(str(p).strip() for p in parts if p)
    gate_text(blob, nsfw=True)


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
    _gate_nsfw_extension_text(
        sequence_name,
        reference_description,
        tension_profile,
        color_grade,
        atmosphere,
        character_injection,
        *(custom_beats or []),
        *(character_names or []),
    )
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
            last_frame_recap=default_recap_for_beat(beat, reference_description if i == 0 else ""),
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
        clip["extend_instructions"] = extend_instructions(extend_mode, i == 0, source_type)

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
    for item in prompt_chain:
        gate_text(item.get("prompt") or "", nsfw=True)

    clip_specs = [
        {"clip_id": c["clip_id"], "index": c["index"], "duration_seconds": c["duration_seconds"]}
        for c in clips
    ]
    seq["cost_estimate"] = estimate_sequence_cost(clip_specs)

    return seq


def build_prompt_chain(seq: dict[str, Any]) -> list[dict[str, Any]]:
    """Return or rebuild ready-to-use prompt chain from sequence."""
    require_attestation()
    if seq.get("prompt_chain"):
        for item in seq["prompt_chain"]:
            gate_text(item.get("prompt") or "", nsfw=True)
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
        gate_text(prompt or "", nsfw=True)
    return chain


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