# Changelog

All notable changes to Grok Imagine Cinematic Studio will be documented in this file.

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