#!/usr/bin/env python3
"""Generate .grok-plugin/plugin-index.json for the Cinematic Studio marketplace."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_ROOT = REPO_ROOT / ".grok" / "skills"
COMMANDS_ROOT = REPO_ROOT / "commands"
PLUGIN_DIR = REPO_ROOT / ".grok-plugin"
INDEX_PATH = PLUGIN_DIR / "plugin-index.json"
MANIFEST_PATH = PLUGIN_DIR / "plugin.json"
MARKETPLACE_PATH = PLUGIN_DIR / "marketplace.json"

MAX_DESCRIPTION_LEN = 120


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8", errors="replace")
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
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    return fields


def clean(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > MAX_DESCRIPTION_LEN:
        return text[: MAX_DESCRIPTION_LEN - 1].rstrip() + "…"
    return text


def discover_commands() -> list[dict[str, str]]:
    if not COMMANDS_ROOT.is_dir():
        return []
    items: list[dict[str, str]] = []
    for path in sorted(COMMANDS_ROOT.glob("*.md")):
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


def discover_skills() -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for skill_dir in sorted(SKILLS_ROOT.iterdir()):
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


def skill_paths() -> list[str]:
    return [
        f".grok/skills/{skill_dir.name}"
        for skill_dir in sorted(SKILLS_ROOT.iterdir())
        if (skill_dir / "SKILL.md").is_file()
    ]


def command_paths() -> list[str]:
    if not COMMANDS_ROOT.is_dir():
        return []
    return [
        f"commands/{path.name}"
        for path in sorted(COMMANDS_ROOT.glob("*.md"))
        if not path.stem.startswith("_")
    ]


def load_plugin_manifest() -> dict:
    if MANIFEST_PATH.exists():
        data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
    return {}


def write_plugin_manifest(manifest: dict) -> None:
    manifest["skills"] = skill_paths()
    commands = command_paths()
    if commands:
        manifest["commands"] = commands
    elif "commands" in manifest:
        del manifest["commands"]
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_index() -> dict:
    marketplace = json.loads(MARKETPLACE_PATH.read_text(encoding="utf-8"))
    plugins = marketplace.get("plugins", [])
    records: dict[str, dict] = {}
    skills = discover_skills()
    commands = discover_commands()
    for entry in plugins:
        if not isinstance(entry, dict):
            continue
        plugin_name = entry.get("name")
        if not isinstance(plugin_name, str) or not plugin_name:
            continue
        components: dict[str, list] = {"skills": skills}
        if commands:
            components["commands"] = commands
        records[plugin_name] = {"components": components}
    return {"version": 1, "plugins": records}


def main() -> int:
    if not MARKETPLACE_PATH.exists():
        print(f"ERROR: missing {MARKETPLACE_PATH}", file=sys.stderr)
        return 1

    manifest = load_plugin_manifest()
    write_plugin_manifest(manifest)

    index = build_index()
    rendered = json.dumps(index, indent=2, ensure_ascii=False) + "\n"

    if "--check" in sys.argv:
        if not INDEX_PATH.exists():
            print("ERROR: plugin-index.json is missing; run without --check", file=sys.stderr)
            return 1
        current = INDEX_PATH.read_text(encoding="utf-8")
        if current != rendered:
            print("ERROR: plugin-index.json is stale; run scripts/generate_plugin_index.py", file=sys.stderr)
            return 1
        print("plugin-index.json is up to date")
        return 0

    INDEX_PATH.write_text(rendered, encoding="utf-8")
    skills = discover_skills()
    commands = discover_commands()
    print(f"Wrote {INDEX_PATH} ({len(skills)} skills, {len(commands)} commands)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())