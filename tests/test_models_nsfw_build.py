"""Tests for Grok Build NSFW custom-model registry (opt-in ErosForge aliases)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from models import (  # noqa: E402
    GROK_BUILD_CLI_MODELS,
    GROK_BUILD_NSFW_MODELS,
    XAI_CHAT_MODELS,
    known_nsfw_build_model,
    list_all_models,
    list_nsfw_build_models,
    nsfw_build_base_model,
    resolve_nsfw_build_model,
    verify_model_compatibility,
)


def test_nsfw_registry_has_eight_roles() -> None:
    expected = {
        "erosforge-director",
        "nsfw-prompt-master",
        "nsfw-quota-planner",
        "nsfw-sequence-extend",
        "nsfw-chain-qa",
        "nsfw-identity-lock",
        "nsfw-long-context",
        "nsfw-creative-fast",
    }
    assert set(GROK_BUILD_NSFW_MODELS) == expected


def test_nsfw_aliases_resolve() -> None:
    assert resolve_nsfw_build_model("erosforge") == "erosforge-director"
    assert resolve_nsfw_build_model("NSFW-QA") == "nsfw-chain-qa"
    assert resolve_nsfw_build_model("nsfw-1m") == "nsfw-long-context"
    assert known_nsfw_build_model("erosforge-director")
    assert not known_nsfw_build_model(None)
    assert not known_nsfw_build_model("totally-fake")
    assert resolve_nsfw_build_model(None) is None
    assert resolve_nsfw_build_model("") is None


def test_nsfw_base_models_are_known() -> None:
    for slug, info in GROK_BUILD_NSFW_MODELS.items():
        base = info["base_model"]
        assert base in GROK_BUILD_CLI_MODELS or base in XAI_CHAT_MODELS, slug
        assert nsfw_build_base_model(slug) == base
        assert "temperature" in info
        assert "label" in info
        assert "role" in info


def test_list_all_models_includes_nsfw_block() -> None:
    catalog = list_all_models()
    assert "grok_build_nsfw" in catalog
    block = catalog["grok_build_nsfw"]
    assert block["opt_in"] is True
    assert set(block["models"]) == set(GROK_BUILD_NSFW_MODELS)
    assert list_nsfw_build_models() == GROK_BUILD_NSFW_MODELS


def test_verify_accepts_nsfw_registry() -> None:
    result = verify_model_compatibility()
    assert result["compatible"], result["issues"]


def test_example_toml_lists_all_slugs() -> None:
    text = (ROOT / "config" / "grok-build-nsfw-models.example.toml").read_text(
        encoding="utf-8"
    )
    for slug in GROK_BUILD_NSFW_MODELS:
        assert f"[model.{slug}]" in text or f'[model."{slug}"]' in text, slug
    assert "cli-chat-proxy.grok.com" in text
    assert "api.x.ai" not in text or "Avoids paid api.x.ai" in text


if __name__ == "__main__":
    test_nsfw_registry_has_eight_roles()
    test_nsfw_aliases_resolve()
    test_nsfw_base_models_are_known()
    test_list_all_models_includes_nsfw_block()
    test_verify_accepts_nsfw_registry()
    test_example_toml_lists_all_slugs()
    print("All NSFW Build model tests passed")
