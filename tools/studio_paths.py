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
POLISHED_DIR = ARTIFACTS_DIR / "polished"
DELIVERY_DIR = ARTIFACTS_DIR / "delivery"
EDL_DIR = ARTIFACTS_DIR / "edl"
ANIMATIC_DIR = ARTIFACTS_DIR / "animatics"
QUOTA_CONFIG_FILE = STUDIO_ROOT / ".quota_config.json"

# Plugin / marketplace catalog paths (Grok plugin system)
PLUGIN_DIR = STUDIO_ROOT / ".grok-plugin"
PLUGIN_MANIFEST_PATH = PLUGIN_DIR / "plugin.json"
PLUGIN_INDEX_PATH = PLUGIN_DIR / "plugin-index.json"
PLUGIN_MARKETPLACE_PATH = PLUGIN_DIR / "marketplace.json"
PLUGIN_PACKS_CONFIG = STUDIO_ROOT / "config" / "plugin_packs.yaml"
PLUGIN_PACKS_DIR = PLUGIN_DIR / "packs"
COMMANDS_DIR = STUDIO_ROOT / "commands"
SKILLS_DIR = STUDIO_ROOT / ".grok" / "skills"