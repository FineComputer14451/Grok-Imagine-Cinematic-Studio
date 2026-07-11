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
from handoff_readiness import evaluate_imagine_handoff_readiness  # noqa: E402

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

# Identity Continuity Protocol: warn-only when drift_evidence is missing/incomplete
EXTEND_PACKET_TYPES_WARN_IF_NO_DRIFT = frozenset({
    "sequence_extend_handoff",
    "identity_lock_handoff",
})

DRIFT_EVIDENCE_STATUSES = frozenset({"pass", "risk", "incomplete", "skipped"})
DRIFT_EVIDENCE_REQUIRED = (
    "schema_version",
    "protocol",
    "protocol_version",
    "clip_id",
    "character_slug",
    "scored_at",
    "tool",
    "score",
    "threshold",
    "status",
    "attempt",
)


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


def _iter_drift_evidence_items(data: dict[str, Any]) -> list[dict[str, Any]]:
    raw = data.get("drift_evidence")
    if raw is None:
        return []
    if isinstance(raw, dict):
        return [raw]
    if isinstance(raw, list):
        return [x for x in raw if isinstance(x, dict)]
    return []


def validate_drift_evidence_section(data: dict[str, Any]) -> tuple[list[str], list[str]]:
    """
    Returns (issues, warnings) for drift_evidence.

    Missing section on extend / identity-lock packets → warning only.
    Invalid status enum when section present → hard issue.
    Incomplete fields, skipped without reason, risk/incomplete status → warnings.
    """
    issues: list[str] = []
    warnings: list[str] = []
    packet_type = data.get("packet_type")
    raw = data.get("drift_evidence", "__missing__")

    if raw == "__missing__" or raw is None:
        if packet_type in EXTEND_PACKET_TYPES_WARN_IF_NO_DRIFT:
            warnings.append(
                "drift_evidence missing — run sequence drift-score (ICP-02/03); "
                "see references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md"
            )
        return issues, warnings

    if not isinstance(raw, (dict, list)):
        issues.append("drift_evidence: must be an object or array of objects")
        return issues, warnings

    items = _iter_drift_evidence_items(data)
    if isinstance(raw, list) and not items:
        issues.append("drift_evidence: array must contain objects")
        return issues, warnings

    for i, item in enumerate(items):
        prefix = (
            f"drift_evidence[{i}]"
            if len(items) > 1 or isinstance(raw, list)
            else "drift_evidence"
        )
        for field in DRIFT_EVIDENCE_REQUIRED:
            if field not in item:
                warnings.append(f"{prefix}: missing field '{field}' (incomplete evidence)")
        status = item.get("status")
        if status is not None and status not in DRIFT_EVIDENCE_STATUSES:
            issues.append(f"{prefix}: invalid status: {status}")
        if status == "skipped" and not str(item.get("skipped_reason") or "").strip():
            warnings.append(f"{prefix}: status=skipped requires skipped_reason")
        if status == "risk":
            warnings.append(
                f"{prefix}: status=risk score={item.get('score')} "
                f"(threshold={item.get('threshold')}) — recommend ICP-07 fix"
            )
        if status == "incomplete":
            warnings.append(f"{prefix}: status=incomplete — run sequence drift-score")
        baseline = item.get("baseline")
        if isinstance(baseline, dict) and not str(baseline.get("dna_slug") or "").strip():
            warnings.append(f"{prefix}: baseline.dna_slug empty")
        elif baseline is None and "baseline" not in item:
            warnings.append(f"{prefix}: missing baseline.dna_slug")

    return issues, warnings


def validate_packet_with_warnings(
    data: dict[str, Any],
    *,
    strict_handoff: bool = False,
) -> tuple[list[str], list[str]]:
    """Return (hard issues, soft warnings). Hard issues fail validation."""
    issues: list[str] = []
    packet_type = data.get("packet_type")
    if not packet_type:
        return ["missing packet_type"], []
    schema = PACKET_TYPES.get(packet_type)
    if not schema:
        return [f"unknown packet_type: {packet_type}"], []
    issues.extend(apply_schema_rules(data, schema))
    drift_issues, warnings = validate_drift_evidence_section(data)
    issues.extend(drift_issues)
    # Semantic readiness for agent-mode packets (default soft; --strict-handoff hard-fails)
    if not issues and packet_type == PACKET_TYPE_IMAGINE_AGENT_MODE:
        ready = evaluate_imagine_handoff_readiness(data)
        for b in ready.get("blockers") or []:
            msg = f"readiness blocker: {b}"
            if strict_handoff:
                issues.append(msg)
            else:
                warnings.append(msg)
        for w in ready.get("warnings") or []:
            warnings.append(f"readiness: {w}")
    return issues, warnings


def validate_packet(
    data: dict[str, Any],
    *,
    strict_handoff: bool = False,
) -> list[str]:
    issues, _warnings = validate_packet_with_warnings(
        data, strict_handoff=strict_handoff
    )
    return issues


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate Cinematic Studio handoff JSON packets"
    )
    parser.add_argument("path", type=Path, help="Path to handoff.json")
    parser.add_argument(
        "--strict-handoff",
        action="store_true",
        help=(
            "Treat imagine_agent_mode_handoff readiness blockers as hard failures "
            "(exit 1); default is warn-only"
        ),
    )
    args = parser.parse_args()
    path: Path = args.path

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

    issues, warnings = validate_packet_with_warnings(
        data, strict_handoff=args.strict_handoff
    )
    for w in warnings:
        print(f"⚠️  {w}")
    if issues:
        print(f"❌ Handoff validation failed ({path.name})")
        for issue in issues:
            print(f"  • {issue}")
        return 1

    if warnings:
        print(f"✅ Handoff valid with warnings: {data.get('packet_type')}")
    else:
        print(f"✅ Handoff valid: {data.get('packet_type')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
