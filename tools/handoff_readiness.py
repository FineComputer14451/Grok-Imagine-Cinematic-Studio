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
from readiness_common import empty_readiness_report, merge_readiness, recompute_pass
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
PROTOCOL_OK = frozenset({"3.7.1", "3.8.0", "3.8.1", "3.8.2", "3.8.3", "3.8.4", "3.8.5", "3.8.6", "3.8.7", "3.8.8", "3.8.9"})


def _studio_version() -> str:
    vf = STUDIO_ROOT / "VERSION"
    if vf.is_file():
        return vf.read_text(encoding="utf-8").strip() or "3.8.9"
    return "3.8.9"


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

    pass=False only when blockers present. Soft CLI still emits unless --strict-handoff.
    strict_motion=True: require full motion_vector triple (same as --strict-handoff).
    """
    if packet.get("packet_type") != PACKET_TYPE_IMAGINE_AGENT_MODE:
        return empty_readiness_report(skipped=True)

    report = empty_readiness_report(strict=True)
    mode = str(packet.get("execution_mode") or "")
    refs = packet.get("reference_hints")
    if not isinstance(refs, list):
        refs = []

    motion: dict[str, Any] = empty_readiness_report(skipped=True)
    plate: dict[str, Any] = empty_readiness_report(skipped=True)
    order: dict[str, Any] = empty_readiness_report(skipped=True)

    if is_video_execution_mode(mode):
        if mode in ("image_to_video", "reference_to_video") and len(refs) == 0:
            report["blockers"].append(
                f"GHR-02: reference_hints empty for still→video mode ({mode})"
            )
            report["fixes"].append(
                "Add locked plate reference_image_id / path to reference_hints"
            )
        motion = evaluate_motion_brief_readiness(
            packet, execution_mode=mode, strict=strict_motion
        )
        merge_readiness(report, motion)

    ret = str(packet.get("return_path") or "")
    if not _has_cue(ret, RETURN_CUES):
        report["blockers"].append(
            "GHR-04: return_path missing re-entry cue "
            "(qa/record/chain/artifact/sfw/sequence/…)"
        )
        report["fixes"].append(
            "Set return_path e.g. 'sfw record + QA Guardian' or 'chain QA'"
        )

    quota = str(packet.get("quota_note") or "").strip().lower()
    if quota in PLACEHOLDER_QUOTA:
        report["warnings"].append("GHR-05: quota_note looks like a placeholder")
        report["fixes"].append("Replace quota_note with a real budget/Fast-mode note")

    current = studio_version or _studio_version()
    pkt_ver = str(packet.get("studio_version") or "").strip()
    if pkt_ver and current and pkt_ver != current:
        report["warnings"].append(
            f"GHR-06: studio_version={pkt_ver!r} differs from current {current!r}"
        )

    proto = str(packet.get("protocol_version") or "").strip()
    if proto and proto not in PROTOCOL_OK and proto != current:
        report["warnings"].append(
            f"GHR-07: protocol_version={proto!r} not in known allowlist"
        )

    steps = packet.get("handoff_steps")
    if isinstance(steps, list) and len(steps) < 2:
        report["warnings"].append("GHR-08: handoff_steps has fewer than 2 steps")

    order = evaluate_specialist_order(packet, execution_mode=mode)
    merge_readiness(report, order)

    plate = evaluate_plate_lock_readiness(packet, execution_mode=mode)
    merge_readiness(report, plate)

    recompute_pass(report)
    report["specialist_order"] = order
    report["plate_lock"] = plate
    report["motion_brief"] = motion
    return report
