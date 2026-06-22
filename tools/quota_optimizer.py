#!/usr/bin/env python3
"""
Workflow Quota Optimizer — per-second 1.5 pricing, session tracking, and recommendations.

Used by:
  - cinematic_studio_cli.py (quota commands)
  - sequence_chain.py (sequence cost estimates)
  - web_ui/app.py (live cost simulator)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"
PROJECT_STATE_FILE = Path(".cinematic_project_state.json")
QUOTA_CONFIG_FILE = Path(".quota_config.json")

# Estimated pricing model (configurable via .quota_config.json)
# Credits are abstract units; usd_per_credit is illustrative.
DEFAULT_PRICING = {
    "imagine_video_1.5": {
        "720p": {"credits_per_second": 10},
        "480p": {"credits_per_second": 6},
    },
    "imagine_image": {"credits_per_image": 5},
    "fast_mode_multiplier": 0.55,
    "quality_pass_multiplier": 1.0,
    "native_audio_surcharge_per_second": 2,
    "extend_stitch_overhead_per_clip": 3,
    "chain_qa_retry_probability": 0.2,
    "retry_buffer": 1.15,
    "usd_per_credit": 0.01,
}

SUBSCRIPTION_TIERS: dict[str, dict[str, Any]] = {
    "supergrok_pro": {
        "label": "SuperGrok Pro",
        "monthly_credits": 10_000,
        "daily_soft_cap": 500,
    },
    "supergrok_heavy": {
        "label": "SuperGrok Heavy",
        "monthly_credits": 50_000,
        "daily_soft_cap": 2_500,
    },
    "custom": {
        "label": "Custom Budget",
        "monthly_credits": None,
        "daily_soft_cap": None,
    },
}

COMPLEXITY_MULTIPLIERS = {
    "low": 1.0,
    "medium": 1.15,
    "high": 1.35,
    "extreme": 1.6,
}

AGENT_OVERHEAD_CREDITS = {
    "minimal": 0,
    "standard": 15,
    "full_studio": 40,
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_pricing_config() -> dict[str, Any]:
    if QUOTA_CONFIG_FILE.exists():
        custom = json.loads(QUOTA_CONFIG_FILE.read_text())
        pricing = dict(DEFAULT_PRICING)
        pricing.update(custom)
        return pricing
    return dict(DEFAULT_PRICING)


def load_project_state(state_file: Path | None = None) -> dict[str, Any]:
    path = state_file or PROJECT_STATE_FILE
    if path.exists():
        return json.loads(path.read_text())
    return {
        "project": None,
        "characters": {},
        "identity_lock": {},
        "locked_variables": {},
        "quota": _default_quota_state(),
    }


def _default_quota_state() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "tier": "supergrok_pro",
        "budget_remaining": None,
        "session_spent": 0,
        "session_generations": 0,
        "history": [],
        "updated_at": _now_iso(),
    }


def save_project_state(state: dict[str, Any], state_file: Path | None = None) -> None:
    path = state_file or PROJECT_STATE_FILE
    path.write_text(json.dumps(state, indent=2))


def ensure_quota_state(state: dict[str, Any]) -> dict[str, Any]:
    if "quota" not in state or not state["quota"]:
        state["quota"] = _default_quota_state()
    return state["quota"]


def estimate_clip_cost(
    duration_seconds: float,
    *,
    resolution: str = "720p",
    fast_mode: bool = False,
    native_audio: bool = True,
    quality_pass: bool = False,
    retries: int = 1,
    pricing: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Estimate cost for a single 1.5 video clip."""
    p = pricing or load_pricing_config()
    rates = p["imagine_video_1.5"].get(resolution, p["imagine_video_1.5"]["720p"])
    base = rates["credits_per_second"] * duration_seconds

    if fast_mode:
        base *= p["fast_mode_multiplier"]
    if quality_pass and fast_mode:
        base += rates["credits_per_second"] * duration_seconds * p["quality_pass_multiplier"]
    if native_audio:
        base += p["native_audio_surcharge_per_second"] * duration_seconds

    base *= retries
    buffered = base * p["retry_buffer"]

    usd = buffered * p["usd_per_credit"]
    return {
        "duration_seconds": duration_seconds,
        "resolution": resolution,
        "fast_mode": fast_mode,
        "native_audio": native_audio,
        "quality_pass": quality_pass,
        "retries": retries,
        "credits_low": round(base, 1),
        "credits_high": round(buffered, 1),
        "usd_low": round(base * p["usd_per_credit"], 2),
        "usd_high": round(usd, 2),
    }


