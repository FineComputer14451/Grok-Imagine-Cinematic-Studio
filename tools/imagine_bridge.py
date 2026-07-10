#!/usr/bin/env python3
"""
Grok Imagine execution bridge — copy-paste handoff packets for grok.com/imagine
and official Imagine Agent Mode Handoff packets (studio v3.7.1+).

Emits VIDEO_PIPELINE_SPEC, reference attachment hints, and native audio Sound Layer
blocks for chat-based generation when API keys are unavailable, plus multi-surface
agent-mode handoffs (Build tools, ACP, web UI, xAI API).
"""

from __future__ import annotations

from typing import Any

from models import (
    DEFAULT_IMAGINE_IMAGE_MODEL,
    DEFAULT_IMAGINE_VIDEO_MODEL,
    DEFAULT_XAI_BUILD_MODEL,
    DEFAULT_XAI_CHAT_MODEL,
    STUDIO_COMPATIBILITY_VERSION,
    build_video_pipeline_spec,
)
from project_state import load_project_state
from imagine_jobs import ensure_asset_manifest

PROTOCOL_VERSION = "3.7.1"

TARGET_SURFACES = frozenset(
    {
        "grok_build_tools",
        "grok_agent_acp",
        "grok_com_imagine",
        "xai_api",
    }
)

EXECUTION_MODES = frozenset(
    {
        "image_prompt",
        "image_edit",
        "image_to_video",
        "video_prompt",
        "reference_to_video",
    }
)

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


def _normalize_execution_mode(subject: dict[str, Any], mode: str | None) -> str:
    raw = mode or subject.get("recommended_mode") or subject.get("decision", {}).get("mode")
    if not raw:
        raw = "video_prompt"
    # Map legacy bridge modes
    aliases = {
        "image": "image_prompt",
        "still": "image_prompt",
        "i2v": "image_to_video",
        "video": "video_prompt",
        "t2v": "video_prompt",
    }
    normalized = aliases.get(str(raw), str(raw))
    if normalized not in EXECUTION_MODES:
        return "video_prompt"
    return normalized


def _agent_handoff_steps(surface: str, execution_mode: str) -> list[str]:
    if surface == "grok_com_imagine":
        return _handoff_steps(
            "image_prompt"
            if execution_mode in ("image_prompt", "image_edit")
            else ("image_to_video" if execution_mode == "image_to_video" else "video_prompt")
        )
    if surface == "xai_api":
        return [
            "1. Run: python tools/cinematic_studio_cli.py imagine verify",
            "2. Submit via sfw run / sequence run / imagine submit with packet prompt + models",
            "3. Attach job_id to directors_notes_log; reconcile quota",
            "4. return_path: record QA score and artifact path",
        ]
    if surface == "grok_agent_acp":
        return [
            "1. Confirm plugin skills loaded (grok-imagine-cinematic-studio) in ACP session",
            "2. Execute Imagine tools or CLI per execution_mode (no TUI-only modals)",
            "3. Save outputs under artifacts/; log tool results",
            "4. return_path: QA Guardian + Project Bible update",
        ]
    # grok_build_tools (default)
    if execution_mode in ("image_prompt", "image_edit"):
        return [
            "1. Call image_gen or image_edit with packet prompt + references",
            "2. Set aspect_ratio from packet; save under artifacts/",
            "3. On QA ≥7, lock plate before any i2v spend",
            "4. return_path: sfw record or plate lock + Director's Notes",
        ]
    if execution_mode in ("image_to_video", "reference_to_video"):
        return [
            "1. Attach locked reference plate as frame-1 source",
            "2. Call image_to_video (or reference_to_video) with motion prompt + Sound Layer",
            "3. Prefer 6–10s shots; native audio when pipeline requires",
            "4. return_path: sequence run / sfw record + chain QA if extend",
        ]
    return [
        "1. Prefer still→i2v when plate exists; else craft first frame then animate",
        "2. Call image_to_video with Sound Layer; duration 6–10s preferred",
        "3. Save artifact; do not claim success without tool result",
        "4. return_path: QA Guardian + Director's Notes",
    ]


def _default_return_path(surface: str, context: str) -> str:
    if context == "clip":
        return "sequence run / chain QA + Continuity Guardian update"
    if surface == "xai_api":
        return "sfw record <batch> <shot> --score … --credits …"
    if surface == "grok_com_imagine":
        return "Download result → sfw record or sequence handoff JSON + QA"
    return "artifacts/ path + Director's Notes + QA Guardian"


