# RELEASE NOTES — Grok Imagine Cinematic Studio v3.6 "Odyssey Native"

**Release Date:** June 20, 2026  
**Latest Patch:** v3.6.6 (July 9, 2026)  
**Focus:** Full native integration with **Grok Imagine Video 1.5** + dual Grok 4.5 Build / Grok 4.3 cinematic stack + Grok plugin marketplace support

---

## v3.6.6 Patch (July 9, 2026) — Dual Model Stack

- **Dual stack** — cinematic orchestration default **`grok-4.3`** (1M context); Grok Build / coding default **`grok-4.5`**
- **Grok Build ≥ 0.2.93** recommended CLI (`RECOMMENDED_GROK_BUILD_CLI_VERSION`; soft-probed by `models verify`)
- **Registry redesign** — `STACK_CONTRACT` → `ROLE_DEFAULTS` (single source), cached alias maps, data-driven `verify_model_compatibility()`, `REQUIRED_MODEL_ROLES`
- **`grok-4.5` pricing** — $2 / $6 per 1M ($0.50 cached in), 500k context; `grok-build-0.1` kept as legacy
- **CLI** — unknown `--chat-model` warns and falls back to cinematic default; `models list` tags cinematic/build defaults from helpers
- **Docs & skills** — README, AGENTS, MASTER_PROMPT, Quick Start, MODELS, Role Cards, quota pricing, meta-installer paths aligned
- **Plugin** — `.grok-plugin` version **3.6.6** + marketplace pin for dual-stack install

**Activation:** `Activate Grok Imagine Cinematic Studio v3.6.6`

**Recommended models (v3.6.6):**

| Layer | Slug | Notes |
|-------|------|-------|
| Cinematic / Production Bibles | `grok-4.3` | 1M context |
| Grok Build CLI / coding API | `grok-4.5` | Default agent; recommend CLI ≥ 0.2.93 |
| Build fork | `grok-build` | Skills / tooling |
| Imagine Video | `grok-imagine-video` (1.0) / `1.5` | Cost default vs native audio |
| Imagine Image | `grok-imagine-image` | Reference stills |

## v3.6.5 Patch (June 24–26, 2026)

- **Grok plugin marketplace support** — `.grok-plugin/marketplace.json`, `plugin.json`, `plugin-index.json` (44 skills + 11 commands); `grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio`
- **`scripts/generate_plugin_index.py`** — auto-generates the skill/command catalog for the Grok plugin system
- **README.md refresh** — v3.6.5 alignment, 44-skill suite docs, model stack everywhere, updated architecture, project structure, agent listings, CLI/Web UI examples, and links
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
- **44 skills** in the Grok plugin catalog (core cinematic agents + i2i + NSFW + delivery + meta)
- `.grok-plugin/` marketplace support for one-command `grok plugin install`
- `scripts/generate_plugin_index.py` keeps the skill + command index fresh
- Consistent markdown formatting across all skill files (SKILL.md)
- Enhanced protocols for 1.5 native video + audio workflows + plugin distribution

### Agent & System Upgrades (v3.6.5–v3.6.6)
- All core agents at v3.6.5+ with 1.5-specific protocols, model stack tables, decision frameworks, and output formats
- Enhanced long-form sequencing (60–180s+) with low-degradation 1.5 native chaining + AUDIO_MOMENTUM_VECTOR
- Stronger emotional + audio continuity across extended sequences
- **v3.6.6 dual stack:** cinematic `grok-4.3` + Build/coding `grok-4.5`; CLI/Web UI model pickers and `models verify` updated
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

**v3.6.5+ additions:** `cinematic-studio-meta-installer`, `github-repo-manager`, `assembly-editor`, `animatic-director`, `reference-asset-curator`, `image-to-video-specialist`, `sfw-batch-orchestrator`, `chain-qa-protocol`, `handoff-packet-validator`, `cinematic-ffmpeg`, `ai-polish-director`, `production-bible-workflow`, `nsfw-*` variants, and more (full 44 in `.grok-plugin/plugin-index.json`).

### Documentation Updates
- `MASTER_PROMPT_v3.6.md` — Complete new activation prompt with 1.5 pipeline rules
- `README.md` — Fully refreshed for v3.6.5 (plugin marketplace, 44-skill suite, model stack, architecture, CLI examples)
- `CHANGELOG.md` — Extended with [3.6.5] and [Unreleased] entries (plugin, web UI fixes, hygiene)
- `AGENT_INDEX.md` — Updated to v3.6.5 with model compatibility table and 16 activation presets
- `Quick_Start_Guide.md` — Updated to v3.6.5 with model stack section (§0) and Grok Build config
- `RELEASE_NOTES_v3.6.md` — This file (now includes v3.6.5 patch + plugin support)
- `UPGRADE_GUIDE.md` — v3.5 → v3.6 migration guide
- `.grok-plugin/` files — `marketplace.json`, `plugin.json`, generated `plugin-index.json` for Grok CLI plugin installation

### CI Improvements
- Removed broken `.markdownlint.json` dependency
- Made Lint Markdown step non-blocking (`continue-on-error: true`)
- Added robust directory existence checks with job outputs
- **v3.6.5+:** Updated path filters after `agents/` removal; plugin manifest + index generation in CI workflows

---

## 🚀 How to Activate v3.6.5

```bash
# Recommended (Grok 4.3 / Grok Build)
Copy MASTER_PROMPT_v3.6.md into a new chat
Type: Activate Grok Imagine Cinematic Studio v3.6.5

# Or install as Grok plugin (recommended for CLI)
grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio --trust

# Or use specific 1.5 mode
ACTIVATE IMAGINE_VIDEO_1.5_FULL
```

See `Quick_Start_Guide.md` for full onboarding (including model stack and plugin marketplace).

---

**v3.6.5 "Odyssey Native"** adds full Grok plugin marketplace support (44 skills), comprehensive model stack wiring across CLI/Web UI/agents, Streamlit API modernization for the Web UI, repo hygiene, and polished documentation.

v3.6 "Odyssey Native" (with 1.5 native video + audio) marks the biggest leap in cinematic quality, audio-visual integration, and system completeness since the original studio launch.

Thank you for building with us. 🎥✨

*— The Grok Imagine Cinematic Studio Team*