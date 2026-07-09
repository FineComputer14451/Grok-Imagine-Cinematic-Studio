# Extend Re-Gen Loop (#5) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** On chain QA **No-Go**, build a **targeted re-gen fix prompt** from QA fixes + memory bank + drift/seam evidence, track an **attempt budget** (quota-aware), and optionally re-submit via the existing sequence runner — without burning quota by default.

**Architecture:** Pure planner in `tools/extend_regen.py` (fix prompt + budget check + attempt record). CLI `sequence regen plan|apply|run`. `apply` writes the fix prompt onto the clip and increments attempt counters; `run` calls `run_sequence_clip` only when budget allows and `--execute`/`run` is explicit. No new agents.

**Tech Stack:** Python 3.11+, existing `sequence_chain`, `sequence_memory`, `chain_qa` / evidence fields, `sequence_runner.run_sequence_clip`, Typer/Rich, pytest.

**Design:** [docs/superpowers/specs/2026-07-09-long-form-continuity-roadmap-design.md](../specs/2026-07-09-long-form-continuity-roadmap-design.md) — backlog **#5**

**Depends on:** #1–#4 shipped (drift, seam, assist v2, memory bank).

---

## Principles

1. **Plan before spend** — default path is `regen plan` (print fix prompt + budget status). API re-submit only via explicit `regen run`.
2. **Budget is hard** — default max attempts per clip = **2** (original + 1 retry); sequence-level optional cap. Exceeding budget returns structured error, does not call Imagine.
3. **Evidence-informed fixes** — prompt includes `chain_qa.fixes`, critical failure keys, drift factors, seam factors, and `SEQUENCE_MEMORY_BANK` block.
4. **Reuse runner** — do not reimplement job submit/poll; call `run_sequence_clip` after `apply` sets `clip["prompt"]`.
5. **TDD + YAGNI** — no auto-loop inside runner that retries N times in one call (that surprises quota). Single attempt per `run` invocation.

## Out of scope

- #6 Audio Momentum Integrity scorer
- #7 Emotional Temperature Gate
- #12 Arc Replan Co-pilot
- Web UI
- Automatic multi-retry loops in `run_sequence_clip` without CLI
- Changing Imagine client pricing math (use simple credits estimate from duration × rate if recording)

---

## Data contract

### Sequence-level (optional, ensured on first regen use)

```python
seq["regen_budget"] = {
  "max_attempts_per_clip": 2,   # default
  "max_sequence_attempts": 20,  # optional soft cap; None = unlimited
  "sequence_attempts_used": 0,
}
```

### Clip-level

```python
clip["regen"] = {
  "attempts": 0,                 # successful plan-apply cycles that led to a run, or count of apply calls
  "max_attempts": 2,             # override per clip optional; else inherit sequence
  "last_plan_at": iso | None,
  "last_run_at": iso | None,
  "history": [                   # append-only short log
    {
      "at": iso,
      "action": "plan" | "apply" | "run" | "blocked",
      "decision": str | None,    # prior chain_qa decision
      "fixes": list[str],
      "prompt_excerpt": str,     # first 200 chars
      "reason": str | None,      # if blocked
    }
  ],
}
clip["prompt"]                    # apply overwrites with fix prompt for next run
clip["regen_fix_prompt"]         # full planned prompt preserved even after further edits
```

**Attempt accounting:**
- `plan` — does not consume budget
- `apply` — does not consume budget (prepares prompt only)
- `run` — consumes 1 attempt **before** submit if `can_regen`; if blocked, no consume
- Count `clip["regen"]["attempts"]` increments on successful `run` start (or on apply if we want “planned retries” — **prefer increment on run** so plans are free)

---

## File map

| Path | Role |
|------|------|
| `tools/extend_regen.py` | Budget + plan fix prompt + apply + run orchestration helpers |
| `tools/cli/sequence_commands.py` | `sequence regen plan\|apply\|run` |
| `tests/test_extend_regen.py` | Unit tests |
| `tests/test_cli_smoke.py` | Help registration |
| `CHANGELOG.md` | Unreleased |

---

### Task 1: Pure extend_regen module + tests

**Files:**
- Create: `tools/extend_regen.py`
- Create: `tests/test_extend_regen.py`

- [ ] **Step 1: Failing tests**

