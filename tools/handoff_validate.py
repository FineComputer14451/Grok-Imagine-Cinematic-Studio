"""Validate handoff JSON packets (schema + soft readiness).

Loads the canonical handoff-packet-validator logic from the skill script when
present; falls back to a minimal packet_type + required-field check.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

from studio_paths import STUDIO_ROOT


def _validator_script_paths() -> list[Path]:
    return [
        STUDIO_ROOT / ".grok" / "skills" / "handoff-packet-validator" / "scripts" / "validate_handoff.py",
        Path.home()
        / ".grok"
        / "skills"
        / "handoff-packet-validator"
        / "scripts"
        / "validate_handoff.py",
    ]


def load_skill_validator() -> Any | None:
    """Import validate_handoff module from skill scripts, or None."""
    for path in _validator_script_paths():
        if not path.is_file():
            continue
        try:
            spec = importlib.util.spec_from_file_location(
                "cinematic_validate_handoff", path
            )
            if spec is None or spec.loader is None:
                continue
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, "validate_packet_with_warnings"):
                return mod
        except Exception:
            continue
    return None


def validate_handoff_data(
    data: dict[str, Any],
    *,
    strict_handoff: bool = False,
    strict_wave_a: bool = False,
) -> dict[str, Any]:
    """
    Return {ok, issues, warnings, packet_type, source}.
    ok=True when issues is empty (warnings allowed).
    """
    mod = load_skill_validator()
    if mod is not None:
        issues, warnings = mod.validate_packet_with_warnings(
            data,
            strict_handoff=strict_handoff,
            strict_wave_a=strict_wave_a,
        )
        return {
            "ok": not issues,
            "issues": list(issues),
            "warnings": list(warnings),
            "packet_type": data.get("packet_type"),
            "source": "skill_validator",
        }

    # Minimal fallback
    issues: list[str] = []
    ptype = data.get("packet_type")
    if not ptype:
        issues.append("missing packet_type")
    return {
        "ok": not issues,
        "issues": issues,
        "warnings": ["full skill validator unavailable — minimal check only"],
        "packet_type": ptype,
        "source": "fallback",
    }


def validate_handoff_file(
    path: str | Path,
    *,
    strict_handoff: bool = False,
    strict_wave_a: bool = False,
) -> dict[str, Any]:
    """Load JSON path and validate. ok=False on IO/JSON errors."""
    p = Path(path).expanduser()
    if not p.is_file():
        return {
            "ok": False,
            "issues": [f"file not found: {p}"],
            "warnings": [],
            "packet_type": None,
            "source": "io",
            "path": str(p),
        }
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {
            "ok": False,
            "issues": [f"invalid JSON: {exc}"],
            "warnings": [],
            "packet_type": None,
            "source": "io",
            "path": str(p),
        }
    if not isinstance(data, dict):
        return {
            "ok": False,
            "issues": ["root must be a JSON object"],
            "warnings": [],
            "packet_type": None,
            "source": "io",
            "path": str(p),
        }
    result = validate_handoff_data(
        data, strict_handoff=strict_handoff, strict_wave_a=strict_wave_a
    )
    result["path"] = str(p)
    return result


def format_validation_report(result: dict[str, Any]) -> str:
    lines = [
        f"Handoff validate · {result.get('path') or 'memory'}",
        f"packet_type: {result.get('packet_type') or '—'}",
        f"source: {result.get('source')}",
        f"status: {'OK' if result.get('ok') else 'FAIL'}",
    ]
    issues = result.get("issues") or []
    warnings = result.get("warnings") or []
    if issues:
        lines.append("Issues:")
        for i in issues:
            lines.append(f"  • {i}")
    if warnings:
        lines.append("Warnings:")
        for w in warnings:
            lines.append(f"  • {w}")
    if result.get("ok") and not warnings:
        lines.append("No issues or warnings.")
    return "\n".join(lines)
