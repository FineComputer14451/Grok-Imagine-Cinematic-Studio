#!/usr/bin/env python3
"""Plate lock readiness — video still→video modes need approved/locked plate."""

from __future__ import annotations

from typing import Any

from handoff_schema import is_video_execution_mode

PLATE_STATUSES = frozenset({"draft", "approved", "locked"})
PLATE_OK = frozenset({"approved", "locked"})

# Modes that require curator plate freeze before spend
PLATE_REQUIRED_MODES = frozenset({"image_to_video", "reference_to_video"})


def normalize_plate_status(raw: Any) -> str | None:
    if raw is None:
        return None
    s = str(raw).strip().lower()
    if not s:
        return None
    if s in PLATE_STATUSES:
        return s
    # common aliases
    aliases = {
        "ok": "approved",
        "pass": "approved",
        "ready": "approved",
        "freeze": "locked",
        "frozen": "locked",
    }
    return aliases.get(s)


def resolve_execution_mode(
    subject: dict[str, Any],
    *,
    execution_mode: str | None = None,
) -> str:
    mode = (
        execution_mode
        or subject.get("execution_mode")
        or subject.get("recommended_mode")
        or (subject.get("decision") or {}).get("mode")
        or ""
    )
    return str(mode).strip()


def _has_plate_identity(subject: dict[str, Any]) -> bool:
    for key in (
        "plate_path",
        "plate_asset_id",
        "reference_image_id",
        "reference_image_url",
        "source_asset_id",
    ):
        val = subject.get(key)
        if isinstance(val, str) and val.strip():
            return True
        if val and not isinstance(val, str):
            return True
    return False


def evaluate_plate_lock_readiness(
    subject: dict[str, Any] | None,
    *,
    execution_mode: str | None = None,
) -> dict[str, Any]:
    """
    Semantic readiness for plate lock before video spend.

    pass=False only when blockers present.
    Soft by default at CLI; --strict-plate / --strict-handoff hard-fail.
    """
    subj = subject if isinstance(subject, dict) else {}
    mode = resolve_execution_mode(subj, execution_mode=execution_mode)
    warnings: list[str] = []
    blockers: list[str] = []
    fixes: list[str] = []
    checks: list[dict[str, Any]] = []

    status = normalize_plate_status(subj.get("plate_status"))
    checks.append({"id": "plate_status", "value": status, "mode": mode})

    if mode not in PLATE_REQUIRED_MODES:
        if mode == "video_prompt" and status and status not in PLATE_OK:
            warnings.append(
                f"PL-04: video_prompt has plate_status={status!r} "
                f"(not approved/locked) — ignored for pure video_prompt"
            )
            fixes.append(
                "Clear plate_status or set approved/locked if this shot should be still→video"
            )
        return {
            "pass": True,
            "strict": True,
            "skipped": mode not in PLATE_REQUIRED_MODES and not is_video_execution_mode(mode),
            "warnings": warnings,
            "blockers": blockers,
            "fixes": fixes,
            "checks": checks,
            "plate_status": status,
            "execution_mode": mode,
        }

    # Plate-required modes
    if status is None:
        blockers.append(
            "PL-01: plate_status missing — set approved or locked before still→video spend"
        )
        fixes.append(
            'Run: sfw plate set <batch> <shot> --status approved   '
            "# or locked after Identity Lock / Curator freeze"
        )
    elif status not in PLATE_OK:
        blockers.append(
            f"PL-02: plate_status={status!r} not in {{approved, locked}} — "
            "do not spend video on draft plates"
        )
        fixes.append(
            "Approve/lock plate after QA ≥7 (hero ≥8): "
            "sfw plate set <batch> <shot> --status approved|locked"
        )
    else:
        if not _has_plate_identity(subj):
            warnings.append(
                "PL-03: plate status OK but no plate_path / reference_image_id / "
                "reference_image_url — weak plate identity"
            )
            fixes.append(
                "Attach plate_path or reference_image_id when locking "
                "(sfw plate set … --path … --asset-id …)"
            )

    return {
        "pass": len(blockers) == 0,
        "strict": True,
        "skipped": False,
        "warnings": warnings,
        "blockers": blockers,
        "fixes": fixes,
        "checks": checks,
        "plate_status": status,
        "execution_mode": mode,
    }
