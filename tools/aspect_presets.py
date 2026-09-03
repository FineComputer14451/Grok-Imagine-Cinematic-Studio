#!/usr/bin/env python3
"""
Aspect ratio and orientation presets for shots, clips, and delivery planning.
"""

from __future__ import annotations

from typing import Any

ASPECT_PRESETS: dict[str, dict[str, Any]] = {
    "16:9": {
        "label": "Cinematic Widescreen",
        "orientation": "landscape",
        "social_crop": "16:9",
        "default_for": ("hero", "story_beat", "coverage"),
        "handoff": {"trailer": "primary", "key_art": "secondary"},
    },
    "9:16": {
        "label": "Vertical Social",
        "orientation": "portrait",
        "social_crop": "9:16",
        "default_for": ("filler",),
        "handoff": {"trailer": "teaser_vertical", "key_art": "mobile_poster"},
    },
    "1:1": {
        "label": "Square Social",
        "orientation": "square",
        "social_crop": "1:1",
        "default_for": (),
        "handoff": {"trailer": "square_hook", "key_art": "instagram_poster"},
    },
    "21:9": {
        "label": "Cinematic Ultra-Wide",
        "orientation": "landscape",
        "social_crop": "21:9",
        "default_for": (),
        "handoff": {"trailer": "ultra_wide", "key_art": "cinematic_banner"},
    },
    "5:2": {
        "label": "Wide Banner",
        "orientation": "landscape",
        "social_crop": "5:2",
        "default_for": (),
        "handoff": {"trailer": "banner", "key_art": "wide_banner"},
    },
}

DEFAULT_ASPECT = "16:9"
ASPECT_OPTIONS = tuple(ASPECT_PRESETS.keys())


def normalize_aspect(value: str | None) -> str:
    if not value:
        return DEFAULT_ASPECT
    cleaned = value.strip().replace("x", ":")
    return cleaned if cleaned in ASPECT_PRESETS else DEFAULT_ASPECT


def default_aspect_for_tier(tier: str) -> str:
    for aspect, meta in ASPECT_PRESETS.items():
        if tier in meta.get("default_for", ()):
            return aspect
    return DEFAULT_ASPECT


def apply_aspect_to_shot(shot: dict[str, Any], aspect: str | None = None) -> dict[str, Any]:
    ratio = normalize_aspect(aspect or shot.get("aspect_ratio"))
    preset = ASPECT_PRESETS[ratio]
    shot["aspect_ratio"] = ratio
    shot["orientation"] = preset["orientation"]
    shot["delivery_formats"] = shot.get("delivery_formats") or [ratio]
    if ratio != "16:9" and "16:9" not in shot["delivery_formats"]:
        shot["delivery_formats"].append("16:9")
    shot["handoff_targets"] = {
        "trailer_director": preset["handoff"]["trailer"],
        "key_art_designer": preset["handoff"]["key_art"],
    }
    return shot


def apply_aspect_to_clip(clip: dict[str, Any], aspect: str | None = None) -> dict[str, Any]:
    ratio = normalize_aspect(aspect or clip.get("aspect_ratio"))
    preset = ASPECT_PRESETS[ratio]
    clip["aspect_ratio"] = ratio
    clip["orientation"] = preset["orientation"]
    clip["delivery_formats"] = clip.get("delivery_formats") or [ratio, "16:9"]
    return clip


def plan_social_variants(
    items: list[dict[str, Any]],
    *,
    include_master: bool = True,
) -> dict[str, Any]:
    """Aggregate delivery format plan for a batch or sequence."""
    formats: set[str] = set()
    by_aspect: dict[str, list[str]] = {a: [] for a in ASPECT_OPTIONS}
    for item in items:
        aspect = normalize_aspect(item.get("aspect_ratio"))
        item_id = item.get("shot_id") or item.get("clip_id") or "item"
        by_aspect[aspect].append(item_id)
        for fmt in item.get("delivery_formats") or [aspect]:
            formats.add(normalize_aspect(fmt))
    if include_master:
        formats.add("16:9")
    return {
        "formats": sorted(formats),
        "by_aspect": {k: v for k, v in by_aspect.items() if v},
        "total_items": len(items),
    }


def parse_aspect_from_spec(spec: str) -> tuple[str | None, str]:
    """Parse aspect:rest or tier:aspect:description patterns."""
    for aspect in sorted(ASPECT_OPTIONS, key=len, reverse=True):
        prefix = f"{aspect}:"
        if spec.startswith(prefix):
            return normalize_aspect(aspect), spec[len(prefix):]

    parts = spec.split(":")
    for i in range(1, len(parts)):
        for j in range(i + 1, min(i + 3, len(parts) + 1)):
            candidate = ":".join(parts[i:j])
            if candidate not in ASPECT_PRESETS:
                continue
            before = ":".join(parts[:i])
            after = ":".join(parts[j:])
            if before and after:
                return normalize_aspect(candidate), f"{before}:{after}"
            if before:
                return normalize_aspect(candidate), before if not after else f"{before}:{after}"
            return normalize_aspect(candidate), after
    return None, spec