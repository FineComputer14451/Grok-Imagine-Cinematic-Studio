# Design: Identity Drift Evidence Quality (Hybrid Still + Metadata)

**Date:** 2026-07-11  
**Topic:** Stronger identity drift evidence via soft-PIL still compare + modest metadata upgrades  
**Status:** Design approved — ready for implementation planning  
**Target version:** 3.8.x patch (tools + CLI + protocol note)  
**Approach:** In-place upgrade of `score_identity_drift` (hybrid when stills resolve; metadata fallback)  
**Parents:** [Identity Continuity Agent Wiring](./2026-07-11-identity-continuity-agent-wiring-design.md) · [Identity Strict CLI Gates](./2026-07-11-identity-strict-cli-gates-design.md)

## Summary of Decisions

| Decision | Choice |
|----------|--------|
| Evidence mode | **Hybrid stack** — stills when available + metadata fallback |
| Dependencies | **Soft PIL only** — no face ML, mediapipe, torch, or vision API |
| Still path source | **Flags + clip fields** (`--ref-still` / `--clip-still` override known clip keys) |
| Implementation | **In-place** upgrade of `score_identity_drift` / still compare (not a v2 dual scorer) |
| Threshold | **Unchanged** (default 2.5) |
| Aggressive artifact search | **Out of scope** (no `artifacts/` guess by `reference_image_id`) |

## Problem

`score_identity_drift` is mostly **text heuristics** (DNA tokens, anchors, ref IDs). Hybrid still compare exists as a 64×64 mean-abs pixel penalty, but:

1. `sequence drift-score` never passes still paths → hybrid almost never runs.  
2. Mean-abs at 64×64 is a weak identity signal.  
3. Facial DNA is not weighted separately from the full DNA corpus.

Scores can look confident while only comparing prose — weak input for ICP, `--strict-identity`, and chain QA.

## Goals

1. Resolve still paths from CLI flags and clip fields.  
2. Improve offline still compare (multi-signal, soft PIL) with structured `still_signals`.  
3. Modest metadata quality (facial DNA emphasis) without breaking existing metadata tests.  
4. Surface hybrid mode clearly on the report and in CLI output.  
5. Keep threshold 2.5 and strict-gate contracts stable.

## Non-goals

- Face recognition / landmarks / external vision APIs  
- New packaging dependencies (Pillow remains soft-optional)  
- Dual scorer modules or score scale redesign  
- Auto-discovery under `artifacts/` by reference id  
- Changing `--strict-identity` fail matrix  
- New agents or Role Card rewrites (protocol note only)

---

## Architecture

```text
sequence drift-score [--ref-still] [--clip-still]
        │
        ├─ resolve_still_paths(clip, ref_still=, clip_still=)
        │     flags > clip keys > (None, None)
        │     nonexistent files → None
        │
        └─ score_identity_drift(..., reference_still_path, clip_still_path)
                 │
                 ├─ metadata penalties (facial DNA weight + existing signals)
                 │
                 └─ if both paths + PIL OK:
                        compare_stills_soft → penalty (0–3) + still_signals
                        mode = "hybrid"
                    else:
                        mode = "metadata"
                 │
                 ▼
        clip["identity_drift"] = report
        report_to_drift_evidence → signals.flags include hybrid/mode hints
```

### Units

| Unit | Responsibility |
|------|----------------|
| `resolve_still_paths` | Flag override + clip key order; validate path exists |
| `compare_stills_soft` | Multi-signal PIL compare; returns `(penalty, signals)` or `None` |
| `score_identity_drift` | Metadata + optional hybrid; additive report fields |
| CLI `sequence drift-score` | `--ref-still`, `--clip-still`; resolve; print mode/signals |

### Clip keys (auto-resolve, first hit wins)

| Role | Keys (in order) |
|------|-----------------|
| Reference / hero | `reference_still_path`, `hero_plate_path`, `ref_still_path` |
| Clip / current | `clip_still_path`, `last_frame_path`, `first_frame_path`, `still_path` |

Empty string or missing file → treat as unset.

### Still compare v2 (soft PIL)

1. Open both as RGB; resize to **128×128**.  
2. **Luma MAE** (normalized) → contribution clamped to **0–1.5**.  
3. **Histogram L1** (per-channel 32 bins, averaged) → **0–1.0**.  
4. **Edge energy delta** (simple greyscale neighbor abs-diff magnitude) → **0–0.5**.  
5. `penalty = clamp(sum, 0.0, 3.0)` — same max as current hybrid for score stability.  
6. Return signals dict: `luma_mae`, `hist_l1`, `edge_delta`, `size` (128).  
7. ImportError / OSError → `None` (stay metadata-only; no crash).

Replace `_optional_still_drift` behavior with `compare_stills_soft` (rename or thin wrapper for clarity).

