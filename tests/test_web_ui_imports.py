"""Smoke tests for Web UI module imports and helpers."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB_UI = ROOT / "web_ui"
sys.path.insert(0, str(WEB_UI))


def test_runtime_imports() -> None:
    from lib import runtime as rt

    assert rt.ROOT == ROOT
    assert rt.STUDIO_VERSION
    assert rt.core_agent_count() >= 23


def test_session_helpers() -> None:
    from lib import session as sess

    assert sess.clip_story("short", 10) == "short"
    assert sess.clip_story("a" * 20, 10).endswith("…")
    assert "genres" in sess.PRODUCTION_OPTIONS
    assert sess.SESSION_DEFAULTS["genre"] in sess.PRODUCTION_OPTIONS["genres"]


def test_page_modules_import() -> None:
    from pages import dashboard, dna, nsfw, production, quota, sequences, settings, tools

    for mod in (dashboard, production, dna, sequences, quota, settings, tools, nsfw):
        assert callable(mod.render)


def test_bootstrap_reexports() -> None:
    from lib import bootstrap as b

    assert b.STUDIO_VERSION
    assert b.clip_story("hello", 3) == "hel…"


if __name__ == "__main__":
    test_runtime_imports()
    test_session_helpers()
    test_page_modules_import()
    test_bootstrap_reexports()
    print("All smoke tests passed")