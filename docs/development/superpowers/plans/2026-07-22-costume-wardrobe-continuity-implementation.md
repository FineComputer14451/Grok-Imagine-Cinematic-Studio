# Costume & Wardrobe Continuity (P1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the Costume & Wardrobe Continuity agent as nested `wardrobe_lock` on Character DNA, pure Python helpers for inject/handoff/clip state, Role Card + skill, and suite index/manifest updates (51 → 52 skills) — **no new CLI**.

**Architecture:** Pure module `tools/wardrobe_lock.py` owns schema helpers (scaffold look, validate, summary → `clothing_style`, inject blocks, clip `wardrobe_state`, optional handoff `wardrobe` section). `tools/character_dna.py` optionally attaches wardrobe handoff when locked. Agent surface is Role Card + skill only; Identity Lock / Continuity get short consume-only integration bullets.

**Tech Stack:** Python 3.11+, pytest, existing DNA paths under `characters/`, Grok skill YAML frontmatter, Role Cards under `references/agents/`. No new packaging dependencies. No Typer CLI commands in this plan.

**Design:** [docs/development/superpowers/specs/2026-07-22-costume-wardrobe-continuity-design.md](../specs/2026-07-22-costume-wardrobe-continuity-design.md)

---

## Global Constraints

- **No new CLI** (`dna wardrobe`, etc.) in P1.
- **Nested DNA only** — `wardrobe_lock` on Character DNA JSON; no parallel `wardrobe.json`.
- **Primary character only** for full lock; secondary cast → `secondary_notes` string.
- **Condition enum only:** `clean` | `worn` | `damaged` | `wet`.
- **Status enum only:** `pending` | `locked` | `drift_review`.
- **Delta does not rewrite** canonical lock without explicit permanent re-lock API (`apply_permanent_look_update` or lock after mutation).
- **Suite count:** skill manifests and marketing strings must move **51 → 52** when the skill is added.
- **Model Layer:** Role Card + skill must cite `grok-v9-4p5-chat-expert` / `grok-v9-4p5-multi` / `grok-4-auto` per design.
- **YAGNI:** no fashion ideation mode, no multi-cast dual wardrobe DNA, no required new handoff `packet_type`.
- Prefer stable `prompt_cache_key` language in Role Card (project slug) — narrative only.

---

## File map

| Path | Responsibility |
|------|----------------|
| `tools/wardrobe_lock.py` | Pure wardrobe schema + inject + clip state + handoff section |
| `tools/character_dna.py` | Attach optional `wardrobe` on identity handoff; markdown section for wardrobe when present |
| `tests/test_wardrobe_lock.py` | Unit tests for wardrobe helpers |
| `tests/test_character_dna_wardrobe.py` | Integration: handoff + clothing_style sync via DNA helpers |
| `references/agents/Costume_Wardrobe_Continuity.md` | Role Card |
| `.grok/skills/costume-wardrobe-continuity/SKILL.md` | Skill |
| `references/agents/AGENT_INDEX.md` | Index row + activation |
| `references/agents/Identity_Lock_Specialist.md` | Consume wardrobe inject when locked |
| `references/agents/Continuity_Consistency_Guardian.md` | Read wardrobe_state / seam notes |
| `.grok/skills/identity-lock-specialist/SKILL.md` | Short integration bullet |
| `.grok/skills/continuity-consistency-guardian/SKILL.md` | Short integration bullet |
| `.grok/skills/character-dna-extractor/SKILL.md` | Point upstream → wardrobe after clothing visible |
| `scripts/required_skills.manifest` | Add skill slug (alphabetically among non-core or after character-dna) |
| `config/plugin_packs.yaml` | Full suite description 51 → 52 |
| `AGENTS.md`, `README.md` (skill-count lines only), `references/SKILLS_TAXONOMY.md`, meta-installer skill count strings | Consistency |
| `CHANGELOG.md` | Unreleased entry |
| `.grok-plugin/` | Regenerate catalog **after** skill exists (`python scripts/generate_plugin_index.py` or `cinematic-studio plugin catalog pin` per release hygiene) |

**Out of scope files:** CLI command modules, ErosForge Role Card rewrites, Sequence Extender full rewrites (optional one-line “include wardrobe inject” is enough if touched).

---

### Task 1: Pure `wardrobe_lock` module + unit tests (TDD)

**Files:**
- Create: `tools/wardrobe_lock.py`
- Create: `tests/test_wardrobe_lock.py`

**Interfaces:**
- Consumes: none (stdlib only)
- Produces:
  - `CONDITION_VALUES = frozenset({"clean", "worn", "damaged", "wet"})`
  - `STATUS_VALUES = frozenset({"pending", "locked", "drift_review"})`
  - `WARDROBE_SCHEMA_VERSION = "1.0"`
  - `create_wardrobe_lock(*, look_id="look_default", label="", silhouette="", garments=None, accessories=None, layer_order=None, condition_default="worn", inject_anchors=None, secondary_notes="", source="manual") -> dict`
  - `validate_wardrobe_lock(wardrobe: dict) -> list[str]`  # empty = ok
  - `active_look(wardrobe: dict) -> dict | None`
  - `clothing_style_summary(wardrobe: dict) -> str`
  - `sync_clothing_style(dna: dict) -> str`  # sets dna["clothing_style"] when wardrobe locked; returns summary
  - `build_wardrobe_inject(wardrobe: dict, *, slug: str) -> dict[str, str]`  # keys: compact, full, video; empty strings if no usable look
  - `build_clip_wardrobe_state(*, character_slug: str, look_id: str, condition: str, delta: str = "", layer_order=None, updated_from_clip: str | None = None) -> dict`
  - `build_wardrobe_handoff_section(wardrobe: dict, *, slug: str, condition: str | None = None) -> dict | None`  # None if missing/not locked
  - `lock_wardrobe(wardrobe: dict) -> dict`  # status locked + locked_at ISO; mutates and returns
  - `set_active_look(wardrobe: dict, look_id: str) -> dict`  # raises ValueError if unknown
  - `apply_clip_delta_note` is **not** required — clip state is separate from DNA

