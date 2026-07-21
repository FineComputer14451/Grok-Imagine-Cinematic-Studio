#!/usr/bin/env python3
"""
Animatic Director (studio v3.7.1 / Grok 4.5) — draft stills → motion tests → hero promotion.

Orchestration defaults to grok-4.5. Prefer 1.0 video for cheap motion probes.
See skill animatic-director.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from models import DEFAULT_IMAGINE_IMAGE_MODEL, DEFAULT_IMAGINE_VIDEO_MODEL
from project_state import load_project_state, save_project_state
from models import usd_to_credits
from quota_optimizer import estimate_clip_cost
from studio_paths import ANIMATIC_DIR

SCHEMA_VERSION = "1.0"
STUDIO_AGENT_VERSION = "v3.8.6"

TIER_MODELS: dict[str, dict[str, str]] = {
    "draft": {"image": DEFAULT_IMAGINE_IMAGE_MODEL, "video": "grok-imagine-video"},
    "standard": {"image": DEFAULT_IMAGINE_IMAGE_MODEL, "video": "grok-imagine-video"},
    "hero": {"image": "grok-imagine-image-quality", "video": DEFAULT_IMAGINE_VIDEO_MODEL},
}

PROMOTION_PATH = ("draft", "standard", "hero")


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def slugify(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-") or "animatic"


def parse_beat_line(spec: str) -> dict[str, Any]:
    """Parse description:seconds or tier:description:seconds."""
    parts = spec.split(":", 2)
    if len(parts) == 2:
        desc, dur = parts
        tier = "draft"
    elif len(parts) == 3:
        tier, desc, dur = parts
    else:
        tier, desc, dur = "draft", spec, "5"
    try:
        duration_hint = float(dur.strip())
    except ValueError:
        duration_hint = 5.0
    return {
        "description": desc.strip(),
        "duration_hint": duration_hint,
        "tier": tier.strip() if tier.strip() in TIER_MODELS else "draft",
    }


def create_frame(
    description: str,
    *,
    tier: str = "draft",
    duration_hint: float = 5.0,
    frame_id: str | None = None,
    index: int = 0,
) -> dict[str, Any]:
    tier = tier if tier in TIER_MODELS else "draft"
    models = TIER_MODELS[tier]
    return {
        "frame_id": frame_id or f"frame_{index + 1:03d}",
        "index": index,
        "description": description,
        "tier": tier,
        "duration_hint": duration_hint,
        "image_model": models["image"],
        "video_model": models["video"],
        "status": "planned",
        "reference_image_id": None,
        "motion_test": False,
        "promoted_from": None,
        "qa_score": None,
        "created_at": _now_iso(),
    }


def plan_animatic(
    title: str,
    beats: list[dict[str, Any] | str],
    *,
    target_duration: int = 60,
    budget_pct: float = 0.20,
) -> dict[str, Any]:
    """Plan animatic board with tiered stills and optional motion probes."""
    frames: list[dict[str, Any]] = []
    for i, raw in enumerate(beats):
        if isinstance(raw, str):
            parsed = parse_beat_line(raw)
        else:
            parsed = dict(raw)
        frames.append(create_frame(
            parsed.get("description", "Beat"),
            tier=parsed.get("tier", "draft"),
            duration_hint=parsed.get("duration_hint", 5),
            index=i,
        ))

    still_credits = sum(
        usd_to_credits(0.02 if f["tier"] != "hero" else 0.05) for f in frames
    )
    motion_frames = [f for f in frames if f.get("motion_test") or f["tier"] == "draft"]
    motion_credits = len(motion_frames[:3]) * estimate_clip_cost(6, video_model="grok-imagine-video")["credits_high"]
    animatic_credits = round(still_credits + motion_credits, 1)

    full_video_est = estimate_clip_cost(target_duration)["credits_high"]
    within_budget = animatic_credits <= full_video_est * budget_pct * 2

    return {
        "schema_version": SCHEMA_VERSION,
        "studio_agent_version": STUDIO_AGENT_VERSION,
        "title": title,
        "slug": slugify(title),
        "target_duration_seconds": target_duration,
        "budget_pct_cap": budget_pct,
        "frames": frames,
        "frame_count": len(frames),
        "cost_estimate": {
            "animatic_credits": animatic_credits,
            "full_production_credits": full_video_est,
            "animatic_pct_of_full": round(animatic_credits / max(full_video_est, 1) * 100, 1),
            "within_budget": within_budget,
        },
        "locked_anchors": [],
        "status": "planned",
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
    }


def promote_frame(
    board: dict[str, Any],
    frame_id: str,
    *,
    to_tier: str = "hero",
    qa_score: float | None = None,
) -> dict[str, Any]:
    """Promote animatic frame tier (draft → standard → hero)."""
    if to_tier not in TIER_MODELS:
        raise ValueError(f"Unknown tier: {to_tier}")

    frame = None
    for f in board.get("frames", []):
        if f["frame_id"] == frame_id:
            frame = f
            break
    if not frame:
        raise ValueError(f"Frame not found: {frame_id}")

    from_tier = frame.get("tier", "draft")
    frame["promoted_from"] = from_tier
    frame["tier"] = to_tier
    frame["image_model"] = TIER_MODELS[to_tier]["image"]
    frame["video_model"] = TIER_MODELS[to_tier]["video"]
    frame["status"] = "promoted"
    if qa_score is not None:
        frame["qa_score"] = qa_score

    if to_tier == "hero":
        anchors = board.setdefault("locked_anchors", [])
        if frame_id not in anchors:
            anchors.append(frame_id)

    board["updated_at"] = _now_iso()
    return frame


def save_animatic(board: dict[str, Any]) -> Path:
    board["updated_at"] = _now_iso()
    out_dir = ANIMATIC_DIR / board["slug"]
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "board.json"
    path.write_text(json.dumps(board, indent=2))

    state = load_project_state()
    animatics = state.setdefault("animatic_boards", {})
    animatics[board["slug"]] = {
        "title": board["title"],
        "path": str(path),
        "status": board.get("status"),
        "frame_count": board.get("frame_count"),
        "updated_at": board["updated_at"],
    }
    save_project_state(state)
    return path


def load_animatic(slug_or_title: str) -> dict[str, Any]:
    slug = slugify(slug_or_title)
    path = ANIMATIC_DIR / slug / "board.json"
    if not path.exists():
        state = load_project_state()
        meta = state.get("animatic_boards", {}).get(slug)
        if meta and Path(meta["path"]).exists():
            path = Path(meta["path"])
        else:
            raise FileNotFoundError(f"Animatic not found: {slug_or_title}")
    return json.loads(path.read_text())


def list_animatics() -> list[dict[str, Any]]:
    state = load_project_state()
    return [{"slug": slug, **meta} for slug, meta in state.get("animatic_boards", {}).items()]


def animatic_to_markdown(board: dict[str, Any]) -> str:
    est = board.get("cost_estimate", {})
    lines = [
        f"# Animatic Board — {board['title']}",
        "",
        f"**Target:** {board.get('target_duration_seconds')}s  ",
        f"**Frames:** {board.get('frame_count')}  ",
        f"**Animatic cost:** {est.get('animatic_credits')} cr ({est.get('animatic_pct_of_full')}% of full est.)  ",
        f"**Within budget:** {est.get('within_budget')}",
        "",
        "## Frames",
        "",
        "| # | Frame | Tier | Duration | Image Model | Status |",
        "|---|-------|------|----------|-------------|--------|",
    ]
    for f in board.get("frames", []):
        lines.append(
            f"| {f.get('index', 0) + 1} | {f['frame_id']} | {f['tier']} | {f.get('duration_hint')}s | "
            f"{f.get('image_model')} | {f.get('status')} |"
        )
    if board.get("locked_anchors"):
        lines.extend(["", "## Locked Anchors", ""])
        for aid in board["locked_anchors"]:
            lines.append(f"- {aid}")
    return "\n".join(lines) + "\n"