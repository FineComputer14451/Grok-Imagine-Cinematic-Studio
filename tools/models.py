#!/usr/bin/env python3
"""
Canonical Grok Build / xAI model registry for Grok Imagine Cinematic Studio (v3.11.3 · Grok 4.6 + v9-4p5).

Single source of truth for CLI, Web UI, quota optimizer, and documentation.
Imagine family: Image 1.0 / 2.0 + Video 1.0 / 1.5 (there is no video 2.0).
``grok-imagine-image-quality`` retires 2026-11-02 → Image 2.0 ``quality=low``.

Unified chat stack:
  - Cinematic orchestration (Production Bibles, multi-agent): grok-4.6
  - Grok Build / coding / agentic: grok-4.6
  - grok-4.5 and cinematic/build/coding aliases resolve to grok-4.6
  - Optional long-context (1M): grok-4.3 via --chat-model grok-4.3
  - Recommended CLI binary: Grok Build ≥ 1.0.5 (not an API slug)
"""

from __future__ import annotations

import re
import shutil
import subprocess
from typing import Any

SCHEMA_VERSION = "1.6"

# ---------------------------------------------------------------------------
# Dual-stack product pins + full role defaults (literals appear once)
# ---------------------------------------------------------------------------

# Change only with a deliberate studio upgrade (also asserted in tests)
STACK_CONTRACT: dict[str, str] = {
    "cinematic": "grok-4.6",
    "build": "grok-4.6",
    "cli": "grok-4.6",
}

# Single source of truth for “which model for which job”
ROLE_DEFAULTS: dict[str, str] = {
    **STACK_CONTRACT,
    "cli_fork": "grok-build",
    "imagine_video": "grok-imagine-video",
    "imagine_image": "grok-imagine-image",
}

# Recommended Grok Build binary version (not an API model slug)
RECOMMENDED_GROK_BUILD_CLI_VERSION = "1.0.5"
# Back-compat alias used by stack summary / older imports
MIN_GROK_BUILD_CLI_VERSION = RECOMMENDED_GROK_BUILD_CLI_VERSION

DEFAULT_XAI_CHAT_MODEL = ROLE_DEFAULTS["cinematic"]
DEFAULT_XAI_CHAT_EXPERT_MODEL = "grok-v9-4p5-chat-expert"
DEFAULT_XAI_MULTI_MODEL = "grok-v9-4p5-multi"
DEFAULT_XAI_AUTO_MODEL = "grok-4-auto"
DEFAULT_XAI_BUILD_MODEL = ROLE_DEFAULTS["build"]
DEFAULT_GROK_BUILD_MODEL = ROLE_DEFAULTS["cli"]
GROK_BUILD_FORK_MODEL = ROLE_DEFAULTS["cli_fork"]
DEFAULT_IMAGINE_VIDEO_MODEL = ROLE_DEFAULTS["imagine_video"]
DEFAULT_IMAGINE_IMAGE_MODEL = ROLE_DEFAULTS["imagine_image"]
HERO_IMAGINE_IMAGE_MODEL = "grok-imagine-image-2.0"
LEGACY_QUALITY_IMAGE_MODEL = "grok-imagine-image-quality"
LEGACY_QUALITY_RETIRED_ON = "2026-11-02"
LEGACY_QUALITY_REDIRECT_QUALITY = "low"
IMAGE_QUALITY_VALUES = ("low", "medium", "auto")
NATIVE_AUDIO_VIDEO_MODEL = "grok-imagine-video-1.5"
EDIT_EXTEND_VIDEO_MODEL = "grok-imagine-video"

# ---------------------------------------------------------------------------
# Grok Build CLI picker (local agent environment — `grok models`)
# ---------------------------------------------------------------------------

GROK_BUILD_CLI_MODELS: dict[str, dict[str, Any]] = {
    "grok-4.6": {
        "label": "Grok 4.6",
        "role": "default",
        "description": "Default agent — cinematic orchestration, coding, agentic tasks",
    },
    "grok-4.5": {
        "label": "Grok 4.5",
        "role": "legacy_default",
        "description": "Legacy picker id — wraps grok-4.6 (alias, not a second stack default)",
    },
    "grok-composer-2.5-fast": {
        "label": "Grok Composer 2.5 Fast",
        "role": "creative",
        "description": "Fast creative orchestration and multi-agent cinematic direction",
    },
    "grok-build": {
        "label": "Grok Build",
        "role": "coding",
        "description": "Fork secondary / coding alias (Grok 4.6 stack)",
    },
    "grok-4.3": {
        "label": "Grok 4.3",
        "role": "long_context",
        "description": "Optional 1M-context orchestration (opt-in via --chat-model grok-4.3)",
    },
}

# ---------------------------------------------------------------------------
# Grok Build custom NSFW / ErosForge picker aliases (opt-in)
# These are NOT separate API products — they map to chat base models with
# role-tuned sampling in ~/.grok/config.toml (see config/grok-build-nsfw-models.example.toml).
# Install: bash scripts/install_nsfw_grok_models.sh
# ---------------------------------------------------------------------------

GROK_BUILD_NSFW_MODELS: dict[str, dict[str, Any]] = {
    "erosforge-director": {
        "label": "ErosForge Director",
        "role": "nsfw_director",
        "base_model": "grok-4.6",
        "temperature": 0.92,
        "description": "Intimate scene design, consent framing, 1.5 intimacy physics",
        "aliases": ["erosforge", "nsfw-director"],
    },
    "nsfw-prompt-master": {
        "label": "NSFW Prompt Master",
        "role": "nsfw_prompt",
        "base_model": "grok-4.6",
        "temperature": 0.78,
        "description": "Erotic prompt craft — DNA inject, Ultimate Template, negatives",
        "aliases": ["nsfw-prompt", "erotic-prompt"],
    },
    "nsfw-quota-planner": {
        "label": "NSFW Quota Planner",
        "role": "nsfw_quota",
        "base_model": "grok-4.6",
        "temperature": 0.35,
        "description": "Hero-first NSFW batch economics under Heavy caps",
        "aliases": ["nsfw-quota", "nsfw-batch-planner"],
    },
    "nsfw-sequence-extend": {
        "label": "NSFW Sequence Extend",
        "role": "nsfw_extend",
        "base_model": "grok-4.6",
        "temperature": 0.72,
        "description": "Sensual 30–120s+ tension curves and extend handoffs",
        "aliases": ["nsfw-extend", "nsfw-sequence"],
    },
    "nsfw-chain-qa": {
        "label": "NSFW Chain QA",
        "role": "nsfw_qa",
        "base_model": "grok-4.6",
        "temperature": 0.25,
        "description": "8-point intimate artifact gate before extend/stitch",
        "aliases": ["nsfw-qa"],
    },
    "nsfw-identity-lock": {
        "label": "NSFW Identity Lock",
        "role": "nsfw_identity",
        "base_model": "grok-4.6",
        "temperature": 0.40,
        "description": "Intimate multi-scene body/face consistency",
        "aliases": ["nsfw-identity", "nsfw-dna"],
    },
    "nsfw-long-context": {
        "label": "NSFW Long Context",
        "role": "nsfw_long_context",
        "base_model": "grok-4.3",
        "temperature": 0.70,
        "description": "1M multi-scene intimacy Bibles (opt-in)",
        "aliases": ["nsfw-1m", "nsfw-long"],
    },
    "nsfw-creative-fast": {
        "label": "NSFW Creative Fast",
        "role": "nsfw_creative",
        "base_model": "grok-composer-2.5-fast",
        "temperature": 0.95,
        "description": "Fast NSFW beat boards and rough shot lists",
        "aliases": ["nsfw-fast", "nsfw-draft"],
    },
}

# ---------------------------------------------------------------------------
# Grok Build v9-4p5 / Auto specialist picker aliases (Model Layer v4.5)
# Native product IDs are not always on the public xAI API; these wrap grok-4.6
# with role-tuned sampling via cli-chat-proxy. Install:
#   bash scripts/install_v9_grok_models.sh
# ---------------------------------------------------------------------------

