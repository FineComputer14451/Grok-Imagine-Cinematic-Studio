# Plugin Modularity Packs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship hybrid+additive marketplace modularity — full suite plus five satellite packs from one skill tree, with manifest-only filters, domain-mapped commands, and `full_suite_wins` declutter.

**Architecture:** `config/plugin_packs.yaml` is the single selector source. `tools/plugin_catalog.py` loads/validates packs, generates full + pack `plugin.json` manifests, a six-entry `marketplace.json`, and a per-plugin `plugin-index.json`. Declutter extends Method A/B cleanup with full-suite-vs-satellite skill dedupe under `~/.grok/installed-plugins/`.

**Tech Stack:** Python 3.11+, PyYAML (or stdlib-only JSON if YAML avoided — prefer PyYAML if already in requirements; else author packs as JSON), existing Typer CLI, bash declutter, pytest.

**Design:** [docs/development/superpowers/specs/2026-07-11-plugin-modularity-packs-design.md](../specs/2026-07-11-plugin-modularity-packs-design.md)

**Target version:** 3.8.0

---

## File map

| File | Responsibility |
|------|----------------|
| `config/plugin_packs.yaml` | Pack membership + declutter policy (source of truth) |
| `tools/plugin_packs.py` | Load, validate, resolve skill/command paths for packs (pure logic) |
| `tools/plugin_catalog.py` | Generate/write multi-plugin artifacts; pin/check integration |
| `tools/studio_paths.py` | Paths for packs YAML + packs output dir |
| `tools/cli/plugin_commands.py` | `plugin list --packs`, catalog generate/check awareness |
| `scripts/lib/cinematic_studio_common.sh` | `full_suite_wins` declutter against satellite plugin dirs |
| `tests/test_plugin_packs.py` | Membership, exclusivity, union, generate |
| `tests/test_plugin_catalog_pin.py` | Multi-plugin pin still valid |
| `.grok-plugin/plugin.json` | Full suite (generated) |
| `.grok-plugin/packs/<id>/plugin.json` | Satellite manifests (generated) |
| `.grok-plugin/marketplace.json` | Six plugins, shared SHA |
| `.grok-plugin/plugin-index.json` | Per-plugin skill/command lists |
| Docs / VERSION / CHANGELOG | User-facing install matrix |

**Do not** copy skill file bodies. Paths in pack manifests stay repo-root relative: `.grok/skills/<name>`, `commands/<stem>.md`.

---

## Principles

1. Full suite remains recommended; pack names are satellites only.
2. Generator **hard-fails** on dual membership, unknown skills, or union ≠ 48.
3. `plugin-index.json` must list **pack-filtered** skills, not the full 48 for every entry.
4. Pin protocol: all six marketplace entries share the same content SHA; post-pin allowlist may include `.grok-plugin/packs/**/plugin.json`.
5. TDD: tests first for pack validation and generation.

---

## Task 0: Baseline + paths

**Files:**
- Modify: `tools/studio_paths.py`
- Test: none yet (path constants only)

- [ ] **Step 1: Add path constants**

```python
# tools/studio_paths.py — append after PLUGIN_MARKETPLACE_PATH
PLUGIN_PACKS_CONFIG = STUDIO_ROOT / "config" / "plugin_packs.yaml"
PLUGIN_PACKS_DIR = PLUGIN_DIR / "packs"
```

- [ ] **Step 2: Commit**

```bash
git add tools/studio_paths.py
git commit -m "chore(paths): add plugin packs config and packs dir constants"
```

---

## Task 1: Packs config + pure loader (TDD)

