# Multi-Character Identity Arbiter (#8) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** When **2+ locked characters** share a frame or sequence, apply **conflict rules**, elect a **primary lock**, order **dual/multi DNA inject** blocks with reference weights, and expose this via tool + CLI + thin skill/Role Card.

**Architecture:** Pure `tools/multi_character_arbiter.py` loads DNA profiles, builds a cast arbitration plan (primary/secondary, weights, inject text), detects conflicts (same ref id, identical anchors, primary ambiguity). CLI under `sequence cast` (or `dna arbitrate`). Thin skill `.grok/skills/multi-character-identity-arbiter/SKILL.md` + Role Card `references/agents/Multi_Character_Identity_Arbiter.md`. Optional: wire inject string into `build_extend_prompt` via `--cast` later — v1 is plan + inject output only.

**Tech Stack:** Python 3.11+, `character_dna` loaders, `identity_drift` (optional per-char scores), Typer/Rich, pytest. No new packaging deps.

**Design:** [docs/superpowers/specs/2026-07-09-long-form-continuity-roadmap-design.md](../specs/2026-07-09-long-form-continuity-roadmap-design.md) — backlog **#8**

**Depends on:** Character DNA + Identity Lock language; memory bank cast map is optional input.

---

## Principles

1. **Tool-first** — judgment rules are coded defaults; Role Card narrates them for agents.
2. **Primary is sacred** — exactly one primary unless user forces co-primary (unsupported in v1 → error).
3. **Inject order** — primary DNA block first, then secondaries with lower ref weights; anti-merge language.
4. **YAGNI** — no face recognition; no automatic vision multi-face count; no plugin catalog pin required for pure skill add if pin is separate release step (include skill files; pin optional Task 4).
5. **TDD**.

## Out of scope

- #9 Continuity Diff CLI
- Full Identity Lock Role Card rewrite
- NSFW-specific dual-body physics (ErosForge owns that)
- Auto-detect cast from prompt NLP beyond simple name slug match

---

## Arbitration plan contract

```python
{
  "mode": "multi_character",
  "primary_slug": str,
  "primary_name": str,
  "cast": [
    {
      "slug": str,
      "name": str,
      "role": "primary" | "secondary",
      "ref_weight": float,          # 0.0–1.0
      "reference_image_id": str,
      "dna_path": str | None,
      "locked": bool,
      "inject_compact": str,        # from build_prompt_blocks compact or cinematic
    }
  ],
  "conflicts": [
    {"code": str, "severity": "info"|"warn"|"error", "message": str}
  ],
  "inject_block": str,              # full multi-character injection for prompts
  "rules_applied": list[str],
  "pass": bool,                     # False if any error conflict
}
```

### Default weight table (N characters)

| Role | Weight |
|------|--------|
| Primary | `0.75` if N==2 else `0.70` if N==3 else `0.65` |
| Secondary (equal split of remainder) | `(1.0 - primary_w) / (N-1)` rounded 2 decimals; last secondary adjusted so sum≈1.0 |

User may pass explicit `--primary` and optional `--weights slug=0.5,slug2=0.5` (must include primary).

### Conflict rules

| Code | Severity | When |
|------|----------|------|
| `missing_dna` | error | slug not found |
| `not_locked` | warn | identity_lock_status != locked |
| `shared_ref_id` | warn | two cast members same reference_image_id |
| `no_primary` | error | primary slug not in cast |
| `single_cast` | info | only 1 character — pass through single inject |
| `empty_cast` | error | no characters |
| `weight_sum` | warn | explicit weights sum outside 0.95–1.05 |

### Inject block shape

```
[MULTI_CHARACTER_LOCK]
Primary: {name} (weight={w}) — never blend facial DNA with co-stars.
Secondary: ...
Anti-merge: Distinct faces, hairstyles, wardrobes; no face morph between characters.
---
{primary cinematic or compact block}
---
{secondary blocks with "Secondary identity — lower ref weight; do not override primary face"}
```

Use `build_prompt_blocks(dna)["cinematic"]` for primary, `compact` for secondaries (or cinematic for all if short).

---

## File map

| Path | Role |
|------|------|
| `tools/multi_character_arbiter.py` | Core |
| `tools/cli/sequence_commands.py` or `dna_commands.py` | CLI — prefer **`sequence cast`** nested |
| `tests/test_multi_character_arbiter.py` | Unit tests |
| `tests/test_cli_smoke.py` | Help |
| `.grok/skills/multi-character-identity-arbiter/SKILL.md` | Thin skill |
| `references/agents/Multi_Character_Identity_Arbiter.md` | Role Card |
| `references/agents/AGENT_INDEX.md` | One row + activation |
| `CHANGELOG.md` | Unreleased |

