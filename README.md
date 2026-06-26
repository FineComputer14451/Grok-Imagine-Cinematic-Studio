<p align="center">
  <img src="assets/banner.jpg" alt="Grok Imagine Cinematic Studio Banner" width="100%">
</p>

# 🎬 Grok Imagine Cinematic Studio v3.6.5 "Odyssey Native"

**The most advanced multi-agent cinematic production system for Grok Build + Grok 4.3 + Grok Imagine Video (1.0 default; 1.5 native audio available)**

Transform any story into emotionally powerful, production-ready cinematic video with **Imagine Video 1.0** ($0.05/sec) or **1.5 native image-to-video** with one-pass synchronized audio (lip-sync + SFX + ambience + music), perfect character consistency, persistent memory, and a full **23-agent** professional film crew.

[![Version](https://img.shields.io/badge/version-3.6.5-blue)](https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Grok](https://img.shields.io/badge/Grok-Build%20%2B%204.3%20%2B%20Imagine-purple)](https://x.ai)

---

## ✨ What's New in v3.6.5 "Odyssey Native"

### Grok Imagine Video 1.5 Native Integration
- **Full native image-to-video** with dramatically improved motion, physics, and consistency
- **One-pass synchronized native audio** (lip-synced dialogue + SFX + ambience + music cues)
- **VIDEO_PIPELINE_SPEC** — Locked variable for model, resolution (720p), clip length (6–15s), native_audio, extend/stitch strategy
- **AUDIO_MOMENTUM_VECTOR** — New handoff protocol carrying dialogue state, SFX timing, emotional tone of audio, and music cue points alongside visual momentum
- **reference_image_id propagation** + 1.5 fidelity scoring in Identity Lock & Continuity systems
- New Director’s Notes metrics: **Audio-Visual Sync Fidelity** and **Physics Realism** (1–10)
- Optimized prompting rules for 1.5 (explicit camera moves with weighty physics, timing beats, Sound Layer syntax)
- Per-second xAI pricing ($0.08/sec for 1.5) + Fast mode → quality pass strategies
- **Model registry** — `tools/models.py`, `models list` CLI, Grok Build + xAI slug reference

### v3.6.1–3.6.4 Production Pipelines
- **Character DNA pipeline** — `dna` CLI commands, Identity Lock handoff, prompt injection
- **Long-form sequence chain** — `sequence` CLI, 10-point chain QA gates, 1.5 extend/stitch protocols
- **Quota orchestration** — `quota` CLI, xAI per-second pricing, session budgeting, Fast mode optimization
- **AI Polish Director** — final delivery upscale via `ai-video-upscaler` skill
- **Model registry** (v3.6.2) — `tools/models.py`, Grok Build + xAI slug reference
- **NSFW Quota Orchestrator** (v3.6.3) — Heavy batch planning, i2v decisions, daily reports
- **NSFW Sequence Extender** (v3.6.4) — 30–120s+ sensual extension, prompt chains, erotic pacing, artifact QA

### v3.6.5 — Plugin Marketplace, Model Verification & Refinements (2026-06)
- **Grok plugin marketplace** — `.grok-plugin/marketplace.json`, `plugin.json`, `plugin-index.json` (44 skills + commands) for `grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio`
- **Imagine 1.0 as default** — `grok-imagine-video` ($0.05/sec); 1.5 remains available for native-audio workflows
- **`models verify`** CLI — validates full Grok 4.3 + Imagine 1.0/1.5 + Grok Build registry compatibility
- **CLI modularization** — extracted `tools/cli/{models,bible,studio,production,...}_commands.py`; slimmer main entrypoint
- **Canonical project state** — `tools/project_state.py` with auto-merge legacy support
- **Model stack everywhere** — `VIDEO_PIPELINE_SPEC` + `model_stack_summary()` wired into CLI, Web UI, DNA/sequence handoffs, Production Bibles
- **Repo hygiene** — removed deprecated `agents/` dir, stale skill mirrors, duplicate MASTER_PROMPT; CI updated
- **Role Cards & skills** — Mega Production Architect, Imagine Prompt Master, Studio Director, etc. updated with model table and 1.5 fidelity
- **Quick Start Guide & Project Bible template** updated with model stack section and Grok Build config example

### Agent & System Upgrades
- All core agents at v3.6.5 with 1.5-specific protocols, decision frameworks, and output formats
- Enhanced long-form sequencing (60–180s+) with low-degradation 1.5 native chaining
- Stronger emotional + audio continuity across extended sequences
- Updated CLI & Web UI with DNA, sequence, quota, NSFW, and model selection tooling + live per-second cost estimation + plugin install support

---

## 🚀 Quick Start

### 1. Fastest: Master Prompt Activation (Recommended)
1. Copy the content of [`MASTER_PROMPT_v3.6.md`](MASTER_PROMPT_v3.6.md)
2. Paste into a new **Grok 4.3** or **Grok Build** chat (enable reasoning=medium/high for complex productions)
3. Type: `Activate Grok Imagine Cinematic Studio v3.6.5`

### 2. Python CLI (Power Users)
```bash
pip install -r requirements.txt
python tools/cinematic_studio_cli.py --help

# Examples
python tools/cinematic_studio_cli.py status
python tools/cinematic_studio_cli.py create-bible "Your Project Title"
python tools/cinematic_studio_cli.py dna init "Elena Voss" --core "..." --facial "..."
python tools/cinematic_studio_cli.py sequence init "Neon Alley Chase" --duration 90
python tools/cinematic_studio_cli.py models list
python tools/cinematic_studio_cli.py models verify
python tools/cinematic_studio_cli.py quota estimate --duration 90 --clips 9 --fast-mode
python tools/cinematic_studio_cli.py generate-prompt "Your story" --chat-model grok-4.3 --video-model 1.0
python tools/cinematic_studio_cli.py nsfw extend plan "Intimate Sequence" --duration 90 --profile passionate --reference "..."
python tools/cinematic_studio_cli.py nsfw plan "Hero Session" --shot "hero:Cover frame" --budget 800
```

### 3. Grok Build Plugin Marketplace (Recommended for Grok CLI)
Install the full Grok plugin suite (**44 skills** + 11 slash commands) as a Grok plugin:

```bash
# Install directly from GitHub (simplest)
grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio --trust

# Or add as a marketplace source and install by name
grok plugin marketplace add FineComputer14451/Grok-Imagine-Cinematic-Studio
grok plugin install grok-imagine-cinematic-studio@finecomputer14451/grok-imagine-cinematic-studio --trust

# Optional: refresh after updates
grok plugin marketplace update
grok plugin update grok-imagine-cinematic-studio
```

Catalog lives in `.grok-plugin/marketplace.json`. Regenerate the component index after skill changes:

```bash
python3 scripts/generate_plugin_index.py
```

### 4. Streamlit Web UI
```bash
pip install -r requirements-streamlit.txt
streamlit run web_ui/app.py
```
(Imagine video model selector, xAI chat model picker (`grok-4.3` / `grok-build-0.1`), live per-second cost simulator)

---

## 🏗️ System Architecture (v3.6.5)

```
Studio Director v3.6.5 + Mega Production Architect v3.6.5
├── .grok-plugin/                 # Marketplace + plugin manifests (44 skills)
├── references/agents/            # Authoritative Role Cards (v3.6.5) + AGENT_INDEX.md
├── tools/                        # character_dna, sequence_chain, quota_optimizer, nsfw_*, models.py
├── tools/cinematic_studio_cli.py   # CLI: dna, sequence, quota, nsfw, models, verify
├── references/MODELS_v3.6.md   # Grok Build + xAI model registry
├── web_ui/app.py                 # Streamlit frontend with 1.5 pipeline + model pickers
├── examples/                     # Production Bible templates (v3.6.5 ready)
├── MASTER_PROMPT_v3.6.md         # Main activation prompt
├── scripts/                      # installers, plugin index generator
└── .grok/skills/                 # 44 Custom Grok skills (primary runtime)
```

**Key v3.6.5 Components:**
- `references/agents/` — Single source of truth for all Role Cards (v3.6.5 content)
- `MASTER_PROMPT_v3.6.md` — Full v3.6.5 activation with 1.5 native pipeline rules + model stack
- `references/agents/AGENT_INDEX.md` — Quick reference + 16 activation presets (updated for 1.5 + plugin)
- `.grok-plugin/` — Grok Marketplace support for `grok plugin install` + generated index

---

## 🎥 The 23-Agent Professional Film Crew (v3.6.5)

### Core Leadership
- **Studio Director v3.6.5** — Central commander & **1.5 video pipeline leader**
- **Mega Production Architect v3.6.5** — Production Bibles with VIDEO_PIPELINE_SPEC

### Visual & Camera
- **Director of Photography (DoP) v3.6.5** — Lighting + **1.5 physics-aware camera moves**
- **Post-Production Color Grading Supervisor v3.6.5**
- **Production Designer / Set Decorator v3.6.5**

### Story & Performance
- **Character DNA Extractor v3.6.5** — Forensic DNA extraction → Identity Lock handoff
- **Performance & Emotion Director v3.6.5** — Micro-expressions **synced to 1.5 audio beats**
- **Identity Lock Specialist v3.6.5** — Character DNA + **reference_image_id + 1.5 fidelity**
- **Narrative Arc & Pacing Strategist v3.6.5**
- **Sequence Director v3.6.5** — 1.5 native chaining & long-form orchestration
- **Cinematic Sequence Extender v3.6.5** — Low-degradation 1.5 extend/stitch

### Technical & Continuity
- **Continuity & Consistency Guardian v3.6.5** — Cross-clip + **1.5 physics/audio drift detection**
- **Quality Assurance Guardian v3.6.5**
- **Imagine Prompt Master v3.6.5** — **Full 1.5 Native Prompt Schema** (motion + Sound Layer)
- **Workflow & Quota Optimizer v3.6.5** — Per-second 1.5 video pricing + Fast mode optimization

### Audio (Now Fully 1.5 Native)
- **Sonic Architect Native Audio Virtuoso v3.6.5** — One-pass native audio + AUDIO_MOMENTUM_VECTOR
- **Foley Sound Design Specialist v3.6.5**

### Action, VFX & SFX
- **Stunt & Action Choreographer v3.6.5**
- **VFX & SFX Supervisor v3.6.5**

### Marketing & Distribution
- **Key Art & Poster Designer v3.6.5**
- **Trailer & Teaser Director v3.6.5**
- **Localization & Subtitle Specialist v3.6.5**

### Post-Production & Delivery
- **AI Polish Director v3.6.5** — Final upscale + face restoration (`ai-video-upscaler`)

### Specialist (Opt-in)
- **ErosForge NSFW Director v3.6.5** — Activate explicitly with `ACTIVATE EROSFORGE`

---

## 📁 Project Structure

```
Grok-Imagine-Cinematic-Studio/
├── .grok-plugin/                 # Grok plugin manifests (marketplace.json, plugin.json, generated index)
├── references/agents/            # Authoritative Role Cards (v3.6.5) + AGENT_INDEX.md
├── examples/                     # Production Bible templates (v3.6.5 ready)
├── tools/                        # cinematic_studio_cli.py + cli/ submodules + models.py
├── web_ui/                       # Streamlit dashboard (1.5 model pickers, quota sim)
├── scripts/                      # install/verify/update + generate_plugin_index.py
├── commands/                     # Slash command docs for Grok (cinematic, dna, nsfw, etc.)
├── MASTER_PROMPT_v3.6.md
├── Quick_Start_Guide.md
├── RELEASE_NOTES_v3.6.md
├── CHANGELOG.md
└── AGENTS.md                     # Agent/coding guidelines (this workspace)
```

---

## 🔗 Useful Links

- [Quick Start Guide](Quick_Start_Guide.md)
- [Agent Index (v3.6.5)](references/agents/AGENT_INDEX.md)
- [Production Bible Template](Project_Bible_Template.md)
- [CHANGELOG](CHANGELOG.md)
- [RELEASE_NOTES_v3.6.md](RELEASE_NOTES_v3.6.md)
- [Upgrade Guide](UPGRADE_GUIDE.md)
- [Slash Commands Reference](commands/) — for cinematic, dna, nsfw, quota, validate etc. inside Grok

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

*Grok Imagine Cinematic Studio v3.6.5 "Odyssey Native" — Built for Grok Build, Grok 4.3, and Imagine Video 1.5*

*Last updated: June 26, 2026 — v3.6.5*
