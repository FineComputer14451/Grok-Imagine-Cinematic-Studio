# Arc Replan Co-pilot (#12) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** After mid-sequence failure (chain QA No-Go, drift lock, temperature fail), **replan remaining clip beats** and temperature targets **without rewriting the Production Bible**.

**Architecture:** Pure `tools/arc_replan.py` builds a replan proposal from sequence state + failure context. CLI `sequence replan plan|apply`. Thin skill `.grok/skills/arc-replan-copilot/SKILL.md` + Sequence Director one-liner. Does not call Imagine or rewrite Bible JSON.

**Tech Stack:** Python 3.11+, `emotional_temperature.normalize_curve`, sequence clips, Typer/Rich, pytest.

**Design:** [docs/superpowers/specs/2026-07-09-long-form-continuity-roadmap-design.md](../specs/2026-07-09-long-form-continuity-roadmap-design.md) — backlog **#12** (final item)

**Depends on:** #5 regen, #7 temperature, #10 health (optional alerts) — all optional inputs.

---

## Principles

1. **Bible stays sacred** — replan only sequence clip beats, curve points, and notes; never Production Bible.
2. **From index forward** — frozen prefix = clips with index < failure index (or approved); replan index ≥ from_index.
3. **Proposal then apply** — `plan` returns structure; `apply` writes with backup of previous curve/beats in `seq["arc_replan_history"]`.
4. **Deterministic heuristics** — no LLM in tool; agents may refine prose later.
5. **TDD + YAGNI** — no full Narrative Arc Role Card rewrite; no automatic re-gen run.

## Out of scope

- New full agent suite expansion beyond thin skill
- Rewriting Production Bible / Mega Architect packages
- Auto-executing `sequence regen run` for all remaining clips
- Plugin catalog pin (only if new skill added — pin as optional final chore)

---

## Replan proposal contract

```python
{
  "from_index": int,
  "reason": str,
  "frozen_clip_ids": list[str],
  "replanned_clips": [
    {
      "clip_id": str | None,       # existing or planned new id
      "index": int,
      "action": "revise_beat" | "keep" | "insert_bridge" | "soft_reset",
      "narrative_beat": str,
      "planned_temp": float,
      "duration_seconds": int,
      "notes": str,
    }
  ],
  "temperature_curve_patch": list[dict],  # full normalized points for indices >= from_index (merged into curve on apply)
  "summary": str,
  "alerts": list[str],
}
```

### Triggers / reason inference (`infer_replan_reason(clip)`)

Priority:
1. `chain_qa.decision == no_go` → "chain_qa_no_go"
2. `identity_drift.pass is False` → "identity_drift"
3. `temperature_gate.severity == fail` → "temperature_fail"
4. `status == qa_hold` → "qa_hold"
5. else → "manual"

### Replan strategies (deterministic)

Given `from_index`, remaining planned count = max(existing clips from index, or pad to fill target duration):

**A. Soft recover (default for no_go / drift)**  
- At `from_index`: action `soft_reset`, beat = "Recover continuity from last good frame; re-establish identity and location before advancing story."  
- planned_temp = clamp(previous planned_temp or 4.0, toward mid 5.0)  
- Subsequent remaining clips: `revise_beat` with progressive temps toward original end target (or 7.0 default climax if none)

**B. Temperature fail**  
- Rebuild curve from from_index with gentler slope (max step +1.5 per clip toward end target)

**C. insert_bridge** (if remaining duration allows and reason is drift/no_go)  
- Optionally one bridge clip suggestion with action `insert_bridge` only when `allow_insert=True` (CLI flag); default False to avoid lengthening sequences unexpectedly.

**Duration:** keep existing clip duration or default 10s.

**narrative_beat templates** by strategy + index offset:
- soft_reset / recover
- re-anchor emotion
- advance plot beat N
- climax / resolution if last clip

### Apply rules

```python
def apply_arc_replan(seq, proposal, *, dry_run=False) -> seq:
    # push history entry
    # for each replanned clip with matching index:
    #   set narrative_beat, optionally duration
    # merge temperature_curve_patch into emotional_temperature_curve via normalize
    # set seq["arc_replan"] = latest proposal meta
```

Do not delete approved early clips. Do not create new clip dicts unless `insert_bridge` and allow_insert (v1 can implement insert by appending a new create_clip at from_index and shifting — **skip insert in v1** if complex; document as flag reserved).

**v1 scope lock:** actions `revise_beat`, `keep`, `soft_reset` only — no insert_bridge implementation (propose in notes only if desired).

