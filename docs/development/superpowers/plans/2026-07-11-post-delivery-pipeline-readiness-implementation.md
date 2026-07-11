# Post-Delivery Pipeline Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add opt-in delivery pipeline readiness so `sequence polish` / `sequence deliver` can hard-fail when prior stages or Go clips are missing, while default stays soft.

**Architecture:** Pure `evaluate_delivery_pipeline_readiness` in `tools/delivery_readiness.py`. Wire `--strict-delivery` on polish/deliver CLI; always print warnings; exit 1 only with flag. Align eligibility with `assembly_editor.build_edl` approved rules.

**Tech Stack:** Python 3.11+, existing sequence CLI / assembly_editor / sequence_polish / sequence_delivery, pytest. No new deps.

**Design:** [docs/development/superpowers/specs/2026-07-11-post-delivery-pipeline-readiness-design.md](../specs/2026-07-11-post-delivery-pipeline-readiness-design.md)

---

## Principles

1. Soft by default; hard only with `--strict-delivery`.  
2. Evaluate **before** polish/deliver side effects.  
3. TDD for pure helper.  
4. YAGNI — no color LUT engine, no new agents.

## Out of scope

Hard-default refuse; full color grade pipeline; social-crop as blockers.

---

## File map

| Path | Action |
|------|--------|
| `tools/delivery_readiness.py` | **Create** |
| `tests/test_delivery_readiness.py` | **Create** |
| `tools/cli/sequence_commands.py` | `--strict-delivery` on polish + deliver |
| `tools/assembly_editor.py` | Reuse eligibility helpers if extractable (optional) |
| Role Cards / skills | Assembly, AI Polish, cinematic-ffmpeg (thin notes) |
| `CHANGELOG.md` | Unreleased |

---

### Task 1: Pure readiness helper + tests

**Files:**
- Create: `tools/delivery_readiness.py`
- Create: `tests/test_delivery_readiness.py`

- [ ] **Step 1: Write failing tests**

```python
"""Delivery pipeline readiness (polish / deliver order gates)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from delivery_readiness import (  # noqa: E402
    clip_eligible_for_assembly,
    evaluate_delivery_pipeline_readiness,
)


def _seq(clips, slug="demo"):
    return {
        "sequence_name": "Demo",
        "slug": slug,
        "clips": clips,
    }


def _go_clip(cid="clip_001", **extra):
    c = {
        "clip_id": cid,
        "status": "approved",
        "duration_seconds": 8,
        "chain_qa": {"decision": "go"},
    }
    c.update(extra)
    return c


def test_polish_blocks_when_no_eligible_clips() -> None:
    seq = _seq([{"clip_id": "clip_001", "status": "pending", "chain_qa": {"decision": "no_go"}}])
    r = evaluate_delivery_pipeline_readiness(seq, stage="polish", approved_only=True)
    assert r["pass"] is False
    assert any("eligible" in b.lower() or "approved" in b.lower() or "go" in b.lower() for b in r["blockers"])


def test_polish_passes_with_go_clip() -> None:
    seq = _seq([_go_clip()])
    r = evaluate_delivery_pipeline_readiness(seq, stage="polish", approved_only=True)
    assert r["pass"] is True


def test_deliver_blocks_without_polished_media(tmp_path, monkeypatch) -> None:
    import delivery_readiness as dr
    import studio_paths

    monkeypatch.setattr(dr, "POLISHED_DIR", tmp_path / "polished")
    (tmp_path / "polished" / "demo").mkdir(parents=True)
    seq = _seq([_go_clip()], slug="demo")
    r = evaluate_delivery_pipeline_readiness(seq, stage="deliver", approved_only=True)
    assert r["pass"] is False
    assert any("polish" in b.lower() for b in r["blockers"])


def test_deliver_passes_with_polished_mp4(tmp_path, monkeypatch) -> None:
    import delivery_readiness as dr

    monkeypatch.setattr(dr, "POLISHED_DIR", tmp_path / "polished")
    d = tmp_path / "polished" / "demo"
    d.mkdir(parents=True)
    (d / "clip_001.mp4").write_bytes(b"fake")
    seq = _seq([_go_clip()], slug="demo")
    r = evaluate_delivery_pipeline_readiness(seq, stage="deliver", approved_only=True)
    assert r["pass"] is True


def test_clip_eligible_helper() -> None:
    assert clip_eligible_for_assembly(_go_clip()) is True
    assert clip_eligible_for_assembly({"clip_id": "x", "status": "pending", "chain_qa": {}}) is False
```

