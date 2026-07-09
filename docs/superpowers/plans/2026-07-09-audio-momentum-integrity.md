# Audio Momentum Integrity (#6) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Diff/validate `AUDIO_MOMENTUM_VECTOR` across stitch boundaries — flag dropped dialogue state, SFX timing gaps, and music cue breaks — and feed evidence into Chain QA Assist (`audio_momentum_sync`).

**Architecture:** Pure module `tools/audio_momentum.py` scores integrity between previous and current AMV (+ optional bank audio). CLI `sequence amv-check`. Chain QA Assist v2.1 overlays `audio_momentum_sync` from the report (same pattern as drift/seam). No waveform analysis, no new deps.

**Tech Stack:** Python 3.11+, existing AMV keys on clips, `sequence_memory` bank audio section, Typer/Rich, pytest.

**Design:** [docs/superpowers/specs/2026-07-09-long-form-continuity-roadmap-design.md](../specs/2026-07-09-long-form-continuity-roadmap-design.md) — backlog **#6**

**Depends on:** #1–#5 helpful for patterns; only #3 assist wiring is a soft dependency (can land pure tool first).

---

## Principles

1. **Metadata integrity first** — compare structured AMV fields, not audio files.
2. **Higher integrity_score = better** (1–10); **risk_score** inverse for reporting (0–10 worse). Prefer one primary: `integrity_score` + `pass` (threshold 7.0, matches chain QA check threshold).
3. **Mirror drift/seam evidence pattern** — store `clip["audio_momentum_report"]`, attach under `evidence.audio_momentum` in assist.
4. **Opening clips** — soft pass (no previous AMV required).
5. **TDD + YAGNI** — no Sonic Architect Role Card rewrite; no native audio decoding.

## Out of scope

- #7 Emotional Temperature Gate
- Actual audio waveform / loudness analysis
- Auto-fix of AMV fields (report only; user/agent fills)
- NSFW-specific audio scorer fork

---

## AMV keys (canonical)

From `sequence_chain._empty_audio_momentum`:

- `dialogue_state` (str)
- `sfx_timing` (str)
- `emotional_tone_audio` (str)
- `music_cue_points` (list[str])
- `lip_sync_state` (str)

---

## Report contract

```python
{
  "clip_id": str | None,
  "previous_clip_id": str | None,
  "integrity_score": float,       # 1–10 higher better
  "pass": bool,                   # integrity_score >= 7.0
  "mode": "metadata",
  "factors": list[str],
  "fixes": list[str],
  "field_status": {
     "dialogue_state": "ok" | "dropped" | "empty" | "changed" | "n/a",
     ...
  },
  "suggested_audio_momentum_sync": float,  # 1–10 for chain QA key
}
```

### Scoring rules (`build_audio_momentum_report(clip, previous_clip=None, memory_bank=None)`)

**Opening (no previous):**
- Score 8.0 if any AMV field filled; 7.0 if all empty (opening seed optional); pass True unless completely empty and index>0 somehow.
- factors: "Opening clip — no prior AMV stitch"

**Extend (previous present):**
Start at 10.0, subtract penalties:

| Condition | Penalty | factor/fix |
|-----------|---------|-------------|
| Prev had non-empty `dialogue_state`, current empty | −2.5 | "dialogue_state dropped" / restore dialogue state |
| Prev had `sfx_timing`, current empty | −1.5 | "sfx_timing gap" |
| Prev had `emotional_tone_audio`, current empty | −1.0 | tone drop |
| Prev had music cues, current empty list | −1.5 | "music_cue_points cleared" |
| Prev had `lip_sync_state`, current empty | −1.0 | lip-sync continuity |
| Current AMV entirely empty on extend | −2.0 additional | "AMV empty on extend clip" |
| Current filled but zero token overlap with prev for dialogue when both non-empty and prev implies continuation (optional soft −0.5 if no shared tokens and both long) | −0.5 | weak dialogue continuity |
| Memory bank `audio.dialogue_state` set and current empty | −1.0 | bank dialogue not on clip |

Clamp to 1–10. `pass = integrity_score >= 7.0`.  
`suggested_audio_momentum_sync = integrity_score` (same scale).

---

## File map

| Path | Role |
|------|------|
| `tools/audio_momentum.py` | Integrity report |
| `tools/chain_qa_assist.py` | Overlay + evidence |
| `tools/cli/sequence_commands.py` | `amv-check` |
| `tests/test_audio_momentum.py` | Unit tests |
| `tests/test_chain_qa_assist.py` | Evidence overlay |
| `tests/test_cli_smoke.py` | Help |
| `CHANGELOG.md` | Unreleased |

