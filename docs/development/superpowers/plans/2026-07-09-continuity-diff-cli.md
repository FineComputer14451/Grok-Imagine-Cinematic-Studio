# Continuity Diff CLI (#9) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Human-readable **clip-to-clip (and clip-to-memory-bank) diffs** of `continuity_state`, momentum, AMV, and memory bank projections for Continuity Guardian / QA — without inventing a new agent.

**Architecture:** Pure `tools/continuity_diff.py` builds structured change lists + markdown report. CLI `sequence continuity-diff` (alias-friendly). Optional store on clip as `continuity_diff`. Strengthen Continuity Guardian skill with one CLI line. Effort **S**.

**Tech Stack:** Python 3.11+, existing clip fields + `sequence_memory.mirror_bank_to_continuity_state` / `ensure_memory_bank`, Typer/Rich, pytest.

**Design:** [docs/superpowers/specs/2026-07-09-long-form-continuity-roadmap-design.md](../specs/2026-07-09-long-form-continuity-roadmap-design.md) — backlog **#9**

**Depends on:** #4 memory bank (optional compare mode).

---

## Principles

1. **Diff, don’t score** — leave scoring to chain QA / drift / seam / AMV tools; this reports **what changed**.
2. **Stable change records** — each change: `path`, `before`, `after`, `kind` (`added`|`removed`|`changed`|`unchanged` summary only for counts).
3. **Human + machine** — `diff_continuity(...)` returns dict; `format_continuity_diff_markdown(report)` for CLI/Guardian.
4. **YAGNI** — no pixel diff, no git binary, no Web UI, no schema bump.
5. **TDD**.

## Out of scope

- #10 Long-Form Health Dashboard (can consume this report later)
- Auto-fix of continuity_state
- NSFW clothing-displacement specialized diff (generic dict/list diff is enough)

---

## Report contract

```python
{
  "mode": "clip_pair" | "clip_vs_bank" | "bank_snapshot",
  "left_label": str,          # e.g. clip_001
  "right_label": str,         # e.g. clip_002 or "memory_bank"
  "changes": [
    {
      "path": str,            # e.g. "continuity_state.location", "momentum_vector.lighting_state", "audio_momentum_vector.dialogue_state", "memory.environment.props"
      "kind": "added" | "removed" | "changed",
      "before": Any,
      "after": Any,
    }
  ],
  "summary": {
    "added": int,
    "removed": int,
    "changed": int,
    "total": int,
  },
  "sections_compared": list[str],
  "warnings": list[str],      # e.g. empty continuity_state both sides
}
```

### Compare surfaces (clip_pair)

For left=previous clip, right=current clip:

| Path prefix | Source |
|-------------|--------|
| `continuity_state.*` | flat dict keys (stringify values) |
| `momentum_vector.*` | scalar keys only; lists as joined string |
| `audio_momentum_vector.*` | same |
| `reference_image_id` | top-level |
| `last_frame_recap` | optional short hash/len + first 80 chars if changed |

### clip_vs_bank

Right side = flattened projection:

- `mirror_bank_to_continuity_state(bank)` → under `continuity_state.*` paths  
- Plus bank lighting/emotion/audio under `memory.*` vs current clip momentum/AMV where applicable

Or simpler v1: only compare `mirror_bank_to_continuity_state(bank)` vs `clip.continuity_state`.

### Diff algorithm

```python
def _scalar(v) -> str:
    if v is None: return ""
    if isinstance(v, list): return ", ".join(str(x) for x in v)
    return str(v).strip()

def diff_maps(left: dict, right: dict, prefix: str) -> list[change]:
    # union of keys; skip both empty
```

Props list: treat as set for kind, but report before/after as sorted lists for stability.

---

## File map

| Path | Role |
|------|------|
| `tools/continuity_diff.py` | Core |
| `tools/cli/sequence_commands.py` | `continuity-diff` command |
| `tests/test_continuity_diff.py` | Unit tests |
| `tests/test_cli_smoke.py` | Help |
| `.grok/skills/continuity-consistency-guardian/SKILL.md` | CLI line |
| `CHANGELOG.md` | Unreleased |

---

### Task 1: Pure continuity_diff module + tests

**Files:**
- Create: `tools/continuity_diff.py`
- Create: `tests/test_continuity_diff.py`

- [ ] **Step 1: Tests**

