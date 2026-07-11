# Design: Plate Lock Readiness (Video Without Locked Plate)

**Date:** 2026-07-11  
**Topic:** Opt-in gate so video spend requires curator plate status `approved` or `locked`  
**Status:** Design approved — implement Approach 1  
**Target version:** 3.8.x patch (tools + CLI + light agent notes)  
**Approach:** Pure readiness helper + soft default + `--strict-plate` on batch; plate blockers under `--strict-handoff`  
**Cluster:** Generation routing (deepen existing — no new Role Cards)

## Summary of Decisions

| Decision | Choice |
|----------|--------|
| Cluster | **Generation routing** (Curator / I2V / batch) |
| Primary pain | **Video without locked plate** |
| Surfaces | **Batch video path** + **`imagine agent-handoff`** (video still→video modes) |
| Pass status | **`approved` or `locked`** |
| Default | **Warn-only**; hard only opt-in |
| Data model | **Shot fields** — `plate_status` + optional ids/paths (no required manifest file) |
| Implementation | **1. Shared helper + flags** |

## Problem

Reference Curator and I2V Specialist say: never burn video without an **approved/locked** plate. Reality:

- Shots only track `has_reference: bool` (and optional `reference_image_id` / URL).
- `batch_runner` fails live i2v only when **reference URL is missing** (not dry-run) — no status gate.
- Handoff GHR checks empty `reference_hints` / motion cues — not curator plate status.
- DNA `identity_lock_status=locked` is character lock, not shot plate lock.

Agents can claim “ready for i2v” while the plate is still draft or unset.

## Goals

1. Pure `evaluate_plate_lock_readiness(subject, *, execution_mode=…)` → `{pass, warnings, blockers, fixes, checks}`.  
2. Soft by default: print plate notes on batch run/session and agent-handoff.  
3. `--strict-plate` on `sfw run` / `sfw session` / NSFW twins → exit 1 on blockers **before** spend.  
4. Fold plate blockers into handoff readiness so `--strict-handoff` also fails when plate not approved/locked (still→video modes).  
5. CLI to set/show plate fields on a batch shot.  
6. Light Role Card / skill notes: Reference Curator, I2V Specialist, SFW Batch.  
7. No new agents; no hard-default refuse.

## Non-goals

- Required `ASSET_MANIFEST` file for v1  
- File-must-exist as a hard blocker (path optional; URL resolve remains separate)  
- Motion-block quality epic (separate)  
- Auto-hard for hero tiers only (rejected hybrid)  
- NSFW-only fork  

---

## Approaches considered

### 1. Shared plate-readiness helper + opt-in flags (selected)

See Architecture.

### 2. Handoff-only plate checks

Rejected — misses `sfw run` credit burn.

### 3. Always-hard on batch i2v

Rejected — user chose opt-in hard only.

---

## Architecture

```text
sfw/nsfw run | session          imagine agent-handoff
        │                              │
        ├─ evaluate_plate_lock_readiness(shot, mode=…)
        │                              │
        │                    evaluate_imagine_handoff_readiness
        │                              │ (includes plate checks)
        ├─ always: print ⚠️
        │
        └─ if --strict-plate / --strict-handoff and not pass:
                 exit 1 (no API / no write)
           else:
                 existing execute / emit
```

### Helper contract

```python
# tools/plate_readiness.py

PLATE_OK = frozenset({"approved", "locked"})
PLATE_STATUSES = frozenset({"draft", "approved", "locked"})

# Modes that require plate lock for video spend
PLATE_REQUIRED_MODES = frozenset({"image_to_video", "reference_to_video"})

def evaluate_plate_lock_readiness(
    subject: dict[str, Any],
    *,
    execution_mode: str | None = None,
) -> dict[str, Any]:
    """
    pass=False only when blockers present.
    Image modes and video_prompt: no plate blockers (optional warnings).
    image_to_video / reference_to_video: require plate_status in {approved, locked}.
    """
```

