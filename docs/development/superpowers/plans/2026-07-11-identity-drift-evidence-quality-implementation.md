# Identity Drift Evidence Quality Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make identity drift scores more trustworthy via soft-PIL multi-signal still compare, still path resolve (flags + clip fields), modest facial DNA metadata weighting, and CLI wiring — threshold 2.5 unchanged.

**Architecture:** In-place upgrade of `tools/identity_drift.py`: add `resolve_still_paths` and `compare_stills_soft`; enhance `score_identity_drift` report with `still_signals` / `still_paths`; wire `sequence drift-score --ref-still` / `--clip-still`. Metadata path remains default when stills unavailable.

**Tech Stack:** Python 3.11+, optional Pillow (soft import), Typer CLI, pytest. No new hard deps.

**Design:** [docs/development/superpowers/specs/2026-07-11-identity-drift-evidence-quality-design.md](../specs/2026-07-11-identity-drift-evidence-quality-design.md)

---

## Principles

1. **Soft PIL only** — never crash if Pillow missing.  
2. **Backward compatible** — existing metadata tests stay green.  
3. **Still penalty max 3.0** — same cap as today.  
4. **TDD** for resolve + still compare + score report fields.

## Out of scope

- Face ML, vision API, artifact directory guessing  
- Changing strict-identity fail matrix  

---

## File map

| Path | Action |
|------|--------|
| `tools/identity_drift.py` | resolve, compare_stills_soft, metadata facial, report fields |
| `tools/cli/sequence_commands.py` | drift-score still flags |
| `tests/test_identity_still_compare.py` | **Create** resolve + hybrid tests |
| `tests/test_identity_drift.py` | Keep green; optional facial factor test |
| `references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md` | Hybrid note |
| `CHANGELOG.md` | Unreleased |

---

### Task 1: `resolve_still_paths` + `compare_stills_soft`

**Files:**
- Modify: `tools/identity_drift.py`
- Create: `tests/test_identity_still_compare.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_identity_still_compare.py`:

```python
"""Still path resolve + hybrid still compare (evidence quality)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from identity_drift import (  # noqa: E402
    compare_stills_soft,
    resolve_still_paths,
    score_identity_drift,
)
from sequence_chain import create_clip  # noqa: E402

PIL = pytest.importorskip("PIL.Image", reason="Pillow optional for hybrid tests")


def _write_solid_png(path: Path, rgb: tuple[int, int, int], size: int = 32) -> None:
    from PIL import Image

    Image.new("RGB", (size, size), rgb).save(path)


def test_resolve_flags_override_clip_fields(tmp_path: Path) -> None:
    ref_flag = tmp_path / "flag_ref.png"
    clip_flag = tmp_path / "flag_clip.png"
    ref_clip = tmp_path / "clip_ref.png"
    clip_clip = tmp_path / "clip_clip.png"
    for p, c in [
        (ref_flag, (10, 10, 10)),
        (clip_flag, (20, 20, 20)),
        (ref_clip, (30, 30, 30)),
        (clip_clip, (40, 40, 40)),
    ]:
        _write_solid_png(p, c)
    clip = create_clip(prompt="x")
    clip["reference_still_path"] = str(ref_clip)
    clip["last_frame_path"] = str(clip_clip)
    r, c = resolve_still_paths(
        clip, ref_still=str(ref_flag), clip_still=str(clip_flag)
    )
    assert r == str(ref_flag)
    assert c == str(clip_flag)


def test_resolve_clip_fields_when_no_flags(tmp_path: Path) -> None:
    ref = tmp_path / "hero.png"
    cur = tmp_path / "last.png"
    _write_solid_png(ref, (1, 2, 3))
    _write_solid_png(cur, (4, 5, 6))
    clip = create_clip(prompt="x")
    clip["hero_plate_path"] = str(ref)
    clip["last_frame_path"] = str(cur)
    r, c = resolve_still_paths(clip)
    assert r == str(ref)
    assert c == str(cur)


def test_resolve_missing_file_returns_none(tmp_path: Path) -> None:
    clip = create_clip(prompt="x")
    clip["reference_still_path"] = str(tmp_path / "nope.png")
    r, c = resolve_still_paths(clip)
    assert r is None
    assert c is None


def test_compare_identical_stills_low_penalty(tmp_path: Path) -> None:
    a = tmp_path / "a.png"
    b = tmp_path / "b.png"
    _write_solid_png(a, (100, 120, 140))
    _write_solid_png(b, (100, 120, 140))
    result = compare_stills_soft(str(a), str(b))
    assert result is not None
    penalty, signals = result
    assert 0.0 <= penalty <= 0.5
    assert signals["size"] == 128
    assert "luma_mae" in signals


def test_compare_different_stills_higher_penalty(tmp_path: Path) -> None:
    a = tmp_path / "a.png"
    b = tmp_path / "b.png"
    _write_solid_png(a, (0, 0, 0))
    _write_solid_png(b, (255, 255, 255))
    result = compare_stills_soft(str(a), str(b))
    assert result is not None
    penalty_same, _ = compare_stills_soft(str(a), str(a))  # type: ignore
    penalty_diff, signals = result
    assert penalty_diff > penalty_same
    assert penalty_diff <= 3.0
    assert signals["hist_l1"] >= 0


def test_score_hybrid_mode_with_stills(tmp_path: Path) -> None:
    ref = tmp_path / "ref.png"
    cur = tmp_path / "cur.png"
    _write_solid_png(ref, (50, 50, 50))
    _write_solid_png(cur, (50, 50, 50))
    clip = create_clip(
        prompt="Liora charcoal coat black bob scar left brow",
        reference_image_id="ref_liora_a1",
        last_frame_recap="same face coat bob scar",
    )
    dna = {
        "character_name": "Liora",
        "slug": "liora",
        "core_identity": "East Asian woman mid-20s",
        "facial_dna": "almond eyes high cheekbones scar left brow",
        "hair_grooming": "black bob",
        "clothing_style": "charcoal coat",
        "key_consistency_anchors": ["scar left brow", "charcoal coat", "black bob"],
        "reference_image_ids": ["ref_liora_a1"],
        "identity_lock_status": "locked",
    }
    report = score_identity_drift(
        clip,
        dna=dna,
        reference_still_path=str(ref),
        clip_still_path=str(cur),
    )
    assert report["mode"] == "hybrid"
    assert report["still_signals"] is not None
    assert report["still_paths"]["ref"] == str(ref)
    assert report["still_paths"]["clip"] == str(cur)
```

- [ ] **Step 2: Run tests — expect FAIL (import/missing functions)**

```bash
pytest tests/test_identity_still_compare.py -v
```

- [ ] **Step 3: Implement in `tools/identity_drift.py`**

Add near top after constants (or before scorer):

