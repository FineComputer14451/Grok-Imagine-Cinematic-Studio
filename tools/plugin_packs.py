#!/usr/bin/env python3
"""Plugin pack selectors — load/validate config/plugin_packs.yaml."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# path bootstrap
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(_ROOT / "tools"))

from studio_paths import (  # noqa: E402
    COMMANDS_DIR,
    PLUGIN_PACKS_CONFIG,
    SKILLS_DIR,
    STUDIO_ROOT,
)

FULL_PLUGIN_NAME = "grok-imagine-cinematic-studio"
PACK_IDS: tuple[str, ...] = (
    "core",
    "camera-image",
    "sequence-narrative",
    "nsfw",
    "delivery-post",
)


class PackValidationError(ValueError):
    """Raised when pack config is invalid and caller wants exception form."""


def _load_yaml(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "PyYAML required for plugin packs. pip install pyyaml"
        ) from exc
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise PackValidationError(f"plugin packs root must be a mapping: {path}")
    return data


def load_plugin_packs(path: Path | None = None) -> dict[str, Any]:
    cfg_path = path or PLUGIN_PACKS_CONFIG
    if not cfg_path.is_file():
        raise FileNotFoundError(f"plugin packs config missing: {cfg_path}")
    return _load_yaml(cfg_path)


def discoverable_skill_names() -> set[str]:
    if not SKILLS_DIR.is_dir():
        return set()
    return {
        d.name
        for d in SKILLS_DIR.iterdir()
        if d.is_dir() and (d / "SKILL.md").is_file()
    }


def discoverable_command_stems() -> set[str]:
    if not COMMANDS_DIR.is_dir():
        return set()
    return {
        p.stem
        for p in COMMANDS_DIR.glob("*.md")
        if not p.stem.startswith("_")
    }


def validate_plugin_packs(cfg: dict[str, Any]) -> list[str]:
    """Return human-readable errors (empty = OK). Never raises for validation issues."""
    errors: list[str] = []
    packs = cfg.get("packs")
    if not isinstance(packs, dict):
        return ["packs must be a mapping"]

    missing_ids = [pid for pid in PACK_IDS if pid not in packs]
    if missing_ids:
        errors.append(f"missing pack ids: {missing_ids}")

    full = cfg.get("full_plugin") or {}
    if full.get("name") != FULL_PLUGIN_NAME:
        errors.append(f"full_plugin.name must be {FULL_PLUGIN_NAME}")

    disk_skills = discoverable_skill_names()
    disk_cmds = discoverable_command_stems()
    claimed: dict[str, str] = {}
    cmd_claimed: dict[str, str] = {}
    union: set[str] = set()

    for pid in PACK_IDS:
        pack = packs.get(pid)
        if not isinstance(pack, dict):
            errors.append(f"pack {pid} must be a mapping")
            continue
        if not pack.get("name"):
            errors.append(f"pack {pid} missing name")
        skills = pack.get("skills") or []
        if not isinstance(skills, list):
            errors.append(f"pack {pid} skills must be a list")
            continue
        for s in skills:
            if s in claimed:
                errors.append(f"skill '{s}' in two packs: {claimed[s]} and {pid}")
            else:
                claimed[s] = pid
            union.add(s)
            if disk_skills and s not in disk_skills:
                errors.append(f"skill '{s}' in pack {pid} not on disk under .grok/skills/")
        commands = pack.get("commands") or []
        if not isinstance(commands, list):
            errors.append(f"pack {pid} commands must be a list")
            continue
        for c in commands:
            if c in cmd_claimed:
                errors.append(f"command '{c}' in two packs: {cmd_claimed[c]} and {pid}")
            else:
                cmd_claimed[c] = pid
            if disk_cmds and c not in disk_cmds:
                errors.append(f"command '{c}' in pack {pid} missing commands/{c}.md")

    if disk_skills:
        missing = sorted(disk_skills - union)
        extra = sorted(union - disk_skills)
        if missing:
            errors.append(f"skills on disk not in any pack: {missing}")
        if extra:
            errors.append(f"skills in packs not on disk: {extra}")
        if len(union) != len(disk_skills):
            errors.append(
                f"pack union size {len(union)} != disk skills {len(disk_skills)}"
            )

    # All commands on disk should be owned by some pack (full suite = union)
    if disk_cmds:
        missing_cmds = sorted(disk_cmds - set(cmd_claimed))
        if missing_cmds:
            errors.append(f"commands not assigned to any pack: {missing_cmds}")

    declutter = cfg.get("declutter") or {}
    if declutter.get("policy") != "full_suite_wins":
        errors.append("declutter.policy must be full_suite_wins")
    if declutter.get("full_suite_plugin") != FULL_PLUGIN_NAME:
        errors.append(f"declutter.full_suite_plugin must be {FULL_PLUGIN_NAME}")

    return errors


def resolve_pack_skill_paths(skill_names: list[str]) -> list[str]:
    return [f".grok/skills/{name}" for name in skill_names]


def resolve_pack_command_paths(command_stems: list[str]) -> list[str]:
    return [f"commands/{stem}.md" for stem in command_stems]


def all_pack_plugin_names(cfg: dict[str, Any] | None = None) -> list[str]:
    cfg = cfg or load_plugin_packs()
    names = [cfg["full_plugin"]["name"]]
    for pid in PACK_IDS:
        names.append(cfg["packs"][pid]["name"])
    return names