- [ ] **Step 1: Write the failing tests**

Create `tests/test_wardrobe_lock.py`:

```python
"""Tests for nested wardrobe_lock helpers (Costume & Wardrobe Continuity P1)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from wardrobe_lock import (  # noqa: E402
    build_clip_wardrobe_state,
    build_wardrobe_handoff_section,
    build_wardrobe_inject,
    clothing_style_summary,
    create_wardrobe_lock,
    lock_wardrobe,
    set_active_look,
    sync_clothing_style,
    validate_wardrobe_lock,
)


def test_create_wardrobe_lock_defaults() -> None:
    w = create_wardrobe_lock(
        label="Hero trench",
        silhouette="long overcoat",
        garments=[
            {
                "id": "coat",
                "name": "brown trench",
                "category": "outerwear",
                "colors": ["brown"],
                "materials": ["cotton twill"],
                "details": "frayed cuffs",
                "layer_index": 2,
            }
        ],
        accessories=[{"id": "ring", "name": "silver ring", "hand": "left", "details": ""}],
        layer_order=["shirt", "coat"],
        condition_default="worn",
        inject_anchors=["frayed cuffs", "silver ring"],
    )
    assert w["schema_version"] == "1.0"
    assert w["status"] == "pending"
    assert w["active_look_id"] == "look_default"
    assert len(w["looks"]) == 1
    assert w["looks"][0]["garments"][0]["name"] == "brown trench"
    assert validate_wardrobe_lock(w) == []


def test_validate_rejects_bad_condition_and_status() -> None:
    w = create_wardrobe_lock()
    w["status"] = "nope"
    w["looks"][0]["condition_default"] = "filthy"
    issues = validate_wardrobe_lock(w)
    assert any("status" in i for i in issues)
    assert any("condition" in i for i in issues)


def test_validate_active_look_must_exist() -> None:
    w = create_wardrobe_lock()
    w["active_look_id"] = "missing"
    issues = validate_wardrobe_lock(w)
    assert any("active_look" in i.lower() or "active_look_id" in i for i in issues)


def test_lock_and_summary_and_inject() -> None:
    w = create_wardrobe_lock(
        label="Hero trench",
        silhouette="long overcoat",
        garments=[
            {
                "id": "coat",
                "name": "brown trench",
                "category": "outerwear",
                "colors": ["brown"],
                "materials": ["twill"],
                "details": "water stains",
                "layer_index": 1,
            }
        ],
        layer_order=["coat"],
        condition_default="worn",
        inject_anchors=["water stains"],
    )
    lock_wardrobe(w)
    assert w["status"] == "locked"
    assert w.get("locked_at")
    summary = clothing_style_summary(w)
    assert "trench" in summary.lower() or "overcoat" in summary.lower()
    inject = build_wardrobe_inject(w, slug="marcus")
    assert inject["compact"].startswith("[WARDROBE_LOCK:marcus:look_default]")
    assert "trench" in inject["full"].lower() or "coat" in inject["full"].lower()
    assert inject["video"]  # non-empty fabric/motion cue line


def test_handoff_section_only_when_locked() -> None:
    w = create_wardrobe_lock(
        garments=[{"id": "coat", "name": "coat", "category": "outerwear", "colors": ["grey"], "materials": [], "details": "", "layer_index": 0}],
        layer_order=["coat"],
    )
    assert build_wardrobe_handoff_section(w, slug="marcus") is None
    lock_wardrobe(w)
    section = build_wardrobe_handoff_section(w, slug="marcus", condition="wet")
    assert section is not None
    assert section["status"] == "locked"
    assert section["active_look_id"] == "look_default"
    assert "compact" in section["inject"]
    assert section["condition"] == "wet"


def test_clip_wardrobe_state() -> None:
    state = build_clip_wardrobe_state(
        character_slug="marcus",
        look_id="look_default",
        condition="wet",
        delta="coat darker from rain",
        layer_order=["shirt", "coat"],
        updated_from_clip="02",
    )
    assert state["condition"] == "wet"
    assert state["delta"] == "coat darker from rain"
    assert state["updated_from_clip"] == "02"


def test_clip_state_rejects_bad_condition() -> None:
    try:
        build_clip_wardrobe_state(
            character_slug="marcus",
            look_id="look_default",
            condition="soaked",
        )
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "condition" in str(exc).lower()


def test_set_active_look() -> None:
    w = create_wardrobe_lock(look_id="look_a", label="A")
    w["looks"].append(
        {
            "look_id": "look_b",
            "label": "B",
            "silhouette": "",
            "garments": [],
            "accessories": [],
            "layer_order_bottom_to_top": [],
            "condition_default": "clean",
            "inject_anchors": [],
        }
    )
    set_active_look(w, "look_b")
    assert w["active_look_id"] == "look_b"
    try:
        set_active_look(w, "look_z")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


def test_sync_clothing_style_when_locked() -> None:
    dna = {
        "character_name": "Marcus",
        "slug": "marcus",
        "clothing_style": "old wrong text",
        "wardrobe_lock": create_wardrobe_lock(
            label="Night coat",
            silhouette="long coat",
            garments=[
                {
                    "id": "coat",
                    "name": "black coat",
                    "category": "outerwear",
                    "colors": ["black"],
                    "materials": ["wool"],
                    "details": "",
                    "layer_index": 0,
                }
            ],
            layer_order=["coat"],
        ),
    }
    # pending: do not overwrite unless we choose to — design: sync when locked
    before = dna["clothing_style"]
    sync_clothing_style(dna)
    assert dna["clothing_style"] == before  # still pending
    lock_wardrobe(dna["wardrobe_lock"])
    sync_clothing_style(dna)
    assert "coat" in dna["clothing_style"].lower() or "night" in dna["clothing_style"].lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_wardrobe_lock.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'wardrobe_lock'` (or import error).

