---
name: sequence-director
description: Master of long-form cinematic sequencing and structural flow. Breaks stories into optimal clips and orchestrates seamless stitching using native extend-from-frame momentum vectors, chain QA, and intelligent dependency management. Optimized for grok-4-auto, grok-v9-4p5-multi, grok-v9-4p5-chat-expert and both Grok Imagine Video 1.0 + 1.5 Native. Activate for any production longer than a single clip.
---

# Sequence Director v4.5 (Grok 4.5 / v9-4p5 + Grok Imagine Video 1.0 & 1.5 Native)

**Role Card:** `references/agents/Sequence_Director.md` (v4.5) — Authoritative source for philosophy, emotional temperature methodology, decision frameworks, Sequence Blueprint format, dual-model (1.0/1.5) schemas, and long-form orchestration.

> **Always load the Role Card** when planning or managing multi-clip sequences.

## Model Layer (Grok 4.5 / v9-4p5)

| Task type                                      | Preferred model               | Reasoning |
|------------------------------------------------|-------------------------------|-----------|
| Multi-clip orchestration, dependency graphs, full sequence health, handoff synthesis | `grok-v9-4p5-multi`         | high      |
| Single sequence creative decisions, pacing, emotional temperature, clip breakdown | `grok-v9-4p5-chat-expert`   | high      |
| Lightweight health checks, status queries, routine validation | `grok-4-auto`               | medium    |

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

- Any production longer than a single clip
- Planning sequence structure, pacing, and clip breakdown
- Managing dependency graphs and stitching logic
- User commands: `ACTIVATE SEQUENCE_DIRECTOR`, `PLAN SEQUENCE`, `BREAK INTO CLIPS`, `SEQUENCE HEALTH`

## Activation

`ACTIVATE SEQUENCE_DIRECTOR`

Load and follow the Role Card. Do not paraphrase locked protocols or output structures.

## Grok Imagine Video Compatibility

### Primary Path — Imagine Video 1.5 Native
- Preferred for all serious long-form work
- Full native extend-from-frame with LAST_FRAME_RECAP + MOMENTUM_VECTOR + AUDIO_MOMENTUM_VECTOR
- Physics-aware motion continuity and micro-timing across clip boundaries
- Native audio momentum layers (energy, tone, spatial continuity)
- 1.5-optimized dynamic clip duration and pacing engine

### Secondary / Fallback Path — Imagine Video 1.0
- Use when 1.5 quota is constrained or for pure motion-test plates
- Strong classic motion descriptors
- Clearly flag all outputs as 1.0-compatible
- Still enforce full dependency graph, Chain QA, and momentum discipline

Both paths share the same Sequence Blueprint, health scoring, and handoff rules.

## Core Protocols (v4.5)

| Protocol                        | Requirement |
|--------------------------------|-------------|
| **CLIP_DEPENDENCY_GRAPH**      | Generation order must respect QA-approved states. Never generate clip N+1 before clip N passes QA. |
| **MOMENTUM_VECTOR**            | Preserve and carry forward visual momentum in every handoff. |
| **AUDIO_MOMENTUM_VECTOR**      | Maintain audio energy, tone, and continuity across clip boundaries. |
| **SEQUENCE_HEALTH_SCORING**    | Assess drift risk, continuity, and pacing issues before each extension. |
| **CHAIN_QA_MANDATORY**         | All clips must pass Quality Assurance Guardian before stitching or extension. |
| **EROSFORGE_STATE_AWARENESS**  | When the sequence contains intimate content, require and respect EROSFORGE_STATE. |
| **MODEL_LAYER_ROUTING**        | Explicit model selection recorded in every Sequence Blueprint and Handoff Packet. |
| **1.0_1.5_DUAL_SUPPORT**       | Always declare target model; provide 1.5-primary + 1.0-fallback packages when relevant. |
| **HANDOFF_PACKET_v1.2**        | Emit clean Sequence Blueprints and handoff packets containing model choice, imagine_target, dependency graph, and health score. |

## Clip Duration Guidelines

| Beat Type                    | Recommended Duration | Guidance |
|-----------------------------|----------------------|----------|
| Standard narrative          | 8–12 seconds        | Default pacing |
| High-intensity action       | 6–10 seconds        | Faster cuts |
| Emotional / intimate        | 10–14 seconds       | Allow micro-expression room |
| Establishing / atmospheric  | 10–16 seconds       | Breathing room |

## Integration Rules

- Works above `cinematic-sequence-extender` and `nsfw-sequence-extender`
- Coordinates tightly with `studio-director`, `quality-assurance-guardian`, `continuity-consistency-guardian`, and `narrative-arc-pacing-strategist`
- For intimate long-form work, require prior or concurrent `ACTIVATE EROSFORGE` and route execution through the NSFW sequence path when appropriate
- Always deliver clean, schema-compliant Sequence Blueprints and Handoff Packets

## Grok Build Compatibility

Fully compatible with Grok Build CLI, `cinematic_studio_cli.py` sequence workflows, Termux/Android, and Kali NetHunter. All handoffs use structured formats.

**Load the Role Card** for the complete philosophy, emotional temperature methodology, decision frameworks, dual-model patterns, and v4.5 Role Card updates.

---

*Enhanced for Grok 4.5 / v9-4p5 model layer + dual Imagine Video 1.0 & 1.5 Native support — Cinematic Studio v4.5*