**Files:**
- Create: `config/plugin_packs.yaml`
- Create: `tools/plugin_packs.py`
- Create: `tests/test_plugin_packs.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_plugin_packs.py
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from plugin_packs import (  # noqa: E402
    FULL_PLUGIN_NAME,
    PACK_IDS,
    PackValidationError,
    load_plugin_packs,
    resolve_pack_skill_paths,
    validate_plugin_packs,
)


def test_load_and_validate_default_config() -> None:
    cfg = load_plugin_packs()
    errors = validate_plugin_packs(cfg)
    assert errors == []
    assert cfg["full_plugin"]["name"] == FULL_PLUGIN_NAME
    assert set(cfg["packs"].keys()) == set(PACK_IDS)


def test_skill_membership_exclusive_and_covers_disk() -> None:
    cfg = load_plugin_packs()
    # validate_plugin_packs already checks exclusivity + union vs discoverable skills
    assert validate_plugin_packs(cfg) == []
    union: list[str] = []
    for pid in PACK_IDS:
        union.extend(cfg["packs"][pid]["skills"])
    assert len(union) == len(set(union))
    assert len(union) == 48


def test_commands_domain_mapped() -> None:
    cfg = load_plugin_packs()
    assert "nsfw" in cfg["packs"]["nsfw"]["commands"]
    assert "delivery" in cfg["packs"]["delivery-post"]["commands"]
    assert "cinematic" in cfg["packs"]["core"]["commands"]
    # no command owned by two packs
    owned: dict[str, str] = {}
    for pid, pack in cfg["packs"].items():
        for cmd in pack.get("commands") or []:
            assert cmd not in owned, f"{cmd} in {owned[cmd]} and {pid}"
            owned[cmd] = pid


def test_resolve_paths_core() -> None:
    cfg = load_plugin_packs()
    paths = resolve_pack_skill_paths(cfg["packs"]["core"]["skills"])
    assert ".grok/skills/studio-director" in paths
    assert all(p.startswith(".grok/skills/") for p in paths)


def test_duplicate_skill_fails_validation() -> None:
    cfg = load_plugin_packs()
    # force dual membership
    cfg["packs"]["nsfw"]["skills"] = list(cfg["packs"]["nsfw"]["skills"]) + [
        cfg["packs"]["core"]["skills"][0]
    ]
    errs = validate_plugin_packs(cfg)
    assert errs
    assert any("duplicate" in e.lower() or "two packs" in e.lower() for e in errs)
```

- [ ] **Step 2: Run tests — expect fail (module missing)**

```bash
cd /home/kali/Grok-Imagine-Cinematic-Studio
pytest tests/test_plugin_packs.py -v
```

Expected: `ModuleNotFoundError: No module named 'plugin_packs'` or import errors.

- [ ] **Step 3: Author `config/plugin_packs.yaml`**

Use exact membership from the design (48 skills). Full text:

```yaml
version: "1"
# studio_version is advisory; generator may prefer VERSION file
full_plugin:
  name: grok-imagine-cinematic-studio
  recommended: true
  display_name: "Grok Imagine Cinematic Studio (Full Suite)"
  description: >-
    Full 23-agent cinematic suite — all skills and slash commands.
    Recommended one-click install.

packs:
  core:
    name: grok-imagine-cinematic-core
    display_name: "Cinematic Studio Core"
    description: >-
      Orchestration, DNA, Imagine runtime, QA, quota, and meta tools.
    requires: []
    skills:
      - grok-imagine-cinematic-studio
      - studio-director
      - mega-production-architect
      - production-bible-workflow
      - cinematic-studio-meta-installer
      - skill-agent-architect
      - github-repo-manager
      - character-dna-extractor
      - identity-lock-specialist
      - multi-character-identity-arbiter
      - imagine-prompt-master
      - imagine-execution-bridge
      - handoff-packet-validator
      - workflow-quota-optimizer
      - quality-assurance-guardian
      - chain-qa-protocol
    commands:
      - cinematic
      - dna
      - imagine
      - dashboard
      - validate
      - quota
      - intelligence
      - automation
      - sfw

  camera-image:
    name: grok-imagine-camera-image
    display_name: "Cinematic Studio Camera & Image"
    description: >-
      DoP, production design, i2i, key art, reference curator, and i2v specialist.
    requires: [core]
    skills:
      - director-of-photography
      - director-of-photography-v3-3
      - production-designer-set-decorator
      - i2i-cinematic-refiner
      - i2i-refiner
      - ai-image-recreation
      - key-art-poster-designer
      - reference-asset-curator
      - image-to-video-specialist
    commands: []

  sequence-narrative:
    name: grok-imagine-sequence-narrative
    display_name: "Cinematic Studio Sequence & Narrative"
    description: >-
      Long-form sequence, continuity, performance, audio, action/VFX, and SFW batches.
    requires: [core]
    skills:
      - sequence-director
      - cinematic-sequence-extender
      - narrative-arc-pacing-strategist
      - arc-replan-copilot
      - animatic-director
      - continuity-consistency-guardian
      - performance-emotion-director
      - trailer-teaser-director
      - sonic-architect-native-audio-virtuoso
      - foley-sound-design-specialist
      - localization-subtitle-specialist
      - stunt-action-choreographer
      - vfx-sfx-supervisor
      - sfw-batch-orchestrator
    commands: []

  nsfw:
    name: grok-imagine-nsfw
    display_name: "Cinematic Studio NSFW (Opt-in)"
    description: >-
      Explicit opt-in ErosForge + NSFW quota/sequence/chain QA. Requires user consent.
    requires: [core]
    skills:
      - erosforge-nsfw-director
      - nsfw-quota-orchestrator
      - nsfw-sequence-extender
      - nsfw-chain-qa-protocol
    commands:
      - nsfw

  delivery-post:
    name: grok-imagine-delivery-post
    display_name: "Cinematic Studio Delivery & Post"
    description: >-
      Assembly EDL, color grade, AI polish, upscale, and cinematic ffmpeg delivery.
    requires: [core]
    skills:
      - assembly-editor
      - post-production-color-grading-supervisor
      - ai-polish-director
      - ai-video-upscaler
      - cinematic-ffmpeg
    commands:
      - delivery

declutter:
  full_suite_plugin: grok-imagine-cinematic-studio
  policy: full_suite_wins
  satellite_plugin_names:
    - grok-imagine-cinematic-core
    - grok-imagine-camera-image
    - grok-imagine-sequence-narrative
    - grok-imagine-nsfw
    - grok-imagine-delivery-post
```

- [ ] **Step 4: Implement `tools/plugin_packs.py`**

```python
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
```

If `pyyaml` is not in `requirements.txt`, add `pyyaml>=6.0` to `requirements.txt` (or `requirements-dev.txt` if generation is dev-only — prefer main requirements because catalog pin runs in verify).

- [ ] **Step 5: Run tests — expect pass**

```bash
pytest tests/test_plugin_packs.py -v
```

Expected: all PASS.

- [ ] **Step 6: Commit**

```bash
git add config/plugin_packs.yaml tools/plugin_packs.py tests/test_plugin_packs.py requirements.txt
git commit -m "feat(plugins): pack config + validate exclusive membership (48 skills)"
```

---

## Task 2: Generate multi-plugin artifacts

**Files:**
- Modify: `tools/plugin_catalog.py`
- Modify: `tests/test_plugin_packs.py` (generation tests)
- Modify: `ALLOWED_POST_PIN_PATHS` for pack manifests

- [ ] **Step 1: Add failing generation tests**