---

### Task 1: Pure arbiter module + tests

**Files:**
- Create: `tools/multi_character_arbiter.py`
- Create: `tests/test_multi_character_arbiter.py`

- [ ] **Step 1: Failing tests**

```python
"""Tests for multi-character identity arbiter (roadmap #8)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from multi_character_arbiter import (  # noqa: E402
    arbitrate_cast,
    build_multi_inject,
)


def _dna(name: str, slug: str, *, locked: bool = True, ref: str = "", anchors: list | None = None):
    return {
        "character_name": name,
        "slug": slug,
        "core_identity": f"{name} core look",
        "facial_dna": f"{name} face signature unique",
        "hair_grooming": f"{name} hair",
        "clothing_style": f"{name} wardrobe",
        "key_consistency_anchors": anchors or [f"{name}-anchor"],
        "reference_image_ids": [ref] if ref else [],
        "identity_lock_status": "locked" if locked else "pending",
        "reference_weights": {"primary_ref_weight": 0.85},
        "version": 1,
        "schema_version": "1.0",
    }


def test_two_char_primary_first() -> None:
    plan = arbitrate_cast(
        [_dna("Liora", "liora", ref="ref_l"), _dna("Detective", "the-detective", ref="ref_d")],
        primary_slug="liora",
    )
    assert plan["pass"] is True
    assert plan["primary_slug"] == "liora"
    assert plan["cast"][0]["role"] == "primary"
    assert plan["cast"][0]["ref_weight"] >= plan["cast"][1]["ref_weight"]
    assert "MULTI_CHARACTER_LOCK" in plan["inject_block"]
    assert plan["inject_block"].index("Liora") < plan["inject_block"].index("Detective") or "Primary" in plan["inject_block"]


def test_missing_dna_error() -> None:
    plan = arbitrate_cast(
        [_dna("Liora", "liora")],
        primary_slug="ghost",
        # only one dna provided but primary ghost
    )
    # Better API: pass slugs + loader — for unit test pass dnas list and primary not in list
    plan = arbitrate_cast(
        [_dna("Liora", "liora")],
        primary_slug="the-detective",
    )
    assert plan["pass"] is False
    assert any(c["code"] == "no_primary" for c in plan["conflicts"])


def test_shared_ref_warns() -> None:
    plan = arbitrate_cast(
        [
            _dna("A", "a", ref="same_ref"),
            _dna("B", "b", ref="same_ref"),
        ],
        primary_slug="a",
    )
    assert any(c["code"] == "shared_ref_id" for c in plan["conflicts"])


def test_unlocked_warns() -> None:
    plan = arbitrate_cast(
        [_dna("A", "a", locked=False), _dna("B", "b", locked=True)],
        primary_slug="b",
    )
    assert any(c["code"] == "not_locked" for c in plan["conflicts"])
    assert plan["pass"] is True  # warn only


def test_single_cast_info() -> None:
    plan = arbitrate_cast([_dna("Solo", "solo")], primary_slug="solo")
    assert plan["pass"] is True
    assert any(c["code"] == "single_cast" for c in plan["conflicts"])


def test_build_multi_inject_contains_anti_merge() -> None:
    dnas = [_dna("Liora", "liora"), _dna("Detective", "the-detective")]
    plan = arbitrate_cast(dnas, primary_slug="liora")
    text = plan["inject_block"]
    assert "Anti-merge" in text or "anti-merge" in text.lower() or "blend" in text.lower()
```

**API design for `arbitrate_cast`:**

```python
def arbitrate_cast(
    dnas: list[dict[str, Any]],
    *,
    primary_slug: str | None = None,
    weights: dict[str, float] | None = None,
) -> dict[str, Any]:
    """
    dnas: loaded DNA dicts (must include slug).
    primary_slug: defaults to first dna slug if omitted.
    """
```

Also provide:

```python
def load_cast_dnas(slugs: list[str], *, characters_root: Path | None = None) -> list[dict]:
    """Load via character_dna.find_character_dna + load_character_dna; skip missing with empty? better raise list of missing."""
```

- [ ] **Step 2: Implement module**

Use `from character_dna import build_prompt_blocks, find_character_dna, load_character_dna, slugify`.

- [ ] **Step 3: pytest + commit**

