# Generation Handoff Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add semantic readiness checks for `imagine_agent_mode_handoff` packets: pure evaluator, validator warnings, and opt-in `--strict-handoff` on `imagine agent-handoff` (evaluate before write).

**Architecture:** New `tools/handoff_readiness.py` with `evaluate_imagine_handoff_readiness`. Wire into handoff validator (warn-only) and `imagine agent-handoff --strict-handoff` (exit 1 on blockers). Light docs on protocol + Studio Director / Prompt Master / I2V. No new schema required fields; no new agents.

**Tech Stack:** Python 3.11+, existing `handoff_schema` / validator / Typer, pytest. No new deps.

**Design:** [docs/development/superpowers/specs/2026-07-11-generation-handoff-readiness-design.md](../specs/2026-07-11-generation-handoff-readiness-design.md)

---

## Principles

1. Schema validation stays the hard structural gate.  
2. Readiness is semantic; default soft.  
3. Strict only on `--strict-handoff`.  
4. TDD for the pure helper.

## Out of scope

Specialist-order automation, new required JSON fields, hard-default refuse, closed-loop job return.

---

## File map

| Path | Action |
|------|--------|
| `tools/handoff_readiness.py` | **Create** |
| `tests/test_handoff_readiness.py` | **Create** |
| `.grok/skills/handoff-packet-validator/scripts/validate_handoff.py` | Wire warnings |
| `tests/test_handoff_validator.py` | Assert readiness warning text |
| `tools/cli/imagine_commands.py` | `--strict-handoff` |
| `references/agents/IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md` | Subsection |
| Role Cards / skills (thin) | Studio Director, Prompt Master, I2V |
| `CHANGELOG.md` | Unreleased |

---

### Task 1: Pure readiness evaluator

**Files:**
- Create: `tools/handoff_readiness.py`
- Create: `tests/test_handoff_readiness.py`

- [ ] **Step 1: Write failing tests**

```python
"""Semantic readiness for imagine_agent_mode_handoff packets."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from handoff_readiness import evaluate_imagine_handoff_readiness  # noqa: E402
from handoff_schema import PACKET_TYPE_IMAGINE_AGENT_MODE  # noqa: E402


def _base(**overrides):
    p = {
        "packet_type": PACKET_TYPE_IMAGINE_AGENT_MODE,
        "protocol_version": "3.7.1",
        "studio_version": "3.8.1",
        "target_surface": "grok_build_tools",
        "execution_mode": "image_prompt",
        "subject_id": "shot_001",
        "prompt": "Hero stands in rain, charcoal coat, soft key light",
        "reference_hints": [],
        "model_stack": {"chat": "grok-4.5", "imagine_image": "grok-imagine-image"},
        "quota_note": "Prefer Fast mode; 1 still budgeted",
        "return_path": "sfw record + QA Guardian",
        "handoff_steps": ["1. image_gen", "2. save artifact"],
    }
    p.update(overrides)
    return p


def test_image_prompt_ready_passes() -> None:
    r = evaluate_imagine_handoff_readiness(_base())
    assert r["pass"] is True
    assert r["blockers"] == []


def test_i2v_empty_references_blocks() -> None:
    r = evaluate_imagine_handoff_readiness(
        _base(
            execution_mode="image_to_video",
            prompt="Slow dolly push-in, first frame locked, motion on coat",
            video_pipeline_spec='[VIDEO_PIPELINE_SPEC: model="grok-imagine-video"]',
            sound_layer="ambience rain",
            reference_hints=[],
            return_path="chain QA then sequence record",
            handoff_steps=["1. image_to_video", "2. QA"],
        )
    )
    assert r["pass"] is False
    assert any("reference" in b.lower() for b in r["blockers"])


def test_video_without_motion_cues_blocks() -> None:
    r = evaluate_imagine_handoff_readiness(
        _base(
            execution_mode="video_prompt",
            prompt="A person stands outside",
            video_pipeline_spec='[VIDEO_PIPELINE_SPEC: model="grok-imagine-video"]',
            sound_layer="room tone",
            reference_hints=["plate_1"],
            return_path="run QA Guardian",
            handoff_steps=["1. generate", "2. record"],
        )
    )
    assert r["pass"] is False
    assert any("motion" in b.lower() or "i2v" in b.lower() for b in r["blockers"])


def test_video_with_motion_and_refs_passes() -> None:
    r = evaluate_imagine_handoff_readiness(
        _base(
            execution_mode="image_to_video",
            prompt="Slow dolly on hero, first frame lock, coat motion, lip-sync soft",
            video_pipeline_spec='[VIDEO_PIPELINE_SPEC: model="grok-imagine-video-1.5"]',
            sound_layer="Sound Layer: breath, rain",
            reference_hints=["reference_image_id: plate_001"],
            return_path="sfw record + chain QA",
            handoff_steps=["1. image_to_video", "2. save", "3. QA"],
        )
    )
    assert r["pass"] is True


def test_weak_return_path_blocks() -> None:
    r = evaluate_imagine_handoff_readiness(_base(return_path="done"))
    assert r["pass"] is False
    assert any("return_path" in b.lower() for b in r["blockers"])


def test_placeholder_quota_warns_but_passes() -> None:
    r = evaluate_imagine_handoff_readiness(_base(quota_note="tbd"))
    assert r["pass"] is True
    assert any("quota" in w.lower() for w in r["warnings"])


def test_wrong_packet_type_is_pass_noop() -> None:
    r = evaluate_imagine_handoff_readiness({"packet_type": "sequence_extend_handoff"})
    assert r["pass"] is True
    assert r.get("skipped") is True or not r["blockers"]
```

