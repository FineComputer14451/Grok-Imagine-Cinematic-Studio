---
name: extend-frame-to-video
description: Create cinematic rough-cut animatics and storyboards from Grok Imagine still sequences using Extend from Frame prompting + advanced FFmpeg assembly (v2.0+). Optimized for grok-4-auto, grok-v9-4p5-multi, grok-v9-4p5-chat-expert and both Grok Imagine Video 1.0 + 1.5 Native. Features proper crossfades/wipes, cinematic filters (grain, vignette, color grade), dynamic Ken Burns, storyboard PDF export, enhanced EDL, and professional metadata. Perfect for client previews and pre-viz before full cinematic studio.
---

# Extend Frame to Video v4.5 (Grok 4.5 / v9-4p5 + Grok Imagine Video 1.0 & 1.5 Native)

**Role Card:** `references/agents/Extend_Frame_to_Video.md` (v4.5) — Authoritative source for extend-from-frame protocols, dual-model (1.0/1.5) support, project.json integration, Handoff Packet generation, and FFmpeg assembly standards.

> Create cinematic rough-cut animatics and storyboards from Grok Imagine still sequences.

## Model Layer (Grok 4.5 / v9-4p5)

| Task type                                      | Preferred model               | Reasoning |
|------------------------------------------------|-------------------------------|-----------|
| Complex multi-clip assembly planning, EDL + storyboard synthesis | `grok-v9-4p5-multi`         | high      |
| Single-sequence extend planning, prompt crafting, Ken Burns design | `grok-v9-4p5-chat-expert`   | high      |
| Quick status / simple assembly checks          | `grok-4-auto`               | medium    |

**Registry:** `tools/models.py` (schema 1.1+) · `references/agents/MODEL_LAYER_v4.5.md` · `models verify`

```yaml
model_compatibility:
  - grok-v9-4p5-chat-expert
  - grok-v9-4p5-multi
  - grok-4-auto
preferred_model: grok-v9-4p5-multi
```

## When to Activate

- Creating rough-cut animatics or storyboards from still sequences
- Pre-visualization before full cinematic video spend
- Client preview packages requiring Ken Burns, crossfades, and professional assembly
- Trigger phrases: `ACTIVATE EXTEND_FRAME_TO_VIDEO`, `ASSEMBLE ROUGH CUT`, `STORYBOARD FROM STILLS`

## Activation

`ACTIVATE EXTEND_FRAME_TO_VIDEO`

Load and follow the Role Card. Do not paraphrase locked protocols or output structures.

## Grok Imagine Video Compatibility

### Primary Path — Imagine Video 1.5 Native
- Preferred for high-fidelity extend-from-frame chains
- Full support for LAST_FRAME_RECAP, momentum vectors, and native audio continuity

### Secondary / Fallback Path — Imagine Video 1.0
- Fully supported for cost-efficient pre-viz and draft animatics
- Clearly label 1.0 vs 1.5 outputs in project manifests and EDLs

Both paths share the same FFmpeg assembly pipeline, project.json schema, and Handoff Packet structure.

## Core Protocols (v4.5)

| Protocol                        | Requirement |
|--------------------------------|-------------|
| **PROJECT_JSON_SUPPORT**       | Accept and generate project.json for declarative assembly |
| **HANDOFF_PACKET_GENERATION**  | Produce clean Handoff Packets for downstream Sequence / Studio agents |
| **DUAL_MODEL_ROUTING**         | Explicitly declare 1.5 vs 1.0 target for every clip package |
| **FFMPEG_ASSEMBLY_v2.2**       | Use advanced crossfades, Ken Burns, grain, vignette, and color grade |
| **STORYBOARD_PDF**             | Optional professional PDF export of the assembled sequence |
| **EDL_EXPORT**                 | Enhanced Edit Decision List for professional handoff |
| **MODEL_LAYER_ROUTING**        | Record model choice in every assembly report |
| **1.0_1.5_DUAL_SUPPORT**       | Support both Imagine Video versions without workflow breakage |

## Integration Rules

- Upstream: Imagine Prompt Master, Reference Asset Curator, Character DNA / Identity Lock
- Downstream: Sequence Director, Cinematic Sequence Extender, QA Guardian, Assembly Editor
- Critical for pre-viz and client-facing rough cuts before heavy video spend

## Grok Build Compatibility

Fully compatible with Grok Build CLI, scripts/assemble-rough.sh, generate-handoff.py, Termux/Android, and Kali NetHunter.

**Load the Role Card** for complete protocols, dual-model standards, and v4.5 Role Card updates.

---

*Enhanced for Grok 4.5 / v9-4p5 model layer + dual Imagine Video 1.0 & 1.5 Native support — Cinematic Studio v4.5*
