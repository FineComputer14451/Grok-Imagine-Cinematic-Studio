"""NSFW orchestrator and sequence helpers for the Web UI."""

from __future__ import annotations

from typing import Any

from nsfw_orchestrator import (
    batch_to_markdown,
    decide_generation_mode,
    generate_daily_report,
    get_next_shots,
    list_batches,
    load_batch,
    parse_inline_shot,
    plan_batch,
    record_shot_result,
    save_batch,
    suggest_retry,
)
from nsfw_sequence_extender import (
    TENSION_PROFILES,
    nsfw_sequence_to_markdown,
    plan_nsfw_extension,
    save_nsfw_sequence,
)

SHOT_TIER_OPTIONS = [
    "hero",
    "consistency_anchor",
    "key_explicit",
    "support",
    "filler",
]
MOTION_OPTIONS = ["low", "medium", "high"]
EXPLICIT_OPTIONS = ["suggestive", "moderate", "explicit"]
RETRY_REASONS = [
    "identity_drift",
    "physics_failure",
    "emotional_flat",
    "explicit_uncanny",
    "audio_sync_fail",
    "quota_pressure",
]


def parse_shot_lines(text: str) -> list[dict[str, Any]]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return [parse_inline_shot(ln) for ln in lines]


def plan_and_save_batch(
    title: str,
    shots: list[dict[str, Any]] | list[str],
    *,
    tier: str = "supergrok_heavy",
    budget_credits: float | None = None,
    fast_mode: bool = False,
) -> tuple[dict[str, Any], str]:
    batch = plan_batch(title, shots, tier=tier, budget_credits=budget_credits, fast_mode=fast_mode)
    path = save_batch(batch)
    return batch, str(path)


def batch_markdown(batch: dict[str, Any]) -> str:
    return batch_to_markdown(batch)


def fetch_batches() -> list[dict[str, Any]]:
    return list_batches()


def next_shots(batch_slug: str, count: int = 5) -> list[dict[str, Any]]:
    batch = load_batch(batch_slug)
    return get_next_shots(batch, count=count)


def mode_decision(
    shot_id: str,
    *,
    shot_tier: str = "support",
    motion: str = "medium",
    has_ref: bool = False,
    explicit: str = "moderate",
    duration: float = 10.0,
    budget_remaining: float | None = None,
) -> dict[str, Any]:
    shot = {
        "shot_id": shot_id,
        "tier": shot_tier,
        "motion_complexity": motion,
        "has_reference": has_ref,
        "explicit_level": explicit,
        "duration_seconds": duration,
        "consistency_required": True,
    }
    return decide_generation_mode(shot, budget_remaining=budget_remaining)


def retry_plan(
    shot_id: str,
    *,
    reason: str = "physics_failure",
    score: float | None = None,
    attempts: int = 0,
    shot_tier: str = "key_explicit",
) -> dict[str, Any]:
    shot = {
        "shot_id": shot_id,
        "tier": shot_tier,
        "duration_seconds": 10,
        "recommended_mode": "image_to_video",
    }
    return suggest_retry(shot, failure_reason=reason, quality_score=score, attempts=attempts)


def record_shot(
    batch_slug: str,
    shot_id: str,
    *,
    score: float,
    credits: float,
    failure_reason: str | None = None,
    notes: str = "",
) -> dict[str, Any]:
    batch = load_batch(batch_slug)
    return record_shot_result(
        batch,
        shot_id,
        quality_score=score,
        credits_spent=credits,
        failure_reason=failure_reason,
        notes=notes,
    )


def daily_report(report_date: str | None = None) -> dict[str, Any]:
    return generate_daily_report(report_date)


def plan_extension(
    title: str,
    *,
    duration: int = 90,
    profile: str = "passionate",
    reference: str = "",
) -> dict[str, Any]:
    return plan_nsfw_extension(
        title,
        target_duration=duration,
        tension_profile=profile,
        reference_description=reference,
    )


def extension_markdown(seq: dict[str, Any]) -> str:
    return nsfw_sequence_to_markdown(seq)


def save_extension(seq: dict[str, Any]) -> str:
    path = save_nsfw_sequence(seq)
    return str(path)