"""Tests for Imagine image model registry and alias resolution."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from models import (  # noqa: E402
    DEFAULT_IMAGINE_IMAGE_MODEL,
    HERO_IMAGINE_IMAGE_MODEL,
    IMAGINE_IMAGE_MODELS,
    LEGACY_QUALITY_IMAGE_MODEL,
    image_usd_per_image,
    imagine_image_pricing_table,
    imagine_surface_catalog,
    ordered_image_model_slugs,
    resolve_image_model,
    serve_image_model,
    verify_model_compatibility,
)


def test_default_image_model() -> None:
    assert DEFAULT_IMAGINE_IMAGE_MODEL == "grok-imagine-image"


def test_xai_api_aliases_resolve() -> None:
    assert resolve_image_model("grok-imagine-image-2026-03-02") == "grok-imagine-image"
    assert resolve_image_model("image") == "grok-imagine-image"
    assert resolve_image_model("grok-imagine-image-pro") == "grok-imagine-image-quality"
    assert resolve_image_model("grok-imagine-image-quality-latest") == "grok-imagine-image-quality"
    assert resolve_image_model("grok-imagine-image-quality-20260403") == "grok-imagine-image-quality"
    assert resolve_image_model("pro") == "grok-imagine-image-quality"
    assert resolve_image_model("quality") == "grok-imagine-image-quality"
    assert resolve_image_model("2.0") == "grok-imagine-image-2.0"
    assert resolve_image_model("image-2.0") == HERO_IMAGINE_IMAGE_MODEL
    assert resolve_image_model("imagine-image-2.0") == HERO_IMAGINE_IMAGE_MODEL


def test_hero_image_is_2_0() -> None:
    assert HERO_IMAGINE_IMAGE_MODEL == "grok-imagine-image-2.0"
    assert HERO_IMAGINE_IMAGE_MODEL in IMAGINE_IMAGE_MODELS
    assert LEGACY_QUALITY_IMAGE_MODEL in IMAGINE_IMAGE_MODELS
    assert IMAGINE_IMAGE_MODELS[HERO_IMAGINE_IMAGE_MODEL].get("quality_param") is True
    slugs = ordered_image_model_slugs()
    assert slugs[0] == DEFAULT_IMAGINE_IMAGE_MODEL
    assert HERO_IMAGINE_IMAGE_MODEL in slugs


def test_image_2_0_pricing_tiers() -> None:
    assert image_usd_per_image("grok-imagine-image-2.0") == 0.04
    assert image_usd_per_image("2.0", resolution="1k", quality="low") == 0.04
    assert image_usd_per_image("2.0", resolution="2k", quality="low") == 0.06
    assert image_usd_per_image("2.0", resolution="1k", quality="medium") == 0.06
    assert image_usd_per_image("2.0", resolution="2k", quality="medium") == 0.08
    catalog = imagine_surface_catalog()
    assert catalog["routing"]["image_hero"] == HERO_IMAGINE_IMAGE_MODEL
    assert any(s["id"] == "xai_responses_tool" for s in catalog["agent_mode_surfaces"])
    assert "no grok-imagine-video-2.0" in catalog["note"]


def test_pricing_table_matches_registry() -> None:
    table = imagine_image_pricing_table()
    assert set(table) == set(IMAGINE_IMAGE_MODELS)
    for slug, rates in table.items():
        assert rates["usd_per_image"] == IMAGINE_IMAGE_MODELS[slug]["usd_per_image"]


def test_serve_image_model_remaps_legacy() -> None:
    assert serve_image_model("grok-imagine-image-quality") == (
        "grok-imagine-image-2.0",
        "low",
    )
    assert serve_image_model("quality", role="hero") == (
        "grok-imagine-image-2.0",
        "medium",
    )
    assert serve_image_model("grok-imagine-image") == ("grok-imagine-image", None)
    assert serve_image_model("2.0", quality="high") == (
        "grok-imagine-image-2.0",
        "low",
    )
    assert serve_image_model("2.0", quality="medium") == (
        "grok-imagine-image-2.0",
        "medium",
    )
    assert serve_image_model("2.0", quality="") == (
        "grok-imagine-image-2.0",
        "low",
    )
    assert resolve_image_model("pro") == LEGACY_QUALITY_IMAGE_MODEL
    info = IMAGINE_IMAGE_MODELS[LEGACY_QUALITY_IMAGE_MODEL]
    assert info.get("retired") is True
    assert info.get("retire_date") == "2026-11-02"


def test_model_compatibility() -> None:
    result = verify_model_compatibility()
    assert result["compatible"], result["issues"]


if __name__ == "__main__":
    test_default_image_model()
    test_xai_api_aliases_resolve()
    test_hero_image_is_2_0()
    test_image_2_0_pricing_tiers()
    test_serve_image_model_remaps_legacy()
    test_pricing_table_matches_registry()
    test_model_compatibility()
    print("All image model tests passed")
