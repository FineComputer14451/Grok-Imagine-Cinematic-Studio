#!/usr/bin/env python3
"""
Generation spend readiness facade — plate lock + motion brief in one place.

CLI soft path: always evaluate + print; exit only when the matching --strict-* flag is set.
Semantics: each child helper owns pass/blockers; hard-fail is flag × child.pass.
"""

from __future__ import annotations

from typing import Any

from motion_readiness import evaluate_motion_brief_readiness
from plate_readiness import evaluate_plate_lock_readiness
from readiness_common import empty_readiness_report, merge_readiness, recompute_pass


def evaluate_generation_spend_readiness(
    subject: dict[str, Any] | None,
    *,
    execution_mode: str | None = None,
    strict_motion: bool = False,
) -> dict[str, Any]:
    """
    Combined plate + motion readiness for a batch shot (or handoff-like subject).

    Returns:
      pass: True if both children pass (soft motion free-text can keep motion.pass True)
      plate / motion: child reports
      hard_fail_reasons(strict_plate, strict_motion): use spend_hard_fail_reasons()
    """
    subj = subject if isinstance(subject, dict) else {}
    plate = evaluate_plate_lock_readiness(subj, execution_mode=execution_mode)
    motion = evaluate_motion_brief_readiness(
        subj, execution_mode=execution_mode, strict=strict_motion
    )
    report = empty_readiness_report(strict=strict_motion)
    merge_readiness(report, plate)
    merge_readiness(report, motion)
    recompute_pass(report)
    report["plate"] = plate
    report["motion"] = motion
    report["execution_mode"] = (
        plate.get("execution_mode")
        or motion.get("execution_mode")
        or execution_mode
    )
    return report


def spend_hard_fail_reasons(
    report: dict[str, Any],
    *,
    strict_plate: bool = False,
    strict_motion: bool = False,
) -> list[str]:
    """Domains that should hard-stop spend under the given flags."""
    reasons: list[str] = []
    plate = report.get("plate") or {}
    motion = report.get("motion") or {}
    if strict_plate and not plate.get("pass", True):
        reasons.append("plate")
    if strict_motion and not motion.get("pass", True):
        reasons.append("motion")
    return reasons
