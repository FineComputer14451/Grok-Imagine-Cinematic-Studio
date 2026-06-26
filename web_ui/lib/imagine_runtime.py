"""Imagine API and reference asset helpers for the Web UI."""

from __future__ import annotations

from typing import Any

from batch_runner import execute_shot
from imagine_bridge import bridge_to_clipboard, bridge_to_markdown, build_bridge_packet
from imagine_client import is_dry_run
from imagine_jobs import (
    job_summary,
    list_jobs,
    list_reference_assets,
    lock_reference_asset,
    register_reference_asset,
)
from sfw_orchestrator import (
    batch_to_markdown,
    get_next_shots,
    list_batches as list_sfw_batches,
    load_batch as load_sfw_batch,
    parse_inline_shot,
    plan_batch as plan_sfw_batch,
    record_shot_result,
    save_batch as save_sfw_batch,
)
from sequence_chain import find_sequence, get_clip, load_sequence


def parse_shot_lines(text: str) -> list[dict[str, Any]]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return [parse_inline_shot(ln) for ln in lines]


def plan_and_save_sfw_batch(
    title: str,
    shots: list[dict[str, Any]],
    *,
    tier: str = "supergrok_pro",
    budget_credits: float | None = None,
    fast_mode: bool = False,
    two_pass: bool = False,
) -> tuple[dict[str, Any], str]:
    batch = plan_sfw_batch(
        title, shots, tier=tier, budget_credits=budget_credits,
        fast_mode=fast_mode, two_pass=two_pass,
    )
    path = save_sfw_batch(batch)
    return batch, str(path)


def get_batch_next_shots(batch_slug: str, count: int = 5) -> list[dict[str, Any]]:
    batch = load_sfw_batch(batch_slug)
    return get_next_shots(batch, count=count)


def run_sfw_shot(
    batch_slug: str,
    shot_id: str,
    *,
    dry_run: bool = False,
    prompt: str | None = None,
) -> dict[str, Any]:
    batch = load_sfw_batch(batch_slug)
    return execute_shot(batch, shot_id, dry_run=dry_run, prompt_override=prompt)


def record_sfw_shot(
    batch_slug: str,
    shot_id: str,
    *,
    quality_score: float,
    credits_spent: float,
    failure_reason: str | None = None,
    notes: str = "",
) -> dict[str, Any]:
    batch = load_sfw_batch(batch_slug)
    return record_shot_result(
        batch, shot_id,
        quality_score=quality_score,
        credits_spent=credits_spent,
        failure_reason=failure_reason,
        notes=notes,
    )


def build_shot_bridge(batch_slug: str, shot_id: str) -> dict[str, Any]:
    batch = load_sfw_batch(batch_slug)
    for sh in batch.get("shots", []):
        if sh["shot_id"] == shot_id:
            return build_bridge_packet({**sh, "batch_slug": batch_slug}, context="shot")
    raise KeyError(shot_id)


def build_clip_bridge(sequence_name: str, clip_id: str) -> dict[str, Any]:
    path = find_sequence(sequence_name)
    if not path:
        raise FileNotFoundError(sequence_name)
    seq = load_sequence(path)
    clip = get_clip(seq, clip_id)
    if not clip:
        raise KeyError(clip_id)
    return build_bridge_packet({**clip, "sequence_slug": seq.get("slug")}, context="clip")


def submit_imagine_via_cli(
    job_type: str,
    prompt: str,
    *,
    model: str | None = None,
    image_url: str | None = None,
    duration: int = 10,
    sequence: str | None = None,
    clip: str | None = None,
    dry_run: bool = False,
) -> tuple[int, str]:
    from lib.runtime import run_cli

    args = ["imagine", "submit", job_type, "--prompt", prompt]
    if model:
        args.extend(["--model", model])
    if image_url:
        args.extend(["--image-url", image_url])
    if duration != 10:
        args.extend(["--duration", str(duration)])
    if sequence:
        args.extend(["--sequence", sequence])
    if clip:
        args.extend(["--clip", clip])
    if dry_run:
        args.append("--dry-run")
    return run_cli(args, timeout=300)


def run_sequence_clip_via_cli(
    sequence_name: str,
    clip_id: str,
    *,
    dry_run: bool = False,
) -> tuple[int, str]:
    from lib.runtime import run_cli

    args = ["sequence", "run", sequence_name, "--clip", clip_id]
    if dry_run:
        args.append("--dry-run")
    return run_cli(args, timeout=300)


def add_reference_plate(
    asset_id: str,
    url: str,
    *,
    tier: str = "standard",
    shot_id: str | None = None,
    lock_status: str = "draft",
    notes: str = "",
) -> dict[str, Any]:
    return register_reference_asset(
        asset_id,
        url=url,
        tier=tier,
        shot_id=shot_id,
        lock_status=lock_status,
        notes=notes,
    )


def lock_plate(asset_id: str, *, lock_status: str = "locked") -> dict[str, Any]:
    return lock_reference_asset(asset_id, lock_status=lock_status)


def dry_run_active() -> bool:
    return is_dry_run()