# Long-Form Continuity Evidence Loop (#1–#3) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship measurable identity-drift scoring, last-frame seam reports, and Chain QA Assist v2 so extend/stitch Go/No-Go decisions use evidence instead of recap-length heuristics alone.

**Architecture:** Two pure library modules (`tools/identity_drift.py`, `tools/seam_report.py`) compute structured reports from clip/DNA/optional still paths. `tools/chain_qa_assist.py` consumes those reports to adjust the existing 10-point SFW scores and attach an `evidence` block. CLI commands under `sequence` expose drift/seam and enrich `qa-assist`. No vision API required for v1 (metadata + optional PIL frame compare); optional Pillow is soft-imported.

**Tech Stack:** Python 3.11+, existing `tools/` path layout, Typer/Rich CLI, pytest (tests insert `tools/` on `sys.path` like other suite tests). Optional: Pillow for histogram/size compare when stills exist.

**Design:** [docs/superpowers/specs/2026-07-09-long-form-continuity-roadmap-design.md](../specs/2026-07-09-long-form-continuity-roadmap-design.md)

**Studio:** v3.6.7 → work targets Unreleased / next minor (no version bump required unless release process demands it)

---

## Principles (non-negotiable)

1. **Evidence-first, not agent-first** — tools return JSON-serializable dicts; Role Cards only *consume* later.
2. **No hard dependency on cv2/ffmpeg** — frame compare uses optional PIL; missing frames → metadata-only path with explicit `mode: "metadata" | "frame" | "hybrid"`.
3. **Stable chain QA keys** — keep the 10 SFW check IDs in `sequence_chain.CHAIN_QA_CHECKS`; only change *how* assist fills scores + add `evidence`.
4. **Drift scale matches Identity Lock language** — raw `drift_score` is 0.0–10.0 where **higher = more drift**; pass when `drift_score < threshold` (default **2.5**, same as DNA inject text / lock state).
5. **TDD** — failing test → minimal impl → pass → commit per task.
6. **YAGNI** — no Sequence Memory Bank (#4), no re-gen loop (#5), no new Role Cards, no Web UI, no NSFW fork of scorers (NSFW assist can *read* drift/seam evidence later without duplicating modules).

## Out of scope (do not implement in this plan)

- Items #4–#12 from the roadmap
- Vision-model / multimodal API scoring
- New plugin skill directory for every tool (optional one-line notes in `chain-qa-protocol` / `identity-lock-specialist` only if time; not blocking)
- Schema bump of `sequence.json` `schema_version` (store reports on clip under `identity_drift` / `seam_report` keys — additive)
- Catalog pin / marketplace version bump (only if skill text changes are committed; pin is a separate release step)

---

## File map

| Path | Responsibility |
|------|----------------|
| `tools/identity_drift.py` | Score identity drift from DNA + clip (+ optional previous clip / ref stills) |
| `tools/seam_report.py` | Seam risk from recap/momentum continuity + optional last/first frame stills |
| `tools/chain_qa_assist.py` | Assist v2: call drift + seam; blend into scores; attach `evidence` |
| `tools/cli/sequence_commands.py` | CLI: `sequence drift-score`, `sequence seam-report`; enrich `qa-assist` output |
| `tests/test_identity_drift.py` | Unit tests for drift scorer |
| `tests/test_seam_report.py` | Unit tests for seam report |
| `tests/test_chain_qa_assist.py` | Extend with evidence-loop / blending tests |
| `tests/fixtures/continuity/` (optional) | Tiny synthetic PNGs for frame compare (created in Task 2 if needed) |

**Import pattern (all tools modules):** tests use:

```python
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
```

CLI already runs with `tools/` on path via `cinematic_studio_cli`.

---

### Task 1: Identity Drift Scorer — core API + tests

**Files:**
- Create: `tools/identity_drift.py`
- Create: `tests/test_identity_drift.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_identity_drift.py`:

```python
"""Tests for identity drift scorer (roadmap #1)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from identity_drift import (  # noqa: E402
    DEFAULT_DRIFT_THRESHOLD,
    score_identity_drift,
)
from sequence_chain import create_clip  # noqa: E402


def _dna(**overrides):
    base = {
        "character_name": "Liora",
        "slug": "liora",
        "core_identity": "East Asian woman, mid-20s, sharp jaw",
        "facial_dna": "almond eyes, high cheekbones, small scar left brow",
        "hair_grooming": "black bob, straight",
        "clothing_style": "long charcoal coat",
        "key_consistency_anchors": ["scar left brow", "charcoal coat", "black bob"],
        "reference_image_ids": ["ref_liora_a1"],
        "identity_lock_status": "locked",
    }
    base.update(overrides)
    return base


def test_default_threshold_is_2_5() -> None:
    assert DEFAULT_DRIFT_THRESHOLD == 2.5


def test_strong_lock_low_drift() -> None:
    dna = _dna()
    clip = create_clip(
        prompt="Liora in charcoal coat, black bob, scar left brow, rain alley",
        reference_image_id="ref_liora_a1",
        last_frame_recap="Coat collar up, bob wet, scar visible, same face",
    )
    clip["momentum_vector"]["emotional_state"] = "tense"
    report = score_identity_drift(clip, dna=dna)
    assert report["drift_score"] < DEFAULT_DRIFT_THRESHOLD
    assert report["pass"] is True
    assert report["mode"] in ("metadata", "hybrid", "frame")
    assert "factors" in report
    assert report["threshold"] == DEFAULT_DRIFT_THRESHOLD


def test_missing_dna_and_thin_prompt_high_drift() -> None:
    clip = create_clip(prompt="person walks", reference_image_id="")
    report = score_identity_drift(clip, dna=None)
    assert report["drift_score"] >= DEFAULT_DRIFT_THRESHOLD
    assert report["pass"] is False
    assert any("dna" in f.lower() or "prompt" in f.lower() for f in report["factors"])


def test_ref_id_mismatch_increases_drift() -> None:
    dna = _dna()
    good = create_clip(
        prompt="Liora charcoal coat black bob scar left brow",
        reference_image_id="ref_liora_a1",
    )
    bad = create_clip(
        prompt="Liora charcoal coat black bob scar left brow",
        reference_image_id="ref_someone_else",
    )
    r_good = score_identity_drift(good, dna=dna)
    r_bad = score_identity_drift(bad, dna=dna)
    assert r_bad["drift_score"] > r_good["drift_score"]


def test_previous_clip_ref_propagation() -> None:
    dna = _dna()
    prev = create_clip(reference_image_id="ref_liora_a1", prompt="Liora coat bob scar")
    prev["index"] = 0
    curr = create_clip(reference_image_id="ref_liora_a1", prompt="Liora coat bob scar continue")
    curr["index"] = 1
    report = score_identity_drift(curr, dna=dna, previous_clip=prev)
    assert report["pass"] is True
    assert "reference" in " ".join(report["factors"]).lower() or report["drift_score"] < 2.5
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/kali/Grok-Imagine-Cinematic-Studio
pytest tests/test_identity_drift.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'identity_drift'` (or import error).

- [ ] **Step 3: Implement `tools/identity_drift.py`**

```python
#!/usr/bin/env python3
"""
Identity drift scorer for long-form extend/stitch (roadmap #1).

Returns a structured report. Higher drift_score = more drift (0–10).
Pass when drift_score < threshold (default 2.5, Identity Lock convention).
v1: metadata heuristics; optional still paths reserved for hybrid/frame mode.
"""

from __future__ import annotations

import re
from typing import Any

DEFAULT_DRIFT_THRESHOLD = 2.5

_TOKEN_RE = re.compile(r"[a-z0-9']+")


def _tokens(text: str) -> set[str]:
    return {t for t in _TOKEN_RE.findall((text or "").lower()) if len(t) > 2}


def _clamp(score: float, lo: float = 0.0, hi: float = 10.0) -> float:
    return round(max(lo, min(hi, score)), 2)


def _dna_corpus(dna: dict[str, Any]) -> str:
    parts = [
        dna.get("core_identity", ""),
        dna.get("facial_dna", ""),
        dna.get("hair_grooming", ""),
        dna.get("clothing_style", ""),
        dna.get("movement_posture", ""),
        " ".join(dna.get("key_consistency_anchors") or []),
    ]
    return " ".join(str(p) for p in parts if p)


def score_identity_drift(
    clip: dict[str, Any],
    *,
    dna: dict[str, Any] | None = None,
    previous_clip: dict[str, Any] | None = None,
    threshold: float = DEFAULT_DRIFT_THRESHOLD,
    reference_still_path: str | None = None,
    clip_still_path: str | None = None,
) -> dict[str, Any]:
    """
    Score identity drift for a clip against Character DNA and chain context.

    Optional still paths are accepted for future/hybrid use; v1 metadata path
    ignores pixel compare if PIL unavailable or paths missing.
    """
    factors: list[str] = []
    penalties: list[float] = []

    prompt = (clip.get("prompt") or "").strip()
    recap = (clip.get("last_frame_recap") or "").strip()
    ref_id = (clip.get("reference_image_id") or "").strip()
    clip_text = f"{prompt} {recap}"
    clip_toks = _tokens(clip_text)

    if not dna:
        penalties.append(4.0)
        factors.append("No DNA profile — high identity risk")
    else:
        if dna.get("identity_lock_status") != "locked":
            penalties.append(1.0)
            factors.append(f"identity_lock_status={dna.get('identity_lock_status', 'pending')}")

        corpus = _dna_corpus(dna)
        dna_toks = _tokens(corpus)
        anchors = [str(a).lower() for a in (dna.get("key_consistency_anchors") or []) if str(a).strip()]

        if not dna_toks:
            penalties.append(2.5)
            factors.append("DNA fields empty")
        elif not clip_toks:
            penalties.append(3.0)
            factors.append("Clip prompt/recap empty — cannot verify identity")
        else:
            overlap = len(dna_toks & clip_toks) / max(1, len(dna_toks))
            # Low lexical overlap → more drift
            lex_penalty = _clamp((1.0 - overlap) * 5.0, 0.0, 5.0)
            penalties.append(lex_penalty)
            factors.append(f"DNA token overlap={overlap:.0%} (lex_penalty={lex_penalty})")

            if anchors:
                hit = sum(1 for a in anchors if a in clip_text.lower() or any(
                    t in clip_toks for t in _tokens(a)
                ))
                miss = len(anchors) - hit
                if miss:
                    ap = min(3.0, miss * 1.0)
                    penalties.append(ap)
                    factors.append(f"Anchors missed={miss}/{len(anchors)}")
                else:
                    factors.append(f"All {len(anchors)} anchors present in prompt/recap")

        dna_refs = [str(r) for r in (dna.get("reference_image_ids") or []) if r]
        if dna_refs:
            if not ref_id:
                penalties.append(1.5)
                factors.append("DNA has reference_image_ids but clip has no reference_image_id")
            elif ref_id not in dna_refs:
                penalties.append(2.0)
                factors.append(f"reference_image_id={ref_id} not in DNA refs {dna_refs}")
            else:
                factors.append(f"reference_image_id matches DNA ({ref_id})")
        elif ref_id:
            factors.append(f"reference_image_id={ref_id} (no DNA ref list)")

    if previous_clip is not None:
        prev_ref = (previous_clip.get("reference_image_id") or "").strip()
        if prev_ref and ref_id and prev_ref == ref_id:
            # Small credit: reduce total later via negative penalty
            penalties.append(-0.5)
            factors.append("reference_image_id propagated from previous clip")
        elif prev_ref and ref_id and prev_ref != ref_id:
            penalties.append(1.5)
            factors.append(
                f"reference_image_id changed {prev_ref} → {ref_id} (ok if scene change)"
            )
        elif prev_ref and not ref_id:
            penalties.append(1.0)
            factors.append("Previous clip had reference_image_id; current missing")

    # Optional frame path (soft)
    mode = "metadata"
    frame_note = None
    if reference_still_path and clip_still_path:
        frame_score = _optional_still_drift(reference_still_path, clip_still_path)
        if frame_score is not None:
            mode = "hybrid"
            penalties.append(frame_score)
            frame_note = f"still_compare_penalty={frame_score}"
            factors.append(frame_note)

    raw = sum(penalties)
    # Map raw penalties into 0–10 drift; empty strong lock should land ~0–2
    drift_score = _clamp(raw if raw > 0 else 0.0)
    # Floor: completely empty everything
    if not prompt and not recap and not dna:
        drift_score = max(drift_score, 6.0)

    passed = drift_score < threshold
    return {
        "clip_id": clip.get("clip_id"),
        "drift_score": drift_score,
        "threshold": threshold,
        "pass": passed,
        "mode": mode,
        "factors": factors,
        "suggested_character_drift_boundary": _drift_to_qa_score(drift_score),
        "fixes": [] if passed else [
            "Reinforce DNA anchors in prompt",
            "Restore reference_image_id from DNA / previous clip",
            "Re-lock identity before extend",
        ],
    }


def _drift_to_qa_score(drift_score: float) -> float:
    """Map drift 0–10 to chain QA character_drift_boundary 1–10 (higher=better)."""
    # drift 0 → 10, drift 2.5 → ~7.5, drift 5 → 5, drift 10 → 1
    return round(max(1.0, min(10.0, 10.0 - drift_score)), 1)


def _optional_still_drift(ref_path: str, clip_path: str) -> float | None:
    """Return extra drift penalty 0–3 from still compare, or None if unavailable."""
    try:
        from PIL import Image
        import math
    except ImportError:
        return None
    try:
        a = Image.open(ref_path).convert("RGB").resize((64, 64))
        b = Image.open(clip_path).convert("RGB").resize((64, 64))
    except OSError:
        return None
    ha = a.histogram()
    hb = b.histogram()
    # Bhattacharyya-ish distance on histograms
    s = sum(math.sqrt(max(x, 0) * max(y, 0)) for x, y in zip(ha, hb))
    s = s / (64 * 64) if s else 0.0
    # s high = similar; convert to penalty
    similarity = min(1.0, s / 256.0) if s > 1 else s  # normalize roughly
    # Simpler: mean abs pixel diff
    px_a = list(a.getdata())
    px_b = list(b.getdata())
    if not px_a or len(px_a) != len(px_b):
        return None
    mad = sum(abs(pa[i] - pb[i]) for pa, pb in zip(px_a, px_b) for i in range(3)) / (
        len(px_a) * 3 * 255.0
    )
    return round(min(3.0, mad * 6.0), 2)
```

Note: Keep `_optional_still_drift` simple; tests above do not require PIL stills. If histogram math is messy, **prefer mean absolute difference only** and delete unused histogram variables for clarity (YAGNI).

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_identity_drift.py -v
```

Expected: all PASS. Fix any off-by-threshold cases by tuning penalties so `test_strong_lock_low_drift` stays under 2.5 and empty DNA stays ≥ 2.5.

- [ ] **Step 5: Commit**

```bash
git add tools/identity_drift.py tests/test_identity_drift.py
git commit -m "feat(continuity): identity drift scorer for extend chains"
```

---

### Task 2: Last-Frame Seam Report — core API + tests

**Files:**
- Create: `tools/seam_report.py`
- Create: `tests/test_seam_report.py`
- Optional: `tests/fixtures/continuity/last.png`, `first.png` (generate in test via PIL if available, else skip frame tests)

- [ ] **Step 1: Write the failing tests**

Create `tests/test_seam_report.py`:

```python
"""Tests for last-frame seam report (roadmap #2)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from seam_report import build_seam_report  # noqa: E402
from sequence_chain import create_clip  # noqa: E402


def test_opening_clip_low_seam_risk() -> None:
    clip = create_clip(prompt="Wide establishing", last_frame_recap="Skyline dusk")
    clip["index"] = 0
    report = build_seam_report(clip, previous_clip=None)
    assert report["seam_risk"] <= 4.0
    assert report["mode"] == "metadata"
    assert "suggested_scores" in report


def test_extend_missing_prev_recap_high_risk() -> None:
    prev = create_clip(prompt="Prev", last_frame_recap="")
    prev["index"] = 0
    curr = create_clip(prompt="Next", last_frame_recap="something")
    curr["index"] = 1
    report = build_seam_report(curr, previous_clip=prev)
    assert report["seam_risk"] >= 5.0
    assert report["pass"] is False or any("recap" in f.lower() for f in report["factors"])


def test_aligned_momentum_reduces_risk() -> None:
    prev = create_clip(
        prompt="Run",
        last_frame_recap="Hero mid-stride left to right, neon rain, camera tracking",
    )
    prev["index"] = 0
    prev["momentum_vector"] = {
        "last_action": "mid-stride run",
        "emotional_state": "urgent",
        "camera_velocity": "tracking right",
        "lighting_state": "neon rain",
        "physics_state": "weighty forward",
    }
    curr = create_clip(
        prompt="Continue run",
        last_frame_recap="Same alley, still tracking, rain continuous",
    )
    curr["index"] = 1
    curr["momentum_vector"] = {
        "last_action": "continues mid-stride run",
        "emotional_state": "urgent",
        "camera_velocity": "tracking right",
        "lighting_state": "neon rain",
        "physics_state": "weighty forward",
    }
    curr["transition_to_next"] = "invisible_edit"
    report = build_seam_report(curr, previous_clip=prev)
    assert report["seam_risk"] < 5.0
    assert report["suggested_scores"]["last_frame_continuity"] >= 7.0


def test_report_includes_fixes_list() -> None:
    prev = create_clip(last_frame_recap="")
    prev["index"] = 0
    curr = create_clip(prompt="Next beat")
    curr["index"] = 1
    report = build_seam_report(curr, previous_clip=prev)
    assert isinstance(report["fixes"], list)
```


- [ ] **Step 2: Run tests — expect FAIL**

```bash
pytest tests/test_seam_report.py -v
```

Expected: `ModuleNotFoundError: No module named 'seam_report'`.

- [ ] **Step 3: Implement `tools/seam_report.py`**

```python
#!/usr/bin/env python3
"""
Last-frame seam report for extend/stitch (roadmap #2).

seam_risk: 0–10 higher = worse seam.
pass: seam_risk < 5.0 (moderate gate; chain QA still final).
"""

from __future__ import annotations

import re
from typing import Any

_TOKEN_RE = re.compile(r"[a-z0-9']+")
SEAM_PASS_THRESHOLD = 5.0


def _tokens(text: str) -> set[str]:
    return {t for t in _TOKEN_RE.findall((text or "").lower()) if len(t) > 2}


def _clamp(x: float, lo: float = 0.0, hi: float = 10.0) -> float:
    return round(max(lo, min(hi, x)), 2)


def build_seam_report(
    clip: dict[str, Any],
    *,
    previous_clip: dict[str, Any] | None = None,
    previous_last_frame_path: str | None = None,
    current_first_frame_path: str | None = None,
) -> dict[str, Any]:
    factors: list[str] = []
    risk_parts: list[float] = []
    fixes: list[str] = []
    idx = int(clip.get("index") or 0)
    is_extend = idx > 0 or previous_clip is not None

    if not is_extend or previous_clip is None:
        factors.append("Opening clip — no stitch boundary")
        return {
            "clip_id": clip.get("clip_id"),
            "seam_risk": 2.0,
            "pass": True,
            "mode": "metadata",
            "factors": factors,
            "fixes": [],
            "suggested_scores": {
                "last_frame_continuity": 8.5,
                "physics_realism": 8.0,
                "stitch_artifact_risk": 8.5,
                "lighting_color_match": 8.0,
            },
        }

    prev_recap = (previous_clip.get("last_frame_recap") or "").strip()
    curr_recap = (clip.get("last_frame_recap") or "").strip()
    prev_mv = previous_clip.get("momentum_vector") or {}
    curr_mv = clip.get("momentum_vector") or {}

    if not prev_recap:
        risk_parts.append(3.5)
        factors.append("Previous LAST_FRAME_RECAP missing")
        fixes.append("Capture LAST_FRAME_RECAP on previous clip before extend")
    else:
        factors.append(f"Previous recap length={len(prev_recap)}")

    if not curr_recap and is_extend:
        risk_parts.append(1.5)
        factors.append("Current clip recap empty")
        fixes.append("Document expected end state on current clip")

    if prev_recap and curr_recap:
        pt, ct = _tokens(prev_recap), _tokens(curr_recap)
        if pt and ct:
            overlap = len(pt & ct) / max(1, len(pt))
            # Low overlap between prev end and current description → higher risk
            # For current clip, also compare prev_recap to current *prompt* if recap is end-state
            risk_parts.append(_clamp((1.0 - overlap) * 4.0, 0.0, 4.0))
            factors.append(f"Recap token overlap vs previous={overlap:.0%}")
        prompt_toks = _tokens(clip.get("prompt") or "")
        if pt and prompt_toks:
            po = len(pt & prompt_toks) / max(1, len(pt))
            risk_parts.append(_clamp((1.0 - po) * 2.5, 0.0, 2.5))
            factors.append(f"Prompt vs prev recap overlap={po:.0%}")

    keys = ("last_action", "emotional_state", "camera_velocity", "lighting_state", "physics_state")
    filled_prev = sum(1 for k in keys if str(prev_mv.get(k, "")).strip())
    filled_curr = sum(1 for k in keys if str(curr_mv.get(k, "")).strip())
    if filled_prev < 3:
        risk_parts.append(1.5)
        factors.append(f"Previous momentum sparse ({filled_prev}/5)")
        fixes.append("Fill momentum_vector on previous clip")
    if filled_curr < 3:
        risk_parts.append(1.0)
        factors.append(f"Current momentum sparse ({filled_curr}/5)")

    matches = 0
    compared = 0
    for k in keys:
        a, b = str(prev_mv.get(k, "")).strip().lower(), str(curr_mv.get(k, "")).strip().lower()
        if a and b:
            compared += 1
            at, bt = _tokens(a), _tokens(b)
            if at & bt or a in b or b in a:
                matches += 1
    if compared:
        match_ratio = matches / compared
        risk_parts.append(_clamp((1.0 - match_ratio) * 3.0, 0.0, 3.0))
        factors.append(f"Momentum field agreement={match_ratio:.0%} ({matches}/{compared})")
    else:
        risk_parts.append(1.0)
        factors.append("No paired momentum fields to compare")

    transition = clip.get("transition_to_next") or previous_clip.get("transition_to_next") or "invisible_edit"
    if transition == "invisible_edit":
        risk_parts.append(0.8)
        factors.append("invisible_edit — higher morph risk at boundary")
    elif transition in ("dissolve", "hard_cut"):
        risk_parts.append(-0.5)
        factors.append(f"{transition} masks boundary")

    mode = "metadata"
    if previous_last_frame_path and current_first_frame_path:
        fr = _optional_frame_seam(previous_last_frame_path, current_first_frame_path)
        if fr is not None:
            mode = "hybrid"
            risk_parts.append(fr)
            factors.append(f"frame_mad_penalty={fr}")

    seam_risk = _clamp(sum(risk_parts))
    passed = seam_risk < SEAM_PASS_THRESHOLD

    # Map to QA score suggestions (higher = better)
    cont = _clamp(10.0 - seam_risk, 1.0, 10.0)
    stitch = _clamp(10.0 - seam_risk * 0.9, 1.0, 10.0)
    physics = _clamp(9.0 - max(0.0, seam_risk - 2.0) * 0.5, 1.0, 10.0)
    lighting = 8.0 if str(prev_mv.get("lighting_state", "")).strip() and str(
        curr_mv.get("lighting_state", "")
    ).strip() else 6.5

    if not passed and not fixes:
        fixes.append("Strengthen LAST_FRAME_RECAP and momentum carry-over before re-gen")

    return {
        "clip_id": clip.get("clip_id"),
        "previous_clip_id": previous_clip.get("clip_id"),
        "seam_risk": seam_risk,
        "pass": passed,
        "mode": mode,
        "factors": factors,
        "fixes": fixes,
        "suggested_scores": {
            "last_frame_continuity": round(cont, 1),
            "physics_realism": round(physics, 1),
            "stitch_artifact_risk": round(stitch, 1),
            "lighting_color_match": round(lighting, 1),
        },
    }


def _optional_frame_seam(prev_path: str, curr_path: str) -> float | None:
    try:
        from PIL import Image
    except ImportError:
        return None
    try:
        a = Image.open(prev_path).convert("RGB").resize((64, 64))
        b = Image.open(curr_path).convert("RGB").resize((64, 64))
    except OSError:
        return None
    px_a, px_b = list(a.getdata()), list(b.getdata())
    if len(px_a) != len(px_b) or not px_a:
        return None
    mad = sum(abs(pa[i] - pb[i]) for pa, pb in zip(px_a, px_b) for i in range(3)) / (
        len(px_a) * 3 * 255.0
    )
    return round(min(4.0, mad * 8.0), 2)
```

Fix the double `seam_risk` assignment in implementation — use a single `seam_risk = _clamp(sum(risk_parts))` only.

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_seam_report.py -v
```

Expected: PASS. Adjust risk weights if `test_aligned_momentum_reduces_risk` fails.

- [ ] **Step 5: Commit**

```bash
git add tools/seam_report.py tests/test_seam_report.py
git commit -m "feat(continuity): last-frame seam report for stitch boundaries"
```

---

### Task 3: Chain QA Assist v2 — blend evidence into scores

**Files:**
- Modify: `tools/chain_qa_assist.py`
- Modify: `tests/test_chain_qa_assist.py`

- [ ] **Step 1: Write failing tests (append to `tests/test_chain_qa_assist.py`)**

```python
from identity_drift import score_identity_drift  # noqa: E402
from seam_report import build_seam_report  # noqa: E402


def test_assist_v2_includes_evidence_block() -> None:
    dna = {
        "character_name": "Liora",
        "slug": "liora",
        "core_identity": "East Asian woman mid-20s",
        "facial_dna": "almond eyes scar left brow",
        "hair_grooming": "black bob",
        "clothing_style": "charcoal coat",
        "key_consistency_anchors": ["scar left brow", "charcoal coat"],
        "reference_image_ids": ["ref_a1"],
        "identity_lock_status": "locked",
    }
    prev = create_clip(
        prompt="Liora charcoal coat black bob scar left brow walks",
        last_frame_recap="Coat wet, bob dripping, scar visible, tracking shot",
        reference_image_id="ref_a1",
    )
    prev["index"] = 0
    prev["momentum_vector"] = {
        "last_action": "walks forward",
        "emotional_state": "tense",
        "camera_velocity": "track",
        "lighting_state": "neon",
        "physics_state": "weighty",
    }
    clip = create_clip(
        prompt="Liora charcoal coat black bob scar left brow continues",
        last_frame_recap="Same coat and bob, scar visible",
        reference_image_id="ref_a1",
    )
    clip["index"] = 1
    clip["momentum_vector"] = dict(prev["momentum_vector"])
    clip["momentum_vector"]["last_action"] = "continues walking"

    assist = assist_sfw_chain_qa(clip, previous_clip=prev, dna=dna)
    assert "evidence" in assist
    assert "identity_drift" in assist["evidence"]
    assert "seam_report" in assist["evidence"]
    assert assist["evidence"]["identity_drift"]["drift_score"] is not None
    # Drift-aware score should not ignore scorer
    assert assist["suggested_scores"]["character_drift_boundary"] == (
        assist["evidence"]["identity_drift"]["suggested_character_drift_boundary"]
    )


def test_assist_v2_without_dna_still_works() -> None:
    clip = create_clip(prompt="Wide shot of city", last_frame_recap="Skyline")
    assist = assist_sfw_chain_qa(clip)
    assert assist["evidence"]["identity_drift"]["pass"] in (True, False)
    assert "suggested_scores" in assist
```

- [ ] **Step 2: Run new tests — expect FAIL**

```bash
pytest tests/test_chain_qa_assist.py -v
```

Expected: FAIL on missing `dna` kwarg / missing `evidence` key.

- [ ] **Step 3: Update `assist_sfw_chain_qa` and `assist_chain_qa` / `apply_assisted_qa`**

In `tools/chain_qa_assist.py`:

1. Import scorers:

```python
from identity_drift import score_identity_drift
from seam_report import build_seam_report
```

2. Extend signature:

```python
def assist_sfw_chain_qa(
    clip: dict[str, Any],
    *,
    previous_clip: dict[str, Any] | None = None,
    sequence: dict[str, Any] | None = None,
    dna: dict[str, Any] | None = None,
    previous_last_frame_path: str | None = None,
    current_first_frame_path: str | None = None,
    reference_still_path: str | None = None,
    clip_still_path: str | None = None,
) -> AssistResult:
```

3. After existing heuristic scores are computed, **overlay** evidence:

```python
    drift = score_identity_drift(
        clip,
        dna=dna,
        previous_clip=previous_clip,
        reference_still_path=reference_still_path,
        clip_still_path=clip_still_path,
    )
    seam = build_seam_report(
        clip,
        previous_clip=previous_clip,
        previous_last_frame_path=previous_last_frame_path,
        current_first_frame_path=current_first_frame_path,
    )

    # Overlay: prefer evidence-backed values for identity + seam-related checks
    scores["character_drift_boundary"] = drift["suggested_character_drift_boundary"]
    reasons["character_drift_boundary"] = (
        f"drift_score={drift['drift_score']} (threshold={drift['threshold']}); "
        + "; ".join(drift["factors"][:2])
    )

    for key, val in seam.get("suggested_scores", {}).items():
        if key in scores:
            # Blend 50/50 heuristic vs seam suggestion for stability
            blended = round((scores[key] + float(val)) / 2.0, 1)
            scores[key] = _clamp(blended)
            reasons[key] = (
                f"{reasons.get(key, '')}; seam:{seam['factors'][0] if seam['factors'] else 'n/a'}"
            )[:200]

    # If drift failed hard, ensure critical identity stays low enough to matter
    if not drift["pass"]:
        scores["character_drift_boundary"] = min(
            scores["character_drift_boundary"],
            drift["suggested_character_drift_boundary"],
        )

    qa = run_chain_qa(clip, previous_clip=previous_clip, scores=scores)
    if not drift["pass"]:
        qa.setdefault("fixes", []).extend(drift.get("fixes") or [])
    if not seam["pass"]:
        qa.setdefault("fixes", []).extend(seam.get("fixes") or [])

    return {
        "mode": "sfw",
        "clip_id": clip["clip_id"],
        "evaluated_at": _now_iso(),
        "suggested_scores": scores,
        "reasons": reasons,
        "evaluation": qa,
        "confidence": _assist_confidence_v2(scores, reasons, drift, seam),
        "sequence_slug": (sequence or {}).get("slug"),
        "evidence": {
            "identity_drift": drift,
            "seam_report": seam,
        },
    }
```

4. Add confidence helper:

```python
def _assist_confidence_v2(
    scores: dict[str, float],
    reasons: dict[str, str],
    drift: dict[str, Any],
    seam: dict[str, Any],
) -> str:
    base = _assist_confidence(scores, reasons)
    if not drift.get("pass") or not seam.get("pass"):
        return "low"
    if drift.get("mode") == "metadata" and seam.get("mode") == "metadata":
        if base == "high":
            return "medium"  # metadata-only should not claim high certainty
    return base
```

5. Thread `dna` through `assist_chain_qa` and `apply_assisted_qa`:

```python
def assist_chain_qa(
    clip: dict[str, Any],
    *,
    previous_clip: dict[str, Any] | None = None,
    sequence: dict[str, Any] | None = None,
    nsfw: bool = False,
    dna: dict[str, Any] | None = None,
    **evidence_paths: Any,
) -> AssistResult:
    if nsfw or (sequence or {}).get("nsfw_extension"):
        # NSFW path: keep existing heuristics; attach evidence for shared visibility
        result = assist_nsfw_chain_qa(clip, previous_clip=previous_clip, sequence=sequence)
        drift = score_identity_drift(clip, dna=dna, previous_clip=previous_clip)
        seam = build_seam_report(clip, previous_clip=previous_clip)
        result["evidence"] = {"identity_drift": drift, "seam_report": seam}
        return result
    return assist_sfw_chain_qa(
        clip,
        previous_clip=previous_clip,
        sequence=sequence,
        dna=dna,
        **{k: v for k, v in evidence_paths.items() if k in {
            "previous_last_frame_path",
            "current_first_frame_path",
            "reference_still_path",
            "clip_still_path",
        }},
    )


def apply_assisted_qa(
    seq: dict[str, Any],
    clip: dict[str, Any],
    *,
    previous_clip: dict[str, Any] | None = None,
    nsfw: bool = False,
    dna: dict[str, Any] | None = None,
) -> dict[str, Any]:
    assist = assist_chain_qa(
        clip, previous_clip=previous_clip, sequence=seq, nsfw=nsfw, dna=dna
    )
    clip["chain_qa_assist"] = assist
    # existing apply logic...
    # also persist:
    clip["identity_drift"] = assist.get("evidence", {}).get("identity_drift")
    clip["seam_report"] = assist.get("evidence", {}).get("seam_report")
    ...
```

Preserve existing NSFW score logic; only attach `evidence`.

- [ ] **Step 4: Run full assist + drift + seam tests**

```bash
pytest tests/test_identity_drift.py tests/test_seam_report.py tests/test_chain_qa_assist.py -v
```

Expected: all PASS. Existing tests must remain green (`test_assist_prefills_sfw_scores`, `test_apply_assisted_qa_updates_clip`).

- [ ] **Step 5: Commit**

```bash
git add tools/chain_qa_assist.py tests/test_chain_qa_assist.py
git commit -m "feat(continuity): chain QA assist v2 with drift and seam evidence"
```

---

### Task 4: CLI — `sequence drift-score`, `sequence seam-report`, enrich `qa-assist`

**Files:**
- Modify: `tools/cli/sequence_commands.py`
- Modify: `tests/test_cli_smoke.py` (or add assertions if smoke already lists sequence commands)

- [ ] **Step 1: Inspect how DNA is loaded in CLI**

```bash
rg -n "load_dna|character_dna|dna " tools/cli/*.py tools/character_dna.py | head -40
```

Use existing loader if present (e.g. `load_character_dna(slug)` / path under `characters/`). If only file path APIs exist, accept `--dna characters/liora/dna.json`.

- [ ] **Step 2: Write a focused CLI unit test if pattern exists**

Prefer testing pure functions already covered; for CLI, extend smoke test to ensure commands register:

```python
def test_sequence_continuity_commands_registered():
    # whatever pattern test_cli_smoke uses — assert "drift-score" and "seam-report" in help
```

Read `tests/test_cli_smoke.py` and mirror its style exactly.

- [ ] **Step 3: Implement CLI commands in `register()` of `sequence_commands.py`**

Add imports:

```python
from identity_drift import score_identity_drift, DEFAULT_DRIFT_THRESHOLD
from seam_report import build_seam_report
from chain_qa_assist import assist_chain_qa, apply_assisted_qa  # already partially imported
```

Check existing imports at top of `sequence_commands.py` and only add missing ones.

**Command: `drift-score`**

```python
    @app.command("drift-score")
    def seq_drift_score(
        name: str = typer.Argument(..., help="Sequence name or slug"),
        clip: str = typer.Option(..., "--clip", "-c"),
        dna: str = typer.Option(None, "--dna", help="Path to dna.json or character slug"),
        threshold: float = typer.Option(DEFAULT_DRIFT_THRESHOLD, "--threshold"),
    ):
        """Score identity drift for a clip against Character DNA (evidence loop #1)."""
        seq = require_sequence(name)
        target = require_clip(seq, clip)
        clips = seq.get("clips", [])
        idx = target["index"]
        prev = clips[idx - 1] if idx > 0 else None
        dna_obj = _load_dna_optional(dna)
        report = score_identity_drift(
            target, dna=dna_obj, previous_clip=prev, threshold=threshold
        )
        target["identity_drift"] = report
        save_sequence(seq)  # only if we want persistence; prefer save always for audit
        color = "green" if report["pass"] else "red"
        console.print(
            f"[{color}]drift_score={report['drift_score']} "
            f"(threshold={report['threshold']}) pass={report['pass']}[/{color}]"
        )
        for f in report["factors"]:
            console.print(f"  • {f}")
        if report["fixes"]:
            console.print("[yellow]Fixes:[/yellow]")
            for fix in report["fixes"]:
                console.print(f"  → {fix}")
```

**Command: `seam-report`**

```python
    @app.command("seam-report")
    def seq_seam_report(
        name: str = typer.Argument(...),
        clip: str = typer.Option(..., "--clip", "-c"),
        prev_frame: str = typer.Option(None, "--prev-frame", help="Path to previous last-frame still"),
        curr_frame: str = typer.Option(None, "--curr-frame", help="Path to current first-frame still"),
    ):
        """Last-frame seam risk report (evidence loop #2)."""
        seq = require_sequence(name)
        target = require_clip(seq, clip)
        clips = seq.get("clips", [])
        idx = target["index"]
        prev = clips[idx - 1] if idx > 0 else None
        report = build_seam_report(
            target,
            previous_clip=prev,
            previous_last_frame_path=prev_frame,
            current_first_frame_path=curr_frame,
        )
        target["seam_report"] = report
        save_sequence(seq)
        color = "green" if report["pass"] else "yellow"
        console.print(
            f"[{color}]seam_risk={report['seam_risk']} pass={report['pass']} "
            f"mode={report['mode']}[/{color}]"
        )
        for f in report["factors"]:
            console.print(f"  • {f}")
```

**Helper `_load_dna_optional`:** implement at bottom of `sequence_commands.py` or in `cli/helpers.py`:

```python
def _load_dna_optional(dna: str | None) -> dict | None:
    if not dna:
        return None
    from pathlib import Path
    import json
    p = Path(dna)
    if p.is_file():
        return json.loads(p.read_text(encoding="utf-8"))
    # try characters/<slug>/dna.json
    from studio_paths import ROOT  # or characters dir constant
    cand = Path("characters") / dna / "dna.json"
    if cand.is_file():
        return json.loads(cand.read_text(encoding="utf-8"))
    console.print(f"[yellow]DNA not found: {dna} — scoring without DNA[/yellow]")
    return None
```

Use the repo’s real characters path (`studio_paths` / project root) — read `tools/studio_paths.py` and match conventions.

**Enrich `qa-assist`:** add options:

```python
        dna: str = typer.Option(None, "--dna", help="DNA path or character slug"),
        prev_frame: str = typer.Option(None, "--prev-frame"),
        curr_frame: str = typer.Option(None, "--curr-frame"),
```

Pass into `assist_chain_qa` / `apply_assisted_qa`. After table of scores, print evidence summary:

```python
        ev = assist.get("evidence") or {}
        if ev.get("identity_drift"):
            d = ev["identity_drift"]
            console.print(
                f"[dim]Evidence drift_score={d.get('drift_score')} "
                f"seam_risk={ev.get('seam_report', {}).get('seam_risk')}[/dim]"
            )
```

- [ ] **Step 4: Manual smoke**

```bash
python tools/cinematic_studio_cli.py sequence --help
# expect drift-score, seam-report, qa-assist

# if a sequence exists:
python tools/cinematic_studio_cli.py sequence drift-score "cli-test" --clip clip_001 --dna characters/liora/dna.json
python tools/cinematic_studio_cli.py sequence seam-report "cli-test" --clip clip_001
python tools/cinematic_studio_cli.py sequence qa-assist "cli-test" --clip clip_001 --dna characters/liora/dna.json
```

If `cli-test` missing, `sequence init` + `add-clip` first (see Quick Start).

- [ ] **Step 5: Run automated tests**

```bash
pytest tests/test_identity_drift.py tests/test_seam_report.py tests/test_chain_qa_assist.py tests/test_cli_smoke.py -v
```

- [ ] **Step 6: Commit**

```bash
git add tools/cli/sequence_commands.py tests/test_cli_smoke.py
git commit -m "feat(cli): sequence drift-score and seam-report commands"
```

---

### Task 5: Docs touch + verification

**Files:**
- Modify: `CHANGELOG.md` under `[Unreleased] → Added`
- Optional one-liner: `.grok/skills/chain-qa-protocol/SKILL.md` or `identity-lock-specialist/SKILL.md` (CLI command names only — keep short)

- [ ] **Step 1: CHANGELOG entry**

```markdown
### Added
- **Long-form continuity evidence loop (v1)** — `tools/identity_drift.py`, `tools/seam_report.py`; Chain QA Assist v2 blends drift + seam into SFW scores with `evidence` block; CLI `sequence drift-score`, `sequence seam-report`, and `qa-assist --dna`
```

- [ ] **Step 2: Full regression on related tests**

```bash
pytest tests/test_identity_drift.py tests/test_seam_report.py tests/test_chain_qa_assist.py tests/test_cli_smoke.py tests/test_handoff_validator.py -v
```

Expected: all PASS.

- [ ] **Step 3: Commit docs**

```bash
git add CHANGELOG.md .grok/skills/chain-qa-protocol/SKILL.md  # only if edited
git commit -m "docs: changelog for continuity evidence loop v1"
```

---

## Spec coverage checklist (self-review)

| Spec item (#1–#3) | Task |
|-------------------|------|
| Identity Drift Scorer tool | Task 1 |
| Last-Frame Seam Report tool | Task 2 |
| Chain QA Assist v2 uses both | Task 3 |
| CLI exposure | Task 4 |
| Metadata-first / optional frame | Tasks 1–2 (`mode`, optional paths) |
| Threshold 2.5 Identity Lock | Task 1 `DEFAULT_DRIFT_THRESHOLD` |
| No #4–#12 scope creep | Principles / out of scope |
| Stable 10-pt check IDs | Task 3 overlay only |

## Placeholder / consistency scan

- Function names locked: `score_identity_drift`, `build_seam_report`, `assist_sfw_chain_qa(..., dna=...)`.
- Report keys locked: `drift_score`, `pass`, `threshold`, `factors`, `fixes`, `mode`, `suggested_character_drift_boundary`; seam: `seam_risk`, `suggested_scores`.
- Clip persistence keys: `identity_drift`, `seam_report`, `chain_qa_assist.evidence`.

## Suggested first epic done when

1. All new tests green.  
2. `sequence qa-assist` prints evidence drift + seam.  
3. A weak DNA/prompt pair can force `character_drift_boundary` down and influence Go/No-Go.  
4. CHANGELOG Unreleased lists the feature.

---

## Execution handoff

Plan complete and saved to `docs/superpowers/plans/2026-07-09-long-form-continuity-evidence-loop.md`.

**Two execution options:**

1. **Subagent-Driven (recommended)** — fresh subagent per task, review between tasks  
2. **Inline Execution** — execute tasks in this session with executing-plans checkpoints  

Which approach?
