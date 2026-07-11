# RELEASE NOTES — Grok Imagine Cinematic Studio v3.6 "Odyssey Native"

**Release Date:** June 20, 2026  
**Latest Patch:** v3.7.1 (July 10, 2026)  
**Focus:** Full native integration with **Grok Imagine Video 1.5** + unified **Grok 4.5** cinematic+Build (optional **Grok 4.3** 1M) + Grok plugin marketplace support

---

## v3.7.1 Patch (July 10, 2026) — Imagine Agent Mode Handoff + Suite-wide Grok 4.5

- **Imagine Agent Mode Handoff** — Studio Director owns routing to Grok Build tools / ACP / grok.com/imagine / xAI API (`imagine agent-handoff` CLI)
- **Suite-wide Grok 4.5** — all Role Cards + skills use **Model Layer (Grok 4.5 · studio v3.7.1)**; enhanced operating rules (reasoning, 1M opt-in, Imagine tools)
- **Canonical docs** — `MODEL_LAYER_v3.7.1.md`, README/Quick Start/MASTER_PROMPT/UPGRADE_GUIDE/installation guide aligned; alias `cinematic` → `grok-4.5`
- **Activation:** `Activate Grok Imagine Cinematic Studio v3.7.1`

---

## v3.6.7 Patch (July 9, 2026) — Guided Bible Wizard + Catalog Pin Hygiene

- **Guided Production Bible wizard** — `create-bible --wizard` (TTY) + Web UI Guided Bible Creator; shared stages → existing `build_production_bible` (no dual schema; direct path stays script-default)
- **Release pin fix** — `plugin catalog check --release` accepts pin-only catalog follow-up commits (install SHA = content revision)
- **Studio / plugin version** — **3.6.7**

**Activation (at release):** `Activate Grok Imagine Cinematic Studio v3.6.7`  
**Current activation:** `Activate Grok Imagine Cinematic Studio v3.7.1`

## v3.6.6 Patch (July 9, 2026) — Dual Model Stack

- **Unified chat default** — cinematic orchestration + Grok Build / coding on **`grok-4.5`**; opt-in **`grok-4.3`** for 1M-context Bibles
- **Grok Build ≥ 0.2.93** recommended CLI (`RECOMMENDED_GROK_BUILD_CLI_VERSION`; soft-probed by `models verify`)
- **Registry redesign** — `STACK_CONTRACT` → `ROLE_DEFAULTS` (single source), cached alias maps, data-driven `verify_model_compatibility()`, `REQUIRED_MODEL_ROLES`
- **`grok-4.5` pricing** — $2 / $6 per 1M ($0.50 cached in), 500k context; `grok-build-0.1` kept as legacy
- **CLI** — unknown `--chat-model` warns and falls back to cinematic default; `models list` tags cinematic/build defaults from helpers
- **Docs & skills** — README, AGENTS, MASTER_PROMPT, Quick Start, MODELS, Role Cards, quota pricing, meta-installer paths aligned
- **Plugin** — `.grok-plugin` version **3.6.6** + marketplace pin for dual-stack install

**Activation (historical):** `Activate Grok Imagine Cinematic Studio v3.7.1.6`

**Recommended models (v3.6.6+ unified Grok 4.5 stack):**

| Layer | Slug | Notes |
|-------|------|-------|
| Cinematic / Production Bibles | `grok-4.5` | Default (use `grok-4.3` for 1M opt-in) |
| Grok Build CLI / coding API | `grok-4.5` | Default agent; recommend CLI ≥ 0.2.93 |
| Build fork | `grok-build` | Skills / tooling |
| Imagine Video | `grok-imagine-video` (1.0) / `1.5` | Cost default vs native audio |
| Imagine Image | `grok-imagine-image` | Reference stills |

## v3.6.5 Patch (June 24–26, 2026)

