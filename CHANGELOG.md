# Changelog

All notable changes to Grok Imagine Cinematic Studio will be documented in this file.

## [Unreleased]

### Changed
- **Repo layout (Grok 4.5 hygiene)** — human docs moved under `docs/{guides,templates,releases,archive,development}/`; root keeps lean `README` / `AGENTS` / `CHANGELOG` / `MASTER_PROMPT.md` with compatibility stubs for old paths; `references/MODELS.md` alias; `MODEL_LAYER_v3.6.7` archived; see `docs/REPOSITORY_LAYOUT.md`

### Added
- **`ai-image-recreation` in plugin suite (Grok 4.5)** — user-upload recreation / style transfer / enhance / design sheets / pre-video plates via `image_edit` + multi-pass protocol; ported into `.grok/skills/ai-image-recreation/` with prompt library + adult cheat sheet; catalog **48 skills** (`plugin.json`, `plugin-index.json`, `required_skills.manifest` parity including `skill-agent-architect`)
- **Character DNA Extractor → Grok 4.5 / v3.7.1** — full skill rewrite (forensic modes, design-sheet bridge, multi-cast path, `video_1.0` inject); template + Role Card refresh; `tools/character_dna.py` `STUDIO_AGENT_VERSION` **v3.7.1** + prompt modes `video_1.0` / `video_1.5`
- **AI Polish Director → Grok 4.5 / v3.7.1** — full skill rewrite (delivery presets, post-upscale gates, sequence polish CLI + upscaler paths); Role Card + `polish_presets.md`; `sequence_polish.py` embeds `polish_spec` / Bible log line; suite package confirmed in plugin catalog (`plugin.json` / index / `required_skills.manifest`) with skill `references/`
- **GitHub Repo Manager → Grok 4.5 / v3.7.1** — full skill rewrite (safety gates, plugin catalog pin protocol, skill-suite parity, conventional commits); fixed `validate-all-skills.sh` / `prepare-release.sh` / `repo-status.sh`; added `references/plugin_catalog_release.md`
- **Cinematic FFmpeg → Grok 4.5 / v3.7.1** — skill rewrite + frontmatter fix (no colons in description; aspect ratios as 9x16/1x1/16x9); sequence deliver CLI + delivery checklist
- **Handoff Packet Validator → Grok 4.5 / v3.7.1** — full skill rewrite (gate policy, generate-then-validate flows, Studio Director block rules); `references/packet_types.md` field cheat sheet
- **Assembly Editor → Grok 4.5 / v3.7.1** — full skill rewrite (EDL CLI, pacing rules, hero polish handoff); Role Card refresh; `assembly_editor.py` stamps `studio_agent_version` + `cut_name`
- **Animatic Director → Grok 4.5 / v3.7.1** — full skill rewrite (tier strategy, budget gate, CLI plan/promote, motion-probe rules); `animatic_orchestrator.py` stamps `studio_agent_version`
- **SFW Batch Orchestrator → Grok 4.5 / v3.7.1** — full skill rewrite (hero-first tiers, mode decisions, retry policy, full `sfw` CLI); Role Card refresh; batch plans stamp `studio_agent_version`
- **Reference Asset Curator → Grok 4.5 / v3.7.1** — full skill rewrite (tier matrix aligned to 1.0 video default, ASSET_MANIFEST + handoff validate, SFW/NSFW maps); Role Card refresh
- **Image-to-Video Specialist → Grok 4.5 / v3.7.1** — full skill rewrite (hard gates, motion tiers, 1.0 default / 1.5 audio, VIDEO_PIPELINE_SPEC, extend-prompt CLI); Role Card refresh
- **Chain QA Protocol → Grok 4.5 / v3.7.1** — full skill rewrite (10-point weights, critical floor, qa-assist/regen CLI, output report); checklist v3.7.1; `CHAIN_QA_PROTOCOL_VERSION` on results
- **Sequence Director → Grok 4.5 / v3.7.1** — full skill rewrite (dependency graph, full `sequence` CLI map, temp/replan/health, 1.0 video default); Role Card refresh
- **Cinematic Sequence Extender → Grok 4.5 / v3.7.1** — full skill rewrite (hard rules, handoff fields, failure recovery, 1.0/1.5 pipeline specs); Role Card + extend_stitch_protocol updated for cost-default 1.0
- **Workflow Quota Optimizer → Grok 4.5 / v3.7.1** — full skill rewrite (risk levels, Fast→quality-pass, full `quota` CLI, 1.0 default economics); Role Card + pricing_model notes; `STUDIO_AGENT_VERSION`
- **Continuity Consistency Guardian → Grok 4.5 / v3.7.1** — full skill rewrite (memory banks, boundary checklist, continuity-diff/memory CLI, Chain QA ownership); Role Card refresh
- **Studio Director → Grok 4.5 / v3.7.1 (enhanced)** — expanded skill (full pipeline order, i2i/handoff rules, hard blocks, specialist map); Role Card pipeline table aligned to animatic/quota/chain/extend
- **Quality Assurance Guardian → Grok 4.5 / v3.7.1** — full skill rewrite (16-point + chain 10-point dual gate, thresholds, hard blocks, report template); Role Card refresh
- **Identity Lock Specialist → Grok 4.5 / v3.7.1** — full skill rewrite (lock/inject CLI, drift gates, multi-cast, video_1.0/1.5 inject, hard blocks); Role Card refresh
- **Imagine Prompt Master → Grok 4.5 / v3.7.1** — full skill rewrite (Ultimate Template, DNA inject modes, 1.0/1.5 video schema, artifact lexicon, output report); Role Card refresh
- **Mega Production Architect → Grok 4.5 / v3.7.1** — full skill rewrite (Bible package, 1.0 video default, create-bible CLI, roadmap order, i2i routing); Role Card refresh
- **Director of Photography → Grok 4.5 / v3.7.1** — full skill rewrite (motivated lighting, camera/lens, physics-aware motion, motif lock, prompt handoff); Role Card refresh
- **Performance Emotion Director → Grok 4.5 / v3.7.1** — full skill rewrite (subtext layers, micro-timing, sequence temp CLI, intimate path); Role Card refresh
- **Production Designer Set Decorator → Grok 4.5 / v3.7.1** — full skill rewrite (Environment DNA, prop bank, practicals for DoP, continuity CLI); Role Card refresh
- **Post-Production Color Grading Supervisor → Grok 4.5 / v3.7.1** — full skill rewrite (grade design checklist, skin protection, stitch-safe unity, pipeline before AI Polish); Role Card refresh
- **Narrative Arc Pacing Strategist → Grok 4.5 / v3.7.1** — full skill rewrite (beat structure, pacing heatmap, temp CLI, quota-aware structure); Role Card refresh
- **Sonic Architect Native Audio Virtuoso → Grok 4.5 / v3.7.1** — full skill rewrite (1.0 vs 1.5 audio paths, multi-layer Sound Layer, AMV for stitches); Role Card refresh
- **Foley Sound Design Specialist → Grok 4.5 / v3.7.1** — full skill rewrite (Sound DNA, physics/perspective checklist, Sound Layer SFX paste, intimate path); Role Card refresh
- **Arc replan co-pilot (roadmap #12)** — `tools/arc_replan.py` replans remaining beats and temperature curve after mid-sequence failure; CLI `sequence replan plan|apply`; skill `arc-replan-copilot` (final long-form continuity roadmap item)
- **Stitch artifact lexicon (roadmap #11)** — `tools/stitch_artifact_lexicon.py` vocabulary + negative/positive packs for flicker/morph/halo; CLI `sequence artifact-lexicon`; re-gen prompts consume suggested packs
- **Long-form health dashboard (roadmap #10)** — `tools/sequence_health_dashboard.py` aggregates chain QA, drift/seam/AMV, regen, temperature, continuity diffs, remaining cost; CLI `sequence health` with `--json` / `--markdown`
- **Continuity diff CLI (roadmap #9)** — `tools/continuity_diff.py` clip-to-clip and clip-vs-memory-bank continuity reports; CLI `sequence continuity-diff` for Continuity Guardian / QA
- **Multi-character identity arbiter (roadmap #8)** — `tools/multi_character_arbiter.py` primary/secondary DNA weights, conflict rules, multi inject blocks; CLI `sequence cast arbitrate|inject`; skill + Role Card
- **Emotional temperature gate (roadmap #7)** — `tools/emotional_temperature.py` normalizes `emotional_temperature_curve`, infers observed temp, flags flat/spike/off-plan; CLI `sequence temp set|show|gate`; extend prompts may include planned temperature
- **Audio momentum integrity (roadmap #6)** — `tools/audio_momentum.py` diffs AMV across stitches (dialogue/SFX/music/lip-sync); Chain QA Assist uses evidence for `audio_momentum_sync`; CLI `sequence amv-check`
- **Extend re-gen loop (roadmap #5)** — `tools/extend_regen.py` builds fix prompts from chain QA + drift/seam + memory bank; per-clip/sequence attempt budget; CLI `sequence regen plan|apply|run` (run spends one attempt via existing sequence runner)
- **Sequence memory bank (roadmap #4)** — `tools/sequence_memory.py`; `sequence.json` `memory_bank` (schema 1.0+1.1); handoff/extend-prompt embed running cast/prop/lighting/audio state; CLI `sequence memory show|sync`
- **Long-form continuity evidence loop (v1)** — `tools/identity_drift.py`, `tools/seam_report.py`; Chain QA Assist v2 blends drift + seam into SFW scores with `evidence` block; CLI `sequence drift-score`, `sequence seam-report`, and `qa-assist --dna`

### Fixed

### Changed
- **Plugin/docs hygiene (46 skills + unified 4.5 copy)** — `plugin.json` / `marketplace.json` descriptions no longer market dual-stack; marketplace skill count **44 → 46**; AGENTS/README/UPGRADE_GUIDE registry lines aligned.
- **All agents → Grok 4.5** — remaining **18** skills that lacked Model Layer now embed `## Model Layer (Grok 4.5 · studio v3.6.7)` (DoP v3.3, Performance, Foley, Key Art, Trailer, Stunt, VFX, Localization, Narrative Arc, Color Grading, Production Designer, Continuity Guardian, i2i refiners, NSFW chain QA, AI video upscaler, cinematic-ffmpeg, Mega Production Architect). Full suite: **46/46** skills + all Role Cards on Grok 4.5 orchestration default (`grok-4.3` 1M opt-in only).
- **Docs: public stack copy → unified Grok 4.5** — README hero/badge/aliases/footer, Quick Start, MASTER_PROMPT, RELEASE_NOTES, UPGRADE_GUIDE, CONTRIBUTING, `commands/cinematic.md`, `scripts/lib/cinematic_studio_common.sh` no longer market dual-stack (4.3-as-cinematic); code already had `STACK_CONTRACT` on `grok-4.5`.
- **Skill hygiene (46 skills)** — `required_skills.manifest` adds `arc-replan-copilot` + `multi-character-identity-arbiter` (parity with disk / `plugin.json`); docs and marketplace copy updated from 44 → 46 skills (AGENTS, README, MASTER_PROMPT, RELEASE_NOTES, installation guide).
- **Cinematic chat default → `grok-4.5`** — `STACK_CONTRACT["cinematic"]` unified with Build/CLI on `grok-4.5`; `grok-4.3` remains opt-in for 1M context (`--chat-model grok-4.3` / alias `long-context`). Alias `cinematic` now resolves to `grok-4.5`. `models verify` warns on unified chat defaults instead of failing.
- **Docs & Role Cards** — MODELS, AGENTS, README, MASTER_PROMPT, Quick Start, Project Bible, RELEASE_NOTES, Studio Director / Mega / Prompt Master / Sequence / Quota / AGENT_INDEX, commands, Web UI, config example aligned to unified default.
- **Agents + skills enhanced for Grok 4.5** — new `references/agents/MODEL_LAYER_v3.7.1.md`; all Role Cards embed Model Layer; all skills carry stack tables and 4.5 operating rules.

---

## [3.7.1] - 2026-07-10

### Added
- **Imagine Agent Mode Handoff protocol (v3.7.1)** — official Studio Director–owned routing from planning into four execution surfaces: `grok_build_tools`, `grok_agent_acp`, `grok_com_imagine`, `xai_api`. Canonical doc: `references/agents/IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md` (mirrored under studio-director + main skill `references/`).
- **Packet type `imagine_agent_mode_handoff`** — required fields for pipeline spec, prompt, Sound Layer (video), model stack, quota note, return path, handoff steps; validated by `handoff-packet-validator`.
- **CLI `imagine agent-handoff`** — emit markdown/json/clipboard handoffs from batch shots or sequence clips (`--surface`, `--mode`).
- **`build_agent_mode_handoff` / `agent_mode_handoff_to_markdown`** in `tools/imagine_bridge.py`.
- **Studio Director Role Card + skill** — own surface decision, specialist-before-handoff, block incomplete video packets, close loop with QA.
- **Main skill `grok-imagine-cinematic-studio`** — activation phrase v3.7.1; `ACTIVATE IMAGINE_AGENT_MODE_HANDOFF` / `HANDOFF TO IMAGINE AGENT MODE`.

### Changed
- **Studio version** — `VERSION` / CLI / Web UI / plugin manifests / `STUDIO_COMPATIBILITY_VERSION` → **3.7.1**
- **Public suite docs → Grok 4.5 / v3.7.1** — README, Quick Start, MASTER_PROMPT, UPGRADE_GUIDE, Project Bible, installation guide, MODELS, RELEASE_NOTES, config example, installer scripts; correct aliases (`cinematic` → 4.5); badge + activation phrases.
- **Handoff code quality (review follow-up)** — role-card inventory fix; default Imagine video 1.0; `tools/handoff_schema.py`; unified `build_handoff` / renderers + CLI `resolve_handoff_subject`; single canonical protocol doc (skill mirrors are pointers only).
- **All skills → Grok 4.5 operating notes (v3.7.1)** — every SKILL.md Model Layer footer adds reasoning/1M/Imagine-tool rules; meta-installer + install_paths → v3.7.1; production-bible-workflow defaults video 1.0 + handoff; github-repo-manager tool paths modernized; i2i skills use `image_edit`; no remaining v3.6.7 skill branding.
- **All Role Cards + skills → Model Layer (Grok 4.5 · studio v3.7.1)** — stamp and links updated across 80+ agent/skill docs; canonical `MODEL_LAYER_v3.7.1.md` (v3.6.7 file is a pointer); `skill-agent-architect` Role Card template and skill revised off Grok 4.3 dual-stack language; `AGENT_INDEX` VIDEO_PIPELINE_SPEC documents 1.0 cost default + 1.5 native-audio variant.

---

## [3.6.7] - 2026-07-09

### Added
- **Guided Production Bible wizard** — shared stage data (`tools/cli/bible_stages.py`) maps answers to kwargs for existing `build_production_bible` (no second schema). CLI: `create-bible --wizard` (TTY-only; direct `create-bible "Title"` remains default for scripts). Web UI: Production → Guided Bible Creator multi-step form. Free-text logline/characters/world/tech notes roll into `notes`. Design + implementation plan under `docs/superpowers/`.

### Fixed
- **`plugin catalog check --release` chicken-and-egg** — release pin accepts install SHA == HEAD **or** ancestor with only `.grok-plugin` catalog paths after it (pin-only follow-up). A commit cannot embed its own hash in `marketplace.json`; docs/CLI workflow updated (content → pin → catalog-only commit).

### Changed
- **Studio version** — `VERSION` / CLI / Web UI / plugin manifests → **3.6.7**

---

## [3.6.6] - 2026-07-09

### Added
- **Dual model stack** — cinematic default `grok-4.3` (1M); Build/coding default `grok-4.5`; recommend Grok Build CLI **≥ 0.2.93**
- **`grok-4.5` registry entry** — $2/$6 per 1M ($0.50 cached), 500k context; aliases (`4.5`, `grok-4.5-latest`, `grok-build-latest`, `coding`, `grok-build`, `build`); `grok-build-0.1` marked legacy
- **`tests/test_models_chat.py`** — dual-default, alias, and `normalize_chat_model` coverage
- **`normalize_chat_model` + CLI warn** — unknown `--chat-model` values warn and fall back to cinematic default

### Changed
- **`tools/models.py`** — `STACK_CONTRACT` → `ROLE_DEFAULTS` (literals once); cached alias maps; data-driven `verify_model_compatibility()` + soft `grok --version` probe; `REQUIRED_MODEL_ROLES`
- **Docs & Role Cards** — README, AGENTS, MASTER_PROMPT, Quick Start, MODELS, Project Bible, RELEASE_NOTES, Studio Director / Mega / Prompt Master / Quota / AGENT_INDEX aligned to dual stack
- **Studio version** — `VERSION` / CLI / Web UI / plugin manifests → **3.6.6**

---

## [3.6.5] - 2026-06-24

### Added
- **`verify_model_compatibility()`** and **`models verify`** CLI — validates Grok 4.3 + Imagine 1.5 + Grok Build registry
- **`references/agents/Mega_Production_Architect.md`** — v3.6 Role Card with model stack
- **`config/grok-build.example.toml`** — Grok Build fork configuration template
- Restored full **`references/agents/AGENT_INDEX.md`** with model compatibility table and 11 activation presets

### Changed
- **`tools/project_state.py`** — canonical `load_project_state` / `save_project_state`; removed duplicate loaders from CLI, `character_dna`, and `quota_optimizer` (legacy files auto-merge missing keys)
- **`tools/cli/`** — extracted `models_commands`, `bible_commands`, `studio_commands`, and `production` builders; main CLI slimmed down
- **Model stack wiring** — `build_video_pipeline_spec()` and `model_stack_summary()` in `tools/models.py` for consistent Grok 4.3 / Grok Build / Imagine 1.5 usage
- **CLI** — `status`, `create-bible`, `cost-simulate`, and `generate-prompt` embed model stack + `VIDEO_PIPELINE_SPEC`; agents list aligned to v3.6
- **Web UI** — master prompt, Production Bible export, and xAI API calls include chat/video models and 1.5 pipeline spec
- **`character_dna.py` / `sequence_chain.py`** — scaffolds and handoffs embed `model_stack` + `VIDEO_PIPELINE_SPEC`
- **Role Cards** — Imagine Prompt Master, Sequence Director, Cinematic Sequence Extender, Workflow Quota Optimizer updated for v3.6 models
- **Skills** — `imagine-prompt-master`, `mega-production-architect` aligned to 1.5 native schema
- **Installer verify** — `cinematic_studio.sh verify` runs `models verify`
- **Quick Start Guide** — model stack section (§0)
- **Studio Director Role Card** — model layer table for Grok Build, Grok 4.3, and Imagine 1.5
- **Project Bible template** — v3.6 model stack and `VIDEO_PIPELINE_SPEC` section

---

## [3.6.4] - 2026-06-21

### Changed
- README, MASTER_PROMPT, RELEASE_NOTES, CLI, and Web UI aligned to v3.6.4
- `workflow-quota-optimizer` and `grok-imagine-cinematic-studio` skills updated with current pricing and NSFW pipelines

### Added
- **NSFW Sequence Extender** — `tools/nsfw_sequence_extender.py` for 30–120s+ sensual extension
- **`nsfw-sequence-extender` skill** — erotic pacing curve, camera vocabulary, artifact QA, extend protocol
- **CLI `nsfw extend`** — `plan`, `chain`, `prompt`, `camera`, `qa`, `export`
- Prompt chain + extension_plan.md output per sequence in `sequences/<slug>/`
- NSFW chain QA (8 checks) for hands, skin, fabric, explicit zones, intimate physics
- AGENT_INDEX preset #11 for NSFW Sequence Extension

### Changed
- `cinematic-sequence-extender`, `erosforge-nsfw-director`, `nsfw-quota-orchestrator` skills updated with integration notes

---

## [3.6.3] - 2026-06-21

### Added
- **NSFW Quota Orchestrator** — `tools/nsfw_orchestrator.py` with batch planning, i2v decisions, retry strategies, daily reports
- **`nsfw-quota-orchestrator` skill** — references, `plan_batch.py` script, Workflow Quota Optimizer integration
- **CLI `nsfw` commands** — `plan`, `list`, `next`, `decide`, `retry`, `record`, `report`
- AGENT_INDEX preset #10 for NSFW Quota Batch (Heavy)

---

## [3.6.2] - 2026-06-21

### Added
- **`tools/models.py`** — canonical Grok Build CLI, xAI chat, and Imagine model registry
- **`references/MODELS_v3.6.md`** — model selection guide and slug reference
- **CLI `models list`** — display all current Grok Build and xAI model slugs
- **`--chat-model` / `--video-model`** on `generate-prompt` and quota commands

### Changed
- **Quota optimizer** — xAI USD pricing ($0.08/sec for 1.5, $0.05/sec for 1.0, $0.02–$0.05/image)
- **Web UI** — Imagine video model selector, xAI chat model picker (`grok-4.3` / `grok-build-0.1`)
- **Docs** — README, MASTER_PROMPT, AGENTS.md, pricing_model_v3.6.md aligned to Grok Build models

---

## [3.6.1] - 2026-06-21

### Added
- **Character DNA pipeline** — `tools/character_dna.py` library with scaffold, handoff, lock, and prompt injection
- **`character-dna-extractor` skill** — extraction template, handoff/inject scripts, Identity Lock integration
- **CLI `dna` commands** — `init`, `save`, `list`, `show`, `handoff`, `lock`, `inject`
- **Web UI Character DNA panel** — create profiles, lock to Identity Bank, generate injection blocks
- **Long-form sequence pipeline** — `tools/sequence_chain.py` with 1.5 extend/stitch handoffs and 10-point chain QA
- **CLI `sequence` commands** — `init`, `add-clip`, `handoff`, `extend-prompt`, `qa`, `health`
- **Extend/stitch protocol docs** — `extend_stitch_protocol_v3.6.md` + `chain_qa_checklist.md`
- **Quota orchestration** — `tools/quota_optimizer.py` with per-second 1.5 pricing, session tracking, risk assessment
- **CLI `quota` commands** — `estimate`, `clip`, `sequence`, `dashboard`, `budget`, `record`, `optimize`
- **Sequence cost integration** — `sequence estimate-cost` + `quota sequence`
- **Web UI quota panel** — live 1.5 per-second estimator with risk level and tier selection
- **AI Polish Director** — 23rd agent for final post-production upscale, face restoration, and delivery polish
- **`ai-video-upscaler` skill** with GPU Real-ESRGAN path, async batch processing, pure-Python fallback, and model installer
- Post-production pipeline: QA Go → Color Grade → AI Polish Director → Studio Director sign-off
- New preset #9 in `references/agents/AGENT_INDEX.md`: Final Delivery Polish

### Changed
- `AGENTS.md` restored and updated for v3.6 with AI Polish Director section
- `MASTER_PROMPT.md` updated to 23 agents with post-production activation commands
- `grok-imagine-cinematic-studio` skill updated to reference 23-agent suite
- `docs/guides/Quick_Start_Guide.md` Phase 4 now includes final delivery polish step

### Fixed
- Restored stub placeholder content in `AGENTS.md`, `references/agents/AGENT_INDEX.md`, and `references/agents/MASTER_PROMPT.md`

---

## [3.5.1] - 2026-06-02

### Added
- Complete **22-agent Role Card system** in `references/agents/` with full structure:
  - Core Mission
  - v3.5 / v4.0 Upgrades
  - Key Responsibilities
  - Specialized Protocols
  - Decision Frameworks
  - Output Formats
  - Activation Triggers
  - Integration Notes
- Comprehensive `AGENT_INDEX.md` in `references/agents/`
- Improved CI workflow (`cinematic-agent-workflow-ci.yml` v3.5) with:
  - Role Card structure validation
  - `references/agents/` directory checking
  - Configurable `validation_mode` (standard / strict / full)
  - Better agent detection logic
- Updated documentation:
  - Revised `README.md` (accurate 22-agent count, Role Card emphasis)
  - Updated `docs/guides/Quick_Start_Guide.md` v2.0 with improved workflow and specialist table
- Full `grok-imagine-cinematic-studio` skill pulled with latest `MASTER_PROMPT_v3.5.md`

### Changed
- Standardized all agent files to `*_v3.5.txt` naming
- Expanded and refined all 22 agent Role Cards to full detailed format
- Improved consistency across agent activation commands
- Better alignment between project structure and documentation

### Fixed
- Broken filename in agents directory (`Continuity_Consistency_Guardian`)
- Outdated agent counts and references in documentation
- Missing references to the new `references/agents/` Role Card system

---

## [3.5.0] - 2026-06

### Added
- Full 22-agent cinematic production system
- ErosForge NSFW Director with artistic standards
- Cinematic Sequence Extender for long-form content
- Native audio design integration
- Production Bible system
- Modular prompt template architecture
- Comprehensive agent personality versioning
- Streamlit Web UI
- Python CLI toolkit

### Changed
- Major reorganization of agent folder structure by production department
- Improved continuity and identity lock systems

## [3.4.0] - Previous

- Initial multi-agent orchestration
- Core leadership agents (Studio Director + Mega Production Architect)
- Basic Production Bible support