```python
# append to tests/test_plugin_packs.py
from plugin_catalog import (  # noqa: E402
    build_marketplace_from_packs,
    build_pack_plugin_manifest,
    build_index_from_packs,
    render_plugin_manifest_for_subset,
)


def test_build_marketplace_has_six_plugins() -> None:
    cfg = load_plugin_packs()
    market = build_marketplace_from_packs(cfg, sha="a" * 40)
    names = [p["name"] for p in market["plugins"]]
    assert len(names) == 6
    assert FULL_PLUGIN_NAME in names
    assert names[0] == FULL_PLUGIN_NAME  # full suite first / recommended order
    for p in market["plugins"]:
        assert p["source"]["sha"] == "a" * 40
        assert p["source"]["url"].endswith("Grok-Imagine-Cinematic-Studio.git")


def test_pack_manifest_subset() -> None:
    cfg = load_plugin_packs()
    m = build_pack_plugin_manifest(cfg, "nsfw")
    assert m["name"] == "grok-imagine-nsfw"
    assert m["skills"] == [
        ".grok/skills/erosforge-nsfw-director",
        ".grok/skills/nsfw-quota-orchestrator",
        ".grok/skills/nsfw-sequence-extender",
        ".grok/skills/nsfw-chain-qa-protocol",
    ]
    assert m["commands"] == ["commands/nsfw.md"]


def test_index_per_plugin_not_global() -> None:
    cfg = load_plugin_packs()
    market = build_marketplace_from_packs(cfg, sha="b" * 40)
    index = build_index_from_packs(market, cfg)
    nsfw = index["plugins"]["grok-imagine-nsfw"]["components"]["skills"]
    names = {s["name"] for s in nsfw}
    assert names == {
        "erosforge-nsfw-director",
        "nsfw-quota-orchestrator",
        "nsfw-sequence-extender",
        "nsfw-chain-qa-protocol",
    }
    full = index["plugins"][FULL_PLUGIN_NAME]["components"]["skills"]
    assert len(full) == 48
```

- [ ] **Step 2: Run — expect fail (functions missing)**

```bash
pytest tests/test_plugin_packs.py::test_build_marketplace_has_six_plugins tests/test_plugin_packs.py::test_pack_manifest_subset tests/test_plugin_packs.py::test_index_per_plugin_not_global -v
```

- [ ] **Step 3: Implement generation helpers in `tools/plugin_catalog.py`**

Add imports and constants:

```python
from plugin_packs import (
    FULL_PLUGIN_NAME,
    PACK_IDS,
    load_plugin_packs,
    resolve_pack_command_paths,
    resolve_pack_skill_paths,
    validate_plugin_packs,
)
from studio_paths import PLUGIN_PACKS_DIR  # add to studio_paths import list
```

Extend allowlist:

```python
ALLOWED_POST_PIN_PATHS = frozenset(
    {
        ".grok-plugin/marketplace.json",
        ".grok-plugin/plugin-index.json",
        ".grok-plugin/plugin.json",
        # pack manifests are catalog-generated pin siblings
        # note: validate_release_pin uses exact path match — extend git_diff check
        # to allow any path under .grok-plugin/packs/ ending in plugin.json
    }
)
```

Update `validate_release_pin` extra-path filter:

```python
def _is_allowed_post_pin_path(path: str) -> bool:
    if path in ALLOWED_POST_PIN_PATHS:
        return True
    if path.startswith(".grok-plugin/packs/") and path.endswith("/plugin.json"):
        return True
    return False

# in validate_release_pin:
extra = sorted({p for p in changed if not _is_allowed_post_pin_path(p)})
```

Core builders:

```python
def build_pack_plugin_manifest(cfg: dict[str, Any], pack_id: str) -> dict[str, Any]:
    pack = cfg["packs"][pack_id]
    version = _studio_version()  # read VERSION file strip
    manifest: dict[str, Any] = {
        "name": pack["name"],
        "version": version,
        "description": pack.get("description") or pack.get("display_name") or pack_id,
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
    # optional soft deps for docs/tools
    if pack.get("requires"):
        manifest["cinematicStudioRequires"] = list(pack["requires"])
    return manifest


def build_full_plugin_manifest_from_packs(cfg: dict[str, Any], base: dict[str, Any] | None = None) -> dict[str, Any]:
    """Full suite = union of pack skills + all commands; preserve author fields from base."""
    base = dict(base or load_plugin_manifest())
    all_skills: list[str] = []
    all_cmds: list[str] = []
    for pid in PACK_IDS:
        all_skills.extend(cfg["packs"][pid]["skills"])
        all_cmds.extend(cfg["packs"][pid].get("commands") or [])
    base["name"] = FULL_PLUGIN_NAME
    base["version"] = _studio_version()
    base["skills"] = resolve_pack_skill_paths(all_skills)
    base["commands"] = resolve_pack_command_paths(all_cmds)
    return base


def build_marketplace_from_packs(cfg: dict[str, Any], *, sha: str | None = None) -> dict[str, Any]:
    errs = validate_plugin_packs(cfg)
    if errs:
        raise ValueError("invalid plugin packs: " + "; ".join(errs))
    pin = sha  # may be None until pin step
    plugins: list[dict[str, Any]] = []

    def entry(name: str, description: str, **extra: Any) -> dict[str, Any]:
        source: dict[str, Any] = {
            "source": "url",
            "url": REPO_GIT_URL,
        }
        if pin:
            source["sha"] = pin
        e: dict[str, Any] = {
            "name": name,
            "description": description,
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
    return {
        "name": "finecomputer14451-cinematic-studio",
        "description": (
            f"Grok Imagine Cinematic Studio v{_studio_version()} marketplace — "
            "full suite + modular packs (core, camera-image, sequence-narrative, nsfw, delivery-post)."
        ),
        "owner": {
            "name": "FineComputer14451",
            "url": "https://github.com/FineComputer14451",
        },
        "plugins": plugins,
    }


def build_index_from_packs(marketplace: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    """Per-plugin skill/command components (not global dump)."""
    skills_by_name = {s["name"]: s for s in discover_skills()}
    cmds_by_name = {c["name"]: c for c in discover_commands()}
    records: dict[str, dict[str, Any]] = {}

    # full suite
    full_skills = []
    full_cmds = []
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
        cm = [cmds_by_name[c] for c in (pack.get("commands") or []) if c in cmds_by_name]
        rec: dict[str, Any] = {"components": {"skills": sk}}
        if cm:
            rec["components"]["commands"] = cm
        records[pack["name"]] = rec

    # attach shas from marketplace
    for entry in marketplace.get("plugins") or []:
        name = entry.get("name")
        if name in records:
            sha = pinned_sha(entry)
            if sha:
                records[name]["sha"] = sha

    return {"version": 1, "plugins": records}


def _studio_version() -> str:
    vf = STUDIO_ROOT / "VERSION"
    if vf.is_file():
        return vf.read_text(encoding="utf-8").strip()
    return "0.0.0"


def write_pack_manifests(cfg: dict[str, Any]) -> list[Path]:
    written: list[Path] = []
    PLUGIN_PACKS_DIR.mkdir(parents=True, exist_ok=True)
    for pid in PACK_IDS:
        out_dir = PLUGIN_PACKS_DIR / pid
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "plugin.json"
        manifest = build_pack_plugin_manifest(cfg, pid)
        path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written.append(path)
    return written
```

Wire `write_artifacts` to:

1. `cfg = load_plugin_packs()`; fail if `validate_plugin_packs` non-empty  
2. Build marketplace from packs (preserve existing SHA if `sync_sha` false by reading current marketplace pin)  
3. Write full `plugin.json` via `build_full_plugin_manifest_from_packs`  
4. `write_pack_manifests(cfg)`  
5. Write marketplace + `build_index_from_packs`  

Preserve existing `sync_marketplace_sha` so **all** URL entries for REPO_GIT_URL get the same SHA (already loops all plugins — good once marketplace has six entries).

- [ ] **Step 4: Update `check_plugin_artifacts`**

- Validate packs config: `errors.extend(validate_plugin_packs(load_plugin_packs()))`  
- Full suite plugin.json matches `build_full_plugin_manifest_from_packs` render  
- Each pack file under `.grok-plugin/packs/<id>/plugin.json` matches generated content  
- Index matches `build_index_from_packs`  
- Marketplace has exactly 6 plugins (or ≥6 including full + 5 packs)

- [ ] **Step 5: Run unit tests**

```bash
pytest tests/test_plugin_packs.py tests/test_plugin_catalog_pin.py -v
```

Expected: PASS (update pin tests if marketplace fixture needs multi-plugin — keep single-plugin fixtures valid for pin logic).

- [ ] **Step 6: Generate artifacts in repo**

