---
name: arc-replan-copilot
description: Replan remaining sequence beats and emotional temperature after mid-sequence QA or drift failure without rewriting the Production Bible. Activate after chain QA No-Go or identity drift lock on long-form sequences.
---

# Arc Replan Co-pilot v3.6.7

**Pipeline skill** — mid-sequence recovery without touching the Production Bible.  
**Tool:** `tools/arc_replan.py`  
**Pairs with:** Sequence Director, Chain QA Protocol, Identity Lock, Emotional Temperature gate

## Model Layer (Grok 4.5 · studio v3.6.7)

| Layer | Slug | When |
|-------|------|------|
| Orchestration (default) | `grok-4.5` | Bibles, direction, agent loops |
| Long-context (opt-in) | `grok-4.3` | 1M memory banks (`--chat-model grok-4.3`) |
| Grok Build CLI | `grok-4.5` · `grok-build` | Skills / coding (≥ 0.2.93) |
| Imagine Video | `grok-imagine-video` / `1.5` | 1.0 cost · 1.5 native audio |
| Imagine Image | `grok-imagine-image` / quality | Stills / hero plates |

Prefer stable `prompt_cache_key` on multi-turn `grok-4.5` loops. Full stack: `references/agents/MODEL_LAYER_v3.6.7.md` · `tools/models.py`.

## Activation

```
ACTIVATE ARC_REPLAN
```

**When to activate**
- Chain QA returns **No-Go** mid-sequence
- Identity drift lock / drift fail on a clip that still has remaining beats
- Emotional temperature gate **fail** on the planned curve
- Status `qa_hold` with remaining clips to schedule

Do **not** activate for first-clip planning — use Sequence Director `sequence init` instead.

## Principles

1. **Bible stays sacred** — replan only sequence clip beats, temperature curve points, and notes. Never rewrite the Production Bible or Mega Architect package.
2. **Frozen prefix** — clips with `index < from_index` stay unchanged; only index ≥ failure point is replanned.
3. **Proposal then apply** — `plan` is read-only (saves `arc_replan_proposal`); `apply` writes beats + curve and records `arc_replan_history`.
4. **Deterministic heuristics** — tool has no LLM and no Imagine spend; agents may refine narrative prose after apply.
5. **No auto re-gen** — after replan, Sequence Director / extend-regen loop own regeneration (`sequence regen plan|apply|run`).

## CLI

Plan remaining beats and temperature curve (does not mutate beats/curve):

```bash
python tools/cinematic_studio_cli.py sequence replan plan "Sequence Name"
python tools/cinematic_studio_cli.py sequence replan plan "Sequence Name" --from-index 2
python tools/cinematic_studio_cli.py sequence replan plan "Sequence Name" --clip clip_003 --reason chain_qa_no_go
```

Apply proposal (mutates `narrative_beat` + `emotional_temperature_curve`):

```bash
python tools/cinematic_studio_cli.py sequence replan apply "Sequence Name" --yes
python tools/cinematic_studio_cli.py sequence replan apply "Sequence Name" --from-index 2 --reason identity_drift --yes
```

Optional: `--reason` override (`chain_qa_no_go` | `identity_drift` | `temperature_fail` | `qa_hold` | `manual`).

## Actions (v1)

| Action | When |
|--------|------|
| `soft_reset` | First replanned clip after no_go / drift / temp fail / qa_hold |
| `revise_beat` | Subsequent remaining clips (progressive temps toward end target) |
| `keep` | Reserved (no change) |
| `insert_bridge` | Reserved / notes only — not applied in v1 |

## Handoff → Sequence Director

After apply:

1. Sequence Director reviews replanned beats + temperature curve (`sequence show`, `sequence temp show`, `sequence health`)
2. Fix failure clip via `sequence regen plan|apply|run` (or full re-extend) before advancing
3. Resume CLIP_DEPENDENCY_GRAPH from the soft-reset index — never generate N+1 until N is QA-approved
4. Chain QA + Continuity Guardian re-gate each boundary after re-generation

```
Chain QA No-Go / drift lock
  → ACTIVATE ARC_REPLAN (plan → apply)
  → Sequence Director re-orders remaining dependency graph
  → regen / extend from frozen last-good frame
  → Chain QA again
```
