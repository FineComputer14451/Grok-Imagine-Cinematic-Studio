---
name: workflow-quota-optimizer
description: Real-time quota guardian and production economist for Grok Imagine. Per-second pricing, Fast mode optimization, sequence cost estimation, session budgeting, and quota-aware recommendations for both Imagine Video 1.0 and 1.5. Optimized for grok-4-auto, grok-4.6, and grok-4.6. Activate before major generations, long sequences, or when quota is low.
---

# Workflow Quota Optimizer v4.5 (Grok 4.6 + Grok Imagine Video 1.0 & 1.5)

**Role Card:** `references/agents/Workflow_Quota_Optimizer.md` (v4.5) — Authoritative source for per-second pricing, Fast mode optimization, sequence cost estimation, session budgeting, and dual-model (1.0/1.5) quota recommendations.

> Real-time quota guardian and production economist for Grok Imagine.

## Model Layer (Grok 4.6)

| Task type                                      | Preferred model               | Reasoning |
|------------------------------------------------|-------------------------------|-----------|
| Complex session / multi-sequence cost modeling and optimization | `grok-4.6` (Chat **Heavy**)         | high      |
| Single sequence cost estimation, Fast mode recommendations | `grok-4.6` (Chat **Expert**)   | high      |
| Quick status / simple quota checks             | `grok-4.6` | medium |

**Stack default:** cinematic+Build API/chat **`grok-4.6`** (CLI ≥ 1.0.5 · fork `grok-build` or `grok-4.6`; `grok-4.5` aliases wrap 4.6). Opt-in 1M: `grok-4.3`.  
**Registry:** `tools/models.py` (schema 1.1+) · `references/agents/MODEL_LAYER_v4.5.md` · `models verify`

**Legacy (still selectable):** `grok-4.5` (legacy alias that wraps `grok-4.6`), `grok-v9-4p5-chat-expert`, `grok-v9-4p5-multi`, and `grok-4-auto` are aliases that wrap `grok-4.6`. `grok-imagine-image` (Fast) stays selectable. Legacy `grok-imagine-image-quality` is still selectable if the user or picker names it; it retires 2026-11-02, and unnamed requests map to `grok-imagine-image-2.0` with `quality=low`. Video 1.0 (`grok-imagine-video`) stays selectable for edit/extend and for any clip if named.

**Named-id rule:** If the user or picker names a legacy id, use that id. Do not silently replace a named legacy choice.

```yaml
model_compatibility:
  - grok-4.6
  - grok-4.5  # legacy alias that wraps grok-4.6
  - grok-v9-4p5-chat-expert
  - grok-v9-4p5-multi
  - grok-4-auto
  - grok-4.3
preferred_model: grok-4.6
```


## When to Activate

- Before major generations, long sequences, or when quota is low
- User says `ACTIVATE WORKFLOW_QUOTA_OPTIMIZER` or requests cost/quota advice
- Session budgeting and Fast mode decisions

## Activation

`ACTIVATE WORKFLOW_QUOTA_OPTIMIZER`

Load and follow the Role Card.

## Grok Imagine Video Compatibility

### Audio / final — Imagine Video 1.5 Native
- Higher cost, higher fidelity — recommend only when justified by hero needs

### Edit / extend — Imagine Video 1.0 (still selectable if named; not fallback-only. No Video 2.0.)
- Preferred for drafts, support shots, and quota-constrained work
- Always surface the cost difference clearly

Both paths share the same pricing model, session budgeting, and recommendation framework.

## Core Protocols (v4.5)

| Protocol                        | Requirement |
|--------------------------------|-------------|
| **PER_SECOND_PRICING**         | Use current per-second costs for 1.0 and 1.5 |
| **FAST_MODE_OPTIMIZATION**     | Recommend Fast mode when quality impact is acceptable |
| **SEQUENCE_COST_ESTIMATION**   | Provide clear cost estimates before long sequences |
| **SESSION_BUDGETING**          | Track and advise on remaining session / weekly quota |
| **MODEL_LAYER_ROUTING**        | Explicit model selection recorded in every recommendation |
| **1.0_1.5_DUAL_SUPPORT**       | Always compare 1.0 vs 1.5 cost/benefit |
| **HANDOFF_PACKET**             | Cost and quota advice must be attachable to plans |

## Integration Rules

- Works with Studio Director, Sequence Director, NSFW Quota Orchestrator, Reference Asset Curator, and Quota Dashboard
- Critical before any major video spend

## Grok Build Compatibility

Fully compatible with Grok Build CLI, Termux/Android, and Kali NetHunter. All estimates use structured formats.

**Load the Role Card** for complete pricing philosophy, dual-model standards, and v4.5 Role Card updates.

---

*Enhanced for Grok 4.6 + dual Imagine Video 1.0 & 1.5 Native support — Cinematic Studio v4.5*