GROK_BUILD_V9_MODELS: dict[str, dict[str, Any]] = {
    "grok-v9-4p5-chat-expert": {
        "label": "Grok v9 4.5 Chat Expert",
        "role": "specialist_craft",
        "base_model": "grok-4.6",
        "temperature": 0.55,
        "description": "Specialist craft — DNA, hero prompts, DoP, QA (high reasoning)",
        "aliases": [
            "v9-4p5-chat-expert",
            "chat-expert",
            "4p5-expert",
            "grok-4.5-expert",
            # Family short names → craft default (not multi)
            "grok-v9",
            "grok-v9-4p5",
            "v9",
            "v9-4p5",
        ],
    },
    "grok-v9-4p5-multi": {
        "label": "Grok v9 4.5 Multi",
        "role": "multi_agent",
        "base_model": "grok-4.6",
        "temperature": 0.65,
        "description": "Multi-agent orchestration — handoffs, sequences, Team Leader",
        "aliases": ["v9-4p5-multi", "4p5-multi", "multi", "grok-4.5-multi"],
    },
    "grok-4-auto": {
        "label": "Grok 4 Auto",
        "role": "auto_route",
        "base_model": "grok-4.6",
        "temperature": 0.50,
        "description": "Draft / quota / automatic routing (medium reasoning)",
        "aliases": ["4-auto", "auto", "grok-auto"],
    },
}

# Role display name / skill slug → preferred specialist chat model
# (registry stack default remains grok-4.6; this is Model Layer routing only)
ROLE_MODEL_PREFERENCES: dict[str, str] = {
    # Multi-agent / orchestration
    "team leader": DEFAULT_XAI_MULTI_MODEL,
    "studio director": DEFAULT_XAI_MULTI_MODEL,
    "studio director (full studio mode)": DEFAULT_XAI_MULTI_MODEL,
    "mega production architect": DEFAULT_XAI_MULTI_MODEL,
    "sequence director": DEFAULT_XAI_MULTI_MODEL,
    "cinematic sequence extender": DEFAULT_XAI_MULTI_MODEL,
    "continuity consistency guardian": DEFAULT_XAI_MULTI_MODEL,
    "continuity & consistency guardian": DEFAULT_XAI_MULTI_MODEL,
    # Specialist craft
    "imagine prompt master": DEFAULT_XAI_CHAT_EXPERT_MODEL,
    "character dna extractor": DEFAULT_XAI_CHAT_EXPERT_MODEL,
    "identity lock specialist": DEFAULT_XAI_CHAT_EXPERT_MODEL,
    "quality assurance guardian": DEFAULT_XAI_CHAT_EXPERT_MODEL,
    "qa guardian": DEFAULT_XAI_CHAT_EXPERT_MODEL,
    "narrative arc": DEFAULT_XAI_CHAT_EXPERT_MODEL,
    "narrative arc pacing strategist": DEFAULT_XAI_CHAT_EXPERT_MODEL,
    "director of photography": DEFAULT_XAI_CHAT_EXPERT_MODEL,
    "sonic architect": DEFAULT_XAI_CHAT_EXPERT_MODEL,
    "sonic architect native audio virtuoso": DEFAULT_XAI_CHAT_EXPERT_MODEL,
    "erosforge nsfw director": DEFAULT_XAI_CHAT_EXPERT_MODEL,
    "costume wardrobe continuity": DEFAULT_XAI_CHAT_EXPERT_MODEL,
    "performance emotion director": DEFAULT_XAI_CHAT_EXPERT_MODEL,
    # Draft / quota
    "animatic director": DEFAULT_XAI_AUTO_MODEL,
    "reference asset curator": DEFAULT_XAI_AUTO_MODEL,
    "generation tracker": DEFAULT_XAI_AUTO_MODEL,
    "workflow quota optimizer": DEFAULT_XAI_AUTO_MODEL,
}

# ---------------------------------------------------------------------------
# xAI API chat models (https://api.x.ai/v1)
# Defaults are ROLE_DEFAULTS only — no per-entry default/build_default flags.
# ---------------------------------------------------------------------------

XAI_CHAT_MODELS: dict[str, dict[str, Any]] = {
    # --- v9-4p5 surface family (opt-in aliases; grok-4.6 is stack default) ---
    # Note: public api.x.ai may not list these product IDs; Grok Build pickers
    # install via scripts/install_v9_grok_models.sh (base_model grok-4.6).
    "grok-v9-4p5-chat-expert": {
        "label": "Grok v9 4.5 Chat Expert",
        "context_tokens": 1_000_000,
        "input_usd_per_1m": 1.25,
        "output_usd_per_1m": 2.50,
        "use_case": "Highest-quality single-agent chat, deep reasoning, expert cinematic direction",
        "role": "specialist_craft",
        "strengths": ["reasoning", "prompt_quality", "character_consistency", "long_context"],
        "preferred_for": ["Studio Director", "Imagine Prompt Master", "Narrative Arc", "QA Guardian"],
        "aliases": [
            "v9-4p5-chat-expert",
            "chat-expert",
            "4p5-expert",
            "grok-4.5-expert",
            # Family short names → chat-expert (craft default)
            "grok-v9",
            "grok-v9-4p5",
            "v9",
            "v9-4p5",
        ],
    },
    "grok-v9-4p5-multi": {
        "label": "Grok v9 4.5 Multi",
        "context_tokens": 1_000_000,
        "input_usd_per_1m": 1.25,
        "output_usd_per_1m": 2.50,
        "use_case": "Multi-agent orchestration, Team Leader synthesis, parallel specialist coordination",
        "role": "multi_agent",
        "strengths": ["multi_agent", "handoff_integrity", "parallel_reasoning", "synthesis"],
        "preferred_for": ["Team Leader", "Studio Director (Full Studio Mode)", "Mega Production Architect", "Sequence Director"],
        "aliases": ["v9-4p5-multi", "4p5-multi", "multi", "grok-4.5-multi"],
    },
    "grok-4-auto": {
        "label": "Grok 4 Auto",
        "context_tokens": 512_000,
        "input_usd_per_1m": 1.00,
        "output_usd_per_1m": 2.00,
        "use_case": "Automatic routing / balanced general-purpose",
        "role": "auto_route",
        "strengths": ["balanced", "speed", "general"],
        "preferred_for": ["Routine specialist work", "draft passes", "quota-sensitive sessions"],
        "aliases": ["4-auto", "auto", "grok-auto"],
    },

    "grok-4.3": {
        "label": "Grok 4.3",
        "context_tokens": 1_000_000,
        "input_usd_per_1m": 1.25,
        "output_usd_per_1m": 2.50,
        "use_case": "optional 1M-context Production Bibles and multi-agent memory banks",
        "role": "long_context",
        "aliases": ["4.3", "long-context", "grok-4"],
    },
    "grok-4.6": {
        "label": "Grok 4.6",
        "context_tokens": 500_000,
        "input_usd_per_1m": 2.00,
        "cached_input_usd_per_1m": 0.50,
        "output_usd_per_1m": 6.00,
        "use_case": "cinematic default, coding, agentic workflows, Grok Build, structured tool use",
        "role": "default",
        "reasoning": "low|medium|high (default high)",
        "aliases": [
            "4.6",
            "grok-4.6-latest",
            "grok-4.5",
            "4.5",
            "grok-4.5-latest",
            "grok-build-latest",
            "coding",
            "grok-build",
            "build",
            "cinematic",
        ],
    },
    "grok-build-0.1": {
        "label": "Grok Build 0.1",
        "context_tokens": 256_000,
        "input_usd_per_1m": 1.00,
        "output_usd_per_1m": 2.00,
        "use_case": "legacy coding API — prefer grok-4.6",
        "role": "legacy_build",
        "deprecated": True,
        "aliases": [],
    },
}

