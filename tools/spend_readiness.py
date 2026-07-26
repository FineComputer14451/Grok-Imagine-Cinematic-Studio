#!/usr/bin/env python3
"""
Generation spend readiness facade — plate lock + motion brief in one place.

CLI soft path: always evaluate + print; exit only when the matching --strict-* flag is set.
Semantics: each child helper owns pass/blockers; hard-fail is flag × child.pass.

``evaluate_spend_gates`` is the single composition point for
``--strict-plate`` / ``--strict-motion`` / ``--strict-wave-a`` (used by batch
preflight and session runner).
"""

from __future__ import annotations

from typing import Any

from motion_readiness import evaluate_motion_brief_readiness
from plate_readiness import evaluate_plate_lock_readiness
from readiness_common import empty_readiness_report, merge_readiness, recompute_pass


def compose_strict_spend_flags(
    *,
    strict_plate: bool = False,
    strict_motion: bool = False,
    strict_wave_a: bool = False,
) -> tuple[bool, bool, bool]:
    """
    Normalize spend flags.

    ``strict_wave_a`` implies plate + motion strict. Returns
    ``(strict_plate, strict_motion, strict_wave_a)``.
    """
    if strict_wave_a:
        return True, True, True
    return bool(strict_plate), bool(strict_motion), False


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
    strict_wave_a: bool = False,
) -> list[str]:
    """Domains that should hard-stop spend under the given flags."""
    sp, sm, sw = compose_strict_spend_flags(
        strict_plate=strict_plate,
        strict_motion=strict_motion,
        strict_wave_a=strict_wave_a,
    )
    reasons: list[str] = []
    plate = report.get("plate") or {}
    motion = report.get("motion") or {}
    if sp and not plate.get("pass", True):
        reasons.append("plate")
    if sm and not motion.get("pass", True):
        reasons.append("motion")
    # Wave A shape issues only hard-fail under strict_wave_a
    if sw and report.get("wave_a_issues"):
        reasons.append("wave_a")
    return reasons


def evaluate_spend_gates(
    subject: dict[str, Any] | None,
    *,
    execution_mode: str | None = None,
    strict_plate: bool = False,
    strict_motion: bool = False,
    strict_wave_a: bool = False,
) -> dict[str, Any]:
    """
    Canonical spend gate: plate + motion readiness, then Wave A field shapes.

    Plate/motion ownership stays in plate_readiness / motion_readiness.
    Wave A only validates Wave A-owned optional shapes (hmu, dialogue, crops, …).

    ``strict_wave_a`` ⇒ plate + motion strict + hard-fail on Wave A shape issues.
    """
    from wave_a_packets import validate_optional_wave_a_fields

    sp, sm, sw = compose_strict_spend_flags(
        strict_plate=strict_plate,
        strict_motion=strict_motion,
        strict_wave_a=strict_wave_a,
    )
    subj = subject if isinstance(subject, dict) else {}
    report = evaluate_generation_spend_readiness(
        subj, execution_mode=execution_mode, strict_motion=sm
    )
    wa_issues, wa_warnings = validate_optional_wave_a_fields(subj)
    report["wave_a_issues"] = wa_issues
    report["wave_a_warnings"] = wa_warnings
    report["strict_plate"] = sp
    report["strict_motion"] = sm
    report["strict_wave_a"] = sw
    report["hard_fail"] = spend_hard_fail_reasons(
        report, strict_plate=sp, strict_motion=sm, strict_wave_a=sw
    )
    return report


def format_spend_gate_failure(report: dict[str, Any]) -> str:
    """Human-readable one-line error from a gates report hard_fail list."""
    hard = report.get("hard_fail") or []
    parts: list[str] = []
    plate = report.get("plate") or {}
    motion = report.get("motion") or {}
    if "plate" in hard:
        parts.append(
            "plate lock: " + "; ".join(plate.get("blockers") or ["not ready"])
        )
    if "motion" in hard:
        parts.append(
            "motion brief: " + "; ".join(motion.get("blockers") or ["not ready"])
        )
    if "wave_a" in hard:
        parts.append(
            "wave-a: " + "; ".join(report.get("wave_a_issues") or ["field issues"])
        )
    return "; ".join(parts) if parts else "spend gate failed"