- [ ] **Step 3: Implement `tools/wardrobe_lock.py`**

```python
#!/usr/bin/env python3
"""Nested wardrobe_lock helpers for Costume & Wardrobe Continuity (P1).

No CLI. Nested under Character DNA as dna["wardrobe_lock"].
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

WARDROBE_SCHEMA_VERSION = "1.0"
CONDITION_VALUES = frozenset({"clean", "worn", "damaged", "wet"})
STATUS_VALUES = frozenset({"pending", "locked", "drift_review"})
SOURCE_VALUES = frozenset({"manual", "extracted", "refined"})


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def create_wardrobe_lock(
    *,
    look_id: str = "look_default",
    label: str = "",
    silhouette: str = "",
    garments: list[dict[str, Any]] | None = None,
    accessories: list[dict[str, Any]] | None = None,
    layer_order: list[str] | None = None,
    condition_default: str = "worn",
    inject_anchors: list[str] | None = None,
    secondary_notes: str = "",
    source: str = "manual",
) -> dict[str, Any]:
    if condition_default not in CONDITION_VALUES:
        raise ValueError(f"Invalid condition_default: {condition_default}")
    if source not in SOURCE_VALUES:
        raise ValueError(f"Invalid source: {source}")
    look = {
        "look_id": look_id,
        "label": label,
        "silhouette": silhouette,
        "garments": list(garments or []),
        "accessories": list(accessories or []),
        "layer_order_bottom_to_top": list(layer_order or []),
        "condition_default": condition_default,
        "inject_anchors": list(inject_anchors or []),
    }
    return {
        "schema_version": WARDROBE_SCHEMA_VERSION,
        "status": "pending",
        "active_look_id": look_id,
        "looks": [look],
        "secondary_notes": secondary_notes or "",
        "locked_at": None,
        "source": source,
    }


def active_look(wardrobe: dict[str, Any]) -> dict[str, Any] | None:
    if not wardrobe:
        return None
    aid = wardrobe.get("active_look_id")
    for look in wardrobe.get("looks") or []:
        if look.get("look_id") == aid:
            return look
    return None


def validate_wardrobe_lock(wardrobe: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    if not isinstance(wardrobe, dict):
        return ["wardrobe_lock must be an object"]
    if wardrobe.get("schema_version") != WARDROBE_SCHEMA_VERSION:
        issues.append(f"Unsupported wardrobe schema_version: {wardrobe.get('schema_version')}")
    status = wardrobe.get("status")
    if status not in STATUS_VALUES:
        issues.append(f"Invalid status: {status}")
    source = wardrobe.get("source")
    if source is not None and source not in SOURCE_VALUES:
        issues.append(f"Invalid source: {source}")
    looks = wardrobe.get("looks") or []
    if not isinstance(looks, list):
        issues.append("looks must be a list")
        return issues
    look_ids = []
    for i, look in enumerate(looks):
        if not isinstance(look, dict):
            issues.append(f"looks[{i}] must be an object")
            continue
        lid = look.get("look_id")
        if not lid:
            issues.append(f"looks[{i}] missing look_id")
        else:
            look_ids.append(lid)
        cond = look.get("condition_default", "worn")
        if cond not in CONDITION_VALUES:
            issues.append(f"looks[{i}] invalid condition_default: {cond}")
    aid = wardrobe.get("active_look_id")
    if aid and aid not in look_ids:
        issues.append(f"active_look_id not in looks: {aid}")
    return issues


def clothing_style_summary(wardrobe: dict[str, Any]) -> str:
    look = active_look(wardrobe)
    if not look:
        return ""
    parts: list[str] = []
    if look.get("label"):
        parts.append(str(look["label"]))
    if look.get("silhouette"):
        parts.append(str(look["silhouette"]))
    for g in look.get("garments") or []:
        name = g.get("name") or g.get("id") or ""
        colors = ", ".join(g.get("colors") or [])
        details = g.get("details") or ""
        chunk = name
        if colors:
            chunk = f"{colors} {chunk}".strip()
        if details:
            chunk = f"{chunk} ({details})" if chunk else details
        if chunk:
            parts.append(chunk)
    for a in look.get("accessories") or []:
        name = a.get("name") or a.get("id") or ""
        if name:
            parts.append(name)
    cond = look.get("condition_default")
    if cond and cond != "clean":
        parts.append(f"condition: {cond}")
    # de-dupe while preserving order
    seen: set[str] = set()
    ordered: list[str] = []
    for p in parts:
        key = p.strip().lower()
        if key and key not in seen:
            seen.add(key)
            ordered.append(p.strip())
    return "; ".join(ordered)


def sync_clothing_style(dna: dict[str, Any]) -> str:
    """When wardrobe_lock is locked, rewrite dna['clothing_style'] from active look."""
    wardrobe = dna.get("wardrobe_lock")
    if not isinstance(wardrobe, dict):
        return str(dna.get("clothing_style") or "")
    if wardrobe.get("status") != "locked":
        return str(dna.get("clothing_style") or "")
    summary = clothing_style_summary(wardrobe)
    if summary:
        dna["clothing_style"] = summary
    return summary


def build_wardrobe_inject(wardrobe: dict[str, Any], *, slug: str) -> dict[str, str]:
    look = active_look(wardrobe)
    if not look:
        return {"compact": "", "full": "", "video": ""}
    look_id = look.get("look_id") or "look_default"
    token = f"[WARDROBE_LOCK:{slug}:{look_id}]"
    summary = clothing_style_summary(wardrobe)
    layers = " > ".join(look.get("layer_order_bottom_to_top") or [])
    anchors = "; ".join(look.get("inject_anchors") or [])
    garments = look.get("garments") or []
    accessories = look.get("accessories") or []
    garment_lines = []
    for g in garments:
        garment_lines.append(
            f"- {g.get('name', g.get('id', 'garment'))}: "
            f"colors={', '.join(g.get('colors') or [])}; "
            f"materials={', '.join(g.get('materials') or [])}; "
            f"{g.get('details') or ''}".strip()
        )
    acc_lines = []
    for a in accessories:
        acc_lines.append(f"- {a.get('name', a.get('id', 'accessory'))}: {a.get('details') or ''}".strip())
    cond = look.get("condition_default", "worn")
    compact = f"{token} {summary}".strip()
    full_parts = [
        token,
        f"Look: {look.get('label') or look_id}",
        f"Silhouette: {look.get('silhouette') or 'n/a'}",
        f"Condition: {cond}",
    ]
    if layers:
        full_parts.append(f"Layers (bottom→top): {layers}")
    if garment_lines:
        full_parts.append("Garments:\n" + "\n".join(garment_lines))
    if acc_lines:
        full_parts.append("Accessories:\n" + "\n".join(acc_lines))
    if anchors:
        full_parts.append(f"Anchors: {anchors}")
    notes = wardrobe.get("secondary_notes") or ""
    if notes:
        full_parts.append(f"Secondary wardrobe notes: {notes}")
    full = "\n".join(full_parts)
    video = (
        f"{full}\n"
        f"Fabric/motion: preserve drape, layer separation, and accessory placement under camera move; "
        f"condition stays {cond} unless continuity delta says otherwise."
    )
    return {"compact": compact, "full": full, "video": video}


def build_clip_wardrobe_state(
    *,
    character_slug: str,
    look_id: str,
    condition: str,
    delta: str = "",
    layer_order: list[str] | None = None,
    updated_from_clip: str | None = None,
) -> dict[str, Any]:
    if condition not in CONDITION_VALUES:
        raise ValueError(f"Invalid condition: {condition}")
    state: dict[str, Any] = {
        "character_slug": character_slug,
        "look_id": look_id,
        "condition": condition,
        "delta": delta or "",
        "layer_order_bottom_to_top": list(layer_order or []),
    }
    if updated_from_clip is not None:
        state["updated_from_clip"] = updated_from_clip
    return state


def build_wardrobe_handoff_section(
    wardrobe: dict[str, Any],
    *,
    slug: str,
    condition: str | None = None,
) -> dict[str, Any] | None:
    if not wardrobe or wardrobe.get("status") != "locked":
        return None
    look = active_look(wardrobe)
    if not look:
        return None
    inject = build_wardrobe_inject(wardrobe, slug=slug)
    cond = condition or look.get("condition_default") or "worn"
    if cond not in CONDITION_VALUES:
        cond = "worn"
    return {
        "status": "locked",
        "active_look_id": wardrobe.get("active_look_id"),
        "inject": {"compact": inject["compact"], "full": inject["full"]},
        "condition": cond,
        "secondary_notes": wardrobe.get("secondary_notes") or "",
    }


def lock_wardrobe(wardrobe: dict[str, Any]) -> dict[str, Any]:
    issues = validate_wardrobe_lock(wardrobe)
    # allow lock even with empty garments; only hard-fail invalid enums / active look
    hard = [i for i in issues if "schema_version" in i or "status" in i or "active_look" in i or "condition" in i]
    # status is pending before lock — strip status errors for pending→locked transition
    hard = [i for i in hard if not i.startswith("Invalid status: pending")]
    if wardrobe.get("status") in (None, "pending", "drift_review", "locked"):
        hard = [i for i in hard if "Invalid status" not in i]
    if any("active_look" in i for i in issues):
        raise ValueError("; ".join(issues))
    if any("condition" in i for i in issues):
        raise ValueError("; ".join(issues))
    if any("schema_version" in i for i in issues):
        raise ValueError("; ".join(issues))
    wardrobe["status"] = "locked"
    wardrobe["locked_at"] = _now_iso()
    return wardrobe


def set_active_look(wardrobe: dict[str, Any], look_id: str) -> dict[str, Any]:
    ids = {look.get("look_id") for look in (wardrobe.get("looks") or [])}
    if look_id not in ids:
        raise ValueError(f"Unknown look_id: {look_id}")
    wardrobe["active_look_id"] = look_id
    return wardrobe
```