# ---------------------------------------------------------------------------
# Grok Imagine models (image + video generation)
# ---------------------------------------------------------------------------

IMAGINE_VIDEO_MODELS: dict[str, dict[str, Any]] = {
    "grok-imagine-video-1.5": {
        "label": "Imagine Video 1.5",
        "version": "1.5",
        "usd_per_second": 0.080,
        "usd_per_second_by_resolution": {"480p": 0.080, "720p": 0.140, "1080p": 0.250},
        "native_audio": True,
        "modalities": "text, image, audio → video",
        "max_resolution": "1080p",
        "max_duration_s": 15,
        "modes": ("t2v", "i2v", "r2v"),
        "r2v_max_resolution": "720p",
        "max_reference_images": 7,
        "max_reference_voices": 3,
        "version_date": "2026-05-30",
        "regions": ["us-east-1", "eu-west-1", "us-west-2"],
        "aliases": [
            "grok-imagine-video-1.5-preview",
            "grok-imagine-video-1.5-2026-05-30",
            "imagine-video-1.5",
            "video-1.5",
            "1.5",
            "1.5-preview",
            "preview",
        ],
    },
    "grok-imagine-video": {
        "label": "Imagine Video 1.0",
        "version": "1.0",
        "usd_per_second": 0.050,
        "usd_per_second_by_resolution": {"480p": 0.050, "720p": 0.070},
        "native_audio": False,
        "modalities": "text, image, video → video",
        "max_resolution": "720p",
        "max_duration_s": 15,
        "modes": ("t2v", "i2v", "edit", "extend"),
        "version_date": "2026-02-02",
        "regions": ["us-east-1", "eu-west-1", "us-west-2"],
        "aliases": ["imagine-video", "video-1.0", "1.0"],
    },
}

IMAGINE_IMAGE_MODELS: dict[str, dict[str, Any]] = {
    "grok-imagine-image": {
        "label": "Imagine Image",
        "version": "1.0",
        "usd_per_image": 0.02,
        "usd_per_input_image": 0.002,
        "usd_by_resolution_quality": {
            "1k": {"low": 0.02, "medium": 0.02},
            "2k": {"low": 0.02, "medium": 0.02},
        },
        "quality_param": False,
        "modalities": "text, image → image",
        "max_edit_refs": 3,
        "version_date": "2026-03-02",
        "regions": ["us-east-1", "eu-west-1", "us-west-2"],
        "aliases": [
            "grok-imagine-image-2026-03-02",
            "imagine-image",
            "image",
            "image-1.0",
        ],
    },
    "grok-imagine-image-quality": {
        "label": "Imagine Image Quality",
        "version": "quality",
        "usd_per_image": 0.04,
        "legacy_usd_per_image": 0.05,
        "usd_per_input_image": 0.01,
        "usd_by_resolution_quality": {
            "1k": {"low": 0.04, "medium": 0.06},
            "2k": {"low": 0.06, "medium": 0.08},
        },
        "quality_param": False,
        "deprecated": True,
        "retired_on": LEGACY_QUALITY_RETIRED_ON,
        "redirect_model": HERO_IMAGINE_IMAGE_MODEL,
        "redirect_quality": LEGACY_QUALITY_REDIRECT_QUALITY,
        "modalities": "text, image → image",
        "max_edit_refs": 3,
        "version_date": "2026-04-03",
        "regions": ["us-east-1", "eu-west-1", "us-west-2"],
        "aliases": [
            "grok-imagine-image-quality-20260403",
            "grok-imagine-image-quality-latest",
            "grok-imagine-image-pro",
            "imagine-image-quality",
            "image-quality",
            "quality",
            "pro",
        ],
    },
    "grok-imagine-image-2.0": {
        "label": "Imagine Image 2.0",
        "version": "2.0",
        "usd_per_image": 0.04,
        "usd_per_input_image": 0.01,
        "usd_by_resolution_quality": {
            "1k": {"low": 0.04, "medium": 0.06},
            "2k": {"low": 0.06, "medium": 0.08},
        },
        "quality_param": True,
        "quality_values": IMAGE_QUALITY_VALUES,
        "default_quality": "auto",
        "modalities": "text, image → image",
        "max_edit_refs": 5,
        "hero": True,
        "version_date": "2026-08-07",
        "regions": ["us-east-1", "us-west-2"],
        "aliases": [
            "image-2.0",
            "2.0",
            "imagine-image-2.0",
            "grok-imagine-image-2",
            "image-2",
        ],
    },
}

# Official Agent Mode / operator surfaces (packet enum lives in handoff_schema.py).
IMAGINE_AGENT_SURFACES: tuple[dict[str, Any], ...] = (
    {
        "id": "grok_build_tools",
        "letter": "A",
        "label": "Grok Build session tools",
        "tools": ("image_gen", "image_edit", "image_to_video", "reference_to_video"),
    },
    {
        "id": "grok_agent_acp",
        "letter": "B",
        "label": "Grok agent ACP",
        "tools": ("image_gen", "image_edit", "image_to_video", "reference_to_video", "cli"),
    },
    {
        "id": "grok_com_imagine",
        "letter": "C",
        "label": "grok.com/imagine (+ mobile)",
        "tools": ("manual_paste",),
        "aliases": ("grok_mobile_imagine",),
    },
    {
        "id": "xai_api",
        "letter": "D",
        "label": "xAI Imagine REST API",
        "tools": ("images/generations", "images/edits", "videos/generations", "videos/edits", "videos/extensions"),
    },
    {
        "id": "xai_responses_tool",
        "letter": "E",
        "label": "Responses API image_generation tool",
        "tools": ("image_generation",),
        "aliases": ("responses", "image_generation_tool"),
        "imagine_image": "grok-imagine-image-2.0",
    },
)

IMAGINE_REST_ENDPOINTS: tuple[dict[str, str], ...] = (
    {"mode": "image_prompt", "method": "POST", "path": "/v1/images/generations"},
    {"mode": "image_edit", "method": "POST", "path": "/v1/images/edits"},
    {"mode": "video_prompt", "method": "POST", "path": "/v1/videos/generations"},
    {"mode": "image_to_video", "method": "POST", "path": "/v1/videos/generations"},
    {"mode": "reference_to_video", "method": "POST", "path": "/v1/videos/generations"},
    {"mode": "video_edit", "method": "POST", "path": "/v1/videos/edits"},
    {"mode": "video_extend", "method": "POST", "path": "/v1/videos/extensions"},
)

STUDIO_COMPATIBILITY_VERSION = "3.11.3"

# Role → slug (unique by construction; no duplicate bag)
REQUIRED_MODEL_ROLES: dict[str, str] = {
    "cli_default": DEFAULT_GROK_BUILD_MODEL,
    "cli_fork": GROK_BUILD_FORK_MODEL,
    "cinematic": DEFAULT_XAI_CHAT_MODEL,
    "build": DEFAULT_XAI_BUILD_MODEL,
    "imagine_video": DEFAULT_IMAGINE_VIDEO_MODEL,
    "imagine_image": DEFAULT_IMAGINE_IMAGE_MODEL,
}
# Unique slugs only (order preserved)
REQUIRED_MODEL_SLUGS = tuple(dict.fromkeys(REQUIRED_MODEL_ROLES.values()))

USD_PER_CREDIT = 0.01


def is_cinematic_default(slug: str) -> bool:
    return slug == DEFAULT_XAI_CHAT_MODEL


def is_build_default(slug: str) -> bool:
    return slug == DEFAULT_XAI_BUILD_MODEL


def is_cli_default(slug: str) -> bool:
    return slug == DEFAULT_GROK_BUILD_MODEL


def _build_alias_map(registry: dict[str, dict[str, Any]]) -> dict[str, str]:
    """Build alias/shorthand → canonical slug map for a registry."""
    mapping: dict[str, str] = {}
    for model_id, info in registry.items():
        mapping[model_id.lower()] = model_id
        for alias in info.get("aliases", []):
            mapping[str(alias).strip().lower()] = model_id
    return mapping


