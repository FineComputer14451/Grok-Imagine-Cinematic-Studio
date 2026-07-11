#!/usr/bin/env python3
"""Semantic readiness checks for Imagine Agent Mode handoff packets."""

from __future__ import annotations

from typing import Any

from handoff_schema import (
    PACKET_TYPE_IMAGINE_AGENT_MODE,
    is_video_execution_mode,
)
from specialist_order import evaluate_specialist_order
from studio_paths import STUDIO_ROOT

MOTION_CUES = (
    "motion",
    "camera",
    "dolly",
    "pan",
    "tilt",
    "track",
    "ken burns",
    "first frame",
    "i2v",
    "extend",
    "momentum",
    "lip-sync",
    "lip sync",
    "physics",
)
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
PROTOCOL_OK = frozenset({"3.7.1", "3.8.0", "3.8.1", "3.8.2"})


def _studio_version() -> str:
    vf = STUDIO_ROOT / "VERSION"
    if vf.is_file():
        return vf.read_text(encoding="utf-8").strip() or "3.8.2"
    return "3.8.2"


def _has_cue(text: str, cues: tuple[str, ...]) -> bool:
    low = (text or "").lower()
    return any(c in low for c in cues)


def evaluate_imagine_handoff_readiness(
    packet: dict[str, Any],
    *,
    studio_version: str | None = None,
) -> dict[str, Any]:
    """
    Semantic readiness for imagine_agent_mode_handoff.

    pass=False only when blockers present. warnings alone keep pass=True.
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
    prompt = str(packet.get("prompt") or "")
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
        motion_ok = _has_cue(prompt, MOTION_CUES)
        for key in ("i2v_motion_block", "motion_vector", "motion_block"):
            val = packet.get(key)
            if isinstance(val, dict) and any(str(v).strip() for v in val.values()):
                motion_ok = True
            if isinstance(val, str) and val.strip():
                motion_ok = True
        if not motion_ok:
            blockers.append(
                "GHR-03: video mode prompt lacks motion/I2V cues "
                "(e.g. dolly, first frame, momentum, lip-sync)"
            )
            fixes.append(
                "Activate I2V Specialist; add MOTION_VECTOR language to prompt"
            )

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

    return {
        "pass": len(blockers) == 0,
        "strict": True,
        "skipped": False,
        "warnings": warnings,
        "blockers": blockers,
        "fixes": fixes,
        "checks": checks,
        "specialist_order": order,
    }
