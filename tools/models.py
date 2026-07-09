#!/usr/bin/env python3
"""
Canonical Grok Build / xAI model registry for Grok Imagine Cinematic Studio.

Single source of truth for CLI, Web UI, quota optimizer, and documentation.

Dual stack (v3.6.6+):
  - Cinematic orchestration (long Bibles, 1M context): grok-4.3
  - Grok Build / coding / agentic: grok-4.5
  - Recommended CLI binary: Grok Build ≥ 0.2.93 (not an API slug)
"""

from __future__ import annotations

import re
import shutil
import subprocess
from typing import Any

SCHEMA_VERSION = "1.2"

# ---------------------------------------------------------------------------
# Dual-stack product pins + full role defaults (literals appear once)
# ---------------------------------------------------------------------------

# Change only with a deliberate studio upgrade (also asserted in tests)
STACK_CONTRACT: dict[str, str] = {
    "cinematic": "grok-4.3",
    "build": "grok-4.5",
    "cli": "grok-4.5",
}

# Single source of truth for “which model for which job”
ROLE_DEFAULTS: dict[str, str] = {
    **STACK_CONTRACT,
    "cli_fork": "grok-build",
    "imagine_video": "grok-imagine-video",
    "imagine_image": "grok-imagine-image",
}

# Recommended Grok Build binary version (not an API model slug)
RECOMMENDED_GROK_BUILD_CLI_VERSION = "0.2.93"
# Back-compat alias used by stack summary / older imports
MIN_GROK_BUILD_CLI_VERSION = RECOMMENDED_GROK_BUILD_CLI_VERSION

DEFAULT_XAI_CHAT_MODEL = ROLE_DEFAULTS["cinematic"]
DEFAULT_XAI_BUILD_MODEL = ROLE_DEFAULTS["build"]
DEFAULT_GROK_BUILD_MODEL = ROLE_DEFAULTS["cli"]
GROK_BUILD_FORK_MODEL = ROLE_DEFAULTS["cli_fork"]
DEFAULT_IMAGINE_VIDEO_MODEL = ROLE_DEFAULTS["imagine_video"]
DEFAULT_IMAGINE_IMAGE_MODEL = ROLE_DEFAULTS["imagine_image"]

# ---------------------------------------------------------------------------
# Grok Build CLI picker (local agent environment — `grok models`)
# ---------------------------------------------------------------------------

GROK_BUILD_CLI_MODELS: dict[str, dict[str, Any]] = {
    "grok-4.5": {
        "label": "Grok 4.5",
        "role": "default",
        "description": "Default Grok Build agent — coding, agentic tasks, knowledge work",
    },
    "grok-composer-2.5-fast": {
        "label": "Grok Composer 2.5 Fast",
        "role": "creative",
        "description": "Fast creative orchestration and multi-agent cinematic direction",
    },
    "grok-build": {
        "label": "Grok Build",
        "role": "coding",
        "description": "Fork secondary / coding alias (Grok 4.5 stack)",
    },
    "grok-4.3": {
        "label": "Grok 4.3",
        "role": "cinematic",
        "description": "1M-context cinematic orchestration inside Grok Build sessions",
    },
}

# ---------------------------------------------------------------------------
# xAI API chat models (https://api.x.ai/v1)
# Defaults are ROLE_DEFAULTS only — no per-entry default/build_default flags.
# ---------------------------------------------------------------------------

