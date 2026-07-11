# Long-Form Health Dashboard (#10) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Per-sequence **long-form health dashboard**: chain QA status, drift trend, seam risks, re-gen counts, continuity diffs, temperature/AMV gates, and **estimated remaining cost** — in one CLI view (and structured dict for reports).

**Architecture:** Pure aggregator `tools/sequence_health_dashboard.py` reads existing clip fields from #1–#9 (no re-scoring). Upgrade `sequence health` CLI to render Rich tables + optional `--json` / `--markdown`. Reuse `estimate_sequence_cost` / quota helpers for remaining cost.

**Tech Stack:** Python 3.11+, existing sequence JSON fields, `quota_optimizer.estimate_sequence_cost`, Typer/Rich, pytest.

**Design:** [docs/superpowers/specs/2026-07-09-long-form-continuity-roadmap-design.md](../specs/2026-07-09-long-form-continuity-roadmap-design.md) — backlog **#10**

**Depends on:** #1–#9 fields optional (dashboard degrades gracefully if missing).

---

## Principles

1. **Aggregate only** — never re-run expensive scorers; read stored `identity_drift`, `seam_report`, `audio_momentum_report`, `regen`, `temperature_gate`, `continuity_diff`, `chain_qa`.
2. **One command** — expand existing `sequence health` (do not invent a second top-level name); keep brief mode default friendly.
3. **Graceful nulls** — missing evidence → `—` / null, not errors.
4. **YAGNI** — no Web UI Streamlit page in v1; no new Role Card; no catalog pin.
5. **TDD**.

## Out of scope

- #11 Stitch Artifact Lexicon
- #12 Arc Replan
- Live quota API sync beyond existing estimate helpers
- Auto-running drift/seam for every clip on health view

---

## Dashboard report contract

```python
{
  "sequence_name": str,
  "slug": str,
  "generated_at": iso,
  "health_score": float | None,          # sequence_health_score after update
  "chain_qa_status": str,
  "clip_count": int,
  "target_duration_seconds": int,
  "clips_approved": int,
  "clips_qa_hold": int,
  "clips_pending": int,
  "chain_qa": {
    "go": int, "no_go": int, "conditional_go": int, "pending": int,
    "avg_weighted_score": float | None,
  },
  "drift": {
    "samples": int,
    "avg_score": float | None,
    "max_score": float | None,
    "fail_count": int,                   # pass == False
    "trend": list[float],                # per-clip drift_score in index order (nulls skipped or use None)
  },
  "seam": {
    "samples": int,
    "avg_risk": float | None,
    "max_risk": float | None,
    "fail_count": int,
  },
  "audio_momentum": {
    "samples": int,
    "avg_integrity": float | None,
    "fail_count": int,
  },
  "regen": {
    "clips_with_attempts": int,
    "total_attempts": int,
    "sequence_attempts_used": int,
    "budget_exhausted_clips": int,
  },
  "temperature": {
    "samples": int,
    "fail_count": int,
    "warn_count": int,
  },
  "continuity_diff": {
    "clips_with_diff": int,
    "total_changes": int,
  },
  "cost": {
    "estimate": dict | None,             # from estimate_sequence_cost if clips present
    "remaining_clips": int,              # not approved
    "remaining_duration_seconds": int,
    "credits_low": float | None,
    "credits_high": float | None,
    "usd_low": float | None,
    "usd_high": float | None,
  },
  "clip_rows": [                         # for table
    {
      "clip_id": str,
      "index": int,
      "status": str,
      "qa_decision": str | None,
      "weighted_score": float | None,
      "drift_score": float | None,
      "seam_risk": float | None,
      "amv_integrity": float | None,
      "regen_attempts": int,
      "temp_severity": str | None,
      "cont_diff_total": int | None,
    }
  ],
  "alerts": list[str],                   # human one-liners for red flags
}
```

### Aggregation rules

```python
def build_longform_health(seq: dict) -> dict:
    # optionally call update_sequence_health first from CLI not pure builder
    for clip in seq["clips"]:
        # read nested fields safely
    # remaining cost: estimate_sequence_cost on clips where status not in approved/go
    # or full sequence estimate minus rough spent — prefer estimate on remaining clip durations only
```

**Remaining cost (simple):**  
`remaining = [c for c in clips if c.status not in ("approved",)]`  
`estimate_sequence_cost(remaining_clip_dicts)` — pass list of duration specs as existing API expects.

Check `estimate_sequence_cost` signature:

```python
# tools/quota_optimizer.py
def estimate_sequence_cost(clips_or_specs, fast_mode=False, quality_pass=False) -> dict
```

Use remaining clips' `duration_seconds`.

**Alerts examples:**
- any no_go
- drift max >= 2.5
- seam fail_count > 0
- regen budget exhausted
- temperature fail

---

## File map

| Path | Role |
|------|------|
| `tools/sequence_health_dashboard.py` | Builder + markdown formatter |
| `tools/cli/sequence_commands.py` | Expand `seq_health` |
| `tests/test_sequence_health_dashboard.py` | Unit tests |
| `tests/test_cli_smoke.py` | optional help still has health |
| `CHANGELOG.md` | Unreleased |

---

### Task 1: Pure dashboard builder + tests

**Files:**
- Create: `tools/sequence_health_dashboard.py`
- Create: `tests/test_sequence_health_dashboard.py`

- [ ] **Step 1: Tests**

