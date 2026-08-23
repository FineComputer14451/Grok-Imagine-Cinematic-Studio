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
        "quota_budget",
        "quota_sequence_estimate",
        "quota_sync",
        "dna_init",
        "dna_lock",
        "dna_handoff",
        "sequence_init",
        "sequence_add_clip",
        "sequence_handoff",
        "sequence_polish_dry",
        "sequence_deliver_dry",
        "wave_a_briefs",
        "imagine_bridge",
        "handoff_validate",
        "doctor_quick",
        "models_verify",
        "validate",
        "stack",
    )
    assert set(COCKPIT_WORKFLOWS) == set(COCKPIT_ORDER)
    assert COCKPIT_WORKFLOWS["models_verify"].fields == ()
    assert COCKPIT_WORKFLOWS["models_verify"].needs_confirm is False
    assert COCKPIT_WORKFLOWS["validate"].needs_confirm is False
    assert COCKPIT_WORKFLOWS["doctor_quick"].needs_confirm is False
    assert COCKPIT_WORKFLOWS["doctor_quick"].fields == ()
    assert COCKPIT_WORKFLOWS["stack"].needs_confirm is False
    assert COCKPIT_WORKFLOWS["quota_sequence_estimate"].needs_confirm is False
    assert COCKPIT_WORKFLOWS["quota_sync"].fields == ()
    assert COCKPIT_WORKFLOWS["quota_sync"].needs_confirm is False
    for wid in (
        "bible_create",
        "dna_init",
        "dna_lock",
        "dna_handoff",
        "sequence_init",
        "sequence_add_clip",
        "sequence_handoff",
        "quota_budget",
    ):
        assert COCKPIT_WORKFLOWS[wid].needs_confirm is True
        assert COCKPIT_WORKFLOWS[wid].fields


def test_bible_happy_argv() -> None:
    answers = {
        "title": "Neon Echo",
        "genre": "Sci-Fi",
        "chat_model": "grok-4.6",
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
        "grok-4.6",
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


def test_v3_dna_lock_and_handoff_argv() -> None:
    assert answers_to_argv("dna_lock", {"name": "Liora"}) == ["dna", "lock", "Liora"]
    assert answers_to_argv("dna_handoff", {"name": "Liora", "output": ""}) == [
        "dna",
        "handoff",
        "Liora",
    ]
    assert answers_to_argv(
        "dna_handoff", {"name": "Liora", "output": "artifacts/h.json"}
    ) == ["dna", "handoff", "Liora", "-o", "artifacts/h.json"]
    assert validate_answers("dna_lock", {"name": ""})


def test_v3_sequence_add_clip_argv() -> None:
    answers = {
        "name": "Act 1",
        "prompt": "hero walks in",
        "duration": "10",
        "recap": "",
        "aspect": "16:9",
        "ref": "LIORA_CU_001",
        "transition": "invisible_edit",
        "action": "walk",
        "emotion": "calm",
        "dialogue": "",
    }
    assert validate_answers("sequence_add_clip", answers) == []
    argv = answers_to_argv("sequence_add_clip", answers)
    assert argv[:3] == ["sequence", "add-clip", "Act 1"]
    assert "-p" in argv and "hero walks in" in argv
    assert "-d" in argv and "10" in argv
    assert "--ref" in argv and "LIORA_CU_001" in argv
    assert "--action" in argv and "walk" in argv
    assert "--dialogue" not in argv
    assert "run" not in argv
    bad = {**answers, "aspect": "21:9"}
    assert validate_answers("sequence_add_clip", bad)


def test_v3_sequence_handoff_and_quota_estimate() -> None:
    assert answers_to_argv(
        "sequence_handoff", {"name": "Act 1", "clip": "clip_001", "output": ""}
    ) == ["sequence", "handoff", "Act 1", "-c", "clip_001"]
    assert answers_to_argv("quota_sequence_estimate", {"name": "Act 1"}) == [
        "quota",
        "sequence",
        "Act 1",
    ]
    assert "record" not in answers_to_argv(
        "quota_sequence_estimate", {"name": "Act 1"}
    )


def test_v3_validate_stack_show() -> None:
    assert answers_to_argv("validate", {}) == ["validate"]
    assert answers_to_argv("stack", {}) == ["stack"]
    assert answers_to_argv("dna_show", {"name": "Liora", "mode": ""}) == [
        "dna",
        "show",
        "Liora",
    ]
    assert answers_to_argv("sequence_show", {"name": "Act 1"}) == [
        "sequence",
        "show",
        "Act 1",
    ]


def test_no_forbidden_tokens_in_any_happy_path() -> None:
    samples = {
        "bible_create": {
            "title": "T",
            "genre": "Cinematic",
            "chat_model": "grok-4.6",
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
        "dna_lock": {"name": "N"},
        "dna_handoff": {"name": "N", "output": ""},
        "sequence_init": {"name": "S", "duration": "60", "genre": ""},
        "sequence_add_clip": {
            "name": "S",
            "prompt": "p",
            "duration": "10",
            "recap": "",
            "aspect": "16:9",
            "ref": "",
            "transition": "invisible_edit",
            "action": "",
            "emotion": "",
            "dialogue": "",
        },
        "sequence_handoff": {"name": "S", "clip": "c1", "output": ""},
        "quota_budget": {"tier": "custom", "remaining": "1"},
        "quota_sequence_estimate": {"name": "S"},
        "models_verify": {},
        "validate": {},
        "stack": {},
        "dna_show": {"name": "N", "mode": ""},
        "sequence_show": {"name": "S"},
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
            "chat_model": "grok-4.6",
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