```python
"""Tests for extend re-gen loop (roadmap #5)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from extend_regen import (  # noqa: E402
    DEFAULT_MAX_ATTEMPTS_PER_CLIP,
    apply_regen_plan,
    build_regen_fix_prompt,
    can_regen,
    ensure_regen_budget,
    ensure_clip_regen,
    plan_regen,
)
from sequence_chain import create_clip, create_sequence_scaffold  # noqa: E402


def test_default_max_attempts() -> None:
    assert DEFAULT_MAX_ATTEMPTS_PER_CLIP == 2


def test_ensure_budget_on_sequence() -> None:
    seq = create_sequence_scaffold("Regen Seq")
    ensure_regen_budget(seq)
    assert seq["regen_budget"]["max_attempts_per_clip"] == 2
    assert seq["regen_budget"]["sequence_attempts_used"] == 0


def test_can_regen_false_when_attempts_exhausted() -> None:
    seq = create_sequence_scaffold("R")
    ensure_regen_budget(seq)
    clip = create_clip(prompt="old")
    clip["clip_id"] = "clip_001"
    ensure_clip_regen(clip, seq)
    clip["regen"]["attempts"] = 2
    ok, reason = can_regen(seq, clip)
    assert ok is False
    assert "budget" in reason.lower() or "attempt" in reason.lower()


def test_can_regen_true_with_no_go() -> None:
    seq = create_sequence_scaffold("R")
    ensure_regen_budget(seq)
    clip = create_clip(prompt="bad stitch")
    clip["clip_id"] = "clip_002"
    clip["status"] = "qa_hold"
    clip["chain_qa"] = {
        "decision": "no_go",
        "fixes": ["Strengthen LAST_FRAME_RECAP", "Critical chain QA failure"],
        "critical_failures": ["last_frame_continuity"],
        "weighted_score": 4.0,
    }
    ensure_clip_regen(clip, seq)
    ok, reason = can_regen(seq, clip)
    assert ok is True


def test_build_fix_prompt_includes_fixes_and_memory() -> None:
    seq = create_sequence_scaffold("R")
    seq["memory_bank"]["environment"]["location"] = "Neon alley"
    seq["memory_bank"]["lighting"]["state"] = "wet neon"
    clip = create_clip(
        prompt="Continue run",
        last_frame_recap="Hero mid-stride",
        reference_image_id="ref_1",
    )
    clip["clip_id"] = "clip_002"
    clip["chain_qa"] = {
        "decision": "no_go",
        "fixes": ["Character drift at stitch", "regenerate clip"],
        "critical_failures": ["character_drift_boundary"],
    }
    clip["identity_drift"] = {
        "drift_score": 4.0,
        "factors": ["Anchors missed=2/3"],
        "fixes": ["Reinforce DNA anchors in prompt"],
    }
    clip["seam_report"] = {
        "seam_risk": 6.5,
        "factors": ["Previous LAST_FRAME_RECAP missing"],
        "fixes": ["Capture LAST_FRAME_RECAP"],
    }
    prev = create_clip(last_frame_recap="End of alley, coat wet")
    text = build_regen_fix_prompt(seq, clip, previous_clip=prev, next_beat="Continue the chase")
    assert "REGEN_FIX" in text or "RE-GEN" in text or "FIX:" in text
    assert "Character drift" in text or "drift" in text.lower()
    assert "Neon alley" in text or "SEQUENCE_MEMORY_BANK" in text
    assert "Continue the chase" in text or "chase" in text.lower()


def test_plan_regen_returns_structured_result() -> None:
    seq = create_sequence_scaffold("R")
    ensure_regen_budget(seq)
    clip = create_clip(prompt="x")
    clip["clip_id"] = "clip_001"
    clip["chain_qa"] = {"decision": "no_go", "fixes": ["Fix A"], "critical_failures": []}
    plan = plan_regen(seq, clip)
    assert plan["allowed"] is True
    assert plan["fix_prompt"]
    assert "Fix A" in plan["fix_prompt"] or "Fix A" in str(plan.get("fixes"))


def test_apply_regen_plan_sets_prompt() -> None:
    seq = create_sequence_scaffold("R")
    ensure_regen_budget(seq)
    clip = create_clip(prompt="original")
    clip["clip_id"] = "clip_001"
    clip["chain_qa"] = {"decision": "no_go", "fixes": ["Add lighting continuity"], "critical_failures": []}
    plan = plan_regen(seq, clip)
    apply_regen_plan(seq, clip, plan)
    assert clip["prompt"] == plan["fix_prompt"]
    assert clip.get("regen_fix_prompt") == plan["fix_prompt"]
    assert clip["status"] in ("pending", "qa_hold", "regen_ready")
```

