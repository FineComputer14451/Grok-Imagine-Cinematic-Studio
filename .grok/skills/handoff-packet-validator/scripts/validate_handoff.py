#!/usr/bin/env python3
"""Validate agent handoff JSON packets for Cinematic Studio.

Field checks are data-driven from each packet schema (required / nonempty /
enums / typed / when). Packet-type special cases only remain where structure is
unique and not expressible as field rules (e.g. momentum key shape).
"""

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
        "nonempty": ("character_name", "slug"),
        "typed": {
            "key_consistency_anchors": {"list_min": 1},
        },
    },
    "sequence_extend_handoff": {
        "required": (
            "packet_type",
            "source_clip_id",
            "last_frame_recap",
            "momentum_vector",
            "audio_momentum_vector",
        ),
        "nonempty": ("source_clip_id", "last_frame_recap"),
        "typed": {
            "momentum_vector": {"object_keys": ("action", "camera", "emotion")},
            "audio_momentum_vector": "dict",
        },
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
        "nonempty": ("asset_id",),
        "enums": {
            "tier": frozenset({"hero", "standard", "draft"}),
            "status": frozenset({"draft", "approved", "locked"}),
        },
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
        "nonempty": ("source_clip_id", "emotional_residue"),
        "typed": {
            "intimacy_physics_state": "dict",
            "post_scene_state": "dict",
            "clothing_displacement_log": "list",
        },
    },
    # Declarative agent-mode schema from tools/handoff_schema.py
    PACKET_TYPE_IMAGINE_AGENT_MODE: imagine_agent_mode_packet_schema(),
}


def _nonempty(value: Any) -> bool:
    return bool(str(value).strip()) if value is not None else False


def _apply_typed_rule(
    field: str,
    value: Any,
    rule: Any,
    issues: list[str],
) -> None:
    """Apply a single typed field rule; mutates issues."""
    if rule == "list":
        if not isinstance(value, list):
            issues.append(f"{field}: must be an array")
        return
    if rule == "dict":
        if not isinstance(value, dict):
            issues.append(f"{field}: must be an object")
        return
    if not isinstance(rule, dict):
        issues.append(f"{field}: unknown typed rule {rule!r}")
        return

    if "list_min" in rule:
        min_n = int(rule["list_min"])
        if not isinstance(value, list) or len(value) < min_n:
            issues.append(f"{field}: need at least {min_n} item(s)")
        return

    if "object_keys" in rule:
        if not isinstance(value, dict):
            issues.append(f"{field}: must be an object")
            return
        for key in rule["object_keys"]:
            if not _nonempty(value.get(key, "")):
                issues.append(f"{field}: missing or empty '{key}'")
        return

    if "object_any_of" in rule:
        keys = tuple(rule["object_any_of"])
        if not isinstance(value, dict):
            issues.append(f"{field}: must be an object")
        elif not any(_nonempty(value.get(k, "")) for k in keys):
            issues.append(f"{field}: need at least one of " + "/".join(keys))
        return

    issues.append(f"{field}: unknown typed rule keys {sorted(rule)}")


def apply_schema_rules(data: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    """
    Data-driven field validation from a packet schema dict.

    Supported schema keys: required, nonempty, enums, typed, when.
    """
    issues: list[str] = []

    for field in schema.get("required", ()):
        if field not in data:
            issues.append(f"missing required field: {field}")

    for field in schema.get("nonempty", ()):
        if not _nonempty(data.get(field, "")):
            issues.append(f"empty required field: {field}")

    for field, allowed in schema.get("enums", {}).items():
        val = data.get(field)
        # Only enforce when field is present or required/nonempty
        if field not in data and field not in schema.get("required", ()) and field not in schema.get(
            "nonempty", ()
        ):
            continue
        if val not in allowed:
            issues.append(f"invalid {field}: {val}")

    typed = schema.get("typed") or {}
    for field, rule in typed.items():
        if field not in data and field not in schema.get("required", ()):
            continue
        _apply_typed_rule(field, data.get(field), rule, issues)

    for cond in schema.get("when") or ():
        when_field = cond.get("field")
        allowed = cond.get("in")
        if when_field is None or allowed is None:
            continue
        # allow "in" as schema key name for frozenset stored on schema
        if isinstance(allowed, str):
            allowed = schema.get(allowed, frozenset())
        if data.get(when_field) not in allowed:
            continue
        for field in cond.get("nonempty") or ():
            if not _nonempty(data.get(field, "")):
                # match prior agent-mode messaging for video fields
                if when_field == "execution_mode" and "video" in str(allowed).lower():
                    issues.append(f"video modes require {field}")
                else:
                    issues.append(f"empty required field: {field}")
        for field, rule in (cond.get("typed") or {}).items():
            _apply_typed_rule(field, data.get(field), rule, issues)

    return issues


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

    issues.extend(apply_schema_rules(data, schema))
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
