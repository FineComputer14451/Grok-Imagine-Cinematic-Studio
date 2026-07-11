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

from plugin_packs import (
    FULL_PLUGIN_NAME,
    PACK_IDS,
    all_pack_plugin_names,
    load_plugin_packs,
    resolve_pack_command_paths,
    resolve_pack_skill_paths,
    validate_plugin_packs,
)
from studio_paths import (
    COMMANDS_DIR,
    PLUGIN_DIR,
    PLUGIN_INDEX_PATH,
    PLUGIN_MANIFEST_PATH,
    PLUGIN_MARKETPLACE_PATH,
    PLUGIN_PACKS_DIR,
    SKILLS_DIR,
    STUDIO_ROOT,
)

REPO_GIT_URL = "https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio.git"
MAX_DESCRIPTION_LEN = 120
SHA_RE = re.compile(r"^[0-9a-f]{40}$")

# Paths allowed to change after the install pin without requiring a re-pin.
# A pin-only commit updates marketplace + index (and sometimes the manifest)
# while the marketplace ``sha`` still points at the content revision.
# Pack manifests under .grok-plugin/packs/*/plugin.json are also allowed
# via _is_allowed_post_pin_path (prefix match, not only this frozenset).
ALLOWED_POST_PIN_PATHS = frozenset(
    {
        ".grok-plugin/marketplace.json",
        ".grok-plugin/plugin-index.json",
        ".grok-plugin/plugin.json",
    }
)


def _studio_version() -> str:
    vf = STUDIO_ROOT / "VERSION"
    if vf.is_file():
        return vf.read_text(encoding="utf-8").strip()
    return "0.0.0"


def _is_allowed_post_pin_path(path: str) -> bool:
    if path in ALLOWED_POST_PIN_PATHS:
        return True
    if path.startswith(".grok-plugin/packs/") and path.endswith("/plugin.json"):
        return True
    return False


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


def git_commit_exists(sha: str) -> bool:
    """True if sha names a commit object in this repo."""
    if not SHA_RE.match(sha):
        return False
    result = subprocess.run(
        ["git", "cat-file", "-t", sha],
        cwd=STUDIO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0 and result.stdout.strip() == "commit"


def git_is_ancestor(ancestor: str, descendant: str) -> bool:
    """True if ancestor is an ancestor of descendant (or equal)."""
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=STUDIO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def git_diff_names(base: str, head: str) -> list[str]:
    """Return paths changed between base and head (name-only)."""
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base}..{head}"],
        cwd=STUDIO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


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


# Production-department taxonomy for declutter / catalog browsing only.
# Flat skill dirs under .grok/skills/ remain the install layout (plugin format).
SKILL_TAXONOMY: dict[str, tuple[str, ...]] = {
    "Core / Orchestration": (
        "grok-imagine-cinematic-studio",
        "studio-director",
        "mega-production-architect",
        "production-bible-workflow",
        "cinematic-studio-meta-installer",
        "skill-agent-architect",
        "github-repo-manager",
    ),
    "Camera & Image": (
        "director-of-photography",
        "director-of-photography-v3-3",
        "imagine-prompt-master",
        "i2i-cinematic-refiner",
        "i2i-refiner",
        "ai-image-recreation",
        "key-art-poster-designer",
        "reference-asset-curator",
    ),
    "Identity & Continuity": (
        "character-dna-extractor",
        "identity-lock-specialist",
        "multi-character-identity-arbiter",
        "continuity-consistency-guardian",
        "performance-emotion-director",
        "production-designer-set-decorator",
    ),
    "Sequence & Narrative": (
        "sequence-director",
        "cinematic-sequence-extender",
        "narrative-arc-pacing-strategist",
        "arc-replan-copilot",
        "animatic-director",
        "image-to-video-specialist",
        "trailer-teaser-director",
    ),
    "Audio": (
        "sonic-architect-native-audio-virtuoso",
        "foley-sound-design-specialist",
        "localization-subtitle-specialist",
    ),
    "Action & VFX": (
        "stunt-action-choreographer",
        "vfx-sfx-supervisor",
    ),
    "Batch & Quota": (
        "workflow-quota-optimizer",
        "sfw-batch-orchestrator",
        "nsfw-quota-orchestrator",
    ),
    "NSFW (explicit activation)": (
        "erosforge-nsfw-director",
        "nsfw-sequence-extender",
        "nsfw-chain-qa-protocol",
    ),
    "QA, Handoff & Delivery": (
        "quality-assurance-guardian",
        "chain-qa-protocol",
        "handoff-packet-validator",
        "imagine-execution-bridge",
        "assembly-editor",
        "post-production-color-grading-supervisor",
        "ai-polish-director",
        "ai-video-upscaler",
        "cinematic-ffmpeg",
    ),
}


