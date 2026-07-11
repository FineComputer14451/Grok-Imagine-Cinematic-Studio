# Identity Strict CLI Gates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add opt-in `--strict-identity` hard-fail on `sequence handoff` and `sequence extend-prompt` using a pure shared gate helper; default soft path unchanged.

**Architecture:** Implement `evaluate_identity_strict_gate` in `tools/identity_drift.py` (reuse `normalize_drift_evidence` / `report_to_drift_evidence`). Wire Typer flag on both commands; evaluate **before** writing artifacts; `typer.Exit(1)` on fail. Document in ICP protocol + CHANGELOG.

**Tech Stack:** Python 3.11+, existing `identity_drift` / `sequence_chain` / Typer CLI, pytest. No new deps.

**Design:** [docs/development/superpowers/specs/2026-07-11-identity-strict-cli-gates-design.md](../specs/2026-07-11-identity-strict-cli-gates-design.md)

**Depends on:** ICP v1.0 wiring (`report_to_drift_evidence`, clip `identity_drift`).

---

## Principles

1. **Opt-in only** — no flag → identical to current behavior.
2. **Evaluate before write** — strict fail never leaves a green handoff/prompt file.
3. **TDD** for the pure helper; CLI wiring is thin.
4. **YAGNI** — no Bible auto-strict, no QA/run gating, no validator exit change.

## Out of scope

- `sequence qa` / `run` / `qa-assist` flags  
- Validator `--strict-identity`  
- Auto-strict from Bible/sequence JSON  

---

## File map

| Path | Action | Responsibility |
|------|--------|----------------|
| `tools/identity_drift.py` | **Modify** | `evaluate_identity_strict_gate` |
| `tests/test_identity_strict_gate.py` | **Create** | Unit tests for gate |
| `tools/cli/sequence_commands.py` | **Modify** | `--strict-identity` on handoff + extend-prompt |
| `references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md` | **Modify** | CLI opt-in subsection |
| `CHANGELOG.md` | **Modify** | Unreleased bullet |

---

### Task 1: Pure gate helper + unit tests

**Files:**
- Modify: `tools/identity_drift.py`
- Create: `tests/test_identity_strict_gate.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_identity_strict_gate.py`:

```python
"""Unit tests for evaluate_identity_strict_gate (opt-in CLI hard fail)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from identity_drift import (  # noqa: E402
    DEFAULT_DRIFT_THRESHOLD,
    evaluate_identity_strict_gate,
    report_to_drift_evidence,
)
from sequence_chain import create_clip  # noqa: E402


def test_missing_evidence_fails() -> None:
    clip = create_clip(prompt="no score", last_frame_recap="x")
    clip["clip_id"] = "clip_001"
    result = evaluate_identity_strict_gate(clip=clip)
    assert result["pass"] is False
    assert result["strict"] is True
    assert result["status"] == "missing"
    assert result["reasons"]
    assert result["fixes"]
    assert result["threshold"] == DEFAULT_DRIFT_THRESHOLD


def test_clip_identity_drift_pass() -> None:
    clip = create_clip(prompt="hero locked", last_frame_recap="same")
    clip["clip_id"] = "clip_002"
    clip["identity_drift"] = {
        "clip_id": "clip_002",
        "drift_score": 1.0,
        "threshold": 2.5,
        "pass": True,
        "factors": ["ok"],
        "fixes": [],
    }
    result = evaluate_identity_strict_gate(clip=clip, threshold=2.5)
    assert result["pass"] is True
    assert result["status"] == "pass"
    assert result["score"] == 1.0


def test_clip_identity_drift_risk() -> None:
    clip = create_clip(prompt="drifted", last_frame_recap="x")
    clip["clip_id"] = "clip_003"
    clip["identity_drift"] = {
        "clip_id": "clip_003",
        "drift_score": 4.0,
        "threshold": 2.5,
        "pass": False,
        "factors": ["bad"],
        "fixes": ["Reinforce DNA"],
    }
    result = evaluate_identity_strict_gate(clip=clip)
    assert result["pass"] is False
    assert result["status"] == "risk"
    assert any("Reinforce" in f or "DNA" in f for f in result["fixes"]) or result["reasons"]


def test_explicit_drift_evidence_pass() -> None:
    clip = create_clip(prompt="x", last_frame_recap="y")
    clip["clip_id"] = "clip_004"
    evidence = report_to_drift_evidence(
        {
            "clip_id": "clip_004",
            "drift_score": 0.5,
            "threshold": 2.5,
            "pass": True,
            "factors": [],
        },
        character_slug="liora",
    )
    result = evaluate_identity_strict_gate(clip=clip, drift_evidence=evidence)
    assert result["pass"] is True
    assert result["status"] == "pass"


def test_skipped_fails_under_strict() -> None:
    clip = create_clip(prompt="x", last_frame_recap="y")
    clip["clip_id"] = "clip_005"
    evidence = {
        "schema_version": "1.0",
        "protocol": "IDENTITY_CONTINUITY_PROTOCOL",
        "protocol_version": "1.0",
        "clip_id": "clip_005",
        "character_slug": "liora",
        "scored_at": "2026-07-11T00:00:00+00:00",
        "tool": "sequence drift-score",
        "score": 0.0,
        "threshold": 2.5,
        "status": "skipped",
        "skipped_reason": "Director waiver",
        "attempt": 1,
        "baseline": {"dna_slug": "liora", "dna_version": 1},
    }
    result = evaluate_identity_strict_gate(clip=clip, drift_evidence=evidence)
    assert result["pass"] is False
    assert result["status"] == "skipped"


def test_multi_cast_any_risk_fails() -> None:
    clip = create_clip(prompt="x", last_frame_recap="y")
    clip["clip_id"] = "clip_006"
    good = report_to_drift_evidence(
        {"clip_id": "clip_006", "drift_score": 1.0, "threshold": 2.5, "pass": True, "factors": []},
        character_slug="a",
    )
    bad = report_to_drift_evidence(
        {"clip_id": "clip_006", "drift_score": 5.0, "threshold": 2.5, "pass": False, "factors": []},
        character_slug="b",
    )
    result = evaluate_identity_strict_gate(clip=clip, drift_evidence=[good, bad])
    assert result["pass"] is False
    assert result["status"] == "risk"


def test_incomplete_status_fails() -> None:
    clip = create_clip(prompt="x", last_frame_recap="y")
    clip["clip_id"] = "clip_007"
    evidence = {
        "schema_version": "1.0",
        "protocol": "IDENTITY_CONTINUITY_PROTOCOL",
        "protocol_version": "1.0",
        "clip_id": "clip_007",
        "character_slug": "liora",
        "scored_at": "2026-07-11T00:00:00+00:00",
        "tool": "sequence drift-score",
        "score": 0.0,
        "threshold": 2.5,
        "status": "incomplete",
        "attempt": 1,
        "baseline": {"dna_slug": "liora", "dna_version": 1},
    }
    result = evaluate_identity_strict_gate(clip=clip, drift_evidence=evidence)
    assert result["pass"] is False
    assert result["status"] == "incomplete"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_identity_strict_gate.py -v
```

Expected: FAIL — `cannot import name evaluate_identity_strict_gate`

- [ ] **Step 3: Implement `evaluate_identity_strict_gate` in `tools/identity_drift.py`**

Append after `normalize_drift_evidence`:

```python
def _evaluate_one_evidence(
    item: dict[str, Any],
    *,
    threshold: float,
) -> dict[str, Any]:
    """Evaluate a single drift_evidence object under strict rules."""
    status = str(item.get("status") or "").strip() or "incomplete"
    score_raw = item.get("score", item.get("drift_score"))
    try:
        score = float(score_raw) if score_raw is not None else None
    except (TypeError, ValueError):
        score = None

    reasons: list[str] = []
    fixes: list[str] = [
        "Run: python tools/cinematic_studio_cli.py sequence drift-score "
        "\"<Seq>\" --clip <clip_id> --dna characters/{slug}/dna.json",
        "Attach drift_evidence (ICP-02/03); see references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md",
    ]

    if status == "missing":
        return {
            "pass": False,
            "status": "missing",
            "score": score,
            "reasons": ["drift_evidence missing"],
            "fixes": fixes,
        }
    if status == "incomplete":
        return {
            "pass": False,
            "status": "incomplete",
            "score": score,
            "reasons": ["drift_evidence status=incomplete"],
            "fixes": fixes,
        }
    if status == "skipped":
        return {
            "pass": False,
            "status": "skipped",
            "score": score,
            "reasons": [
                "drift_evidence status=skipped — strict mode does not allow skip"
            ],
            "fixes": fixes + ["Remove --strict-identity or run drift-score"],
        }
    if status == "risk":
        extra = []
        for f in item.get("signals", {}).get("flags") or []:
            extra.append(str(f))
        # scorer fixes may live only on clip report; include notes/summary
        summary = (item.get("signals") or {}).get("summary") or ""
        reasons = [f"identity risk (status=risk, score={score})"]
        if summary:
            reasons.append(str(summary))
        risk_fixes = list(fixes)
        if "Reinforce" not in " ".join(risk_fixes):
            risk_fixes.append("Reinforce DNA anchors / re-lock identity before extend")
        return {
            "pass": False,
            "status": "risk",
            "score": score,
            "reasons": reasons,
            "fixes": risk_fixes,
        }

    # status == pass or unknown treated carefully
    if status != "pass":
        return {
            "pass": False,
            "status": status or "incomplete",
            "score": score,
            "reasons": [f"unknown or non-pass status={status!r}"],
            "fixes": fixes,
        }

    if score is not None and score >= threshold:
        return {
            "pass": False,
            "status": "risk",
            "score": score,
            "reasons": [
                f"score {score} >= threshold {threshold} despite status=pass"
            ],
            "fixes": fixes + ["Re-run sequence drift-score and refresh evidence"],
        }

    return {
        "pass": True,
        "status": "pass",
        "score": score,
        "reasons": [],
        "fixes": [],
    }


def evaluate_identity_strict_gate(
    *,
    clip: dict[str, Any],
    drift_evidence: dict | list | None = None,
    threshold: float = DEFAULT_DRIFT_THRESHOLD,
) -> dict[str, Any]:
    """
    Opt-in strict identity gate for extend-path CLI.

    Fail on missing/incomplete/skipped evidence or risk (score >= threshold).
    """
    thr = float(threshold)

    items = normalize_drift_evidence(drift_evidence)
    if not items:
        report = clip.get("identity_drift")
        if isinstance(report, dict) and report.get("drift_score") is not None:
            slug = (
                str(clip.get("character_slug") or "")
                or str(report.get("character_slug") or "")
                or "unknown"
            )
            items = [
                report_to_drift_evidence(
                    report,
                    character_slug=slug,
                    reference_hint=str(clip.get("reference_image_id") or ""),
                )
            ]
            # Prefer scorer pass flag if present
            if report.get("pass") is False:
                items[0]["status"] = "risk"
            # Merge scorer fixes into signals for messaging
            scorer_fixes = [str(f) for f in (report.get("fixes") or []) if f]
            if scorer_fixes:
                items[0].setdefault("signals", {})
                # stash for _evaluate_one — use notes
                items[0]["notes"] = (items[0].get("notes") or "") + "; ".join(
                    scorer_fixes
                )

    if not items:
        return {
            "pass": False,
            "strict": True,
            "status": "missing",
            "reasons": [
                "No drift_evidence and no clip identity_drift score — run sequence drift-score"
            ],
            "fixes": [
                "Run: python tools/cinematic_studio_cli.py sequence drift-score "
                "\"<Seq>\" --clip <clip_id> --dna characters/{slug}/dna.json",
                "See references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md (ICP-02/03)",
            ],
            "score": None,
            "threshold": thr,
        }

    worst_status = "pass"
    all_reasons: list[str] = []
    all_fixes: list[str] = []
    scores: list[float] = []
    overall_pass = True

    for item in items:
        # If scorer fixes embedded in notes, append on risk
        one = _evaluate_one_evidence(item, threshold=thr)
        if item.get("notes") and not one["pass"]:
            for part in str(item["notes"]).split(";"):
                part = part.strip()
                if part and part not in one["fixes"]:
                    one["fixes"].append(part)
        if not one["pass"]:
            overall_pass = False
        if one["status"] != "pass":
            # precedence: missing > skipped > incomplete > risk > pass
            order = {
                "missing": 4,
                "skipped": 3,
                "incomplete": 2,
                "risk": 1,
                "pass": 0,
            }
            if order.get(one["status"], 0) >= order.get(worst_status, 0):
                worst_status = one["status"]
        all_reasons.extend(one.get("reasons") or [])
        for f in one.get("fixes") or []:
            if f not in all_fixes:
                all_fixes.append(f)
        if one.get("score") is not None:
            scores.append(float(one["score"]))

    return {
        "pass": overall_pass,
        "strict": True,
        "status": "pass" if overall_pass else worst_status,
        "reasons": all_reasons,
        "fixes": all_fixes,
        "score": max(scores) if scores else None,
        "threshold": thr,
    }
```

