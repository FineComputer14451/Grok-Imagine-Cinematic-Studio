#!/usr/bin/env python3
"""Specialist-order checklist for generation handoffs (DNA→Lock→Curator→Prompt→I2V)."""

from __future__ import annotations

from typing import Any

from handoff_schema import is_video_execution_mode

# Canonical keys (packet specialist_checklist)
SPECIALIST_KEYS: tuple[str, ...] = (
    "dna",
    "identity_lock",
    "reference_curator",
    "prompt_master",
    "i2v",
)

# CLI / human aliases → canonical
SPECIALIST_ALIASES: dict[str, str] = {
    "dna": "dna",
    "character_dna": "dna",
    "extractor": "dna",
    "lock": "identity_lock",
    "identity_lock": "identity_lock",
    "identity": "identity_lock",
    "curator": "reference_curator",
    "reference_curator": "reference_curator",
    "reference": "reference_curator",
    "asset": "reference_curator",
    "prompt": "prompt_master",
    "prompt_master": "prompt_master",
    "i2v": "i2v",
    "image_to_video": "i2v",
    "video": "i2v",
}

LABELS: dict[str, str] = {
    "dna": "Character DNA Extractor",
    "identity_lock": "Identity Lock Specialist",
    "reference_curator": "Reference Asset Curator",
    "prompt_master": "Imagine Prompt Master",
    "i2v": "Image-to-Video Specialist",
}


def required_specialists(execution_mode: str | None) -> list[str]:
    """Steps required before spend for this execution mode."""
    required = [
        "dna",
        "identity_lock",
        "reference_curator",
        "prompt_master",
    ]
    if is_video_execution_mode(execution_mode):
        required.append("i2v")
    return required


def normalize_specialist_checklist(raw: Any) -> dict[str, bool]:
    """Normalize checklist dict or list of step names to canonical bool map."""
    out: dict[str, bool] = {k: False for k in SPECIALIST_KEYS}
    if raw is None:
        return out
    if isinstance(raw, dict):
        for key, val in raw.items():
            canon = SPECIALIST_ALIASES.get(str(key).strip().lower())
            if not canon:
                continue
            if isinstance(val, bool):
                out[canon] = val
            elif isinstance(val, (int, float)):
                out[canon] = bool(val)
            elif isinstance(val, str):
                out[canon] = val.strip().lower() in {
                    "1",
                    "true",
                    "yes",
                    "done",
                    "ok",
                    "y",
                }
            else:
                out[canon] = bool(val)
        return out
    if isinstance(raw, (list, tuple, set)):
        for item in raw:
            canon = SPECIALIST_ALIASES.get(str(item).strip().lower())
            if canon:
                out[canon] = True
        return out
    return out


def parse_checklist_csv(text: str | None) -> dict[str, bool]:
    """
    Parse CLI --checklist string.

    Forms:
      dna,lock,curator,prompt,i2v
      dna=1,lock=true,i2v=0
    """
    out: dict[str, bool] = {k: False for k in SPECIALIST_KEYS}
    if not text or not str(text).strip():
        return out
    for part in str(text).split(","):
        part = part.strip()
        if not part:
            continue
        if "=" in part:
            key, _, val = part.partition("=")
            canon = SPECIALIST_ALIASES.get(key.strip().lower())
            if canon:
                out[canon] = val.strip().lower() in {
                    "1",
                    "true",
                    "yes",
                    "done",
                    "ok",
                    "y",
                }
        else:
            canon = SPECIALIST_ALIASES.get(part.lower())
            if canon:
                out[canon] = True
    return out


def evaluate_specialist_order(
    packet: dict[str, Any],
    *,
    execution_mode: str | None = None,
) -> dict[str, Any]:
    """
    Evaluate specialist checklist on a packet.

    - No checklist: warning only (soft); not a blocker.
    - Checklist present: any required step False → blocker.
    """
    mode = execution_mode or str(packet.get("execution_mode") or "")
    required = required_specialists(mode)
    raw = packet.get("specialist_checklist")
    warnings: list[str] = []
    blockers: list[str] = []
    fixes: list[str] = []
    checks: list[dict[str, Any]] = []

    if raw is None:
        warnings.append(
            "GHR-09: specialist_checklist missing — "
            "set via --checklist dna,lock,curator,prompt[,i2v] or state.specialist_checklist"
        )
        fixes.append(
            "Activate DNA → Identity Lock → Reference Curator → Prompt Master"
            + (" → I2V" if "i2v" in required else "")
            + " then re-emit handoff with --checklist"
        )
        for key in required:
            checks.append(
                {
                    "specialist": key,
                    "label": LABELS[key],
                    "required": True,
                    "done": None,
                    "status": "unknown",
                }
            )
        return {
            "pass": True,  # missing checklist is soft
            "required": required,
            "checklist": None,
            "warnings": warnings,
            "blockers": blockers,
            "fixes": fixes,
            "checks": checks,
        }

    checklist = normalize_specialist_checklist(raw)
    for key in required:
        done = bool(checklist.get(key))
        checks.append(
            {
                "specialist": key,
                "label": LABELS[key],
                "required": True,
                "done": done,
                "status": "done" if done else "missing",
            }
        )
        if not done:
            blockers.append(
                f"GHR-10: specialist step not confirmed: {key} ({LABELS[key]})"
            )
            fixes.append(f"Run {LABELS[key]} then mark {key}=true on checklist")

    # Non-required i2v on image modes: informational if present false
    if "i2v" not in required and not checklist.get("i2v"):
        checks.append(
            {
                "specialist": "i2v",
                "label": LABELS["i2v"],
                "required": False,
                "done": False,
                "status": "skipped",
            }
        )

    return {
        "pass": len(blockers) == 0,
        "required": required,
        "checklist": checklist,
        "warnings": warnings,
        "blockers": blockers,
        "fixes": fixes,
        "checks": checks,
    }
