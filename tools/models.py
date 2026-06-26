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
        "modalities": "image → video",
        "version_date": "2026-05-30",
        "regions": ["us-east-1", "eu-west-1", "us-west-2"],
        "default": True,
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
        "usd_per_second": 0.050,
        "native_audio": False,
        "modalities": "text, image, video → video",
        "regions": ["us-east-1", "eu-west-1", "us-west-2"],
        "default": False,
        "aliases": ["imagine-video", "video-1.0", "1.0"],
    },
}

IMAGINE_IMAGE_MODELS: dict[str, dict[str, Any]] = {
    "grok-imagine-image": {
        "label": "Imagine Image",
        "usd_per_image": 0.02,
        "modalities": "text, image → image",
        "version_date": "2026-03-02",
        "regions": ["us-east-1", "eu-west-1", "us-west-2"],
        "default": True,
        "aliases": [
            "grok-imagine-image-2026-03-02",
            "imagine-image",
            "image",
        ],
    },
    "grok-imagine-image-quality": {
        "label": "Imagine Image Quality",
        "usd_per_image": 0.05,
        "modalities": "text, image → image",
        "version_date": "2026-04-03",
        "regions": ["us-east-1", "eu-west-1", "us-west-2"],
        "default": False,
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
}

DEFAULT_IMAGINE_VIDEO_MODEL = "grok-imagine-video-1.5"
DEFAULT_IMAGINE_IMAGE_MODEL = "grok-imagine-image"

# Studio compatibility target (Grok 4.3 + Imagine 1.5 + Grok Build)
STUDIO_COMPATIBILITY_VERSION = "3.6.5"
REQUIRED_MODEL_SLUGS = (
    DEFAULT_GROK_BUILD_MODEL,
    GROK_BUILD_FORK_MODEL,
    DEFAULT_XAI_CHAT_MODEL,
    DEFAULT_XAI_BUILD_MODEL,
    DEFAULT_IMAGINE_VIDEO_MODEL,
    DEFAULT_IMAGINE_IMAGE_MODEL,
)

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


def build_video_pipeline_spec(model: str | None = None) -> str:
    """Return locked VIDEO_PIPELINE_SPEC string for Production Bibles and prompts."""
    slug = resolve_video_model(model)
    native = IMAGINE_VIDEO_MODELS[slug].get("native_audio", False)
    native_str = "true" if native else "false"
    return (
        f'[VIDEO_PIPELINE_SPEC: model="{slug}", resolution="720p", '
        f'clip_length="8-12s preferred", native_audio={native_str}, '
        f"reference_image_fidelity=high, "
        f'extend_protocol="LAST_FRAME + MOTION_VECTOR + AUDIO_CUE", stitch_priority=high]'
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
        "xai_chat": resolve_chat_model(chat_model),
        "xai_build": DEFAULT_XAI_BUILD_MODEL,
        "imagine_video": resolve_video_model(video_model),
        "imagine_image": resolve_image_model(image_model),
    }


def verify_model_compatibility() -> dict[str, Any]:
    """Validate canonical model registry for Grok 4.3 + Imagine 1.5 + Grok Build."""
    issues: list[str] = []
    stack = model_stack_summary()

    if DEFAULT_XAI_CHAT_MODEL != "grok-4.3":
        issues.append(f"DEFAULT_XAI_CHAT_MODEL must be grok-4.3 (got {DEFAULT_XAI_CHAT_MODEL})")
    if DEFAULT_IMAGINE_VIDEO_MODEL != "grok-imagine-video-1.5":
        issues.append(
            f"DEFAULT_IMAGINE_VIDEO_MODEL must be grok-imagine-video-1.5 "
            f"(got {DEFAULT_IMAGINE_VIDEO_MODEL})"
        )
    if not IMAGINE_VIDEO_MODELS[DEFAULT_IMAGINE_VIDEO_MODEL].get("native_audio"):
        issues.append("Default Imagine video model must support native_audio")
    if resolve_chat_model("grok-4") != "grok-4.3":
        issues.append("Alias grok-4 must resolve to grok-4.3")
    if resolve_chat_model("grok-build") != "grok-build-0.1":
        issues.append("Alias grok-build must resolve to grok-build-0.1")
    if resolve_video_model("1.5") != "grok-imagine-video-1.5":
        issues.append("Alias 1.5 must resolve to grok-imagine-video-1.5")
    if resolve_video_model("grok-imagine-video-1.5-preview") != "grok-imagine-video-1.5":
        issues.append("Alias grok-imagine-video-1.5-preview must resolve to grok-imagine-video-1.5")
    if resolve_video_model("grok-imagine-video-1.5-2026-05-30") != "grok-imagine-video-1.5":
        issues.append("Alias grok-imagine-video-1.5-2026-05-30 must resolve to grok-imagine-video-1.5")
    if resolve_image_model("grok-imagine-image-2026-03-02") != "grok-imagine-image":
        issues.append("Alias grok-imagine-image-2026-03-02 must resolve to grok-imagine-image")
    if resolve_image_model("grok-imagine-image-pro") != "grok-imagine-image-quality":
        issues.append("Alias grok-imagine-image-pro must resolve to grok-imagine-image-quality")
    if resolve_image_model("grok-imagine-image-quality-latest") != "grok-imagine-image-quality":
        issues.append("Alias grok-imagine-image-quality-latest must resolve to grok-imagine-image-quality")

    spec = build_video_pipeline_spec()
    if "grok-imagine-video-1.5" not in spec:
        issues.append("VIDEO_PIPELINE_SPEC must reference grok-imagine-video-1.5 by default")

    return {
        "compatible": len(issues) == 0,
        "studio_version": STUDIO_COMPATIBILITY_VERSION,
        "model_stack": stack,
        "video_pipeline_spec": spec,
        "required_slugs": list(REQUIRED_MODEL_SLUGS),
        "issues": issues,
    }


def imagine_video_pricing_table() -> dict[str, dict[str, float]]:
    """USD/sec rates keyed by canonical video slug (for quota optimizer sync)."""
    return {
        slug: {"usd_per_second": info["usd_per_second"]}
        for slug, info in IMAGINE_VIDEO_MODELS.items()
    }


def list_video_model_aliases() -> dict[str, list[str]]:
    """Canonical slug → all accepted aliases (studio + xAI API)."""
    return {slug: list(info.get("aliases", [])) for slug, info in IMAGINE_VIDEO_MODELS.items()}


def imagine_image_pricing_table() -> dict[str, dict[str, float]]:
    """USD/image rates keyed by canonical image slug (for quota optimizer sync)."""
    return {
        slug: {"usd_per_image": info["usd_per_image"]}
        for slug, info in IMAGINE_IMAGE_MODELS.items()
    }


def list_image_model_aliases() -> dict[str, list[str]]:
    """Canonical slug → all accepted aliases (studio + xAI API)."""
    return {slug: list(info.get("aliases", [])) for slug, info in IMAGINE_IMAGE_MODELS.items()}


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
        "studio_compatibility_version": STUDIO_COMPATIBILITY_VERSION,
        "model_stack": model_stack_summary(),
        "video_pipeline_spec": build_video_pipeline_spec(),
        "usd_per_credit": USD_PER_CREDIT,
    }