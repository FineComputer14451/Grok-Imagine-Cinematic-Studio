<p align="center">
  <img src="assets/banner.jpg" alt="Grok Imagine Cinematic Studio Banner" width="100%">
</p>

# 🎬 Grok Imagine Cinematic Studio v3.8.0 "Odyssey Native"

**The most advanced multi-agent cinematic production system for Grok Build 0.2.93+ · Grok 4.5 (cinematic + coding default) · optional Grok 4.3 (1M) · Grok Imagine Video (1.0 default; 1.5 native audio available)**

Transform any story into emotionally powerful, production-ready cinematic video with **Imagine Video 1.0** ($0.05/sec) or **1.5 native image-to-video** with one-pass synchronized audio (lip-sync + SFX + ambience + music), perfect character consistency, persistent memory, and a full **23-agent** professional film crew.

[![Version](https://img.shields.io/badge/version-3.8.0-blue)](https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Grok](https://img.shields.io/badge/Grok-4.5%20cinematic%2BBuild%20%C2%B7%20optional%204.3%201M%20%C2%B7%20Imagine-purple)](https://x.ai)

---

## ✨ What's New in v3.8.0

- **Plugin modularity** — marketplace ships recommended full suite + five satellite packs (`core`, `camera-image`, `sequence-narrative`, `nsfw`, `delivery-post`) from `config/plugin_packs.yaml`
- **`plugin packs` CLI** — list pack membership; pack-aware catalog generation and pin
- **Declutter `full_suite_wins`** — dual full-suite + satellite installs drop satellite skill dupes

## ✨ What's New in v3.7.1

- **Imagine Agent Mode Handoff** — Studio Director routes planning → generation across Grok Build tools, ACP, grok.com/imagine, and xAI API
- **Full suite on Grok 4.5** — all Role Cards + skills embed **Model Layer (Grok 4.5 · studio v3.7.1)**; operating rules (reasoning high, 1M opt-in only, Imagine tools ≠ chat)
- **Canonical model docs** — `references/agents/MODEL_LAYER_v3.7.1.md` + `tools/models.py` (`STACK_CONTRACT` cinematic+Build = `grok-4.5`)
- Builds on **v3.6.7** guided Bible wizard + catalog pin hygiene

## ✨ Unified Grok 4.5 Stack (since v3.6.6/3.6.7)

- **Unified chat default** — cinematic orchestration + Grok Build / coding on **`grok-4.5`**; opt-in **`grok-4.3`** for 1M-context Bibles only
- **Grok Build ≥ 0.2.93** documented as minimum recommended CLI (`grok --version`)
- **Registry + verify** — `tools/models.py` / `models verify`; `grok-build-0.1` marked legacy
- Aliases: `4.5`, `coding`, `cinematic`, `grok-build-latest` → **4.5**; `4.3`, `long-context` → **4.3** (1M opt-in)
- **Guided Production Bible wizard** (v3.6.7) — `create-bible --wizard` + Web UI Guided Bible Creator

### What's New in v3.6.5 "Odyssey Native"

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
- **Grok plugin marketplace** — `.grok-plugin/marketplace.json`, `plugin.json`, `plugin-index.json` (48 skills + commands) for `grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio`
- **Imagine 1.0 as default** — `grok-imagine-video` ($0.05/sec); 1.5 opt-in for native audio ($0.08/sec)
- **`models verify`** CLI — validates Grok 4.5 cinematic+Build + optional 4.3 + Imagine 1.0/1.5 registry
- **CLI modularization** — extracted `tools/cli/{models,bible,studio,production,...}_commands.py`; slimmer main entrypoint
- **Canonical project state** — `tools/project_state.py` with auto-merge legacy support
- **Model stack everywhere** — `VIDEO_PIPELINE_SPEC` + `model_stack_summary()` wired into CLI, Web UI, DNA/sequence handoffs, Production Bibles
- **Repo hygiene** — removed deprecated `agents/` dir, stale skill mirrors, duplicate MASTER_PROMPT; CI updated
- **Role Cards & skills** — Mega Production Architect, Imagine Prompt Master, Studio Director, etc. updated with model table and 1.5 fidelity
- **Quick Start Guide & Project Bible template** updated with model stack section and Grok Build config example

### Agent & System Upgrades
- Core agents at **v3.6.5 Role Cards** under **studio v3.7.1** (1.5 protocols, Grok 4.5 Model Layer on all agents, decision frameworks)
- Enhanced long-form sequencing (60–180s+) with low-degradation 1.5 native chaining
- Stronger emotional + audio continuity across extended sequences
- CLI & Web UI: DNA, sequence, quota, NSFW, model pickers, guided Bible wizard, live cost estimation, plugin install

---

## 🚀 Quick Start

### 1. Fastest: Master Prompt Activation (Recommended)
1. Copy the content of [`MASTER_PROMPT.md`](MASTER_PROMPT.md)
2. Paste into a new **Grok 4.5** chat (default) or **Grok 4.3** for long 1M Bibles (enable reasoning=medium/high for complex productions)
3. Type: `Activate Grok Imagine Cinematic Studio v3.7.1`

### 2. Python CLI (Power Users)
```bash
pip install -r requirements.txt
cinematic-studio --help

# Examples (short form; also works as `python -m tools.cinematic_studio_cli`)
cinematic-studio status
cinematic-studio create-bible "Your Project Title"
cinematic-studio create-bible --wizard   # optional guided stages (TTY); same Bible JSON
cinematic-studio dna init "Elena Voss" --core "..." --facial "..."
cinematic-studio sequence init "Neon Alley Chase" --duration 90
cinematic-studio models list
cinematic-studio models verify
cinematic-studio quota estimate --duration 90 --clips 9 --fast-mode
cinematic-studio generate-prompt "Your story" --chat-model grok-4.5 --video-model 1.0
cinematic-studio nsfw extend plan "Intimate Sequence" --duration 90 --profile passionate --reference "..."
cinematic-studio nsfw plan "Hero Session" --shot "hero:Cover frame" --budget 800
cinematic-studio plugin catalog pin
cinematic-studio plugin catalog check --release
```

### 3. Grok Build Plugin Marketplace (Recommended for Grok CLI)
Install the full Grok plugin suite (**48 skills** + 11 slash commands) as a Grok plugin (**recommended**):

```bash
# Install directly from GitHub (simplest — full suite)
grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio --trust

# Or add as a marketplace source and install by name
grok plugin marketplace add FineComputer14451/Grok-Imagine-Cinematic-Studio
grok plugin install grok-imagine-cinematic-studio@finecomputer14451/grok-imagine-cinematic-studio --trust

# Optional: refresh after updates
grok plugin marketplace update
grok plugin update grok-imagine-cinematic-studio
```

#### Plugin install matrix (v3.8.0 modular packs)

Marketplace lists **6 plugins** from one repo (`config/plugin_packs.yaml`). Prefer the **full suite** unless you intentionally want a smaller satellite set.

| Plugin | Pack id | Skills | Notes |
|--------|---------|--------|--------|
| **`grok-imagine-cinematic-studio`** | *(full)* | 48 | **Recommended** one-click install — all skills + slash commands |
| `grok-imagine-cinematic-core` | `core` | 16 | Orchestration, DNA, Imagine runtime, QA, quota, meta |
| `grok-imagine-camera-image` | `camera-image` | 9 | DoP, production design, i2i, key art, i2v — soft-requires **core** |
| `grok-imagine-sequence-narrative` | `sequence-narrative` | 14 | Sequence, continuity, performance, audio, action/VFX, SFW batches — soft-requires **core** |
| `grok-imagine-nsfw` | `nsfw` | 4 | Opt-in ErosForge + NSFW quota/sequence/chain QA — soft-requires **core** |
| `grok-imagine-delivery-post` | `delivery-post` | 5 | Assembly, color grade, AI polish, upscale, ffmpeg — soft-requires **core** |

```bash
# List packs from a repo checkout
cinematic-studio plugin packs
```

If full suite **and** a satellite pack are both installed, declutter uses **`full_suite_wins`** (keeps full suite, drops satellite skill dupes). See `docs/guides/installation_guide.md`.

Catalog lives in `.grok-plugin/marketplace.json` (full + 5 packs). Satellite manifests: `.grok-plugin/packs/<id>/plugin.json`.

**Plugin catalog commands:**
```bash
cinematic-studio plugin packs                # full suite + pack matrix
cinematic-studio plugin catalog pin          # regenerate + pin SHA for release
cinematic-studio plugin catalog check        # verify freshness
cinematic-studio plugin catalog check --release  # pre-publish gate
cinematic-studio plugin status
cinematic-studio plugin list
```

After skill/command changes, run `pin` and commit the `.grok-plugin/` files atomically with your feature work.

### 4. Streamlit Web UI
```bash
pip install -r requirements-streamlit.txt
streamlit run web_ui/app.py
```
(Imagine video model selector, xAI chat model picker (`grok-4.5` default / `grok-4.3` 1M opt-in), live per-second cost simulator)

---

## 🏗️ System Architecture (v3.7.1)

```
Studio Director v3.7.1 + Mega Production Architect v3.6.5  (Role Cards; studio v3.7.1 · Grok 4.5)
├── .grok-plugin/                 # Marketplace + plugin manifests (48 skills) — managed via `cinematic-studio plugin catalog`
├── references/agents/            # Role Cards + AGENT_INDEX + MODEL_LAYER_v3.7.1 + Handoff protocol
├── tools/                        # character_dna, sequence_chain, quota_optimizer, nsfw_*, models.py, bible_stages, imagine_bridge
├── tools/cinematic_studio_cli.py   # CLI: create-bible --wizard, dna, sequence, quota, nsfw, models, imagine, plugin catalog
├── references/MODELS_v3.6.md   # Grok Build + xAI model registry (Grok 4.5 default)
├── web_ui/app.py                 # Streamlit + Guided Bible Creator + model pickers
├── examples/                     # Production Bible templates
├── MASTER_PROMPT.md         # Main activation prompt (v3.7.1 · Grok 4.5)
├── scripts/                      # thin shims (release/verify); real catalog work via `cinematic-studio plugin catalog`
└── .grok/skills/                 # 48 custom Grok skills (primary runtime)
```

**Key v3.7.1 Components:**
- `references/agents/` — Role Cards (labels remain v3.6.5 in CLI registry; Studio Director **v3.7.1**)
- `references/agents/MODEL_LAYER_v3.7.1.md` — Grok 4.5 operating rules for every agent/skill
- `MASTER_PROMPT.md` — Activation with Grok 4.5 stack + Imagine Agent Mode Handoff
- `tools/cli/bible_stages.py` — Guided Production Bible wizard (CLI `--wizard` + Web UI)
- `references/agents/AGENT_INDEX.md` — Quick reference + activation presets
- `.grok-plugin/` — Marketplace support for `grok plugin install` + release-pin hygiene

---

## 🎥 The 23-Agent Professional Film Crew (v3.6.5 Role Cards · studio v3.7.1 · Grok 4.5)

### Core Leadership
- **Studio Director v3.7.1** — Central commander, **Imagine Agent Mode Handoff** owner, pipeline leader
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
├── .grok/skills/                 # 48 studio skills (agent-only)
├── .grok-plugin/                 # Marketplace manifests + pin
├── references/agents/            # Role Cards + MODEL_LAYER_v3.7.1 + AGENT_INDEX
├── references/MODELS.md          # Model registry guide (alias → MODELS_v3.6.md)
├── docs/                         # Human docs (guides, templates, releases, archive)
│   ├── guides/                   # Quick Start, Upgrade, Installation
│   ├── templates/                # Production Bible, kink library
│   └── releases/                 # RELEASE_NOTES_v3.7.1.md
├── tools/                        # cinematic_studio_cli.py + models.py + cli/
├── web_ui/ · scripts/ · commands/ · examples/ · tests/
├── MASTER_PROMPT.md              # Chat activation (Grok 4.5)
├── CHANGELOG.md · AGENTS.md · VERSION
└── characters/ · sequences/ · artifacts/   # Runtime (CLI paths; contents mostly gitignored)
```

Layout details: [docs/REPOSITORY_LAYOUT.md](docs/REPOSITORY_LAYOUT.md) · [docs/README.md](docs/README.md)

---

## 🔗 Useful Links

- [Documentation index](docs/README.md)
- [Quick Start Guide](docs/guides/Quick_Start_Guide.md)
- [Agent Index (v3.7.1)](references/agents/AGENT_INDEX.md)
- [Production Bible Template](docs/templates/Project_Bible_Template.md)
- [CHANGELOG](CHANGELOG.md)
- [Release notes v3.7.1](docs/releases/RELEASE_NOTES_v3.7.1.md)
- [Upgrade Guide](docs/guides/UPGRADE_GUIDE.md)
- [Slash Commands Reference](commands/) — cinematic, dna, nsfw, quota, validate, etc.

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

*Grok Imagine Cinematic Studio v3.8.0 "Odyssey Native" — Built for Grok Build 0.2.93+, Grok 4.5 (cinematic + coding), optional Grok 4.3 (1M), and Imagine Video 1.0/1.5*

*Last updated: July 11, 2026 — v3.8.0*
