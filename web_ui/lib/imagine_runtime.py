"""Imagine API and reference asset helpers for the Web UI."""

from __future__ import annotations

from typing import Any

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
    list_batches as list_sfw_batches,
    load_batch as load_sfw_batch,
    parse_inline_shot,
    plan_batch as plan_sfw_batch,
    save_batch as save_sfw_batch,
)


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
) -> tuple[dict[str, Any], str]:
    batch = plan_sfw_batch(title, shots, tier=tier, budget_credits=budget_credits, fast_mode=fast_mode)
    path = save_sfw_batch(batch)
    return batch, str(path)


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