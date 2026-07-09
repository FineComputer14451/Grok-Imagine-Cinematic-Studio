# Emotional Temperature Gate (#7) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enforce `emotional_temperature_curve` against planned beats at extend time — warn when the arc goes **flat** or **spikes** without plan — via a pure gate tool + CLI + light assist/evidence hook.

**Architecture:** `tools/emotional_temperature.py` owns curve schema normalize, planned temp lookup, observed temp inference (from momentum/memory/prompt labels), and gate report. CLI `sequence temp-gate` and `sequence temp-set`. Optional: store report on clip; extend-prompt can append planned temperature note. No new Role Card; Narrative Arc skill one-liner only.

**Tech Stack:** Python 3.11+, `sequence_chain` curve field, memory bank emotion, Typer/Rich, pytest.

**Design:** [docs/superpowers/specs/2026-07-09-long-form-continuity-roadmap-design.md](../specs/2026-07-09-long-form-continuity-roadmap-design.md) — backlog **#7**

**Depends on:** #4 memory bank (optional observed signal); works without it.

---

## Principles

1. **Define curve shape** — today `emotional_temperature_curve` is always `[]`; gate needs a stable point schema.
2. **Warn, don’t hard-block by default** — `pass` may be False with severity `warn` / `fail`; CLI exit 0 on warn, exit 1 only with `--strict`.
3. **Observed is heuristic** — map `momentum_vector.emotional_state` + bank emotion + known labels to 0–10; unknown → null observed (skip spike check, flag “unobserved”).
4. **YAGNI** — no LLM calls; no auto-replan (#12); no Web UI.
5. **TDD**.

## Out of scope

- #8 Multi-Character Identity Arbiter
- #12 Arc Replan Co-pilot (consumes gate output later)
- Auto-writing full Narrative Arc Role Card rewrites
- Forcing curve on every `sequence init` (optional empty stays valid)

---

## Curve point contract

```python
# sequence["emotional_temperature_curve"] : list[dict]
{
  "index": int,              # clip index this target applies to (required)
  "temp": float,             # 0.0–10.0 planned emotional intensity (required)
  "label": str,              # optional free text e.g. "dread rising"
  "beat": str,               # optional narrative beat id/name
}
```

**Normalize rules (`normalize_curve(raw)`):**
- Accept list of dicts as above
- Also accept legacy list of bare numbers → `[{index:i, temp:float(v)} for i,v in enumerate]`
- Also accept list of `{t, temperature, emotion}` aliases → map to index/temp/label
- Sort by index; drop invalid points (missing temp)
- Clamp temp to 0–10

**Planned temp at clip index:** exact index match; else interpolate between nearest neighbors; else None if curve empty.

---

## Observed temperature

`infer_observed_temp(clip, memory_bank=None) -> float | None`

1. Prefer numeric if clip has `emotional_temperature` or `qa_scores.emotion_temp`
2. Else parse `momentum_vector.emotional_state` via keyword map:

```python
LABEL_TEMP = {
  "numb": 1, "flat": 1, "calm": 2, "wary": 3, "tense": 5,
  "anxious": 6, "fear": 7, "dread": 7, "rage": 9, "ecstatic": 9,
  "hopeful": 4, "grief": 6, "tender": 3, "urgent": 6, "panicked": 8,
  "determined": 5, "intimate": 4, "euphoric": 9, "despair": 8,
}
```

Substring match (case-insensitive); if multiple hits take max.  
3. Else memory bank `emotion.last_emotional_state` same map.  
4. Else None.

---

## Gate report contract

```python
{
  "clip_id": str | None,
  "clip_index": int,
  "planned_temp": float | None,
  "observed_temp": float | None,
  "delta": float | None,          # observed - planned
  "pass": bool,                   # True if no fail-level issues
  "severity": "ok" | "warn" | "fail",
  "flags": list[str],             # "flat_arc", "unplanned_spike", "unplanned_drop", "missing_curve", "unobserved", "off_plan"
  "factors": list[str],
  "fixes": list[str],
  "curve_length": int,
  "suggested_emotion_score": float,  # 1–10 for optional future QA; not a chain QA key today
}
```

### Gate rules (`evaluate_temperature_gate(seq, clip, *, previous_clip=None)`)

| Condition | severity | flag |
|-----------|----------|------|
| Curve empty | warn | missing_curve |
| Planned None (empty curve) | warn | missing_curve |
| Observed None | warn | unobserved |
| abs(delta) > 2.5 | warn | off_plan |
| abs(delta) > 4.0 | fail | off_plan |
| Spike: observed - prev_observed > 3.0 AND planned rise < 1.5 | fail | unplanned_spike |
| Drop: prev_observed - observed > 3.0 AND planned drop < 1.5 | warn | unplanned_drop |
| Flat: last 3 observed (or planned) temps all within 0.5 and sequence has ≥3 clips with curve span ≥3 points | warn | flat_arc |

`pass = severity != "fail"`  
`suggested_emotion_score`: if planned and observed, `10 - min(10, abs(delta)*1.5)`; else 7.0 default warn path.

---

## File map

| Path | Role |
|------|------|
| `tools/emotional_temperature.py` | Curve + gate |
| `tools/cli/sequence_commands.py` | `temp-gate`, `temp-set` |
| `tools/sequence_chain.py` | Optional: docstring on scaffold field; no schema bump required |
| `tests/test_emotional_temperature.py` | Unit tests |
| `tests/test_cli_smoke.py` | Help |
| `CHANGELOG.md` | Unreleased |
| Optional skill one-liner | narrative-arc or sequence-director |

---

### Task 1: Pure emotional_temperature module + tests

**Files:**
- Create: `tools/emotional_temperature.py`
- Create: `tests/test_emotional_temperature.py`

- [ ] **Step 1: Failing tests**

```python
"""Tests for emotional temperature gate (roadmap #7)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from emotional_temperature import (  # noqa: E402
    evaluate_temperature_gate,
    infer_observed_temp,
    normalize_curve,
    planned_temp_at,
)
from sequence_chain import create_clip, create_sequence_scaffold  # noqa: E402


def test_normalize_bare_numbers() -> None:
    curve = normalize_curve([2, 5, 8])
    assert len(curve) == 3
    assert curve[0]["index"] == 0 and curve[0]["temp"] == 2.0
    assert curve[2]["temp"] == 8.0


def test_normalize_dicts() -> None:
    curve = normalize_curve([
        {"index": 1, "temp": 4, "label": "wary"},
        {"index": 0, "temp": 2, "beat": "open"},
    ])
    assert curve[0]["index"] == 0
    assert curve[1]["label"] == "wary"


def test_planned_temp_exact_and_interp() -> None:
    curve = normalize_curve([
        {"index": 0, "temp": 2},
        {"index": 2, "temp": 8},
    ])
    assert planned_temp_at(curve, 0) == 2.0
    assert planned_temp_at(curve, 2) == 8.0
    mid = planned_temp_at(curve, 1)
    assert mid is not None and 4.5 <= mid <= 5.5


def test_infer_observed_from_momentum() -> None:
    clip = create_clip()
    clip["momentum_vector"]["emotional_state"] = "rising dread"
    t = infer_observed_temp(clip)
    assert t is not None and t >= 6.0


def test_gate_missing_curve_warns() -> None:
    seq = create_sequence_scaffold("Emo")
    clip = create_clip()
    clip["index"] = 0
    report = evaluate_temperature_gate(seq, clip)
    assert report["severity"] in ("warn", "ok")
    assert "missing_curve" in report["flags"] or report["curve_length"] == 0


def test_gate_unplanned_spike_fails() -> None:
    seq = create_sequence_scaffold("Spike")
    seq["emotional_temperature_curve"] = normalize_curve([
        {"index": 0, "temp": 3},
        {"index": 1, "temp": 3.5},  # planned nearly flat
    ])
    prev = create_clip()
    prev["index"] = 0
    prev["momentum_vector"]["emotional_state"] = "calm"
    clip = create_clip()
    clip["index"] = 1
    clip["clip_id"] = "clip_002"
    clip["momentum_vector"]["emotional_state"] = "panicked rage"
    report = evaluate_temperature_gate(seq, clip, previous_clip=prev)
    assert report["severity"] == "fail"
    assert "unplanned_spike" in report["flags"]
    assert report["pass"] is False


def test_gate_on_plan_passes() -> None:
    seq = create_sequence_scaffold("Ok")
    seq["emotional_temperature_curve"] = normalize_curve([
        {"index": 0, "temp": 3},
        {"index": 1, "temp": 7},
    ])
    prev = create_clip()
    prev["index"] = 0
    prev["momentum_vector"]["emotional_state"] = "wary"
    clip = create_clip()
    clip["index"] = 1
    clip["momentum_vector"]["emotional_state"] = "dread"
    report = evaluate_temperature_gate(seq, clip, previous_clip=prev)
    assert report["pass"] is True
    assert report["severity"] in ("ok", "warn")
```

- [ ] **Step 2: Implement module** with helpers above; tune keyword map so spike test fails and on-plan passes.

- [ ] **Step 3: pytest + commit**

```bash
pytest tests/test_emotional_temperature.py -v
git add tools/emotional_temperature.py tests/test_emotional_temperature.py
git commit -m "feat(continuity): emotional temperature gate core"
```

---

### Task 2: CLI temp-set / temp-gate + optional extend-prompt note

**Files:**
- Modify: `tools/cli/sequence_commands.py`
- Modify: `tests/test_cli_smoke.py`
- Optional: `tools/sequence_chain.py` `build_extend_prompt` append planned temp line

- [ ] **Step 1: CLI**

Nested or flat:

```python
# Preferred nested
temp_app = typer.Typer(help="Emotional temperature curve gate (roadmap #7)")
app.add_typer(temp_app, name="temp")

@temp_app.command("set")
def temp_set(
    name: str,
    index: int = typer.Option(..., "--index", "-i"),
    temp: float = typer.Option(..., "--temp", "-t"),
    label: str = typer.Option("", "--label"),
    beat: str = typer.Option("", "--beat"),
):
    """Upsert a curve point for a clip index."""
    # normalize, replace same index, sort, save

@temp_app.command("show")
def temp_show(name: str):
    """Show normalized emotional temperature curve."""

@temp_app.command("gate")
def temp_gate(
    name: str,
    clip: str = typer.Option(..., "--clip", "-c"),
    strict: bool = typer.Option(False, "--strict"),
):
    """Evaluate temperature gate for a clip."""
    # report, store clip["temperature_gate"], save
    # exit 1 if strict and not pass
```

- [ ] **Step 2: Smoke tests** for `sequence temp --help` with set/show/gate

- [ ] **Step 3: Optional extend-prompt**

In `build_extend_prompt`, after memory bank block:

```python
from emotional_temperature import normalize_curve, planned_temp_at
curve = normalize_curve(seq.get("emotional_temperature_curve"))
# next clip index = previous_clip.index + 1
pt = planned_temp_at(curve, previous_clip.get("index", 0) + 1)
if pt is not None:
    lines.append(f"PLANNED_EMOTIONAL_TEMPERATURE: {pt:.1f}/10")
```

Keep import soft/local to avoid cycles.

- [ ] **Step 4: Commit**

```bash
git commit -m "feat(cli): sequence temp set show and gate commands"
```

---

### Task 3: Docs + regression

- [ ] **CHANGELOG:**

```markdown
- **Emotional temperature gate (roadmap #7)** — `tools/emotional_temperature.py` normalizes `emotional_temperature_curve`, infers observed temp, flags flat/spike/off-plan; CLI `sequence temp set|show|gate`; extend prompts may include planned temperature
```

- [ ] **Optional skill note** in `narrative-arc-pacing-strategist` or `sequence-director` SKILL.md (one line)

- [ ] **Regression:**

```bash
pytest tests/test_emotional_temperature.py tests/test_audio_momentum.py tests/test_extend_regen.py tests/test_sequence_memory.py tests/test_sequence_chain_memory.py tests/test_identity_drift.py tests/test_seam_report.py tests/test_chain_qa_assist.py tests/test_cli_smoke.py tests/test_handoff_validator.py -v
```

- [ ] **Commit:** `docs: changelog for emotional temperature gate`

---

## Spec coverage

| Spec #7 | Task |
|---------|------|
| Enforce curve vs beats at extend | Task 1–2 gate + optional prompt |
| Warn flat arc | Task 1 flat_arc rule |
| Warn/fail spikes without plan | Task 1 unplanned_spike |
| Tool + skill touch | Task 2 CLI + optional skill line |

## Hooks for #12

Gate report `flags` / `fixes` feed Arc Replan later — do not implement replan here.

---

## Execution handoff

**Two execution options:**

1. **Subagent-Driven (recommended)**
2. **Inline Execution**

Which approach?
