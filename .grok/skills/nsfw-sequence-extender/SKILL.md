---
name: nsfw-sequence-extender
description: NSFW sensual sequence extension from reference frame or short clip to 30-120+ seconds. Plans erotic tension curves, Grok Imagine prompt chains, extend-from-frame instructions, camera pacing, and artifact-aware chain QA. Optimized for grok-4-auto, grok-v9-4p5-multi, grok-v9-4p5-chat-expert and both Grok Imagine Video 1.0 + 1.5 Native. Integrates Cinematic Sequence Extender, ErosForge, and NSFW Quota Orchestrator. Activate with ACTIVATE NSFW_SEQUENCE_EXTENDER or when extending intimate sequences. Requires ACTIVATE EROSFORGE first.
---

# NSFW Sequence Extender v4.5 (Grok 4.5 / v9-4p5 + Grok Imagine Video 1.0 & 1.5 Native)

**Role Card:** `references/agents/NSFW_Sequence_Extender.md` (v4.5) — Authoritative source for erotic tension curves, extend-from-frame chains, dual-model (1.0/1.5) support, artifact-aware Chain QA, and EROSFORGE_STATE continuity.

> NSFW sensual sequence extension from reference frame or short clip to 30-120+ seconds.

## Model Layer (Grok 4.5 / v9-4p5)

| Task type                                      | Preferred model               | Reasoning |
|------------------------------------------------|-------------------------------|-----------|
| Multi-clip erotic sequence planning, tension curve + dependency management | `grok-v9-4p5-multi`         | high      |
| Single extension craft, camera pacing, micro-timing, artifact avoidance | `grok-v9-4p5-chat-expert`   | high      |
| Quick status / simple extension checks         | `grok-4-auto`               | medium    |

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

- Extending intimate sequences beyond a single clip
- User says `ACTIVATE NSFW_SEQUENCE_EXTENDER` or requests long-form sensual extension
- **Requires prior or concurrent `ACTIVATE EROSFORGE`**

## Activation

`ACTIVATE NSFW_SEQUENCE_EXTENDER`

Requires ErosForge. Load and follow the Role Card.

## Grok Imagine Video Compatibility

### Primary Path — Imagine Video 1.5 Native
- Preferred for high-fidelity sensual sequences
- Full support for extend-from-frame, LAST_FRAME_RECAP, momentum vectors, and native audio continuity

### Secondary / Fallback Path — Imagine Video 1.0
- Supported for cost-efficient drafts and shorter extensions
- Clearly label 1.0 vs 1.5 in Sequence Blueprints and handoffs

Both paths share the same tension-curve discipline, Chain QA, and EROSFORGE_STATE requirements.

## Core Protocols (v4.5)

| Protocol                        | Requirement |
|--------------------------------|-------------|
| **EROSFORGE_PREREQUISITE**     | Never operate without prior or concurrent ErosForge activation |
| **EROTIC_TENSION_CURVE**       | Design deliberate tension / release pacing across the sequence |
| **EXTEND_FROM_FRAME_CHAIN**    | Use native extend with LAST_FRAME_RECAP + momentum vectors |
| **ARTIFACT_AWARE_CHAIN_QA**    | Apply heightened artifact and identity checks for intimate content |
| **CAMERA_PACING**              | Control camera movement to support emotional and physical intimacy |
| **MODEL_LAYER_ROUTING**        | Explicit model selection recorded in every plan |
| **1.0_1.5_DUAL_SUPPORT**       | Declare target model; support both paths |
| **HANDOFF_PACKET**             | Sequence plans and EROSFORGE_STATE must be handoff-ready |

## Integration Rules

- Requires ErosForge
- Coordinates with NSFW Quota Orchestrator, Cinematic Sequence Extender, Identity Lock, Continuity Guardian, and QA Guardian
- Critical for any long-form intimate production

## Grok Build Compatibility

Fully compatible with Grok Build CLI, Termux/Android, and Kali NetHunter. All plans use structured formats.

**Load the Role Card** for complete sensual extension philosophy, dual-model standards, and v4.5 Role Card updates.

---

*Enhanced for Grok 4.5 / v9-4p5 model layer + dual Imagine Video 1.0 & 1.5 Native support — Cinematic Studio v4.5*