- [ ] **Step 2: pytest fail expected**

```bash
pytest tests/test_delivery_readiness.py -v
```

- [ ] **Step 3: Implement `tools/delivery_readiness.py`**

```python
#!/usr/bin/env python3
"""Readiness checks for sequence polish / deliver pipeline order."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Literal

from studio_paths import EDL_DIR, POLISHED_DIR

Stage = Literal["polish", "deliver"]


def clip_eligible_for_assembly(clip: dict[str, Any]) -> bool:
    """Match assembly_editor approved_only spirit."""
    status = clip.get("status", "pending")
    if status in ("approved", "qa_pass"):
        return True
    qa = clip.get("chain_qa") or clip.get("nsfw_chain_qa") or {}
    return qa.get("decision") == "go"


def _eligible_clips(seq: dict[str, Any], *, approved_only: bool) -> list[dict[str, Any]]:
    clips = seq.get("clips") or []
    if not approved_only:
        return list(clips)
    return [c for c in clips if clip_eligible_for_assembly(c)]


def _edl_path(slug: str) -> Path:
    # Matches assembly_editor.load_edl / save_edl
    return EDL_DIR / slug / "assembly_edl.json"


def _has_polished_media(slug: str) -> bool:
    d = POLISHED_DIR / slug
    if not d.is_dir():
        return False
    return any(d.glob("*.mp4"))


def evaluate_delivery_pipeline_readiness(
    seq: dict[str, Any],
    *,
    stage: Stage,
    approved_only: bool = True,
) -> dict[str, Any]:
    """
    pass=False only when blockers present.
    """
    slug = str(seq.get("slug") or "sequence")
    blockers: list[str] = []
    warnings: list[str] = []
    fixes: list[str] = []

    eligible = _eligible_clips(seq, approved_only=approved_only)
    edl_file = _edl_path(slug)

    if not edl_file.is_file():
        warnings.append(
            f"EDL missing at {edl_file} — recommend: sequence edl \"{seq.get('sequence_name', slug)}\""
        )
        fixes.append(f'Run: python tools/cinematic_studio_cli.py sequence edl "{seq.get("sequence_name", slug)}"')

    if stage == "polish":
        if approved_only and not eligible:
            blockers.append(
                "No Go/approved clips eligible for polish (approved_only=True)"
            )
            fixes.append("Run chain QA to Go or use polish with all clips only if intentional")
        if seq.get("color_grade") is None and not (seq.get("grade_notes") or seq.get("lut")):
            warnings.append(
                "No color_grade/grade_notes/lut on sequence — color pass recommended before hero polish"
            )

    elif stage == "deliver":
        if not _has_polished_media(slug):
            blockers.append(
                f"No polished mp4 under polished/{slug}/ — run sequence polish first"
            )
            fixes.append(
                f'Run: python tools/cinematic_studio_cli.py sequence polish "{seq.get("sequence_name", slug)}"'
            )
        if approved_only and not eligible:
            blockers.append(
                "No Go/approved clips for delivery assembly (approved_only=True)"
            )
        if shutil.which("ffmpeg") is None:
            warnings.append("ffmpeg not on PATH — deliver may be manifest-only")

    else:
        blockers.append(f"Unknown stage: {stage!r}")

    return {
        "pass": len(blockers) == 0,
        "strict": True,
        "stage": stage,
        "slug": slug,
        "eligible_count": len(eligible),
        "blockers": blockers,
        "warnings": warnings,
        "fixes": fixes,
    }
```

Note: `EDL_DIR` layout — check `assembly_editor.save_edl` for actual path pattern and match it.

- [ ] **Step 4: Fix EDL path if needed**

Inspect `save_edl` / `load_edl` in `assembly_editor.py` and align `_edl_path`.

- [ ] **Step 5: pytest pass + commit**

