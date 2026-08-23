"""PR2: studio_core action registry is UI-agnostic and shims cleanly."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))

from studio_core.services.actions import (  # noqa: E402
    ACTIONS,
    COCKPIT_ORDER,
    FORBIDDEN_ARGV_TOKENS,
    LAUNCHER_ORDER,
    answers_to_argv,
    validate_answers,
)
from cli.tui import actions as tui_actions  # noqa: E402


def test_core_and_tui_shim_share_actions_dict() -> None:
    assert tui_actions.ACTIONS is ACTIONS
    assert tui_actions.answers_to_argv is answers_to_argv
    assert tui_actions.validate_answers is validate_answers
    assert tui_actions.LAUNCHER_ORDER is LAUNCHER_ORDER
    assert tui_actions.COCKPIT_ORDER is COCKPIT_ORDER


def test_core_actions_cover_both_surfaces() -> None:
    assert "models_verify" in ACTIONS
    assert ACTIONS["models_verify"].surfaces == frozenset({"launcher", "cockpit"})
    assert set(LAUNCHER_ORDER) <= set(ACTIONS)
    assert set(COCKPIT_ORDER) <= set(ACTIONS)


def test_core_argv_roundtrip_safe() -> None:
    assert validate_answers("models_verify", {}) == []
    assert answers_to_argv("models_verify", {}) == ["models", "verify"]
    argv = answers_to_argv(
        "bible_create",
        {
            "title": "T",
            "genre": "Cinematic",
            "chat_model": "grok-4.6",
            "video_model": "grok-imagine-video",
            "output": "production_bible.json",
        },
    )
    for tok in FORBIDDEN_ARGV_TOKENS:
        assert tok not in argv


def test_core_module_has_no_ui_framework_imports() -> None:
    src = (ROOT / "studio_core" / "services" / "actions.py").read_text(encoding="utf-8")
    for ban in (
        "import rich",
        "from rich",
        "import streamlit",
        "from streamlit",
        "import textual",
        "from textual",
    ):
        assert ban not in src, f"forbidden: {ban}"


if __name__ == "__main__":
    test_core_and_tui_shim_share_actions_dict()
    test_core_actions_cover_both_surfaces()
    test_core_argv_roundtrip_safe()
    test_core_module_has_no_ui_framework_imports()
    print("studio_core actions tests passed")
