#!/usr/bin/env python3
"""Shared readiness report helpers (merge, empty shell, spend field lists)."""

from __future__ import annotations

from typing import Any

# Shot → agent-mode handoff fields (single contract for stamping)
SUBJECT_HANDOFF_FIELDS: tuple[str, ...] = (
    "plate_status",
    "plate_asset_id",
    "plate_path",
    "reference_image_id",
    "reference_image_url",
    "source_asset_id",
    "motion_vector",
    "motion_tier",
    "i2v_motion_block",
    "motion_block",
)


def empty_readiness_report(
    *,
    skipped: bool = False,
    strict: bool = False,
    **extra: Any,
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "pass": True,
        "strict": strict,
        "skipped": skipped,
        "warnings": [],
        "blockers": [],
        "fixes": [],
        "checks": [],
    }
    base.update(extra)
    return base


def merge_readiness(
    into: dict[str, Any],
    child: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Fold child readiness into parent (warnings/blockers/fixes/checks).
    Does not recompute pass — caller sets pass from len(blockers) or flags.
    """
    if not child:
        return into
    for w in child.get("warnings") or []:
        if w not in into["warnings"]:
            into["warnings"].append(w)
    for b in child.get("blockers") or []:
        if b not in into["blockers"]:
            into["blockers"].append(b)
    for f in child.get("fixes") or []:
        if f not in into["fixes"]:
            into["fixes"].append(f)
    checks = child.get("checks")
    if checks:
        into.setdefault("checks", []).extend(checks)
    return into


def recompute_pass(report: dict[str, Any]) -> dict[str, Any]:
    report["pass"] = len(report.get("blockers") or []) == 0
    return report
