#!/usr/bin/env python3
"""
Grok Imagine execution bridge — handoff packets for grok.com/imagine and
official Imagine Agent Mode (studio v3.7.1+).

One core builder feeds both classic bridge packets and agent-mode envelopes.
Canonical surface/mode enums live in handoff_schema.py.
"""

from __future__ import annotations

from typing import Any

from aup_gate import gate_planning_subject
from models import (
    DEFAULT_IMAGINE_IMAGE_MODEL,
    DEFAULT_IMAGINE_VIDEO_MODEL,
    DEFAULT_XAI_BUILD_MODEL,
    DEFAULT_XAI_CHAT_MODEL,
    HERO_IMAGINE_IMAGE_MODEL,
    STUDIO_COMPATIBILITY_VERSION,
    build_video_pipeline_spec,
)
from handoff_schema import (
    CANONICAL_PROTOCOL_DOC,
    EXECUTION_MODES,
    PACKET_TYPE_IMAGINE_AGENT_MODE,
    PROTOCOL_VERSION,
    TARGET_SURFACES,
    VIDEO_EXECUTION_MODES,
    is_video_execution_mode,
    normalize_execution_mode,
    normalize_target_surface,
)
from project_state import load_project_state
from imagine_jobs import ensure_asset_manifest

# Re-export schema constants for CLI / callers
__all__ = [
    "PROTOCOL_VERSION",
    "TARGET_SURFACES",
    "EXECUTION_MODES",
    "VIDEO_EXECUTION_MODES",
    "build_handoff",
    "build_bridge_packet",
    "build_agent_mode_handoff",
    "handoff_to_markdown",
    "handoff_to_clipboard",
    "bridge_to_markdown",
    "bridge_to_clipboard",
    "agent_mode_handoff_to_markdown",
    "build_reference_hints",
    "build_sound_layer",
]

DEFAULT_SOUND_LAYER = (
    "Sound Layer: lip-synced dialogue at t=0, SFX: environmental texture, "
    "ambience: room tone match, music cue: subtle underscore at t=2s"
)

GROK_IMAGINE_URL = "https://grok.com/imagine"

# ---------------------------------------------------------------------------
# Handoff steps — data table (surface × mode bucket)
# ---------------------------------------------------------------------------

_MODE_BUCKET_IMAGE = "image"
_MODE_BUCKET_I2V = "i2v"
_MODE_BUCKET_VIDEO = "video"
_MODE_BUCKET_V2V = "v2v"

# Web / classic grok.com paste steps (mode bucket → steps)
_WEB_STEPS: dict[str, list[str]] = {
    _MODE_BUCKET_IMAGE: [
        "1. Paste prompt into grok.com/imagine Image — Quality Mode (Imagine Image 2.0)",
        "2. Attach reference plate if listed (up to 3 refs on edit)",
        "3. On QA ≥7, lock plate and run i2v pass",
    ],
    _MODE_BUCKET_I2V: [
        "1. Attach locked reference plate first (Image 2.0 hero plate preferred)",
        "2. Paste i2v prompt with MOTION_VECTOR block — Video 1.0 default, 1.5 if native audio",
        "3. Enable native audio on 1.5 — verify Sound Layer sync",
    ],
    _MODE_BUCKET_VIDEO: [
        "1. Paste full video prompt with Sound Layer (1.5) or silent 1.0 cost path",
        "2. Set duration 8–12s; 1080p only on Video 1.5 t2v/i2v",
        "3. Record result via: sfw record or sequence run",
    ],
    _MODE_BUCKET_V2V: [
        "1. Use xAI API / CLI for video edit or extend (Video 1.0) — grok.com/imagine is paste-only",
        "2. Prefer: cinematic-studio imagine submit video_edit|video_extend --video-url …",
        "3. Record result via sfw record / sequence handoff JSON + QA",
    ],
}