```python
REF_STILL_KEYS = (
    "reference_still_path",
    "hero_plate_path",
    "ref_still_path",
)
CLIP_STILL_KEYS = (
    "clip_still_path",
    "last_frame_path",
    "first_frame_path",
    "still_path",
)


def _existing_path(value: str | None) -> str | None:
    if not value or not str(value).strip():
        return None
    p = Path(str(value).strip())
    if p.is_file():
        return str(p)
    return None


def resolve_still_paths(
    clip: dict[str, Any],
    *,
    ref_still: str | None = None,
    clip_still: str | None = None,
) -> tuple[str | None, str | None]:
    """Resolve reference and clip still paths. Flags override clip fields."""
    from pathlib import Path  # if not already imported at module level

    ref = _existing_path(ref_still)
    if ref is None:
        for key in REF_STILL_KEYS:
            ref = _existing_path(clip.get(key) if isinstance(clip.get(key), str) else None)
            if ref:
                break
    cur = _existing_path(clip_still)
    if cur is None:
        for key in CLIP_STILL_KEYS:
            cur = _existing_path(clip.get(key) if isinstance(clip.get(key), str) else None)
            if cur:
                break
    return ref, cur


def compare_stills_soft(
    ref_path: str, clip_path: str
) -> tuple[float, dict[str, Any]] | None:
    """
    Multi-signal still compare. Returns (penalty 0–3, signals) or None.
    Soft-depends on Pillow.
    """
    try:
        from PIL import Image
    except ImportError:
        return None
    try:
        a = Image.open(ref_path).convert("RGB").resize((128, 128))
        b = Image.open(clip_path).convert("RGB").resize((128, 128))
    except OSError:
        return None

    px_a = list(a.getdata())
    px_b = list(b.getdata())
    n = len(px_a)
    if not n or n != len(px_b):
        return None

    # Luma MAE normalized 0–1 → contrib 0–1.5
    def _luma(rgb: tuple[int, ...]) -> float:
        r, g, b = rgb[0], rgb[1], rgb[2]
        return 0.299 * r + 0.587 * g + 0.114 * b

    luma_mae = sum(abs(_luma(pa) - _luma(pb)) for pa, pb in zip(px_a, px_b)) / (
        n * 255.0
    )
    luma_contrib = min(1.5, luma_mae * 3.0)

    # Histogram L1 per channel (32 bins), mean over channels → 0–1.0
    def _hist(channel_vals: list[int]) -> list[int]:
        bins = [0] * 32
        for v in channel_vals:
            bins[min(31, v * 32 // 256)] += 1
        return bins

    hist_l1_sum = 0.0
    for ch in range(3):
        ha = _hist([p[ch] for p in px_a])
        hb = _hist([p[ch] for p in px_b])
        hist_l1_sum += sum(abs(x - y) for x, y in zip(ha, hb)) / (2.0 * n)
    hist_l1 = hist_l1_sum / 3.0
    hist_contrib = min(1.0, hist_l1 * 2.0)

    # Edge energy: mean abs horizontal neighbor delta on luma
    def _edge_energy(px: list) -> float:
        w = 128
        total = 0.0
        count = 0
        for y in range(128):
            for x in range(127):
                i = y * w + x
                total += abs(_luma(px[i]) - _luma(px[i + 1]))
                count += 1
        return total / max(1, count) / 255.0

    ea, eb = _edge_energy(px_a), _edge_energy(px_b)
    edge_delta = abs(ea - eb)
    edge_contrib = min(0.5, edge_delta * 2.0)

    penalty = round(min(3.0, luma_contrib + hist_contrib + edge_contrib), 2)
    signals = {
        "luma_mae": round(luma_mae, 4),
        "hist_l1": round(hist_l1, 4),
        "edge_delta": round(edge_delta, 4),
        "size": 128,
        "penalty": penalty,
    }
    return penalty, signals
```

Add at module top if missing: `from pathlib import Path`.

Replace hybrid block in `score_identity_drift` and retire old `_optional_still_drift` (or make it call `compare_stills_soft` and return only penalty for back-compat).

Update hybrid section of `score_identity_drift`:

```python
    mode = "metadata"
    still_signals = None
    still_paths = {"ref": reference_still_path, "clip": clip_still_path}

    if reference_still_path and clip_still_path:
        compared = compare_stills_soft(reference_still_path, clip_still_path)
        if compared is not None:
            frame_score, still_signals = compared
            mode = "hybrid"
            penalties.append(frame_score)
            factors.append(f"still_compare_penalty={frame_score}")
```

Return dict additions:

```python
        "still_signals": still_signals,
        "still_paths": {
            "ref": reference_still_path,
            "clip": clip_still_path,
        },
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_identity_still_compare.py tests/test_identity_drift.py -q
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tools/identity_drift.py tests/test_identity_still_compare.py
git commit -m "feat(identity): hybrid still compare v2 and path resolve"
```

