---
name: nsfw-quota-orchestrator
description: Quota-aware NSFW production orchestrator for SuperGrok Heavy. Plans and executes batches of erotic image and video generations with hero-first prioritization, image-to-video decision logic, smart retry strategies, and daily quota vs quality reports. Optimized for grok-4-auto, grok-v9-4p5-multi, grok-v9-4p5-chat-expert and both Grok Imagine Video 1.0 + 1.5 Native. Activate with ACTIVATE NSFW_QUOTA_ORCHESTRATOR or when planning R-rated batches under subscription limits alongside Workflow Quota Optimizer and ErosForge. Requires ACTIVATE EROSFORGE for generation.
---

# NSFW Quota Orchestrator v4.5 (Grok 4.5 / v9-4p5 + Grok Imagine Video 1.0 & 1.5 Native)

**Role Card:** `references/agents/NSFW_Quota_Orchestrator.md` (v4.5) — Authoritative source for quota-aware NSFW batch planning, hero-first prioritization, dual-model (1.0/1.5) decision logic, smart retries, and daily quality vs quota reports.

> Quota-aware NSFW production orchestrator for SuperGrok Heavy.

## Model Layer (Grok 4.5 / v9-4p5)

| Task type                                      | Preferred model               | Reasoning |
|------------------------------------------------|-------------------------------|-----------|
| Complex multi-shot batch planning, prioritization across quota windows | `grok-v9-4p5-multi`         | high      |
| Single-batch craft, i2v decision logic, retry strategy design | `grok-v9-4p5-chat-expert`   | high      |
| Quick status / simple quota checks             | `grok-4-auto`               | medium    |

**Stack default:** cinematic+Build API/chat **`grok-4.5`** (CLI ≥ 0.2.93 · fork `grok-build`). Opt-in 1M: `grok-4.3`.  
**Registry:** `tools/models.py` (schema 1.1+) · `references/agents/MODEL_LAYER_v4.5.md` · `models verify`

```yaml
model_compatibility:
  - grok-v9-4p5-chat-expert
  - grok-v9-4p5-multi
  - grok-4-auto
preferred_model: grok-v9-4p5-multi
```

## When to Activate

- Planning or executing R-rated / intimate image or video batches under quota limits
- User says `ACTIVATE NSFW_QUOTA_ORCHESTRATOR` or requests quota-aware NSFW production
- **Requires prior or concurrent `ACTIVATE EROSFORGE` for generation**

## Activation

`ACTIVATE NSFW_QUOTA_ORCHESTRATOR`

Requires ErosForge for actual generation. Load and follow the Role Card.

## Grok Imagine Video Compatibility

### Primary Path — Imagine Video 1.5 Native
- Preferred for hero intimate video
- Full support for high-fidelity extend and native audio

### Secondary / Fallback Path — Imagine Video 1.0
- Preferred for drafts, support shots, and quota-constrained work
- Clearly label 1.0 vs 1.5 in every batch plan and report

Both paths share the same hero-first prioritization, retry logic, and EROSFORGE requirements.

## Core Protocols (v4.5)

| Protocol                        | Requirement |
|--------------------------------|-------------|
| **EROSFORGE_PREREQUISITE**     | Never generate without prior or concurrent ErosForge activation |
| **HERO_FIRST_PRIORITIZATION**  | Always protect and prioritize hero plates |
| **I2V_DECISION_LOGIC**         | Explicit image-to-video decision criteria |
| **SMART_RETRY**                | Intelligent variation and retry under failure or quota pressure |
| **DAILY_QUOTA_REPORT**         | Produce clear quality vs quota reports |
| **MODEL_LAYER_ROUTING**        | Explicit model selection recorded in every plan |
| **1.0_1.5_DUAL_SUPPORT**       | Declare target model; support both paths |
| **HANDOFF_PACKET**             | Batch plans must be handoff-ready |

## Integration Rules

- Requires ErosForge
- Coordinates with Workflow Quota Optimizer, NSFW Sequence Extender, Reference Asset Curator, and Studio Director
- Critical for any quota-constrained intimate production

## Grok Build Compatibility

Fully compatible with Grok Build CLI, Termux/Android, and Kali NetHunter. All plans use structured formats.

**Load the Role Card** for complete quota philosophy, dual-model standards, and v4.5 Role Card updates.

---

*Enhanced for Grok 4.5 / v9-4p5 model layer + dual Imagine Video 1.0 & 1.5 Native support — Cinematic Studio v4.5*
