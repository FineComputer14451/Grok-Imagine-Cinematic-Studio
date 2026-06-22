<p align="center">
  <img src="assets/banner.jpg" alt="Grok Imagine Cinematic Studio Banner" width="100%">
</p>

# 🎬 Grok Imagine Cinematic Studio v3.6 "Odyssey Native"

**The most advanced multi-agent cinematic production system for Grok 4.3 Full + Grok Imagine Video 1.5**

Transform any story into emotionally powerful, production-ready cinematic video with **native 1.5 image-to-video**, one-pass synchronized audio (lip-sync + SFX + ambience + music), perfect character consistency, persistent memory, and a full **23-agent** professional film crew.

[![Version](https://img.shields.io/badge/version-3.6.1-blue)](https://github.com/FineComputer14451/grok-imagine-cinematic-studio)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Grok](https://img.shields.io/badge/Grok-4.3%20%2B%201.5-purple)](https://x.ai)

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
- Per-second 1.5 video quota modeling + Fast mode → quality pass strategies

### v3.6.1 Production Pipelines (New)
- **Character DNA pipeline** — `dna` CLI commands, Identity Lock handoff, prompt injection
- **Long-form sequence chain** — `sequence` CLI, 10-point chain QA gates, 1.5 extend/stitch protocols
- **Quota orchestration** — `quota` CLI, per-second 1.5 pricing, session budgeting, Fast mode optimization
- **AI Polish Director** — final delivery upscale via `ai-video-upscaler` skill

### Agent & System Upgrades
- All core agents upgraded to v3.6 with 1.5-specific protocols, decision frameworks, and output formats
- Enhanced long-form sequencing (60–180s+) with low-degradation 1.5 native chaining
- Stronger emotional + audio continuity across extended sequences
- Updated CLI & Web UI with DNA, sequence, and quota tooling + live per-second cost estimation

---

## 🚀 Quick Start

### 1. Fastest: Master Prompt Activation (Recommended)
1. Copy the content of [`MASTER_PROMPT_v3.6.md`](MASTER_PROMPT_v3.6.md)
2. Paste into a new **Grok 4.3 Full** chat (enable reasoning=medium/high for complex productions)
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
python tools/cinematic_studio_cli.py quota estimate --duration 90 --clips 9 --fast-mode
```

### 3. Streamlit Web UI
```bash
pip install -r requirements-streamlit.txt
streamlit run web_ui/app.py
```
(Now includes Imagine Model selector: 1.5 Native (default), resolution, duration, native audio toggle, and live 1.5 cost simulator)

---

## 🏗️ System Architecture (v3.6)

```
Studio Director v3.6 + Mega Production Architect v3.6
├── references/agents/          # Authoritative Role Cards (v3.6)
├── tools/                      # CLI libraries: character_dna, sequence_chain, quota_optimizer
├── tools/cinematic_studio_cli.py   # CLI: dna, sequence, quota + memory + PDF
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

*Grok Imagine Cinematic Studio v3.6 "Odyssey Native" — Built for professional cinematic storytelling with Grok 4.3 + Imagine Video 1.5*

*Last updated: June 20, 2026*