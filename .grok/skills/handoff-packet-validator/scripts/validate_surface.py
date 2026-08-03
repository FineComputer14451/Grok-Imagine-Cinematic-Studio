#!/usr/bin/env python3
"""Surface bridge validation for Imagine Agent Mode Handoff packets.

Standalone checker — does not require the full studio tools/ tree.
Validates that target_surface is known and that the packet acknowledges
the required supporting skill / bridge for that surface.

Usage:
  python validate_surface.py path/to/packet.json
  python validate_surface.py path/to/packet.json --strict
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

VALID_SURFACES = frozenset({
    "grok_build_tools",
    "grok_agent_acp",
    "grok_com_imagine",
    "xai_api",
})

SURFACE_REQUIREMENTS: dict[str, dict[str, str]] = {
    "grok_build_tools": {
        "skill": "grok-imagine-image-tools",
        "bridge": "GROK_IMAGINE_IMAGE_TOOLS_BRIDGE.md",
        "note": "Prompt craft, code-vs-image, reference-first, consistency",
    },
    "grok_agent_acp": {
        "skill": "inherits Surface A (or D)",
        "bridge": "(see handoff protocol Surface B clarification)",
        "note": "Must follow A rules when local tools available; D rules if routing to API",
    },
    "grok_com_imagine": {
        "skill": "paste-friendly packet rules",
        "bridge": "GROK_COM_IMAGINE_BRIDGE.md",
        "note": "Manual paste path; still respect prompt craft from grok-imagine-image-tools",
    },
    "xai_api": {
        "skill": "xai-grok-skill",
        "bridge": "XAI_API_SURFACE_BRIDGE.md",
        "note": "Real injected key, Responses API preferred, server-only, quota care",
    },
}


def validate_surface(packet: dict[str, Any], strict: bool = False) -> list[str]:
    """Return list of error messages (empty = pass)."""
    errors: list[str] = []

    packet_type = packet.get("packet_type")
    if packet_type != "imagine_agent_mode_handoff":
        return errors

    surface = packet.get("target_surface")
    if not surface:
        errors.append("missing required field: target_surface")
        return errors

    if surface not in VALID_SURFACES:
        errors.append(
            f"invalid target_surface '{surface}'. "
            f"Allowed: {sorted(VALID_SURFACES)}"
        )
        return errors

    req = SURFACE_REQUIREMENTS[surface]

    text_blob = " ".join(
        str(packet.get(k, ""))
        for k in (
            "quota_note",
            "return_path",
            "handoff_steps",
            "notes",
            "bridge_ack",
            "supporting_skills",
            "surface_notes",
        )
    ).lower()

    skill_token = req["skill"].lower().split()[0]
    bridge_token = req["bridge"].lower().replace(".md", "")

    acknowledged = (
        skill_token in text_blob
        or bridge_token in text_blob
        or "surface_bridges_index" in text_blob
        or packet.get("bridge_ack") is True
        or packet.get("surface_validated") is True
    )

    if not acknowledged:
        msg = (
            f"surface '{surface}' requires supporting guidance "
            f"({req['skill']} / {req['bridge']}). "
            f"Add bridge_ack=true or reference the skill/bridge in notes/quota_note/handoff_steps."
        )
        if strict:
            errors.append(msg)
        else:
            errors.append(f"[warn] {msg}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate target_surface + bridge requirements")
    parser.add_argument("packet", type=Path, help="Path to handoff JSON packet")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat missing bridge acknowledgement as a hard error",
    )
    args = parser.parse_args()

    if not args.packet.is_file():
        print(f"ERROR: file not found: {args.packet}", file=sys.stderr)
        return 2

    try:
        data = json.loads(args.packet.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid JSON: {e}", file=sys.stderr)
        return 2

    if not isinstance(data, dict):
        print("ERROR: packet root must be a JSON object", file=sys.stderr)
        return 2

    errors = validate_surface(data, strict=args.strict)

    hard = [e for e in errors if not e.startswith("[warn]")]
    warns = [e for e in errors if e.startswith("[warn]")]

    for w in warns:
        print(w)
    for e in hard:
        print(f"ERROR: {e}")

    if hard:
        print("SURFACE VALIDATION: FAIL")
        return 1

    surface = data.get("target_surface", "?")
    if warns:
        print(f"SURFACE VALIDATION: PASS (with warnings) — surface={surface}")
    else:
        print(f"SURFACE VALIDATION: PASS — surface={surface}")
        if surface in SURFACE_REQUIREMENTS:
            req = SURFACE_REQUIREMENTS[surface]
            print(f"  required: {req['skill']} + {req['bridge']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