Keep implementation readable; if `_evaluate_one_evidence` is simpler as nested logic inside the main function, that is fine as long as tests pass.

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_identity_strict_gate.py -v
```

Expected: PASS

Also regression:

```bash
pytest tests/test_identity_drift.py -q
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tools/identity_drift.py tests/test_identity_strict_gate.py
git commit -m "feat(identity): evaluate_identity_strict_gate for opt-in CLI hard fail"
```

---

### Task 2: Wire `--strict-identity` on sequence handoff + extend-prompt

**Files:**
- Modify: `tools/cli/sequence_commands.py` (`seq_handoff`, `seq_extend_prompt`)

- [ ] **Step 1: Add import**

Near other identity imports (top of file already has `from identity_drift import DEFAULT_DRIFT_THRESHOLD, score_identity_drift`):

```python
from identity_drift import (
    DEFAULT_DRIFT_THRESHOLD,
    evaluate_identity_strict_gate,
    score_identity_drift,
)
```

(Merge with existing import line.)

- [ ] **Step 2: Update `seq_handoff`**

Replace the handoff command body with evaluate-before-write:

```python
    @app.command("handoff")
    def seq_handoff(
        name: str = typer.Argument(..., help="Sequence name or slug"),
        clip: str = typer.Option(..., "--clip", "-c", help="Source clip ID"),
        output: str = typer.Option(None, "--output", "-o"),
        strict_identity: bool = typer.Option(
            False,
            "--strict-identity",
            help="Exit 1 if drift evidence missing or identity risk (opt-in hard fail)",
        ),
    ):
        """Generate extend/stitch handoff packet from a clip."""
        seq, seq_path = require_sequence_bundle(name)
        source = require_clip(seq, clip)

        if strict_identity:
            gate = evaluate_identity_strict_gate(clip=source)
            if not gate.get("pass"):
                console.print(
                    f"[red]Identity strict gate failed[/red] "
                    f"(status={gate.get('status')}, score={gate.get('score')})"
                )
                for r in gate.get("reasons") or []:
                    console.print(f"  • {r}")
                if gate.get("fixes"):
                    console.print("[yellow]Fixes:[/yellow]")
                    for fix in gate["fixes"]:
                        console.print(f"  → {fix}")
                raise typer.Exit(1)

        handoff = build_handoff_from_clip(source, memory_bank=seq.get("memory_bank"))

        # Optional second check if handoff has evidence that worsens (should not if clip was source)
        if strict_identity and handoff.get("drift_evidence") is not None:
            gate2 = evaluate_identity_strict_gate(
                clip=source, drift_evidence=handoff.get("drift_evidence")
            )
            if not gate2.get("pass"):
                console.print("[red]Identity strict gate failed on handoff evidence[/red]")
                for r in gate2.get("reasons") or []:
                    console.print(f"  • {r}")
                raise typer.Exit(1)

        out_path = Path(output) if output else seq_path.parent / f"handoff_{clip}.json"
        out_path.write_text(json.dumps(handoff, indent=2))
        console.print(f"[green]✅ Handoff packet:[/green] {out_path}")
        if strict_identity:
            console.print("[dim]Identity strict gate: pass[/dim]")
        console.print(Panel(json.dumps(handoff, indent=2)[:2000], title="Handoff Preview", border_style="cyan"))
