#!/usr/bin/env python3
"""Semantic readiness checks for Imagine Agent Mode handoff packets."""

from __future__ import annotations

from typing import Any

from handoff_schema import (
    PACKET_TYPE_IMAGINE_AGENT_MODE,
    is_video_execution_mode,
)
from motion_readiness import MOTION_CUES, evaluate_motion_brief_readiness
from plate_readiness import evaluate_plate_lock_readiness
from specialist_order import evaluate_specialist_order
from studio_paths import STUDIO_ROOT

# Re-export for tests / callers that imported MOTION_CUES from here
__all__ = ("MOTION_CUES", "evaluate_imagine_handoff_readiness")

RETURN_CUES = (
    "qa",
    "record",
    "chain",
    "artifact",
    "sfw",
    "sequence",
    "handoff",
    "validate",
    "polish",
)
PLACEHOLDER_QUOTA = frozenset({"todo", "tbd", "n/a", "na", "none", "-", "—"})
PROTOCOL_OK = frozenset({"3.7.1", "3.8.0", "3.8.1", "3.8.2", "3.8.3"})


def _studio_version() -> str:
    vf = STUDIO_ROOT / "VERSION"
    if vf.is_file():
        return vf.read_text(encoding="utf-8").strip() or "3.8.3"
    return "3.8.3"


def _has_cue(text: str, cues: tuple[str, ...]) -> bool:
    low = (text or "").lower()
    return any(c in low for c in cues)


def evaluate_imagine_handoff_readiness(
    packet: dict[str, Any],
    *,
    studio_version: str | None = None,
    strict_motion: bool = False,
) -> dict[str, Any]:
    """
    Semantic readiness for imagine_agent_mode_handoff.

    pass=False only when blockers present. warnings alone keep pass=True.
    strict_motion=True (CLI --strict-handoff): require full motion_vector triple.
    """
    if packet.get("packet_type") != PACKET_TYPE_IMAGINE_AGENT_MODE:
        return {
            "pass": True,
            "strict": True,
            "skipped": True,
            "warnings": [],
            "blockers": [],
            "fixes": [],
            "checks": [],
        }

    warnings: list[str] = []
    blockers: list[str] = []
    fixes: list[str] = []
    checks: list[dict[str, Any]] = []
    mode = str(packet.get("execution_mode") or "")
    refs = packet.get("reference_hints")
    if not isinstance(refs, list):
        refs = []

    if is_video_execution_mode(mode):
        if mode in ("image_to_video", "reference_to_video") and len(refs) == 0:
            blockers.append(
                f"GHR-02: reference_hints empty for still→video mode ({mode})"
            )
            fixes.append(
                "Add locked plate reference_image_id / path to reference_hints"
            )
        # GHR-03 — motion brief (structured preferred; free-text soft fallback)
        motion = evaluate_motion_brief_readiness(
            packet, execution_mode=mode, strict=strict_motion
        )
        for w in motion.get("warnings") or []:
            if w not in warnings:
                warnings.append(w if w.startswith("MB-") else f"GHR-03: {w}")
        for b in motion.get("blockers") or []:
            # Keep MB-* ids; map legacy message under GHR-03 when unstructured miss
            if b not in blockers:
                blockers.append(b)
        for f in motion.get("fixes") or []:
            if f not in fixes:
                fixes.append(f)
        checks.extend(motion.get("checks") or [])
    else:
        motion = {
            "pass": True,
            "skipped": True,
            "warnings": [],
            "blockers": [],
            "fixes": [],
            "checks": [],
        }

    ret = str(packet.get("return_path") or "")
    if not _has_cue(ret, RETURN_CUES):
        blockers.append(
            "GHR-04: return_path missing re-entry cue "
            "(qa/record/chain/artifact/sfw/sequence/…)"
        )
        fixes.append(
            "Set return_path e.g. 'sfw record + QA Guardian' or 'chain QA'"
        )

    quota = str(packet.get("quota_note") or "").strip().lower()
    if quota in PLACEHOLDER_QUOTA:
        warnings.append("GHR-05: quota_note looks like a placeholder")
        fixes.append("Replace quota_note with a real budget/Fast-mode note")

    current = studio_version or _studio_version()
    pkt_ver = str(packet.get("studio_version") or "").strip()
    if pkt_ver and current and pkt_ver != current:
        warnings.append(
            f"GHR-06: studio_version={pkt_ver!r} differs from current {current!r}"
        )

    proto = str(packet.get("protocol_version") or "").strip()
    if proto and proto not in PROTOCOL_OK and proto != current:
        warnings.append(
            f"GHR-07: protocol_version={proto!r} not in known allowlist"
        )

    steps = packet.get("handoff_steps")
    if isinstance(steps, list) and len(steps) < 2:
        warnings.append("GHR-08: handoff_steps has fewer than 2 steps")

    # GHR-09 / GHR-10 — specialist order (DNA→Lock→Curator→Prompt→I2V)
    order = evaluate_specialist_order(packet, execution_mode=mode)
    warnings.extend(order.get("warnings") or [])
    blockers.extend(order.get("blockers") or [])
    for f in order.get("fixes") or []:
        if f not in fixes:
            fixes.append(f)
    checks.extend(order.get("checks") or [])

    # GHR-11 — plate lock (approved/locked) for still→video modes
    plate = evaluate_plate_lock_readiness(packet, execution_mode=mode)
    for w in plate.get("warnings") or []:
        if w not in warnings:
            warnings.append(w)
    for b in plate.get("blockers") or []:
        # Prefix with GHR-11 for handoff lineage when not already PL-*
        label = b if b.startswith("PL-") or b.startswith("GHR-") else f"GHR-11: {b}"
        if label not in blockers and b not in blockers:
            blockers.append(b if b.startswith("PL-") else label)
    for f in plate.get("fixes") or []:
        if f not in fixes:
            fixes.append(f)
    checks.extend(plate.get("checks") or [])

    return {
        "pass": len(blockers) == 0,
        "strict": True,
        "skipped": False,
        "warnings": warnings,
        "blockers": blockers,
        "fixes": fixes,
        "checks": checks,
        "specialist_order": order,
        "plate_lock": plate,
        "motion_brief": motion,
    }