Note: simplify `lock_wardrobe` validation if the above is overly defensive — required behavior is: set `status=locked`, set `locked_at`, raise if `active_look_id` missing from looks or condition enums invalid.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_wardrobe_lock.py -v`  
Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/wardrobe_lock.py tests/test_wardrobe_lock.py
git commit -m "feat(wardrobe): add nested wardrobe_lock helpers and unit tests"
```

---

### Task 2: Wire wardrobe into Character DNA handoff + markdown

**Files:**
- Modify: `tools/character_dna.py`
- Create: `tests/test_character_dna_wardrobe.py`

**Interfaces:**
- Consumes: `wardrobe_lock.build_wardrobe_handoff_section`, `sync_clothing_style`, `build_wardrobe_inject` (optional in markdown)
- Produces: `build_handoff_packet` may include `"wardrobe": {...}` when DNA has locked wardrobe; `dna_to_markdown` includes a Wardrobe Lock section when present

- [ ] **Step 1: Write failing integration tests**

Create `tests/test_character_dna_wardrobe.py`:

```python
"""Character DNA handoff attaches optional wardrobe section when locked."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from character_dna import build_handoff_packet, create_dna_scaffold, dna_to_markdown  # noqa: E402
from wardrobe_lock import create_wardrobe_lock, lock_wardrobe, sync_clothing_style  # noqa: E402


def test_handoff_omits_wardrobe_when_absent() -> None:
    dna = create_dna_scaffold("Marcus", core_identity="detective", facial_dna="tired hazel eyes")
    packet = build_handoff_packet(dna)
    assert packet["packet_type"] == "identity_lock_handoff"
    assert "wardrobe" not in packet or packet.get("wardrobe") is None


def test_handoff_includes_wardrobe_when_locked() -> None:
    dna = create_dna_scaffold(
        "Marcus",
        core_identity="detective",
        facial_dna="tired hazel eyes",
        clothing_style="placeholder",
    )
    w = create_wardrobe_lock(
        label="Trench",
        silhouette="long coat",
        garments=[
            {
                "id": "coat",
                "name": "brown trench",
                "category": "outerwear",
                "colors": ["brown"],
                "materials": ["twill"],
                "details": "frayed cuffs",
                "layer_index": 1,
            }
        ],
        layer_order=["coat"],
        condition_default="worn",
    )
    lock_wardrobe(w)
    dna["wardrobe_lock"] = w
    sync_clothing_style(dna)
    packet = build_handoff_packet(dna)
    assert packet["wardrobe"]["status"] == "locked"
    assert "WARDROBE_LOCK" in packet["wardrobe"]["inject"]["compact"]
    assert "trench" in dna["clothing_style"].lower() or "coat" in dna["clothing_style"].lower()


def test_markdown_includes_wardrobe_section_when_present() -> None:
    dna = create_dna_scaffold("Marcus", core_identity="x", facial_dna="y")
    w = create_wardrobe_lock(
        garments=[
            {
                "id": "coat",
                "name": "grey coat",
                "category": "outerwear",
                "colors": ["grey"],
                "materials": [],
                "details": "",
                "layer_index": 0,
            }
        ],
        layer_order=["coat"],
    )
    lock_wardrobe(w)
    dna["wardrobe_lock"] = w
    md = dna_to_markdown(dna)
    assert "Wardrobe Lock" in md
    assert "locked" in md.lower()
```

