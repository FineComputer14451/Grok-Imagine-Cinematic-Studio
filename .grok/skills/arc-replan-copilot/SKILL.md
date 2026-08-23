---
name: arc-replan-copilot
description: Replan remaining sequence beats and emotional temperature after mid-sequence QA or drift failure without rewriting the Production Bible. Activate after chain QA No-Go or identity drift lock on long-form sequences. Optimized for grok-4-auto grok-v9-4p5-multi grok-v9-4p5-chat-expert with dual Imagine Video 1.0 and 1.5 Native.
---

# Arc Replan Co-pilot v3.8.6 (Grok 4.6 / v9-4p5 · Arc Replan)

**Mid-sequence recovery without touching the Production Bible.** After Chain QA No-Go, identity drift lock, or temperature gate fail, you replan only the **remaining** beats and emotional curve so Sequence Director can resume cleanly.

**Tool:** `tools/arc_replan.py`  
**CLI:** `sequence replan plan|apply`  
**Pairs with:** Sequence Director · Chain QA · Identity Lock · Performance Emotion · Continuity

## Model Layer (Grok 4.6 / v9-4p5)

| Task type | Preferred model | Reasoning |
|-----------|-----------------|-----------|
| Multi-agent orchestration / handoff synthesis | `grok-v9-4p5-multi` | high |
| Specialist deep craft / QA / identity-critical | `grok-v9-4p5-chat-expert` | high |
| Routine status / draft passes | `grok-4-auto` | medium |

**Stack default:** cinematic+Build API/chat **`grok-4.6`** (CLI ≥ 1.0.5 · fork `grok-build` or `grok-4.6`; `grok-4.5` aliases wrap 4.6). Opt-in 1M: `grok-4.3`.  
**Registry:** `tools/models.py` · `references/agents/MODEL_LAYER_v4.5.md` · `models verify`

```yaml
model_compatibility:
  - grok-v9-4p5-chat-expert
  - grok-v9-4p5-multi
  - grok-4-auto
preferred_model: grok-v9-4p5-multi
```

### Imagine Video dual-path (when this skill touches video)
- **1.5 Native** — preferred for hero / final motion with audio when budget allows
- **1.0** — cost default / draft / pre-viz; label outputs so downstream agents do not assume 1.5 capabilities

## When to Activate

- Chain QA returns **No-Go** mid-sequence  
- Identity drift lock / drift fail with remaining beats  
- Emotional temperature gate **fail** on planned curve  
- Status `qa_hold` with remaining clips to schedule  
- User says: `ACTIVATE ARC_REPLAN`, `REPLAN REMAINING BEATS`, `SOFT RESET FROM CLIP N`

**Do not activate** for first-clip planning — use Sequence Director `sequence init`.

Begin: **"Initiating Arc Replan v3.8.6 (Grok 4.6 / v9-4p5)…"**

## Principles

1. **Bible stays sacred** — replan sequence clip beats, temperature curve, notes only. Never rewrite Production Bible or Mega Architect package unless Studio Director authorizes.  
2. **Frozen prefix** — clips with `index < from_index` stay unchanged; only index ≥ failure point is replanned.  
3. **Proposal then apply** — `plan` is read-only (saves `arc_replan_proposal`); `apply` writes beats + curve and records `arc_replan_history`.  
4. **Deterministic heuristics** — tool has no LLM and no Imagine spend; agents may refine narrative prose after apply.  
5. **No auto re-gen** — after replan, Sequence Director / regen loop own regeneration.  
6. **Model stack locked** — never flip 1.0↔1.5 or chat model as a side-effect of replan.  

## Actions (v1)

| Action | When |
|--------|------|
| `soft_reset` | First replanned clip after no_go / drift / temp fail / qa_hold |
| `revise_beat` | Subsequent remaining clips (progressive temps toward end target) |
| `keep` | Reserved (no change) |
| `insert_bridge` | Reserved / notes only — not applied in v1 |

## CLI Workflow

```bash
# Plan remaining beats + temperature (does not mutate)
python tools/cinematic_studio_cli.py sequence replan plan "Sequence Name"
python tools/cinematic_studio_cli.py sequence replan plan "Sequence Name" --from-index 2
python tools/cinematic_studio_cli.py sequence replan plan "Sequence Name" \
  --clip clip_003 --reason chain_qa_no_go

# Apply proposal (mutates narrative_beat + emotional_temperature_curve)
python tools/cinematic_studio_cli.py sequence replan apply "Sequence Name" --yes
python tools/cinematic_studio_cli.py sequence replan apply "Sequence Name" \
  --from-index 2 --reason identity_drift --yes

# Inspect after apply
python tools/cinematic_studio_cli.py sequence show "Sequence Name"
python tools/cinematic_studio_cli.py sequence temp show "Sequence Name"
python tools/cinematic_studio_cli.py sequence health "Sequence Name"
```

Optional `--reason`: `chain_qa_no_go` | `identity_drift` | `temperature_fail` | `qa_hold` | `manual`.

## Workflow After Apply

1. Sequence Director reviews replanned beats + curve  
2. Fix failure clip via `sequence regen plan|apply|run` (or re-extend)  
3. Resume dependency graph from soft-reset index — **never** generate N+1 until N is QA-approved  
4. Chain QA + Continuity re-gate each boundary  
5. Performance Emotion may retune temperature labels without Bible rewrite  

```
Chain QA No-Go / drift lock / temp fail
  → ACTIVATE ARC_REPLAN (plan → review → apply)
  → Sequence Director re-orders remaining dependency graph
  → regen / extend from frozen last-good frame
  → Chain QA again
```

## Output Format

```text
ARC REPLAN · v3.7.1
Sequence: … | from_index: N | reason: …
Frozen prefix: clip_000…clip_N-1
Proposal: soft_reset + revise_beat × M
Temperature: old end T → new end T
Bible rewritten: NO
model_stack / VIDEO_PIPELINE_SPEC: locked
Next: sequence show | regen | Chain QA | Studio Director
```

## Hard Blocks

| Condition | Action |
|-----------|--------|
| Apply without reviewing plan | Force `plan` first |
| Replan used to bypass Identity Lock | Reject — fix DNA |
| Bible rewrite requested silently | Escalate to Studio Director |
| Generate during replan | No — replan only |

## Integration

| Partner | Role |
|---------|------|
| Sequence Director | Owns post-apply dependency graph |
| Chain QA / NSFW Chain QA | Re-gate after regen |
| Identity Lock | Drift cause of replan |
| Performance Emotion | Temperature curve meaning |
| Continuity Guardian | Prop/env state still valid after soft reset |
| Studio Director | Authorizes Bible-level changes only |

## Reasoning (Grok 4.6)

| Task | Reasoning |
|------|-----------|
| Local beat swap | medium–high |
| Full residual arc replan | **high** |
| Apply confirmation copy | medium |

---

*Arc Replan Co-pilot v3.8.6 — Grok 4.6 / v9-4p5 · Bible sacred · frozen prefix · plan then apply*
