#!/usr/bin/env python3
"""
Canonical Grok Build / xAI model registry for Grok Imagine Cinematic Studio.

Single source of truth for CLI, Web UI, quota optimizer, and documentation.
"""

from __future__ import annotations

from typing import Any

SCHEMA_VERSION = "1.0"

# ---------------------------------------------------------------------------
# Grok Build CLI (local agent environment — `grok models`)
# ---------------------------------------------------------------------------

GROK_BUILD_CLI_MODELS: dict[str, dict[str, Any]] = {
    "grok-composer-2.5-fast": {
        "label": "Grok Composer 2.5 Fast",
        "role": "default",
        "description": "Default Grok Build agent — fast orchestration and creative direction",
    },
    "grok-build": {
        "label": "Grok Build",
        "role": "coding",
        "description": "Secondary fork model for code generation, tooling, and agentic workflows",
    },
}

DEFAULT_GROK_BUILD_MODEL = "grok-composer-2.5-fast"
GROK_BUILD_FORK_MODEL = "grok-build"

# ---------------------------------------------------------------------------
# xAI API chat models (https://api.x.ai/v1)
# ---------------------------------------------------------------------------

XAI_CHAT_MODELS: dict[str, dict[str, Any]] = {
    "grok-4.3": {
        "label": "Grok 4.3",
        "context_tokens": 1_000_000,
        "input_usd_per_1m": 1.25,
        "output_usd_per_1m": 2.50,
        "use_case": "cinematic orchestration, 1M context, complex multi-agent productions",
        "default": True,
    },
    "grok-build-0.1": {
        "label": "Grok Build 0.1",
        "context_tokens": 256_000,
        "input_usd_per_1m": 1.00,
        "output_usd_per_1m": 2.00,
        "use_case": "coding, agentic workflows, CLI automation, structured tool use",
        "default": False,
    },
}

DEFAULT_XAI_CHAT_MODEL = "grok-4.3"
DEFAULT_XAI_BUILD_MODEL = "grok-build-0.1"

# ---------------------------------------------------------------------------
# Grok Imagine models (image + video generation)
# ---------------------------------------------------------------------------

IMAGINE_VIDEO_MODELS: dict[str, dict[str, Any]] = {
    "grok-imagine-video-1.5": {
        "label": "Imagine Video 1.5",
        "usd_per_second": 0.080,
        "native_audio": True,
        "default": True,
        "aliases": ["imagine-video-1.5", "video-1.5", "1.5"],
    },
    "grok-imagine-video": {
        "label": "Imagine Video 1.0",
        "usd_per_second": 0.050,
        "native_audio": False,
        "default": False,
        "aliases": ["imagine-video", "video-1.0", "1.0"],
    },
}

IMAGINE_IMAGE_MODELS: dict[str, dict[str, Any]] = {
    "grok-imagine-image": {
        "label": "Imagine Image",
        "usd_per_image": 0.02,
        "default": True,
        "aliases": ["imagine-image", "image"],
    },
    "grok-imagine-image-quality": {
        "label": "Imagine Image Quality",
        "usd_per_image": 0.05,
        "default": False,
        "aliases": ["imagine-image-quality", "image-quality", "quality"],
    },
}

DEFAULT_IMAGINE_VIDEO_MODEL = "grok-imagine-video-1.5"
DEFAULT_IMAGINE_IMAGE_MODEL = "grok-imagine-image"

# Credit conversion: 1 credit = $0.01 (for quota dashboard compatibility)
USD_PER_CREDIT = 0.01


def resolve_video_model(slug: str | None = None) -> str:
    """Resolve alias or shorthand to canonical Imagine video model slug."""
    if not slug:
        return DEFAULT_IMAGINE_VIDEO_MODEL
    normalized = slug.strip().lower()
    if normalized in IMAGINE_VIDEO_MODELS:
        return normalized
    for model_id, info in IMAGINE_VIDEO_MODELS.items():
        if normalized in info.get("aliases", []):
            return model_id
    return DEFAULT_IMAGINE_VIDEO_MODEL


def resolve_image_model(slug: str | None = None) -> str:
    """Resolve alias or shorthand to canonical Imagine image model slug."""
    if not slug:
        return DEFAULT_IMAGINE_IMAGE_MODEL
    normalized = slug.strip().lower()
    if normalized in IMAGINE_IMAGE_MODELS:
        return normalized
    for model_id, info in IMAGINE_IMAGE_MODELS.items():
        if normalized in info.get("aliases", []):
            return model_id
    return DEFAULT_IMAGINE_IMAGE_MODEL


def resolve_chat_model(slug: str | None = None) -> str:
    """Resolve chat model slug; falls back to default."""
    if not slug:
        return DEFAULT_XAI_CHAT_MODEL
    normalized = slug.strip().lower()
    if normalized in XAI_CHAT_MODELS:
        return normalized
    aliases = {
        "grok-build": DEFAULT_XAI_BUILD_MODEL,
        "build": DEFAULT_XAI_BUILD_MODEL,
        "grok-4": DEFAULT_XAI_CHAT_MODEL,
        "4.3": DEFAULT_XAI_CHAT_MODEL,
    }
    return aliases.get(normalized, DEFAULT_XAI_CHAT_MODEL)


def usd_to_credits(usd: float) -> float:
    return round(usd / USD_PER_CREDIT, 2)


def video_usd_per_second(model: str | None = None) -> float:
    slug = resolve_video_model(model)
    return IMAGINE_VIDEO_MODELS[slug]["usd_per_second"]


def image_usd_per_image(model: str | None = None) -> float:
    slug = resolve_image_model(model)
    return IMAGINE_IMAGE_MODELS[slug]["usd_per_image"]


def list_all_models() -> dict[str, Any]:
    """Return full registry for CLI/UI display."""
    return {
        "schema_version": SCHEMA_VERSION,
        "grok_build_cli": {
            "default": DEFAULT_GROK_BUILD_MODEL,
            "fork_secondary": GROK_BUILD_FORK_MODEL,
            "models": GROK_BUILD_CLI_MODELS,
        },
        "xai_chat": {
            "default": DEFAULT_XAI_CHAT_MODEL,
            "build_default": DEFAULT_XAI_BUILD_MODEL,
            "models": XAI_CHAT_MODELS,
        },
        "imagine_video": {
            "default": DEFAULT_IMAGINE_VIDEO_MODEL,
            "models": IMAGINE_VIDEO_MODELS,
        },
        "imagine_image": {
            "default": DEFAULT_IMAGINE_IMAGE_MODEL,
            "models": IMAGINE_IMAGE_MODELS,
        },
        "usd_per_credit": USD_PER_CREDIT,
    }