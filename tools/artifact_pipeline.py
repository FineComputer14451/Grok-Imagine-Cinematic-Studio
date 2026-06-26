#!/usr/bin/env python3
"""
Artifact pipeline — register and cache Imagine generation outputs under artifacts/.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from project_state import load_project_state, save_project_state
from studio_paths import ARTIFACTS_DIR

SCHEMA_VERSION = "1.0"
GENERATIONS_DIR = ARTIFACTS_DIR / "generations"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def default_artifacts_state() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "entries": [],
        "updated_at": _now_iso(),
    }


def ensure_artifacts_state(state: dict[str, Any]) -> dict[str, Any]:
    if "artifacts" not in state or not isinstance(state.get("artifacts"), dict):
        state["artifacts"] = default_artifacts_state()
    art = state["artifacts"]
    art.setdefault("entries", [])
    art.setdefault("schema_version", SCHEMA_VERSION)
    return art


def _guess_extension(url: str, job_type: str | None = None) -> str:
    path = urlparse(url).path
    if "." in path.split("/")[-1]:
        return path.rsplit(".", 1)[-1].split("?")[0]
    if job_type in ("video", "video_extend"):
        return "mp4"
    return "png"


def _safe_slug(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-") or "item"


def register_artifact_from_result(
    result: dict[str, Any],
    *,
    batch_slug: str | None = None,
    sequence_slug: str | None = None,
    pipeline: str | None = None,
    download: bool = False,
) -> dict[str, Any]:
    """Record artifact metadata; optionally write placeholder manifest for dry-run URLs."""
    url = result.get("result_url")
    if not url:
        raise ValueError("result has no result_url")

    job_id = result.get("job_id", "unknown")
    shot_id = result.get("shot_id") or result.get("clip_id") or "shot"
    ext = _guess_extension(url, result.get("job_type"))
    subdir = GENERATIONS_DIR / _safe_slug(pipeline or "studio") / _safe_slug(batch_slug or sequence_slug or "misc")
    subdir.mkdir(parents=True, exist_ok=True)
    local_path = subdir / f"{_safe_slug(shot_id)}_{job_id[-12:]}.{ext}"

    manifest = {
        "job_id": job_id,
        "shot_id": result.get("shot_id"),
        "clip_id": result.get("clip_id"),
        "result_url": url,
        "local_path": str(local_path),
        "pipeline": pipeline,
        "batch_slug": batch_slug,
        "sequence_slug": sequence_slug,
        "dry_run": result.get("dry_run", False),
        "registered_at": _now_iso(),
    }
    local_path.with_suffix(local_path.suffix + ".manifest.json").write_text(json.dumps(manifest, indent=2))

    if download and not result.get("dry_run"):
        try:
            import urllib.request
            urllib.request.urlretrieve(url, local_path)
            manifest["downloaded"] = True
        except OSError:
            manifest["downloaded"] = False
    else:
        manifest["downloaded"] = local_path.exists() and local_path.stat().st_size > 0

    state = load_project_state()
    art = ensure_artifacts_state(state)
    art["entries"].append(manifest)
    art["entries"] = art["entries"][-200:]
    art["updated_at"] = _now_iso()
    save_project_state(state)
    return manifest


def register_artifact_from_job(job_id: str, *, download: bool = False) -> dict[str, Any]:
    from imagine_jobs import get_job

    job = get_job(job_id)
    if not job:
        raise KeyError(f"Job not found: {job_id}")
    if not job.get("result_url"):
        raise ValueError(f"Job {job_id} has no result_url")

    meta = job.get("metadata") or {}
    return register_artifact_from_result(
        {
            "job_id": job_id,
            "shot_id": job.get("shot_id"),
            "clip_id": job.get("clip_id"),
            "result_url": job.get("result_url"),
            "dry_run": job.get("dry_run", False),
            "job_type": job.get("job_type"),
        },
        batch_slug=meta.get("batch_slug"),
        pipeline=meta.get("pipeline"),
        download=download,
    )


def list_artifacts(*, limit: int = 30) -> list[dict[str, Any]]:
    state = load_project_state()
    art = ensure_artifacts_state(state)
    return list(reversed(art.get("entries", [])))[:limit]


def artifacts_summary() -> dict[str, Any]:
    state = load_project_state()
    art = ensure_artifacts_state(state)
    entries = art.get("entries", [])
    downloaded = sum(1 for e in entries if e.get("downloaded"))
    return {
        "total": len(entries),
        "downloaded": downloaded,
        "generations_dir": str(GENERATIONS_DIR),
        "updated_at": art.get("updated_at"),
    }