### Metadata modest upgrades

| Signal | Behavior |
|--------|----------|
| Facial DNA tokens | Tokenize `facial_dna` separately; if facial recall is much worse than full-corpus overlap, add up to **+1.0** penalty + explicit factor |
| Anchors | Keep existing hit/miss + full-hit credit (−0.75) |
| Prompt + recap | Continue combined corpus; factor when anchors land primarily via recap |

**Constraint:** Existing tests such as `test_strong_lock_low_drift` must remain green without flaky retuning.

### Report shape (additive)

```python
{
  "clip_id": ...,
  "drift_score": float,
  "threshold": float,
  "pass": bool,
  "mode": "metadata" | "hybrid",
  "factors": list[str],
  "fixes": list[str],
  "suggested_character_drift_boundary": float,
  "still_signals": dict | None,       # hybrid only
  "still_paths": {"ref": str|None, "clip": str|None},
}
```

### CLI

```bash
python tools/cinematic_studio_cli.py sequence drift-score "Seq" --clip clip_002 \
  --dna characters/liora/dna.json \
  --ref-still path/to/hero.png \
  --clip-still path/to/last_frame.png
```

- Flags optional; auto-resolve from clip when omitted.  
- Print `mode=` and a one-line still_signals summary when hybrid.  
- Unchanged: DNA option, threshold option, persistence of `identity_drift` on clip.

### Evidence mapping

When `report_to_drift_evidence` runs, if `mode == "hybrid"` append flag `hybrid_still` (and optionally top still signal names) to `signals.flags` so handoffs show evidence quality source.

### Files

| Path | Action |
|------|--------|
| `tools/identity_drift.py` | resolve, compare_stills_soft, metadata tweak, report fields |
| `tools/cli/sequence_commands.py` | `drift-score` flags + resolve + print |
| `tests/test_identity_drift.py` and/or `tests/test_identity_still_compare.py` | unit + hybrid |
| `references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md` | hybrid note |
| `CHANGELOG.md` | Unreleased |

---

## Testing

| Case | Expected |
|------|----------|
| Existing metadata suite | Pass without change of intent |
| Flags override clip fields | Resolved paths = flags |
| Clip fields with real temp files | Auto hybrid when PIL present |
| Missing path | No hybrid |
| Identical synthetic stills | Low still penalty; `mode=hybrid` |
| Highly different stills | Higher still penalty than identical |
| No PIL installed | Metadata path works; hybrid tests skipped |
| Facial DNA miss | Factor present; score may rise |

Use temporary PNGs via Pillow when available; skip hybrid-only tests if PIL missing.

---

## Docs & rollout

1. Implement resolve + compare + metadata + tests.  
2. Wire CLI.  
3. Protocol subsection **Hybrid still compare**.  
4. CHANGELOG Unreleased.  
5. No plugin pin required for tools-only change (optional if protocol-only skill touch).

### Protocol note (sketch)

```markdown
## Hybrid still compare (evidence quality)

`sequence drift-score` accepts `--ref-still` / `--clip-still`, or reads clip
fields (`reference_still_path`, `last_frame_path`, …). When both stills load
via optional Pillow, scorer runs multi-signal still compare (mode=hybrid)
in addition to DNA/metadata heuristics. No face-recognition dependency.
```

---

## Risks

| Risk | Mitigation |
|------|------------|
| Score drift breaks old tests | Cap still penalty at 3; keep metadata path primary; run full identity test suite |
| False hybrid from bad paths | Require file exists; nonexistent → None |
| PIL not installed | Soft import; metadata-only |
| Users expect real face ID | Document structural compare only, not biometrics |

---

## Acceptance criteria

- [ ] `resolve_still_paths` with flags + clip keys  
- [ ] Multi-signal still compare, penalty 0–3, `still_signals` on hybrid reports  
- [ ] CLI `--ref-still` / `--clip-still` + auto-resolve  
- [ ] Modest facial metadata weighting; baseline metadata tests pass  
- [ ] Threshold 2.5 unchanged; no new hard deps  
- [ ] Protocol + CHANGELOG updated  

---

## Approaches considered

| Approach | Outcome |
|----------|---------|
| **1. In-place hybrid upgrade** | **Selected** |
| 2. Separate v2 scorer module | Rejected — dual maintenance |
| 3. Metadata-only | Rejected — user chose hybrid |

---

## Relationship to prior work

- Improves inputs to ICP `drift_evidence` and `--strict-identity` without changing gate rules.  
- Complements seam-report (seams ≠ identity) — still paths may overlap but signals stay separate.  
- Future: optional face landmarks, vision API — not this epic.

---

## Next step

After user review of this written spec: invoke **writing-plans** for implementation.

---

*Grok Imagine Cinematic Studio — Identity Drift Evidence Quality design — 2026-07-11*
