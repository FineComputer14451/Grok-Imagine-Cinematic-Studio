# Changelog

All notable changes to Grok Imagine Cinematic Studio will be documented in this file.

## [Unreleased]

### Changed
- **CLI reference expansion** — `docs/CLI_REFERENCE.md` matches the live Typer tree (sequence nested tools, sfw/nsfw plate·motion, wave-a, handoff validate, TUI `--print`, meta installer); corrects `validate --strict-handoff` (strict flags live on `handoff validate` / `imagine agent-handoff`)
- **25-agent core wording** — retire stale “23-agent” strings in CLI help, activation prompt, PDF report, and `/cinematic` slash command (align with `list-agents` core count)
- **TUI command palette** — `/` or Ctrl+P opens allowlisted action search; KPI bar under status strip; `y` saves orient brief to `artifacts/tui_orient_brief.txt`; scroll preserved on refresh
- **TUI non-TTY fallback** — `cinematic-studio ui --print` (and bare `ui` without a TTY) prints the orient dashboard instead of hard-failing; optional `artifacts/tui_orient_brief.txt`

## [3.8.9] - 2026-07-26

### Changed
- **Studio version** — `VERSION` → **3.8.9**; activation `Activate Grok Imagine Cinematic Studio v3.8.9`
- **TUI Home view modes** — `1` compact / `2` ops / `3` full / Tab cycle; `p` pause auto-refresh; dual-column readiness|convergence; launcher/cockpit type-to-filter
- **Streamlit Dashboard view modes** — compact / ops / full density (TUI 1/2/3 parity); session-persisted radio; section visibility matches control-plane Home
- Handoff `PROTOCOL_OK` includes **3.8.9**; `STUDIO_COMPATIBILITY_VERSION` aligned

## [3.8.8] - 2026-07-26

### Changed
- **Studio version** — `VERSION` → **3.8.8**; activation `Activate Grok Imagine Cinematic Studio v3.8.8`
- **TUI Home density** — `cinematic-studio ui` Home is a multi-panel ops board (status strip, Quota | Studio, Sequences, dedicated Chain QA, Characters, optional Recent Jobs) instead of a single Markdown wall; still driven by `build_studio_dashboard()`
- **TUI Home attention + severity** — ATTENTION board from snapshot signals; status strip severity CSS (ok/warn/critical); Home keys **d** doctor · **v** validate · **m** models · **k** stack · **s** quota sync
- **Streamlit Web UI dashboard density** — ops status strip + Attention board (shared TUI alert/severity helpers), dedicated Chain QA table, quota recon/alignment, recent jobs, sidebar ops severity, refresh control
- **Operator UX Phase 1 (Orient + Health)** — control-plane contract tests; Streamlit Dashboard health action strip; doctor **control plane** check; Quick Start operator loop
- **Operator UX Phase 2 (Produce + Gate)** — `readiness` rollup on studio dashboard (identity/plate-motion/chain QA + next actions); TUI READINESS panel + DNA/sequence next-step coaching; `cinematic-studio handoff validate`; TUI/Web handoff validate entry; Web DNA lock feedback; chain QA no-go next actions
- **Operator UX Phase 3 (Multi-agent + Deliver)** — Parallel Brief log discovery; convergence checklist for agent-mode handoff; delivery polish/deliver readiness rollup; TUI panels + Cockpit dry-run polish/deliver + wave-a briefs + imagine bridge; Web Dashboard/Tools parity
- Handoff `PROTOCOL_OK` includes **3.8.8**; `STUDIO_COMPATIBILITY_VERSION` / agent version stamps aligned

### Added
- **Operator UX North-Star** — journey-first control plane design (`docs/development/superpowers/specs/2026-07-26-operator-ux-north-star-design.md`)
- **Wave A agent scaffold (P0)** — eight specialists: `plate-motion-readiness-lead`, `contact-micro-physics-specialist`, `hair-makeup-continuity`, `dialogue-adr-director`, `score-temp-music-supervisor`, `title-motion-graphics-lead`, `distribution-crop-strategist`, `parallel-brief-dispatcher` (suite **62** skills; packs updated)
- **Wave A packets (P1)** — `tools/wave_a_packets.py` builders + 8 handoff `packet_type`s; optional field checks; `validate_handoff.py --strict-wave-a`; `attach_wave_a_to_imagine()`
- **Wave A CLI (P2)** — `cinematic-studio wave-a` (plate-motion, contact, hmu, dialogue, score, title, crop, briefs, validate, attach); `--strict-wave-a` on `sfw run` / `nsfw run` / `imagine agent-handoff`
- **Grok Build CLI management** — `cinematic-studio grok status|ensure|update|install` (Method A already ensured the binary on install; now first-class Python CLI + `tools/grok_build_cli.py`)
- **Multi-surface install docs** — shell CLI + **grok.com chat** + **grok.com/imagine** bridge + mobile app matrix in meta-installer skill, installation guide, AGENTS, CLI reference
- **`cinematic-studio handoff validate`** — schema + soft readiness for handoff packets

### Fixed
- **Method A `tools_complete`** — require `grok_build_cli.py`, `cli/grok_cli_commands.py`, and `cli/wave_a_commands.py` so stale `~/Grok-Cinematic-Projects` is refreshed and PATH `cinematic-studio grok` works
- **Meta installer passthrough** — `bash scripts/cinematic_studio.sh grok …` forwards to the Python CLI

## [3.8.7] - 2026-07-25

### Added
- **Parallel Brief Protocol v1.0** (`references/agents/Parallel_Brief_Protocol.md`) — concurrent specialist briefs under MAXIMUM AGENTIC MODE; Foley + NSFW densification patterns; wired into Studio Director + specialist Role Cards
- **Grok Doctor** — CLI health registry (`cinematic-studio doctor` / `grok-doctor`) plus skill/Role Card (`grok-doctor`, `Grok_Doctor.md`)
- **Multi-Clip Continuity Orchestrator** (`multi-clip-continuity-orchestrator`) — multi-clip LAST_FRAME_RECAP / AMV continuity commander
- **Method A Grok Build CLI ensure** — install ensures `grok` ≥ **0.2.93** (`CINEMATIC_SKIP_GROK_CLI` / `CINEMATIC_FORCE_GROK_CLI` / `CINEMATIC_MIN_GROK_CLI`)
- **Costume & Wardrobe Continuity** agent (`costume-wardrobe-continuity`) — nested `wardrobe_lock` on Character DNA (packaged with suite)

### Changed
- **Studio version** — `VERSION` → **3.8.7**; activation `Activate Grok Imagine Cinematic Studio v3.8.7`
- **Suite size** — **54 skills** · **25** Role-Card core agents; packs core **20**, sequence-narrative **16**
- Handoff `PROTOCOL_OK` includes **3.8.7**; `STUDIO_COMPATIBILITY_VERSION` / agent version stamps aligned
- Grok Doctor prefers full git clone when present; quota recon + catalog pin checks hardened
- Quota cascade / dashboard / TUI alignment improvements (ledger-backed recon)

### Fixed
- **`scripts/verify_plugins.sh` / `scripts/release_plugin_catalog.sh`** — prefer in-repo CLI so release pin resolves checkout HEAD (not tools-only PROJECT_DIR)

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
- Handoff readiness `PROTOCOL_OK` includes **3.8.5`; role-card shared-doc allowlist updated

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
