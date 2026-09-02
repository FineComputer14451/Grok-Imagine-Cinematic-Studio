"""NSFW helpers for the Web UI — thin wrappers over tools/."""

from __future__ import annotations

from typing import Any

from aup_gate import gate_nsfw_batch, gate_nsfw_shot
from nsfw_orchestrator import (
    EXPLICIT_OPTIONS,
    MOTION_OPTIONS,
    RETRY_REASON_OPTIONS,
    SHOT_TIER_OPTIONS,
    batch_to_markdown,  # re-export for pages
    build_shot_context,
    decide_generation_mode,
    generate_daily_report,
    get_next_shots,
    list_batches,  # re-export for pages
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
from batch_runner import execute_nsfw_shot
from project_state import load_project_state
from session_runner import run_batch_session as _run_batch_session

# Re-export canonical option lists for Streamlit widgets
SHOT_TIER_OPTIONS = list(SHOT_TIER_OPTIONS)
MOTION_OPTIONS = list(MOTION_OPTIONS)
EXPLICIT_OPTIONS = list(EXPLICIT_OPTIONS)
RETRY_REASONS = list(RETRY_REASON_OPTIONS)


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
    normalized: list[dict[str, Any]] = []
    for item in shots:
        if isinstance(item, str):
            normalized.append(parse_inline_shot(item))
        else:
            normalized.append(item)
    gate_nsfw_batch(title, normalized)
    batch = plan_batch(title, normalized, tier=tier, budget_credits=budget_credits, fast_mode=fast_mode)
    path = save_batch(batch)
    return batch, str(path)


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
    shot = build_shot_context(
        shot_id,
        tier=shot_tier,
        motion=motion,
        has_ref=has_ref,
        explicit=explicit,
        duration=duration,
    )
    gate_nsfw_shot(shot)
    if budget_remaining is None:
        budget_remaining = load_project_state().get("quota", {}).get("budget_remaining")
    return decide_generation_mode(shot, budget_remaining=budget_remaining)


def retry_plan(
    shot_id: str,
    *,
    reason: str = "physics_failure",
    score: float | None = None,
    attempts: int = 0,
    shot_tier: str = "key_explicit",
) -> dict[str, Any]:
    shot = build_shot_context(shot_id, tier=shot_tier, recommended_mode="image_to_video")
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


def save_extension(seq: dict[str, Any]) -> str:
    return str(save_nsfw_sequence(seq))


def run_nsfw_shot(
    batch_slug: str,
    shot_id: str,
    *,
    dry_run: bool = False,
    prompt: str | None = None,
) -> dict[str, Any]:
    batch = load_batch(batch_slug)
    return execute_nsfw_shot(batch, shot_id, dry_run=dry_run, prompt_override=prompt)


def run_nsfw_session(
    batch_slug: str,
    *,
    count: int = 3,
    dry_run: bool = False,
) -> dict[str, Any]:
    return _run_batch_session(batch_slug, pipeline="nsfw", count=count, dry_run=dry_run)