---

### Task 1: Pure audio_momentum module + tests

**Files:**
- Create: `tools/audio_momentum.py`
- Create: `tests/test_audio_momentum.py`

- [ ] **Step 1: Failing tests**

```python
"""Tests for audio momentum integrity (roadmap #6)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from audio_momentum import (  # noqa: E402
    AMV_PASS_THRESHOLD,
    build_audio_momentum_report,
)
from sequence_chain import create_clip  # noqa: E402


def test_threshold_is_7() -> None:
    assert AMV_PASS_THRESHOLD == 7.0


def test_opening_clip_passes() -> None:
    clip = create_clip(prompt="Open")
    clip["index"] = 0
    clip["audio_momentum_vector"]["sfx_timing"] = "soft rain bed"
    report = build_audio_momentum_report(clip, previous_clip=None)
    assert report["pass"] is True
    assert report["integrity_score"] >= 7.0
    assert report["mode"] == "metadata"


def test_dropped_dialogue_fails() -> None:
    prev = create_clip()
    prev["index"] = 0
    prev["clip_id"] = "clip_001"
    prev["audio_momentum_vector"] = {
        "dialogue_state": "mid-sentence: I never said—",
        "sfx_timing": "rain on glass",
        "emotional_tone_audio": "tense whisper",
        "music_cue_points": ["low drone"],
        "lip_sync_state": "mouth open mid-word",
    }
    curr = create_clip()
    curr["index"] = 1
    curr["clip_id"] = "clip_002"
    curr["audio_momentum_vector"] = {
        "dialogue_state": "",
        "sfx_timing": "",
        "emotional_tone_audio": "",
        "music_cue_points": [],
        "lip_sync_state": "",
    }
    report = build_audio_momentum_report(curr, previous_clip=prev)
    assert report["pass"] is False
    assert report["integrity_score"] < 7.0
    assert report["field_status"]["dialogue_state"] == "dropped"
    assert any("dialogue" in f.lower() for f in report["factors"])
    assert report["suggested_audio_momentum_sync"] == report["integrity_score"]


def test_preserved_amv_passes() -> None:
    prev = create_clip()
    prev["index"] = 0
    prev["audio_momentum_vector"] = {
        "dialogue_state": "whisper continues",
        "sfx_timing": "rain continuous",
        "emotional_tone_audio": "intimate low",
        "music_cue_points": ["drone holds"],
        "lip_sync_state": "subtle lip motion",
    }
    curr = create_clip()
    curr["index"] = 1
    curr["audio_momentum_vector"] = {
        "dialogue_state": "whisper continues into next line",
        "sfx_timing": "rain continuous, glass tick",
        "emotional_tone_audio": "intimate low",
        "music_cue_points": ["drone holds"],
        "lip_sync_state": "subtle lip motion",
    }
    report = build_audio_momentum_report(curr, previous_clip=prev)
    assert report["pass"] is True
    assert report["integrity_score"] >= 7.0


def test_music_cues_cleared_penalized() -> None:
    prev = create_clip()
    prev["audio_momentum_vector"]["music_cue_points"] = ["theme swell t=3"]
    prev["audio_momentum_vector"]["dialogue_state"] = "ok"
    curr = create_clip()
    curr["index"] = 1
    curr["audio_momentum_vector"]["dialogue_state"] = "ok"
    curr["audio_momentum_vector"]["music_cue_points"] = []
    report = build_audio_momentum_report(curr, previous_clip=prev)
    assert any("music" in f.lower() for f in report["factors"])
    assert report["field_status"]["music_cue_points"] in ("dropped", "cleared", "empty")


def test_memory_bank_dialogue_mismatch() -> None:
    curr = create_clip()
    curr["index"] = 1
    curr["audio_momentum_vector"]["dialogue_state"] = ""
    prev = create_clip()
    prev["audio_momentum_vector"]["dialogue_state"] = "line"
    bank = {"audio": {"dialogue_state": "important bank line"}}
    report = build_audio_momentum_report(curr, previous_clip=prev, memory_bank=bank)
    assert any("bank" in f.lower() or "dialogue" in f.lower() for f in report["factors"])
```

- [ ] **Step 2: Implement `tools/audio_momentum.py`**

API:

```python
AMV_PASS_THRESHOLD = 7.0
AMV_KEYS = ("dialogue_state", "sfx_timing", "emotional_tone_audio", "music_cue_points", "lip_sync_state")

def build_audio_momentum_report(
    clip: dict,
    *,
    previous_clip: dict | None = None,
    memory_bank: dict | None = None,
) -> dict: ...
```

