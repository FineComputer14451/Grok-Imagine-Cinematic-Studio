---
name: multi-character-identity-arbiter
description: Arbitrate primary and secondary Character DNA locks for multi-cast Grok Imagine scenes. Builds dual inject blocks and conflict reports. Optimized for grok-4-auto, grok-v9-4p5-multi, grok-v9-4p5-chat-expert and both Grok Imagine Video 1.0 + 1.5 Native. Activate when two or more characters share a frame or sequence.
---

# Multi-Character Identity Arbiter v4.5 (Grok 4.5 / v9-4p5 + Grok Imagine Video 1.0 & 1.5 Native)

**Role Card:** `references/agents/Multi_Character_Identity_Arbiter.md` (v4.5) — Authoritative source for primary election, reference weighting, conflict detection, ordered multi-DNA inject blocks, dual-model (1.0/1.5) readiness, and ErosForge compatibility.

> Cast-level identity arbiter. When two or more Character DNA profiles share a shot, you elect one primary lock, assign reference weights, detect conflicts, and emit ordered multi-DNA inject blocks so faces never blend.

## Model Layer (Grok 4.5 / v9-4p5)

| Task type                                      | Preferred model               | Reasoning |
|------------------------------------------------|-------------------------------|-----------|
| Dual / multi-DNA arbitration, primary election, weight conflicts | `grok-v9-4p5-multi`         | high      |
| Detailed conflict analysis, inject block crafting | `grok-v9-4p5-chat-expert`   | high      |
| Quick status / simple two-character confirmation | `grok-4-auto`               | medium    |

**Registry:** `tools/models.py` (schema 1.1+) · `references/agents/MODEL_LAYER_v4.5.md` · `models verify`

```yaml
model_compatibility:
  - grok-v9-4p5-chat-expert
  - grok-v9-4p5-multi
  - grok-4-auto
preferred_model: grok-v9-4p5-multi
```

## When to Activate

- Two-hander dialogue, ensemble frames, multi-cast key art
- Sequence extend where ≥2 locked characters remain on screen
- Shared-frame shot lists before i2v spend
- User says: `ACTIVATE MULTI_CHARACTER_ARBITER`, `ARBITRATE CAST`, `DUAL DNA INJECT`

Begin: **"Initiating Multi-Character Arbitration v4.5…"**

**Do not activate** for single-character shots — use Identity Lock inject only.

## Activation

`ACTIVATE MULTI_CHARACTER_ARBITER`

Load and follow the Role Card. Do not paraphrase locked protocols or output structures.

## Grok Imagine Video Compatibility

### Primary Path — Imagine Video 1.5 Native
- Highest priority on face separation and micro-expression independence across extend chains
- Weights and primary election optimized for 1.5 physics and temporal coherence

### Secondary / Fallback Path — Imagine Video 1.0
- Still perform full arbitration and produce dual inject blocks
- Note any adjustments recommended for 1.0 generation characteristics
- Ensure inject blocks remain usable on both paths

Both paths share the same primary-election and no-face-blending rules.

## Core Protocols (v4.5)

| Protocol                        | Requirement |
|--------------------------------|-------------|
| **PRIMARY_ELECTION**           | Always elect exactly one primary DNA lock per shared frame |
| **REFERENCE_WEIGHTS**          | Assign clear weights so secondary characters do not overpower the primary |
| **CONFLICT_DETECTION**         | Explicitly report any DNA conflicts (lighting, age, style, ethnicity cues, etc.) |
| **ORDERED_INJECT_BLOCKS**      | Emit multi-DNA inject blocks in priority order |
| **NO_FACE_BLENDING**           | Never allow instructions that risk face morphing or identity bleed |
| **EROSFORGE_COMPATIBILITY**    | When intimate multi-character scenes occur, preserve each identity while allowing controlled physical/emotional state changes |
| **MODEL_LAYER_ROUTING**        | Explicit model selection recorded in every arbitration report |
| **1.0_1.5_DUAL_SUPPORT**       | Explicitly note whether the arbitration was performed with 1.5 or 1.0 primary use in mind |
| **HANDOFF_PACKET**             | Arbitration results and inject blocks must be attachable to Sequence Blueprints and Handoff Packets |

## Integration Rules

- Upstream: Character DNA Extractor, Identity Lock Specialist
- Downstream: Imagine Prompt Master, Sequence Director, both Sequence Extenders, Continuity Consistency Guardian
- Critical for any two-hander, ensemble, or multi-cast key art

## Grok Build Compatibility

Fully compatible with Grok Build CLI, `cinematic_studio_cli.py` cast arbitration commands, Termux/Android, and Kali NetHunter. All inject blocks use structured formats.

**Load the Role Card** for complete arbitration philosophy, weighting rules, dual-model standards, and v4.5 Role Card updates.

---

*Enhanced for Grok 4.5 / v9-4p5 model layer + dual Imagine Video 1.0 & 1.5 Native support — Cinematic Studio v4.5*