# In-session Build tools / ACP steps
_BUILD_STEPS: dict[str, list[str]] = {
    _MODE_BUCKET_IMAGE: [
        "1. Call image_gen or image_edit with packet prompt + references",
        "2. Set aspect_ratio from packet; save under artifacts/",
        "3. On QA ≥7, lock plate before any i2v spend",
        "4. return_path: sfw record or plate lock + Director's Notes",
    ],
    _MODE_BUCKET_I2V: [
        "1. Attach locked reference plate as frame-1 source",
        "2. Call image_to_video (or reference_to_video) with motion prompt + Sound Layer",
        "3. Prefer 6–10s shots; native audio when pipeline requires",
        "4. return_path: sequence run / sfw record + chain QA if extend",
    ],
    _MODE_BUCKET_VIDEO: [
        "1. Prefer still→i2v when plate exists; else craft first frame then animate",
        "2. Call image_to_video with Sound Layer; duration 6–10s preferred",
        "3. Save artifact; do not claim success without tool result",
        "4. return_path: QA Guardian + Director's Notes",
    ],
    _MODE_BUCKET_V2V: [
        "1. Video edit/extend is xAI REST Video 1.0 — session image_to_video cannot restyle a clip",
        "2. Run: cinematic-studio imagine submit video_edit|video_extend --video-url … --dry-run if no key",
        "3. Do not send grok-imagine-video-1.5 for edit/extend (failed_precondition)",
        "4. return_path: chain QA + Continuity Guardian before another extend",
    ],
}

_XAI_API_STEPS = [
    "1. Run: python tools/cinematic_studio_cli.py imagine verify",
    "2. Submit via imagine submit (image|image_edit|video|video_edit|video_extend|reference_to_video)",
    "3. Attach job_id to directors_notes_log; reconcile quota",
    "4. return_path: record QA score and artifact path",
]

_ACP_STEPS = [
    "1. Confirm plugin skills loaded (grok-imagine-cinematic-studio) in ACP session",
    "2. Execute Imagine tools or CLI per execution_mode (no TUI-only modals)",
    "3. Save outputs under artifacts/; log tool results",
    "4. return_path: QA Guardian + Project Bible update",
]

_RESPONSES_STEPS: dict[str, list[str]] = {
    _MODE_BUCKET_IMAGE: [
        "1. Enable Responses API tool image_generation (action=generate or edit) — uses Imagine Image 2.0",
        "2. Keep packet prompt; model picks aspect unless you specify it in the request text",
        "3. Write response.image_outputs (or image_generation_call.result) under artifacts/",
        "4. return_path: sfw record + plate lock before any video spend",
    ],
    _MODE_BUCKET_I2V: [
        "1. image_generation tool is stills-only — generate/lock the Image 2.0 plate first",
        "2. Hand off i2v to grok_build_tools (image_to_video) or xai_api imagine submit video",
        "3. Do not claim video from the Responses image_generation tool",
        "4. return_path: sequence run / sfw record + chain QA if extend",
    ],
    _MODE_BUCKET_VIDEO: [
        "1. Responses image_generation cannot emit video — retarget xai_api or grok_build_tools",
        "2. Keep this packet as the still/prompt source; submit video via Imagine REST",
        "3. Save artifacts/; do not claim success without a video URL",
        "4. return_path: QA Guardian + Director's Notes",
    ],
    _MODE_BUCKET_V2V: [
        "1. Video edit/extend is REST Video 1.0 only — use xai_api, not image_generation",
        "2. cinematic-studio imagine submit video_edit|video_extend --video-url …",
        "3. Save artifacts/ and attach job_id",
        "4. return_path: chain QA before another extend",
    ],
}

_RETURN_PATHS: dict[str, str] = {
    "clip": "sequence run / chain QA + Continuity Guardian update",
    "xai_api": "sfw record <batch> <shot> --score … --credits …",
    "grok_com_imagine": "Download result → sfw record or sequence handoff JSON + QA",
    "xai_responses_tool": "Decode image_generation_call → artifacts/ + sfw record",
    "default": "artifacts/ path + Director's Notes + QA Guardian",
}


def _mode_bucket(execution_mode: str) -> str:
    if execution_mode in ("image_prompt", "image_edit"):
        return _MODE_BUCKET_IMAGE
    if execution_mode in ("image_to_video", "reference_to_video"):
        return _MODE_BUCKET_I2V
    if execution_mode in ("video_edit", "video_extend"):
        return _MODE_BUCKET_V2V
    return _MODE_BUCKET_VIDEO