```

**Note:** Spec says evaluate before write. Prefer a **single** gate on the clip (and/or on projected evidence) before `write_text`. The second check is optional YAGNI — **prefer only one gate** before build/write:

Minimal preferred body:

```python
        seq, seq_path = require_sequence_bundle(name)
        source = require_clip(seq, clip)

        if strict_identity:
            gate = evaluate_identity_strict_gate(clip=source)
            if not gate.get("pass"):
                console.print(
                    f"[red]Identity strict gate failed[/red] "
                    f"(status={gate.get('status')}, score={gate.get('score')})"
                )
                for r in gate.get("reasons") or []:
                    console.print(f"  • {r}")
                if gate.get("fixes"):
                    console.print("[yellow]Fixes:[/yellow]")
                    for fix in gate["fixes"]:
                        console.print(f"  → {fix}")
                raise typer.Exit(1)

        handoff = build_handoff_from_clip(source, memory_bank=seq.get("memory_bank"))
        out_path = Path(output) if output else seq_path.parent / f"handoff_{clip}.json"
        out_path.write_text(json.dumps(handoff, indent=2))
        console.print(f"[green]✅ Handoff packet:[/green] {out_path}")
        if strict_identity:
            console.print("[dim]Identity strict gate: pass[/dim]")
        console.print(Panel(json.dumps(handoff, indent=2)[:2000], title="Handoff Preview", border_style="cyan"))
```

- [ ] **Step 3: Update `seq_extend_prompt`**

```python
    @app.command("extend-prompt")
    def seq_extend_prompt(
        name: str = typer.Argument(..., help="Sequence name or slug"),
        clip: str = typer.Option(..., "--clip", "-c", help="Previous clip ID"),
        beat: str = typer.Option(..., "--beat", "-b", help="Next narrative beat"),
        character: str = typer.Option("", "--character", help="CHARACTER_DNA injection block"),
        output: str = typer.Option(None, "--output", "-o"),
        strict_identity: bool = typer.Option(
            False,
            "--strict-identity",
            help="Exit 1 if drift evidence missing or identity risk (opt-in hard fail)",
        ),
    ):
        """Build Grok Imagine Video 1.5 extend prompt for the next clip."""
        seq = require_sequence(name)
        source = require_clip(seq, clip)

        if strict_identity:
            gate = evaluate_identity_strict_gate(clip=source)
            if not gate.get("pass"):
                console.print(
                    f"[red]Identity strict gate failed[/red] "
                    f"(status={gate.get('status')}, score={gate.get('score')})"
                )
                for r in gate.get("reasons") or []:
                    console.print(f"  • {r}")
                if gate.get("fixes"):
                    console.print("[yellow]Fixes:[/yellow]")
                    for fix in gate["fixes"]:
                        console.print(f"  → {fix}")
                raise typer.Exit(1)

        prompt = build_extend_prompt(seq, source, beat, character_injection=character)
        if output:
            Path(output).write_text(prompt)
            console.print(f"[green]✅ Extend prompt saved:[/green] {output}")
        else:
            console.print(Panel(prompt, title="1.5 Extend Prompt", border_style="green"))
        if strict_identity:
            console.print("[dim]Identity strict gate: pass[/dim]")