# Built once after registries (immutable in practice for this module)
_CHAT_ALIAS_MAP = _build_alias_map(XAI_CHAT_MODELS)
_VIDEO_ALIAS_MAP = _build_alias_map(IMAGINE_VIDEO_MODELS)
_IMAGE_ALIAS_MAP = _build_alias_map(IMAGINE_IMAGE_MODELS)
_NSFW_BUILD_ALIAS_MAP = _build_alias_map(GROK_BUILD_NSFW_MODELS)
_V9_BUILD_ALIAS_MAP = _build_alias_map(GROK_BUILD_V9_MODELS)


def _resolve_from_alias_map(
    slug: str | None,
    alias_map: dict[str, str],
    default: str,
) -> str:
    if not slug:
        return default
    normalized = slug.strip().lower()
    if not normalized:
        return default
    return alias_map.get(normalized, default)


def resolve_video_model(slug: str | None = None) -> str:
    """Resolve alias or shorthand to canonical Imagine video model slug."""
    return _resolve_from_alias_map(slug, _VIDEO_ALIAS_MAP, DEFAULT_IMAGINE_VIDEO_MODEL)


def resolve_image_model(slug: str | None = None) -> str:
    """Resolve alias or shorthand to canonical Imagine image model slug."""
    return _resolve_from_alias_map(slug, _IMAGE_ALIAS_MAP, DEFAULT_IMAGINE_IMAGE_MODEL)


def is_legacy_quality_image_model(slug: str | None) -> bool:
    """True when slug/alias resolves to the retired quality product (not 2.0)."""
    if not slug or not str(slug).strip():
        return False
    return resolve_image_model(slug) == LEGACY_QUALITY_IMAGE_MODEL


def normalize_image_quality(value: str | None, *, strict: bool = False) -> str | None:
    """Return low|medium|auto, or None when omitted. Unknown non-empty raises if strict."""
    if value is None or not str(value).strip():
        return None
    key = str(value).strip().lower()
    if key in IMAGE_QUALITY_VALUES:
        return key
    if strict:
        raise ValueError(
            f"invalid image quality: {value!r}; expected one of {IMAGE_QUALITY_VALUES}"
        )
    return None


def resolve_image_request(
    model: str | None = None,
    *,
    quality: str | None = None,
    mode: str = "generate",
) -> tuple[str, str | None, list[str]]:
    """Map operator slug + quality to the Imagine wire payload.

    Returns ``(wire_slug, quality_to_send, warnings)``.
    ``quality_to_send`` is None when the API ``quality`` field must be omitted
    (Image 1.0, or Image 2.0 auto/default).
    """
    warnings: list[str] = []
    resolved = resolve_image_model(model)
    q = normalize_image_quality(quality, strict=True)
    info = IMAGINE_IMAGE_MODELS.get(resolved) or {}

    if resolved == LEGACY_QUALITY_IMAGE_MODEL:
        wire = str(info.get("redirect_model") or HERO_IMAGINE_IMAGE_MODEL)
        send = q or str(info.get("redirect_quality") or LEGACY_QUALITY_REDIRECT_QUALITY)
        warnings.append(
            f"{LEGACY_QUALITY_IMAGE_MODEL} retires {LEGACY_QUALITY_RETIRED_ON}; "
            f"studio sends {wire} with quality={send} (xAI redirect). "
            f"Pin --model {HERO_IMAGINE_IMAGE_MODEL} --quality medium for hero plates."
        )
        return wire, send, warnings

    if not info.get("quality_param"):
        if q is not None:
            warnings.append(
                f"{resolved} does not accept the quality parameter; omitting {q!r}"
            )
        return resolved, None, warnings

    # Image 2.0: omit quality unless the operator pinned low|medium|auto
    return resolved, q, warnings


def image_max_edit_refs(model: str | None = None) -> int:
    """Max source images for /images/edits on the resolved *wire* model."""
    wire, _, _ = resolve_image_request(model, mode="edit")
    info = IMAGINE_IMAGE_MODELS.get(wire) or {}
    return int(info.get("max_edit_refs") or 3)


def resolve_chat_model(slug: str | None = None) -> str:
    """Resolve chat model slug; empty/None → cinematic default (grok-4.6)."""
    return _resolve_from_alias_map(slug, _CHAT_ALIAS_MAP, DEFAULT_XAI_CHAT_MODEL)


def resolve_v9_build_model(slug: str | None = None) -> str | None:
    """Resolve Grok Build v9/auto picker alias → canonical custom-model id.

    Returns None when slug is empty. Unknown non-empty slugs return None
    (no silent fallback — use resolve_chat_model for chat registry).
    """
    if not slug or not str(slug).strip():
        return None
    normalized = str(slug).strip().lower()
    return _V9_BUILD_ALIAS_MAP.get(normalized)


def known_v9_build_model(slug: str | None) -> bool:
    """True if slug is a registered v9/auto Build picker id or alias."""
    if not slug or not str(slug).strip():
        return False
    return str(slug).strip().lower() in _V9_BUILD_ALIAS_MAP


def v9_build_base_model(slug: str | None) -> str | None:
    """Return the underlying chat base model for a v9/auto picker alias."""
    resolved = resolve_v9_build_model(slug)
    if not resolved:
        return None
    return GROK_BUILD_V9_MODELS[resolved].get("base_model")


def recommended_model_for_role(role: str | None) -> str:
    """Return preferred Model Layer chat slug for a Role Card / agent name.

    Falls back to DEFAULT_XAI_CHAT_EXPERT_MODEL for unknown specialist-style
    names, and DEFAULT_XAI_CHAT_MODEL only when role is empty.
    """
    if not role or not str(role).strip():
        return DEFAULT_XAI_CHAT_MODEL
    key = str(role).strip().lower()
    if key in ROLE_MODEL_PREFERENCES:
        return ROLE_MODEL_PREFERENCES[key]
    # Fuzzy contains match (e.g. "Imagine Prompt Master v3.5")
    for pref_key, slug in ROLE_MODEL_PREFERENCES.items():
        if pref_key in key or key in pref_key:
            return slug
    # Explicit multi/expert/auto keywords
    if any(t in key for t in ("multi", "handoff", "orchestrat", "team leader", "sequence")):
        return DEFAULT_XAI_MULTI_MODEL
    if any(t in key for t in ("draft", "animatic", "quota", "auto", "fast")):
        return DEFAULT_XAI_AUTO_MODEL
    return DEFAULT_XAI_CHAT_EXPERT_MODEL


def resolve_nsfw_build_model(slug: str | None = None) -> str | None:
    """Resolve Grok Build NSFW picker alias → canonical custom-model id.

    Returns None when slug is empty (no silent default — NSFW is opt-in).
    Unknown non-empty slugs fall back to erosforge-director only if they look
    like an NSFW alias miss; prefer known_nsfw_build_model() for strict checks.
    """
    if not slug or not str(slug).strip():
        return None
    normalized = str(slug).strip().lower()
    return _NSFW_BUILD_ALIAS_MAP.get(normalized)


def known_nsfw_build_model(slug: str | None) -> bool:
    """True if slug is a registered Grok Build NSFW custom-model id or alias."""
    if not slug or not str(slug).strip():
        return False
    return str(slug).strip().lower() in _NSFW_BUILD_ALIAS_MAP


def nsfw_build_base_model(slug: str | None) -> str | None:
    """Return the underlying chat/CLI base model for an NSFW picker alias."""
    resolved = resolve_nsfw_build_model(slug)
    if not resolved:
        return None
    return GROK_BUILD_NSFW_MODELS[resolved].get("base_model")


def known_chat_model(slug: str | None) -> bool:
    """True if slug is a registered chat model id or alias (not silent fallback)."""
    if not slug or not str(slug).strip():
        return False
    return str(slug).strip().lower() in _CHAT_ALIAS_MAP