---

### Task 2: Facial DNA metadata weight + evidence flags

**Files:**
- Modify: `tools/identity_drift.py` (`score_identity_drift` DNA branch, `report_to_drift_evidence`)
- Modify: `tests/test_identity_drift.py` (add one facial-miss test if safe)

- [ ] **Step 1: After global DNA token overlap block, add facial check**

Inside the `else` branch when `dna` is present and `dna_toks` / `clip_toks` exist, after the global overlap factor:

```python
        facial = (dna.get("facial_dna") or "").strip()
        if facial and clip_toks:
            facial_toks = _tokens(facial)
            if facial_toks:
                f_overlap = len(facial_toks & clip_toks) / max(1, len(facial_toks))
                # If facial recall much worse than overall, add up to +1.0
                if f_overlap + 0.15 < overlap:
                    fp = _clamp((1.0 - f_overlap) * 1.5, 0.0, 1.0)
                    penalties.append(fp)
                    factors.append(
                        f"facial_dna overlap={f_overlap:.0%} (penalty={fp})"
                    )
```

Note: `overlap` must be defined in that branch (it already is for the global path). If DNA empty tokens path skips, skip facial too.

- [ ] **Step 2: `report_to_drift_evidence` — if report has mode hybrid, flags**

In `report_to_drift_evidence`, after building factors list:

```python
    flags = factors[:8]
    if report.get("mode") == "hybrid":
        if "hybrid_still" not in flags:
            flags = ["hybrid_still"] + flags
    # also allow report factors already present
```

Use `flags` in `signals.flags`.

- [ ] **Step 3: Test facial miss increases score (optional careful)**

```python
def test_facial_dna_miss_increases_drift() -> None:
    dna = _dna(facial_dna="unique violet heterochromia freckle constellation")
    good = create_clip(
        prompt="Liora charcoal coat black bob scar left brow violet heterochromia freckle constellation",
        reference_image_id="ref_liora_a1",
        last_frame_recap="scar coat bob violet eyes freckle",
    )
    bad = create_clip(
        prompt="Liora charcoal coat black bob scar left brow",
        reference_image_id="ref_liora_a1",
        last_frame_recap="coat bob scar",
    )
    r_good = score_identity_drift(good, dna=dna)
    r_bad = score_identity_drift(bad, dna=dna)
    assert r_bad["drift_score"] >= r_good["drift_score"]
```

- [ ] **Step 4: Run full identity tests**

```bash
pytest tests/test_identity_drift.py tests/test_identity_still_compare.py tests/test_identity_strict_gate.py -q
```

- [ ] **Step 5: Commit**

```bash
git add tools/identity_drift.py tests/test_identity_drift.py
git commit -m "feat(identity): weight facial DNA and hybrid flags in evidence"
```

---

### Task 3: CLI `sequence drift-score` still options

**Files:**
- Modify: `tools/cli/sequence_commands.py` (`seq_drift_score`)

- [ ] **Step 1: Update command**

