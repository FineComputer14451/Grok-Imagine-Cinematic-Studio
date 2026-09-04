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


def test_files_action_argv() -> None:
    assert answers_to_argv("files_list", {}) == ["files", "list"]
    assert answers_to_argv("imagine_poll", {"request_id": "req-1"}) == [
        "imagine",
        "poll",
        "req-1",
    ]
    assert answers_to_argv("files_get", {"file_id": "file_abc"}) == [
        "files",
        "get",
        "file_abc",
    ]
    upload = answers_to_argv(
        "files_upload",
        {
            "path": "locked-plate.png",
            "expires_after": "86400",
            "purpose": "assistants",
            "dry_run": "--dry-run",
        },
    )
    assert upload[:3] == ["files", "upload", "locked-plate.png"]
    assert "--expires-after" in upload and "86400" in upload
    assert "--purpose" in upload and "assistants" in upload
    assert "--dry-run" in upload
    for tok in FORBIDDEN_ARGV_TOKENS:
        assert tok not in upload
    delete = answers_to_argv("files_delete", {"file_id": "file_abc"})
    assert delete == ["files", "delete", "file_abc", "--yes"]
    share = answers_to_argv(
        "files_share", {"file_id": "file_abc", "expires_after": "86400"}
    )
    assert share[:3] == ["files", "share", "file_abc"]
    assert "--expires-after" in share and "86400" in share
    assert answers_to_argv("files_unshare", {"file_id": "file_abc"}) == [
        "files",
        "unshare",
        "file_abc",
    ]
    assert ACTIONS["files_share"].needs_confirm is False
    assert ACTIONS["files_unshare"].needs_confirm is True
    assert validate_answers("files_upload", {"path": ""}) != []
    assert validate_answers("files_get", {}) != []


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