```

- [ ] **Step 4: Run unit tests + import smoke**

```bash
pytest tests/test_identity_strict_gate.py tests/test_identity_drift.py tests/test_drift_evidence_handoff.py -q
python -c "from cli.sequence_commands import register; print('ok')"
```

Expected: PASS / ok  
(CWD may need `cd` repo root and `PYTHONPATH=tools` if import path requires it — match how other CLI tests run.)

- [ ] **Step 5: Commit**

```bash
git add tools/cli/sequence_commands.py
git commit -m "feat(cli): --strict-identity on sequence handoff and extend-prompt"
```

---

### Task 3: Protocol + CHANGELOG

**Files:**
- Modify: `references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Append CLI subsection to protocol**

After the Validator section (or at end before footer), add:

```markdown
## CLI opt-in hard mode

Default: no CLI hard-block (agent protocol + warn-only handoff validator).

With **`--strict-identity`** on:

- `sequence handoff`
- `sequence extend-prompt`

…the CLI exits **1** when drift evidence is missing, incomplete, skipped, or `status=risk` (score ≥ 2.5). Evaluation runs **before** writing handoff/prompt artifacts.

```bash
python tools/cinematic_studio_cli.py sequence handoff "Seq" --clip clip_001 --strict-identity
python tools/cinematic_studio_cli.py sequence extend-prompt "Seq" --clip clip_001 --beat "next" --strict-identity
```

Helper: `evaluate_identity_strict_gate` in `tools/identity_drift.py`.
```

Also update the top **Enforcement** line from “CLI does **not** hard-block” to:

```markdown
**Enforcement:** Agent protocol by default; CLI **opt-in** hard-fail via `--strict-identity` on `sequence handoff` / `extend-prompt`. Handoff validator remains warn-only unless separately extended.
```

- [ ] **Step 2: CHANGELOG Unreleased**

Under `### Added` (create if needed next to existing Identity Continuity bullet):

```markdown
- **`--strict-identity`** on `sequence handoff` and `sequence extend-prompt` — opt-in hard-fail when drift evidence is missing or identity risk (default soft path unchanged).
```

- [ ] **Step 3: Commit**

```bash
git add references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md CHANGELOG.md
git commit -m "docs: document --strict-identity CLI opt-in hard mode"
```

---

### Task 4: Verification gate

- [ ] **Step 1: Full related tests**

```bash
pytest tests/test_identity_strict_gate.py tests/test_identity_drift.py \
  tests/test_drift_evidence_handoff.py tests/test_handoff_validator.py -q
```

Expected: all PASS

- [ ] **Step 2: Manual gate smoke (optional if no sequence fixtures)**

If a sequence exists under `sequences/`:

```bash
# Should fail with exit 1 when clip has no identity_drift
python tools/cinematic_studio_cli.py sequence handoff "<name>" --clip clip_001 --strict-identity; echo exit:$?
```

Without flag should still write handoff (exit 0).

- [ ] **Step 3: Grep wiring**

```bash
grep -n "strict-identity\|evaluate_identity_strict_gate" tools/cli/sequence_commands.py tools/identity_drift.py
```

Expected: matches present

- [ ] **Step 4: No empty commit** if nothing to fix

---

## Spec coverage checklist

| Spec requirement | Task |
|------------------|------|
| `evaluate_identity_strict_gate` | Task 1 |
| Missing + risk fail matrix | Task 1 |
| Skipped fails under strict | Task 1 |
| Multi-cast any fail | Task 1 |
| `--strict-identity` on handoff | Task 2 |
| `--strict-identity` on extend-prompt | Task 2 |
| Evaluate before write | Task 2 |
| Default unchanged | Task 2 (flag default False) |
| Protocol docs | Task 3 |
| CHANGELOG | Task 3 |
| No Bible auto-strict / QA gating | (omitted by design) |

---

## Execution handoff

Plan complete and saved to `docs/development/superpowers/plans/2026-07-11-identity-strict-cli-gates-implementation.md`.

**Two execution options:**

1. **Subagent-Driven (recommended)** — fresh subagent per task, review between tasks  
2. **Inline Execution** — this session with executing-plans  

Which approach?
