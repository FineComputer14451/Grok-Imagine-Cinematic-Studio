<p align="center">
  <img src="assets/banner.jpg" alt="Grok Imagine Cinematic Studio Banner" width="100%">
</p>

# 🎬 Grok Imagine Cinematic Studio v3.6 "Odyssey Native"

**The most advanced multi-agent cinematic production system for Grok Build + Grok 4.3 + Grok Imagine Video 1.5**

Transform any story into emotionally powerful, production-ready cinematic video with **native 1.5 image-to-video**, one-pass synchronized audio (lip-sync + SFX + ambience + music), perfect character consistency, persistent memory, and a full **23-agent** professional film crew.

[![Version](https://img.shields.io/badge/version-3.6.5-blue)](https://github.com/FineComputer14451/grok-imagine-cinematic-studio)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Grok](https://img.shields.io/badge/Grok-Build%20%2B%204.3%20%2B%201.5-purple)](https://x.ai)

---

## ✨ What's New in v3.6 "Odyssey Native"

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

### Agent & System Upgrades
- All core agents upgraded to v3.6 with 1.5-specific protocols, decision frameworks, and output formats
- Enhanced long-form sequencing (60–180s+) with low-degradation 1.5 native chaining
- Stronger emotional + audio continuity across extended sequences
- Updated CLI & Web UI with DNA, sequence, and quota tooling + live per-second cost estimation

---

## 🚀 Quick Start

### 1. Fastest: Master Prompt Activation (Recommended)
1. Copy the content of [`MASTER_PROMPT_v3.6.md`](MASTER_PROMPT_v3.6.md)
2. Paste into a new **Grok 4.3** or **Grok Build** chat (enable reasoning=medium/high for complex productions)
3. Type: `Activate Grok Imagine Cinematic Studio v3.6`

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
python tools/cinematic_studio_cli.py generate-prompt "Your story" --chat-model grok-4.3 --video-model 1.5
python tools/cinematic_studio_cli.py nsfw extend plan "Intimate Sequence" --duration 90 --profile passionate --reference "..."
python tools/cinematic_studio_cli.py nsfw plan "Hero Session" --shot "hero:Cover frame" --budget 800
```

### 3. Grok Build Plugin Marketplace (Recommended for Grok CLI)
Install the full **32-skill** suite as a Grok plugin:

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

## 🏗️ System Architecture (v3.6)

```
Studio Director v3.6 + Mega Production Architect v3.6
├── references/agents/          # Authoritative Role Cards (v3.6)
├── tools/                      # character_dna, sequence_chain, quota_optimizer, nsfw_*
├── tools/cinematic_studio_cli.py   # CLI: dna, sequence, quota, nsfw, models
├── references/MODELS_v3.6.md   # Grok Build + xAI model registry
├── web_ui/app.py                 # Streamlit frontend with 1.5 pipeline controls
├── examples/                     # Production Bible templates (v3.6 ready)
├── MASTER_PROMPT_v3.6.md         # Main activation prompt
└── .grok/skills/                 # Custom Grok skills
```

**Key v3.6 Components:**
- `references/agents/` — Single source of truth for all Role Cards (v3.6 content)
- `MASTER_PROMPT_v3.6.md` — Full v3.6 activation with 1.5 pipeline rules
- `AGENT_INDEX.md` — Quick reference + activation examples (updated for 1.5)

---

## 🎥 The 23-Agent Professional Film Crew (v3.6)

### Core Leadership
- **Studio Director v3.6** — Central commander & **1.5 video pipeline leader**
- **Mega Production Architect v3.6** — Production Bibles with VIDEO_PIPELINE_SPEC

### Visual & Camera
- **Director of Photography (DoP) v3.6** — Lighting + **1.5 physics-aware camera moves**
- **Post-Production Color Grading Supervisor v3.6**
- **Production Designer / Set Decorator v3.6**

### Story & Performance
- **Character DNA Extractor v3.6** — Forensic DNA extraction → Identity Lock handoff
- **Performance & Emotion Director v3.6** — Micro-expressions **synced to 1.5 audio beats**
- **Identity Lock Specialist v3.6** — Character DNA + **reference_image_id + 1.5 fidelity**
- **Narrative Arc & Pacing Strategist v3.6**
- **Sequence Director v3.6** — 1.5 native chaining & long-form orchestration
- **Cinematic Sequence Extender v3.6** — Low-degradation 1.5 extend/stitch

### Technical & Continuity
- **Continuity & Consistency Guardian v3.6** — Cross-clip + **1.5 physics/audio drift detection**
- **Quality Assurance Guardian v3.6**
- **Imagine Prompt Master v3.6** — **Full 1.5 Native Prompt Schema** (motion + Sound Layer)
- **Workflow & Quota Optimizer v3.6** — Per-second 1.5 video pricing + Fast mode optimization

### Audio (Now Fully 1.5 Native)
- **Sonic Architect Native Audio Virtuoso v3.6** — One-pass native audio + AUDIO_MOMENTUM_VECTOR
- **Foley Sound Design Specialist v3.6**

### Action, VFX & SFX
- **Stunt & Action Choreographer v3.6**
- **VFX & SFX Supervisor v3.6**

### Marketing & Distribution
- **Key Art & Poster Designer v3.6**
- **Trailer & Teaser Director v3.6**
- **Localization & Subtitle Specialist v3.6**

### Post-Production & Delivery
- **AI Polish Director v3.6** — Final upscale + face restoration (`ai-video-upscaler`)

### Specialist (Opt-in)
- **ErosForge NSFW Director v3.6** — Activate explicitly with `ACTIVATE EROSFORGE`

---

## 📁 Project Structure

```
Grok-Imagine-Cinematic-Studio/
├── references/agents/          # Authoritative Role Cards (v3.6)
├── examples/                     # Production Bible templates
├── tools/                        # cinematic_studio_cli.py
├── web_ui/                       # Streamlit app
├── MASTER_PROMPT_v3.6.md
├── AGENT_INDEX.md
├── Quick_Start_Guide.md
└── RELEASE_NOTES_v3.6.md        # New in v3.6
```

---

## 🔗 Useful Links

- [Quick Start Guide](Quick_Start_Guide.md)
- [Agent Index (v3.6)](references/agents/AGENT_INDEX.md)
- [Production Bible Template](Project_Bible_Template.md)
- [CHANGELOG](CHANGELOG.md)
- [RELEASE_NOTES_v3.6.md](RELEASE_NOTES_v3.6.md) ← New

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

*Grok Imagine Cinematic Studio v3.6 "Odyssey Native" — Built for Grok Build, Grok 4.3, and Imagine Video 1.5*

*Last updated: June 21, 2026 — v3.6.4*