```python
    @app.command("drift-score")
    def seq_drift_score(
        name: str = typer.Argument(..., help="Sequence name or slug"),
        clip: str = typer.Option(..., "--clip", "-c"),
        dna: str = typer.Option(None, "--dna", help="Path to dna.json or character slug"),
        threshold: float = typer.Option(None, "--threshold", help="Default 2.5"),
        ref_still: str = typer.Option(
            None, "--ref-still", help="Hero/reference still path (overrides clip fields)"
        ),
        clip_still: str = typer.Option(
            None, "--clip-still", help="Clip/current still path (overrides clip fields)"
        ),
    ):
        """Score identity drift for a clip against Character DNA (evidence loop #1)."""
        from identity_drift import resolve_still_paths  # or top-level import

        seq = require_sequence(name)
        target = require_clip(seq, clip)
        clips = seq.get("clips", [])
        idx = target["index"]
        prev = clips[idx - 1] if idx > 0 else None
        dna_obj = _load_dna_optional(dna)
        thr = DEFAULT_DRIFT_THRESHOLD if threshold is None else threshold
        ref_p, clip_p = resolve_still_paths(
            target, ref_still=ref_still, clip_still=clip_still
        )
        report = score_identity_drift(
            target,
            dna=dna_obj,
            previous_clip=prev,
            threshold=thr,
            reference_still_path=ref_p,
            clip_still_path=clip_p,
        )
        target["identity_drift"] = report
        save_sequence(seq)
        color = "green" if report["pass"] else "red"
        console.print(
            f"[{color}]drift_score={report['drift_score']} "
            f"(threshold={report['threshold']}) pass={report['pass']} "
            f"mode={report.get('mode')}[/{color}]"
        )
        if report.get("mode") == "hybrid" and report.get("still_signals"):
            ss = report["still_signals"]
            console.print(
                f"[dim]still: luma_mae={ss.get('luma_mae')} "
                f"hist_l1={ss.get('hist_l1')} edge_delta={ss.get('edge_delta')} "
                f"penalty={ss.get('penalty')}[/dim]"
            )
        for factor in report.get("factors") or []:
            console.print(f"  • {factor}")
        if report.get("fixes"):
            console.print("[yellow]Fixes:[/yellow]")
            for fix in report["fixes"]:
                console.print(f"  → {fix}")
```

Import `resolve_still_paths` at module top with other identity_drift imports.

- [ ] **Step 2: Smoke import**

```bash
python -c "from identity_drift import resolve_still_paths, compare_stills_soft; print('ok')"
```

- [ ] **Step 3: Commit**

```bash
git add tools/cli/sequence_commands.py
git commit -m "feat(cli): drift-score --ref-still/--clip-still and hybrid print"
```

---

### Task 4: Protocol + CHANGELOG + verification

- [ ] **Step 1: Protocol subsection**

In `references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md`, after CLI opt-in hard mode (or Tooling section), add:

```markdown
## Hybrid still compare (evidence quality)

`sequence drift-score` accepts `--ref-still` / `--clip-still`, or reads clip fields
(`reference_still_path`, `hero_plate_path`, `last_frame_path`, `first_frame_path`, …).
When both stills load via optional Pillow, the scorer runs multi-signal still compare
(`mode=hybrid`: luma MAE, histogram, edge energy; penalty capped 0–3) in addition to
DNA/metadata heuristics. No face-recognition dependency. Metadata-only when stills
or PIL are unavailable.
```

- [ ] **Step 2: CHANGELOG**

```markdown
- **Identity drift evidence quality** — multi-signal soft-PIL still compare, still path resolve (CLI flags + clip fields), modest facial DNA weighting; `sequence drift-score --ref-still` / `--clip-still`.
```

- [ ] **Step 3: Full verification**

```bash
pytest tests/test_identity_still_compare.py tests/test_identity_drift.py \
  tests/test_identity_strict_gate.py tests/test_drift_evidence_handoff.py -q
```

Expected: all PASS

- [ ] **Step 4: Commit docs**

```bash
git add references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md CHANGELOG.md
git commit -m "docs: hybrid still compare for identity drift evidence quality"
```

---

## Spec coverage

| Spec item | Task |
|-----------|------|
| resolve_still_paths | Task 1 |
| compare_stills_soft multi-signal | Task 1 |
| Report still_signals / still_paths / mode | Task 1 |
| Facial DNA weight | Task 2 |
| hybrid flags in evidence | Task 2 |
| CLI flags | Task 3 |
| Protocol + CHANGELOG | Task 4 |
| Threshold 2.5 / no new hard deps | All |

---

## Execution handoff

Plan complete and saved to `docs/development/superpowers/plans/2026-07-11-identity-drift-evidence-quality-implementation.md`.

**Two execution options:**

1. **Subagent-Driven (recommended)**  
2. **Inline Execution**  

Which approach?