- [ ] **Step 2: pytest fail**

```bash
pytest tests/test_extend_regen.py -v
```

- [ ] **Step 3: Implement `tools/extend_regen.py`**

```python
#!/usr/bin/env python3
"""
Extend re-gen loop — fix prompts + attempt budget after chain QA No-Go (roadmap #5).
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

from sequence_chain import build_extend_prompt
from sequence_memory import ensure_memory_bank, memory_bank_to_prompt_block

DEFAULT_MAX_ATTEMPTS_PER_CLIP = 2
DEFAULT_MAX_SEQUENCE_ATTEMPTS = 20


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_regen_budget(seq: dict[str, Any]) -> dict[str, Any]:
    budget = seq.get("regen_budget")
    if not isinstance(budget, dict):
        budget = {}
    seq["regen_budget"] = {
        "max_attempts_per_clip": int(
            budget.get("max_attempts_per_clip", DEFAULT_MAX_ATTEMPTS_PER_CLIP)
        ),
        "max_sequence_attempts": budget.get(
            "max_sequence_attempts", DEFAULT_MAX_SEQUENCE_ATTEMPTS
        ),
        "sequence_attempts_used": int(budget.get("sequence_attempts_used", 0)),
    }
    return seq["regen_budget"]


def ensure_clip_regen(clip: dict[str, Any], seq: dict[str, Any] | None = None) -> dict[str, Any]:
    budget = ensure_regen_budget(seq) if seq is not None else {
        "max_attempts_per_clip": DEFAULT_MAX_ATTEMPTS_PER_CLIP
    }
    regen = clip.get("regen")
    if not isinstance(regen, dict):
        regen = {}
    clip["regen"] = {
        "attempts": int(regen.get("attempts", 0)),
        "max_attempts": int(
            regen.get("max_attempts", budget.get("max_attempts_per_clip", DEFAULT_MAX_ATTEMPTS_PER_CLIP))
        ),
        "last_plan_at": regen.get("last_plan_at"),
        "last_run_at": regen.get("last_run_at"),
        "history": list(regen.get("history") or []),
    }
    return clip["regen"]


def can_regen(seq: dict[str, Any], clip: dict[str, Any]) -> tuple[bool, str]:
    """Return (allowed, reason)."""
    ensure_regen_budget(seq)
    regen = ensure_clip_regen(clip, seq)
    max_a = regen["max_attempts"]
    if regen["attempts"] >= max_a:
        return False, f"Clip attempt budget exhausted ({regen['attempts']}/{max_a})"
    seq_budget = seq["regen_budget"]
    max_seq = seq_budget.get("max_sequence_attempts")
    if max_seq is not None and int(seq_budget.get("sequence_attempts_used", 0)) >= int(max_seq):
        return False, f"Sequence attempt budget exhausted ({seq_budget['sequence_attempts_used']}/{max_seq})"
    return True, "ok"


def _collect_fixes(clip: dict[str, Any]) -> list[str]:
    fixes: list[str] = []
    qa = clip.get("chain_qa") or {}
    for f in qa.get("fixes") or []:
        if f and f not in fixes:
            fixes.append(str(f))
    for key in ("identity_drift", "seam_report"):
        block = clip.get(key) or {}
        for f in block.get("fixes") or []:
            if f and f not in fixes:
                fixes.append(str(f))
        for fac in (block.get("factors") or [])[:3]:
            line = f"[{key}] {fac}"
            if line not in fixes:
                fixes.append(line)
    return fixes


def build_regen_fix_prompt(
    seq: dict[str, Any],
    clip: dict[str, Any],
    *,
    previous_clip: dict[str, Any] | None = None,
    next_beat: str | None = None,
    character_injection: str = "",
) -> str:
    """Build a targeted re-gen prompt from QA + evidence + memory bank."""
    beat = (
        next_beat
        or clip.get("narrative_beat")
        or "Re-generate this clip fixing continuity failures; match previous end state exactly"
    )
    base = ""
    if previous_clip is not None:
        base = build_extend_prompt(
            seq, previous_clip, beat, character_injection=character_injection
        )
    else:
        # Opening clip re-gen: keep original intent + fixes
        parts = []
        if character_injection:
            parts.append(character_injection.strip())
        parts.append(clip.get("prompt") or beat)
        # still attach memory bank
        bank_block = memory_bank_to_prompt_block(seq.get("memory_bank"))
        if bank_block and "empty" not in bank_block.lower():
            parts.append("")
            parts.append(bank_block)
        base = "\n".join(parts)

    fixes = _collect_fixes(clip)
    qa = clip.get("chain_qa") or {}
    critical = qa.get("critical_failures") or []
    drift = clip.get("identity_drift") or {}
    seam = clip.get("seam_report") or {}

    header = [
        "REGEN_FIX: Prior generation failed chain QA — apply ALL fixes below.",
        "Priority: invisible stitch continuity, identity lock, no morphing at boundary.",
        f"Prior decision: {qa.get('decision', 'unknown')} | weighted={qa.get('weighted_score')}",
    ]
    if critical:
        header.append(f"Critical failures: {', '.join(critical)}")
    if drift.get("drift_score") is not None:
        header.append(f"identity_drift_score={drift.get('drift_score')} (pass={drift.get('pass')})")
    if seam.get("seam_risk") is not None:
        header.append(f"seam_risk={seam.get('seam_risk')} (pass={seam.get('pass')})")
    if fixes:
        header.append("FIXES:")
        for f in fixes:
            header.append(f"  - {f}")
    header.append(
        "NEGATIVES: face morph, wardrobe teleport, lighting pop, temporal flicker, "
        "identity drift, lost props, audio dialogue drop"
    )
    header.append("---")
    return "\n".join(header) + "\n\n" + base


def plan_regen(
    seq: dict[str, Any],
    clip: dict[str, Any],
    *,
    previous_clip: dict[str, Any] | None = None,
    next_beat: str | None = None,
    character_injection: str = "",
) -> dict[str, Any]:
    ensure_regen_budget(seq)
    ensure_clip_regen(clip, seq)
    allowed, reason = can_regen(seq, clip)
    fixes = _collect_fixes(clip)
    # Always build prompt for inspection even if not allowed
    fix_prompt = build_regen_fix_prompt(
        seq,
        clip,
        previous_clip=previous_clip,
        next_beat=next_beat,
        character_injection=character_injection,
    )
    return {
        "clip_id": clip.get("clip_id"),
        "allowed": allowed,
        "reason": reason,
        "fixes": fixes,
        "fix_prompt": fix_prompt,
        "attempts": clip["regen"]["attempts"],
        "max_attempts": clip["regen"]["max_attempts"],
        "sequence_attempts_used": seq["regen_budget"]["sequence_attempts_used"],
        "prior_decision": (clip.get("chain_qa") or {}).get("decision"),
    }


def _append_history(clip: dict[str, Any], entry: dict[str, Any]) -> None:
    regen = ensure_clip_regen(clip)
    hist = list(regen.get("history") or [])
    hist.append(entry)
    # keep last 10
    regen["history"] = hist[-10:]


def apply_regen_plan(
    seq: dict[str, Any],
    clip: dict[str, Any],
    plan: dict[str, Any] | None = None,
    *,
    previous_clip: dict[str, Any] | None = None,
    next_beat: str | None = None,
    character_injection: str = "",
) -> dict[str, Any]:
    """Write fix prompt onto clip; does not consume attempt budget."""
    if plan is None:
        plan = plan_regen(
            seq,
            clip,
            previous_clip=previous_clip,
            next_beat=next_beat,
            character_injection=character_injection,
        )
    ensure_clip_regen(clip, seq)
    prompt = plan["fix_prompt"]
    clip["prompt"] = prompt
    clip["regen_fix_prompt"] = prompt
    clip["status"] = "regen_ready"
    clip["regen"]["last_plan_at"] = _now_iso()
    _append_history(
        clip,
        {
            "at": _now_iso(),
            "action": "apply",
            "decision": plan.get("prior_decision"),
            "fixes": list(plan.get("fixes") or []),
            "prompt_excerpt": prompt[:200],
            "reason": plan.get("reason"),
        },
    )
    return plan


def consume_regen_attempt(seq: dict[str, Any], clip: dict[str, Any]) -> None:
    """Increment counters at start of a re-gen run."""
    ensure_regen_budget(seq)
    regen = ensure_clip_regen(clip, seq)
    regen["attempts"] = int(regen["attempts"]) + 1
    regen["last_run_at"] = _now_iso()
    seq["regen_budget"]["sequence_attempts_used"] = int(
        seq["regen_budget"].get("sequence_attempts_used", 0)
    ) + 1
    _append_history(
        clip,
        {
            "at": _now_iso(),
            "action": "run",
            "decision": (clip.get("chain_qa") or {}).get("decision"),
            "fixes": _collect_fixes(clip),
            "prompt_excerpt": (clip.get("prompt") or "")[:200],
            "reason": None,
        },
    )


def prepare_regen_run(
    seq: dict[str, Any],
    clip: dict[str, Any],
    *,
    previous_clip: dict[str, Any] | None = None,
    next_beat: str | None = None,
    character_injection: str = "",
    auto_apply: bool = True,
) -> dict[str, Any]:
    """
    Validate budget, optionally apply plan, consume attempt.
    Returns plan dict with allowed flag. Raises ValueError if not allowed.
    """
    plan = plan_regen(
        seq,
        clip,
        previous_clip=previous_clip,
        next_beat=next_beat,
        character_injection=character_injection,
    )
    if not plan["allowed"]:
        ensure_clip_regen(clip, seq)
        _append_history(
            clip,
            {
                "at": _now_iso(),
                "action": "blocked",
                "decision": plan.get("prior_decision"),
                "fixes": plan.get("fixes") or [],
                "prompt_excerpt": "",
                "reason": plan["reason"],
            },
        )
        raise ValueError(plan["reason"])
    if auto_apply:
        apply_regen_plan(seq, clip, plan)
    consume_regen_attempt(seq, clip)
    return plan
```

