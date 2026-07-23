# Changelog

All notable changes to Grok Imagine Cinematic Studio will be documented in this file.

## [Unreleased]

### Added
- **Grok Doctor** — `scripts/grok_doctor.sh`, `cinematic-studio doctor`, and `grok-doctor` PATH entry for Grok Build + Cinematic Studio health checks (`--quick`, `--json`, `--strict`)

### Changed
- **Grok Doctor** is now a **Python check registry** (`tools/doctor.py` + `doctor_checks.py` + `doctor_types.py`) reusing `models.verify_model_compatibility`, `studio_health`, and `plugin_catalog`. Shell entrypoints are thin launchers; `cinematic-studio doctor` routes through the Python CLI (not the meta installer).
- Doctor uses a **declarative `CheckSpec` registry** (`quick` / `skip_external` filter flags only — no fake PASS rows). Catalog **artifact** errors FAIL; pin-drift WARNs. Model stack summary is embedded in verify detail (no free PASS after FAIL).
- `models.verify_model_compatibility` splits **`warnings`** (operational) vs **`notes`** (intentional stack info). Public helpers: `version_tuple`, `cli_version_at_least`, `probe_grok_cli`.

## [3.8.6] - 2026-07-21

### Added
- **Clean release packaging** for full dual-model completion (post–v3.8.5 systematic alignment)
- Fresh install zips built from complete **51-skill** suite with full `model_compatibility` coverage

### Changed
- **Studio version** — `VERSION` → **3.8.6** (docs, installers, packs, activation, registry compatibility)
- Activation phrase: `Activate Grok Imagine Cinematic Studio v3.8.6`
- Handoff `PROTOCOL_OK` includes **3.8.6**; `STUDIO_COMPATIBILITY_VERSION` / `STUDIO_AGENT_VERSION` aligned

### Notes
- v3.8.5 remains the dual-model feature wave; **3.8.6** is the polished install/release pin after full-repo completion (models API restore, Generation Tracker, meta-installer restore, 51-skill dual-model finish).

## [3.8.5] - 2026-07-20

### Added
- **Full v4.5 Dual-Model Wave** — 16 core skills upgraded to uniform Grok 4.5 / v9-4p5 Model Layer with explicit dual Imagine Video 1.0 + 1.5 Native support:
  - **Identity & Continuity**: `character-dna-extractor`, `identity-lock-specialist`, `multi-character-identity-arbiter`, `continuity-consistency-guardian`
  - **Sequencing & Direction**: `sequence-director`, `studio-director`, `cinematic-sequence-extender`, `extend-frame-to-video`
  - **Prompting & Assets**: `imagine-prompt-master`, `reference-asset-curator`
  - **Quality & Quota**: `quality-assurance-guardian`, `workflow-quota-optimizer`, `quota-dashboard`
  - **NSFW Pipeline**: `erosforge-nsfw-director`, `nsfw-sequence-extender`, `nsfw-quota-orchestrator`
- Every upgraded skill now includes:
  - Full Model Layer table (`grok-4-auto` / `grok-v9-4p5-multi` / `grok-v9-4p5-chat-expert`)
  - `model_compatibility` YAML block
  - Explicit dual-path (1.5 primary / 1.0 fallback) documentation
  - New or upgraded v4.5 Role Cards under `references/agents/`
  - Updated Core Protocols (MODEL_LAYER_ROUTING, 1.0_1.5_DUAL_SUPPORT, EROSFORGE awareness where relevant)
  - Handoff Packet readiness
- **Generation Tracker CLI** — `cinematic-studio generation log|list|summary|report|update|import-jobs` (`tools/generation_tracker.py`) for local Imagine spend ledger
- **Shared agent docs** — `MODEL_LAYER_v4.5.md`, `IMAGINE_EXECUTION_BRIDGE.md` (excluded from role-card file counts)

