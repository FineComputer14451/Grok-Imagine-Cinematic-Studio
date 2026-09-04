"""Tests for Imagine image model registry and alias resolution."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from models import (  # noqa: E402
    DEFAULT_IMAGINE_IMAGE_MODEL,
    HERO_IMAGINE_IMAGE_MODEL,
    IMAGE_QUALITY_VALUES,
    IMAGINE_IMAGE_MODELS,
    LEGACY_QUALITY_IMAGE_MODEL,
    LEGACY_QUALITY_RETIRED_ON,
    image_max_edit_refs,
    image_usd_per_image,
    image_usd_per_input_image,
    live_image_model,
    imagine_image_pricing_table,
    imagine_surface_catalog,
    ordered_image_model_slugs,
    resolve_image_model,
    resolve_image_request,
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
    assert set(IMAGINE_IMAGE_MODELS[HERO_IMAGINE_IMAGE_MODEL]["quality_values"]) == set(
        IMAGE_QUALITY_VALUES
    )
    assert IMAGINE_IMAGE_MODELS[HERO_IMAGINE_IMAGE_MODEL]["max_edit_refs"] == 5
    assert IMAGINE_IMAGE_MODELS[LEGACY_QUALITY_IMAGE_MODEL].get("deprecated") is True
    assert IMAGINE_IMAGE_MODELS[LEGACY_QUALITY_IMAGE_MODEL]["retired_on"] == LEGACY_QUALITY_RETIRED_ON
    slugs = ordered_image_model_slugs()
    assert slugs[0] == DEFAULT_IMAGINE_IMAGE_MODEL
    assert HERO_IMAGINE_IMAGE_MODEL in slugs
    assert LEGACY_QUALITY_IMAGE_MODEL not in slugs
    assert LEGACY_QUALITY_IMAGE_MODEL in ordered_image_model_slugs(include_deprecated=True)
    assert live_image_model("quality") == HERO_IMAGINE_IMAGE_MODEL
    assert live_image_model("grok-imagine-image-pro") == HERO_IMAGINE_IMAGE_MODEL
    assert live_image_model("grok-imagine-image") == DEFAULT_IMAGINE_IMAGE_MODEL
    assert live_image_model(None) == DEFAULT_IMAGINE_IMAGE_MODEL


def test_quality_slug_rewrites_to_2_0_low() -> None:
    assert resolve_image_model("quality") == LEGACY_QUALITY_IMAGE_MODEL
    assert resolve_image_model("pro") == LEGACY_QUALITY_IMAGE_MODEL
    wire, sent, warnings = resolve_image_request("quality")
    assert wire == HERO_IMAGINE_IMAGE_MODEL
    assert sent == "low"
    assert any("retires" in w for w in warnings)
    wire_m, sent_m, _ = resolve_image_request("quality", quality="medium")
    assert wire_m == HERO_IMAGINE_IMAGE_MODEL
    assert sent_m == "medium"
    wire_1, sent_1, _ = resolve_image_request("grok-imagine-image", quality="low")
    assert wire_1 == DEFAULT_IMAGINE_IMAGE_MODEL
    assert sent_1 is None
    wire_2, sent_2, _ = resolve_image_request("2.0")
    assert wire_2 == HERO_IMAGINE_IMAGE_MODEL
    assert sent_2 is None


def test_image_2_0_pricing_tiers() -> None:
    assert image_usd_per_image("grok-imagine-image-2.0") == 0.04
    assert image_usd_per_image("2.0", resolution="1k", quality="low") == 0.04
    assert image_usd_per_image("2.0", resolution="2k", quality="low") == 0.06
    assert image_usd_per_image("2.0", quality="auto") == 0.04
    assert image_usd_per_image("2.0", resolution="1k") == 0.04
    assert image_usd_per_image("quality") == 0.04
    assert image_usd_per_image("pro") == image_usd_per_image("2.0", quality="low")
    assert image_usd_per_image("2.0", quality="medium") == 0.06
    assert image_usd_per_image("2.0", resolution="2k", quality="medium") == 0.08
    assert image_usd_per_image("2.0", quality="auto", mode="edit") == 0.06
    assert image_usd_per_input_image("grok-imagine-image") == 0.002
    assert image_usd_per_input_image("2.0") == 0.01
    assert image_usd_per_input_image("quality") == 0.01
    assert image_usd_per_image("2.0", quality="medium", mode="edit", n_input_images=2) == 0.08
    assert image_max_edit_refs("2.0") == 5
    assert image_max_edit_refs("grok-imagine-image") == 3
    assert image_max_edit_refs("quality") == 5
    catalog = imagine_surface_catalog()
    assert catalog["routing"]["image_hero"] == HERO_IMAGINE_IMAGE_MODEL
    assert catalog["routing"]["image_legacy_quality_retired_on"] == LEGACY_QUALITY_RETIRED_ON
    assert any(s["id"] == "xai_responses_tool" for s in catalog["agent_mode_surfaces"])
    assert "no grok-imagine-video-2.0" in catalog["note"]
    assert "retires" in catalog["note"]
    rest_paths = {(row["method"], row["path"]) for row in catalog["rest_endpoints"]}
    assert ("GET", "/v1/files") in rest_paths
    assert ("GET", "/v1/files/{id}") in rest_paths
    assert ("POST", "/v1/files") in rest_paths
    assert ("DELETE", "/v1/files/{id}") in rest_paths
    assert ("POST", "/v1/images/generations") in rest_paths
    assert ("POST", "/v1/images/edits") in rest_paths
    assert ("POST", "/v1/videos/generations") in rest_paths
    assert ("GET", "/v1/videos/{request_id}") in rest_paths


def test_pricing_table_matches_registry() -> None:
    table = imagine_image_pricing_table()
    assert set(table) == set(IMAGINE_IMAGE_MODELS)
    for slug, rates in table.items():
        assert rates["usd_per_image"] == IMAGINE_IMAGE_MODELS[slug]["usd_per_image"]


def test_model_compatibility() -> None:
    result = verify_model_compatibility()
    assert result["compatible"], result["issues"]


if __name__ == "__main__":
    test_default_image_model()
    test_xai_api_aliases_resolve()
    test_pricing_table_matches_registry()
    test_model_compatibility()
    print("All image model tests passed")