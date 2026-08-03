"""Guided Production Bible API — same stages as create-bible wizard, no --wizard."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent.parent
_SAFE_REL = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,200}$")


def stages_payload() -> dict[str, Any]:
    from cli.bible_stages import STAGES

    return {
        "count": len(STAGES),
        "stages": [
            {
                "id": s["id"],
                "title": s["title"],
                "fields": [
                    {
                        "key": f["key"],
                        "prompt": f["prompt"],
                        "example": f["example"],
                        "required": f["required"],
                        "default": f["default"],
                    }
                    for f in s["fields"]
                ],
            }
            for s in STAGES
        ],
    }


def validate_stage(stage_id: str, answers: dict[str, Any]) -> dict[str, Any]:
    from cli.bible_stages import validate_answers

    errors = validate_answers(stage_id, answers or {})
    return {"ok": not errors, "stage_id": stage_id, "errors": errors}


def _safe_output_path(output: str) -> Path:
    """Resolve write path under repo root; reject traversal."""
    raw = (output or "production_bible.json").strip() or "production_bible.json"
    if raw.startswith("/") or ".." in raw.split("/"):
        raise ValueError("output path must be relative and cannot contain '..'")
    if not _SAFE_REL.match(raw.replace("\\", "/")):
        raise ValueError("output path has invalid characters")
    path = (_ROOT / raw).resolve()
    if not str(path).startswith(str(_ROOT.resolve())):
        raise ValueError("output path escapes repository root")
    return path


def generate_bible(
    answers: dict[str, Any],
    *,
    write: bool = False,
    output: str = "production_bible.json",
) -> dict[str, Any]:
    """Build bible from wizard answers; optionally write JSON under repo root."""
    from cli.bible_stages import (
        STAGES,
        answers_to_kwargs,
        summary_and_next_steps,
        validate_answers,
    )
    from cli.production import build_production_bible

    # Validate all field stages before review
    all_errors: list[str] = []
    for stage in STAGES:
        if stage["id"] == "review":
            continue
        all_errors.extend(validate_answers(stage["id"], answers or {}))
    if all_errors:
        return {
            "ok": False,
            "errors": all_errors,
            "bible": None,
            "summary": None,
            "written_path": None,
        }

    try:
        kwargs = answers_to_kwargs(answers or {})
    except (ValueError, TypeError) as exc:
        return {
            "ok": False,
            "errors": [str(exc)],
            "bible": None,
            "summary": None,
            "written_path": None,
        }

    bible = build_production_bible(**kwargs)
    summary = summary_and_next_steps(bible)
    written: str | None = None
    if write:
        path = _safe_output_path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(bible, indent=2) + "\n", encoding="utf-8")
        try:
            written = str(path.relative_to(_ROOT))
        except ValueError:
            written = str(path)

    return {
        "ok": True,
        "errors": [],
        "bible": bible,
        "summary": summary,
        "kwargs": kwargs,
        "written_path": written,
    }
