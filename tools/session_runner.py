#!/usr/bin/env python3
"""
Automated batch session runner — execute next N shots in priority order.
"""

from __future__ import annotations

from typing import Any, Literal

from artifact_pipeline import register_artifact_from_result
from batch_runner import BatchPipeline, execute_shot, nsfw_pipeline, sfw_pipeline

PipelineName = Literal["sfw", "nsfw"]


def _pipeline(name: PipelineName) -> BatchPipeline:
    return sfw_pipeline() if name == "sfw" else nsfw_pipeline()


def _load_batch(name: PipelineName, slug: str) -> dict[str, Any]:
    if name == "sfw":
        from sfw_orchestrator import load_batch
    else:
        from nsfw_orchestrator import load_batch
    return load_batch(slug)


def _get_next(name: PipelineName, batch: dict[str, Any], count: int) -> list[dict[str, Any]]:
    if name == "sfw":
        from sfw_orchestrator import get_next_shots
    else:
        from nsfw_orchestrator import get_next_shots
    return get_next_shots(batch, count=count)


def run_batch_session(
    batch_slug: str,
    *,
    pipeline: PipelineName = "sfw",
    count: int = 3,
    dry_run: bool | None = None,
    stop_on_fail: bool = True,
    cache_artifacts: bool = True,
) -> dict[str, Any]:
    """Run up to `count` next shots sequentially."""
    batch = _load_batch(pipeline, batch_slug)
    pipe = _pipeline(pipeline)
    queue = _get_next(pipeline, batch, count=count)
    if not queue:
        return {
            "batch_slug": batch_slug,
            "pipeline": pipeline,
            "executed": 0,
            "results": [],
            "message": "No pending shots",
        }

    results: list[dict[str, Any]] = []
    for shot in queue:
        shot_id = shot["shot_id"]
        try:
            result = execute_shot(
                batch, shot_id,
                pipeline=pipe,
                dry_run=dry_run,
            )
            if cache_artifacts and result.get("result_url"):
                artifact = register_artifact_from_result(
                    result,
                    batch_slug=batch_slug,
                    pipeline=pipeline,
                )
                result["artifact_path"] = str(artifact.get("local_path", ""))
            results.append(result)
        except Exception as exc:
            results.append({
                "shot_id": shot_id,
                "status": "failed",
                "error": str(exc),
            })
            if stop_on_fail:
                break

    return {
        "batch_slug": batch_slug,
        "pipeline": pipeline,
        "executed": len(results),
        "succeeded": sum(1 for r in results if r.get("status") == "qa_pending"),
        "failed": sum(1 for r in results if r.get("status") == "failed" or r.get("error")),
        "results": results,
    }