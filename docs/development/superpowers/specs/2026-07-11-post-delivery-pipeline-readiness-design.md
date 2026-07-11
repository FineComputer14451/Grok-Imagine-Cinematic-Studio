# Design: Post-Delivery Pipeline Readiness (Order Gates)

**Date:** 2026-07-11  
**Topic:** Opt-in readiness gates for Assembly → Polish → Deliver pipeline order  
**Status:** Design approved — ready for implementation planning  
**Target version:** 3.8.x patch  
**Approach:** Pure readiness helper + soft default + `--strict-delivery` on `sequence polish` / `sequence deliver`  
**Cluster:** Post & delivery (deepen existing — no new agents)

## Summary of Decisions

| Decision | Choice |
|----------|--------|
| Cluster | **Post & delivery** |
| Primary pain | **Pipeline order / readiness** |
| Enforcement | **Opt-in hard only** (`--strict-delivery`) |
| Implementation approach | **1. Shared readiness helper + CLI flags** (recommended) |

## Problem

CLI already exposes:

```bash
sequence edl → sequence polish → sequence deliver
```

But:

- `polish` does not require a saved EDL  
- `deliver` only **notes** “No polished clips” and can still produce empty/weak manifests  
- Non-Go / unapproved clips can slip in depending on flags  
- Agents (Assembly, Color, Polish, ffmpeg) state order in prose without a shared machine check  

Same pattern as identity / handoff readiness: **tools exist; order is soft**.

## Goals

1. Pure `evaluate_delivery_pipeline_readiness(seq, *, stage)` with blockers + warnings.  
2. Soft by default: print readiness notes on polish/deliver.  
3. `--strict-delivery` on `sequence polish` and `sequence deliver` → exit 1 on blockers **before** side effects.  
4. Light agent notes: Assembly Editor, AI Polish Director, Color (optional), cinematic-ffmpeg.  
5. No new Role Cards; no hard-default refuse.

## Non-goals

- Full color LUT pipeline as code  
- Replacing ai-video-upscaler / ffmpeg scripts  
- Social-crop completeness as hard blockers (may warn)  
- Specialist-order for generation (separate epic)  

---

## Approaches considered

### 1. Shared readiness helper + flags (selected)

`tools/delivery_readiness.py`:

```python
def evaluate_delivery_pipeline_readiness(
    seq: dict,
    *,
    stage: Literal["polish", "deliver"],
    approved_only: bool = True,
) -> dict:  # pass, blockers, warnings, fixes, checks
```

| Stage | Blockers (strict) | Warnings |
|-------|-------------------|----------|
| **polish** | Zero clips eligible for polish (no Go/approved when approved_only); optional: zero source media paths found | EDL file missing (recommend `sequence edl`); partial missing media |
| **deliver** | No polished mp4 under polished dir for slug; zero EDL entries when approved_only and no approved clips | EDL missing (auto-build may still run); ffmpeg not on PATH |

Wire:

```bash
sequence polish "Seq" --strict-delivery
sequence deliver "Seq" --strict-delivery
```

Default: call readiness, print ⚠️, continue (current behavior).

### 2. Protocol-only agent wiring

Docs only — rejected for chosen opt-in hard enforcement.

### 3. Hard by default with --force

Rejected — user chose opt-in hard only.

---

## Architecture

```text
sequence polish / deliver
        │
        ├─ evaluate_delivery_pipeline_readiness(seq, stage=...)
        │
        ├─ always: print warnings / blockers
        │
        └─ if --strict-delivery and not pass:
                 exit 1 (no polish/deliver side effects)
           else:
                 existing polish_sequence / deliver_sequence
```

### Eligibility (aligned with assembly_editor)

Clip eligible when (same spirit as `build_edl` approved_only):

- `status in (approved, qa_pass)` **or** `chain_qa.decision == go` (or nsfw_chain_qa)

### Files

| Path | Action |
|------|--------|
| `tools/delivery_readiness.py` | **Create** |
| `tests/test_delivery_readiness.py` | **Create** |
| `tools/cli/sequence_commands.py` | `--strict-delivery` on polish + deliver |
| Role Cards / skills (Assembly, AI Polish, cinematic-ffmpeg) | Short order + flag notes |
| `CHANGELOG.md` | Unreleased |

### Color grading

Warn-only note in readiness when stage=polish: “Color grade notes recommended before hero polish” if no `color_grade` / grade field on seq — **not a blocker** (color is protocol-heavy).

---

## Testing

| Case | Expected |
|------|----------|
| Seq with no Go clips, polish strict | pass=False |
| Seq with Go clip but no media file | warn or block if zero resolveable sources |
| Polished dir empty, deliver strict | pass=False |
| Polished mp4 present, deliver | pass=True |
| Soft path without flag | still runs; prints notes |

---

## Acceptance criteria

- [ ] Readiness helper + unit tests  
- [ ] `--strict-delivery` on polish and deliver  
- [ ] Default path unchanged (no exit 1 without flag)  
- [ ] Agent/docs notes + CHANGELOG  
- [ ] No new agents  

---

## Next step

User confirms design → commit spec → writing-plans → implement.

---

*Grok Imagine Cinematic Studio — Post-Delivery Pipeline Readiness design — 2026-07-11*