Tune `build_regen_fix_prompt` so tests find expected substrings. For opening clip without previous, memory bank still appears if location set — test uses previous_clip path preferably.

For `test_build_fix_prompt_includes_fixes_and_memory`: pass `previous_clip=prev`.

For `test_can_regen_true_with_no_go`: can_regen does **not** require no_go — budget only. That's fine (plan can run anytime). Optionally warn if decision is go — YAGNI for v1.

- [ ] **Step 4: pytest green**

```bash
pytest tests/test_extend_regen.py -v
```

- [ ] **Step 5: Commit**

```bash
git add tools/extend_regen.py tests/test_extend_regen.py
git commit -m "feat(continuity): extend re-gen fix prompt and attempt budget"
```

---

### Task 2: CLI `sequence regen plan|apply|run`

**Files:**
- Modify: `tools/cli/sequence_commands.py`
- Modify: `tests/test_cli_smoke.py`

- [ ] **Step 1: Smoke test**

```python
def test_sequence_regen_commands_registered() -> None:
    result = run_cli("sequence", "regen", "--help")
    assert result.returncode == 0
    out = result.stdout.lower()
    assert "plan" in out
    assert "apply" in out
    assert "run" in out
```

- [ ] **Step 2: Nested typer `regen`**

```python
regen_app = typer.Typer(help="Re-gen loop after chain QA No-Go (roadmap #5)")
app.add_typer(regen_app, name="regen")

@regen_app.command("plan")
def regen_plan(
    name: str = typer.Argument(...),
    clip: str = typer.Option(..., "--clip", "-c"),
    beat: str = typer.Option(None, "--beat", "-b"),
    character: str = typer.Option("", "--character", help="DNA inject block text"),
):
    """Build fix prompt + show budget (no spend)."""
    seq = require_sequence(name)
    target = require_clip(seq, clip)
    prev = seq["clips"][target["index"] - 1] if target["index"] > 0 else None
    from extend_regen import plan_regen
    plan = plan_regen(seq, target, previous_clip=prev, next_beat=beat, character_injection=character)
    # print allowed, attempts, fixes table, prompt panel
    # do not save unless we want last_plan only — optional save plan meta without applying
    target.setdefault("regen", {})
    from extend_regen import ensure_clip_regen
    ensure_clip_regen(target, seq)
    target["regen"]["last_plan_at"] = ...  # or only on apply
    save_sequence only if we attach plan snapshot: clip["regen_last_plan"] = {allowed, fixes, attempts} without full prompt to keep JSON small — OR save full regen_fix_prompt on plan for convenience:
    target["regen_fix_prompt"] = plan["fix_prompt"]  # plan stores prompt for inspect
    save_sequence(seq)

@regen_app.command("apply")
def regen_apply(...):
    """Write fix prompt onto clip as prompt (regen_ready). No Imagine call."""
    plan = apply_regen_plan(...)
    save_sequence(seq)

@regen_app.command("run")
def regen_run(
    name: str,
    clip: str = ...,
    beat: str = None,
    character: str = "",
    dry_run: bool = typer.Option(False, "--dry-run"),
    force: bool = typer.Option(False, "--force", help="Run even if last decision was go"),
):
    """Consume one attempt and call run_sequence_clip with fix prompt."""
    from extend_regen import prepare_regen_run
    from sequence_runner import run_sequence_clip
    # optional: refuse if decision==go unless --force
    try:
        prepare_regen_run(seq, target, previous_clip=prev, next_beat=beat, character_injection=character)
    except ValueError as e:
        console.print(f"[red]{e}[/red]"); raise typer.Exit(1)
    save_sequence(seq)  # persist counters before API
    result = run_sequence_clip(seq, clip, dry_run=dry_run if dry_run else None)
    save_sequence(seq)
    # print status
```

