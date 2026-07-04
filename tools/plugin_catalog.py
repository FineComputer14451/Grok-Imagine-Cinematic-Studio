"""
Canonical plugin catalog, manifest, and marketplace index logic.

Shared between the Typer CLI (cinematic-studio plugin ...), scripts/generate_plugin_index.py,
CI, and verification flows.

This centralizes discovery, building, pinning, and validation so we avoid
duplicated logic across scripts.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

# Robust import support when invoked from scripts/ or as standalone module
if __name__ != "__main__" or "tools" not in str(Path(__file__)):
    _root = Path(__file__).resolve().parent.parent
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))
    if str(_root / "tools") not in sys.path:
        sys.path.insert(0, str(_root / "tools"))

from studio_paths import (
    COMMANDS_DIR,
    PLUGIN_DIR,
    PLUGIN_INDEX_PATH,
    PLUGIN_MANIFEST_PATH,
    PLUGIN_MARKETPLACE_PATH,
    SKILLS_DIR,
    STUDIO_ROOT,
)

REPO_GIT_URL = "https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio.git"
MAX_DESCRIPTION_LEN = 120
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def parse_frontmatter(path: Path) -> dict[str, str]:
    """Parse simple YAML frontmatter from SKILL.md or command .md files."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return {}
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end]
    fields: dict[str, str] = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, value = [x.strip() for x in line.split(":", 1)]
        fields[key] = value
    return fields