---

## File map

| Path | Role |
|------|------|
| `tools/arc_replan.py` | plan + apply |
| `tools/cli/sequence_commands.py` | `replan plan|apply` |
| `tests/test_arc_replan.py` | Unit tests |
| `tests/test_cli_smoke.py` | Help |
| `.grok/skills/arc-replan-copilot/SKILL.md` | Thin skill |
| `.grok/skills/sequence-director/SKILL.md` | Cross-link |
| `CHANGELOG.md` | Unreleased |

---

### Task 1: Pure arc_replan module + tests

**Files:**
- Create: `tools/arc_replan.py`
- Create: `tests/test_arc_replan.py`

- [ ] **Tests**

```python
def test_plan_from_no_go_revises_remaining():
    seq = create_sequence_scaffold("Arc", target_duration=40)
    # two clips index 0 approved, index 1 no_go
    # plan from clip 1
    prop = plan_arc_replan(seq, from_index=1)
    assert prop["from_index"] == 1
    assert prop["replanned_clips"]
    assert prop["replanned_clips"][0]["action"] in ("soft_reset", "revise_beat")
    assert prop["temperature_curve_patch"]

def test_apply_writes_narrative_beat_and_curve():
    ...
    apply_arc_replan(seq, prop)
    assert seq["clips"][1].get("narrative_beat")
    assert seq["emotional_temperature_curve"]
    assert seq.get("arc_replan_history")

def test_frozen_prefix_not_in_replanned_actions_for_index_0_keep():
    # from_index=1 → frozen includes clip 0
    assert "clip_001" in prop["frozen_clip_ids"] or index 0 frozen
```

API:

```python
def infer_replan_reason(clip: dict) -> str: ...
def plan_arc_replan(
    seq: dict,
    *,
    from_index: int | None = None,
    from_clip_id: str | None = None,
    reason: str | None = None,
) -> dict: ...
def apply_arc_replan(seq: dict, proposal: dict) -> dict: ...
def format_arc_replan_markdown(proposal: dict) -> str: ...
```

Resolve from_index from clip_id via get_clip; default from_index = first no_go / qa_hold else last index.

- [ ] **Commit** `feat(continuity): arc replan co-pilot core`

---

### Task 2: CLI `sequence replan plan|apply`

```python
replan_app = typer.Typer(help="Arc replan co-pilot (roadmap #12)")
app.add_typer(replan_app, name="replan")

@replan_app.command("plan")
def replan_plan(
    name: str,
    clip: str | None = Option(None, "--clip", "-c"),
    from_index: int | None = Option(None, "--from-index"),
    reason: str | None = Option(None, "--reason"),
):
    # print markdown + summary; optional save proposal to seq["arc_replan_proposal"] without apply

@replan_app.command("apply")
def replan_apply(
    name: str,
    clip: str | None = ...,
    from_index: int | None = ...,
    reason: str | None = ...,
    yes: bool = Option(False, "--yes", help="Skip confirm"),
):
    # plan then apply, save_sequence
```

Smoke: `sequence replan --help` has plan and apply.

- [ ] **Commit** `feat(cli): sequence replan plan and apply commands`

---

### Task 3: Skill + docs + regression

- [ ] Create `.grok/skills/arc-replan-copilot/SKILL.md` (name, description, activation `ACTIVATE ARC_REPLAN`, CLI, when to use after No-Go)
- [ ] Sequence Director skill: one line under health/planning
- [ ] CHANGELOG entry for #12
- [ ] If skill added: `plugin catalog pin` + catalog-only follow-up commit (same pattern as multi-character)
- [ ] Regression:

```bash
pytest tests/test_arc_replan.py tests/test_emotional_temperature.py tests/test_extend_regen.py tests/test_cli_smoke.py tests/test_sequence_health_dashboard.py -v
```

- [ ] **Commit** `docs: changelog for arc replan co-pilot` (+ skill/catalog commits as needed)

---

## Spec coverage

| Spec #12 | Task |
|----------|------|
| Mid-sequence failure replan | Task 1 reason + from_index |
| Remaining clip beats | Task 1 replanned_clips narrative_beat |
| No whole Bible rewrite | Principle + no bible files |
| Sequence Director skill | Task 3 |

## Roadmap completion

After #12 ships, long-form continuity roadmap **#1–#12** is complete. Optional follow-up: update design doc status to "implemented".

---

## Execution handoff

**Two execution options:**

1. **Subagent-Driven (recommended)**
2. **Inline Execution**

Which approach?
