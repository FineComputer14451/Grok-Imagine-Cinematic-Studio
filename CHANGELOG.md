# Changelog

All notable changes to Grok Imagine Cinematic Studio will be documented in this file.

## [Unreleased]

### Added
- **Dual model stack (v3.6.6)** — cinematic default `grok-4.3` (1M); Build/coding default `grok-4.5`; min Grok Build CLI **0.2.93**
- **`grok-4.5` registry entry** — $2/$6 per 1M, 500k context, aliases (`4.5`, `grok-4.5-latest`, `grok-build-latest`, `coding`); `grok-build-0.1` marked legacy
- **`tests/test_models_chat.py`** — dual-default and alias coverage
- **Grok plugin marketplace** — `.grok-plugin/marketplace.json`, `plugin.json`, and `scripts/generate_plugin_index.py` for `grok plugin marketplace add FineComputer14451/Grok-Imagine-Cinematic-Studio`
- **`verify --plugin`** — validates Grok plugin checkout (44 skills, 11 slash commands, model registry)
- **`cinematic-studio plugin`** — `status`, `list`, and `catalog` subcommands (`check [--release]`, `pin`) for manifest, index, and marketplace pinning (via shared `tools/plugin_catalog.py`)

### Fixed
- **`plugin_commands` import** — fix `ModuleNotFoundError: No module named 'tools'` when invoking `python tools/cinematic_studio_cli.py` (import `plugin_catalog` directly to match CLI `sys.path`)
- **Installer manifest sync** — `required_skills.manifest` expanded to 44 skills; release bundle, `verify --all`, and GitHub release zip aligned with the plugin suite
- **Grok marketplace install** — `.grok-plugin/marketplace.json` uses pinned `url`+`sha` source (required for `grok plugin install …@finecomputer14451/grok-imagine-cinematic-studio`); `generate_plugin_index.py` syncs sha from `git HEAD`

### Changed
- **`tools/models.py`** — `STUDIO_COMPATIBILITY_VERSION` → 3.6.6; dual stack via `STACK_CONTRACT` → `ROLE_DEFAULTS` (literals once); cached alias maps; data-driven verify + soft `grok --version` probe; `REQUIRED_MODEL_ROLES`; `normalize_chat_model` + CLI warn on unknown `--chat-model`; recommend CLI ≥ 0.2.93
- **Docs & Role Cards** — README, AGENTS, MASTER_PROMPT, Quick Start, MODELS, Project Bible, Studio Director / Mega / Prompt Master / Quota / AGENT_INDEX aligned to dual stack
- **Meta-installer docs** and `references/installation_guide.md` — explicit Method A (meta/zip) vs Method B (Grok plugin) install paths
- **Release build scripts** — normalize relative zip output paths before staging `cd` (fixes `artifacts/*.zip` builds)
- **Plugin tooling** — centralized discovery/build/pin/validate into `tools/plugin_catalog.py`; `generate_plugin_index.py`, verify_plugins.sh, and release_plugin_catalog.sh now delegate to CLI + shared module; atomic `.grok-plugin/` commit hygiene enforced

### Removed
- **Deprecated `agents/`** — legacy v3.4/v3.5 stubs; canonical Role Cards remain in `references/agents/`
- **Stale skill mirrors** — duplicate Role Cards and v3.5 prompts under `grok-imagine-cinematic-studio/references/`
- **Duplicate `references/agents/MASTER_PROMPT_v3.6.md`** — root `MASTER_PROMPT_v3.6.md` is canonical

### Changed
- Moved `REPOSITORY_STRUCTURE.md` and `Example_Production_Bible_Example.md` into `docs/archive/` and `examples/`
- **CI workflow** — removed deprecated `agents/**` path filters and validation scan
- **README.md** — comprehensive update for v3.6.5 (plugin marketplace, 44-skill suite, model stack everywhere, updated architecture/project structure, agent crew to v3.6.5, CLI/Web UI examples, links)
- **Web UI** — migrated all Streamlit widgets (st.dataframe, st.button, st.form_submit_button) from deprecated `use_container_width=True` to `width="stretch"`. Added `str()` guard for dashboard health column for dataframe robustness. Affects dashboard, dna, imagine, nsfw, production, tools pages.
- **Imagine 1.0 installed as default** — DEFAULT_IMAGINE_VIDEO_MODEL switched to `grok-imagine-video` (1.0, $0.05/sec); 1.5 remains available for native-audio. Updated models.py verify, web_ui, MODELS doc, and compatibility notes.

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
- `MASTER_PROMPT_v3.6.md` updated to 23 agents with post-production activation commands
- `grok-imagine-cinematic-studio` skill updated to reference 23-agent suite
- `Quick_Start_Guide.md` Phase 4 now includes final delivery polish step

### Fixed
- Restored stub placeholder content in `AGENTS.md`, `references/agents/AGENT_INDEX.md`, and `references/agents/MASTER_PROMPT_v3.6.md`

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
  - Updated `Quick_Start_Guide.md` v2.0 with improved workflow and specialist table
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