- [ ] **Step 2: Run tests — expect FAIL**

Run: `pytest tests/test_character_dna_wardrobe.py -v`  
Expected: FAIL on missing `wardrobe` key / markdown section.

- [ ] **Step 3: Patch `tools/character_dna.py`**

At top of file (with other imports), add:

```python
from wardrobe_lock import build_wardrobe_handoff_section, build_wardrobe_inject
```

In `build_handoff_packet`, after building the base dict, before return:

```python
    wardrobe = dna.get("wardrobe_lock")
    if isinstance(wardrobe, dict):
        section = build_wardrobe_handoff_section(wardrobe, slug=dna["slug"])
        if section is not None:
            packet["wardrobe"] = section
            packet["identity_lock_instructions"] = list(packet["identity_lock_instructions"]) + [
                "When wardrobe.status is locked, require wardrobe inject on primary-character prompts",
                "Do not drop accessories or layer_order; clip wardrobe_state delta does not rewrite DNA without permanent re-lock",
            ]
    return packet
```

(Refactor so `packet = { ... }` is assigned, then mutate, then return — match existing style.)

In `dna_to_markdown`, after the Clothing & Style section, add:

```python
    wardrobe = dna.get("wardrobe_lock")
    if isinstance(wardrobe, dict):
        lines += [
            "",
            "## Wardrobe Lock",
            f"**Status:** {wardrobe.get('status', 'pending')}  ",
            f"**Active look:** `{wardrobe.get('active_look_id', '')}`  ",
        ]
        if wardrobe.get("secondary_notes"):
            lines += [f"**Secondary notes:** {wardrobe['secondary_notes']}", ""]
        try:
            inj = build_wardrobe_inject(wardrobe, slug=dna.get("slug") or "character")
            if inj.get("compact"):
                lines += [
                    "### Wardrobe Inject — Compact",
                    f"```\n{inj['compact']}\n```",
                    "",
                    "### Wardrobe Inject — Full",
                    f"```\n{inj['full']}\n```",
                ]
        except Exception:
            lines.append("_Wardrobe inject unavailable_")
```

Do **not** change `validate_dna` required fields (wardrobe remains optional).

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_character_dna_wardrobe.py tests/test_wardrobe_lock.py -v`  
Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/character_dna.py tests/test_character_dna_wardrobe.py
git commit -m "feat(dna): attach locked wardrobe section to identity handoff"
```

---

### Task 3: Role Card + skill

**Files:**
- Create: `references/agents/Costume_Wardrobe_Continuity.md`
- Create: `.grok/skills/costume-wardrobe-continuity/SKILL.md`

**Interfaces:**
- Consumes: design protocols; `tools/wardrobe_lock.py` as tool-first helpers when agents run code
- Produces: agent activation surface `costume-wardrobe-continuity`

- [ ] **Step 1: Write Role Card**

Create `references/agents/Costume_Wardrobe_Continuity.md` with this content (edit only if studio version stamp differs — keep Model Layer table exact). Outer fence uses four backticks so inner `yaml` fences stay intact:

````markdown
# Costume & Wardrobe Continuity v4.5 — Role Card

