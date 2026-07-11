# Design: Motion Brief Readiness (Structured MOTION_VECTOR)

**Date:** 2026-07-11  
**Topic:** Structured `motion_vector` {action, camera, emotion} before video spend  
**Status:** Design approved — implement Approach 1  
**Target version:** 3.8.x patch  
**Approach:** Pure readiness helper + soft default + free-text fallback; `--strict-motion` / `--strict-handoff` require full triple  
**Cluster:** Generation routing (deepen existing — no new Role Cards)

## Summary of Decisions

| Decision | Choice |
|----------|--------|
| Pain | **No structured motion brief** |
| Surfaces | **All video modes** on batch + agent-handoff |
| Complete brief | Nonempty **action, camera, emotion** |
| Default | **Warn-only** for incomplete structure |
| Free-text (GHR-03) | **Fallback** soft; **not enough** under strict |
| Implementation | **1. Shared helper + CLI + handoff/batch wire** |

## Goals

1. `evaluate_motion_brief_readiness(subject, *, execution_mode, strict=False)`.  
2. Soft: complete triple → pass; free-text only → pass + warning; neither → blocker.  
3. Strict: require complete triple (free-text alone fails).  
4. `sfw motion set/show`; `--strict-motion` on SFW/NSFW run/session.  
5. Handoff stamps `motion_vector`; GHR-03 uses helper (`strict=True` under `--strict-handoff`).  
6. No new agents.

## Non-goals

- Sequence `momentum_vector` redesign  
- Auto-writing motion from description LLM  
- Unified `--strict-spend` mega-flag (later)

## Architecture

```text
video modes (i2v | ref2v | video_prompt)
        │
        └─ evaluate_motion_brief_readiness(..., strict=?)
                 complete triple → pass
                 free-text only  → soft pass + MB-01 warn; strict → MB-02 blocker
                 neither         → blocker MB-03 / GHR-03
```

### Shot fields

| Field | Notes |
|-------|--------|
| `motion_vector` | `{action, camera, emotion}` strings |
| `motion_tier` | optional: micro \| medium \| kinetic |

Also accept aliases on packet: `i2v_motion_block`, `motion_block` (same shape).

### CLI

```bash
sfw motion set <batch> <shot> --action "…" --camera "…" --emotion "…" [--tier medium]
sfw motion show <batch> <shot>
sfw run <batch> <shot> --strict-motion
sfw session <batch> --strict-motion
```

### Files

| Path | Action |
|------|--------|
| `tools/motion_readiness.py` | Create |
| `tests/test_motion_readiness.py` | Create |
| `tools/handoff_readiness.py` | GHR-03 via helper |
| `tools/imagine_bridge.py` | Stamp motion fields |
| `tools/cli/sfw_commands.py` | motion set/show + flag |
| `tools/cli/nsfw_commands.py` | flag |
| `tools/session_runner.py` | strict_motion |
| Role Cards / skills | I2V, Prompt Master, SFW thin notes |
| `CHANGELOG.md` | Unreleased |

---

*Motion Brief Readiness design — 2026-07-11*
