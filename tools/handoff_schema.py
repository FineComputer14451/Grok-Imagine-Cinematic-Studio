#!/usr/bin/env python3
"""
Canonical Imagine Agent Mode Handoff schema (studio v3.7.1+).

Single source of truth for target surfaces, execution modes, and protocol
metadata. Imported by:
  - tools/imagine_bridge.py (packet builders)
  - .grok/skills/handoff-packet-validator/scripts/validate_handoff.py
  - tools/cli/imagine_commands.py (via imagine_bridge re-exports)

Do not duplicate these frozensets elsewhere.
"""

from __future__ import annotations

from typing import Any

from models import STUDIO_COMPATIBILITY_VERSION

# Protocol ships with the studio release; single source so pins cannot drift.
PROTOCOL_VERSION = STUDIO_COMPATIBILITY_VERSION
PACKET_TYPE_IMAGINE_AGENT_MODE = "imagine_agent_mode_handoff"

# Human-readable protocol — single doc of record (skill mirrors are pointers only)
CANONICAL_PROTOCOL_DOC = "references/agents/IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md"

TARGET_SURFACES: frozenset[str] = frozenset(
    {
        "grok_build_tools",
        "grok_agent_acp",
        "grok_com_imagine",
        "xai_api",
    }
)

EXECUTION_MODES: frozenset[str] = frozenset(
    {
        "image_prompt",
        "image_edit",
        "image_to_video",
        "video_prompt",
        "reference_to_video",
    }
)

VIDEO_EXECUTION_MODES: frozenset[str] = frozenset(
    {
        "image_to_video",
        "video_prompt",
        "reference_to_video",
    }
)

# Legacy / shorthand modes from batch subjects → official execution_mode
EXECUTION_MODE_ALIASES: dict[str, str] = {
    "image": "image_prompt",
    "still": "image_prompt",
    "i2v": "image_to_video",
    "video": "video_prompt",
    "t2v": "video_prompt",
}

# Fields always required on imagine_agent_mode_handoff packets
IMAGINE_AGENT_MODE_REQUIRED_FIELDS: tuple[str, ...] = (
    "packet_type",
    "protocol_version",
    "studio_version",
    "target_surface",
    "execution_mode",
    "subject_id",
    "prompt",
    "reference_hints",
    "model_stack",
    "quota_note",
    "return_path",
    "handoff_steps",
)

# Extra required when execution_mode ∈ VIDEO_EXECUTION_MODES
IMAGINE_AGENT_MODE_VIDEO_REQUIRED_FIELDS: tuple[str, ...] = (
    "video_pipeline_spec",
    "sound_layer",
)

# model_stack keys accepted for non-empty check
MODEL_STACK_KEYS: tuple[str, ...] = ("chat", "build", "imagine_image", "imagine_video")


def is_video_execution_mode(mode: str | None) -> bool:
    return mode in VIDEO_EXECUTION_MODES


def resolve_execution_mode(
    subject: dict[str, Any] | None,
    *,
    execution_mode: str | None = None,
) -> str:
    """Resolve execution mode from explicit override or subject fields (batch/shot)."""
    subj = subject if isinstance(subject, dict) else {}
    mode = (
        execution_mode
        or subj.get("execution_mode")
        or subj.get("recommended_mode")
        or (subj.get("decision") or {}).get("mode")
        or ""
    )
    return str(mode).strip()


def normalize_execution_mode(
    raw: str | None,
    *,
    default: str = "video_prompt",
    strict: bool = False,
) -> str:
    """
    Map subject/CLI mode strings to an official EXECUTION_MODES value.

    strict=False (classic bridge): unknown → default
    strict=True (agent-mode builder): unknown → ValueError
    """
    if not raw:
        return default
    key = str(raw).strip()
    normalized = EXECUTION_MODE_ALIASES.get(key, key)
    if normalized not in EXECUTION_MODES:
        if strict:
            raise ValueError(
                f"invalid execution_mode: {raw!r}; "
                f"expected one of {sorted(EXECUTION_MODES)} "
                f"(aliases: {sorted(EXECUTION_MODE_ALIASES)})"
            )
        return default
    return normalized


def normalize_target_surface(surface: str) -> str:
    """Return surface if valid; raise ValueError otherwise."""
    cleaned = surface.strip()
    if cleaned not in TARGET_SURFACES:
        raise ValueError(
            f"invalid target_surface: {surface!r}; "
            f"expected one of {sorted(TARGET_SURFACES)}"
        )
    return cleaned


def imagine_agent_mode_packet_schema() -> dict[str, Any]:
    """
    Declarative schema for PACKET_TYPES['imagine_agent_mode_handoff'].

    Consumed by the handoff validator's data-driven engine (no packet-type
    special-case branches for agent-mode fields).

    Keys:
      required   — must be present
      nonempty   — must be non-empty strings after strip
      enums      — field → allowed frozenset
      typed      — field → type rule (list | list_min | object_any_of | …)
      when       — conditional rules when field ∈ set
    """
    return {
        "required": IMAGINE_AGENT_MODE_REQUIRED_FIELDS,
        "nonempty": (
            "subject_id",
            "prompt",
            "quota_note",
            "return_path",
            "protocol_version",
            "studio_version",
        ),
        "enums": {
            "target_surface": TARGET_SURFACES,
            "execution_mode": EXECUTION_MODES,
        },
        "typed": {
            "reference_hints": "list",
            "handoff_steps": {"list_min": 1},
            "model_stack": {"object_any_of": MODEL_STACK_KEYS},
        },
        "when": (
            {
                "field": "execution_mode",
                "in": VIDEO_EXECUTION_MODES,
                "nonempty": IMAGINE_AGENT_MODE_VIDEO_REQUIRED_FIELDS,
            },
        ),
        # kept for callers that still read these keys directly
        "target_surfaces": TARGET_SURFACES,
        "execution_modes": EXECUTION_MODES,
        "video_modes": VIDEO_EXECUTION_MODES,
        "video_required": IMAGINE_AGENT_MODE_VIDEO_REQUIRED_FIELDS,
        "model_stack_keys": MODEL_STACK_KEYS,
    }
