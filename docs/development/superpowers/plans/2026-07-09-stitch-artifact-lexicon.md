# Stitch Artifact Lexicon (#11) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Shared **vocabulary + negative-prompt packs** for stitch artifacts (flicker, morph, halo, identity melt, wardrobe teleport, lighting pop) that **Imagine Prompt Master** and **Sequence Extender / re-gen** can consume.

**Architecture:** Data-first module `tools/stitch_artifact_lexicon.py` (catalog + pack builders). CLI `sequence artifact-lexicon` (list / pack / inject). Thin reference under extender skill or `references/stitch_artifact_lexicon.md`. Wire into `extend_regen.build_regen_fix_prompt` negatives section (optional merge). Effort **S**.

**Tech Stack:** Python 3.11+, Typer/Rich, pytest. No ML.

**Design:** [docs/superpowers/specs/2026-07-09-long-form-continuity-roadmap-design.md](../specs/2026-07-09-long-form-continuity-roadmap-design.md) — backlog **#11**

---

## Principles

1. **Lexicon is data** — structured entries, not a new agent personality essay.
2. **Packs are composable** — `build_negative_pack(tags)` and `build_positive_guardrails(tags)`.
3. **Map from evidence** — seam_report factors / chain QA critical keys → suggested tags.
4. **YAGNI** — no new Role Card; skill one-liners only; no catalog pin unless new skill dir required (prefer tool-only + reference md).
5. **TDD**.

## Out of scope

- #12 Arc Replan Co-pilot
- Vision-based artifact detection
- Full Prompt Master skill rewrite

---

## Lexicon entry contract

```python
{
  "id": "flicker",                 # kebab/snake id
  "name": "Temporal flicker",
  "aliases": ["strobe", "frame flicker"],
  "category": "temporal" | "identity" | "geometry" | "lighting" | "wardrobe" | "audio",
  "description": str,
  "symptoms": list[str],
  "negative_phrases": list[str],   # for negative prompt
  "positive_guards": list[str],    # affirmative continuity language
  "qa_hooks": list[str],           # e.g. stitch_artifact_risk, character_drift_boundary
}
```

### Seed catalog (minimum v1)

| id | category | focus |
|----|----------|--------|
| `flicker` | temporal | frame flashing at stitch |
| `morph` | identity | face/body melt between clips |
| `halo` | geometry | edge glow / double contour |
| `identity_melt` | identity | features blend toward co-star or prior frame |
| `wardrobe_teleport` | wardrobe | clothing change without story |
| `lighting_pop` | lighting | sudden key/color shift |
| `prop_pop` | geometry | props appear/disappear |
| `lip_desync` | audio | mouth out of phase (1.5) |
| `motion_hitch` | temporal | velocity discontinuity |
| `resolution_swim` | temporal | soft/sharp pumping |

---

## API

```python
LEXICON: dict[str, Entry]  # or list + index

def list_entries(*, category: str | None = None) -> list[dict]
def get_entry(entry_id: str) -> dict | None
def build_negative_pack(entry_ids: list[str] | None = None, *, all_default: bool = False) -> str
def build_positive_guards(entry_ids: list[str] | None = None) -> str
def suggest_entries_from_seam(seam_report: dict | None) -> list[str]
def suggest_entries_from_chain_qa(chain_qa: dict | None) -> list[str]
def format_lexicon_markdown(entry_ids: list[str] | None = None) -> str
```

**Default pack** when `all_default=True` or empty ids for extend: core set  
`flicker, morph, halo, identity_melt, wardrobe_teleport, lighting_pop, motion_hitch`.

**suggest_from_seam:** map factors text:
- morph/halo/flicker keywords → ids
- high seam_risk → full default pack

**suggest_from_chain_qa:** critical `character_drift_boundary` → identity_melt, morph; `stitch_artifact_risk` → flicker, halo, motion_hitch; etc.

---

## File map

| Path | Role |
|------|------|
| `tools/stitch_artifact_lexicon.py` | Catalog + builders |
| `tools/cli/sequence_commands.py` | `artifact-lexicon` command group or flat |
| `tools/extend_regen.py` | Optional: append pack to REGEN_FIX negatives |
| `tests/test_stitch_artifact_lexicon.py` | Unit tests |
| `tests/test_cli_smoke.py` | Help |
| `references/stitch_artifact_lexicon.md` | Human/agent reference (optional mirror of catalog) |
| `.grok/skills/imagine-prompt-master/SKILL.md` or cinematic-sequence-extender | One consume line |
| `CHANGELOG.md` | Unreleased |

---

### Task 1: Lexicon module + tests

**Files:**
- Create: `tools/stitch_artifact_lexicon.py`
- Create: `tests/test_stitch_artifact_lexicon.py`

- [ ] **Tests**

```python
def test_catalog_has_core_entries():
    ids = {e["id"] for e in list_entries()}
    assert {"flicker", "morph", "halo", "identity_melt"}.issubset(ids)

def test_negative_pack_contains_phrases():
    pack = build_negative_pack(["flicker", "morph"])
    assert "flicker" in pack.lower() or "temporal" in pack.lower()
    assert len(pack) > 20

def test_suggest_from_seam_morph_factor():
    ids = suggest_entries_from_seam({"factors": ["morph risk at boundary"], "seam_risk": 7})
    assert "morph" in ids or "flicker" in ids

def test_default_pack_nonempty():
    assert build_negative_pack(all_default=True)
```

- [ ] **Implement** full seed catalog + builders

- [ ] **Commit** `feat(continuity): stitch artifact lexicon and negative packs`

---

### Task 2: CLI + optional extend_regen wire + skill lines

**CLI** (nested preferred):

```python
lex_app = typer.Typer(help="Stitch artifact lexicon (roadmap #11)")
app.add_typer(lex_app, name="artifact-lexicon")

@lex_app.command("list")
# optional --category

@lex_app.command("pack")
# --tags flicker,morph OR --all; --positives; print pack

@lex_app.command("suggest")
# sequence name + --clip: read seam_report + chain_qa, print suggested tags + pack
```

**extend_regen.py:** In `build_regen_fix_prompt` NEGATIVES line, append  
`build_negative_pack(suggest_from_seam + suggest_from_chain_qa)` or default pack if no tags.

**Skill one-liners:** imagine-prompt-master and/or cinematic-sequence-extender:
```bash
cinematic-studio sequence artifact-lexicon pack --all
```

- [ ] **Commit** `feat(cli): sequence artifact-lexicon commands`

---

### Task 3: Docs + regression

- [ ] Optional `references/stitch_artifact_lexicon.md` generated summary (or hand-written short)

- [ ] **CHANGELOG**

```markdown
- **Stitch artifact lexicon (roadmap #11)** — `tools/stitch_artifact_lexicon.py` vocabulary + negative/positive packs for flicker/morph/halo; CLI `sequence artifact-lexicon`; re-gen prompts consume suggested packs
```

- [ ] **Regression**

```bash
pytest tests/test_stitch_artifact_lexicon.py tests/test_extend_regen.py tests/test_cli_smoke.py -v
```

- [ ] **Commit** `docs: changelog for stitch artifact lexicon`

---

## Spec coverage

| Spec #11 | Task |
|----------|------|
| Shared vocabulary | Task 1 catalog |
| Negative-prompt packs | Task 1–2 pack |
| Prompt Master / Extender consume | Task 2 CLI + skill + regen wire |

---

## Execution handoff

**Two execution options:**

1. **Subagent-Driven (recommended)**
2. **Inline Execution**

Which approach?
