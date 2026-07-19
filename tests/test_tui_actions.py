# tests/test_tui_actions.py
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from cli.tui.actions import (  # noqa: E402
    ACTIONS,
    COCKPIT_ORDER,
    FORBIDDEN_ARGV_TOKENS,
    LAUNCHER_ORDER,
    actions_for,
    answers_to_argv,
    reject_forbidden_argv,
    static_allowed_argvs,
    validate_answers,
)


def test_single_registry_covers_both_surfaces() -> None:
    launcher = {s.id for s in actions_for("launcher")}
    cockpit = {s.id for s in actions_for("cockpit")}
    assert launcher == set(LAUNCHER_ORDER)
    assert cockpit == set(COCKPIT_ORDER)
    assert "models_verify" in launcher and "models_verify" in cockpit
    # one definition
    assert ACTIONS["models_verify"].surfaces == frozenset({"launcher", "cockpit"})


def test_static_allowlist_is_fieldless_only() -> None:
    allowed = static_allowed_argvs()
    assert ("status",) in allowed
    assert ("models", "verify") in allowed
    # form actions are not static allowlist entries by argv alone
    bible = answers_to_argv(
        "bible_create",
        {
            "title": "T",
            "genre": "Cinematic",
            "chat_model": "grok-4.5",
            "video_model": "grok-imagine-video",
            "output": "production_bible.json",
        },
    )
    assert tuple(bible) not in allowed


def test_reject_forbidden_tokens() -> None:
    try:
        reject_forbidden_argv(["create-bible", "X", "--wizard"])
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "wizard" in str(exc).lower() or "Forbidden" in str(exc)


def test_no_action_emits_forbidden_tokens() -> None:
    samples = {
        "status": {},
        "models_verify": {},
        "validate": {},
        "stack": {},
        "bible_create": {
            "title": "T",
            "genre": "Cinematic",
            "chat_model": "grok-4.5",
            "video_model": "grok-imagine-video",
            "output": "production_bible.json",
        },
        "dna_init": {"name": "N", "core": "c", "facial": "", "hair": "", "clothing": "", "emotion": ""},
        "dna_lock": {"name": "N"},
        "sequence_init": {"name": "S", "duration": "60", "genre": ""},
        "sequence_add_clip": {
            "name": "S",
            "prompt": "p",
            "duration": "10",
            "recap": "",
            "aspect": "9:16",
            "ref": "",
            "transition": "invisible_edit",
            "action": "",
            "emotion": "",
            "dialogue": "",
        },
        "quota_budget": {"tier": "custom", "remaining": "1"},
        "quota_sequence_estimate": {"name": "S"},
    }
    for aid, ans in samples.items():
        assert validate_answers(aid, ans) == []
        argv = answers_to_argv(aid, ans)
        for tok in FORBIDDEN_ARGV_TOKENS:
            assert tok not in argv


def test_v3_static_allowlist_includes_validate_stack() -> None:
    allowed = static_allowed_argvs()
    assert ("validate",) in allowed
    assert ("stack",) in allowed
    # form-based estimate is not field-less static
    assert ("quota", "sequence") not in allowed