def handoff_steps(surface: str, execution_mode: str) -> list[str]:
    """Ordered steps for a surface × mode pair."""
    bucket = _mode_bucket(execution_mode)
    if surface == "grok_com_imagine":
        return list(_WEB_STEPS.get(bucket, _WEB_STEPS[_MODE_BUCKET_VIDEO]))
    if surface == "xai_api":
        return list(_XAI_API_STEPS)
    if surface == "grok_agent_acp":
        return list(_ACP_STEPS)
    if surface == "xai_responses_tool":
        return list(_RESPONSES_STEPS.get(bucket, _RESPONSES_STEPS[_MODE_BUCKET_IMAGE]))
    # grok_build_tools (default)
    steps = _BUILD_STEPS.get(bucket)
    if steps:
        return list(steps)
    return list(_BUILD_STEPS[_MODE_BUCKET_VIDEO])


def default_return_path(surface: str, context: str) -> str:
    if context == "clip":
        return _RETURN_PATHS["clip"]
    return _RETURN_PATHS.get(surface, _RETURN_PATHS["default"])


# ---------------------------------------------------------------------------
# Shared subject field extraction
# ---------------------------------------------------------------------------


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


def _raw_subject_mode(subject: dict[str, Any], override: str | None = None) -> str | None:
    return (
        override
        or subject.get("recommended_mode")
        or subject.get("decision", {}).get("mode")
    )


def _core_content(
    subject: dict[str, Any],
    *,
    context: str,
    video_model: str | None,
    prompt: str | None,
    state: dict[str, Any] | None,
) -> dict[str, Any]:
    """Shared content fields for classic and agent-mode packets."""
    vid_model = (
        video_model
        or subject.get("video_model")
        or DEFAULT_IMAGINE_VIDEO_MODEL
    )
    img_explicit = bool(subject.get("image_model"))
    img_model = subject.get("image_model") or DEFAULT_IMAGINE_IMAGE_MODEL
    description = prompt or subject.get("prompt") or subject.get("description", "")
    core: dict[str, Any] = {
        "context": context,
        "subject_id": subject.get("shot_id") or subject.get("clip_id") or "item",
        "video_model": vid_model,
        "image_model": img_model,
        "image_model_explicit": img_explicit,
        "aspect_ratio": subject.get("aspect_ratio", "16:9"),
        "video_pipeline_spec": build_video_pipeline_spec(vid_model),
        "prompt": description.strip(),
        "reference_hints": build_reference_hints(
            reference_image_id=subject.get("reference_image_id"),
            reference_url=subject.get("reference_image_url"),
            state=state,
        ),
        "sound_layer": build_sound_layer(
            dialogue=subject.get("dialogue", "")
            or ((subject.get("audio_momentum_vector") or {}).get("dialogue_state", "")),
        ),
        "grok_imagine_url": GROK_IMAGINE_URL,
    }
    if context == "clip" and subject.get("last_frame_recap"):
        core["last_frame_recap"] = subject["last_frame_recap"]
        mv = subject.get("momentum_vector") or {}
        if mv:
            core["momentum_vector"] = mv
    slug = subject.get("batch_slug") or subject.get("sequence_slug")
    if slug:
        core["slug_link"] = slug
    if subject.get("audio_momentum_vector"):
        core["audio_momentum_vector"] = subject["audio_momentum_vector"]
    if subject.get("dna_inject"):
        core["dna_inject"] = subject["dna_inject"]
    for key in ("reference_image_id", "reference_image_url", "has_reference", "has_ref"):
        val = subject.get(key)
        if val:
            core[key] = val
    return core


# ---------------------------------------------------------------------------
# Unified builder
# ---------------------------------------------------------------------------