**Note:** `prepare_regen_run` already applies + consumes. `run_sequence_clip` uses `clip["prompt"]` via `_resolve_clip_prompt` — good.

**Block on go without force:** in CLI before prepare:

```python
dec = (target.get("chain_qa") or {}).get("decision")
if dec == "go" and not force:
    console.print("[yellow]Last decision is go — use --force to re-gen anyway[/yellow]")
    raise typer.Exit(1)
```

- [ ] **Step 3: Verify**

```bash
pytest tests/test_extend_regen.py tests/test_cli_smoke.py -v
python tools/cinematic_studio_cli.py sequence regen --help
```

- [ ] **Step 4: Commit**

```bash
git add tools/cli/sequence_commands.py tests/test_cli_smoke.py
git commit -m "feat(cli): sequence regen plan apply and run commands"
```

---

### Task 3: Optional dry-run integration test + docs

**Files:**
- Modify: `tests/test_extend_regen.py` (add integration with dry_run runner if easy)
- Modify: `CHANGELOG.md`
- Optional one-liner in chain-qa-protocol SKILL.md

- [ ] **Step 1: Integration test (dry_run)**

```python
def test_prepare_and_run_dry(monkeypatch, tmp_path):
    # Optional: if sequence_runner dry_run is heavy, skip and only unit-test prepare_regen_run consume
    seq = create_sequence_scaffold("DryRegen")
    ensure_regen_budget(seq)
    clip = create_clip(prompt="orig", last_frame_recap="end state detailed enough for stitch")
    clip["clip_id"] = "clip_001"
    clip["index"] = 0
    clip["chain_qa"] = {"decision": "no_go", "fixes": ["Fix lighting"], "critical_failures": []}
    seq["clips"] = [clip]
    from extend_regen import prepare_regen_run
    plan = prepare_regen_run(seq, clip, auto_apply=True)
    assert plan["allowed"]
    assert clip["regen"]["attempts"] == 1
    assert "REGEN_FIX" in clip["prompt"] or "FIX" in clip["prompt"]
```

