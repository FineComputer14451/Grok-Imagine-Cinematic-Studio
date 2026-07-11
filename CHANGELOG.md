# Changelog

All notable changes to Grok Imagine Cinematic Studio will be documented in this file.

## [Unreleased]

### Added
- **Specialist-order checklist** — optional `specialist_checklist` on agent-mode handoffs; `--checklist` on `imagine agent-handoff`; GHR-09/GHR-10 in readiness (incomplete steps block under `--strict-handoff`).

### Fixed
- **Still compare** — use Pillow `get_flattened_data()` instead of deprecated `getdata()` in `compare_stills_soft`.

## [3.8.2] - 2026-07-11

### Added
- **Generation handoff readiness** — semantic checks for `imagine_agent_mode_handoff` (motion cues, references, return_path); validator warnings; `imagine agent-handoff --strict-handoff`. Helper: `evaluate_imagine_handoff_readiness`.
- **Post-delivery pipeline readiness** — `evaluate_delivery_pipeline_readiness`; `--strict-delivery` on `sequence polish` / `sequence deliver` (soft by default).
- **Validator `--strict-handoff`** — handoff-packet-validator treats agent-mode readiness blockers as hard failures (exit 1); default remains warn-only.
- **Streamlit Community Cloud deploy** — root `requirements.txt` + `runtime.txt` (Python 3.12), `.streamlit/config.toml` + secrets example, secrets→env key resolution, cloud banner, and `docs/guides/streamlit_cloud_deploy.md`.

### Changed
- **Studio version** — `VERSION` / plugin catalog / compatibility → **3.8.2**

## [3.8.1] - 2026-07-11

### Added
- **Identity Continuity Protocol v1.0** — deepen existing long-form agents: canonical ICP (`references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md`), `drift_evidence` handoff mapping from clip `identity_drift`, warn-only validator checks (no new agents; no CLI hard-block by default).
- **`--strict-identity`** on `sequence handoff` and `sequence extend-prompt` — opt-in hard-fail when drift evidence is missing or identity risk (default soft path unchanged). Helper: `evaluate_identity_strict_gate`.
- **Identity drift evidence quality** — multi-signal soft-PIL still compare, still path resolve (CLI flags + clip fields), modest facial DNA weighting; `sequence drift-score --ref-still` / `--clip-still`.

### Fixed
- **Role card inventory** — exclude `IDENTITY_CONTINUITY_PROTOCOL_v3.8.md` from Role Card counts (`ROLE_CARD_SHARED_DOCS`) so `cinematic-studio validate` stays clean.

### Changed
- **Studio version** — `VERSION` / plugin catalog / compatibility → **3.8.1**

## [3.8.0] - 2026-07-11

### Added
- **Plugin modularity (full suite + 5 packs)** — marketplace lists **6 plugins** from `config/plugin_packs.yaml`: recommended full suite `grok-imagine-cinematic-studio` plus satellites **core**, **camera-image**, **sequence-narrative**, **nsfw**, **delivery-post**. Pack manifests under `.grok-plugin/packs/<id>/plugin.json`; exclusive skill membership validated across packs.
- **Plugin packs CLI** — `cinematic-studio plugin packs` lists full suite + pack skill/command counts and soft `requires`; catalog generation writes pack-aware marketplace entries and satellite manifests.
- **Declutter `full_suite_wins`** — when full suite and one or more satellite packs are both installed, declutter prefers the full suite and removes satellite skill dupes (`config/plugin_packs.yaml` → `declutter.policy: full_suite_wins`).

### Changed
- **Studio version** — `VERSION` / plugin manifests → **3.8.0**
- **Install / taxonomy docs** — README + installation guide pack install matrix; `references/SKILLS_TAXONOMY.md` marketplace packs section; AGENTS marketplace multi-plugin + declutter note

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