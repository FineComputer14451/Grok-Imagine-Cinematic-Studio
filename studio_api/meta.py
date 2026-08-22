"""Read-only meta endpoints for custom UIs (Settings / Tools parity).

No free-form execute — listing agents, Role Cards, and env presence only.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent.parent
_SAFE_STEM = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$")
_PREVIEW_CHARS = 12_000


def env_status() -> dict[str, Any]:
    """Non-secret environment signals for Settings UI."""
    key = (os.environ.get("XAI_API_KEY") or "").strip()
    return {
        "xai_api_key_set": bool(key),
        "xai_api_key_source": "env" if key else None,
        "note": (
            "Key material is never returned. Set XAI_API_KEY on the API process "
            "for live Imagine; SPA cannot inject secrets into the server."
        ),
    }


def agents_roster() -> dict[str, Any]:
    from cli.shared import AGENTS, core_agent_count, total_agent_count

    return {
        "core_count": core_agent_count(),
        "total_count": total_agent_count(),
        "groups": {k: list(v) for k, v in AGENTS.items()},
    }


def list_role_cards() -> dict[str, Any]:
    from cli.shared import list_role_card_files

    items = []
    for path in list_role_card_files():
        try:
            relpath = str(path.relative_to(_ROOT))
        except ValueError:
            relpath = path.name
        items.append(
            {
                "stem": path.stem,
                "filename": path.name,
                "relpath": relpath,
            }
        )
    return {"count": len(items), "role_cards": items}


def role_card_preview(stem: str) -> dict[str, Any]:
    """Return a text preview of one Role Card (path-safe)."""
    if not _SAFE_STEM.match(stem or ""):
        raise ValueError("Invalid role card name")
    # Disallow traversal fragments even if regex passes
    if ".." in stem or "/" in stem or "\\" in stem:
        raise ValueError("Invalid role card name")

    from cli.shared import AGENTS_DIR, list_role_card_files

    agents_dir = AGENTS_DIR.resolve()
    path = (agents_dir / f"{stem}.md").resolve()
    if not str(path).startswith(str(agents_dir)) or not path.is_file():
        # Allow exact match from listed cards only
        allowed = {p.stem: p for p in list_role_card_files()}
        path = allowed.get(stem)
        if path is None:
            raise FileNotFoundError(stem)
        path = path.resolve()
        if not str(path).startswith(str(agents_dir)):
            raise FileNotFoundError(stem)

    text = path.read_text(encoding="utf-8", errors="replace")
    truncated = len(text) > _PREVIEW_CHARS
    if truncated:
        text = text[:_PREVIEW_CHARS] + "\n\n…(truncated)"
    return {
        "stem": path.stem,
        "filename": path.name,
        "truncated": truncated,
        "content": text,
    }


def production_options() -> dict[str, Any]:
    """Static option lists mirroring Streamlit session PRODUCTION_OPTIONS."""
    try:
        from models import (
            DEFAULT_IMAGINE_IMAGE_MODEL,
            DEFAULT_IMAGINE_VIDEO_MODEL,
            HERO_IMAGINE_IMAGE_MODEL,
            ordered_image_model_slugs,
            ordered_video_model_slugs,
        )
        from handoff_schema import EXECUTION_MODES, TARGET_SURFACES

        video_models = ordered_video_model_slugs()
        image_models = ordered_image_model_slugs()
        surfaces = sorted(TARGET_SURFACES)
        exec_modes = sorted(EXECUTION_MODES)
        video_default = DEFAULT_IMAGINE_VIDEO_MODEL
        image_default = DEFAULT_IMAGINE_IMAGE_MODEL
        image_hero = HERO_IMAGINE_IMAGE_MODEL
    except ImportError:
        video_models = ["grok-imagine-video", "grok-imagine-video-1.5"]
        image_models = [
            "grok-imagine-image",
            "grok-imagine-image-2.0",
            "grok-imagine-image-quality",
        ]
        surfaces = [
            "grok_build_tools",
            "grok_agent_acp",
            "grok_com_imagine",
            "xai_api",
            "xai_responses_tool",
        ]
        exec_modes = [
            "image_prompt",
            "image_edit",
            "image_to_video",
            "video_prompt",
            "reference_to_video",
            "video_edit",
            "video_extend",
        ]
        video_default = "grok-imagine-video"
        image_default = "grok-imagine-image"
        image_hero = "grok-imagine-image-2.0"

    return {
        "genres": [
            "Sci-Fi",
            "Psychological Horror",
            "Action",
            "Drama",
            "Cyberpunk",
            "Intimate Drama",
            "Thriller",
            "Neo-Noir",
            "Fantasy",
            "Documentary Style",
        ],
        "directors": [
            "Denis Villeneuve",
            "Christopher Nolan",
            "David Fincher",
            "Roger Deakins",
            "Zack Snyder",
            "Default",
        ],
        "complexities": ["Low", "Medium", "High", "Extreme"],
        "tiers": ["supergrok_pro", "supergrok_heavy", "custom"],
        "reasoning_levels": ["low", "medium", "high"],
        "chat_models": ["grok-4.5", "grok-4.3", "grok-v9-4p5-multi", "grok-v9-4p5-chat-expert", "grok-4-auto"],
        "video_models": video_models,
        "image_models": image_models,
        "imagine_surfaces": surfaces,
        "imagine_execution_modes": exec_modes,
        "imagine_regions": ["us-east-1", "eu-west-1", "ap-southeast-1"],
        "defaults": {
            "genre": "Sci-Fi",
            "director": "Denis Villeneuve",
            "video_model": video_default,
            "image_model": image_default,
            "image_hero_model": image_hero,
            "chat_model": "grok-4.5",
            "duration": 60,
            "complexity": "Medium",
            "fast_mode": False,
            "quota_tier": "supergrok_pro",
            "imagine_region": "us-east-1",
            "nsfw_opt_in": False,
            "reasoning_level": "high",
            "prompt_cache_key": "",
            "dashboard_view_mode": "ops",
        },
    }
