#!/usr/bin/env python3
"""Validate agent handoff JSON packets for Cinematic Studio."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

# Resolve studio tools/ so we can import the canonical handoff schema
_SCRIPT = Path(__file__).resolve()
_STUDIO_ROOT = _SCRIPT.parents[4]  # .../.grok/skills/<skill>/scripts → repo root
_TOOLS = _STUDIO_ROOT / "tools"
if _TOOLS.is_dir() and str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from handoff_schema import (  # noqa: E402
    MODEL_STACK_KEYS,
    PACKET_TYPE_IMAGINE_AGENT_MODE,
    imagine_agent_mode_packet_schema,
)

PACKET_TYPES: dict[str, dict[str, Any]] = {
    "identity_lock_handoff": {
        "required": (
            "packet_type",
            "character_name",
            "slug",
            "dna_profile",
            "prompt_injection",
            "key_consistency_anchors",
        ),
    },
    "sequence_extend_handoff": {
        "required": (
            "packet_type",
            "source_clip_id",
            "last_frame_recap",
            "momentum_vector",
            "audio_momentum_vector",
        ),
        "momentum_keys": ("action", "camera", "emotion"),
    },
    "asset_manifest_entry": {
        "required": (
            "packet_type",
            "asset_id",
            "tier",
            "image_model",
            "video_model",
            "status",
        ),
        "tier_values": frozenset({"hero", "standard", "draft"}),
        "status_values": frozenset({"draft", "approved", "locked"}),
    },
    "intimacy_state_handoff": {
        "required": (
            "packet_type",
            "source_clip_id",
            "intimacy_physics_state",
            "post_scene_state",
            "clothing_displacement_log",
            "emotional_residue",
        ),
    },
    # Surfaces / modes come from tools/handoff_schema.py — do not re-list here
    PACKET_TYPE_IMAGINE_AGENT_MODE: imagine_agent_mode_packet_schema(),
}


def _check_momentum_vector(mv: Any, label: str, issues: list[str]) -> None:
    if not isinstance(mv, dict):
        issues.append(f"{label}: must be an object")
        return
    for key in ("action", "camera", "emotion"):
        if not str(mv.get(key, "")).strip():
            issues.append(f"{label}: missing or empty '{key}'")


def validate_packet(data: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    packet_type = data.get("packet_type")
    if not packet_type:
        issues.append("missing packet_type")
        return issues

    schema = PACKET_TYPES.get(packet_type)
    if not schema:
        issues.append(f"unknown packet_type: {packet_type}")
        return issues

    for field in schema["required"]:
        if field not in data:
            issues.append(f"missing required field: {field}")
        elif field in ("last_frame_recap", "character_name", "asset_id") and not str(data[field]).strip():
            issues.append(f"empty required field: {field}")

    if packet_type == "sequence_extend_handoff":
        _check_momentum_vector(data.get("momentum_vector"), "momentum_vector", issues)
        amv = data.get("audio_momentum_vector")
        if not isinstance(amv, dict):
            issues.append("audio_momentum_vector: must be an object")

    if packet_type == "asset_manifest_entry":
        tier = data.get("tier")
        if tier not in schema.get("tier_values", ()):
            issues.append(f"invalid tier: {tier}")
        status = data.get("status")
        if status not in schema.get("status_values", ()):
            issues.append(f"invalid status: {status}")

    if packet_type == "identity_lock_handoff":
        anchors = data.get("key_consistency_anchors")
        if not isinstance(anchors, list) or len(anchors) < 1:
            issues.append("key_consistency_anchors: need at least one anchor")

    if packet_type == "intimacy_state_handoff":
        if not str(data.get("source_clip_id", "")).strip():
            issues.append("empty required field: source_clip_id")
        if not isinstance(data.get("intimacy_physics_state"), dict):
            issues.append("intimacy_physics_state: must be an object")
        if not isinstance(data.get("post_scene_state"), dict):
            issues.append("post_scene_state: must be an object")
        log = data.get("clothing_displacement_log")
        if not isinstance(log, list):
            issues.append("clothing_displacement_log: must be an array")
        if not str(data.get("emotional_residue", "")).strip():
            issues.append("empty required field: emotional_residue")

    if packet_type == PACKET_TYPE_IMAGINE_AGENT_MODE:
        if not str(data.get("subject_id", "")).strip():
            issues.append("empty required field: subject_id")
        if not str(data.get("prompt", "")).strip():
            issues.append("empty required field: prompt")
        surface = data.get("target_surface")
        if surface not in schema.get("target_surfaces", ()):
            issues.append(f"invalid target_surface: {surface}")
        mode = data.get("execution_mode")
        if mode not in schema.get("execution_modes", ()):
            issues.append(f"invalid execution_mode: {mode}")
        if not isinstance(data.get("reference_hints"), list):
            issues.append("reference_hints: must be an array")
        stack = data.get("model_stack")
        stack_keys = schema.get("model_stack_keys") or MODEL_STACK_KEYS
        if not isinstance(stack, dict):
            issues.append("model_stack: must be an object")
        elif not any(str(stack.get(k, "")).strip() for k in stack_keys):
            issues.append(
                "model_stack: need at least one of " + "/".join(stack_keys)
            )
        steps = data.get("handoff_steps")
        if not isinstance(steps, list) or len(steps) < 1:
            issues.append("handoff_steps: need at least one step")
        if not str(data.get("quota_note", "")).strip():
            issues.append("empty required field: quota_note")
        if not str(data.get("return_path", "")).strip():
            issues.append("empty required field: return_path")
        if mode in schema.get("video_modes", ()):
            for field in schema.get("video_required") or ("video_pipeline_spec", "sound_layer"):
                if not str(data.get(field, "")).strip():
                    issues.append(f"video modes require {field}")

    return issues


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: validate_handoff.py <handoff.json>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"File not found: {path}", file=sys.stderr)
        return 2

    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON: {exc}", file=sys.stderr)
        return 1

    if not isinstance(data, dict):
        print("Root must be a JSON object", file=sys.stderr)
        return 1

    issues = validate_packet(data)
    if issues:
        print(f"❌ Handoff validation failed ({path.name})")
        for issue in issues:
            print(f"  • {issue}")
        return 1

    print(f"✅ Handoff valid: {data.get('packet_type')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