- [ ] **Step 2: Run — expect ImportError**

```bash
pytest tests/test_handoff_readiness.py -v
```

- [ ] **Step 3: Implement `tools/handoff_readiness.py`**

```python
#!/usr/bin/env python3
"""Semantic readiness checks for Imagine Agent Mode handoff packets."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from handoff_schema import (
    PACKET_TYPE_IMAGINE_AGENT_MODE,
    is_video_execution_mode,
)
from studio_paths import STUDIO_ROOT

MOTION_CUES = (
    "motion",
    "camera",
    "dolly",
    "pan",
    "tilt",
    "track",
    "ken burns",
    "first frame",
    "i2v",
    "extend",
    "momentum",
    "lip-sync",
    "lip sync",
    "physics",
)
RETURN_CUES = (
    "qa",
    "record",
    "chain",
    "artifact",
    "sfw",
    "sequence",
    "handoff",
    "validate",
    "polish",
)
PLACEHOLDER_QUOTA = frozenset({"todo", "tbd", "n/a", "na", "none", "-", "—"})
PROTOCOL_OK = frozenset({"3.7.1", "3.8.0", "3.8.1"})


def _studio_version() -> str:
    vf = STUDIO_ROOT / "VERSION"
    if vf.is_file():
        return vf.read_text(encoding="utf-8").strip() or "3.8.1"
    return "3.8.1"


def _has_cue(text: str, cues: tuple[str, ...]) -> bool:
    low = (text or "").lower()
    return any(c in low for c in cues)


def evaluate_imagine_handoff_readiness(
    packet: dict[str, Any],
    *,
    studio_version: str | None = None,
) -> dict[str, Any]:
    """
    Semantic readiness for imagine_agent_mode_handoff.

    pass=False only when blockers present. warnings alone keep pass=True.
    """
    if packet.get("packet_type") != PACKET_TYPE_IMAGINE_AGENT_MODE:
        return {
            "pass": True,
            "strict": True,
            "skipped": True,
            "warnings": [],
            "blockers": [],
            "fixes": [],
            "checks": [],
        }

    warnings: list[str] = []
    blockers: list[str] = []
    fixes: list[str] = []
    checks: list[dict[str, Any]] = []
    mode = str(packet.get("execution_mode") or "")
    prompt = str(packet.get("prompt") or "")
    refs = packet.get("reference_hints")
    if not isinstance(refs, list):
        refs = []

    # GHR-02 / GHR-03 video
    if is_video_execution_mode(mode):
        if mode in ("image_to_video", "reference_to_video") and len(refs) == 0:
            blockers.append(
                "GHR-02: reference_hints empty for still→video mode "
                f"({mode})"
            )
            fixes.append("Add locked plate reference_image_id / path to reference_hints")
        motion_ok = _has_cue(prompt, MOTION_CUES)
        for key in ("i2v_motion_block", "motion_vector", "motion_block"):
            val = packet.get(key)
            if isinstance(val, dict) and any(str(v).strip() for v in val.values()):
                motion_ok = True
            if isinstance(val, str) and val.strip():
                motion_ok = True
        if not motion_ok:
            blockers.append(
                "GHR-03: video mode prompt lacks motion/I2V cues "
                "(e.g. dolly, first frame, momentum, lip-sync)"
            )
            fixes.append("Activate I2V Specialist; add MOTION_VECTOR language to prompt")

    # GHR-04 return_path
    ret = str(packet.get("return_path") or "")
    if not _has_cue(ret, RETURN_CUES):
        blockers.append(
            "GHR-04: return_path missing re-entry cue "
            "(qa/record/chain/artifact/sfw/sequence/…)"
        )
        fixes.append("Set return_path e.g. 'sfw record + QA Guardian' or 'chain QA'")

    # GHR-05 quota
    quota = str(packet.get("quota_note") or "").strip().lower()
    if quota in PLACEHOLDER_QUOTA:
        warnings.append("GHR-05: quota_note looks like a placeholder")
        fixes.append("Replace quota_note with a real budget/Fast-mode note")

    # GHR-06 studio version
    current = studio_version or _studio_version()
    pkt_ver = str(packet.get("studio_version") or "").strip()
    if pkt_ver and current and pkt_ver != current:
        warnings.append(
            f"GHR-06: studio_version={pkt_ver!r} differs from current {current!r}"
        )

    # GHR-07 protocol
    proto = str(packet.get("protocol_version") or "").strip()
    if proto and proto not in PROTOCOL_OK and proto != current:
        warnings.append(f"GHR-07: protocol_version={proto!r} not in known allowlist")

    # GHR-08 steps
    steps = packet.get("handoff_steps")
    if isinstance(steps, list) and len(steps) < 2:
        warnings.append("GHR-08: handoff_steps has fewer than 2 steps")

    return {
        "pass": len(blockers) == 0,
        "strict": True,
        "skipped": False,
        "warnings": warnings,
        "blockers": blockers,
        "fixes": fixes,
        "checks": checks,
    }
```