```bash
pytest tests/test_multi_character_arbiter.py -v
git commit -m "feat(continuity): multi-character identity arbiter core"
```

---

### Task 2: CLI `sequence cast arbitrate|inject`

**Files:**
- Modify: `tools/cli/sequence_commands.py`
- Modify: `tests/test_cli_smoke.py`

- [ ] **Nested CLI**

```python
cast_app = typer.Typer(help="Multi-character identity arbitration (roadmap #8)")
app.add_typer(cast_app, name="cast")

@cast_app.command("arbitrate")
def cast_arbitrate(
    name: str = typer.Argument(..., help="Sequence name or slug"),
    characters: str = typer.Option(..., "--characters", "-c", help="Comma-separated slugs"),
    primary: str = typer.Option(None, "--primary", "-p", help="Primary slug (default first)"),
    weights: str = typer.Option(None, "--weights", help="slug=0.7,other=0.3"),
    save: bool = typer.Option(True, "--save/--no-save"),
):
    """Arbitrate cast lock for a sequence; store on sequence.cast_arbitration."""

@cast_app.command("inject")
def cast_inject(
    name: str,
    ... same cast options or read seq["cast_arbitration"],
    output: str = typer.Option(None, "--output", "-o"),
):
    """Print multi-character inject block (from saved plan or fresh arbitrate)."""
```

On arbitrate with `--save`:  
`seq["cast_arbitration"] = plan` (maybe strip huge inject for size? keep inject_block — useful).  
Update memory bank cast keys if bank present (optional): for each cast entry ensure bank cast slug exists.

Parse weights: `liora=0.7,the-detective=0.3`.

- [ ] **Smoke**

```python
def test_sequence_cast_commands_registered():
    r = run_cli("sequence", "cast", "--help")
    assert "arbitrate" in r.stdout.lower()
    assert "inject" in r.stdout.lower()
```

- [ ] **Commit**

```bash
git commit -m "feat(cli): sequence cast arbitrate and inject commands"
```

---

### Task 3: Skill + Role Card + AGENT_INDEX

**Files:**
- Create: `.grok/skills/multi-character-identity-arbiter/SKILL.md`
- Create: `references/agents/Multi_Character_Identity_Arbiter.md`
- Modify: `references/agents/AGENT_INDEX.md`
- Optional: Identity Lock Role Card one cross-link line

**SKILL.md frontmatter:**

```yaml
---
name: multi-character-identity-arbiter
description: Arbitrate primary and secondary Character DNA locks for multi-cast Grok Imagine scenes. Builds dual inject blocks and conflict reports. Activate when two or more characters share a frame or sequence.
---
```

Keep body short: activation, CLI, handoff to Identity Lock, output plan keys.

**Role Card:** v3.6.5 style short card with Model Layer include pattern, activation `ACTIVATE MULTI_CHARACTER_ARBITER`, decision frameworks matching tool rules.

**AGENT_INDEX:** specialist table row + preset optional.

- [ ] **Commit**

```bash
git commit -m "feat(agents): multi-character identity arbiter skill and role card"
```

Do **not** run plugin catalog pin unless user requests release (pin is separate hygiene).

---

### Task 4: Docs + regression

- [ ] **CHANGELOG**

```markdown
- **Multi-character identity arbiter (roadmap #8)** — `tools/multi_character_arbiter.py` primary/secondary DNA weights, conflict rules, multi inject blocks; CLI `sequence cast arbitrate|inject`; skill + Role Card
```

- [ ] **Regression**

```bash
pytest tests/test_multi_character_arbiter.py tests/test_emotional_temperature.py tests/test_audio_momentum.py tests/test_identity_drift.py tests/test_cli_smoke.py tests/test_handoff_validator.py -v
```

- [ ] **Commit** `docs: changelog for multi-character identity arbiter`

---

## Spec coverage

| Spec #8 | Task |
|---------|------|
| 2+ characters share frame/sequence | Task 1–2 |
| Conflict rules | Task 1 conflicts |
| Primary lock | Task 1 primary_slug + weights |
| Dual-DNA inject order | Task 1 inject_block |
| Skill + Role Card | Task 3 |

## Notes

- Characters on disk: `liora`, `liora-nsfw`, `the-detective` — good fixtures for manual CLI test.
- Plugin index / catalog pin deferred to release.

---

## Execution handoff

**Two execution options:**

1. **Subagent-Driven (recommended)**
2. **Inline Execution**

Which approach?