def build_agent_mode_handoff(
    subject: dict[str, Any],
    *,
    target_surface: str = "grok_build_tools",
    context: str = "shot",
    execution_mode: str | None = None,
    video_model: str | None = None,
    prompt: str | None = None,
    quota_note: str = "Confirm remaining quota before video spend; prefer Fast mode when quality allows",
    return_path: str | None = None,
    dna_inject: str | None = None,
    qa_gate: str = "still QA ≥7 before hero video; chain QA Go before extend",
    state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build official imagine_agent_mode_handoff packet (protocol v3.7.1)."""
    surface = target_surface.strip()
    if surface not in TARGET_SURFACES:
        raise ValueError(
            f"invalid target_surface: {target_surface!r}; "
            f"expected one of {sorted(TARGET_SURFACES)}"
        )

    base = build_bridge_packet(
        subject,
        context=context,
        video_model=video_model,
        prompt=prompt,
        state=state,
    )
    mode = _normalize_execution_mode(subject, execution_mode or base.get("mode"))
    is_video = mode in ("image_to_video", "video_prompt", "reference_to_video")

    packet: dict[str, Any] = {
        "packet_type": "imagine_agent_mode_handoff",
        "protocol_version": PROTOCOL_VERSION,
        "studio_version": STUDIO_COMPATIBILITY_VERSION,
        "target_surface": surface,
        "execution_mode": mode,
        "context": base["context"],
        "subject_id": base["subject_id"],
        "video_model": base["video_model"],
        "image_model": base["image_model"],
        "aspect_ratio": base.get("aspect_ratio", "16:9"),
        "video_pipeline_spec": base["video_pipeline_spec"] if is_video else base.get("video_pipeline_spec", ""),
        "prompt": base["prompt"],
        "reference_hints": base["reference_hints"],
        "sound_layer": base["sound_layer"] if is_video else base.get("sound_layer", ""),
        "model_stack": {
            "chat": DEFAULT_XAI_CHAT_MODEL,
            "build": DEFAULT_XAI_BUILD_MODEL,
            "imagine_image": base.get("image_model") or DEFAULT_IMAGINE_IMAGE_MODEL,
            "imagine_video": base.get("video_model") or DEFAULT_IMAGINE_VIDEO_MODEL,
        },
        "quota_note": quota_note,
        "return_path": return_path or _default_return_path(surface, context),
        "handoff_steps": _agent_handoff_steps(surface, mode),
        "qa_gate": qa_gate,
        "grok_imagine_url": base.get("grok_imagine_url", "https://grok.com/imagine"),
    }

    if dna_inject or subject.get("dna_inject"):
        packet["dna_inject"] = dna_inject or subject.get("dna_inject")

    if base.get("last_frame_recap"):
        packet["last_frame_recap"] = base["last_frame_recap"]
    if base.get("momentum_vector"):
        packet["momentum_vector"] = base["momentum_vector"]
    amv = subject.get("audio_momentum_vector")
    if amv:
        packet["audio_momentum_vector"] = amv
    if base.get("slug_link"):
        packet["slug_link"] = base["slug_link"]

    return packet


def agent_mode_handoff_to_markdown(packet: dict[str, Any]) -> str:
    """Human/agent-readable Imagine Agent Mode Handoff document."""
    lines = [
        f"# Imagine Agent Mode Handoff v{packet.get('protocol_version', PROTOCOL_VERSION)}",
        "",
        f"**Packet:** `{packet.get('packet_type', 'imagine_agent_mode_handoff')}`",
        f"**Studio:** v{packet.get('studio_version', STUDIO_COMPATIBILITY_VERSION)}",
        f"**Subject:** `{packet.get('subject_id')}` · **Context:** {packet.get('context')}",
        f"**Target surface:** `{packet.get('target_surface')}`",
        f"**Execution mode:** `{packet.get('execution_mode')}`",
        f"**Models:** `{packet.get('image_model')}` → `{packet.get('video_model')}`",
        f"**Aspect:** {packet.get('aspect_ratio', '16:9')}",
        "",
        "## Model stack",
    ]
    stack = packet.get("model_stack") or {}
    for key in ("chat", "build", "imagine_image", "imagine_video"):
        if key in stack:
            lines.append(f"- {key}: `{stack[key]}`")
    lines.append("")

    if packet.get("video_pipeline_spec"):
        lines += [
            "## VIDEO_PIPELINE_SPEC",
            "```",
            str(packet["video_pipeline_spec"]),
            "```",
            "",
        ]

    lines += ["## Prompt", str(packet.get("prompt", "")), ""]

    if packet.get("dna_inject"):
        lines += ["## DNA inject", str(packet["dna_inject"]), ""]
    if packet.get("last_frame_recap"):
        lines += ["## LAST_FRAME_RECAP", str(packet["last_frame_recap"]), ""]
    if packet.get("momentum_vector"):
        mv = packet["momentum_vector"]
        if isinstance(mv, dict):
            lines += [
                "## MOMENTUM_VECTOR",
                f"- last_action: {mv.get('last_action', mv.get('action', ''))}",
                f"- emotional_state: {mv.get('emotional_state', mv.get('emotion', ''))}",
                f"- camera_velocity: {mv.get('camera_velocity', mv.get('camera', ''))}",
                "",
            ]

    hints = packet.get("reference_hints") or []
    if hints:
        lines += ["## Reference", *[f"- {h}" for h in hints], ""]

    if packet.get("sound_layer"):
        lines += ["## Sound Layer", str(packet["sound_layer"]), ""]

    lines += [
        "## Quota",
        str(packet.get("quota_note", "")),
        "",
        "## QA gate",
        str(packet.get("qa_gate", "")),
        "",
        "## Return path",
        str(packet.get("return_path", "")),
        "",
        "## Handoff steps",
        *[f"{s}" for s in packet.get("handoff_steps") or []],
        "",
    ]
    if packet.get("target_surface") == "grok_com_imagine":
        lines.append(f"Open: {packet.get('grok_imagine_url', 'https://grok.com/imagine')}")
    if packet.get("slug_link"):
        lines.append(f"Studio slug: `{packet['slug_link']}`")
    lines.append("")
    lines.append(
        "_Canonical protocol: references/agents/IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md_"
    )
    return "\n".join(lines)