```bash
pytest tests/test_delivery_readiness.py -v
git add tools/delivery_readiness.py tests/test_delivery_readiness.py
git commit -m "feat(delivery): pipeline readiness evaluator for polish/deliver"
```

---

### Task 2: Wire CLI `--strict-delivery`

**Files:**
- Modify: `tools/cli/sequence_commands.py` (`seq_polish`, `seq_deliver`)

- [ ] **Step 1: Helper to print readiness**

```python
def _print_delivery_readiness(ready: dict) -> None:
    for w in ready.get("warnings") or []:
        console.print(f"[yellow]⚠️  {w}[/yellow]")
    for b in ready.get("blockers") or []:
        console.print(f"[yellow]⚠️  readiness blocker: {b}[/yellow]")
    if ready.get("fixes"):
        console.print("[dim]Fixes:[/dim]")
        for f in ready["fixes"]:
            console.print(f"  → {f}")
```

- [ ] **Step 2: `seq_polish`**

Add:

```python
        strict_delivery: bool = typer.Option(
            False,
            "--strict-delivery",
            help="Exit 1 if pipeline readiness fails (no Go clips / not ready to polish)",
        ),
```

After `seq = require_sequence(name)`:

```python
        from delivery_readiness import evaluate_delivery_pipeline_readiness
        ready = evaluate_delivery_pipeline_readiness(
            seq, stage="polish", approved_only=not bool(clip)  # or True always when no --all
        )
        # Prefer approved_only=True unless a future --all-clips on polish exists
        ready = evaluate_delivery_pipeline_readiness(seq, stage="polish", approved_only=True)
        _print_delivery_readiness(ready)
        if strict_delivery and not ready.get("pass"):
            console.print("[red]Delivery readiness failed (--strict-delivery)[/red]")
            raise typer.Exit(1)
```

- [ ] **Step 3: `seq_deliver`**

```python
        strict_delivery: bool = typer.Option(
            False,
            "--strict-delivery",
            help="Exit 1 if no polished media / not ready to deliver",
        ),
```

```python
        ready = evaluate_delivery_pipeline_readiness(
            seq, stage="deliver", approved_only=not all_clips
        )
        _print_delivery_readiness(ready)
        if strict_delivery and not ready.get("pass"):
            console.print("[red]Delivery readiness failed (--strict-delivery)[/red]")
            raise typer.Exit(1)
```

Then existing `deliver_sequence(...)`.

- [ ] **Step 4: Commit**

```bash
git add tools/cli/sequence_commands.py
git commit -m "feat(cli): --strict-delivery on sequence polish and deliver"
```

---

### Task 3: Agent notes + CHANGELOG + verify

- [ ] **Step 1:** Short notes in Assembly Editor, AI Polish Director, cinematic-ffmpeg skills/Role Cards: order `edl → polish → deliver`; automation uses `--strict-delivery`.

- [ ] **Step 2: CHANGELOG Unreleased**

```markdown
- **Post-delivery pipeline readiness** — `evaluate_delivery_pipeline_readiness`; `--strict-delivery` on `sequence polish` / `sequence deliver` (soft by default).
```

- [ ] **Step 3: Verify**

```bash
pytest tests/test_delivery_readiness.py tests/test_assembly_editor.py -q 2>/dev/null || pytest tests/test_delivery_readiness.py -q
```

- [ ] **Step 4: Commit docs**

```bash
git add CHANGELOG.md references/agents/*.md .grok/skills/*/SKILL.md
# only edited files
git commit -m "docs: post-delivery pipeline readiness and --strict-delivery"
```

---

## Spec coverage

| Spec | Task |
|------|------|
| evaluate_delivery_pipeline_readiness | Task 1 |
| polish / deliver stage rules | Task 1 |
| --strict-delivery | Task 2 |
| Soft default | Task 2 |
| Agent notes + CHANGELOG | Task 3 |

---

## Execution handoff

Plan complete at `docs/development/superpowers/plans/2026-07-11-post-delivery-pipeline-readiness-implementation.md`.

**Two execution options:**

1. **Subagent-Driven (recommended)**  
2. **Inline Execution**  

Which approach?
