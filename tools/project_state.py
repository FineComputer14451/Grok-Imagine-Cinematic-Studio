#!/usr/bin/env python3
"""
Canonical project state for Grok Imagine Cinematic Studio.

Single source of truth for `.cinematic_project_state.json` — used by CLI, Web UI,
character DNA, quota optimizer, and NSFW orchestrator.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from models import (
    STUDIO_COMPATIBILITY_VERSION,
    build_video_pipeline_spec,
    model_stack_summary,
)
from studio_paths import PROJECT_STATE_FILE

SCHEMA_VERSION = "1.0"
QUOTA_SCHEMA_VERSION = "1.1"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def default_quota_state() -> dict[str, Any]:
    return {
        "schema_version": QUOTA_SCHEMA_VERSION,
        "tier": "supergrok_pro",
        "budget_remaining": None,
        "session_spent": 0,
        "session_generations": 0,
        "history": [],
        "updated_at": _now_iso(),
    }


def default_imagine_jobs_state() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "jobs": {},
        "updated_at": _now_iso(),
    }


def default_asset_manifest() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "assets": {},
        "updated_at": _now_iso(),
    }


def default_project_state() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "project": None,
        "characters": {},
        "identity_lock": {},
        "locked_variables": {},
        "quota": default_quota_state(),
        "imagine_jobs": default_imagine_jobs_state(),
        "asset_manifest": default_asset_manifest(),
        "model_stack": model_stack_summary(),
        "video_pipeline_spec": build_video_pipeline_spec(),
        "studio_compatibility_version": STUDIO_COMPATIBILITY_VERSION,
    }


def _merge_dict_field(
    merged: dict[str, Any],
    key: str,
    default_val: Any,
) -> None:
    """Repair missing, null, or wrongly-typed dict fields from legacy state files."""
    if isinstance(merged.get(key), dict):
        return
    merged[key] = dict(default_val) if isinstance(default_val, dict) else {}


def _merge_defaults(state: dict[str, Any], defaults: dict[str, Any]) -> dict[str, Any]:
    """Fill missing top-level keys and normalize legacy null/wrong types."""
    merged = dict(state)
    for key, default_val in defaults.items():
        if key not in merged:
            merged[key] = default_val
    for key in ("characters", "identity_lock", "locked_variables", "imagine_jobs", "asset_manifest"):
        _merge_dict_field(merged, key, defaults.get(key, {}))
    if not isinstance(merged.get("quota"), dict):
        merged["quota"] = default_quota_state()
    else:
        quota_defaults = default_quota_state()
        for key, default_val in quota_defaults.items():
            if key not in merged["quota"]:
                merged["quota"][key] = default_val
    return merged


def load_project_state(state_file: Path | None = None) -> dict[str, Any]:
    path = state_file or PROJECT_STATE_FILE
    defaults = default_project_state()
    if not path.exists():
        return defaults
    loaded = json.loads(path.read_text())
    if not isinstance(loaded, dict):
        return defaults
    return _merge_defaults(loaded, defaults)


def save_project_state(state: dict[str, Any], state_file: Path | None = None) -> None:
    path = state_file or PROJECT_STATE_FILE
    path.write_text(json.dumps(state, indent=2))