- [ ] **Step 2: CHANGELOG**

```markdown
- **Extend re-gen loop (roadmap #5)** — `tools/extend_regen.py` builds fix prompts from chain QA + drift/seam + memory bank; per-clip/sequence attempt budget; CLI `sequence regen plan|apply|run` (run spends one attempt via existing sequence runner)
```

- [ ] **Step 3: Full regression**

```bash
pytest tests/test_extend_regen.py tests/test_sequence_memory.py tests/test_sequence_chain_memory.py tests/test_identity_drift.py tests/test_seam_report.py tests/test_chain_qa_assist.py tests/test_cli_smoke.py tests/test_handoff_validator.py -v
```

- [ ] **Step 4: Commit**

```bash
git add CHANGELOG.md tests/test_extend_regen.py  # + skill if edited
git commit -m "docs: changelog for extend re-gen loop"
```

---

## Spec coverage

| Spec #5 | Task |
|---------|------|
| On No-Go auto-build targeted fix prompt | Task 1 `build_regen_fix_prompt` |
| From QA fixes + memory bank | Task 1 |
| Attempt budget quota-aware | Task 1 `can_regen` / `consume_regen_attempt` |
| sequence_runner upgrade | Task 2 `regen run` → `run_sequence_clip` |
| No surprise multi-retry | Principles |

## Self-review notes

- `can_regen` is budget-only (not decision-gated); CLI gates on `go` + `--force`.
- Attempt increments on **run**, not plan/apply.
- Handoff validator unchanged (no new packet type required).

---

## Execution handoff

Plan saved to `docs/superpowers/plans/2026-07-09-extend-regen-loop.md`.

**Two execution options:**

1. **Subagent-Driven (recommended)**
2. **Inline Execution**

Which approach?
