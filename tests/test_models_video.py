"""Tests for Imagine video model registry and alias resolution."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from models import (  # noqa: E402
    DEFAULT_IMAGINE_VIDEO_MODEL,
    IMAGINE_VIDEO_MODELS,
    imagine_video_pricing_table,
    resolve_video_model,
    verify_model_compatibility,
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