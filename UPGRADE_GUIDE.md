# Grok Imagine Cinematic Studio — UPGRADE GUIDE

**From v3.5 → v3.6 "Odyssey Native"**

**Date:** June 20, 2026

**Focus:** Full native integration with **Grok Imagine Video 1.5** + Grok 4.3 Full optimizations

---

## Overview

This guide helps you upgrade from **v3.5** to **v3.6 "Odyssey Native"**. The v3.6 update brings the biggest leap in cinematic quality since the studio’s launch by adding deep, native support for **Grok Imagine Video 1.5** (image-to-video with one-pass synchronized audio, improved physics, and low-degradation chaining).

---

## What’s New in v3.6

### 1. Grok Imagine Video 1.5 Native Integration (Major)
- Full support for native image-to-video generation
- **One-pass synchronized native audio** (lip-synced dialogue + SFX + ambience + music cues)
- Dramatically improved motion physics, weight, and consistency
- Reduced quality loss on video extension and stitching

### 2. New Core Protocols
- **`VIDEO_PIPELINE_SPEC`** — Locked variable in every Production Bible
  - `model="grok-imagine-video-1.5"`
  - `resolution="720p"` (or 480p)
  - Preferred clip length 6–15s (optimal 8–12s)
  - `native_audio=true`
  - `extend_from_last=true` / `stitch_to_previous=true`
- **`AUDIO_MOMENTUM_VECTOR`** — New handoff protocol (carries dialogue state, SFX timing, emotional tone of audio, music cue points)
- **`reference_image_id` propagation** + 1.5 fidelity scoring in Identity Lock & Continuity systems

### 3. New Quality Metrics
Director’s Notes now include two new scores:
- **Audio-Visual Sync Fidelity** (1–10)
- **Physics Realism** (1–10)

### 4. Agent Upgrades (All Core Agents to v3.6)
Every major agent has been updated with 1.5-specific:
- Prompt schemas and decision frameworks
- Handoff packets (now include AUDIO_MOMENTUM_VECTOR and reference_image_id)
- Output formats
- Activation commands and power modes

**Key updated agents include:**
- Studio Director & Mega Production Architect (1.5 pipeline leadership + VIDEO_PIPELINE_SPEC)
- Imagine Prompt Master (full 1.5 Native Prompt Schema + Sound Layer syntax)
- Director of Photography (1.5 camera moves with physics descriptors)
- Sequence Director & Cinematic Sequence Extender (native 1.5 chaining + AUDIO_MOMENTUM_VECTOR)
- Identity Lock Specialist & Continuity Guardian (reference_image_id + 1.5 fidelity + physics drift detection)
- Performance & Emotion Director (micro-expressions synced to 1.5 audio beats)
- Sonic Architect (one-pass native audio + AUDIO_MOMENTUM_VECTOR creation)
- Workflow & Quota Optimizer (per-second 1.5 video pricing + Fast mode optimization)

### 5. New Activation Commands
- `ACTIVATE IMAGINE_VIDEO_1.5_FULL`
- `GENERATE_NATIVE_AUDIO_SEQUENCE`
- `STITCH_WITH_AUDIO_SYNC`
- `1.5 NATIVE CHAINING`
- `1.5 PHYSICS-AWARE CAMERA MOVES`
- `1.5 AUDIO-SYNCED MICRO-EXPRESSIONS`

### 6. Documentation Updates
- `MASTER_PROMPT_v3.6.md` (new main activation prompt)
- `README.md` (fully updated)
- `RELEASE_NOTES_v3.6.md` (new)
- `AGENT_INDEX.md` (updated with 1.5 examples)
- All core Role Cards in `references/agents/` upgraded to v3.6 content

---

## Migration Steps

### Step 1: Switch to the v3.6 Branch (Recommended)
```bash
git checkout v3.6-imagine-video-1.5-native
```
Or simply use the latest `MASTER_PROMPT_v3.6.md` in a new chat.

### Step 2: Activate the New Studio
In a new Grok 4.3 Full chat, paste `MASTER_PROMPT_v3.6.md` and type:
```
Activate Grok Imagine Cinematic Studio v3.6
```

Or use the powerful new mode:
```
ACTIVATE IMAGINE_VIDEO_1.5_FULL
```

### Step 3: Update Existing Projects (Recommended)
For ongoing projects:
1. Say: `"Update Project Bible to v3.6 standards"`
2. Re-activate key agents (especially Imagine Prompt Master, Sonic Architect, Cinematic Sequence Extender)
3. Add `VIDEO_PIPELINE_SPEC` to your existing Bible
4. Run `RUN QA REVIEW` with focus on 1.5 audio-visual sync and physics

### Step 4: Explore the New Role Cards
Browse `references/agents/` — all major cards now contain dedicated **v3.6 / 1.5 Integration** sections with updated protocols, decision frameworks, and output formats.

### Step 5: Start Using 1.5-Specific Features
- Use `VIDEO_PIPELINE_SPEC` in every new Production Bible
- Include `AUDIO_MOMENTUM_VECTOR` in handoffs for long sequences
- Activate `Sonic Architect v3.6` early when native audio matters
- Use new Director’s Notes metrics to evaluate 1.5 quality

---

## Breaking Changes

- Old activation commands remain supported, but new 1.5-specific commands are strongly recommended for best results.
- The system now defaults to **v3.6 behavior** when using `MASTER_PROMPT_v3.6.md`.
- Some prompt structures have been optimized for 1.5 (slightly different emphasis on motion/physics/audio layers).

**No breaking changes** to core functionality — all previous v3.5 workflows continue to work.

---

## Recommended New Workflow (v3.6)

1. **Primary Activation** — Start with `Activate Grok Imagine Cinematic Studio v3.6` or `ACTIVATE IMAGINE_VIDEO_1.5_FULL`
2. **Use VIDEO_PIPELINE_SPEC** — Define your 1.5 parameters early in the Bible
3. **Activate Sonic Architect early** when native audio is important
4. **Reference updated Role Cards** in `references/agents/` for 1.5-specific guidance
5. **Use new handoff protocols** — Include AUDIO_MOMENTUM_VECTOR and reference_image_id

---

## Need Help?

- See `MASTER_PROMPT_v3.6.md` for the complete v3.6 activation prompt
- See `RELEASE_NOTES_v3.6.md` for the full changelog
- See `AGENT_INDEX.md` for updated activation examples and 1.5 power commands
- See individual Role Cards in `references/agents/` for detailed 1.5 integration notes

---

**Welcome to Grok Imagine Cinematic Studio v3.6 "Odyssey Native"!**

This release brings native 1.5 video + audio capabilities that dramatically raise the bar for cinematic quality and emotional impact.

*Upgrade completed — June 20, 2026*