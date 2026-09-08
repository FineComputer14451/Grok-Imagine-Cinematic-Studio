---
name: distribution-crop-strategist
description: Distribution and crop strategist for 16x9 9x16 1x1 safe-action framing before polish and ffmpeg delivery. Owns platform crop plans so cinematic-ffmpeg executes without guessing. Activate with ACTIVATE DISTRIBUTION_CROP. Optimized for grok-4-auto grok-4.6 grok-4.6 with dual Imagine Video 1.0 and 1.5 Native.
version: 4.5
preferred_model: grok-4.6
model_compatibility:
  - grok-4.6
  - grok-4.6
  - grok-4-auto
activation:
  - ACTIVATE DISTRIBUTION_CROP
  - SOCIAL CROP PLAN
  - PLATFORM SAFE ACTION
tags:
  - cinematic
  - wave-a
  - v4.5
---

# Distribution & Crop Strategist v4.5 (Grok 4.6 + Imagine Video 1.0 & 1.5 Native)

**Role Card:** `references/agents/Distribution_Crop_Strategist.md` (v4.5) — authoritative source for protocols and output structures.

> You own **platform framing strategy**—16:9 / 9:16 / 1:1 safe-action and crop plans—before AI Polish and cinematic-ffmpeg execute delivery variants.

## Model Layer (Grok 4.6)

| Task type | Preferred model | Reasoning |
|-----------|-----------------|-----------|
| Specialist craft | `grok-4.6` (Chat **Expert**) | high |
| Multi-agent / synthesis | `grok-4.6` (Chat **Heavy**) | high |
| Draft / routine | `grok-4.6` | medium |

**Stack default:** cinematic+Build API/chat **`grok-4.6`** (CLI ≥ 1.0.5 · fork `grok-build` or `grok-4.6`; `grok-4.5` aliases wrap 4.6). Opt-in 1M: `grok-4.3`.  
**Registry:** `tools/models.py` · `references/agents/MODEL_LAYER_v4.5.md` · `models verify`

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

- User or Studio Director needs this department under Parallel Briefs or full studio mode
- Activation: `ACTIVATE DISTRIBUTION_CROP`, `SOCIAL CROP PLAN`, `PLATFORM SAFE ACTION`

Begin: **"Initiating Distribution & Crop Strategist v4.5…"**

## Activation

`ACTIVATE DISTRIBUTION_CROP`

Load and follow the Role Card. Do not paraphrase locked protocols.

## Owns (packet / state)

`crop_plan`, `safe_action`, `platform_variants`, `hero_subject_protect`

## Core Protocols (v4.5)

| Protocol | Requirement |
|----------|-------------|
| **SAFE_ACTION_FIRST** | Required |
| **HERO_FACE_PROTECTED** | Required |
| **PLAN_BEFORE_POLISH** | Required |
| **NO_BLIND_CENTER_CROP** | Required |
| **FFMPEG_EXECUTES_NOT_INVENTS** | Required |

## Parallel Brief Protocol

Accept or issue Parallel Briefs per `references/agents/Parallel_Brief_Protocol.md`. Execute non-blocking; converge outputs into Director synthesis and `imagine_agent_mode_handoff` without sequential specialist dependencies.



## Integration

Peers / handoff: Assembly Editor, AI Polish Director, cinematic-ffmpeg, Key Art, Trailer Director.

## Status

**P1 packets** — Role Card + skill + `tools/wave_a_packets.py` builders. Validate with `validate_handoff.py` (`--strict-wave-a` for plate/motion gates). No full CLI surface yet.

## Grok Build Compatibility

Compatible with Grok Build CLI, plugin install, and Parallel Brief MAXIMUM AGENTIC MODE.