## Core Mission
You are the **outfit DNA and wardrobe state guardian** for Grok Imagine Cinematic Studio. You own structured `wardrobe_lock` on Character DNA, wardrobe inject blocks, and clip-level `wardrobe_state` so stills → i2v → extend keep the same garments, layers, accessories, and condition. You do **not** invent fashion lookbooks, arbitrate full multi-cast wardrobes, or own face/body Identity Lock.

## Model Layer (Grok 4.5 / v9-4p5)

| Task type | Preferred model | Reasoning |
|-----------|-----------------|-----------|
| Lock / detailed outfit extraction / inject craft | `grok-v9-4p5-chat-expert` | high |
| Multi-shot wardrobe audit across a sequence | `grok-v9-4p5-multi` | high |
| Routine status / condition-only update | `grok-4-auto` | medium |

**Registry:** `tools/models.py` · `references/agents/MODEL_LAYER_v4.5.md` · `models verify`

```yaml
model_compatibility:
  - grok-v9-4p5-chat-expert
  - grok-v9-4p5-multi
  - grok-4-auto
preferred_model: grok-v9-4p5-chat-expert
```

Prefer stable `prompt_cache_key` (project slug). Reasoning **high** for lock and inject.

## Tool-first helpers
Use `tools/wardrobe_lock.py` when code execution is available:
- `create_wardrobe_lock` · `validate_wardrobe_lock` · `lock_wardrobe`
- `build_wardrobe_inject` · `build_clip_wardrobe_state` · `build_wardrobe_handoff_section`
- `sync_clothing_style` after lock

If tools are unavailable, produce the same JSON shapes and inject strings by hand.

## Core Protocols

| Protocol | Rule |
|----------|------|
| **WARDROBE_FROM_VISIBLE** | Prefer refs + approved stills; flag inventions as `inferred — confirm` |
| **ONE_ACTIVE_LOOK** | Exactly one `active_look_id` in force |
| **PRIMARY_ONLY** | Full lock for primary only; others → `secondary_notes` |
| **STRUCTURED_CORE** | Garments, colors/materials, silhouette, accessories, layer order, condition, optional delta |
| **INJECT_READY** | Emit compact + full; add video when fabric/motion matters |
| **DELTA_NOT_REWRITE** | Clip `wardrobe_state` does not rewrite DNA without permanent re-lock |
| **HANDOFF_ATTACH** | Attach `wardrobe` on identity handoff when status is `locked` |
| **NO_FASHION_MODE** | No lookbook-from-logline track |
| **EROSFORGE_CONSUME** | Intimate work may read layer/condition; you do not author intimacy beats |

## Condition enum
`clean` | `worn` | `damaged` | `wet`

## Status enum
`pending` | `locked` | `drift_review`

## Inject token
`[WARDROBE_LOCK:<slug>:<look_id>] …`

## Activation Triggers
- `ACTIVATE COSTUME_WARDROBE`
- `ACTIVATE WARDROBE_CONTINUITY`
- `LOCK WARDROBE`
- After DNA extraction when clothing is visible
- Before hero still / i2v / extend with signature outfit
- After Continuity / Chain QA clothing seam flags

## Output Formats
1. Updated `dna.wardrobe_lock` (nested on Character DNA)
2. Inject blocks: compact / full / video
3. Optional handoff `wardrobe` section
4. Clip `wardrobe_state` after Go clips
5. Short status report: status, active look, condition, secondary notes, drift flags

## Integration Notes

```
DNA Extractor → Costume & Wardrobe Continuity → Identity Lock
                     ↓ inject
           Prompt Master / I2V / Extender
                     ↓ wardrobe_state
           Continuity Guardian + Chain QA
```

| Direction | Agent | Packet |
|-----------|-------|--------|
| Receives from | Character DNA Extractor, Studio Director | DNA + refs |
| Sends to | Identity Lock Specialist | `wardrobe` on identity_lock_handoff |
| Sends to | Imagine Prompt Master | wardrobe inject verbatim |
| Sends to | Continuity / Extender | lock + last clip wardrobe_state |

**Skill:** `costume-wardrobe-continuity` · **Tool:** `tools/wardrobe_lock.py` · **No CLI in v1**

**You keep the coat itself when the face is already locked.**

---
*Costume & Wardrobe Continuity — 2026-07-22 for grok-4-auto · grok-v9-4p5-multi · grok-v9-4p5-chat-expert + Imagine Video 1.0 / 1.5 Native*
````

- [ ] **Step 2: Write skill SKILL.md**

Create `.grok/skills/costume-wardrobe-continuity/SKILL.md` (four-backtick outer fence):

````markdown
---
name: costume-wardrobe-continuity
description: Structured outfit DNA wardrobe lock and inject blocks nested on Character DNA for Grok Imagine stills i2v and extend chains. Owns wardrobe_lock clip wardrobe_state and handoff wardrobe fields for primary characters. Activate with ACTIVATE COSTUME_WARDROBE or LOCK WARDROBE when clothing continuity matters. Optimized for grok-4-auto grok-v9-4p5-multi grok-v9-4p5-chat-expert with dual Imagine Video 1.0 and 1.5 Native.
---

# Costume & Wardrobe Continuity v4.5 (Grok 4.5 / v9-4p5 + Imagine Video 1.0 & 1.5 Native)

**Role Card:** `references/agents/Costume_Wardrobe_Continuity.md` (v4.5) — Authoritative source for wardrobe_lock schema, inject blocks, clip wardrobe_state, primary-only multi-cast notes, and handoff fields.

> You own **outfit DNA and wardrobe state**. Face/body stay with Identity Lock. Sets/props stay with Production Designer.

## Model Layer (Grok 4.5 / v9-4p5)

| Task type | Preferred model | Reasoning |
|-----------|-----------------|-----------|
| Lock / inject craft | `grok-v9-4p5-chat-expert` | high |
| Sequence wardrobe audit | `grok-v9-4p5-multi` | high |
| Routine status | `grok-4-auto` | medium |