def normalize_chat_model(slug: str | None) -> tuple[str, bool]:
    """Return (canonical_slug, is_known).

    Empty/None → cinematic default with is_known=True (intentional default).
    Unknown non-empty slug → cinematic default with is_known=False (silent fallback).
    """
    if not slug or not str(slug).strip():
        return DEFAULT_XAI_CHAT_MODEL, True
    if known_chat_model(slug):
        return resolve_chat_model(slug), True
    return DEFAULT_XAI_CHAT_MODEL, False


def usd_to_credits(usd: float) -> float:
    return round(usd / USD_PER_CREDIT, 2)


def _normalize_video_resolution(resolution: str | None) -> str | None:
    if not resolution or not str(resolution).strip():
        return None
    key = str(resolution).strip().lower()
    if key in ("480", "480p", "sd"):
        return "480p"
    if key in ("720", "720p", "hd"):
        return "720p"
    if key in ("1080", "1080p", "fhd", "fullhd"):
        return "1080p"
    return key


def _normalize_image_resolution(resolution: str | None) -> str:
    if not resolution or not str(resolution).strip():
        return "1k"
    key = str(resolution).strip().lower()
    if key in ("1k", "1", "1024"):
        return "1k"
    if key in ("2k", "2", "2048"):
        return "2k"
    return key


def video_usd_per_second(model: str | None = None, *, resolution: str | None = None) -> float:
    slug = resolve_video_model(model)
    info = IMAGINE_VIDEO_MODELS[slug]
    res = _normalize_video_resolution(resolution)
    if res:
        by_res = info.get("usd_per_second_by_resolution") or {}
        if res in by_res:
            return float(by_res[res])
    return float(info["usd_per_second"])


def image_usd_per_input_image(model: str | None = None) -> float:
    """USD per source image on /images/edits (and i2i). Quality slug → 2.0 rate."""
    wire, _, _ = resolve_image_request(model, mode="edit")
    info = IMAGINE_IMAGE_MODELS.get(wire) or {}
    return float(info.get("usd_per_input_image") or 0.0)


def image_usd_per_image(
    model: str | None = None,
    *,
    resolution: str | None = None,
    quality: str | None = None,
    mode: str | None = None,
    n_input_images: int = 0,
) -> float:
    """USD per generated image after quality-slug rewrite (retired quality → 2.0 low).

    ``n_input_images`` adds official input-image fees (1.0 $0.002; 2.0 $0.01).
    """
    job_mode = (mode or "generate").strip().lower()
    if job_mode not in ("generate", "edit"):
        job_mode = "generate"
    wire, quality_sent, _ = resolve_image_request(model, quality=quality, mode=job_mode)
    info = IMAGINE_IMAGE_MODELS[wire]
    table = info.get("usd_by_resolution_quality") or {}
    billed = quality_sent
    if billed is None or billed == "auto":
        billed = "medium" if job_mode == "edit" else "low"
    if resolution is None and quality is None and mode is None and quality_sent is None:
        out = float(info["usd_per_image"])
    else:
        res = _normalize_image_resolution(resolution)
        if res in table and billed in (table.get(res) or {}):
            out = float(table[res][billed])
        else:
            out = float(info["usd_per_image"])
    n_in = max(0, int(n_input_images or 0))
    if n_in:
        out += n_in * float(info.get("usd_per_input_image") or 0.0)
    return out


def video_supports_mode(model: str | None, mode: str) -> bool:
    slug = resolve_video_model(model)
    return mode in set(IMAGINE_VIDEO_MODELS[slug].get("modes") or ())


def recommended_video_model_for_mode(mode: str) -> str:
    """Pick 1.0 vs 1.5 from official capability split (edit/extend → 1.0, r2v → 1.5)."""
    key = (mode or "").strip().lower()
    if key in ("edit", "video_edit", "extend", "video_extend"):
        return EDIT_EXTEND_VIDEO_MODEL
    if key in ("r2v", "reference_to_video"):
        return NATIVE_AUDIO_VIDEO_MODEL
    return DEFAULT_IMAGINE_VIDEO_MODEL


def build_video_pipeline_spec(model: str | None = None, *, resolution: str = "720p") -> str:
    """Return locked VIDEO_PIPELINE_SPEC string for Production Bibles and prompts."""
    slug = resolve_video_model(model)
    info = IMAGINE_VIDEO_MODELS[slug]
    native = bool(info.get("native_audio", False))
    native_str = "true" if native else "false"
    version = str(info.get("version") or "")
    res = _normalize_video_resolution(resolution) or "720p"
    extend = (
        "LAST_FRAME + MOTION_VECTOR + AUDIO_CUE"
        if native
        else "LAST_FRAME + MOTION_VECTOR"
    )
    audio_momentum = "true" if native else "false"
    return (
        f'[VIDEO_PIPELINE_SPEC: model="{slug}", version="{version}", resolution="{res}", '
        f'clip_length="8-12s preferred", native_audio={native_str}, '
        f"reference_image_fidelity=high, "
        f'extend_protocol="{extend}", stitch_priority=high, audio_momentum={audio_momentum}]'
    )


def model_stack_summary(
    chat_model: str | None = None,
    video_model: str | None = None,
    image_model: str | None = None,
) -> dict[str, str]:
    """Canonical model stack for bibles, CLI output, and Web UI exports."""
    return {
        "grok_build_cli_default": DEFAULT_GROK_BUILD_MODEL,
        "grok_build_cli_fork": GROK_BUILD_FORK_MODEL,
        "grok_build_cli_min_version": RECOMMENDED_GROK_BUILD_CLI_VERSION,
        "xai_chat": resolve_chat_model(chat_model),
        "xai_build": DEFAULT_XAI_BUILD_MODEL,
        "imagine_video": resolve_video_model(video_model),
        "imagine_image": resolve_image_model(image_model),
    }


def _parse_grok_cli_version(text: str) -> str | None:
    match = re.search(r"\b(\d+\.\d+\.\d+)\b", text)
    return match.group(1) if match else None


def version_tuple(version: str) -> tuple[int, ...]:
    """Parse a dotted numeric version for ordering (e.g. ``0.2.111``)."""
    return tuple(int(p) for p in version.split("."))


# Back-compat alias (older imports / private use)
_version_tuple = version_tuple


def cli_version_at_least(installed: str, minimum: str) -> bool:
    """True when ``installed`` ≥ ``minimum`` (dotted numeric semver-ish)."""
    return version_tuple(installed) >= version_tuple(minimum)