def estimate_sequence_cost(
    clips: list[dict[str, Any]],
    *,
    resolution: str = "720p",
    fast_mode: bool = False,
    native_audio: bool = True,
    quality_pass: bool = False,
    include_qa_retries: bool = True,
    pricing: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Estimate cost for a multi-clip 1.5 sequence with extend/stitch overhead."""
    p = pricing or load_pricing_config()
    per_clip: list[dict[str, Any]] = []
    total_low = 0.0
    total_high = 0.0

    for clip in clips:
        dur = clip.get("duration_seconds", 10)
        retries = 1
        if include_qa_retries and clip.get("index", 0) > 0:
            retries = 1 + p["chain_qa_retry_probability"]

        est = estimate_clip_cost(
            dur,
            resolution=resolution,
            fast_mode=fast_mode,
            native_audio=native_audio,
            quality_pass=quality_pass,
            retries=retries,
            pricing=p,
        )
        overhead = p["extend_stitch_overhead_per_clip"] if clip.get("index", 0) > 0 else 0
        est["credits_low"] += overhead
        est["credits_high"] += overhead * p["retry_buffer"]
        est["clip_id"] = clip.get("clip_id", f"clip_{clip.get('index', 0) + 1:03d}")
        per_clip.append(est)
        total_low += est["credits_low"]
        total_high += est["credits_high"]

    usd_per = p["usd_per_credit"]
    return {
        "clip_count": len(clips),
        "total_duration_seconds": sum(c.get("duration_seconds", 10) for c in clips),
        "credits_low": round(total_low, 1),
        "credits_high": round(total_high, 1),
        "usd_low": round(total_low * usd_per, 2),
        "usd_high": round(total_high * usd_per, 2),
        "per_clip": per_clip,
        "fast_mode": fast_mode,
        "quality_pass": quality_pass,
        "resolution": resolution,
    }


def estimate_production(
    target_duration_seconds: int,
    *,
    clip_count: int | None = None,
    avg_clip_duration: float = 10.0,
    resolution: str = "720p",
    fast_mode: bool = False,
    native_audio: bool = True,
    quality_pass: bool = False,
    complexity: str = "medium",
    agent_mode: str = "standard",
    num_images: int = 0,
    pricing: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Estimate full production cost with complexity and agent overhead."""
    p = pricing or load_pricing_config()
    if clip_count is None:
        clip_count = max(1, int(target_duration_seconds / avg_clip_duration))

    clips = [
        {"clip_id": f"clip_{i + 1:03d}", "index": i, "duration_seconds": avg_clip_duration}
        for i in range(clip_count)
    ]
    seq = estimate_sequence_cost(
        clips,
        resolution=resolution,
        fast_mode=fast_mode,
        native_audio=native_audio,
        quality_pass=quality_pass,
        pricing=p,
    )

    complexity_mult = COMPLEXITY_MULTIPLIERS.get(complexity.lower(), 1.15)
    agent_overhead = AGENT_OVERHEAD_CREDITS.get(agent_mode, 15)
    image_cost = num_images * p["imagine_image"]["credits_per_image"]

    credits_low = seq["credits_low"] * complexity_mult + agent_overhead + image_cost
    credits_high = seq["credits_high"] * complexity_mult + agent_overhead + image_cost

    return {
        "target_duration_seconds": target_duration_seconds,
        "clip_count": clip_count,
        "avg_clip_duration": avg_clip_duration,
        "complexity": complexity,
        "agent_mode": agent_mode,
        "num_images": num_images,
        "credits_low": round(credits_low, 1),
        "credits_high": round(credits_high, 1),
        "usd_low": round(credits_low * p["usd_per_credit"], 2),
        "usd_high": round(credits_high * p["usd_per_credit"], 2),
        "sequence_breakdown": seq,
        "estimated_tokens": int(credits_high * 120),
    }


def assess_budget_risk(
    estimate: dict[str, Any],
    *,
    tier: str = "supergrok_pro",
    budget_remaining: float | None = None,
) -> dict[str, Any]:
    """Assess quota risk level for an estimate against tier/budget."""
    tier_info = SUBSCRIPTION_TIERS.get(tier, SUBSCRIPTION_TIERS["custom"])
    credits_high = estimate.get("credits_high", 0)

    if budget_remaining is not None:
        remaining = budget_remaining
        pct = (credits_high / remaining * 100) if remaining > 0 else 100
    elif tier_info.get("daily_soft_cap"):
        remaining = tier_info["daily_soft_cap"]
        pct = credits_high / remaining * 100
    else:
        remaining = tier_info.get("monthly_credits")
        pct = (credits_high / remaining * 100) if remaining else 0

    if pct >= 80:
        risk = "critical"
    elif pct >= 50:
        risk = "high"
    elif pct >= 25:
        risk = "medium"
    else:
        risk = "low"

    return {
        "risk_level": risk,
        "credits_high": credits_high,
        "budget_remaining": remaining,
        "budget_pct_used": round(pct, 1),
        "tier": tier,
        "tier_label": tier_info["label"],
    }


def get_optimization_recommendations(
    estimate: dict[str, Any],
    *,
    risk: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    """Generate quota-aware optimization recommendations."""
    recs: list[dict[str, str]] = []
    seq = estimate.get("sequence_breakdown") or estimate
    clip_count = estimate.get("clip_count") or seq.get("clip_count", 1)

    if not estimate.get("fast_mode") and estimate.get("credits_high", 0) > 200:
        recs.append({
            "priority": "high",
            "action": "Use Fast mode for iteration, then quality pass on hero shots only",
            "savings": "~40-45% on draft clips",
        })

    if clip_count > 8:
        recs.append({
            "priority": "medium",
            "action": f"Reduce clip count from {clip_count} to {max(6, clip_count - 2)} with longer 10-12s atmospheric beats",
            "savings": "~15-20% fewer extend overhead charges",
        })

    avg_dur = estimate.get("avg_clip_duration", 10)
    if avg_dur > 12:
        recs.append({
            "priority": "medium",
            "action": "Split clips longer than 12s — 1.5 sweet spot is 8-12s for consistency",
            "savings": "Fewer QA retries and drift regens",
        })

    if risk and risk.get("risk_level") in ("high", "critical"):
        recs.append({
            "priority": "critical",
            "action": "ACTIVATE ONLY core agents: Studio Director, Imagine Prompt Master, Identity Lock, Quota Optimizer",
            "savings": f"Reduce agent overhead; budget at {risk.get('budget_pct_used')}%",
        })
        recs.append({
            "priority": "high",
            "action": "Run chain QA before every extend — prevent costly regen loops",
            "savings": "~20% retry buffer recovery",
        })

    if estimate.get("num_images", 0) > 5:
        recs.append({
            "priority": "low",
            "action": "Batch keyframe generation; reuse reference_image_id across clips",
            "savings": "~1 image credit per reused ref",
        })

    if not recs:
        recs.append({
            "priority": "low",
            "action": "Production estimate within efficient range — proceed with balanced mode",
            "savings": "N/A",
        })

    return recs


def record_spend(
    credits: float,
    *,
    note: str = "",
    state: dict[str, Any] | None = None,
    state_file: Path | None = None,
) -> dict[str, Any]:
    """Record generation spend to session quota tracker."""
    if state is None:
        state = load_project_state(state_file)
    quota = ensure_quota_state(state)
    quota["session_spent"] = round(quota.get("session_spent", 0) + credits, 1)
    quota["session_generations"] = quota.get("session_generations", 0) + 1
    if quota.get("budget_remaining") is not None:
        quota["budget_remaining"] = round(max(0, quota["budget_remaining"] - credits), 1)
    quota["history"].append({
        "credits": credits,
        "note": note,
        "at": _now_iso(),
    })
    quota["history"] = quota["history"][-50:]
    quota["updated_at"] = _now_iso()
    save_project_state(state, state_file)
    return quota


def set_budget(
    *,
    tier: str = "supergrok_pro",
    remaining: float | None = None,
    state: dict[str, Any] | None = None,
    state_file: Path | None = None,
) -> dict[str, Any]:
    """Set subscription tier and optional remaining budget."""
    if state is None:
        state = load_project_state(state_file)
    quota = ensure_quota_state(state)
    quota["tier"] = tier
    if remaining is not None:
        quota["budget_remaining"] = remaining
    elif tier in SUBSCRIPTION_TIERS and SUBSCRIPTION_TIERS[tier].get("monthly_credits"):
        quota["budget_remaining"] = float(SUBSCRIPTION_TIERS[tier]["monthly_credits"])
    quota["updated_at"] = _now_iso()
    save_project_state(state, state_file)
    return quota


def quota_dashboard(state: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build quota dashboard summary."""
    if state is None:
        state = load_project_state()
    quota = ensure_quota_state(state)
    tier = quota.get("tier", "supergrok_pro")
    tier_info = SUBSCRIPTION_TIERS.get(tier, SUBSCRIPTION_TIERS["custom"])
    remaining = quota.get("budget_remaining")
    spent = quota.get("session_spent", 0)

    return {
        "tier": tier,
        "tier_label": tier_info["label"],
        "session_spent": spent,
        "session_generations": quota.get("session_generations", 0),
        "budget_remaining": remaining,
        "budget_pct_used": round(spent / remaining * 100, 1) if remaining else None,
        "daily_soft_cap": tier_info.get("daily_soft_cap"),
        "monthly_credits": tier_info.get("monthly_credits"),
        "recent_history": quota.get("history", [])[-5:],
        "updated_at": quota.get("updated_at"),
    }