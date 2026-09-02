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
NSFW_MANIFEST_PATH = PLUGIN_DIR / "nsfw-plugin.json"
MARKETPLACE_PATH = PLUGIN_DIR / "marketplace.json"

MAX_DESCRIPTION_LEN = 120

NSFW_SKILL_DIR_NAMES = {
    "erosforge-nsfw-director",
    "nsfw-quota-orchestrator",
    "nsfw-sequence-extender",
    "nsfw-chain-qa-protocol",
}
NSFW_COMMAND_NAMES = {"nsfw"}


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


def _is_nsfw_skill(name: str) -> bool:
    return name in NSFW_SKILL_DIR_NAMES


def _is_nsfw_command(name: str) -> bool:
    return name in NSFW_COMMAND_NAMES


def _nsfw_plugin_name(name: str) -> bool:
    return "nsfw" in (name or "").lower()


def discover_commands(*, nsfw: bool = False) -> list[dict[str, str]]:
    if not COMMANDS_ROOT.is_dir():
        return []
    items: list[dict[str, str]] = []
    for path in sorted(COMMANDS_ROOT.glob("*.md")):
        if path.stem.startswith("_"):
            continue
        if _is_nsfw_command(path.stem) != nsfw:
            continue
        frontmatter = parse_frontmatter(path)
        items.append(
            {
                "name": path.stem,
                "description": clean(frontmatter.get("description", "")),
            }
        )
    return items


def discover_skills(*, nsfw: bool = False) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for skill_dir in sorted(SKILLS_ROOT.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue
        if _is_nsfw_skill(skill_dir.name) != nsfw:
            continue
        frontmatter = parse_frontmatter(skill_md)
        items.append(
            {
                "name": frontmatter.get("name") or skill_dir.name,
                "description": clean(frontmatter.get("description", "")),
            }
        )
    return items


def skill_paths(*, nsfw: bool = False) -> list[str]:
    return [
        f".grok/skills/{skill_dir.name}"
        for skill_dir in sorted(SKILLS_ROOT.iterdir())
        if (skill_dir / "SKILL.md").is_file() and _is_nsfw_skill(skill_dir.name) == nsfw
    ]


def command_paths(*, nsfw: bool = False) -> list[str]:
    if not COMMANDS_ROOT.is_dir():
        return []
    return [
        f"commands/{path.name}"
        for path in sorted(COMMANDS_ROOT.glob("*.md"))
        if not path.stem.startswith("_") and _is_nsfw_command(path.stem) == nsfw
    ]


def load_plugin_manifest() -> dict:
    if MANIFEST_PATH.exists():
        data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
    return {}


def write_plugin_manifest(manifest: dict) -> None:
    manifest["skills"] = skill_paths(nsfw=False)
    commands = command_paths(nsfw=False)
    if commands:
        manifest["commands"] = commands
    elif "commands" in manifest:
        del manifest["commands"]
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_nsfw_plugin_manifest() -> None:
    payload = {
        "name": "grok-imagine-cinematic-studio-nsfw",
        "version": load_plugin_manifest().get("version", "3.6.5"),
        "description": (
            "Optional 18+ R-rated fictional-adult add-on. Requires local AUP attestation. "
            "Not affiliated with xAI or SpaceXAI. Policy: https://x.ai/legal/acceptable-use-policy"
        ),
        "aup_required": True,
        "aup_url": "https://x.ai/legal/acceptable-use-policy",
        "license": "MIT",
        "skills": skill_paths(nsfw=True),
        "commands": command_paths(nsfw=True),
    }
    NSFW_MANIFEST_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_index() -> dict:
    marketplace = json.loads(MARKETPLACE_PATH.read_text(encoding="utf-8"))
    plugins = marketplace.get("plugins", [])
    records: dict[str, dict] = {}
    for entry in plugins:
        if not isinstance(entry, dict):
            continue
        plugin_name = entry.get("name")
        if not isinstance(plugin_name, str) or not plugin_name:
            continue
        nsfw = _nsfw_plugin_name(plugin_name)
        skills = discover_skills(nsfw=nsfw)
        commands = discover_commands(nsfw=nsfw)
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
    write_nsfw_plugin_manifest()

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
    print(
        f"Wrote {INDEX_PATH} ({len(skills)} SFW skills, {len(commands)} SFW commands); "
        f"NSFW add-on → {NSFW_MANIFEST_PATH}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())