Adjust imports if `studio_paths.STUDIO_ROOT` differs — use same pattern as `plugin_catalog` / `shared.py`.

- [ ] **Step 4: pytest pass**

```bash
pytest tests/test_handoff_readiness.py -v
```

- [ ] **Step 5: Commit**

```bash
git add tools/handoff_readiness.py tests/test_handoff_readiness.py
git commit -m "feat(handoff): evaluate_imagine_handoff_readiness semantic checks"
```

---

### Task 2: Validator warnings

**Files:**
- Modify: `.grok/skills/handoff-packet-validator/scripts/validate_handoff.py`
- Modify: `tests/test_handoff_validator.py`

- [ ] **Step 1: After schema validation succeeds, run readiness for agent-mode packets**

In `validate_packet_with_warnings` (or main path after issues collected):

```python
from handoff_readiness import evaluate_imagine_handoff_readiness
# ensure tools on path already

def validate_packet_with_warnings(...):
    ...
    issues, warnings = ...
    if not issues and data.get("packet_type") == PACKET_TYPE_IMAGINE_AGENT_MODE:
        ready = evaluate_imagine_handoff_readiness(data)
        for b in ready.get("blockers") or []:
            warnings.append(f"readiness blocker: {b}")
        for w in ready.get("warnings") or []:
            warnings.append(f"readiness: {w}")
    return issues, warnings
```

Blockers as **warnings** in validator (exit 0); only CLI strict hard-fails.

- [ ] **Step 2: Test**

```python
def test_agent_mode_readiness_warns_on_weak_return_path() -> None:
    result = run_validator({
        "packet_type": "imagine_agent_mode_handoff",
        "protocol_version": "3.7.1",
        "studio_version": "3.8.1",
        "target_surface": "grok_build_tools",
        "execution_mode": "image_prompt",
        "subject_id": "shot_001",
        "prompt": "Hero in rain",
        "reference_hints": [],
        "model_stack": {"chat": "grok-4.5"},
        "quota_note": "1 still",
        "return_path": "done",
        "handoff_steps": ["1. gen", "2. save"],
    })
    assert result.returncode == 0
    out = (result.stdout + result.stderr).lower()
    assert "readiness" in out or "return_path" in out or "⚠️" in result.stdout
```