### Rules (v1)

| ID | Severity | When | Rule |
|----|----------|------|------|
| **PL-01** | blocker | plate-required modes | `plate_status` missing / empty |
| **PL-02** | blocker | plate-required modes | `plate_status` not in {approved, locked} (e.g. draft) |
| **PL-03** | warning | plate-required modes | No `plate_path` / `reference_image_id` / `reference_image_url` (status OK but weak identity of plate) |
| **PL-04** | warning | `video_prompt` | `plate_status` present and not approved/locked (optional plate ignored) |
| **PL-05** | — | image modes | skip (pass; no plate required) |

### Shot fields (v1)

| Field | Type | Notes |
|-------|------|--------|
| `plate_status` | `draft` \| `approved` \| `locked` | Primary gate |
| `plate_asset_id` | str optional | Curator asset id |
| `plate_path` | str optional | Local path hint |
| `reference_image_id` | existing | Optional; already used by bridge |
| `reference_image_url` | existing | Optional; runner still resolves URL for live i2v |

`has_reference` remains; does **not** satisfy PL-01/02 alone.

### CLI

```bash
# Set / show
sfw plate set <batch> <shot> --status approved [--path …] [--asset-id …]
sfw plate show <batch> <shot>

# Soft warn, still run
sfw run <batch> <shot>
sfw session <batch>

# Hard
sfw run <batch> <shot> --strict-plate
sfw session <batch> --strict-plate
# NSFW twins same flags
```

### Handoff

- When building agent-mode packet from a batch shot, stamp `plate_status` (and optional plate ids) onto the packet if present on the shot.  
- `evaluate_imagine_handoff_readiness` calls plate helper for `image_to_video` / `reference_to_video` using packet fields.  
- Soft: plate blockers print as ⚠️; hard: existing `--strict-handoff` (no separate flag required on handoff).

### Files

| Path | Action |
|------|--------|
| `tools/plate_readiness.py` | **Create** |
| `tests/test_plate_readiness.py` | **Create** |
| `tools/handoff_readiness.py` | Integrate plate checks |
| `tools/imagine_bridge.py` | Stamp plate fields from subject |
| `tools/batch_runner.py` / `session_runner.py` | Optional preflight hook or CLI-only evaluate |
| `tools/cli/sfw_commands.py` | `plate set/show`, `--strict-plate` on run/session |
| `tools/cli/nsfw_commands.py` | `--strict-plate` on run/session |
| Role Cards / skills (Curator, I2V, sfw-batch) | Thin notes |
| `CHANGELOG.md` | Unreleased |

Prefer **CLI preflight** (evaluate before `execute_shot`) so dry-run and live share the same soft/hard path; keep existing URL check for live i2v.

---

## Testing

| Case | Expected |
|------|----------|
| image_prompt, no plate | pass |
| image_to_video, no plate_status | pass=False, PL-01 |
| image_to_video, draft | pass=False, PL-02 |
| image_to_video, approved | pass=True |
| image_to_video, locked, no path | pass=True + PL-03 warning |
| video_prompt, draft plate | pass=True + PL-04 warning |
| Soft `sfw run` without flag | still executes; prints warnings |
| `--strict-plate` on i2v without plate | exit 1 before API |
| `--strict-handoff` i2v packet without plate_status | exit 1 |

---

## Acceptance criteria

- [ ] Helper + unit tests  
- [ ] `sfw plate set/show`  
- [ ] `--strict-plate` on SFW/NSFW run + session  
- [ ] Handoff stamps + readiness integration under `--strict-handoff`  
- [ ] Default path unchanged without flags  
- [ ] Agent notes + CHANGELOG  
- [ ] No new agents  

---

## Next step

Implementation plan → TDD implement → commit.

---

*Grok Imagine Cinematic Studio — Plate Lock Readiness design — 2026-07-11*