```python
"""Tests for long-form health dashboard (roadmap #10)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from sequence_chain import (  # noqa: E402
    add_clip_to_sequence,
    create_clip,
    create_sequence_scaffold,
    update_sequence_health,
)
from sequence_health_dashboard import (  # noqa: E402
    build_longform_health,
    format_longform_health_markdown,
)


def test_empty_sequence_dashboard() -> None:
    seq = create_sequence_scaffold("Empty Dash")
    report = build_longform_health(seq)
    assert report["clip_count"] == 0
    assert report["chain_qa"]["pending"] == 0
    assert report["slug"] == seq["slug"]


def test_aggregates_drift_seam_regen() -> None:
    seq = create_sequence_scaffold("Health Seq")
    c0 = create_clip(prompt="open", last_frame_recap="wide")
    c0["status"] = "approved"
    c0["chain_qa"] = {"decision": "go", "weighted_score": 8.5}
    c0["identity_drift"] = {"drift_score": 1.0, "pass": True}
    c0["seam_report"] = {"seam_risk": 2.0, "pass": True}
    add_clip_to_sequence(seq, c0)

    c1 = create_clip(prompt="extend", last_frame_recap="close")
    c1["status"] = "qa_hold"
    c1["chain_qa"] = {"decision": "no_go", "weighted_score": 4.0}
    c1["identity_drift"] = {"drift_score": 3.5, "pass": False}
    c1["seam_report"] = {"seam_risk": 6.0, "pass": False}
    c1["regen"] = {"attempts": 1, "max_attempts": 2}
    c1["audio_momentum_report"] = {"integrity_score": 5.0, "pass": False}
    c1["temperature_gate"] = {"severity": "fail", "pass": False}
    c1["continuity_diff"] = {"summary": {"total": 3}}
    add_clip_to_sequence(seq, c1)

    seq["regen_budget"] = {"sequence_attempts_used": 1, "max_attempts_per_clip": 2}
    update_sequence_health(seq)

    report = build_longform_health(seq)
    assert report["clip_count"] == 2
    assert report["chain_qa"]["no_go"] >= 1
    assert report["drift"]["fail_count"] >= 1
    assert report["drift"]["max_score"] == 3.5
    assert report["seam"]["fail_count"] >= 1
    assert report["regen"]["total_attempts"] >= 1
    assert report["audio_momentum"]["fail_count"] >= 1
    assert report["temperature"]["fail_count"] >= 1
    assert report["continuity_diff"]["total_changes"] >= 3
    assert len(report["clip_rows"]) == 2
    assert any("no_go" in a.lower() or "drift" in a.lower() for a in report["alerts"])
    assert report["cost"]["remaining_clips"] >= 1


def test_markdown_includes_title() -> None:
    seq = create_sequence_scaffold("MD Seq")
    md = format_longform_health_markdown(build_longform_health(seq))
    assert "MD Seq" in md or "Health" in md
```

- [ ] **Step 2: Implement builder**

Safely dig nested dicts; build alerts; call `estimate_sequence_cost` for remaining clips (list of `{"duration_seconds": n}` or full clips as API allows).

- [ ] **Commit**

```bash
git commit -m "feat(continuity): long-form sequence health dashboard builder"
```

---

### Task 2: Expand `sequence health` CLI

**Files:**
- Modify: `tools/cli/sequence_commands.py` `seq_health`
- Modify: `tests/test_cli_smoke.py` if needed (health already registered)

```python
@app.command("health")
def seq_health(
    name: str = typer.Argument(...),
    json_out: bool = typer.Option(False, "--json"),
    markdown: bool = typer.Option(False, "--markdown"),
    output: str = typer.Option(None, "--output", "-o"),
):
    """Long-form health dashboard — QA, drift, seam, regen, cost (roadmap #10)."""
    seq = require_sequence(name)
    update_sequence_health(seq)
    report = build_longform_health(seq)
    save_sequence(seq)  # persist refreshed health score

    if json_out:
        console.print_json(data=report)  # or print json.dumps
        ...
    # Rich panels:
    # 1) Overview panel (health, chain_qa_status, alerts)
    # 2) Table of clip_rows
    # 3) Cost panel
    if markdown or output:
        md = format_longform_health_markdown(report)
        ...
```

Keep backward-compatible: still shows health score prominently.

- [ ] **Commit**

```bash
git commit -m "feat(cli): expand sequence health into long-form dashboard"
```

---

### Task 3: Docs + regression

- [ ] **CHANGELOG**

```markdown
- **Long-form health dashboard (roadmap #10)** — `tools/sequence_health_dashboard.py` aggregates chain QA, drift/seam/AMV, regen, temperature, continuity diffs, remaining cost; CLI `sequence health` with `--json` / `--markdown`
```

- [ ] **Regression**

```bash
pytest tests/test_sequence_health_dashboard.py tests/test_continuity_diff.py tests/test_cli_smoke.py tests/test_extend_regen.py -v
```

- [ ] **Commit** `docs: changelog for long-form health dashboard`

---

## Spec coverage

| Spec #10 | Task |
|----------|------|
| chain QA status | Task 1 |
| drift trend | Task 1 drift.trend / max |
| seam risks | Task 1 seam |
| re-gen count | Task 1 regen |
| estimated remaining cost | Task 1 cost + estimate_sequence_cost |
| CLI dashboard / report | Task 2 |

---

## Execution handoff

**Two execution options:**

1. **Subagent-Driven (recommended)**
2. **Inline Execution**

Which approach?