```python
"""Tests for continuity diff (roadmap #9)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from continuity_diff import (  # noqa: E402
    diff_clip_pair,
    diff_clip_vs_bank,
    format_continuity_diff_markdown,
)
from sequence_chain import create_clip  # noqa: E402
from sequence_memory import empty_memory_bank  # noqa: E402


def test_clip_pair_detects_location_change() -> None:
    prev = create_clip()
    prev["clip_id"] = "clip_001"
    prev["continuity_state"] = {"location": "Alley", "props": ["umbrella"]}
    prev["momentum_vector"]["lighting_state"] = "neon"
    curr = create_clip()
    curr["clip_id"] = "clip_002"
    curr["continuity_state"] = {"location": "Rooftop", "props": ["umbrella", "phone"]}
    curr["momentum_vector"]["lighting_state"] = "neon"
    report = diff_clip_pair(prev, curr)
    assert report["mode"] == "clip_pair"
    assert report["summary"]["total"] >= 1
    paths = {c["path"] for c in report["changes"]}
    assert any("location" in p for p in paths)
    assert any("props" in p for p in paths)


def test_no_changes_empty_summary() -> None:
    a = create_clip()
    a["continuity_state"] = {"location": "Dock"}
    b = create_clip()
    b["continuity_state"] = {"location": "Dock"}
    report = diff_clip_pair(a, b)
    assert report["summary"]["changed"] == 0 or report["summary"]["total"] == 0


def test_markdown_contains_headers() -> None:
    prev = create_clip()
    prev["clip_id"] = "clip_001"
    prev["continuity_state"] = {"location": "A"}
    curr = create_clip()
    curr["clip_id"] = "clip_002"
    curr["continuity_state"] = {"location": "B"}
    md = format_continuity_diff_markdown(diff_clip_pair(prev, curr))
    assert "Continuity Diff" in md or "continuity" in md.lower()
    assert "location" in md.lower()


def test_clip_vs_bank_prop_gap() -> None:
    bank = empty_memory_bank()
    bank["environment"]["location"] = "Neon alley"
    bank["environment"]["props"] = ["key", "coat"]
    clip = create_clip()
    clip["clip_id"] = "clip_003"
    clip["continuity_state"] = {"location": "Neon alley", "props": ["key"]}
    report = diff_clip_vs_bank(clip, bank)
    assert report["mode"] == "clip_vs_bank"
    assert report["summary"]["total"] >= 1
```

- [ ] **Step 2: Implement**

```python
def diff_clip_pair(left_clip, right_clip) -> dict: ...
def diff_clip_vs_bank(clip, memory_bank) -> dict: ...
def format_continuity_diff_markdown(report) -> str: ...
def format_continuity_diff_table_rows(report) -> list[tuple]:  # optional for Rich
```

- [ ] **Commit**

```bash
git commit -m "feat(continuity): continuity state diff report core"
```

---

### Task 2: CLI `sequence continuity-diff`

**Files:**
- Modify: `tools/cli/sequence_commands.py`
- Modify: `tests/test_cli_smoke.py`
- Modify: continuity guardian SKILL.md

- [ ] **CLI**

```python
@app.command("continuity-diff")
def seq_continuity_diff(
    name: str = typer.Argument(...),
    clip: str = typer.Option(..., "--clip", "-c", help="Right-hand clip ID"),
    against: str = typer.Option(
        "prev",
        "--against",
        help="prev | bank | <clip_id>",
    ),
    save: bool = typer.Option(False, "--save", help="Store report on right clip"),
    output: str = typer.Option(None, "--output", "-o", help="Write markdown file"),
):
    """Diff continuity_state / momentum / AMV for Continuity Guardian (roadmap #9)."""
```

Logic:
- `against=prev` → previous index clip; error if opening
- `against=bank` → `diff_clip_vs_bank`
- else resolve as clip id for left

Print Rich table of changes + summary; print markdown panel truncated; optional save `clip["continuity_diff"] = report`.

- [ ] **Smoke:** `"continuity-diff" in sequence --help`

- [ ] **Skill one-liner** under Continuity Guardian sequence chain section:

```bash
python tools/cinematic_studio_cli.py sequence continuity-diff "Sequence Name" --clip clip_002
```

- [ ] **Commit**

```bash
git commit -m "feat(cli): sequence continuity-diff command"
```

---

### Task 3: Docs + regression

- [ ] **CHANGELOG**

```markdown
- **Continuity diff CLI (roadmap #9)** — `tools/continuity_diff.py` clip-to-clip and clip-vs-memory-bank continuity reports; CLI `sequence continuity-diff` for Continuity Guardian / QA
```

- [ ] **Regression**

```bash
pytest tests/test_continuity_diff.py tests/test_sequence_memory.py tests/test_cli_smoke.py tests/test_handoff_validator.py -v
```

- [ ] **Commit** `docs: changelog for continuity diff CLI`

---

## Spec coverage

| Spec #9 | Task |
|---------|------|
| continuity_state / memory bank diff | Task 1 |
| clip-to-clip | Task 1 `diff_clip_pair` |
| Human-readable report | Task 1–2 markdown + CLI |
| Continuity Guardian strengthen | Task 2 skill line |

## Hooks for #10

Health dashboard can count `continuity_diff.summary.total` per clip — do not implement here.

---

## Execution handoff

**Two execution options:**

1. **Subagent-Driven (recommended)**
2. **Inline Execution**

Which approach?