- **Grok plugin marketplace support** — `.grok-plugin/marketplace.json`, `plugin.json`, `plugin-index.json` (skill catalog; **48 skills** as of suite + `ai-image-recreation`); `grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio`
- **`scripts/generate_plugin_index.py`** — auto-generates the skill/command catalog for the Grok plugin system
- **README.md refresh** — v3.6.5+ alignment, full skill suite docs, model stack everywhere, updated architecture, project structure, agent listings, CLI/Web UI examples, and links
- **Web UI Streamlit fixes** — migrated all `use_container_width=True` (dataframes, buttons, forms) to `width="stretch"` for newer Streamlit compatibility; minor robustness update in dashboard
- **CHANGELOG.md** updated with detailed entries for 3.6.5 and post-release refinements
- **Repo hygiene** — removed deprecated `agents/` dir and stale mirrors; canonical Role Cards stay in `references/agents/`
- **Imagine 1.0 as default** — `DEFAULT_IMAGINE_VIDEO_MODEL` switched to `grok-imagine-video` ($0.05/sec); 1.5 remains for native-audio
- **Model stack & CLI** — full wiring of `VIDEO_PIPELINE_SPEC`, `models verify` CLI, refactored `tools/cli/`, canonical project state
- See [3.6.5] section in `CHANGELOG.md` for the core model registry, CLI modularization, Web UI model pickers, Role Card updates, etc.

## v3.6.4 Patch (June 21, 2026)

- **NSFW Sequence Extender** — 30–120s+ sensual extension, prompt chains, erotic pacing, artifact QA
- **NSFW Quota Orchestrator** — Heavy batch planning, i2v decisions, daily reports
- **Model registry** (v3.6.2) — `tools/models.py`, xAI USD pricing alignment
- Docs, CLI, Web UI version strings aligned to v3.6.4

## v3.6.1 Patch (June 22, 2026)

- **AI Polish Director** (23rd agent) + `ai-video-upscaler` skill
- **Character DNA pipeline** — `dna` CLI + `character-dna-extractor` skill
- **Sequence chain** — `sequence` CLI + 10-point chain QA for 1.5 extend/stitch
- **Quota orchestration** — `quota` CLI + per-second 1.5 pricing model
- CLI/Web UI/README aligned to 23 agents and v3.6.1

See `CHANGELOG.md` for full details.

---

## 🎉 Major Highlights

### Grok Imagine Video 1.5 Native Support (Major)
- Full native image-to-video generation with dramatically improved motion, physics, and consistency
- **One-pass synchronized native audio** (lip-synced dialogue + SFX + ambience + music cues)
- `VIDEO_PIPELINE_SPEC` — Locked variable for model, resolution (720p), clip length (6–15s), native_audio, extend/stitch strategy
- `AUDIO_MOMENTUM_VECTOR` — New handoff protocol carrying dialogue state, SFX timing, emotional tone of audio, and music cue points
- `reference_image_id` propagation + 1.5 fidelity scoring in Identity Lock & Continuity systems
- New Director’s Notes metrics: **Audio-Visual Sync Fidelity** and **Physics Realism**
- Optimized prompting rules for 1.5 (explicit camera moves with weighty physics, timing beats, Sound Layer syntax)
- Per-second 1.5 video quota modeling + Fast mode → quality pass strategies

### Complete Skill Layer (`.grok/skills/`) + Plugin Marketplace
- **48 skills** in the Grok plugin catalog (core cinematic agents + i2i + upload recreation + NSFW + delivery + meta)
- `.grok-plugin/` marketplace support for one-command `grok plugin install`
- `scripts/generate_plugin_index.py` keeps the skill + command index fresh
- Consistent markdown formatting across all skill files (SKILL.md)
- Enhanced protocols for 1.5 native video + audio workflows + plugin distribution

### Agent & System Upgrades (v3.6.5–v3.6.7)
- Core agents at v3.6.5 Role Cards under studio **v3.6.7** (1.5 protocols, Grok 4.5 Model Layer, decision frameworks)
- Enhanced long-form sequencing (60–180s+) with low-degradation 1.5 native chaining + AUDIO_MOMENTUM_VECTOR
- Stronger emotional + audio continuity across extended sequences
- **v3.6.6 dual stack (historical):** cinematic `grok-4.3` + Build/coding `grok-4.5`; later unified cinematic default to `grok-4.5` (4.3 remains 1M opt-in)
- **v3.6.7:** Guided Production Bible wizard + catalog release-pin hygiene
- Grok plugin distribution for the full 23-agent + specialist suite

