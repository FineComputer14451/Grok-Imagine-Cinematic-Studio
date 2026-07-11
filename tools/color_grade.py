#!/usr/bin/env python3
"""
Sequence color grade notes for Color Grading Supervisor → AI Polish handoff.

Additive `seq["color_grade"]` object (or legacy string fields grade_notes / lut).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

GRADE_STATUSES = frozenset({"pending", "draft", "approved", "waived"})


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_color_grade(raw: Any) -> dict[str, Any] | None:
    """Normalize color_grade from dict, string, or None."""
    if raw is None:
        return None
    if isinstance(raw, str):
        text = raw.strip()
        if not text:
            return None
        return {
            "status": "draft",
            "notes": text,
            "lut": "",
            "emotional_temperature": "",
            "skin_protection": "protect skin tones",
            "motif": "",
            "source": "legacy_string",
            "updated_at": _now_iso(),
        }
    if not isinstance(raw, dict):
        return None
    status = str(raw.get("status") or "draft").strip().lower()
    if status not in GRADE_STATUSES:
        status = "draft"
    return {
        "status": status,
        "notes": str(raw.get("notes") or raw.get("grade_notes") or "").strip(),
        "lut": str(raw.get("lut") or raw.get("lut_name") or "").strip(),
        "emotional_temperature": str(
            raw.get("emotional_temperature") or raw.get("emotion") or ""
        ).strip(),
        "skin_protection": str(
            raw.get("skin_protection") or "protect skin tones"
        ).strip(),
        "motif": str(raw.get("motif") or raw.get("visual_motif") or "").strip(),
        "source": str(raw.get("source") or "color_grading_supervisor").strip(),
        "updated_at": str(raw.get("updated_at") or _now_iso()),
    }


def extract_color_grade(seq: dict[str, Any]) -> dict[str, Any] | None:
    """
    Resolve grade from seq.color_grade or legacy grade_notes / lut top-level fields.
    """
    grade = normalize_color_grade(seq.get("color_grade"))
    if grade:
        # Merge legacy top-level if grade object empty in places
        if not grade.get("notes") and seq.get("grade_notes"):
            grade["notes"] = str(seq.get("grade_notes")).strip()
        if not grade.get("lut") and seq.get("lut"):
            grade["lut"] = str(seq.get("lut")).strip()
        return grade
    # Legacy only
    notes = str(seq.get("grade_notes") or "").strip()
    lut = str(seq.get("lut") or "").strip()
    if notes or lut:
        return {
            "status": "draft",
            "notes": notes,
            "lut": lut,
            "emotional_temperature": "",
            "skin_protection": "protect skin tones",
            "motif": "",
            "source": "legacy_fields",
            "updated_at": _now_iso(),
        }
    return None


def color_grade_is_usable(grade: dict[str, Any] | None) -> bool:
    """True when polish has meaningful grade direction (not bare pending empty)."""
    if not grade:
        return False
    status = str(grade.get("status") or "").lower()
    if status == "waived":
        return True
    if status == "pending":
        return False
    # draft or approved: need at least notes or lut or temperature/motif
    return bool(
        grade.get("notes")
        or grade.get("lut")
        or grade.get("emotional_temperature")
        or grade.get("motif")
    )


def color_grade_summary(grade: dict[str, Any] | None) -> str:
    """One-line summary for polish manifest / agent prompts."""
    if not grade:
        return ""
    parts: list[str] = []
    status = grade.get("status")
    if status:
        parts.append(f"status={status}")
    if grade.get("lut"):
        parts.append(f"LUT={grade['lut']}")
    if grade.get("emotional_temperature"):
        parts.append(f"temp={grade['emotional_temperature']}")
    if grade.get("motif"):
        parts.append(f"motif={grade['motif']}")
    if grade.get("notes"):
        notes = str(grade["notes"])
        parts.append(notes if len(notes) <= 120 else notes[:117] + "…")
    if grade.get("skin_protection"):
        parts.append(str(grade["skin_protection"]))
    return "; ".join(parts)


def apply_color_grade(
    seq: dict[str, Any],
    *,
    notes: str = "",
    lut: str = "",
    emotional_temperature: str = "",
    skin_protection: str = "protect skin tones",
    motif: str = "",
    status: str = "draft",
    source: str = "color_grading_supervisor",
    waive: bool = False,
) -> dict[str, Any]:
    """Write normalized color_grade onto sequence; return the grade object."""
    if waive:
        grade = {
            "status": "waived",
            "notes": notes or "Director waived formal color pass",
            "lut": lut,
            "emotional_temperature": emotional_temperature,
            "skin_protection": skin_protection,
            "motif": motif,
            "source": source or "director_waiver",
            "updated_at": _now_iso(),
        }
    else:
        existing = extract_color_grade(seq) or {}
        grade = {
            "status": status if status in GRADE_STATUSES else "draft",
            "notes": notes if notes else str(existing.get("notes") or ""),
            "lut": lut if lut else str(existing.get("lut") or ""),
            "emotional_temperature": (
                emotional_temperature
                if emotional_temperature
                else str(existing.get("emotional_temperature") or "")
            ),
            "skin_protection": skin_protection
            or str(existing.get("skin_protection") or "protect skin tones"),
            "motif": motif if motif else str(existing.get("motif") or ""),
            "source": source,
            "updated_at": _now_iso(),
        }
    seq["color_grade"] = grade
    # Keep legacy mirrors for older readers
    if grade.get("notes"):
        seq["grade_notes"] = grade["notes"]
    if grade.get("lut"):
        seq["lut"] = grade["lut"]
    return grade
