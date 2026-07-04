#!/usr/bin/env python3
"""Generate .grok-plugin/plugin-index.json for the Cinematic Studio marketplace."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_ROOT = REPO_ROOT / ".grok" / "skills"
COMMANDS_ROOT = REPO_ROOT / "commands"
PLUGIN_DIR = REPO_ROOT / ".grok-plugin"
INDEX_PATH = PLUGIN_DIR / "plugin-index.json"
MANIFEST_PATH = PLUGIN_DIR / "plugin.json"
MARKETPLACE_PATH = PLUGIN_DIR / "marketplace.json"
REPO_GIT_URL = "https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio.git"

MAX_DESCRIPTION_LEN = 120
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


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


def git_head_sha() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    sha = result.stdout.strip() if result.returncode == 0 else ""
    if not SHA_RE.match(sha):
        raise RuntimeError("unable to resolve current git HEAD sha for marketplace pin")
    return sha


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


def build_plugin_manifest(manifest: dict) -> dict:
    updated = dict(manifest)
    updated["skills"] = skill_paths()
    commands = command_paths()
    if commands:
        updated["commands"] = commands
    elif "commands" in updated:
        del updated["commands"]
    return updated


def render_plugin_manifest(manifest: dict) -> str:
    return json.dumps(build_plugin_manifest(manifest), indent=2, ensure_ascii=False) + "\n"


def write_plugin_manifest(manifest: dict) -> None:
    MANIFEST_PATH.write_text(render_plugin_manifest(manifest), encoding="utf-8")


def render_index(marketplace: dict) -> str:
    return json.dumps(build_index(marketplace), indent=2, ensure_ascii=False) + "\n"


def sync_marketplace_sha(marketplace: dict, sha: str) -> bool:
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


def pinned_sha(entry: dict) -> str | None:
    source = entry.get("source")
    if not isinstance(source, dict):
        return None
    sha = source.get("sha")
    return sha if isinstance(sha, str) and SHA_RE.match(sha) else None


def build_index(marketplace: dict) -> dict:
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
        record: dict[str, object] = {
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


def catalog_pinned_sha(marketplace: dict) -> str | None:
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


def validate_marketplace_pins(marketplace: dict) -> bool:
    for entry in marketplace.get("plugins", []):
        if pinned_sha(entry) is None:
            print("ERROR: marketplace plugin entry missing pinned sha", file=sys.stderr)
            return False
    return True


def validate_release_pin(marketplace: dict) -> bool:
    try:
        head_sha = git_head_sha()
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return False

    catalog_sha = catalog_pinned_sha(marketplace)
    if catalog_sha is None:
        print("ERROR: marketplace catalog missing pinned sha for this repo", file=sys.stderr)
        return False
    if catalog_sha != head_sha:
        print(
            "ERROR: marketplace sha does not match git HEAD; "
            "run scripts/release_plugin_catalog.sh and commit catalog files in this commit",
            file=sys.stderr,
        )
        print(f"       catalog: {catalog_sha}", file=sys.stderr)
        print(f"       HEAD:    {head_sha}", file=sys.stderr)
        return False
    return True


def run_check(marketplace: dict, *, require_release_pin: bool = False) -> int:
    if not validate_marketplace_pins(marketplace):
        return 1
    if require_release_pin and not validate_release_pin(marketplace):
        return 1

    if not MANIFEST_PATH.exists():
        print(f"ERROR: {MANIFEST_PATH} is missing; run scripts/generate_plugin_index.py", file=sys.stderr)
        return 1
    expected_manifest = render_plugin_manifest(load_plugin_manifest())
    if MANIFEST_PATH.read_text(encoding="utf-8") != expected_manifest:
        print("ERROR: plugin.json is stale; run scripts/generate_plugin_index.py", file=sys.stderr)
        return 1

    if not INDEX_PATH.exists():
        print("ERROR: plugin-index.json is missing; run scripts/generate_plugin_index.py", file=sys.stderr)
        return 1
    if INDEX_PATH.read_text(encoding="utf-8") != render_index(marketplace):
        print("ERROR: plugin-index.json is stale; run scripts/generate_plugin_index.py", file=sys.stderr)
        return 1

    if require_release_pin:
        print("marketplace catalog pinned to HEAD; plugin.json and plugin-index.json are up to date")
    else:
        print("marketplace.json, plugin.json, and plugin-index.json are up to date")
    return 0


def run_write(marketplace: dict, *, sync_sha: bool) -> int:
    if sync_sha:
        head_sha = git_head_sha()
        if sync_marketplace_sha(marketplace, head_sha):
            MARKETPLACE_PATH.write_text(
                json.dumps(marketplace, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        print(f"Pinned marketplace sha: {head_sha}")

    write_plugin_manifest(load_plugin_manifest())
    INDEX_PATH.write_text(render_index(marketplace), encoding="utf-8")

    skills = discover_skills()
    commands = discover_commands()
    print(f"Wrote {INDEX_PATH} ({len(skills)} skills, {len(commands)} commands)")
    if not sync_sha:
        print("Tip: run with --sync-sha before release to pin marketplace catalog to HEAD")
    return 0


def main() -> int:
    if not MARKETPLACE_PATH.exists():
        print(f"ERROR: missing {MARKETPLACE_PATH}", file=sys.stderr)
        return 1

    marketplace = json.loads(MARKETPLACE_PATH.read_text(encoding="utf-8"))
    check_mode = "--check" in sys.argv
    sync_sha = "--sync-sha" in sys.argv
    release_mode = "--release" in sys.argv

    if check_mode and sync_sha:
        print("ERROR: --check and --sync-sha are mutually exclusive", file=sys.stderr)
        return 1
    if release_mode and not check_mode:
        print("ERROR: --release requires --check", file=sys.stderr)
        return 1
    if release_mode and sync_sha:
        print("ERROR: --release and --sync-sha are mutually exclusive", file=sys.stderr)
        return 1

    if check_mode:
        return run_check(marketplace, require_release_pin=release_mode)
    return run_write(marketplace, sync_sha=sync_sha)


if __name__ == "__main__":
    raise SystemExit(main())