---

## 📦 Files Changed / Added

### New Skill Files Created (v3.6 base)
- `sequence-director/SKILL.md`
- `cinematic-sequence-extender/SKILL.md`
- `erosforge-nsfw-director/SKILL.md`
- `director-of-photography/SKILL.md`
- `foley-sound-design-specialist/SKILL.md`
- `key-art-poster-designer/SKILL.md`
- `trailer-teaser-director/SKILL.md`
- `localization-subtitle-specialist/SKILL.md`
- `production-designer-set-decorator/SKILL.md`
- `stunt-action-choreographer/SKILL.md`
- `vfx-sfx-supervisor/SKILL.md`

**v3.6.5+ additions:** `cinematic-studio-meta-installer`, `github-repo-manager`, `assembly-editor`, `animatic-director`, `reference-asset-curator`, `image-to-video-specialist`, `sfw-batch-orchestrator`, `chain-qa-protocol`, `handoff-packet-validator`, `cinematic-ffmpeg`, `ai-polish-director`, `production-bible-workflow`, `nsfw-*` variants, `arc-replan-copilot`, `multi-character-identity-arbiter`, `ai-image-recreation`, and more (full 48 in `.grok-plugin/plugin-index.json`).

### Documentation Updates
- `MASTER_PROMPT_v3.6.md` — Activation prompt (unified Grok 4.5 stack + 1.5 + v3.6.7 wizard pointers)
- `README.md` — Refreshed for **v3.6.7** (wizard, Grok 4.5 default, plugin marketplace, architecture, CLI)
- `CHANGELOG.md` — [3.6.7], [3.6.6], [3.6.5], … historical entries
- `AGENT_INDEX.md` — Model compatibility table + activation presets (studio v3.7.1)
- `Quick_Start_Guide.md` — Model stack §0, wizard, activation **v3.6.7**
- `RELEASE_NOTES_v3.6.md` — This file (through v3.6.7 patch)
- `UPGRADE_GUIDE.md` — v3.5 → v3.6 migration (unified 4.5 stack + wizard + pin hygiene)
- `references/installation_guide.md` — Meta installer + plugin install paths
- `.grok-plugin/` files — `marketplace.json`, `plugin.json`, generated `plugin-index.json`

### CI Improvements
- Removed broken `.markdownlint.json` dependency
- Made Lint Markdown step non-blocking (`continue-on-error: true`)
- Added robust directory existence checks with job outputs
- **v3.6.5+:** Updated path filters after `agents/` removal; plugin manifest + index generation in CI workflows

---

## 🚀 How to Activate v3.6.7

```bash
# Recommended (Grok 4.5 default; optional Grok 4.3 for 1M Bibles)
Copy MASTER_PROMPT_v3.6.md into a new chat
Type: Activate Grok Imagine Cinematic Studio v3.7.1

# Or install as Grok plugin (recommended for CLI)
grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio --trust
# then: grok plugin update   # if already installed

# Guided Bible (CLI TTY or Web UI Guided Bible Creator)
cinematic-studio create-bible --wizard

# Or use specific 1.5 mode
ACTIVATE IMAGINE_VIDEO_1.5_FULL
```

See `Quick_Start_Guide.md` for full onboarding (model stack, wizard, plugin marketplace).

---

**v3.6.7 "Odyssey Native"** adds the guided Production Bible wizard and catalog release-pin hygiene on top of the **unified Grok 4.5** cinematic+Build stack (optional Grok 4.3 1M) and **v3.6.5+** plugin marketplace (now **48 skills**, including `ai-image-recreation`).

v3.6 "Odyssey Native" (1.5 native video + audio + unified Grok 4.5 stack + wizard) marks the biggest leap in cinematic quality, audio-visual integration, and system completeness since the original studio launch.

Thank you for building with us. 🎥✨

*— The Grok Imagine Cinematic Studio Team*