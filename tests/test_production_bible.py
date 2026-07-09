"""Baseline contract for build_production_bible JSON shape.

Locks top-level keys so guided-wizard work cannot invent a second schema.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from cli.production import build_production_bible  # noqa: E402

# Canonical top-level keys emitted by build_production_bible (v3.6.6).
# Wizard tests assert output keys are exactly this set (or a superset only if
# production.py is intentionally extended in the same change).
REQUIRED_BIBLE_KEYS = frozenset(
    {
        "project_title",
        "genre",
        "director_signature",
        "target_duration_seconds",
        "complexity",
        "total_agents",
        "version",
        "role_cards_source",
        "model_stack",
        "video_pipeline_spec",
        "locked_variables",
        "key_agents_involved",
        "recommended_phases",
        "created",
        "status",
        "notes",
    }
)

REQUIRED_LOCKED_VARIABLES = frozenset(
    {
        "PROJECT_TITLE",
        "GENRE",
        "DIRECTOR_SIGNATURE",
        "DURATION",
        "VIDEO_PIPELINE_SPEC",
    }
)


def test_build_production_bible_required_keys() -> None:
    bible = build_production_bible("Baseline Project", genre="Sci-Fi")
    assert REQUIRED_BIBLE_KEYS == frozenset(bible.keys())


def test_build_production_bible_locked_variables_and_stack() -> None:
    bible = build_production_bible(
        "Locked Vars",
        genre="Thriller",
        director_signature="Neo-noir grit",
        target_duration_seconds=90,
        notes="Custom notes",
    )
    assert bible["project_title"] == "Locked Vars"
    assert bible["genre"] == "Thriller"
    assert bible["director_signature"] == "Neo-noir grit"
    assert bible["target_duration_seconds"] == 90
    assert bible["notes"] == "Custom notes"
    assert isinstance(bible["model_stack"], dict)
    assert isinstance(bible["video_pipeline_spec"], str)
    assert bible["video_pipeline_spec"]
    assert REQUIRED_LOCKED_VARIABLES <= frozenset(bible["locked_variables"].keys())
    assert bible["locked_variables"]["PROJECT_TITLE"] == "Locked Vars"
    assert bible["locked_variables"]["GENRE"] == "Thriller"
    assert "90s" in bible["locked_variables"]["DURATION"]


def test_build_production_bible_default_notes() -> None:
    bible = build_production_bible("Defaults")
    assert bible["genre"] == "Cinematic"
    assert bible["target_duration_seconds"] == 60
    assert "Grok Imagine" in bible["notes"] or "CLI" in bible["notes"]