### Changed
- **Studio version** — `VERSION` → **3.8.5**; cascade across installer scripts, plugin packs, marketplace, AGENTS/README/MASTER_PROMPT, `/cinematic` command, meta-installer paths
- **Skill suite 48 → 51** — add `cinematic-skill-creator`, `extend-frame-to-video`, `quota-dashboard` to full pack union + `required_skills.manifest`
- Residual Grok 4.3 language removed from the upgraded skill set
- All upgraded skills now declare preferred model routing and dual Imagine Video support consistently
- Handoff readiness `PROTOCOL_OK` includes **3.8.5**; role-card shared-doc allowlist updated

### Changed (full systematic alignment)
- **Complete dual-model wave** — all **51** suite skills now include `model_compatibility` + Grok 4.5 / v9-4p5 Model Layer + dual Imagine 1.0/1.5 notes
- **STUDIO_AGENT_VERSION** unified to `v3.8.5` across DNA / quota / animatic / assembly / SFW tools
- Canonical `references/MODELS.md` points at `MODEL_LAYER_v4.5.md`
- Meta-installer skill body restored (full Method A/B docs) at v3.8.5

### Fixed
- **`tools/models.py` API** — restore full registry helpers required by CLI/handoff (`STUDIO_COMPATIBILITY_VERSION`, `verify_model_compatibility`, stack summary, pricing tables) after the v3.8.5 slim rewrite; keep `grok-4.5` defaults and add opt-in v9-4p5 chat models

## [3.8.4] - 2026-07-19

### Added
- **Interactive CLI TUI (`cinematic-studio ui`)** — Textual home dashboard, allowlisted launcher, and production Cockpit with group separators (Setup / Quota / DNA / Sequence / Health).
- **TUI cockpit v3 scaffold** — DNA lock/handoff, sequence add-clip/handoff, quota sequence estimate, validate/stack, launcher DNA/sequence show; still no spend/wizard (`tools/cli/tui/actions.py`).
- **TUI RunningScreen (async CLI)** — launcher and cockpit actions run on Textual worker threads with a “Running…” screen so the UI stays responsive (`tools/cli/tui/screens.py`).
- **Unified TUI action registry** — single ActionSpec model for launcher + cockpit; forbidden tokens never emitted (`run` / `submit` / `record` / `--wizard`).
- **Plate lock readiness** — `evaluate_plate_lock_readiness` for still→video (`image_to_video` / `reference_to_video`); shot fields `plate_status` (`draft`|`approved`|`locked`); `sfw`/`nsfw` plate set/show; soft warnings always; hard-fail with `--strict-plate` and plate blockers under `imagine agent-handoff --strict-handoff`.
- **Motion brief readiness** — `evaluate_motion_brief_readiness` for all video modes; structured `motion_vector` {action, camera, emotion} preferred; free-text MOTION_CUES soft fallback (MB-01); `--strict-motion` / `--strict-handoff` require full triple (MB-02); `sfw`/`nsfw` motion set/show.
- **Install hardening** — static `cinematic-studio` dispatcher, VERSION pin + CLI wrappers during Method A setup; ComfyUI / Lustify Grok Build guides.

### Fixed
- **TUI confirm re-run hazard (I1)** — after a cockpit write, Confirm/Form are popped before Output so Esc cannot re-execute the same mutating argv.
- **TUI form validation banner (M1)** — plain text on Static (no Markdown markers).
- **TUI form Enter-to-submit (M4)** — Enter in any field shares Submit path (`_try_submit`).

### Changed
- **Spend readiness facade** — `evaluate_generation_spend_readiness` + shared CLI preflight (`cli/spend_preflight.py`); plate/motion set/show on **both** SFW and NSFW; session runner no longer mutates shot dicts; `resolve_execution_mode` on `handoff_schema`; motion extract uses canonical keys only (no silent momentum aliasing).
- **Studio version** — `VERSION` / plugin catalog / compatibility → **3.8.4**
- **Cinematic Studio Meta Installer → v3.8.4** — skill + install paths + wrapper stamp aligned with studio release.

---
*(Full history of earlier releases is preserved in previous commits.)*
