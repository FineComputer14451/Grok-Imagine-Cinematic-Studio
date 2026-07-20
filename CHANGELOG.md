# Changelog

All notable changes to Grok Imagine Cinematic Studio will be documented in this file.

## [Unreleased]

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

### Changed
- **Studio version** — `VERSION` → **3.8.5**
- Residual Grok 4.3 language removed from the upgraded skill set
- All upgraded skills now declare preferred model routing and dual Imagine Video support consistently

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