**Registry:** `tools/models.py` · `references/agents/MODEL_LAYER_v4.5.md` · `models verify`

```yaml
model_compatibility:
  - grok-v9-4p5-chat-expert
  - grok-v9-4p5-multi
  - grok-4-auto
preferred_model: grok-v9-4p5-chat-expert
```

## When to Activate

- Signature outfits must survive stills → i2v → extend
- Clothing seam / outfit drift after Continuity or Chain QA
- After Character DNA Extractor when clothing is visible
- User says: `ACTIVATE COSTUME_WARDROBE`, `ACTIVATE WARDROBE_CONTINUITY`, `LOCK WARDROBE`

Begin: **"Initiating Costume & Wardrobe Continuity v4.5…"**

## Activation

`ACTIVATE COSTUME_WARDROBE`

Load and follow the Role Card. Do not paraphrase locked protocols or output structures.

## Tool-first

When Python tools are available, prefer:

- `tools/wardrobe_lock.py` — create/validate/lock/inject/clip state/handoff section
- `tools/character_dna.py` — persist DNA; identity handoff auto-attaches locked wardrobe

No dedicated CLI in v1.

## Core Protocols (v4.5)

| Protocol | Requirement |
|----------|-------------|
| **WARDROBE_FROM_VISIBLE** | Extract or confirm from refs; flag inferences |
| **ONE_ACTIVE_LOOK** | Single active_look_id |
| **PRIMARY_ONLY** | Full lock primary; secondary_notes only for others |
| **STRUCTURED_CORE** | Garments, materials, silhouette, accessories, layers, condition, delta |
| **INJECT_READY** | compact + full (+ video when needed) |
| **DELTA_NOT_REWRITE** | Clip delta ≠ DNA rewrite without permanent re-lock |
| **HANDOFF_ATTACH** | wardrobe section when locked |
| **NO_FASHION_MODE** | No ideation lookbook track |
| **MODEL_LAYER_ROUTING** | Record preferred model in status reports |
| **1.0_1.5_DUAL_SUPPORT** | Video inject usable on both pipelines |

## Integration Rules

- Upstream: Character DNA Extractor, Studio Director
- Peer: Identity Lock Specialist, Continuity Consistency Guardian, Imagine Prompt Master
- Downstream: I2V Specialist, Sequence Extender, Chain QA
- Opt-in consumer: ErosForge (layer/condition only)

## Grok Build Compatibility

Fully compatible with Grok Build CLI sessions, Termux/Android, and Kali NetHunter. Structured JSON only; no new CLI surface in v1.

**Load the Role Card** for complete protocol text and output formats.

---

*Enhanced for Grok 4.5 / v9-4p5 + dual Imagine Video 1.0 & 1.5 Native — Cinematic Studio*
````

- [ ] **Step 3: Validate skill frontmatter quickly**

Run:  
`python -c "from pathlib import Path; p=Path('.grok/skills/costume-wardrobe-continuity/SKILL.md'); t=p.read_text(); assert t.startswith('---'); assert 'name: costume-wardrobe-continuity' in t; print('ok', len(t.splitlines()), 'lines')"`  
Expected: `ok` and line count under ~500.

- [ ] **Step 4: Commit**

```bash
git add references/agents/Costume_Wardrobe_Continuity.md .grok/skills/costume-wardrobe-continuity/SKILL.md
git commit -m "feat(agents): add Costume & Wardrobe Continuity Role Card and skill"
```

---

### Task 4: Index, integration bullets, suite count, changelog

**Files:**
- Modify: `references/agents/AGENT_INDEX.md`
- Modify: `references/agents/Identity_Lock_Specialist.md` (short bullets)
- Modify: `references/agents/Continuity_Consistency_Guardian.md` (short bullets)
- Modify: `.grok/skills/identity-lock-specialist/SKILL.md`
- Modify: `.grok/skills/continuity-consistency-guardian/SKILL.md`
- Modify: `.grok/skills/character-dna-extractor/SKILL.md`
- Modify: `scripts/required_skills.manifest`
- Modify: `config/plugin_packs.yaml` (full suite blurb 51 → 52)
- Modify: `AGENTS.md` (skill count + slug row)
- Modify: `references/SKILLS_TAXONOMY.md` (51 → 52 where it states full suite size)
- Modify: `CHANGELOG.md` under Unreleased or next version section
- Optionally touch `README.md` skill-count lines only if they hardcode 51

**Interfaces:**
- Consumes: new skill slug `costume-wardrobe-continuity`
- Produces: discoverable agent in indexes; verify manifest includes skill

- [ ] **Step 1: AGENT_INDEX**

Under **Technical & Continuity** (or Production Pipeline), add a row:

| Costume & Wardrobe Continuity | `Costume_Wardrobe_Continuity.md` | chat-expert | `ACTIVATE COSTUME_WARDROBE` · `LOCK WARDROBE` |

Add activation preset row if presets table is maintained, e.g.  
`Wardrobe Lock | ACTIVATE COSTUME_WARDROBE + ACTIVATE IDENTITY_LOCK`

- [ ] **Step 2: Integration bullets (keep minimal)**

**Identity Lock Role Card** — under Integration / handoff, add:

- When `wardrobe.status == locked` (or DNA `wardrobe_lock.status`), require wardrobe inject on primary-character generations.
- Do not treat clothing drift as face-identity drift; escalate outfit issues to Costume & Wardrobe Continuity.

**Continuity Role Card** — add:

- Read last clip `wardrobe_state` + DNA `wardrobe_lock` when present; flag layer/accessory/condition seams before extend.