def skill_taxonomy_groups(skill_names: list[str] | None = None) -> dict[str, list[str]]:
    """Return ordered taxonomy groups for the given skill names (or all known)."""
    names = set(skill_names if skill_names is not None else [])
    if skill_names is None:
        names = {s["name"] for s in discover_skills()}

    grouped: dict[str, list[str]] = {}
    claimed: set[str] = set()
    for group, members in SKILL_TAXONOMY.items():
        present = [m for m in members if m in names]
        grouped[group] = present
        claimed.update(present)

    other = sorted(n for n in names if n not in claimed)
    if other:
        grouped["Other / uncategorized"] = other
    return grouped


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
    """Legacy full-suite rebuild from disk discovery (sorted paths).

    Prefer :func:`build_full_plugin_manifest_from_packs` for catalog writes.
    """
    updated = dict(manifest)
    updated["skills"] = skill_paths()
    commands = command_paths()
    if commands:
        updated["commands"] = commands
    elif "commands" in updated:
        del updated["commands"]
    return updated


def build_pack_plugin_manifest(cfg: dict[str, Any], pack_id: str) -> dict[str, Any]:
    """Build a satellite pack plugin.json from packs config."""
    pack = cfg["packs"][pack_id]
    description = pack.get("description") or pack.get("display_name") or pack_id
    if isinstance(description, str):
        description = description.strip()
    manifest: dict[str, Any] = {
        "name": pack["name"],
        "version": _studio_version(),
        "description": description,
        "author": {
            "name": "FineComputer14451",
            "url": "https://github.com/FineComputer14451",
        },
        "homepage": "https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio",
        "repository": "https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio",
        "license": "MIT",
        "keywords": ["grok-imagine-cinematic-studio", pack_id, "cinematic studio"],
        "skills": resolve_pack_skill_paths(list(pack["skills"])),
    }
    cmds = list(pack.get("commands") or [])
    if cmds:
        manifest["commands"] = resolve_pack_command_paths(cmds)
    if pack.get("requires"):
        manifest["cinematicStudioRequires"] = list(pack["requires"])
    return manifest


