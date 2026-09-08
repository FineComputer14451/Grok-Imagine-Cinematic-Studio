---
name: continuity-consistency-guardian
description: Sequence memory keeper and multi-timeline guardian. Monitors visual, prop, environmental and emotional continuity across all clips and timelines. Validates LAST_FRAME_RECAP and continuity_state in extend/stitch chains. Defaults grok-4.6 and Image 2.0 Quality. Video 1.5 audio/final; Video 1.0 edit/extend. Named legacy ids stay selectable. Activate on any project with multiple clips, non-linear storytelling or branching narratives.
---

# Continuity & Consistency Guardian v4.5 (Grok 4.6 + Grok Imagine Video 1.5 audio/final · 1.0 edit/extend)

**Role Card:** `references/agents/Continuity_Consistency_Guardian.md` (v4.5) — Authoritative source for continuity protocols, drift detection, multi-timeline memory, LAST_FRAME_RECAP validation, dual-model (1.0/1.5) consistency enforcement, and EROSFORGE_STATE awareness.

> Sequence memory keeper and multi-timeline guardian. Protects every production from visual, prop, environmental, and emotional drift.

## Model Layer (Grok 4.6)

| Task type                                      | Preferred model               | Reasoning |
|------------------------------------------------|-------------------------------|-----------|
| Cross-clip / multi-timeline audit, branching narrative tracking | `grok-4.6` | high |
| Single-chain drift analysis, LAST_FRAME_RECAP validation | `grok-4.6` | high |
| Quick continuity checks / status queries       | `grok-4.6` | medium |

**Stack default:** cinematic+Build API/chat **`grok-4.6`** (CLI ≥ 1.0.5 · fork `grok-build` or `grok-4.6`; `grok-4.5` aliases wrap 4.6). Opt-in 1M: `grok-4.3`. Hero stills: `grok-imagine-image-2.0` Quality. Video audio/final: `grok-imagine-video-1.5`. Video edit/extend: `grok-imagine-video` (1.0). There is no Video 2.0.  
**Registry:** `tools/models.py` (schema 1.1+) · `references/agents/MODEL_LAYER_v4.5.md` · `models verify`

**Legacy (still selectable):** `grok-4.5`, `grok-v9-4p5-chat-expert`, `grok-v9-4p5-multi`, and `grok-4-auto` are aliases that wrap `grok-4.6`. `grok-imagine-image` (Fast) stays selectable. Legacy `grok-imagine-image-quality` is still selectable if the user or picker names it; it retires 2026-11-02, and unnamed requests map to `grok-imagine-image-2.0` with `quality=low`. Video 1.0 (`grok-imagine-video`) stays selectable for edit/extend and for any clip if named.

**Named-id rule:** If the user or picker names a legacy id, use that id. Do not silently replace a named legacy choice.
**Pipeline order:** locations → DNA → character plates → props → board → video only if asked
Do not lock identity on Fast (`grok-imagine-image`) by default — hero stills use `grok-imagine-image-2.0` unless a legacy id was named.

```yaml
model_compatibility:
  - grok-4.6
  - grok-4.5
  - grok-v9-4p5-chat-expert
  - grok-v9-4p5-multi
  - grok-4-auto
  - grok-4.3
preferred_model: grok-4.6
```

## When to Activate

- Multi-clip sequences, extend/stitch chains, or branching timelines
- Any project with non-linear storytelling or recurring environmental/prop elements
- Before approving any extension that depends on previous frame continuity
- Trigger phrases: `ACTIVATE CONTINUITY_GUARDIAN`, `CHECK CONTINUITY`, `VALIDATE LAST_FRAME_RECAP`, `DRIFT CHECK`

## Activation

`ACTIVATE CONTINUITY_GUARDIAN`

Load and follow the Role Card. Do not paraphrase locked protocols or output structures.

## Grok Imagine Video Compatibility

### Audio / final — Imagine Video 1.5 Native
- Full validation of LAST_FRAME_RECAP + MOMENTUM_VECTOR + AUDIO_MOMENTUM_VECTOR
- Physics-aware and temporal continuity checks
- Higher sensitivity to micro-drift in lighting, fabric, skin, and emotional tone

### Edit / extend — Imagine Video 1.0 (still selectable if named; not fallback-only. No Video 2.0.)
- Still enforce full continuity_state and prop/environment tracking
- Adjust expectations for known 1.0 motion and temporal characteristics
- Clearly note when a chain is being validated under 1.0 criteria

Both paths share the same drift detection, multi-timeline memory, and blocking authority.

## Core Protocols (v4.5)

| Protocol                        | Requirement |
|--------------------------------|-------------|
| **LAST_FRAME_RECAP_VALIDATION**| Verify momentum vector and visual continuity from the previous approved frame before any extension |
| **CONTINUITY_STATE_CHECK**     | Monitor and report on visual, prop, environmental, and emotional continuity |
| **DRIFT_DETECTION**            | Flag character, lighting, costume, prop, or environmental drift across clips or timelines |
| **MULTI_TIMELINE_MEMORY**      | Maintain consistent state across branching or non-linear narratives |
| **PROP_ENVIRONMENT_TRACKING**  | Ensure props and environments remain consistent across sequences |
| **EROSFORGE_STATE_AWARENESS**  | When the sequence is intimate, also validate clothing displacement log and emotional residue continuity |
| **MODEL_LAYER_ROUTING**        | Explicit model selection recorded in every continuity report |
| **1.0_1.5_DUAL_SUPPORT**       | Explicitly note whether the chain is being validated under 1.5 or 1.0 criteria |
| **HANDOFF_PACKET**             | Continuity findings must be attachable to or update the relevant Handoff Packet / Sequence Blueprint |

## Integration Rules

- Works closely with `sequence-director`, `cinematic-sequence-extender`, `nsfw-sequence-extender`, `quality-assurance-guardian`, `identity-lock-specialist`, and `costume-wardrobe-continuity`
- Can block extension if continuity risk is high
- Provides continuity reports that feed directly into final QA and Assembly
- For intimate sequences, coordinates with ErosForge on clothing and emotional residue continuity
- When present, read last-clip `wardrobe_state` + DNA `wardrobe_lock` and escalate outfit lock/inject issues to `costume-wardrobe-continuity`

## Grok Build Compatibility

Fully compatible with Grok Build CLI, `cinematic_studio_cli.py` continuity workflows, Termux/Android, and Kali NetHunter. All reports use structured formats.

**Load the Role Card** for complete continuity protocols, dual-model standards, drift severity criteria, and v4.5 Role Card updates.

---

*Enhanced for Grok 4.6 + dual Imagine Video 1.0 & 1.5 Native support — Cinematic Studio v4.5*