**Skills** — one Integration Rules bullet each pointing at `costume-wardrobe-continuity`.

**Character DNA Extractor skill** — Integration: after clothing-visible extraction, recommend `ACTIVATE COSTUME_WARDROBE` before Identity Lock for signature outfits.

- [ ] **Step 3: Manifest**

Append alphabetically-ish among non-core skills:

```
costume-wardrobe-continuity
```

Place after `continuity-consistency-guardian` (or `character-dna-extractor`) so the list stays readable.  
Do **not** mark `# core` unless verify policy requires it (default: non-core like other specialists).

- [ ] **Step 4: Count strings 51 → 52**

Update explicit “51 skills” / “51-skill” phrases in:
- `AGENTS.md`
- `config/plugin_packs.yaml` full suite description
- `references/SKILLS_TAXONOMY.md` full-suite rows
- Meta-installer skill description if it hardcodes 51
- `README.md` only where it asserts current suite size

Do **not** rewrite historical release notes for v3.8.6 (those correctly said 51 at ship time). Put new count in CHANGELOG Unreleased / next version notes.

- [ ] **Step 5: CHANGELOG**

Add under Unreleased:

```markdown
### Added
- **Costume & Wardrobe Continuity** agent (`costume-wardrobe-continuity`) — nested `wardrobe_lock` on Character DNA, inject blocks, clip `wardrobe_state`, optional identity handoff `wardrobe` section (`tools/wardrobe_lock.py`)
```

- [ ] **Step 6: Verify skill presence**

Run:  
`test -f .grok/skills/costume-wardrobe-continuity/SKILL.md && grep -n costume-wardrobe-continuity scripts/required_skills.manifest`  
Expected: file exists + manifest line.

Run: `pytest tests/test_wardrobe_lock.py tests/test_character_dna_wardrobe.py -v`  
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add references/agents/AGENT_INDEX.md \
  references/agents/Identity_Lock_Specialist.md \
  references/agents/Continuity_Consistency_Guardian.md \
  .grok/skills/identity-lock-specialist/SKILL.md \
  .grok/skills/continuity-consistency-guardian/SKILL.md \
  .grok/skills/character-dna-extractor/SKILL.md \
  scripts/required_skills.manifest \
  config/plugin_packs.yaml \
  AGENTS.md \
  references/SKILLS_TAXONOMY.md \
  CHANGELOG.md \
  README.md
# include any other files you actually edited for 51→52
git commit -m "docs(agents): index Costume & Wardrobe Continuity and bump suite to 52 skills"
```

---

### Task 5: Plugin catalog regen (if marketplace ships full suite from repo)

**Files:**
- Modify: `.grok-plugin/plugin-index.json` and related pack indexes via generator (do not hand-edit if generator owns them)

**Interfaces:**
- Consumes: `.grok/skills/costume-wardrobe-continuity/`
- Produces: catalog listing 52 skills for full suite

- [ ] **Step 1: Generate index**

Run from repo root (prefer project script):

```bash
python scripts/generate_plugin_index.py
```

If that script requires flags, use the repo’s documented equivalent:  
`python tools/cinematic_studio_cli.py plugin catalog` **or** `bash scripts/cinematic_studio.sh` plugin helpers — use whatever `docs/guides/installation_guide.md` / AGENTS.md specify for **plain generation** (not release pin).

- [ ] **Step 2: Confirm skill appears**

Run:  
`python -c "import json; from pathlib import Path; p=Path('.grok-plugin/plugin-index.json'); d=json.loads(p.read_text()); s=str(d); assert 'costume-wardrobe-continuity' in s; print('catalog ok')"`  
Expected: `catalog ok`.

If the JSON shape nests skills differently, adjust the assert to the actual structure (print keys once if needed).

- [ ] **Step 3: Optional local verify**

Run: `bash scripts/verify_cinematic_studio.sh` (or `verify --skills` if long).  
Expected: skill manifest checks include the new skill; fix only failures caused by this change.

- [ ] **Step 4: Commit catalog artifacts only if generator dirtied files**

```bash
git add .grok-plugin/
git commit -m "chore(plugins): include costume-wardrobe-continuity in marketplace catalog"
```

**Do not** run release pin (`catalog pin`) unless the user explicitly wants a release commit; plain generation is enough for the implementation branch.

---

## Spec coverage checklist (plan self-review)

| Spec requirement | Task |
|------------------|------|
| Nested `wardrobe_lock` on DNA | Task 1–2 |
| Inject compact/full/video + token | Task 1 |
| Clip `wardrobe_state` | Task 1 |
| Optional handoff `wardrobe` | Task 1–2 |
| Primary-only + secondary_notes | Task 1 schema + Task 3 Role Card |
| No fashion mode / no CLI | Global constraints + Task 3–4 |
| Role Card + skill | Task 3 |
| Identity Lock / Continuity integration | Task 4 |
| AGENT_INDEX / AGENTS | Task 4 |
| Suite 51 → 52 + manifest | Task 4–5 |
| ErosForge consume-only | Task 3 protocols |
| Python helpers chosen (not agent-docs-only) | Task 1 (explicit plan choice) |
| Handoff validator optional | Deferred — not in tasks (YAGNI; handoff section shape tested via DNA) |

## Placeholder scan

No TBD steps. Open plan choice **handoff-packet-validator** left out intentionally (design: follow-up). **Plugin pack satellite membership** left as full-suite only (skill in full suite manifest).

---

## Execution handoff

Plan complete and saved to `docs/development/superpowers/plans/2026-07-22-costume-wardrobe-continuity-implementation.md`.

**Two execution options:**

1. **Subagent-Driven (recommended)** — fresh subagent per task, review between tasks  
2. **Inline Execution** — execute tasks in this session with checkpoints  

Which approach?