def build_full_plugin_manifest_from_packs(
    cfg: dict[str, Any], base: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Full suite = union of pack skills + commands; preserve author fields from base."""
    base = dict(base or load_plugin_manifest())
    all_skills: list[str] = []
    all_cmds: list[str] = []
    for pid in PACK_IDS:
        all_skills.extend(cfg["packs"][pid]["skills"])
        all_cmds.extend(cfg["packs"][pid].get("commands") or [])
    base["name"] = FULL_PLUGIN_NAME
    base["version"] = _studio_version()
    base["skills"] = resolve_pack_skill_paths(all_skills)
    if all_cmds:
        base["commands"] = resolve_pack_command_paths(all_cmds)
    elif "commands" in base:
        del base["commands"]
    return base


def build_marketplace_from_packs(
    cfg: dict[str, Any], sha: str | None = None
) -> dict[str, Any]:
    """Build a six-plugin marketplace (full suite + five packs), shared SHA."""
    errs = validate_plugin_packs(cfg)
    if errs:
        raise ValueError("invalid plugin packs: " + "; ".join(errs))
    pin = sha
    plugins: list[dict[str, Any]] = []

    def entry(name: str, description: str, **extra: Any) -> dict[str, Any]:
        source: dict[str, Any] = {
            "source": "url",
            "url": REPO_GIT_URL,
        }
        if pin:
            source["sha"] = pin
        desc = description.strip() if isinstance(description, str) else description
        e: dict[str, Any] = {
            "name": name,
            "description": desc,
            "category": "creative",
            "version": _studio_version(),
            "source": source,
            "homepage": "https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio",
            "keywords": ["grok-imagine-cinematic-studio", "cinematic studio"],
        }
        e.update(extra)
        return e

    full = cfg["full_plugin"]
    plugins.append(
        entry(
            full["name"],
            full.get("description") or "Full Cinematic Studio suite",
            recommended=True,
        )
    )
    for pid in PACK_IDS:
        pack = cfg["packs"][pid]
        plugins.append(
            entry(
                pack["name"],
                pack.get("description") or pack.get("display_name") or pid,
                pack_id=pid,
                requires=list(pack.get("requires") or []),
            )
        )
    version = _studio_version()
    return {
        "name": "finecomputer14451-cinematic-studio",
        "description": (
            f"Grok Imagine Cinematic Studio v{version} marketplace — "
            "full suite + modular packs (core, camera-image, sequence-narrative, "
            "nsfw, delivery-post)."
        ),
        "owner": {
            "name": "FineComputer14451",
            "url": "https://github.com/FineComputer14451",
        },
        "plugins": plugins,
    }


def build_index_from_packs(
    marketplace: dict[str, Any], cfg: dict[str, Any]
) -> dict[str, Any]:
    """Per-plugin skill/command components (not a global dump for every entry)."""
    skills_by_name = {s["name"]: s for s in discover_skills()}
    cmds_by_name = {c["name"]: c for c in discover_commands()}
    records: dict[str, dict[str, Any]] = {}

    full_skills: list[dict[str, str]] = []
    full_cmds: list[dict[str, str]] = []
    for pid in PACK_IDS:
        for s in cfg["packs"][pid]["skills"]:
            if s in skills_by_name:
                full_skills.append(skills_by_name[s])
        for c in cfg["packs"][pid].get("commands") or []:
            if c in cmds_by_name:
                full_cmds.append(cmds_by_name[c])
    full_name = cfg["full_plugin"]["name"]
    records[full_name] = {
        "components": {
            "skills": full_skills,
            **({"commands": full_cmds} if full_cmds else {}),
        }
    }

    for pid in PACK_IDS:
        pack = cfg["packs"][pid]
        sk = [skills_by_name[s] for s in pack["skills"] if s in skills_by_name]
        cm = [
            cmds_by_name[c]
            for c in (pack.get("commands") or [])
            if c in cmds_by_name
        ]
        rec: dict[str, Any] = {"components": {"skills": sk}}
        if cm:
            rec["components"]["commands"] = cm
        records[pack["name"]] = rec

    for market_entry in marketplace.get("plugins") or []:
        if not isinstance(market_entry, dict):
            continue
        name = market_entry.get("name")
        if isinstance(name, str) and name in records:
            sha = pinned_sha(market_entry)
            if sha:
                records[name]["sha"] = sha

    return {"version": 1, "plugins": records}


def write_pack_manifests(cfg: dict[str, Any]) -> list[Path]:
    """Write .grok-plugin/packs/<id>/plugin.json for each satellite pack."""
    written: list[Path] = []
    PLUGIN_PACKS_DIR.mkdir(parents=True, exist_ok=True)
    for pid in PACK_IDS:
        out_dir = PLUGIN_PACKS_DIR / pid
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "plugin.json"
        manifest = build_pack_plugin_manifest(cfg, pid)
        path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        written.append(path)
    return written


def render_plugin_manifest(manifest: dict[str, Any]) -> str:
    return json.dumps(build_plugin_manifest(manifest), indent=2, ensure_ascii=False) + "\n"


def write_plugin_manifest(manifest: dict[str, Any]) -> None:
    PLUGIN_MANIFEST_PATH.write_text(render_plugin_manifest(manifest), encoding="utf-8")


def render_index(marketplace: dict[str, Any], cfg: dict[str, Any] | None = None) -> str:
    if cfg is None:
        try:
            cfg = load_plugin_packs()
        except Exception:
            return json.dumps(build_index(marketplace), indent=2, ensure_ascii=False) + "\n"
    return (
        json.dumps(build_index_from_packs(marketplace, cfg), indent=2, ensure_ascii=False)
        + "\n"
    )


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
    """Return list of error messages for release pin check.

    A valid release pin means the marketplace install SHA points at the content
    revision that should be installed. That SHA is almost never the tip commit
    after a pin-only follow-up (a commit cannot contain its own hash in
    marketplace.json). Accepted states:

    1. ``catalog_sha == HEAD`` — pin just applied, not yet committed (or pin
       commit somehow matches, rare).
    2. ``catalog_sha`` is an ancestor of HEAD **and** every path changed from
       catalog_sha..HEAD is in ``ALLOWED_POST_PIN_PATHS`` — normal pin-only
       commit(s) on top of the content revision.

    Any skill/code/doc change after the pin fails and requires re-pin.
    """
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

    if not git_commit_exists(catalog_sha):
        errors.append(
            f"marketplace pin {catalog_sha} is not a commit in this repository"
        )
        return errors

    if catalog_sha == head_sha:
        return errors

    if not git_is_ancestor(catalog_sha, head_sha):
        errors.append(
            f"marketplace pin {catalog_sha} is not an ancestor of HEAD {head_sha}; "
            f"re-run: cinematic-studio plugin catalog pin"
        )
        return errors

    changed = git_diff_names(catalog_sha, head_sha)
    extra = sorted({p for p in changed if not _is_allowed_post_pin_path(p)})
    if extra:
        preview = ", ".join(extra[:8])
        more = f" (+{len(extra) - 8} more)" if len(extra) > 8 else ""
        errors.append(
            f"content changed after marketplace pin {catalog_sha[:12]}… "
            f"without re-pin (HEAD {head_sha[:12]}…). "
            f"Non-catalog paths: {preview}{more}. "
            f"Re-run: cinematic-studio plugin catalog pin, then commit only "
            f".grok-plugin/ on top of the content revision."
        )
    return errors


def check_plugin_artifacts(
    marketplace: dict[str, Any], *, require_release_pin: bool = False
) -> list[str]:
    """Full artifact freshness + pin validation. Returns list of errors."""
    errors: list[str] = []

    cfg: dict[str, Any] | None = None
    try:
        cfg = load_plugin_packs()
        pack_errors = validate_plugin_packs(cfg)
        if pack_errors:
            errors.extend(pack_errors)
    except Exception as exc:
        errors.append(f"plugin packs config: {exc}")

    pin_errors = validate_marketplace_pins(marketplace)
    if pin_errors:
        errors.extend(pin_errors)

    if require_release_pin:
        release_errors = validate_release_pin(marketplace)
        if release_errors:
            errors.extend(release_errors)

    plugins = marketplace.get("plugins") or []
    if len(plugins) != 6:
        errors.append(f"marketplace must list 6 plugins, found {len(plugins)}")
    elif cfg is not None:
        expected_names = all_pack_plugin_names(cfg)
        actual_names = [
            p.get("name") for p in plugins if isinstance(p, dict)
        ]
        if actual_names != expected_names:
            errors.append(
                "marketplace plugin order/names mismatch expected pack set: "
                f"got {actual_names}, want {expected_names}"
            )

    if not PLUGIN_MANIFEST_PATH.exists():
        errors.append(f"{PLUGIN_MANIFEST_PATH} is missing")
    elif cfg is not None:
        expected_full = (
            json.dumps(
                build_full_plugin_manifest_from_packs(cfg, base=load_plugin_manifest()),
                indent=2,
                ensure_ascii=False,
            )
            + "\n"
        )
        if PLUGIN_MANIFEST_PATH.read_text(encoding="utf-8") != expected_full:
            errors.append("plugin.json is stale")

    if cfg is not None:
        for pid in PACK_IDS:
            path = PLUGIN_PACKS_DIR / pid / "plugin.json"
            if not path.is_file():
                errors.append(f"pack manifest missing: .grok-plugin/packs/{pid}/plugin.json")
                continue
            expected_pack = (
                json.dumps(
                    build_pack_plugin_manifest(cfg, pid),
                    indent=2,
                    ensure_ascii=False,
                )
                + "\n"
            )
            if path.read_text(encoding="utf-8") != expected_pack:
                errors.append(f"pack plugin.json is stale: packs/{pid}/plugin.json")

    if not PLUGIN_INDEX_PATH.exists():
        errors.append(f"{PLUGIN_INDEX_PATH} is missing")
    elif cfg is not None:
        expected_index = (
            json.dumps(
                build_index_from_packs(marketplace, cfg),
                indent=2,
                ensure_ascii=False,
            )
            + "\n"
        )
        if PLUGIN_INDEX_PATH.read_text(encoding="utf-8") != expected_index:
            errors.append("plugin-index.json is stale")

    return errors


def write_artifacts(marketplace: dict[str, Any], *, sync_sha: bool = False) -> dict[str, Any]:
    """Write pack-aware marketplace, full + satellite manifests, and index.

    When ``sync_sha`` is True, pin all marketplace entries to current HEAD.
    When False, preserve the existing catalog pin SHA (if any) across all six
    plugin entries.
    """
    result: dict[str, Any] = {"pinned": False, "sha": None}

    try:
        cfg = load_plugin_packs()
    except Exception as exc:
        result["error"] = str(exc)
        return result

    pack_errors = validate_plugin_packs(cfg)
    if pack_errors:
        result["error"] = "invalid plugin packs: " + "; ".join(pack_errors)
        return result

    pin_sha: str | None = None
    if sync_sha:
        try:
            pin_sha = git_head_sha()
            result["sha"] = pin_sha
            result["pinned"] = True
        except RuntimeError as exc:
            result["error"] = str(exc)
            pin_sha = catalog_pinned_sha(marketplace)
    else:
        pin_sha = catalog_pinned_sha(marketplace)
        result["sha"] = pin_sha

    new_market = build_marketplace_from_packs(cfg, sha=pin_sha)

    # If caller passed a marketplace and we only need to sync SHA into an
    # already multi-plugin market, rebuild-from-packs is still authoritative.
    full_manifest = build_full_plugin_manifest_from_packs(
        cfg, base=load_plugin_manifest()
    )
    PLUGIN_MANIFEST_PATH.write_text(
        json.dumps(full_manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    written_packs = write_pack_manifests(cfg)
    result["pack_manifests"] = len(written_packs)

    PLUGIN_MARKETPLACE_PATH.write_text(
        json.dumps(new_market, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    index = build_index_from_packs(new_market, cfg)
    PLUGIN_INDEX_PATH.write_text(
        json.dumps(index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    # Keep in-memory marketplace in sync for callers that reuse the dict.
    marketplace.clear()
    marketplace.update(new_market)

    skills = discover_skills()
    commands = discover_commands()
    result["skills"] = len(skills)
    result["commands"] = len(commands)
    result["plugins"] = len(new_market.get("plugins", []))
    return result


def get_status_summary(marketplace: dict[str, Any]) -> dict[str, Any]:
    """Lightweight status for dashboard / status commands."""
    return {
        "skills": len(discover_skills()),
        "commands": len(discover_commands()),
        "pinned_sha": catalog_pinned_sha(marketplace),
    }
