#!/usr/bin/env python3
"""
Sequence clip runner — submit Imagine jobs, poll, chain QA, update health.
"""

from __future__ import annotations

from typing import Any

from chain_qa_assist import apply_assisted_qa
from imagine_client import (
    ImagineAPIError,
    extract_video_url,
    is_dry_run,
    poll_video_job,
    submit_video_extension,
    submit_video_generation,
)
from imagine_jobs import create_job, transition_job
from quota_optimizer import record_spend
from sequence_chain import (
    build_extend_prompt,
    get_clip,
    run_chain_qa,
    save_sequence,
    update_sequence_health,
)

from models import DEFAULT_IMAGINE_VIDEO_MODEL


def _resolve_clip_prompt(seq: dict[str, Any], clip: dict[str, Any]) -> str:
    if clip.get("prompt"):
        return clip["prompt"]
    idx = clip.get("index", 0)
    if idx == 0:
        return f"Cinematic opening shot for {seq.get('sequence_name', 'sequence')}"
    prev = seq["clips"][idx - 1]
    beat = clip.get("narrative_beat") or "Continue the sequence seamlessly"
    return build_extend_prompt(seq, prev, beat)


def _block_extend(seq: dict[str, Any], clip: dict[str, Any]) -> str | None:
    idx = clip.get("index", 0)
    if idx == 0:
        return None
    prev = seq["clips"][idx - 1]
    prev_qa = prev.get("chain_qa") or {}
    if prev_qa.get("decision") == "no_go":
        return f"Previous clip {prev['clip_id']} has no_go — fix before extending"
    if prev.get("status") == "qa_hold":
        return f"Previous clip {prev['clip_id']} is on QA hold"
    if seq.get("chain_qa_status") == "no_go":
        return "Sequence chain_qa_status is no_go — resolve failing clips first"
    return None


def run_sequence_clip(
    seq: dict[str, Any],
    clip_id: str,
    *,
    dry_run: bool | None = None,
    auto_qa_scores: dict[str, float] | None = None,
    poll: bool = True,
    record_quota: bool = True,
) -> dict[str, Any]:
    """
    Submit a sequence clip to Imagine, poll the job, run chain QA, update health.

    When dry_run (no API key), completes with mock URLs and optional auto QA scores.
    """
    clip = get_clip(seq, clip_id)
    if not clip:
        raise ValueError(f"Clip not found: {clip_id}")

    block = _block_extend(seq, clip)
    if block:
        raise RuntimeError(block)

    pipeline = seq.get("video_pipeline_spec", {})
    video_model = pipeline.get("model", DEFAULT_IMAGINE_VIDEO_MODEL)
    prompt = _resolve_clip_prompt(seq, clip)
    duration = int(clip.get("duration_seconds", 10))
    idx = clip.get("index", 0)

    job = create_job(
        "video_extend" if idx > 0 else "video",
        prompt=prompt,
        model=video_model,
        sequence_slug=seq.get("slug"),
        clip_id=clip_id,
        reference_image_id=clip.get("reference_image_id") or None,
        metadata={"duration_seconds": duration, "index": idx},
    )

    use_dry = is_dry_run() if dry_run is None else dry_run
    transition_job(job["job_id"], "running", dry_run=use_dry)
    clip["status"] = "generating"
    clip["imagine_job_id"] = job["job_id"]

    credits_est = duration * 8  # rough 1.5 credits/sec placeholder for quota log

    try:
        if idx > 0:
            prev = seq["clips"][idx - 1]
            prev_url = prev.get("result_url") or prev.get("video_url")
            if not prev_url and use_dry:
                prev_url = f"https://dry-run.x.ai/videos/{prev['clip_id']}.mp4"
            if not prev_url:
                raise ImagineAPIError(
                    f"Previous clip {prev['clip_id']} has no result_url — generate it first"
                )
            submit_resp = submit_video_extension(
                prompt,
                video_url=prev_url,
                model=video_model,
                duration=duration,
                dry_run=use_dry,
            )
        else:
            image_url = None
            ref_id = clip.get("reference_image_id")
            if ref_id:
                image_url = clip.get("reference_image_url")
            submit_resp = submit_video_generation(
                prompt,
                model=video_model,
                duration=duration,
                image_url=image_url,
                aspect_ratio=clip.get("aspect_ratio"),
                dry_run=use_dry,
            )

        request_id = submit_resp.get("request_id")
        if use_dry and submit_resp.get("status") == "done":
            result = submit_resp
        elif request_id and poll:
            result = poll_video_job(request_id)
        else:
            result = submit_resp

        video_url = extract_video_url(result)
        transition_job(
            job["job_id"],
            "qa_pending",
            request_id=request_id,
            result_url=video_url,
        )
        clip["result_url"] = video_url
        clip["video_url"] = video_url
        clip["status"] = "qa_pending"

        prev_clip = seq["clips"][idx - 1] if idx > 0 else None
        if auto_qa_scores is not None:
            qa = run_chain_qa(clip, previous_clip=prev_clip, scores=auto_qa_scores)
        elif use_dry:
            applied = apply_assisted_qa(
                seq,
                clip,
                previous_clip=prev_clip,
                nsfw=bool(seq.get("nsfw_extension")),
            )
            qa = applied["chain_qa"]
        else:
            qa = run_chain_qa(clip, previous_clip=prev_clip, scores=None)
        clip["chain_qa"] = qa
        job_qa = qa

        if qa["decision"] == "go":
            clip["status"] = "approved"
            job_status = "extend_ready" if idx < len(seq["clips"]) - 1 else "approved"
            transition_job(job["job_id"], job_status, chain_qa=job_qa)
        elif qa["decision"] == "no_go":
            clip["status"] = "qa_hold"
            transition_job(job["job_id"], "qa_pending", chain_qa=job_qa)
        else:
            clip["status"] = "qa_pending"
            transition_job(job["job_id"], "qa_pending", chain_qa=job_qa)

        update_sequence_health(seq)
        save_sequence(seq)

        if record_quota and not use_dry:
            record_spend(credits_est, note=f"sequence:{seq.get('slug')}:{clip_id}")

        return {
            "job_id": job["job_id"],
            "clip_id": clip_id,
            "status": clip["status"],
            "result_url": video_url,
            "chain_qa": qa,
            "dry_run": use_dry,
            "sequence_health": seq.get("sequence_health_score"),
            "chain_qa_status": seq.get("chain_qa_status"),
        }

    except ImagineAPIError as exc:
        transition_job(job["job_id"], "failed", error=str(exc))
        clip["status"] = "failed"
        save_sequence(seq)
        raise