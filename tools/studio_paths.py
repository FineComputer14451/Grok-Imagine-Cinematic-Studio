"""Canonical repo-root paths for Grok Imagine Cinematic Studio tooling."""

from __future__ import annotations

from pathlib import Path

STUDIO_ROOT = Path(__file__).resolve().parent.parent

AGENTS_DIR = STUDIO_ROOT / "references" / "agents"
PROJECT_STATE_FILE = STUDIO_ROOT / ".cinematic_project_state.json"
CHARACTERS_DIR = STUDIO_ROOT / "characters"
SEQUENCES_DIR = STUDIO_ROOT / "sequences"
NSFW_BATCHES_DIR = STUDIO_ROOT / "nsfw_batches"
SFW_BATCHES_DIR = STUDIO_ROOT / "sfw_batches"
ARTIFACTS_DIR = STUDIO_ROOT / "artifacts"
REFERENCE_ASSETS_DIR = ARTIFACTS_DIR / "references"
IMAGINE_JOBS_DIR = ARTIFACTS_DIR / "jobs"
QUOTA_CONFIG_FILE = STUDIO_ROOT / ".quota_config.json"