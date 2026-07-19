# tests/test_tui_forms.py
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from cli.tui.catalog import FORBIDDEN_ARGV_TOKENS  # noqa: E402
from cli.tui.forms import (  # noqa: E402
    COCKPIT_ORDER,
    COCKPIT_WORKFLOWS,
    answers_to_argv,
    default_answers,
    summarize_action,
    validate_answers,
)


def test_cockpit_order_and_ids() -> None:
    assert COCKPIT_ORDER == (
        "bible_create",
        "dna_init",
        "sequence_init",
        "quota_budget",
        "models_verify",
    )
    assert set(COCKPIT_WORKFLOWS) == set(COCKPIT_ORDER)
    assert COCKPIT_WORKFLOWS["models_verify"].fields == ()
    assert COCKPIT_WORKFLOWS["models_verify"].needs_confirm is False
    for wid in ("bible_create", "dna_init", "sequence_init", "quota_budget"):
        assert COCKPIT_WORKFLOWS[wid].needs_confirm is True
        assert COCKPIT_WORKFLOWS[wid].fields


def test_bible_happy_argv() -> None:
    answers = {
        "title": "Neon Echo",
        "genre": "Sci-Fi",
        "chat_model": "grok-4.5",
        "video_model": "grok-imagine-video",
        "output": "production_bible.json",
    }
    assert validate_answers("bible_create", answers) == []
    argv = answers_to_argv("bible_create", answers)
    assert argv == [
        "create-bible",
        "Neon Echo",
        "--genre",
        "Sci-Fi",
        "--chat-model",
        "grok-4.5",
        "--video-model",
        "grok-imagine-video",
        "-o",
        "production_bible.json",
    ]
    assert "--wizard" not in argv


def test_bible_missing_title() -> None:
    errs = validate_answers("bible_create", default_answers("bible_create"))
    assert any("title" in e.lower() for e in errs)


def test_dna_optional_flags_omitted_when_empty() -> None:
    answers = {"name": "Liora", "core": "", "facial": "soft", "hair": "", "clothing": "", "emotion": ""}
    assert validate_answers("dna_init", answers) == []
    argv = answers_to_argv("dna_init", answers)
    assert argv[:3] == ["dna", "init", "Liora"]
    assert "--facial" in argv and "soft" in argv
    assert "--core" not in argv
    assert "--hair" not in argv


def test_sequence_duration_and_genre() -> None:
    assert validate_answers("sequence_init", {"name": "Act 1", "duration": "90", "genre": "Drama"}) == []
    argv = answers_to_argv("sequence_init", {"name": "Act 1", "duration": "90", "genre": "Drama"})
    assert argv == ["sequence", "init", "Act 1", "-d", "90", "-g", "Drama"]
    assert validate_answers("sequence_init", {"name": "X", "duration": "0", "genre": ""})
    assert validate_answers("sequence_init", {"name": "X", "duration": "nope", "genre": ""})


def test_quota_budget_tier_and_remaining() -> None:
    assert validate_answers("quota_budget", {"tier": "supergrok_pro", "remaining": ""}) == []
    assert answers_to_argv("quota_budget", {"tier": "supergrok_pro", "remaining": ""}) == [
        "quota",
        "budget",
        "--tier",
        "supergrok_pro",
    ]
    argv = answers_to_argv("quota_budget", {"tier": "supergrok_heavy", "remaining": "500"})
    assert argv == ["quota", "budget", "--tier", "supergrok_heavy", "--remaining", "500"]
    assert validate_answers("quota_budget", {"tier": "free_tier", "remaining": ""})


def test_models_verify_argv() -> None:
    assert validate_answers("models_verify", {}) == []
    assert answers_to_argv("models_verify", {}) == ["models", "verify"]


def test_no_forbidden_tokens_in_any_happy_path() -> None:
    samples = {
        "bible_create": {
            "title": "T",
            "genre": "Cinematic",
            "chat_model": "grok-4.5",
            "video_model": "grok-imagine-video",
            "output": "production_bible.json",
        },
        "dna_init": {
            "name": "N",
            "core": "c",
            "facial": "",
            "hair": "",
            "clothing": "",
            "emotion": "",
        },
        "sequence_init": {"name": "S", "duration": "60", "genre": ""},
        "quota_budget": {"tier": "custom", "remaining": "1"},
        "models_verify": {},
    }
    for wid, ans in samples.items():
        assert validate_answers(wid, ans) == []
        argv = answers_to_argv(wid, ans)
        for tok in FORBIDDEN_ARGV_TOKENS:
            assert tok not in argv, f"{wid}: forbidden {tok}"
        assert "--wizard" not in argv


def test_summarize_includes_label_and_argv() -> None:
    text = summarize_action(
        "bible_create",
        {
            "title": "Neon",
            "genre": "Cinematic",
            "chat_model": "grok-4.5",
            "video_model": "grok-imagine-video",
            "output": "production_bible.json",
        },
    )
    assert "Bible" in text or "bible" in text.lower() or "Neon" in text
    assert "create-bible" in text


def test_unknown_workflow() -> None:
    errs = validate_answers("nope", {})
    assert errs
    try:
        answers_to_argv("nope", {})
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
