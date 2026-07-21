# Grok Imagine Cinematic Studio — UPGRADE GUIDE

**Current target:** **v3.7.1** — unified **Grok 4.5** cinematic+Build · optional **Grok 4.3** 1M · Imagine Agent Mode Handoff · Imagine Video 1.0/1.5

**Date:** July 10, 2026

---

## Upgrade to v3.7.1 (from v3.6.7)

1. Pull / reinstall the repo or run `bash scripts/cinematic_studio.sh update` / `grok plugin update grok-imagine-cinematic-studio`
2. Confirm `VERSION` is **3.7.1** and `python tools/cinematic_studio_cli.py models verify` shows Grok **4.5** cinematic+Build
3. Set `~/.grok/config.toml` defaults: `[models] default = "grok-4.5"` · `[ui] fork_secondary_model = "grok-build"`
4. Activation phrase: `Activate Grok Imagine Cinematic Studio v3.8.6`
5. Read `references/agents/MODEL_LAYER_v3.7.1.md` and `references/agents/IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md`
6. Re-pin plugin catalog after skill edits: `cinematic-studio plugin catalog pin`

### What changed for Grok 4.5
- Orchestration default remains **`grok-4.5`** (not dual-stack 4.3 cinematic)
- All skills/Role Cards embed Model Layer **Grok 4.5 · studio v3.7.1**
- Imagine Agent Mode Handoff standardizes generation surfaces
- Alias `cinematic` → `grok-4.5`; use `long-context` / `grok-4.3` only for 1M Bibles

---

## From v3.5 → v3.6 "Odyssey Native" (background)

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
- `MASTER_PROMPT.md` (new main activation prompt)
- `README.md` (fully updated)
- `docs/releases/RELEASE_NOTES_v3.7.1.md` (new)
- `AGENT_INDEX.md` (updated with 1.5 examples)
- All core Role Cards in `references/agents/` upgraded to v3.6 content (clean filenames)

### 7. Plugin Catalog CLI (v3.6.5+ Refinement)
The plugin index and marketplace catalog system has been modernized for better maintainability:

- **Canonical logic** moved to `tools/plugin_catalog.py`
- New dedicated CLI commands:
  - `cinematic-studio plugin catalog pin` — regenerate + pin SHA to current HEAD
  - `cinematic-studio plugin catalog check [--release]` — verify freshness or run pre-publish gate
  - `cinematic-studio plugin status` / `list`
- `scripts/generate_plugin_index.py` is now a **thin pure-generation wrapper** only (no more `--sync-sha` / `--check` flags)
- `scripts/release_plugin_catalog.sh` and `verify_plugins.sh` are thin shims that delegate to the CLI
- Strong enforcement of **atomic commits** (feature changes + `.grok-plugin/` files in the same commit)
- Old direct script + flag workflows are deprecated in favor of the integrated `cinematic-studio` commands

This makes plugin maintenance consistent with the rest of the CLI surface.

---

## Migration Steps

### Step 1: Switch to the v3.6 Branch (Recommended)
```bash
git checkout main
```
Or simply use the latest `MASTER_PROMPT.md` in a new chat.

### Step 1b: Unified Grok 4.5 stack (v3.6.6+) + Grok Build CLI
```bash
grok --version   # recommend ≥ 0.2.93
python tools/cinematic_studio_cli.py models verify
```
- **Cinematic / Bible:** `grok-4.5` (default chat); `grok-4.3` for 1M opt-in
- **Build / coding / agent sessions:** `grok-4.5` (CLI + build API default)
- See `references/MODELS_v3.6.md` and `config/grok-build.example.toml`

### Step 2: Activate the New Studio
In a new **Grok 4.5** chat (default) or **Grok 4.3** for very long Bibles, paste `MASTER_PROMPT.md` and type:
```
Activate Grok Imagine Cinematic Studio v3.8.6
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
- Activate `Sonic Architect v3.6` early when native audio is important
- Use new Director’s Notes metrics to evaluate 1.5 quality

### Step 6: Plugin Catalog Maintenance (Post-v3.6)
If you contribute to or maintain the Grok plugin:
1. Commit **content** first (skills, commands, tools, docs)
2. Run `cinematic-studio plugin catalog pin` (regenerate + pin install SHA)
3. Commit **only** `.grok-plugin/` (pin-only follow-up is expected; a commit cannot embed its own hash)
4. Pre-publish: `cinematic-studio plugin catalog check --release` (green when pin == HEAD **or** pin is ancestor with only catalog paths after it)

### Step 7: Guided Production Bible Wizard (v3.7.1)
Optional multi-step Bible creation (same JSON shape as direct `create-bible`):
```bash
cinematic-studio create-bible --wizard          # TTY only; scripts keep create-bible "Title"
# Web UI: Production → Guided Bible Creator
```
Free-text logline/characters/world/tech notes roll into `notes`. Stages live in `tools/cli/bible_stages.py`.

---

## Breaking Changes

- Old activation commands remain supported, but new 1.5-specific commands are strongly recommended for best results.
- The system now defaults to **v3.6 behavior** when using `MASTER_PROMPT.md`.
- Some prompt structures have been optimized for 1.5 (slightly different emphasis on motion/physics/audio layers).

**No breaking changes** to core functionality — all previous v3.5 workflows continue to work.

**Plugin catalog tooling** (v3.6.5+): The old direct `python scripts/generate_plugin_index.py --sync-sha` / `--check` interface has been replaced by `cinematic-studio plugin catalog` subcommands. The generator script is now a thin pure-generation wrapper only. See `AGENTS.md` for the current recommended process.

---

## Recommended New Workflow (v3.7.1)

1. **Primary Activation** — `Activate Grok Imagine Cinematic Studio v3.8.6` or `ACTIVATE IMAGINE_VIDEO_1.5_FULL`
2. **Production Bible** — `create-bible "Title"` (scripts) or `create-bible --wizard` (guided TTY) / Web Guided Bible Creator
3. **Use VIDEO_PIPELINE_SPEC** — 1.0 cost default; 1.5 when native audio is required
4. **Activate Sonic Architect early** when native audio is important
5. **Reference Role Cards** in `references/agents/` for 1.5 + Grok 4.5 Model Layer guidance
6. **Handoff protocols** — AUDIO_MOMENTUM_VECTOR and reference_image_id on long sequences
7. **Plugin catalog (if contributing)** — content commit → `catalog pin` → catalog-only commit → `check --release`

---

## Need Help?

- See `MASTER_PROMPT.md` for the complete v3.6.7 activation prompt
- See `docs/releases/RELEASE_NOTES_v3.7.1.md` for the full changelog
- See `references/agents/AGENT_INDEX.md` for activation examples and power commands
- See individual Role Cards in `references/agents/` for 1.5 integration notes
- See `Quick_Start_Guide.md` and `installation_guide.md` for install paths
- See `commands/validate.md` and `AGENTS.md` for plugin catalog CLI usage and release process

---

**Welcome to Grok Imagine Cinematic Studio v3.7.1 "Odyssey Native"!**

Unified Grok 4.5 cinematic+Build (optional 4.3 1M), guided Bible wizard, plugin marketplace, and native 1.5 video + audio.

*Upgrade guide updated — July 10, 2026 (v3.6.7 · unified Grok 4.5)*