```bash
python -c "
from pathlib import Path
import json, sys
sys.path.insert(0,'tools')
from plugin_catalog import write_artifacts, load_marketplace
# if load_marketplace missing:
from studio_paths import PLUGIN_MARKETPLACE_PATH
m = json.loads(PLUGIN_MARKETPLACE_PATH.read_text())
from plugin_packs import load_plugin_packs
from plugin_catalog import write_artifacts
# implement write_artifacts to accept packs path
print(write_artifacts(m, sync_sha=False))
"
# Or use existing CLI:
python tools/cinematic_studio_cli.py plugin catalog generate  # if command exists; else pin/check path
```

If CLI only has `catalog pin` / `check`, extend `plugin catalog` generate to call pack-aware `write_artifacts` (see Task 3).

- [ ] **Step 7: Commit**

```bash
git add tools/plugin_catalog.py tools/studio_paths.py tests/test_plugin_packs.py \
  .grok-plugin/plugin.json .grok-plugin/marketplace.json .grok-plugin/plugin-index.json \
  .grok-plugin/packs/
git commit -m "feat(plugins): generate full suite + five pack manifests and marketplace"
```

---

## Task 3: CLI surfaces

**Files:**
- Modify: `tools/cli/plugin_commands.py`

- [ ] **Step 1: Add `plugin packs` command**

```python
@plugin_app.command("packs")
def plugin_packs_cmd(
    json_output: bool = typer.Option(False, "--json"),
):
    """List modular packs from config/plugin_packs.yaml."""
    from plugin_packs import PACK_IDS, load_plugin_packs, validate_plugin_packs

    cfg = load_plugin_packs()
    errs = validate_plugin_packs(cfg)
    if errs:
        for e in errs:
            console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)
    if json_output:
        console.print_json(data=cfg)
        return
    console.print(f"[bold]Full suite:[/bold] {cfg['full_plugin']['name']} (recommended)")
    for pid in PACK_IDS:
        p = cfg["packs"][pid]
        console.print(
            f"[cyan]{pid}[/cyan] → {p['name']}  "
            f"skills={len(p['skills'])} commands={len(p.get('commands') or [])} "
            f"requires={p.get('requires') or []}"
        )
```

- [ ] **Step 2: Ensure catalog generate/pin uses pack-aware write**

In existing `plugin catalog pin` / generate handlers, call the updated `write_artifacts`. No separate user flag for v1 — always pack-aware.

- [ ] **Step 3: Manual smoke**

```bash
python tools/cinematic_studio_cli.py plugin packs
python tools/cinematic_studio_cli.py plugin catalog check
```

Expected: packs listed; check green after generate.

- [ ] **Step 4: Commit**

```bash
git add tools/cli/plugin_commands.py
git commit -m "feat(cli): plugin packs list and pack-aware catalog generation"
```

---

## Task 4: Declutter `full_suite_wins`

**Files:**
- Modify: `scripts/lib/cinematic_studio_common.sh` (`cinematic_studio_declutter`)
- Modify: `tools/cli/plugin_commands.py` (docstring only if still delegates)
- Optional: `tests/test_declutter_packs.sh` or Python unit for pure helper

**Behavior:**

After existing Method A cleanup:

1. Scan `~/.grok/installed-plugins/` for dirs containing full suite plugin name **and** any satellite pack names (from packs YAML satellite list or fixed names).  
2. If full suite install is present **and** a satellite install is present:  
   - For each skill name in the satellite’s `.grok/skills/*` that also exists under the full suite install’s skills dir → remove the **satellite** skill directory (dry-run lists them).  
3. Never remove skills from the full suite install.  
4. If only satellites (no full suite) → skip this pass (keep satellites).

- [ ] **Step 1: Implement bash pass**

Sketch to insert near end of `cinematic_studio_declutter` before Summary:

```bash
# --- full_suite_wins: satellite vs full suite under installed-plugins ---
local plugins_root="${GROK_PLUGINS_DIR:-$HOME/.grok/installed-plugins}"
local full_glob satellite_skill
local full_install="" sat_install
local -a sat_roots=()

if [[ -d "$plugins_root" ]]; then
    # Resolve full suite install dir (name contains grok-imagine-cinematic-studio, not -core/-nsfw/etc.)
    while IFS= read -r d; do
        [[ -z "$d" ]] && continue
        base="$(basename "$d")"
        # Prefer exact-ish: contains cinematic-studio but not pack suffixes
        if [[ "$base" == *grok-imagine-cinematic-studio* ]] \
           && [[ "$base" != *cinematic-core* ]] \
           && [[ "$base" != *camera-image* ]] \
           && [[ "$base" != *sequence-narrative* ]] \
           && [[ "$base" != *delivery-post* ]] \
           && [[ "$base" != *grok-imagine-nsfw* ]]; then
            if [[ -d "$d/.grok/skills" ]]; then
                full_install="$d"
                break
            fi
        fi
    done < <(find "$plugins_root" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort)

    # Satellite installs
    for pattern in \
        '*cinematic-core*' \
        '*camera-image*' \
        '*sequence-narrative*' \
        '*grok-imagine-nsfw*' \
        '*delivery-post*'; do
        while IFS= read -r d; do
            [[ -n "$d" && -d "$d/.grok/skills" ]] && sat_roots+=("$d")
        done < <(find "$plugins_root" -mindepth 1 -maxdepth 1 -type d -name "$pattern" 2>/dev/null)
    done

    if [[ -n "$full_install" && ${#sat_roots[@]} -gt 0 ]]; then
        echo "→ full_suite_wins: full=$full_install"
        echo "  satellites: ${#sat_roots[@]}"
        for sat_install in "${sat_roots[@]}"; do
            echo "  satellite: $sat_install"
            while IFS= read -r satellite_skill; do
                [[ -z "$satellite_skill" ]] && continue
                if [[ -d "$full_install/.grok/skills/$satellite_skill" ]]; then
                    echo "  - drop satellite skill: $satellite_skill ($sat_install)"
                    if [[ $apply -eq 1 ]]; then
                        rm -rf "$sat_install/.grok/skills/$satellite_skill"
                    fi
                fi
            done < <(find "$sat_install/.grok/skills" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' 2>/dev/null | sort)
        done
    fi
fi
```

Tune basename matching against real Grok install dir naming (`grok-imagine-cinematic-studio-<hash>`). Prefer reading each install’s `plugin.json` `"name"` field when present:

```bash
# Prefer plugin.json name over directory heuristics
jq -r .name "$d/plugin.json" 2>/dev/null || jq -r .name "$d/.grok-plugin/plugin.json"
```

Use name equality to `grok-imagine-cinematic-studio` vs satellite names from packs YAML.

- [ ] **Step 2: Dry-run smoke**

```bash
bash scripts/cinematic_studio.sh declutter --dry-run
```

Expected: still works without dual pack installs; no crash.

- [ ] **Step 3: Commit**

```bash
git add scripts/lib/cinematic_studio_common.sh
git commit -m "feat(declutter): full_suite_wins removes satellite skill dupes"
```

---

## Task 5: Docs + version bump

**Files:**
- `VERSION` → `3.8.0`
- `CHANGELOG.md`
- `README.md` (install matrix)
- `docs/guides/installation_guide.md`
- `references/SKILLS_TAXONOMY.md`
- `AGENTS.md`
- `.grok-plugin/plugin.json` / pack manifests version via regenerate
- Optional: `references/agents/AGENT_INDEX.md` pack note (one paragraph)

- [ ] **Step 1: VERSION**

```text
3.8.0
```

- [ ] **Step 2: CHANGELOG entry (top)**

```markdown
## [3.8.0] — 2026-07-11

### Added
- **Plugin modularity** — marketplace ships full suite + five satellite packs
  (`core`, `camera-image`, `sequence-narrative`, `nsfw`, `delivery-post`) from
  `config/plugin_packs.yaml` (manifest-only filtered views).
- **`plugin packs` CLI** — list pack membership and soft deps.
- **Declutter `full_suite_wins`** — when full suite and satellites coexist under
  `~/.grok/installed-plugins/`, remove overlapping satellite skill copies.

### Changed
- Plugin catalog generation and pin protocol cover six marketplace plugin entries.
```