def build_handoff(
    subject: dict[str, Any],
    *,
    context: str = "shot",
    target_surface: str | None = None,
    execution_mode: str | None = None,
    video_model: str | None = None,
    prompt: str | None = None,
    quota_note: str = (
        "Confirm remaining quota before video spend; prefer Fast mode when quality allows"
    ),
    return_path: str | None = None,
    dna_inject: str | None = None,
    qa_gate: str = "still QA ≥7 before hero video; chain QA Go before extend",
    state: dict[str, Any] | None = None,
    agent_mode: bool | None = None,
) -> dict[str, Any]:
    """
    Build a handoff packet.

    - agent_mode=False / target_surface=None → classic bridge packet (web paste).
    - agent_mode=True or target_surface set → official imagine_agent_mode_handoff.
    """
    core = _core_content(
        subject,
        context=context,
        video_model=video_model,
        prompt=prompt,
        state=state,
    )
    want_agent = agent_mode if agent_mode is not None else target_surface is not None
    raw_mode = _raw_subject_mode(subject, execution_mode)

    if not want_agent:
        # Classic bridge: soft mode normalization; web steps
        mode = normalize_execution_mode(raw_mode, strict=False)
        packet = {
            **core,
            "mode": mode,
            "handoff_steps": handoff_steps("grok_com_imagine", mode),
        }
        gate_planning_subject(packet)
        return packet

    surface = normalize_target_surface(target_surface or "grok_build_tools")
    mode = normalize_execution_mode(raw_mode, strict=True)
    is_video = is_video_execution_mode(mode)

    image_slug = core["image_model"]
    if not core.get("image_model_explicit") and mode in ("image_prompt", "image_edit"):
        image_slug = HERO_IMAGINE_IMAGE_MODEL

    packet: dict[str, Any] = {
        "packet_type": PACKET_TYPE_IMAGINE_AGENT_MODE,
        "protocol_version": PROTOCOL_VERSION,
        "studio_version": STUDIO_COMPATIBILITY_VERSION,
        "target_surface": surface,
        "execution_mode": mode,
        "context": core["context"],
        "subject_id": core["subject_id"],
        "video_model": core["video_model"],
        "image_model": image_slug,
        "aspect_ratio": core.get("aspect_ratio", "16:9"),
        "video_pipeline_spec": core["video_pipeline_spec"] if is_video else "",
        "prompt": core["prompt"],
        "reference_hints": core["reference_hints"],
        "sound_layer": core["sound_layer"] if is_video else "",
        "model_stack": {
            "chat": DEFAULT_XAI_CHAT_MODEL,
            "build": DEFAULT_XAI_BUILD_MODEL,
            "imagine_image": image_slug,
            "imagine_video": core.get("video_model") or DEFAULT_IMAGINE_VIDEO_MODEL,
        },
        "quota_note": quota_note,
        "return_path": return_path or default_return_path(surface, context),
        "handoff_steps": handoff_steps(surface, mode),
        "qa_gate": qa_gate,
        "grok_imagine_url": core.get("grok_imagine_url", GROK_IMAGINE_URL),
    }

    inject = dna_inject or core.get("dna_inject")
    if inject:
        packet["dna_inject"] = inject
    for key in ("last_frame_recap", "momentum_vector", "audio_momentum_vector", "slug_link"):
        if core.get(key):
            packet[key] = core[key]
    # Optional specialist-order checklist (DNA→Lock→Curator→Prompt→I2V)
    if state and state.get("specialist_checklist") is not None:
        from specialist_order import normalize_specialist_checklist

        packet["specialist_checklist"] = normalize_specialist_checklist(
            state.get("specialist_checklist")
        )
    # Spend-related shot fields → agent-mode packet (single contract)
    from readiness_common import SUBJECT_HANDOFF_FIELDS

    for key in SUBJECT_HANDOFF_FIELDS:
        val = subject.get(key)
        if val is not None and val != "" and key not in packet:
            packet[key] = val
    gate_planning_subject(packet)
    return packet