XAI_CHAT_MODELS: dict[str, dict[str, Any]] = {
    "grok-4.3": {
        "label": "Grok 4.3",
        "context_tokens": 1_000_000,
        "input_usd_per_1m": 1.25,
        "output_usd_per_1m": 2.50,
        "use_case": "cinematic orchestration, 1M context, Production Bibles, multi-agent productions",
        "role": "cinematic",
        "aliases": ["4.3", "cinematic", "grok-4"],
    },
    "grok-4.5": {
        "label": "Grok 4.5",
        "context_tokens": 500_000,
        "input_usd_per_1m": 2.00,
        "cached_input_usd_per_1m": 0.50,
        "output_usd_per_1m": 6.00,
        "use_case": "coding, agentic workflows, Grok Build default, structured tool use",
        "role": "build",
        "reasoning": "low|medium|high (default high)",
        "aliases": [
            "4.5",
            "grok-4.5-latest",
            "grok-build-latest",
            "coding",
            "grok-build",
            "build",
        ],
    },
    "grok-build-0.1": {
        "label": "Grok Build 0.1",
        "context_tokens": 256_000,
        "input_usd_per_1m": 1.00,
        "output_usd_per_1m": 2.00,
        "use_case": "legacy coding API — prefer grok-4.5",
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
        "usd_per_second": 0.080,
        "native_audio": True,
        "modalities": "image → video",
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
        "usd_per_second": 0.050,
        "native_audio": False,
        "modalities": "text, image, video → video",
        "regions": ["us-east-1", "eu-west-1", "us-west-2"],
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

STUDIO_COMPATIBILITY_VERSION = "3.6.6"

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


def resolve_chat_model(slug: str | None = None) -> str:
    """Resolve chat model slug; empty/None → cinematic default (grok-4.3)."""
    return _resolve_from_alias_map(slug, _CHAT_ALIAS_MAP, DEFAULT_XAI_CHAT_MODEL)


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
        "grok_build_cli_min_version": RECOMMENDED_GROK_BUILD_CLI_VERSION,
        "xai_chat": resolve_chat_model(chat_model),
        "xai_build": DEFAULT_XAI_BUILD_MODEL,
        "imagine_video": resolve_video_model(video_model),
        "imagine_image": resolve_image_model(image_model),
    }


def _parse_grok_cli_version(text: str) -> str | None:
    match = re.search(r"\b(\d+\.\d+\.\d+)\b", text)
    return match.group(1) if match else None


def _version_tuple(version: str) -> tuple[int, ...]:
    return tuple(int(p) for p in version.split("."))


def probe_grok_cli_version() -> str | None:
    """Return installed `grok` version string, or None if unavailable."""
    if not shutil.which("grok"):
        return None
    try:
        result = subprocess.run(
            ["grok", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    blob = (result.stdout or "") + (result.stderr or "")
    return _parse_grok_cli_version(blob)


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
    """Validate dual-stack contract, registry integrity, and optional CLI version probe."""
    issues: list[str] = []
    warnings: list[str] = []
    stack = model_stack_summary()

    # Dual-stack integrity: ROLE_DEFAULTS embeds STACK_CONTRACT; cinematic ≠ build
    for role, expected in STACK_CONTRACT.items():
        if ROLE_DEFAULTS.get(role) != expected:
            issues.append(
                f"ROLE_DEFAULTS[{role!r}] drifted from STACK_CONTRACT "
                f"(got {ROLE_DEFAULTS.get(role)!r}, expected {expected!r})"
            )

    if DEFAULT_XAI_CHAT_MODEL == DEFAULT_XAI_BUILD_MODEL:
        issues.append("cinematic and build defaults must differ (dual stack)")

    # Role defaults must exist in the right registries
    if DEFAULT_XAI_CHAT_MODEL not in XAI_CHAT_MODELS:
        issues.append(f"cinematic default {DEFAULT_XAI_CHAT_MODEL!r} missing from XAI_CHAT_MODELS")
    if DEFAULT_XAI_BUILD_MODEL not in XAI_CHAT_MODELS:
        issues.append(f"build default {DEFAULT_XAI_BUILD_MODEL!r} missing from XAI_CHAT_MODELS")
    if DEFAULT_GROK_BUILD_MODEL not in GROK_BUILD_CLI_MODELS:
        issues.append(f"CLI default {DEFAULT_GROK_BUILD_MODEL!r} missing from GROK_BUILD_CLI_MODELS")
    if GROK_BUILD_FORK_MODEL not in GROK_BUILD_CLI_MODELS:
        issues.append(f"CLI fork {GROK_BUILD_FORK_MODEL!r} missing from GROK_BUILD_CLI_MODELS")
    if DEFAULT_IMAGINE_VIDEO_MODEL not in IMAGINE_VIDEO_MODELS:
        issues.append(f"video default {DEFAULT_IMAGINE_VIDEO_MODEL!r} missing from IMAGINE_VIDEO_MODELS")
    if DEFAULT_IMAGINE_IMAGE_MODEL not in IMAGINE_IMAGE_MODELS:
        issues.append(f"image default {DEFAULT_IMAGINE_IMAGE_MODEL!r} missing from IMAGINE_IMAGE_MODELS")

    # Native-audio only required when 1.5 is the default
    if DEFAULT_IMAGINE_VIDEO_MODEL == "grok-imagine-video-1.5":
        if not IMAGINE_VIDEO_MODELS[DEFAULT_IMAGINE_VIDEO_MODEL].get("native_audio"):
            issues.append("Default Imagine video model (1.5) must support native_audio")

    # Data-driven alias integrity (implementation matches registry)
    _check_registry_aliases("chat", XAI_CHAT_MODELS, resolve_chat_model, issues)
    _check_registry_aliases("video", IMAGINE_VIDEO_MODELS, resolve_video_model, issues)
    _check_registry_aliases("image", IMAGINE_IMAGE_MODELS, resolve_image_model, issues)

    # Empty resolve → cinematic / video / image defaults
    if resolve_chat_model(None) != DEFAULT_XAI_CHAT_MODEL:
        issues.append("resolve_chat_model(None) must return cinematic default")
    if resolve_chat_model("") != DEFAULT_XAI_CHAT_MODEL:
        issues.append('resolve_chat_model("") must return cinematic default')

    spec = build_video_pipeline_spec()
    if DEFAULT_IMAGINE_VIDEO_MODEL not in spec:
        issues.append(f"VIDEO_PIPELINE_SPEC must reference {DEFAULT_IMAGINE_VIDEO_MODEL} by default")

    # Soft probe: recommended CLI version (never hard-fails missing binary)
    installed = probe_grok_cli_version()
    if installed is None:
        warnings.append(
            f"Grok Build CLI not found on PATH; recommend ≥ {RECOMMENDED_GROK_BUILD_CLI_VERSION}"
        )
    else:
        try:
            if _version_tuple(installed) < _version_tuple(RECOMMENDED_GROK_BUILD_CLI_VERSION):
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
        "role_defaults": dict(ROLE_DEFAULTS),
        "stack_contract": dict(STACK_CONTRACT),
        "grok_build_cli": {
            "default": DEFAULT_GROK_BUILD_MODEL,
            "fork_secondary": GROK_BUILD_FORK_MODEL,
            "recommended_version": RECOMMENDED_GROK_BUILD_CLI_VERSION,
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
