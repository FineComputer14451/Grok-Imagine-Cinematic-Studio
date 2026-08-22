"""Tests for Imagine video model registry and alias resolution."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from models import (  # noqa: E402
    DEFAULT_IMAGINE_VIDEO_MODEL,
    IMAGINE_VIDEO_MODELS,
    NATIVE_AUDIO_VIDEO_MODEL,
    build_video_pipeline_spec,
    imagine_video_pricing_table,
    recommended_video_model_for_mode,
    resolve_video_model,
    verify_model_compatibility,
    video_supports_mode,
    video_usd_per_second,
)


def test_default_video_model() -> None:
    assert DEFAULT_IMAGINE_VIDEO_MODEL == "grok-imagine-video"


def test_studio_shorthand_aliases_resolve() -> None:
    for alias in ("1.0", "video-1.0", "imagine-video"):
        assert resolve_video_model(alias) == "grok-imagine-video"


def test_xai_api_aliases_resolve() -> None:
    for alias in (
        "grok-imagine-video-1.5-preview",
        "grok-imagine-video-1.5-2026-05-30",
        "1.5",
        "1.5-preview",
        "preview",
    ):
        assert resolve_video_model(alias) == "grok-imagine-video-1.5"


def test_pricing_table_matches_registry() -> None:
    table = imagine_video_pricing_table()
    assert set(table) == set(IMAGINE_VIDEO_MODELS)
    for slug, rates in table.items():
        assert rates["usd_per_second"] == IMAGINE_VIDEO_MODELS[slug]["usd_per_second"]
        assert "usd_per_second_by_resolution" in rates


def test_resolution_rates_and_no_video_2_0() -> None:
    assert video_usd_per_second("grok-imagine-video") == 0.05
    assert video_usd_per_second("grok-imagine-video", resolution="720p") == 0.07
    assert video_usd_per_second("grok-imagine-video-1.5") == 0.08
    assert video_usd_per_second("1.5", resolution="720p") == 0.14
    assert video_usd_per_second("1.5", resolution="1080p") == 0.25
    # 2.0 is Image only — unknown video slug falls back to cost default
    assert resolve_video_model("2.0") == DEFAULT_IMAGINE_VIDEO_MODEL
    assert "grok-imagine-video-2.0" not in IMAGINE_VIDEO_MODELS
    spec = build_video_pipeline_spec("grok-imagine-video-1.5", resolution="1080p")
    assert 'version="1.5"' in spec
    assert 'resolution="1080p"' in spec
    assert video_supports_mode("grok-imagine-video", "edit")
    assert not video_supports_mode("grok-imagine-video-1.5", "edit")
    assert recommended_video_model_for_mode("reference_to_video") == NATIVE_AUDIO_VIDEO_MODEL
    assert recommended_video_model_for_mode("video_extend") == DEFAULT_IMAGINE_VIDEO_MODEL


def test_model_compatibility() -> None:
    result = verify_model_compatibility()
    assert result["compatible"], result["issues"]


if __name__ == "__main__":
    test_default_video_model()
    test_studio_shorthand_aliases_resolve()
    test_xai_api_aliases_resolve()
    test_pricing_table_matches_registry()
    test_model_compatibility()
    print("All video model tests passed")