def build_bridge_packet(
    subject: dict[str, Any],
    *,
    context: str = "shot",
    video_model: str | None = None,
    prompt: str | None = None,
    state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Classic grok.com/imagine bridge packet (soft mode)."""
    return build_handoff(
        subject,
        context=context,
        video_model=video_model,
        prompt=prompt,
        state=state,
        agent_mode=False,
    )


def build_agent_mode_handoff(
    subject: dict[str, Any],
    *,
    target_surface: str = "grok_build_tools",
    context: str = "shot",
    execution_mode: str | None = None,
    video_model: str | None = None,
    prompt: str | None = None,
    quota_note: str = (
        "Confirm remaining quota before video spend; prefer Fast mode when quality allows"
    ),
    return_path: str | None = None,
    dna_inject: str | None = None,
    qa_gate: str = "still QA ≥7 before hero video; chain QA Go before extend",
    state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Official imagine_agent_mode_handoff packet (protocol v3.7.1)."""
    return build_handoff(
        subject,
        context=context,
        target_surface=target_surface,
        execution_mode=execution_mode,
        video_model=video_model,
        prompt=prompt,
        quota_note=quota_note,
        return_path=return_path,
        dna_inject=dna_inject,
        qa_gate=qa_gate,
        state=state,
        agent_mode=True,
    )


# ---------------------------------------------------------------------------
# Unified renderers
# ---------------------------------------------------------------------------


def _momentum_lines(mv: dict[str, Any]) -> list[str]:
    return [
        "## MOMENTUM_VECTOR",
        f"- last_action: {mv.get('last_action', mv.get('action', ''))}",
        f"- emotional_state: {mv.get('emotional_state', mv.get('emotion', ''))}",
        f"- camera_velocity: {mv.get('camera_velocity', mv.get('camera', ''))}",
        "",
    ]


def handoff_to_markdown(packet: dict[str, Any]) -> str:
    """Render classic or agent-mode packet as markdown."""
    gate_planning_subject(packet)
    if packet.get("packet_type") == PACKET_TYPE_IMAGINE_AGENT_MODE:
        return _agent_mode_markdown(packet)
    return _classic_bridge_markdown(packet)


def handoff_to_clipboard(packet: dict[str, Any]) -> str:
    """
    Single copy-paste block for generation UIs.

    Uses the packet itself (pipeline + prompt + sound + refs) — no second rebuild.
    """
    gate_planning_subject(packet)
    parts: list[str] = []
    pipeline = packet.get("video_pipeline_spec") or ""
    if pipeline:
        parts.extend([str(pipeline), ""])
    parts.append(str(packet.get("prompt", "")))
    sound = packet.get("sound_layer") or ""
    if sound:
        parts.extend(["", str(sound)])
    hints = packet.get("reference_hints") or []
    if hints:
        parts.append("")
        parts.extend(str(h) for h in hints)
    if packet.get("last_frame_recap"):
        parts.extend(["", f"LAST_FRAME_RECAP: {packet['last_frame_recap']}"])
    return "\n".join(parts)


def _classic_bridge_markdown(packet: dict[str, Any]) -> str:
    lines = [
        f"# Imagine Execution Bridge — {packet['subject_id']}",
        "",
        f"**Context:** {packet['context']} · **Mode:** `{packet.get('mode', packet.get('execution_mode', ''))}`",
        f"**Models:** `{packet['image_model']}` → `{packet['video_model']}`",
        f"**Aspect:** {packet.get('aspect_ratio', '16:9')}",
        "",
        "## VIDEO_PIPELINE_SPEC",
        "```",
        str(packet.get("video_pipeline_spec", "")),
        "```",
        "",
        "## Prompt",
        str(packet.get("prompt", "")),
        "",
    ]
    if packet.get("last_frame_recap"):
        lines += ["## LAST_FRAME_RECAP", str(packet["last_frame_recap"]), ""]
    if isinstance(packet.get("momentum_vector"), dict):
        lines += _momentum_lines(packet["momentum_vector"])
    hints = packet.get("reference_hints") or []
    if hints:
        lines += ["## Reference", *[f"- {h}" for h in hints], ""]
    lines += [
        "## Sound Layer",
        str(packet.get("sound_layer", "")),
        "",
        "## Handoff steps",
        *[str(s) for s in packet.get("handoff_steps") or []],
        "",
        f"Open: {packet.get('grok_imagine_url', GROK_IMAGINE_URL)}",
    ]
    if packet.get("slug_link"):
        lines.append(f"Studio slug: `{packet['slug_link']}`")
    return "\n".join(lines)


def _agent_mode_markdown(packet: dict[str, Any]) -> str:
    lines = [
        f"# Imagine Agent Mode Handoff v{packet.get('protocol_version', PROTOCOL_VERSION)}",
        "",
        f"**Packet:** `{packet.get('packet_type', PACKET_TYPE_IMAGINE_AGENT_MODE)}`",
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
    if isinstance(packet.get("momentum_vector"), dict):
        lines += _momentum_lines(packet["momentum_vector"])

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
        *[str(s) for s in packet.get("handoff_steps") or []],
        "",
    ]
    if packet.get("target_surface") == "grok_com_imagine":
        lines.append(f"Open: {packet.get('grok_imagine_url', GROK_IMAGINE_URL)}")
    if packet.get("slug_link"):
        lines.append(f"Studio slug: `{packet['slug_link']}`")
    lines.append("")
    lines.append(f"_Canonical protocol: {CANONICAL_PROTOCOL_DOC}_")
    return "\n".join(lines)


# Back-compat aliases
def bridge_to_markdown(packet: dict[str, Any]) -> str:
    return handoff_to_markdown(packet)


def bridge_to_clipboard(packet: dict[str, Any]) -> str:
    return handoff_to_clipboard(packet)


def agent_mode_handoff_to_markdown(packet: dict[str, Any]) -> str:
    return handoff_to_markdown(packet)
