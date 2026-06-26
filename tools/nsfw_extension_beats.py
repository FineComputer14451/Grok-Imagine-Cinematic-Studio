"""NSFW extension beat sheet allocation and sequence scaffold."""

from __future__ import annotations

import math
from typing import Any

from models import DEFAULT_IMAGINE_VIDEO_MODEL
from sequence_chain import DEFAULT_PIPELINE, create_sequence_scaffold

from nsfw_extension_config import (
    CAMERA_MOVES,
    EROTIC_PHASES,
    NSFW_SEQUENCES_TAG,
    SCHEMA_VERSION,
    TENSION_PROFILES,
)
from nsfw_util import now_iso


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
        "created_at": now_iso(),
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
        for _j in range(count):
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