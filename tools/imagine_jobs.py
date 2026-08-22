#!/usr/bin/env python3
"""
Imagine generation job queue — persisted in project state.

Lifecycle: queued → running → qa_pending → approved → extend_ready
Terminal: failed, cancelled
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from project_state import load_project_state, save_project_state
from studio_paths import IMAGINE_JOBS_DIR

SCHEMA_VERSION = "1.0"

JOB_STATUSES = (
    "queued",
    "running",
    "qa_pending",
    "approved",
    "extend_ready",
    "failed",
    "cancelled",
)

JOB_TYPES = ("image", "image_edit", "video", "video_extend", "video_edit", "reference_to_video")


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _job_id() -> str:
    return f"job_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')}"


def _default_jobs_state() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "jobs": {},
        "updated_at": _now_iso(),
    }


def ensure_imagine_jobs_state(state: dict[str, Any]) -> dict[str, Any]:
    if "imagine_jobs" not in state or not isinstance(state.get("imagine_jobs"), dict):
        state["imagine_jobs"] = _default_jobs_state()
    jobs = state["imagine_jobs"]
    jobs.setdefault("jobs", {})
    jobs.setdefault("schema_version", SCHEMA_VERSION)
    return jobs


def _default_asset_manifest() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "assets": {},
        "updated_at": _now_iso(),
    }


def ensure_asset_manifest(state: dict[str, Any]) -> dict[str, Any]:
    if "asset_manifest" not in state or not isinstance(state.get("asset_manifest"), dict):
        state["asset_manifest"] = _default_asset_manifest()
    manifest = state["asset_manifest"]
    manifest.setdefault("assets", {})
    manifest.setdefault("schema_version", SCHEMA_VERSION)
    return manifest


def create_job(
    job_type: str,
    *,
    prompt: str,
    model: str,
    sequence_slug: str | None = None,
    clip_id: str | None = None,
    shot_id: str | None = None,
    reference_image_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if job_type not in JOB_TYPES:
        raise ValueError(f"Unknown job type: {job_type}")

    job = {
        "job_id": _job_id(),
        "job_type": job_type,
        "status": "queued",
        "prompt": prompt,
        "model": model,
        "sequence_slug": sequence_slug,
        "clip_id": clip_id,
        "shot_id": shot_id,
        "reference_image_id": reference_image_id,
        "request_id": None,
        "result_url": None,
        "dry_run": False,
        "error": None,
        "chain_qa": None,
        "metadata": metadata or {},
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
    }

    state = load_project_state()
    jobs_state = ensure_imagine_jobs_state(state)
    jobs_state["jobs"][job["job_id"]] = job
    jobs_state["updated_at"] = _now_iso()
    save_project_state(state)
    _persist_job_file(job)
    return job


def get_job(job_id: str) -> dict[str, Any] | None:
    state = load_project_state()
    jobs_state = ensure_imagine_jobs_state(state)
    return jobs_state["jobs"].get(job_id)


def list_jobs(
    *,
    status: str | None = None,
    sequence_slug: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    state = load_project_state()
    jobs_state = ensure_imagine_jobs_state(state)
    rows = list(jobs_state["jobs"].values())
    if status:
        rows = [j for j in rows if j.get("status") == status]
    if sequence_slug:
        rows = [j for j in rows if j.get("sequence_slug") == sequence_slug]
    rows.sort(key=lambda j: j.get("created_at", ""), reverse=True)
    return rows[:limit]


def update_job(job_id: str, **fields: Any) -> dict[str, Any]:
    state = load_project_state()
    jobs_state = ensure_imagine_jobs_state(state)
    job = jobs_state["jobs"].get(job_id)
    if not job:
        raise KeyError(f"Job not found: {job_id}")

    job.update(fields)
    job["updated_at"] = _now_iso()
    jobs_state["updated_at"] = _now_iso()
    save_project_state(state)
    _persist_job_file(job)
    return job


def transition_job(job_id: str, status: str, **fields: Any) -> dict[str, Any]:
    if status not in JOB_STATUSES:
        raise ValueError(f"Invalid status: {status}")
    return update_job(job_id, status=status, **fields)


def cancel_job(job_id: str, *, reason: str = "") -> dict[str, Any]:
    return transition_job(job_id, "cancelled", error=reason or "Cancelled by user")


def register_reference_asset(
    asset_id: str,
    *,
    url: str,
    tier: str = "standard",
    shot_id: str | None = None,
    reference_image_id: str | None = None,
    lock_status: str = "draft",
    notes: str = "",
) -> dict[str, Any]:
    """Add or update a reference plate in the asset manifest."""
    state = load_project_state()
    manifest = ensure_asset_manifest(state)
    entry = {
        "asset_id": asset_id,
        "type": "reference_plate",
        "url": url,
        "tier": tier,
        "shot_id": shot_id,
        "reference_image_id": reference_image_id or asset_id,
        "lock_status": lock_status,
        "notes": notes,
        "updated_at": _now_iso(),
    }
    if asset_id not in manifest["assets"]:
        entry["created_at"] = _now_iso()
    manifest["assets"][asset_id] = entry
    manifest["updated_at"] = _now_iso()
    save_project_state(state)
    return entry


def lock_reference_asset(asset_id: str, *, lock_status: str = "locked") -> dict[str, Any]:
    state = load_project_state()
    manifest = ensure_asset_manifest(state)
    asset = manifest["assets"].get(asset_id)
    if not asset:
        raise KeyError(f"Asset not found: {asset_id}")
    asset["lock_status"] = lock_status
    asset["updated_at"] = _now_iso()
    manifest["updated_at"] = _now_iso()
    save_project_state(state)
    return asset


def get_reference_asset(asset_id: str) -> dict[str, Any] | None:
    state = load_project_state()
    manifest = ensure_asset_manifest(state)
    return manifest["assets"].get(asset_id)


def list_reference_assets(*, lock_status: str | None = None) -> list[dict[str, Any]]:
    state = load_project_state()
    manifest = ensure_asset_manifest(state)
    rows = list(manifest["assets"].values())
    if lock_status:
        rows = [a for a in rows if a.get("lock_status") == lock_status]
    rows.sort(key=lambda a: a.get("updated_at", ""), reverse=True)
    return rows


def job_summary() -> dict[str, Any]:
    state = load_project_state()
    jobs_state = ensure_imagine_jobs_state(state)
    manifest = ensure_asset_manifest(state)
    counts: dict[str, int] = {s: 0 for s in JOB_STATUSES}
    for job in jobs_state["jobs"].values():
        status = job.get("status", "queued")
        counts[status] = counts.get(status, 0) + 1
    return {
        "total": len(jobs_state["jobs"]),
        "by_status": counts,
        "reference_assets": len(manifest["assets"]),
        "updated_at": jobs_state.get("updated_at"),
    }


def _persist_job_file(job: dict[str, Any]) -> None:
    IMAGINE_JOBS_DIR.mkdir(parents=True, exist_ok=True)
    path = IMAGINE_JOBS_DIR / f"{job['job_id']}.json"
    path.write_text(json.dumps(job, indent=2))