Existing `test_valid_imagine_agent_mode_handoff` should still exit 0 (prompt has “dolly”, refs non-empty, return_path has QA).

- [ ] **Step 3: Commit**

```bash
git add .grok/skills/handoff-packet-validator/scripts/validate_handoff.py tests/test_handoff_validator.py
git commit -m "feat(handoff): warn on agent-mode readiness in validator"
```

---

### Task 3: CLI `--strict-handoff`

**Files:**
- Modify: `tools/cli/imagine_commands.py` (`imagine_agent_handoff`)

- [ ] **Step 1: Add flag and gate before write**

```python
        strict_handoff: bool = typer.Option(
            False,
            "--strict-handoff",
            help="Exit 1 if semantic readiness fails (blockers); do not write output",
        ),
```

After successful `build_agent_mode_handoff`:

```python
        from handoff_readiness import evaluate_imagine_handoff_readiness

        ready = evaluate_imagine_handoff_readiness(packet)
        for w in ready.get("warnings") or []:
            console.print(f"[yellow]⚠️  {w}[/yellow]")
        if ready.get("blockers"):
            for b in ready["blockers"]:
                console.print(f"[yellow]⚠️  readiness blocker: {b}[/yellow]")
            if ready.get("fixes"):
                console.print("[dim]Fixes:[/dim]")
                for f in ready["fixes"]:
                    console.print(f"  → {f}")
        if strict_handoff and not ready.get("pass"):
            console.print("[red]Handoff readiness failed (--strict-handoff)[/red]")
            raise typer.Exit(1)

        # then _write_handoff_output ...
```

- [ ] **Step 2: Commit**

```bash
git add tools/cli/imagine_commands.py
git commit -m "feat(cli): imagine agent-handoff --strict-handoff"
```

---

### Task 4: Docs + light agent notes + CHANGELOG

- [ ] **Step 1: Protocol subsection** in `references/agents/IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md`

```markdown
## Handoff readiness (semantic quality)

Structural validation is not enough. Run semantic readiness before spend:

```bash
python .grok/skills/handoff-packet-validator/scripts/validate_handoff.py packet.json
python tools/cinematic_studio_cli.py imagine agent-handoff ... --strict-handoff
```

Blockers (strict): empty refs on i2v; video without motion cues; weak return_path.
Warnings: placeholder quota_note; studio_version mismatch; short handoff_steps.
```

- [ ] **Step 2: Thin notes** on Studio Director, Imagine Prompt Master, I2V Role Card or skill (3–5 lines each pointing at readiness + GHR-02/03/04).

- [ ] **Step 3: CHANGELOG Unreleased**

```markdown
- **Generation handoff readiness** — semantic checks for `imagine_agent_mode_handoff` (motion cues, references, return_path); validator warnings; `imagine agent-handoff --strict-handoff`.
```

- [ ] **Step 4: Verify**

```bash
pytest tests/test_handoff_readiness.py tests/test_handoff_validator.py tests/test_handoff_schema.py -q
```

- [ ] **Step 5: Commit**

```bash
git add references/agents/IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md \
  references/agents/Studio_Director.md \
  references/agents/Imagine_Prompt_Master.md \
  references/agents/Image_to_Video_Specialist.md \
  .grok/skills/studio-director/SKILL.md \
  .grok/skills/imagine-prompt-master/SKILL.md \
  .grok/skills/image-to-video-specialist/SKILL.md \
  CHANGELOG.md
# only add files that exist and were edited
git commit -m "docs: generation handoff readiness protocol and agent notes"
```

---

## Spec coverage

| Spec | Task |
|------|------|
| evaluate_imagine_handoff_readiness | Task 1 |
| GHR-02/03/04 blockers | Task 1 |
| GHR-05–08 warnings | Task 1 |
| Validator warn | Task 2 |
| --strict-handoff before write | Task 3 |
| Protocol + agents + CHANGELOG | Task 4 |
| No new schema fields / agents | All |

---

## Execution handoff

Plan complete and saved to `docs/development/superpowers/plans/2026-07-11-generation-handoff-readiness-implementation.md`.

**Two execution options:**

1. **Subagent-Driven (recommended)**  
2. **Inline Execution**  

Which approach?