- [ ] **Step 3: Install guide matrix**

```markdown
| Install | Command / marketplace name | When |
|---------|----------------------------|------|
| **Recommended** | `grok-imagine-cinematic-studio` | Full production |
| Core only | `grok-imagine-cinematic-core` | Lean orchestration + DNA + Imagine |
| Camera & Image | `grok-imagine-camera-image` | Stills / i2i / key art (requires core) |
| Sequence & Narrative | `grok-imagine-sequence-narrative` | Long-form (requires core) |
| NSFW opt-in | `grok-imagine-nsfw` | Explicit consent only (requires core) |
| Delivery & Post | `grok-imagine-delivery-post` | Polish / mux (requires core) |
```

- [ ] **Step 4: Taxonomy** — add “Marketplace packs” section mapping pack id → skill list (or pointer to `config/plugin_packs.yaml`).

- [ ] **Step 5: Regenerate catalog + pin**

```bash
# after content commit:
python tools/cinematic_studio_cli.py plugin catalog pin   # or project equivalent
# commit only .grok-plugin/ as pin tip
```

- [ ] **Step 6: Verify**

```bash
bash scripts/verify_plugins.sh
# or
python tools/cinematic_studio_cli.py plugin catalog check --release
pytest tests/test_plugin_packs.py tests/test_plugin_catalog_pin.py -v
```

- [ ] **Step 7: Commit content then pin**

```bash
git add VERSION CHANGELOG.md README.md docs/guides/installation_guide.md \
  references/SKILLS_TAXONOMY.md AGENTS.md
git commit -m "docs(release): v3.8.0 plugin modularity packs"

# then pin commit
git add .grok-plugin/
git commit -m "chore(plugins): pin marketplace catalog to content SHA (6 plugins)"
```

---

## Task 6: Install-layout spike note (blocking only if generate install fails)

**Goal:** Confirm Grok Build can install a satellite pack whose `plugin.json` lives at `.grok-plugin/packs/<id>/plugin.json` with skill paths `.grok/skills/...`.

- [ ] **Step 1:** Read Grok plugin docs under `~/.grok/docs/` for multi-plugin / monorepo install paths.

- [ ] **Step 2:** If install requires package-root-relative skills, adjust pack manifests to ship **only** the selector + document that packs install from full clone (paths still shared). Do **not** copy skill bodies.

- [ ] **Step 3:** Record outcome in `docs/guides/installation_guide.md` under “Pack install notes”.

If spike finds marketplace only supports one `plugin.json` at repo root: fall back to documenting packs as **catalog profiles** that users install via CLI filter (`plugin install --pack core`) generating a temporary plugin.json — still matching design intent. Prefer true multi-entry marketplace if supported.

---

## Spec coverage checklist

| Spec requirement | Task |
|------------------|------|
| Hybrid + additive install story | 2, 5 |
| Five packs + full suite | 1, 2 |
| Mono-repo filtered views | 1, 2 |
| Domain-mapped commands | 1 YAML |
| Declutter full_suite_wins | 4 |
| Generator hard-fail dual/unknown/union | 1 validate |
| Shared pin SHA | 2 sync_marketplace_sha |
| Per-plugin index not global dump | 2 build_index_from_packs |
| Docs + 3.8.0 | 5 |
| Install layout spike | 6 |
| No new creative agents | n/a (out of scope) |

---

## Out of scope (do not implement in this plan)

- New Role Cards / creative skills  
- `/sequence` or `/camera` slash commands  
- Multi-repo packs  
- Hard Grok-runtime package dependencies  
- Splitting Python CLI into pack-specific wheels  

---

## Execution handoff

Plan complete and saved to `docs/development/superpowers/plans/2026-07-11-plugin-modularity-packs-implementation.md`.

**Two execution options:**

1. **Subagent-Driven (recommended)** — fresh subagent per task, review between tasks  
2. **Inline Execution** — execute tasks in this session with checkpoints  

Which approach?
