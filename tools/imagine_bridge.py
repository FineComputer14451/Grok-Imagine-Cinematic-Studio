#!/usr/bin/env python3
"""
Grok Imagine execution bridge — copy-paste handoff packets for grok.com/imagine.

Emits VIDEO_PIPELINE_SPEC, reference attachment hints, and native audio Sound Layer
blocks for chat-based generation when API keys are unavailable.
"""

from __future__ import annotations

from typing import Any

from models import build_video_pipeline_spec
from project_state import load_project_state
from imagine_jobs import ensure_asset_manifest

DEFAULT_SOUND_LAYER = (
    "Sound Layer: lip-synced dialogue at t=0, SFX: environmental texture, "
    "ambience: room tone match, music cue: subtle underscore at t=2s"
)


def _reference_asset(asset_id: str | None, state: dict[str, Any] | None = None) -> dict[str, Any] | None:
    if not asset_id:
        return None
    if state is None:
        state = load_project_state()
    manifest = ensure_asset_manifest(state)
    return manifest.get("assets", {}).get(asset_id)


def build_reference_hints(
    *,
    reference_image_id: str | None = None,
    reference_url: str | None = None,
    lock_status: str | None = None,
    state: dict[str, Any] | None = None,
) -> list[str]:
    hints: list[str] = []
    asset = _reference_asset(reference_image_id, state) if reference_image_id else None
    url = reference_url or (asset.get("url") if asset else None)
    lock = lock_status or (asset.get("lock_status") if asset else None)

    if reference_image_id:
        hints.append(f"reference_image_id: {reference_image_id}")
    if url:
        hints.append(f"Attach reference plate: {url}")
    if lock:
        hints.append(f"Plate lock status: {lock}")
    if reference_image_id and lock == "locked":
        hints.append("Use locked plate as first-frame anchor — preserve identity fidelity")
    elif reference_image_id:
        hints.append("Reference plate draft — verify QA ≥7 before hero video spend")
    return hints


def build_sound_layer(
    *,
    dialogue: str = "",
    sfx: str = "environmental texture, cloth movement",
    ambience: str = "room tone, spatial reverb",
    music_cue: str = "subtle underscore at t=2s",
) -> str:
    parts = ["Sound Layer:"]
    if dialogue:
        parts.append(f"lip-synced dialogue: '{dialogue}'")
    parts.append(f"SFX: {sfx}")
    parts.append(f"ambience: {ambience}")
    parts.append(f"music cue: {music_cue}")
    return ", ".join(parts)


def build_bridge_packet(
    subject: dict[str, Any],
    *,
    context: str = "shot",
    video_model: str | None = None,
    prompt: str | None = None,
    state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build structured handoff packet for a shot, clip, or sequence item."""
    mode = subject.get("recommended_mode") or subject.get("decision", {}).get("mode", "video_prompt")
    vid_model = video_model or subject.get("video_model", "grok-imagine-video-1.5")
    img_model = subject.get("image_model", "grok-imagine-image")
    ref_id = subject.get("reference_image_id")
    description = prompt or subject.get("prompt") or subject.get("description", "")
    aspect = subject.get("aspect_ratio", "16:9")

    packet: dict[str, Any] = {
        "context": context,
        "subject_id": subject.get("shot_id") or subject.get("clip_id") or "item",
        "mode": mode,
        "video_model": vid_model,
        "image_model": img_model,
        "aspect_ratio": aspect,
        "video_pipeline_spec": build_video_pipeline_spec(vid_model),
        "prompt": description.strip(),
        "reference_hints": build_reference_hints(
            reference_image_id=ref_id,
            reference_url=subject.get("reference_image_url"),
            state=state,
        ),
        "sound_layer": build_sound_layer(
            dialogue=subject.get("dialogue", "") or (
                (subject.get("audio_momentum_vector") or {}).get("dialogue_state", "")
            ),
        ),
        "handoff_steps": _handoff_steps(mode),
        "grok_imagine_url": "https://grok.com/imagine",
    }

    if context == "clip" and subject.get("last_frame_recap"):
        packet["last_frame_recap"] = subject["last_frame_recap"]
        mv = subject.get("momentum_vector") or {}
        if mv:
            packet["momentum_vector"] = mv

    slug = subject.get("batch_slug") or subject.get("sequence_slug")
    if slug:
        packet["slug_link"] = slug

    return packet


def _handoff_steps(mode: str) -> list[str]:
    if mode == "image_prompt":
        return [
            "1. Paste prompt + VIDEO_PIPELINE_SPEC into grok.com/imagine (Image)",
            "2. Attach reference plate if listed",
            "3. On QA ≥7, lock plate and run i2v pass",
        ]
    if mode == "image_to_video":
        return [
            "1. Attach locked reference plate first",
            "2. Paste i2v prompt with MOTION_VECTOR block",
            "3. Enable native audio — verify Sound Layer sync",
        ]
    return [
        "1. Paste full video prompt with Sound Layer",
        "2. Set duration 8–12s, native audio on",
        "3. Record result via: sfw record or sequence run",
    ]


def bridge_to_markdown(packet: dict[str, Any]) -> str:
    lines = [
        f"# Imagine Execution Bridge — {packet['subject_id']}",
        "",
        f"**Context:** {packet['context']} · **Mode:** `{packet['mode']}`",
        f"**Models:** `{packet['image_model']}` → `{packet['video_model']}`",
        f"**Aspect:** {packet.get('aspect_ratio', '16:9')}",
        "",
        "## VIDEO_PIPELINE_SPEC",
        "```",
        packet["video_pipeline_spec"],
        "```",
        "",
        "## Prompt",
        packet["prompt"],
        "",
    ]

    if packet.get("last_frame_recap"):
        lines += ["## LAST_FRAME_RECAP", packet["last_frame_recap"], ""]
    if packet.get("momentum_vector"):
        mv = packet["momentum_vector"]
        lines += [
            "## MOMENTUM_VECTOR",
            f"- last_action: {mv.get('last_action', '')}",
            f"- emotional_state: {mv.get('emotional_state', '')}",
            f"- camera_velocity: {mv.get('camera_velocity', '')}",
            "",
        ]

    if packet["reference_hints"]:
        lines += ["## Reference", *[f"- {h}" for h in packet["reference_hints"]], ""]

    lines += [
        "## Sound Layer",
        packet["sound_layer"],
        "",
        "## Handoff steps",
        *[f"{s}" for s in packet["handoff_steps"]],
        "",
        f"Open: {packet['grok_imagine_url']}",
    ]
    if packet.get("slug_link"):
        lines.append(f"Studio slug: `{packet['slug_link']}`")
    return "\n".join(lines)


def bridge_to_clipboard(packet: dict[str, Any]) -> str:
    """Single copy-paste block for grok.com/imagine."""
    parts = [
        packet["video_pipeline_spec"],
        "",
        packet["prompt"],
        "",
        packet["sound_layer"],
    ]
    if packet["reference_hints"]:
        parts.append("")
        parts.extend(packet["reference_hints"])
    if packet.get("last_frame_recap"):
        parts += ["", f"LAST_FRAME_RECAP: {packet['last_frame_recap']}"]
    return "\n".join(parts)