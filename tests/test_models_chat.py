"""Tests for xAI chat model registry (Grok 4.5 cinematic+build default; 4.3 opt-in 1M)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from models import (  # noqa: E402
    DEFAULT_GROK_BUILD_MODEL,
    DEFAULT_XAI_BUILD_MODEL,
    DEFAULT_XAI_CHAT_MODEL,
    RECOMMENDED_GROK_BUILD_CLI_VERSION,
    REQUIRED_MODEL_ROLES,
    REQUIRED_MODEL_SLUGS,
    ROLE_DEFAULTS,
    STACK_CONTRACT,
    XAI_CHAT_MODELS,
    is_build_default,
    is_cinematic_default,
    known_chat_model,
    model_stack_summary,
    normalize_chat_model,
    resolve_chat_model,
    verify_model_compatibility,
)


def test_role_defaults_are_single_source() -> None:
    # Literals live only in STACK_CONTRACT; ROLE_DEFAULTS embeds them
    assert STACK_CONTRACT == {
        "cinematic": "grok-4.5",
        "build": "grok-4.5",
        "cli": "grok-4.5",
    }
    for role, slug in STACK_CONTRACT.items():
        assert ROLE_DEFAULTS[role] == slug
    assert ROLE_DEFAULTS["cinematic"] == DEFAULT_XAI_CHAT_MODEL == "grok-4.5"
    assert ROLE_DEFAULTS["build"] == DEFAULT_XAI_BUILD_MODEL == "grok-4.5"
    assert ROLE_DEFAULTS["cli"] == DEFAULT_GROK_BUILD_MODEL == "grok-4.5"
    assert RECOMMENDED_GROK_BUILD_CLI_VERSION == "0.2.93"


def test_no_per_model_default_flags() -> None:
    """Defaults live in ROLE_DEFAULTS only — not duplicated on each entry."""
    for slug, info in XAI_CHAT_MODELS.items():
        assert "default" not in info, slug
        assert "build_default" not in info, slug
    # Unified stack: cinematic and build both pin grok-4.5
    assert is_cinematic_default("grok-4.5")
    assert is_build_default("grok-4.5")
    assert not is_cinematic_default("grok-4.3")
    assert not is_build_default("grok-4.3")


def test_registry_contains_both_generations() -> None:
    assert "grok-4.3" in XAI_CHAT_MODELS
    assert "grok-4.5" in XAI_CHAT_MODELS
    assert XAI_CHAT_MODELS["grok-4.3"]["context_tokens"] == 1_000_000
    assert XAI_CHAT_MODELS["grok-4.5"]["context_tokens"] == 500_000
    assert XAI_CHAT_MODELS["grok-4.5"]["input_usd_per_1m"] == 2.00
    assert XAI_CHAT_MODELS["grok-4.5"]["output_usd_per_1m"] == 6.00


def test_long_context_aliases() -> None:
    for alias in ("grok-4.3", "4.3", "long-context", "grok-4"):
        assert resolve_chat_model(alias) == "grok-4.3"
        assert known_chat_model(alias)


def test_build_and_cinematic_aliases() -> None:
    for alias in (
        "grok-4.5",
        "4.5",
        "grok-4.5-latest",
        "grok-build-latest",
        "grok-build",
        "build",
        "coding",
        "cinematic",
    ):
        assert resolve_chat_model(alias) == "grok-4.5", alias
        assert known_chat_model(alias), alias


def test_default_resolve_is_cinematic() -> None:
    assert resolve_chat_model(None) == "grok-4.5"
    assert resolve_chat_model("") == "grok-4.5"
    assert resolve_chat_model() == "grok-4.5"
    assert not known_chat_model(None)
    assert not known_chat_model("")


def test_unknown_slug_falls_back_but_is_not_known() -> None:
    assert resolve_chat_model("totally-fake-model") == DEFAULT_XAI_CHAT_MODEL
    assert not known_chat_model("totally-fake-model")
    resolved, known = normalize_chat_model("totally-fake-model")
    assert resolved == DEFAULT_XAI_CHAT_MODEL
    assert known is False
    resolved, known = normalize_chat_model(None)
    assert resolved == DEFAULT_XAI_CHAT_MODEL
    assert known is True
    resolved, known = normalize_chat_model("4.5")
    assert resolved == "grok-4.5"
    assert known is True


def test_required_roles_have_unique_slugs() -> None:
    assert set(REQUIRED_MODEL_ROLES) == {
        "cli_default",
        "cli_fork",
        "cinematic",
        "build",
        "imagine_video",
        "imagine_image",
    }
    # Unified 4.5 collapses cinematic + build + cli to one entry in unique tuple
    assert REQUIRED_MODEL_SLUGS == tuple(dict.fromkeys(REQUIRED_MODEL_ROLES.values()))
    assert REQUIRED_MODEL_SLUGS.count("grok-4.5") == 1


def test_model_stack_summary_unified() -> None:
    stack = model_stack_summary()
    assert stack["xai_chat"] == "grok-4.5"
    assert stack["xai_build"] == "grok-4.5"
    assert stack["grok_build_cli_default"] == "grok-4.5"
    assert stack["grok_build_cli_min_version"] == "0.2.93"


def test_model_compatibility() -> None:
    result = verify_model_compatibility()
    assert result["compatible"], result["issues"]
    assert result["studio_version"] == "3.6.7"
    assert result["min_grok_build_cli_version"] == "0.2.93"
    assert "required_roles" in result
    assert isinstance(result.get("warnings"), list)
    # Unified stack emits an informational warning, not a hard failure
    assert any("unified" in w for w in result["warnings"])


if __name__ == "__main__":
    test_role_defaults_are_single_source()
    test_no_per_model_default_flags()
    test_registry_contains_both_generations()
    test_long_context_aliases()
    test_build_and_cinematic_aliases()
    test_default_resolve_is_cinematic()
    test_unknown_slug_falls_back_but_is_not_known()
    test_required_roles_have_unique_slugs()
    test_model_stack_summary_unified()
    test_model_compatibility()
    print("All chat model tests passed")
