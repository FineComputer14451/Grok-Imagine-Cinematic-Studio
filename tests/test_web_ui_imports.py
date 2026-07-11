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
    assert rt.BIBLE_STAGES_AVAILABLE is True
    assert len(rt.STAGES) == 5
    assert callable(rt.answers_to_kwargs)
    assert callable(rt.validate_answers)
    assert callable(rt.summary_and_next_steps)
    assert callable(rt.build_notes)
    assert rt.DEFAULT_XAI_CHAT_MODEL == "grok-4.5"
    assert rt.DEFAULT_IMAGINE_VIDEO_MODEL == "grok-imagine-video"
    assert callable(rt.ordered_chat_model_slugs)
    assert callable(rt.ordered_video_model_slugs)
    assert callable(rt.stack_banner_markdown)
    assert callable(rt.session_model_stack)
    assert callable(rt.cached_models_verify)
    assert callable(rt.is_streamlit_cloud)
    assert callable(rt.resolve_xai_api_key)
    assert callable(rt.sync_xai_api_key_to_environ)
    assert rt.is_streamlit_cloud() is False  # local/dev path
    if rt.MODELS_AVAILABLE and rt.XAI_CHAT_MODELS:
        ordered = rt.ordered_chat_model_slugs()
        assert ordered[0] == "grok-4.5"
    if rt.MODELS_AVAILABLE and rt.IMAGINE_VIDEO_MODELS:
        v_ordered = rt.ordered_video_model_slugs()
        assert v_ordered[0] == "grok-imagine-video"


def test_session_helpers() -> None:
    from lib import session as sess

    assert sess.clip_story("short", 10) == "short"
    assert sess.clip_story("a" * 20, 10).endswith("…")
    assert "genres" in sess.PRODUCTION_OPTIONS
    assert sess.SESSION_DEFAULTS["genre"] in sess.PRODUCTION_OPTIONS["genres"]
    assert sess.SESSION_DEFAULTS["chat_model"] == "grok-4.5"
    assert sess.SESSION_DEFAULTS["reasoning_level"] == "high"
    assert "reasoning_levels" in sess.PRODUCTION_OPTIONS


def test_page_modules_import() -> None:
    from pages import dashboard, dna, imagine, nsfw, production, quota, sequences, settings, tools

    for mod in (dashboard, production, dna, sequences, imagine, quota, settings, tools, nsfw):
        assert callable(mod.render)


def test_bible_wizard_ui_import() -> None:
    from lib import bible_wizard_ui

    assert callable(bible_wizard_ui.render_bible_wizard)


def test_bootstrap_reexports() -> None:
    from lib import bootstrap as b

    assert b.STUDIO_VERSION
    assert b.clip_story("hello", 3) == "hel…"


def test_nsfw_runtime_imports() -> None:
    from lib import nsfw_runtime as nr

    assert nr.SHOT_TIER_OPTIONS[0] == "hero"
    assert callable(nr.parse_shot_lines)
    assert callable(nr.plan_and_save_batch)
    assert callable(nr.batch_to_markdown)
    assert callable(nr.list_batches)


def test_imagine_runtime_imports() -> None:
    from lib import imagine_runtime as ir

    assert callable(ir.plan_and_save_sfw_batch)
    assert callable(ir.add_reference_plate)
    assert callable(ir.dry_run_active)


def test_dashboard_uses_shared_builder() -> None:
    from lib import runtime as rt

    assert rt.DASHBOARD_AVAILABLE
    snap = rt.build_studio_dashboard()
    assert "studio" in snap
    assert "quota" in snap
    assert "production" in snap


if __name__ == "__main__":
    test_runtime_imports()
    test_session_helpers()
    test_page_modules_import()
    test_bootstrap_reexports()
    test_nsfw_runtime_imports()
    test_imagine_runtime_imports()
    test_dashboard_uses_shared_builder()
    print("All smoke tests passed")