#!/usr/bin/env python3
"""
Canonical Grok Build / xAI model registry for Grok Imagine Cinematic Studio.

Single source of truth for CLI, Web UI, quota optimizer, skill model layers,
and documentation. Updated for Grok 4.5 / v9-4p5 surface variants.

Schema Version: 1.1 (2026-07-20)
"""

from __future__ import annotations

from typing import Any

SCHEMA_VERSION = "1.1"

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
# Primary Chat / Orchestration Models (xAI surfaces + internal routing)
# Includes the v9-4p5 family requested for skill enhancement
# ---------------------------------------------------------------------------

XAI_CHAT_MODELS: dict[str, dict[str, Any]] = {
    # --- Current production 4.5 / v9 family ---
    "grok-v9-4p5-chat-expert": {
        "label": "Grok v9 4.5 Chat Expert",
        "context_tokens": 1_000_000,
        "input_usd_per_1m": 1.25,
        "output_usd_per_1m": 2.50,
        "use_case": "Highest-quality single-agent chat, deep reasoning, expert cinematic direction, complex prompt craft",
        "strengths": ["reasoning", "prompt_quality", "character_consistency", "long_context"],
        "preferred_for": ["Studio Director", "Imagine Prompt Master", "Narrative Arc", "QA Guardian"],
        "default": True,
        "aliases": ["v9-4p5-chat-expert", "chat-expert", "4p5-expert", "grok-4.5-expert"],
    },
    "grok-v9-4p5-multi": {
        "label": "Grok v9 4.5 Multi",
        "context_tokens": 1_000_000,
        "input_usd_per_1m": 1.25,
        "output_usd_per_1m": 2.50,
        "use_case": "Multi-agent orchestration, Team Leader synthesis, parallel specialist coordination, handoff packet work",
        "strengths": ["multi_agent", "handoff_integrity", "parallel_reasoning", "synthesis"],
        "preferred_for": ["Team Leader", "Studio Director (Full Studio Mode)", "Mega Production Architect", "Sequence Director"],
        "default": False,
        "aliases": ["v9-4p5-multi", "4p5-multi", "multi", "grok-4.5-multi"],
    },
    "grok-4-auto": {
        "label": "Grok 4 Auto",
        "context_tokens": 512_000,
        "input_usd_per_1m": 1.00,
        "output_usd_per_1m": 2.00,
        "use_case": "Automatic routing / balanced general-purpose. Good default when model choice is not critical.",
        "strengths": ["balanced", "speed", "general"],
        "preferred_for": ["Routine specialist work", "draft passes", "quota-sensitive sessions"],
        "default": False,
        "aliases": ["4-auto", "auto", "grok-auto"],
    },
    # --- Legacy / fallback ---
    "grok-4.3": {
        "label": "Grok 4.3 (Legacy 1M)",
        "context_tokens": 1_000_000,
        "input_usd_per_1m": 1.25,
        "output_usd_per_1m": 2.50,
        "use_case": "Previous long-context cinematic orchestration (kept for compatibility)",
        "strengths": ["long_context"],
        "preferred_for": ["Legacy Production Bibles", "1M context fallback"],
        "default": False,
        "aliases": ["4.3", "grok-4.3-legacy"],
    },
    "grok-build-0.1": {
        "label": "Grok Build 0.1",
        "context_tokens": 256_000,
        "input_usd_per_1m": 1.00,
        "output_usd_per_1m": 2.00,
        "use_case": "Coding, agentic workflows, CLI automation, structured tool use",
        "strengths": ["coding", "tool_use"],
        "preferred_for": ["Grok Build CLI", "skill development", "scripts"],
        "default": False,
        "aliases": ["build", "grok-build"],
    },
}

DEFAULT_XAI_CHAT_MODEL = "grok-v9-4p5-chat-expert"
DEFAULT_XAI_MULTI_MODEL = "grok-v9-4p5-multi"
DEFAULT_XAI_AUTO_MODEL = "grok-4-auto"
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
    """Resolve chat model slug; falls back to default (chat-expert)."""
    if not slug:
        return DEFAULT_XAI_CHAT_MODEL
    normalized = slug.strip().lower()
    if normalized in XAI_CHAT_MODELS:
        return normalized
    # Flatten aliases
    for model_id, info in XAI_CHAT_MODELS.items():
        if normalized in [a.lower() for a in info.get("aliases", [])]:
            return model_id
    # Legacy shortcuts
    aliases = {
        "grok-4.5": DEFAULT_XAI_CHAT_MODEL,
        "4.5": DEFAULT_XAI_CHAT_MODEL,
        "expert": DEFAULT_XAI_CHAT_MODEL,
        "multi": DEFAULT_XAI_MULTI_MODEL,
        "auto": DEFAULT_XAI_AUTO_MODEL,
        "build": DEFAULT_XAI_BUILD_MODEL,
        "4.3": "grok-4.3",
    }
    return aliases.get(normalized, DEFAULT_XAI_CHAT_MODEL)


def get_model_info(slug: str) -> dict[str, Any] | None:
    """Return full info dict for a chat model slug (resolved)."""
    resolved = resolve_chat_model(slug)
    return XAI_CHAT_MODELS.get(resolved)


def recommended_model_for_role(role: str) -> str:
    """Simple role → preferred model helper for skills."""
    role = role.lower().strip()
    mapping = {
        "team leader": DEFAULT_XAI_MULTI_MODEL,
        "studio director": DEFAULT_XAI_MULTI_MODEL,
        "mega production architect": DEFAULT_XAI_MULTI_MODEL,
        "sequence director": DEFAULT_XAI_MULTI_MODEL,
        "imagine prompt master": DEFAULT_XAI_CHAT_MODEL,
        "prompt master": DEFAULT_XAI_CHAT_MODEL,
        "qa": DEFAULT_XAI_CHAT_MODEL,
        "quality assurance": DEFAULT_XAI_CHAT_MODEL,
        "identity lock": DEFAULT_XAI_CHAT_MODEL,
        "dna": DEFAULT_XAI_CHAT_MODEL,
        "default": DEFAULT_XAI_CHAT_MODEL,
        "auto": DEFAULT_XAI_AUTO_MODEL,
        "draft": DEFAULT_XAI_AUTO_MODEL,
        "build": DEFAULT_XAI_BUILD_MODEL,
        "coding": DEFAULT_XAI_BUILD_MODEL,
    }
    return mapping.get(role, DEFAULT_XAI_CHAT_MODEL)


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
            "multi_default": DEFAULT_XAI_MULTI_MODEL,
            "auto_default": DEFAULT_XAI_AUTO_MODEL,
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