Helpers: `_amv(clip)`, `_filled(val)`, `_clamp`, field_status computation.

- [ ] **Step 3: pytest green + commit**

```bash
pytest tests/test_audio_momentum.py -v
git add tools/audio_momentum.py tests/test_audio_momentum.py
git commit -m "feat(continuity): audio momentum integrity scorer"
```

---

### Task 2: Wire into chain_qa_assist + CLI

**Files:**
- Modify: `tools/chain_qa_assist.py`
- Modify: `tools/cli/sequence_commands.py`
- Modify: `tests/test_chain_qa_assist.py`
- Modify: `tests/test_cli_smoke.py`

- [ ] **Step 1: Assist tests**

```python
def test_assist_includes_audio_momentum_evidence() -> None:
    prev = create_clip()
    prev["index"] = 0
    prev["audio_momentum_vector"]["dialogue_state"] = "Hello—"
    prev["audio_momentum_vector"]["sfx_timing"] = "rain"
    clip = create_clip(prompt="Continue", last_frame_recap="Same room")
    clip["index"] = 1
    clip["audio_momentum_vector"]["dialogue_state"] = ""  # drop
    assist = assist_sfw_chain_qa(clip, previous_clip=prev)
    assert "audio_momentum" in assist["evidence"]
    assert assist["suggested_scores"]["audio_momentum_sync"] == (
        assist["evidence"]["audio_momentum"]["suggested_audio_momentum_sync"]
    )
```

- [ ] **Step 2: In `assist_sfw_chain_qa`**

After drift/seam block (or after AMV ratio block):

```python
from audio_momentum import build_audio_momentum_report

amv_report = build_audio_momentum_report(
    clip,
    previous_clip=previous_clip,
    memory_bank=(sequence or {}).get("memory_bank"),
)
scores["audio_momentum_sync"] = amv_report["suggested_audio_momentum_sync"]
reasons["audio_momentum_sync"] = (
    f"integrity={amv_report['integrity_score']}; "
    + "; ".join(amv_report["factors"][:2])
)[:200]
# evidence:
"evidence": {
    "identity_drift": drift,
    "seam_report": seam,
    "audio_momentum": amv_report,
}
```

NSFW path: attach `audio_momentum` to evidence only (like drift), do not change NSFW score keys.

`apply_assisted_qa`: `clip["audio_momentum_report"] = evidence audio_momentum`

- [ ] **Step 3: CLI `amv-check`**

```python
@app.command("amv-check")
def seq_amv_check(
    name: str = typer.Argument(...),
    clip: str = typer.Option(..., "--clip", "-c"),
):
    """Audio momentum integrity across stitch (roadmap #6)."""
    # build report, store on clip, save, print score/pass/factors/fixes/field_status
```

- [ ] **Step 4: Smoke**

```python
def test_sequence_amv_check_registered():
    result = run_cli("sequence", "--help")
    assert "amv-check" in result.stdout
```

- [ ] **Step 5: pytest + commit**

```bash
pytest tests/test_audio_momentum.py tests/test_chain_qa_assist.py tests/test_cli_smoke.py -v
git add tools/audio_momentum.py tools/chain_qa_assist.py tools/cli/sequence_commands.py tests/
git commit -m "feat(continuity): wire AMV integrity into assist and CLI"
```

---

### Task 3: Docs + full regression

- [ ] **CHANGELOG** under Unreleased Added:

```markdown
- **Audio momentum integrity (roadmap #6)** — `tools/audio_momentum.py` diffs AMV across stitches (dialogue/SFX/music/lip-sync); Chain QA Assist uses evidence for `audio_momentum_sync`; CLI `sequence amv-check`
```

- [ ] **Optional:** one line in sonic-architect skill or chain-qa-protocol

- [ ] **Regression:**

```bash
pytest tests/test_audio_momentum.py tests/test_extend_regen.py tests/test_sequence_memory.py tests/test_sequence_chain_memory.py tests/test_identity_drift.py tests/test_seam_report.py tests/test_chain_qa_assist.py tests/test_cli_smoke.py tests/test_handoff_validator.py -v
```

- [ ] **Commit:** `docs: changelog for audio momentum integrity`

---

## Spec coverage

| Spec #6 | Task |
|---------|------|
| Diff/validate AMV across stitch | Task 1 |
| Dropped dialogue / SFX / music | Task 1 rules |
| Tool + CLI | Task 1–2 |
| Feed chain QA | Task 2 assist overlay |

## Hooks for #7

Emotional temperature is separate; do not mix into AMV scorer.

---

## Execution handoff

**Two execution options:**

1. **Subagent-Driven (recommended)**
2. **Inline Execution**

Which approach?