def probe_grok_cli() -> dict[str, str | None]:
    """
    Single probe of the ``grok`` binary.

    Returns dict with keys:
      path, version (X.Y.Z or None), display (first line), raw (stdout+stderr).
    """
    path = shutil.which("grok")
    empty = {"path": path, "version": None, "display": None, "raw": None}
    if not path:
        return empty
    try:
        result = subprocess.run(
            ["grok", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return empty
    blob = ((result.stdout or "") + (result.stderr or "")).strip()
    line = blob.splitlines()[0] if blob else None
    return {
        "path": path,
        "version": _parse_grok_cli_version(blob),
        "display": line,
        "raw": blob or None,
    }


def probe_grok_cli_version() -> str | None:
    """Return installed `grok` version string, or None if unavailable."""
    version = probe_grok_cli().get("version")
    return version if isinstance(version, str) else None


def _check_registry_aliases(
    name: str,
    registry: dict[str, dict[str, Any]],
    resolve_fn,
    issues: list[str],
) -> None:
    """Ensure every registered alias uniquely resolves to its owner."""
    seen: dict[str, str] = {}
    for model_id, info in registry.items():
        keys = [model_id, *info.get("aliases", [])]
        for key in keys:
            normalized = str(key).strip().lower()
            if not normalized:
                issues.append(f"{name}: empty alias on {model_id}")
                continue
            if normalized in seen and seen[normalized] != model_id:
                issues.append(
                    f"{name}: alias {key!r} claimed by both {seen[normalized]} and {model_id}"
                )
            seen[normalized] = model_id
            got = resolve_fn(key)
            if got != model_id:
                issues.append(f"{name}: alias {key!r} resolves to {got!r}, expected {model_id!r}")


def verify_model_compatibility() -> dict[str, Any]:
    """Validate stack contract, registry integrity, and optional CLI version probe.

    Return keys include:
      issues — hard failures (compatible=False when non-empty)
      warnings — operational concerns (CLI missing/old, parse failures)
      notes — intentional stack information (not doctor --strict failures)
    """
    issues: list[str] = []
    warnings: list[str] = []
    notes: list[str] = []
    stack = model_stack_summary()

    # Stack integrity: ROLE_DEFAULTS embeds STACK_CONTRACT
    for role, expected in STACK_CONTRACT.items():
        if ROLE_DEFAULTS.get(role) != expected:
            issues.append(
                f"ROLE_DEFAULTS[{role!r}] drifted from STACK_CONTRACT "
                f"(got {ROLE_DEFAULTS.get(role)!r}, expected {expected!r})"
            )

    # Unified cinematic+build on 4.6 is intentional; note opt-in 1M path
    if DEFAULT_XAI_CHAT_MODEL == DEFAULT_XAI_BUILD_MODEL:
        notes.append(
            f"cinematic and build defaults are unified ({DEFAULT_XAI_CHAT_MODEL}); "
            "use --chat-model grok-4.3 (or long-context) for 1M-context Bibles"
        )
    notes.append(
        f"{LEGACY_QUALITY_IMAGE_MODEL} retires {LEGACY_QUALITY_RETIRED_ON}; "
        f"Imagine spend rewrites to {HERO_IMAGINE_IMAGE_MODEL} "
        f"quality={LEGACY_QUALITY_REDIRECT_QUALITY}"
    )

    # Role defaults must exist in the right registries
    if DEFAULT_XAI_CHAT_MODEL not in XAI_CHAT_MODELS:
        issues.append(f"cinematic default {DEFAULT_XAI_CHAT_MODEL!r} missing from XAI_CHAT_MODELS")
    if DEFAULT_XAI_BUILD_MODEL not in XAI_CHAT_MODELS:
        issues.append(f"build default {DEFAULT_XAI_BUILD_MODEL!r} missing from XAI_CHAT_MODELS")
    if DEFAULT_XAI_CHAT_EXPERT_MODEL not in XAI_CHAT_MODELS:
        issues.append(
            f"chat-expert specialist {DEFAULT_XAI_CHAT_EXPERT_MODEL!r} missing from XAI_CHAT_MODELS"
        )
    if DEFAULT_XAI_MULTI_MODEL not in XAI_CHAT_MODELS:
        issues.append(f"multi specialist {DEFAULT_XAI_MULTI_MODEL!r} missing from XAI_CHAT_MODELS")
    if DEFAULT_XAI_AUTO_MODEL not in XAI_CHAT_MODELS:
        issues.append(f"auto specialist {DEFAULT_XAI_AUTO_MODEL!r} missing from XAI_CHAT_MODELS")
    for v9_slug in (
        DEFAULT_XAI_CHAT_EXPERT_MODEL,
        DEFAULT_XAI_MULTI_MODEL,
        DEFAULT_XAI_AUTO_MODEL,
    ):
        if v9_slug not in GROK_BUILD_V9_MODELS:
            issues.append(f"specialist {v9_slug!r} missing from GROK_BUILD_V9_MODELS picker registry")
    if DEFAULT_GROK_BUILD_MODEL not in GROK_BUILD_CLI_MODELS:
        issues.append(f"CLI default {DEFAULT_GROK_BUILD_MODEL!r} missing from GROK_BUILD_CLI_MODELS")
    if GROK_BUILD_FORK_MODEL not in GROK_BUILD_CLI_MODELS:
        issues.append(f"CLI fork {GROK_BUILD_FORK_MODEL!r} missing from GROK_BUILD_CLI_MODELS")
    if DEFAULT_IMAGINE_VIDEO_MODEL not in IMAGINE_VIDEO_MODELS:
        issues.append(f"video default {DEFAULT_IMAGINE_VIDEO_MODEL!r} missing from IMAGINE_VIDEO_MODELS")
    if DEFAULT_IMAGINE_IMAGE_MODEL not in IMAGINE_IMAGE_MODELS:
        issues.append(f"image default {DEFAULT_IMAGINE_IMAGE_MODEL!r} missing from IMAGINE_IMAGE_MODELS")
    if HERO_IMAGINE_IMAGE_MODEL not in IMAGINE_IMAGE_MODELS:
        issues.append(f"hero image {HERO_IMAGINE_IMAGE_MODEL!r} missing from IMAGINE_IMAGE_MODELS")
    if LEGACY_QUALITY_IMAGE_MODEL not in IMAGINE_IMAGE_MODELS:
        issues.append(f"legacy quality image {LEGACY_QUALITY_IMAGE_MODEL!r} missing from IMAGINE_IMAGE_MODELS")
    quality_info = IMAGINE_IMAGE_MODELS.get(LEGACY_QUALITY_IMAGE_MODEL) or {}
    if not quality_info.get("deprecated"):
        issues.append(f"{LEGACY_QUALITY_IMAGE_MODEL} must be marked deprecated")
    if quality_info.get("retired_on") != LEGACY_QUALITY_RETIRED_ON:
        issues.append(
            f"{LEGACY_QUALITY_IMAGE_MODEL} retired_on must be {LEGACY_QUALITY_RETIRED_ON!r}"
        )
    if quality_info.get("redirect_model") != HERO_IMAGINE_IMAGE_MODEL:
        issues.append(
            f"{LEGACY_QUALITY_IMAGE_MODEL} redirect_model must be {HERO_IMAGINE_IMAGE_MODEL}"
        )
    if quality_info.get("redirect_quality") != LEGACY_QUALITY_REDIRECT_QUALITY:
        issues.append(
            f"{LEGACY_QUALITY_IMAGE_MODEL} redirect_quality must be {LEGACY_QUALITY_REDIRECT_QUALITY!r}"
        )
    hero_info = IMAGINE_IMAGE_MODELS.get(HERO_IMAGINE_IMAGE_MODEL) or {}
    hero_qvals = tuple(hero_info.get("quality_values") or ())
    if set(hero_qvals) != set(IMAGE_QUALITY_VALUES):
        issues.append(
            f"{HERO_IMAGINE_IMAGE_MODEL} quality_values must be {IMAGE_QUALITY_VALUES}"
        )
    if int(hero_info.get("max_edit_refs") or 0) != 5:
        issues.append(f"{HERO_IMAGINE_IMAGE_MODEL} max_edit_refs must be 5")
    hero_rq = hero_info.get("usd_by_resolution_quality") or {}
    if (hero_rq.get("1k") or {}).get("medium") != 0.06:
        issues.append(f"{HERO_IMAGINE_IMAGE_MODEL} 1K medium must be $0.06")
    if (hero_rq.get("2k") or {}).get("medium") != 0.08:
        issues.append(f"{HERO_IMAGINE_IMAGE_MODEL} 2K medium must be $0.08")
    if float(hero_info.get("usd_per_input_image") or 0) != 0.01:
        issues.append(f"{HERO_IMAGINE_IMAGE_MODEL} usd_per_input_image must be $0.01")
    wire, send_q, _warn = resolve_image_request(LEGACY_QUALITY_IMAGE_MODEL)
    if wire != HERO_IMAGINE_IMAGE_MODEL or send_q != LEGACY_QUALITY_REDIRECT_QUALITY:
        issues.append(
            "resolve_image_request(quality) must rewrite to grok-imagine-image-2.0 quality=low"
        )
    if resolve_image_model("2.0") != HERO_IMAGINE_IMAGE_MODEL:
        issues.append('resolve_image_model("2.0") must map to grok-imagine-image-2.0')
    if "2.0" in {a.lower() for info in IMAGINE_VIDEO_MODELS.values() for a in info.get("aliases", [])}:
        issues.append("video registry must not claim alias 2.0 (Image 2.0 only)")
    if resolve_video_model("2.0") != DEFAULT_IMAGINE_VIDEO_MODEL:
        issues.append('unknown video slug "2.0" must fall back to video default, not a 2.0 product')
    surface_ids = [s["id"] for s in IMAGINE_AGENT_SURFACES]
    if len(surface_ids) != len(set(surface_ids)):
        issues.append("IMAGINE_AGENT_SURFACES ids must be unique")
    if "xai_responses_tool" not in surface_ids:
        issues.append("IMAGINE_AGENT_SURFACES must include xai_responses_tool")

    # Native-audio only required when 1.5 is the default
    if DEFAULT_IMAGINE_VIDEO_MODEL == "grok-imagine-video-1.5":
        if not IMAGINE_VIDEO_MODELS[DEFAULT_IMAGINE_VIDEO_MODEL].get("native_audio"):
            issues.append("Default Imagine video model (1.5) must support native_audio")

    # Data-driven alias integrity (implementation matches registry)
    _check_registry_aliases("chat", XAI_CHAT_MODELS, resolve_chat_model, issues)
    _check_registry_aliases("video", IMAGINE_VIDEO_MODELS, resolve_video_model, issues)
    _check_registry_aliases("image", IMAGINE_IMAGE_MODELS, resolve_image_model, issues)

    def _resolve_nsfw_strict(key: str) -> str:
        got = resolve_nsfw_build_model(key)
        return got if got is not None else ""

    _check_registry_aliases(
        "nsfw_build", GROK_BUILD_NSFW_MODELS, _resolve_nsfw_strict, issues
    )
    for nsfw_id, info in GROK_BUILD_NSFW_MODELS.items():
        base = info.get("base_model")
        if not base:
            issues.append(f"nsfw_build: {nsfw_id!r} missing base_model")
            continue
        # Base must be a known CLI picker or chat model
        if base not in GROK_BUILD_CLI_MODELS and base not in XAI_CHAT_MODELS:
            # composer may only appear in CLI catalog
            if base not in ("grok-composer-2.5-fast",):
                issues.append(
                    f"nsfw_build: {nsfw_id!r} base_model {base!r} not in known catalogs"
                )

    def _resolve_v9_strict(key: str) -> str:
        got = resolve_v9_build_model(key)
        return got if got is not None else ""

    _check_registry_aliases("v9_build", GROK_BUILD_V9_MODELS, _resolve_v9_strict, issues)
    for v9_id, info in GROK_BUILD_V9_MODELS.items():
        base = info.get("base_model")
        if not base:
            issues.append(f"v9_build: {v9_id!r} missing base_model")
            continue
        if base not in GROK_BUILD_CLI_MODELS and base not in XAI_CHAT_MODELS:
            if base not in ("grok-composer-2.5-fast",):
                issues.append(
                    f"v9_build: {v9_id!r} base_model {base!r} not in known catalogs"
                )
        # Canonical chat registry must resolve the same slug
        if resolve_chat_model(v9_id) != v9_id:
            issues.append(
                f"v9_build: resolve_chat_model({v9_id!r}) → {resolve_chat_model(v9_id)!r}"
            )

    # Role routing sanity
    if recommended_model_for_role("Imagine Prompt Master") != DEFAULT_XAI_CHAT_EXPERT_MODEL:
        issues.append("recommended_model_for_role(Imagine Prompt Master) must be chat-expert")
    if recommended_model_for_role("Team Leader") != DEFAULT_XAI_MULTI_MODEL:
        issues.append("recommended_model_for_role(Team Leader) must be multi")
    if recommended_model_for_role("Animatic Director") != DEFAULT_XAI_AUTO_MODEL:
        issues.append("recommended_model_for_role(Animatic Director) must be auto")

    # Empty resolve → cinematic / video / image defaults
    if resolve_chat_model(None) != DEFAULT_XAI_CHAT_MODEL:
        issues.append("resolve_chat_model(None) must return cinematic default")
    if resolve_chat_model("") != DEFAULT_XAI_CHAT_MODEL:
        issues.append('resolve_chat_model("") must return cinematic default')

    spec = build_video_pipeline_spec()
    if DEFAULT_IMAGINE_VIDEO_MODEL not in spec:
        issues.append(f"VIDEO_PIPELINE_SPEC must reference {DEFAULT_IMAGINE_VIDEO_MODEL} by default")

    # Soft probe: recommended CLI version (never hard-fails missing binary)
    probe = probe_grok_cli()
    installed = probe.get("version")
    if probe.get("path") is None:
        warnings.append(
            f"Grok Build CLI not found on PATH; recommend ≥ {RECOMMENDED_GROK_BUILD_CLI_VERSION}"
        )
    elif installed is None:
        warnings.append(
            f"Could not parse Grok Build CLI version from {probe.get('raw')!r}; "
            f"recommend ≥ {RECOMMENDED_GROK_BUILD_CLI_VERSION}"
        )
    else:
        try:
            if not cli_version_at_least(str(installed), RECOMMENDED_GROK_BUILD_CLI_VERSION):
                warnings.append(
                    f"Grok Build CLI {installed} < recommended {RECOMMENDED_GROK_BUILD_CLI_VERSION}"
                )
        except ValueError:
            warnings.append(f"Could not parse Grok Build CLI version from {installed!r}")

    return {
        "compatible": len(issues) == 0,
        "studio_version": STUDIO_COMPATIBILITY_VERSION,
        "model_stack": stack,
        "video_pipeline_spec": spec,
        "required_roles": dict(REQUIRED_MODEL_ROLES),
        "required_slugs": list(REQUIRED_MODEL_SLUGS),
        "min_grok_build_cli_version": RECOMMENDED_GROK_BUILD_CLI_VERSION,
        "installed_grok_cli_version": installed,
        "warnings": warnings,
        "notes": notes,
        "issues": issues,
    }


def imagine_video_pricing_table() -> dict[str, dict[str, Any]]:
    """USD/sec rates keyed by canonical video slug (for quota optimizer sync)."""
    table: dict[str, dict[str, Any]] = {}
    for slug, info in IMAGINE_VIDEO_MODELS.items():
        row: dict[str, Any] = {"usd_per_second": info["usd_per_second"]}
        by_res = info.get("usd_per_second_by_resolution")
        if by_res:
            row["usd_per_second_by_resolution"] = dict(by_res)
        table[slug] = row
    return table


def list_video_model_aliases() -> dict[str, list[str]]:
    """Canonical slug → all accepted aliases (studio + xAI API)."""
    return {slug: list(info.get("aliases", [])) for slug, info in IMAGINE_VIDEO_MODELS.items()}


def imagine_image_pricing_table() -> dict[str, dict[str, Any]]:
    """USD/image rates keyed by canonical image slug (for quota optimizer sync)."""
    table: dict[str, dict[str, Any]] = {}
    for slug, info in IMAGINE_IMAGE_MODELS.items():
        row: dict[str, Any] = {"usd_per_image": info["usd_per_image"]}
        if info.get("usd_per_input_image") is not None:
            row["usd_per_input_image"] = info["usd_per_input_image"]
        by_rq = info.get("usd_by_resolution_quality")
        if by_rq:
            row["usd_by_resolution_quality"] = {
                res: dict(qs) for res, qs in by_rq.items()
            }
        table[slug] = row
    return table


def ordered_video_model_slugs() -> list[str]:
    keys = list(IMAGINE_VIDEO_MODELS.keys())
    if DEFAULT_IMAGINE_VIDEO_MODEL in keys:
        return [DEFAULT_IMAGINE_VIDEO_MODEL] + [k for k in keys if k != DEFAULT_IMAGINE_VIDEO_MODEL]
    return keys


def live_image_model(slug: str | None = None) -> str:
    """Session/picker slug: deprecated quality → Image 2.0; empty/unknown → draft default."""
    if not slug or not str(slug).strip():
        return DEFAULT_IMAGINE_IMAGE_MODEL
    resolved = resolve_image_model(slug)
    info = IMAGINE_IMAGE_MODELS.get(resolved) or {}
    if info.get("deprecated"):
        return str(info.get("redirect_model") or HERO_IMAGINE_IMAGE_MODEL)
    return resolved


def ordered_image_model_slugs(*, include_deprecated: bool = False) -> list[str]:
    """Draft 1.0 first, then 2.0 hero. Deprecated quality slug is picker-hidden."""
    keys = [
        k
        for k, info in IMAGINE_IMAGE_MODELS.items()
        if include_deprecated or not info.get("deprecated")
    ]
    preferred = [
        slug
        for slug in (DEFAULT_IMAGINE_IMAGE_MODEL, HERO_IMAGINE_IMAGE_MODEL)
        if slug in keys
    ]
    if include_deprecated and LEGACY_QUALITY_IMAGE_MODEL in keys:
        preferred.append(LEGACY_QUALITY_IMAGE_MODEL)
    return preferred + [k for k in keys if k not in preferred]


def imagine_surface_catalog() -> dict[str, Any]:
    """Models × REST endpoints × Agent Mode surfaces for CLI / meta / doctor."""
    return {
        "schema_version": SCHEMA_VERSION,
        "studio_version": STUDIO_COMPATIBILITY_VERSION,
        "note": (
            "There is no grok-imagine-video-2.0; 2.0 is Imagine Image only. "
            f"{LEGACY_QUALITY_IMAGE_MODEL} retires {LEGACY_QUALITY_RETIRED_ON} → "
            f"{HERO_IMAGINE_IMAGE_MODEL} quality={LEGACY_QUALITY_REDIRECT_QUALITY}."
        ),
        "routing": {
            "image_default": DEFAULT_IMAGINE_IMAGE_MODEL,
            "image_hero": HERO_IMAGINE_IMAGE_MODEL,
            "image_legacy_quality": LEGACY_QUALITY_IMAGE_MODEL,
            "image_legacy_quality_retired_on": LEGACY_QUALITY_RETIRED_ON,
            "image_legacy_quality_redirect": HERO_IMAGINE_IMAGE_MODEL,
            "image_legacy_quality_redirect_quality": LEGACY_QUALITY_REDIRECT_QUALITY,
            "video_default": DEFAULT_IMAGINE_VIDEO_MODEL,
            "video_native_audio": NATIVE_AUDIO_VIDEO_MODEL,
            "video_edit_extend": EDIT_EXTEND_VIDEO_MODEL,
        },
        "images": [
            {
                "slug": slug,
                "label": info.get("label"),
                "version": info.get("version"),
                "usd_per_image": info.get("usd_per_image"),
                "hero": bool(info.get("hero")),
                "quality_param": bool(info.get("quality_param")),
                "deprecated": bool(info.get("deprecated")),
                "retired_on": info.get("retired_on"),
                "max_edit_refs": int(info.get("max_edit_refs") or 3),
                "aliases": list(info.get("aliases") or []),
            }
            for slug, info in IMAGINE_IMAGE_MODELS.items()
        ],
        "videos": [
            {
                "slug": slug,
                "label": info.get("label"),
                "version": info.get("version"),
                "usd_per_second": info.get("usd_per_second"),
                "usd_per_second_by_resolution": dict(info.get("usd_per_second_by_resolution") or {}),
                "native_audio": bool(info.get("native_audio")),
                "modes": list(info.get("modes") or []),
                "max_resolution": info.get("max_resolution"),
                "aliases": list(info.get("aliases") or []),
            }
            for slug, info in IMAGINE_VIDEO_MODELS.items()
        ],
        "rest_endpoints": [dict(row) for row in IMAGINE_REST_ENDPOINTS],
        "agent_mode_surfaces": [dict(row) for row in IMAGINE_AGENT_SURFACES],
    }


def list_image_model_aliases() -> dict[str, list[str]]:
    """Canonical slug → all accepted aliases (studio + xAI API)."""
    return {slug: list(info.get("aliases", [])) for slug, info in IMAGINE_IMAGE_MODELS.items()}


def list_nsfw_build_models() -> dict[str, dict[str, Any]]:
    """Return Grok Build NSFW custom-model registry (opt-in picker aliases)."""
    return dict(GROK_BUILD_NSFW_MODELS)


def list_v9_build_models() -> dict[str, dict[str, Any]]:
    """Return Grok Build v9-4p5 / Auto specialist picker registry."""
    return dict(GROK_BUILD_V9_MODELS)


def list_all_models() -> dict[str, Any]:
    """Return full registry for CLI/UI display."""
    return {
        "schema_version": SCHEMA_VERSION,
        "role_defaults": dict(ROLE_DEFAULTS),
        "stack_contract": dict(STACK_CONTRACT),
        "grok_build_cli": {
            "default": DEFAULT_GROK_BUILD_MODEL,
            "fork_secondary": GROK_BUILD_FORK_MODEL,
            "recommended_version": RECOMMENDED_GROK_BUILD_CLI_VERSION,
            "models": GROK_BUILD_CLI_MODELS,
        },
        "grok_build_v9": {
            "opt_in": True,
            "install": "bash scripts/install_v9_grok_models.sh",
            "config_example": "config/grok-build-v9-models.example.toml",
            "note": (
                "Picker aliases for Model Layer v4.5 (chat-expert / multi / auto). "
                "Wrap grok-4.6 when native product IDs are unavailable on the team/API. "
                "Not Imagine generators. Prefer cli-chat-proxy session auth."
            ),
            "chat_expert": DEFAULT_XAI_CHAT_EXPERT_MODEL,
            "multi": DEFAULT_XAI_MULTI_MODEL,
            "auto": DEFAULT_XAI_AUTO_MODEL,
            "models": GROK_BUILD_V9_MODELS,
        },
        "grok_build_nsfw": {
            "opt_in": True,
            "install": "bash scripts/install_nsfw_grok_models.sh",
            "config_example": "config/grok-build-nsfw-models.example.toml",
            "note": (
                "Picker aliases for ErosForge orchestration; not Imagine generators. "
                "Require install into ~/.grok/config.toml. Prefer cli-chat-proxy session auth."
            ),
            "models": GROK_BUILD_NSFW_MODELS,
        },
        "xai_chat": {
            "default": DEFAULT_XAI_CHAT_MODEL,
            "build_default": DEFAULT_XAI_BUILD_MODEL,
            "chat_expert": DEFAULT_XAI_CHAT_EXPERT_MODEL,
            "multi": DEFAULT_XAI_MULTI_MODEL,
            "auto": DEFAULT_XAI_AUTO_MODEL,
            "models": XAI_CHAT_MODELS,
        },
        "imagine_video": {
            "default": DEFAULT_IMAGINE_VIDEO_MODEL,
            "native_audio": NATIVE_AUDIO_VIDEO_MODEL,
            "edit_extend": EDIT_EXTEND_VIDEO_MODEL,
            "models": IMAGINE_VIDEO_MODELS,
        },
        "imagine_image": {
            "default": DEFAULT_IMAGINE_IMAGE_MODEL,
            "hero": HERO_IMAGINE_IMAGE_MODEL,
            "legacy_quality": LEGACY_QUALITY_IMAGE_MODEL,
            "models": IMAGINE_IMAGE_MODELS,
        },
        "imagine_surfaces": imagine_surface_catalog(),
        "studio_compatibility_version": STUDIO_COMPATIBILITY_VERSION,
        "model_stack": model_stack_summary(),
        "video_pipeline_spec": build_video_pipeline_spec(),
        "usd_per_credit": USD_PER_CREDIT,
    }
