"""Tests for guided Production Bible stage data and kwargs mapping."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from cli.bible_stages import (  # noqa: E402
    ALLOWED_BIBLE_KWARGS,
    STAGES,
    answers_to_kwargs,
    build_notes,
    should_run_wizard,
    stage_by_id,
    summary_and_next_steps,
    validate_answers,
)
from cli.production import build_production_bible  # noqa: E402
from test_production_bible import REQUIRED_BIBLE_KEYS  # noqa: E402


SAMPLE_ANSWERS = {
    "title": "Rain Code",
    "logline": "A detective hunts a rogue AI through neon rain.",
    "genre": "Neo-Noir",
    "director_signature": "Wet neon, handheld urgency",
    "complexity": "High",
    "characters_text": "Mara: exhausted detective. Kai: rogue AI.",
    "world_text": "Tokyo 2091; rain never stops.",
    "target_duration_seconds": 90,
    "video_model": "1.5",
    "chat_model": "grok-4.3",
    "tech_notes": "16:9; native rain SFX",
}


def test_stages_count_and_unique_ids() -> None:
    assert len(STAGES) == 5
    ids = [s["id"] for s in STAGES]
    assert ids == ["story", "genre", "characters", "technicals", "review"]
    assert len(set(ids)) == 5


def test_stage_by_id() -> None:
    assert stage_by_id("story")["title"].startswith("Story")
    assert stage_by_id("review")["fields"] == []
    with pytest.raises(KeyError):
        stage_by_id("nope")


def test_validate_title_required() -> None:
    errs = validate_answers("story", {})
    assert any("title" in e.lower() or "required" in e.lower() for e in errs)
    assert validate_answers("story", {"title": "Ok"}) == []


def test_validate_duration_invalid() -> None:
    errs = validate_answers(
        "technicals",
        {"target_duration_seconds": "nope"},
    )
    assert errs
    assert validate_answers("technicals", {"target_duration_seconds": 60}) == []
    # Default satisfies required when blank
    assert validate_answers("technicals", {}) == []


def test_build_notes_rollup() -> None:
    notes = build_notes(SAMPLE_ANSWERS)
    assert "Logline:" in notes
    assert "detective" in notes
    assert "Characters:" in notes
    assert "Mara" in notes
    assert "World:" in notes
    assert "Technical notes:" in notes
    assert build_notes({"title": "Only"}) == ""


def test_answers_to_kwargs_allowed_keys_only() -> None:
    kwargs = answers_to_kwargs(SAMPLE_ANSWERS)
    assert set(kwargs) <= ALLOWED_BIBLE_KWARGS
    assert kwargs["title"] == "Rain Code"
    assert kwargs["genre"] == "Neo-Noir"
    assert kwargs["target_duration_seconds"] == 90
    assert kwargs["complexity"] == "High"
    assert kwargs["director_signature"] == "Wet neon, handheld urgency"
    assert kwargs["video_model"] == "1.5"
    assert kwargs["chat_model"] == "grok-4.3"
    assert "Logline:" in kwargs["notes"]
    assert "Mara" in kwargs["notes"]


def test_answers_to_kwargs_requires_title() -> None:
    with pytest.raises(ValueError, match="title"):
        answers_to_kwargs({"genre": "Sci-Fi"})


def test_answers_to_kwargs_feeds_builder_compatible() -> None:
    kwargs = answers_to_kwargs(SAMPLE_ANSWERS)
    bible = build_production_bible(**kwargs)
    assert frozenset(bible.keys()) == REQUIRED_BIBLE_KEYS
    assert bible["project_title"] == "Rain Code"
    assert bible["genre"] == "Neo-Noir"
    assert bible["target_duration_seconds"] == 90
    assert "Mara" in bible["notes"]


def test_summary_and_next_steps() -> None:
    bible = build_production_bible(**answers_to_kwargs(SAMPLE_ANSWERS))
    text = summary_and_next_steps(bible)
    assert "Rain Code" in text
    assert "dna init" in text
    assert "quota" in text.lower()
    assert "sequence init" in text


def test_should_run_wizard_policy() -> None:
    assert should_run_wizard(wizard_flag=True, title="X", stdin_isatty=False) is True
    assert should_run_wizard(wizard_flag=False, title="X", stdin_isatty=True) is False
    assert should_run_wizard(wizard_flag=False, title=None, stdin_isatty=True) is True
    assert should_run_wizard(wizard_flag=False, title="", stdin_isatty=True) is True
    assert should_run_wizard(wizard_flag=False, title=None, stdin_isatty=False) is False
    assert should_run_wizard(wizard_flag=False, title="  ", stdin_isatty=False) is False
