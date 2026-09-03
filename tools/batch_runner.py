#!/usr/bin/env python3
"""
Batch shot runner — execute SFW/NSFW batch shots via Imagine API with job tracking.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from aup_gate import gate_imagine_prompt, gate_nsfw_shot
from imagine_bridge import build_bridge_packet, bridge_to_markdown
from imagine_client import (
    ImagineAPIError,
    extract_image_url,
    extract_video_url,
    generate_image,
    is_dry_run,
    poll_video_job,
    submit_video_generation,
)
from imagine_jobs import create_job, get_reference_asset, transition_job
from models import HERO_IMAGINE_IMAGE_MODEL
from quota_sync import record_generation_spend


@dataclass(frozen=True)
class BatchPipeline:
    name: str
    decide_mode: Callable[..., dict[str, Any]]
    estimate_cost: Callable[..., dict[str, Any]]
    save_batch: Callable[[dict[str, Any]], Any]
    prompt_prefix: str = "Cinematic"


def _build_shot_prompt(
    shot: dict[str, Any],
    *,
    override: str | None = None,
    prefix: str = "Cinematic",
) -> str:
    if override:
        return override.strip()
    desc = shot.get("description", "").strip()
    tier = shot.get("tier", "coverage")
    return f"{prefix} {tier} shot: {desc}. Masterpiece, film grain, volumetric lighting, 8K UHD."


def _resolve_reference_url(shot: dict[str, Any]) -> str | None:
    ref_id = shot.get("reference_image_id")
    if shot.get("reference_image_url"):
        return shot["reference_image_url"]
    if ref_id:
        asset = get_reference_asset(ref_id)
        if asset:
            return asset.get("url")
    return None


def execute_shot(
    batch: dict[str, Any],
    shot_id: str,
    *,
    pipeline: BatchPipeline,
    dry_run: bool | None = None,
    prompt_override: str | None = None,
    poll: bool = True,
    record_quota: bool = True,
) -> dict[str, Any]:
    """Submit a batch shot to Imagine and update shot + batch state."""
    shot = None
    for s in batch.get("shots", []):
        if s["shot_id"] == shot_id:
            shot = s
            break
    if not shot:
        raise ValueError(f"Shot not found: {shot_id}")

    if pipeline.name == "nsfw":
        gate_nsfw_shot(shot, extra_prompt=prompt_override or "")

    if shot.get("status") not in ("scheduled", "pending", "qa_fail", "qa_pass"):
        if shot.get("quality_pass_status") == "quality_pass_pending":
            pass
        elif shot.get("status") == "generating":
            raise RuntimeError(f"Shot {shot_id} is already generating")

    decision = pipeline.decide_mode(shot)
    mode = shot.get("recommended_mode") or decision["mode"]
    cost_est = pipeline.estimate_cost(
        {**shot, "recommended_mode": mode},
        fast_mode=batch.get("fast_mode", False),
    )
    prompt = _build_shot_prompt(shot, override=prompt_override, prefix=pipeline.prompt_prefix)
    use_dry = is_dry_run() if dry_run is None else dry_run
    ref_url = _resolve_reference_url(shot)
    gate_imagine_prompt(
        prompt,
        nsfw=pipeline.name == "nsfw",
        has_reference_image=bool(ref_url),
    )

    job_type = "video"
    img_model = shot.get("image_model", "grok-imagine-image")
    vid_model = shot.get("video_model", "grok-imagine-video-1.5")
    model = vid_model

    image_quality_pin: str | None = None
    if mode == "image_prompt":
        job_type = "image"
        model = img_model
        if shot.get("image_quality"):
            model = HERO_IMAGINE_IMAGE_MODEL
            image_quality_pin = "medium"
    elif mode == "image_to_video":
        job_type = "video"
        model = vid_model

    job = create_job(
        job_type,
        prompt=prompt,
        model=model,
        shot_id=shot_id,
        reference_image_id=shot.get("reference_image_id"),
        metadata={
            "batch_id": batch.get("batch_id"),
            "batch_slug": batch.get("slug"),
            "pipeline": pipeline.name,
            "mode": mode,
            "tier": shot.get("tier"),
        },
    )
    transition_job(job["job_id"], "running", dry_run=use_dry)
    shot["status"] = "generating"
    shot["imagine_job_id"] = job["job_id"]
    shot["last_prompt"] = prompt

    est_credits = cost_est.get("credits", 10)
    result_url: str | None = None

    try:
        if mode == "image_prompt":
            resp = generate_image(
                prompt,
                model=model,
                quality=image_quality_pin,
                dry_run=use_dry,
            )
            result_url = extract_image_url(resp)
            transition_job(job["job_id"], "qa_pending", result_url=result_url)
            shot["result_url"] = result_url
            shot["reference_image_url"] = result_url
            shot["has_reference"] = True
            shot["status"] = "qa_pending"
        elif mode == "image_to_video":
            if not ref_url and not use_dry:
                raise ImagineAPIError("image_to_video requires reference plate — register and lock first")
            resp = submit_video_generation(
                prompt,
                model=vid_model,
                duration=int(shot.get("duration_seconds", 10)),
                image_url=ref_url,
                aspect_ratio=shot.get("aspect_ratio"),
                dry_run=use_dry,
            )
            request_id = resp.get("request_id")
            result = poll_video_job(request_id) if request_id and poll and not use_dry else resp
            result_url = extract_video_url(result)
            transition_job(job["job_id"], "qa_pending", request_id=request_id, result_url=result_url)
            shot["result_url"] = result_url
            shot["status"] = "qa_pending"
        else:
            resp = submit_video_generation(
                prompt,
                model=vid_model,
                duration=int(shot.get("duration_seconds", 10)),
                aspect_ratio=shot.get("aspect_ratio"),
                dry_run=use_dry,
            )
            request_id = resp.get("request_id")
            result = poll_video_job(request_id) if request_id and poll and not use_dry else resp
            result_url = extract_video_url(result)
            transition_job(job["job_id"], "qa_pending", request_id=request_id, result_url=result_url)
            shot["result_url"] = result_url
            shot["status"] = "qa_pending"

        pipeline.save_batch(batch)

        if record_quota and not use_dry:
            record_generation_spend(
                est_credits,
                estimated_credits=est_credits,
                note=f"{pipeline.name}:{batch.get('slug')}:{shot_id}",
                job_id=job["job_id"],
                shot_id=shot_id,
            )

        bridge = build_bridge_packet(
            {**shot, "recommended_mode": mode, "batch_slug": batch.get("slug")},
            context="shot",
            prompt=prompt,
        )

        return {
            "job_id": job["job_id"],
            "shot_id": shot_id,
            "pipeline": pipeline.name,
            "mode": mode,
            "status": shot["status"],
            "result_url": result_url,
            "dry_run": use_dry,
            "estimated_credits": est_credits,
            "bridge_markdown": bridge_to_markdown(bridge),
        }

    except ImagineAPIError as exc:
        transition_job(job["job_id"], "failed", error=str(exc))
        shot["status"] = "failed"
        pipeline.save_batch(batch)
        raise


def sfw_pipeline() -> BatchPipeline:
    from sfw_decisions import decide_generation_mode, estimate_shot_cost
    from sfw_orchestrator import save_batch

    return BatchPipeline("sfw", decide_generation_mode, estimate_shot_cost, save_batch)


def nsfw_pipeline() -> BatchPipeline:
    from nsfw_decisions import decide_generation_mode, estimate_shot_cost
    from nsfw_orchestrator import save_batch

    return BatchPipeline("nsfw", decide_generation_mode, estimate_shot_cost, save_batch, prompt_prefix="Intimate cinematic")


def execute_sfw_shot(batch: dict[str, Any], shot_id: str, **kwargs: Any) -> dict[str, Any]:
    return execute_shot(batch, shot_id, pipeline=sfw_pipeline(), **kwargs)


def execute_nsfw_shot(batch: dict[str, Any], shot_id: str, **kwargs: Any) -> dict[str, Any]:
    return execute_shot(batch, shot_id, pipeline=nsfw_pipeline(), **kwargs)