def clean(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > MAX_DESCRIPTION_LEN:
        return text[: MAX_DESCRIPTION_LEN - 1].rstrip() + "…"
    return text


def git_head_sha() -> str:
    """Return current HEAD sha or raise RuntimeError."""
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=STUDIO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    sha = result.stdout.strip() if result.returncode == 0 else ""
    if not SHA_RE.match(sha):
        raise RuntimeError("unable to resolve current git HEAD sha for marketplace pin")
    return sha


def discover_skills() -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    if not SKILLS_DIR.is_dir():
        return items
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue
        frontmatter = parse_frontmatter(skill_md)
        items.append(
            {
                "name": frontmatter.get("name") or skill_dir.name,
                "description": clean(frontmatter.get("description", "")),
            }
        )
    return items


def discover_commands() -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    if not COMMANDS_DIR.is_dir():
        return items
    for path in sorted(COMMANDS_DIR.glob("*.md")):
        if path.stem.startswith("_"):
            continue
        frontmatter = parse_frontmatter(path)
        items.append(
            {
                "name": path.stem,
                "description": clean(frontmatter.get("description", "")),
            }
        )
    return items


def skill_paths() -> list[str]:
    if not SKILLS_DIR.is_dir():
        return []
    return [
        f".grok/skills/{skill_dir.name}"
        for skill_dir in sorted(SKILLS_DIR.iterdir())
        if (skill_dir / "SKILL.md").is_file()
    ]


def command_paths() -> list[str]:
    if not COMMANDS_DIR.is_dir():
        return []
    return [
        f"commands/{path.name}"
        for path in sorted(COMMANDS_DIR.glob("*.md"))
        if not path.stem.startswith("_")
    ]


def load_plugin_manifest() -> dict[str, Any]:
    if PLUGIN_MANIFEST_PATH.exists():
        try:
            data = json.loads(PLUGIN_MANIFEST_PATH.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return {}


def build_plugin_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    updated = dict(manifest)
    updated["skills"] = skill_paths()
    commands = command_paths()
    if commands:
        updated["commands"] = commands
    elif "commands" in updated:
        del updated["commands"]
    return updated


def render_plugin_manifest(manifest: dict[str, Any]) -> str:
    return json.dumps(build_plugin_manifest(manifest), indent=2, ensure_ascii=False) + "\n"


def write_plugin_manifest(manifest: dict[str, Any]) -> None:
    PLUGIN_MANIFEST_PATH.write_text(render_plugin_manifest(manifest), encoding="utf-8")


def render_index(marketplace: dict[str, Any]) -> str:
    return json.dumps(build_index(marketplace), indent=2, ensure_ascii=False) + "\n"


def sync_marketplace_sha(marketplace: dict[str, Any], sha: str) -> bool:
    """Update sha in-place for the cinematic studio entry if present. Returns whether changed."""
    changed = False
    for entry in marketplace.get("plugins", []):
        if not isinstance(entry, dict):
            continue
        source = entry.get("source")
        if not isinstance(source, dict):
            continue
        if source.get("source") != "url" and source.get("type") != "url":
            continue
        if source.get("url") != REPO_GIT_URL:
            continue
        if source.get("sha") != sha:
            source["sha"] = sha
            changed = True
    return changed


def pinned_sha(entry: dict[str, Any]) -> str | None:
    source = entry.get("source")
    if not isinstance(source, dict):
        return None
    sha = source.get("sha")
    return sha if isinstance(sha, str) and SHA_RE.match(sha) else None


def build_index(marketplace: dict[str, Any]) -> dict[str, Any]:
    plugins = marketplace.get("plugins", [])
    records: dict[str, dict[str, Any]] = {}
    skills = discover_skills()
    commands = discover_commands()
    for entry in plugins:
        if not isinstance(entry, dict):
            continue
        plugin_name = entry.get("name")
        if not isinstance(plugin_name, str) or not plugin_name:
            continue
        record: dict[str, Any] = {
            "components": {
                "skills": skills,
                **({"commands": commands} if commands else {}),
            }
        }
        sha = pinned_sha(entry)
        if sha:
            record["sha"] = sha
        records[plugin_name] = record
    return {"version": 1, "plugins": records}


def catalog_pinned_sha(marketplace: dict[str, Any]) -> str | None:
    for entry in marketplace.get("plugins", []):
        if not isinstance(entry, dict):
            continue
        source = entry.get("source")
        if not isinstance(source, dict):
            continue
        if source.get("url") != REPO_GIT_URL:
            continue
        return pinned_sha(entry)
    return None


def validate_marketplace_pins(marketplace: dict[str, Any]) -> list[str]:
    """Return list of error messages (empty means OK)."""
    errors: list[str] = []
    for entry in marketplace.get("plugins", []):
        if pinned_sha(entry) is None:
            name = entry.get("name", "<unknown>")
            errors.append(f"marketplace plugin entry '{name}' missing pinned sha")
    return errors


def validate_release_pin(marketplace: dict[str, Any]) -> list[str]:
    """Return list of error messages for release pin check."""
    errors: list[str] = []
    try:
        head_sha = git_head_sha()
    except RuntimeError as exc:
        errors.append(str(exc))
        return errors

    catalog_sha = catalog_pinned_sha(marketplace)
    if catalog_sha is None:
        errors.append("marketplace catalog missing pinned sha for this repo")
        return errors
    if catalog_sha != head_sha:
        errors.append(
            f"marketplace sha does not match git HEAD; "
            f"catalog: {catalog_sha}, HEAD: {head_sha}"
        )
    return errors


def check_plugin_artifacts(marketplace: dict[str, Any], *, require_release_pin: bool = False) -> list[str]:
    """Full artifact freshness + pin validation. Returns list of errors."""
    errors: list[str] = []

    pin_errors = validate_marketplace_pins(marketplace)
    if pin_errors:
        errors.extend(pin_errors)

    if require_release_pin:
        release_errors = validate_release_pin(marketplace)
        if release_errors:
            errors.extend(release_errors)

    if not PLUGIN_MANIFEST_PATH.exists():
        errors.append(f"{PLUGIN_MANIFEST_PATH} is missing")
    else:
        expected = render_plugin_manifest(load_plugin_manifest())
        if PLUGIN_MANIFEST_PATH.read_text(encoding="utf-8") != expected:
            errors.append("plugin.json is stale")

    if not PLUGIN_INDEX_PATH.exists():
        errors.append(f"{PLUGIN_INDEX_PATH} is missing")
    else:
        if PLUGIN_INDEX_PATH.read_text(encoding="utf-8") != render_index(marketplace):
            errors.append("plugin-index.json is stale")

    return errors


def write_artifacts(marketplace: dict[str, Any], *, sync_sha: bool = False) -> dict[str, Any]:
    """Write (or pin) the artifacts. Returns summary info."""
    result: dict[str, Any] = {"pinned": False, "sha": None}

    if sync_sha:
        try:
            head_sha = git_head_sha()
            result["sha"] = head_sha
            if sync_marketplace_sha(marketplace, head_sha):
                PLUGIN_MARKETPLACE_PATH.write_text(
                    json.dumps(marketplace, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                )
                result["pinned"] = True
        except RuntimeError as exc:
            result["error"] = str(exc)

    write_plugin_manifest(load_plugin_manifest())
    PLUGIN_INDEX_PATH.write_text(render_index(marketplace), encoding="utf-8")

    skills = discover_skills()
    commands = discover_commands()
    result["skills"] = len(skills)
    result["commands"] = len(commands)
    return result


def get_status_summary(marketplace: dict[str, Any]) -> dict[str, Any]:
    """Lightweight status for dashboard / status commands."""
    return {
        "skills": len(discover_skills()),
        "commands": len(discover_commands()),
        "pinned_sha": catalog_pinned_sha(marketplace),
    }
