# Changelog

All notable changes to Grok Imagine Cinematic Studio will be documented in this file.

## [Unreleased]

## [3.11.4] - 2026-09-04

### Changed
- **Leftover grok-4.5 live defaults** — React Settings/Bible wizard, API `/v1/meta` pickers, Streamlit captions, Academy examples, and agent CLI samples pin **`grok-4.6`**. `grok-4.5` remains a resolve alias (old Bibles/handoffs still normalize). Operator pickers hide 4.5 (same pattern as retired Image Quality).
- **Persisted React chat prefs** — `liveChatModel()` remaps `grok-4.5` / `4.5` / `grok-4.5-latest` → `grok-4.6`.
- **Image 2.0 quota rows** — 1K medium **$0.06**, 2K medium **$0.08** (was $0.05 / $0.07). 1K/2K low stay $0.04 / $0.06. Auto generate still bills low; auto edit bills medium.
- **Studio version** — `VERSION` / `STUDIO_COMPATIBILITY_VERSION` / handoff `PROTOCOL_OK` include **3.11.4**.

### Added
- **Input-image fees** — `image_usd_per_input_image()` / `n_input_images` on `image_usd_per_image()`: Image 1.0 **$0.002**, Image 2.0 **$0.01** per source still.
- **`cinematic-studio` workflow** — `.grok/workflows/cinematic-studio.rhai` (Parallel Brief DoP / Prompt Master / Quota / Identity → handoff verify → director packet). Plan-only; no Imagine generation. Run `/cinematic-studio` or `/workflow cinematic-studio` with `args.brief`.
- **Chat 4.6 copy scan** — `tests/test_chat_46_copy.py` fails if skills/commands recommend sending `grok-4.5` as the live default (alias/wrap/legacy language allowed).

### Fixed
- **Release zip staging** — `build_release_bundle.sh` and `build_meta_installer.sh` use `TMPDIR` and fall back to Python `zipfile` when `zip` is missing (Termux).
- **DNA markdown AUP tests** — `dna_to_markdown` with `nsfw_notes` now attests in CI (fail-closed without `nsfw attest`). Unblocks Multi-Agent Workflow CI.
- **Catalog pin CI race** — `test_live_repo_release_pin_passes` skips the main-push window before auto-pin. PRs and pin-only tips still fail closed.

## [3.11.3] - 2026-09-03

### Changed
- **Official image-edit payload** — multi-ref edits send `images[]` with `type: image_url` (single-ref stays `image`). The unofficial `extra_images` field is no longer sent.
- **Served `model`** — live `/images/generations` and `/images/edits` keep xAI’s response `model` and record `request_model` so logs can confirm the Nov 2 Quality → 2.0 `low` redirect.
- **Agent-facing Quality leftovers** — animatic, SFW batch, NSFW command, ErosForge/NSFW-prompt personas, and the `xai_api` bridge example pin **Image 2.0** (`quality=medium` for hero) instead of sending `grok-imagine-image-quality` (xAI retires that slug 2026-11-02 → 2.0 `quality=low`).
- **Hero batch stills** — `image_quality` shots send `grok-imagine-image-2.0` with `quality=medium` instead of the retired quality slug (which would have redirected to 2.0 `low`). API meta fallback picker no longer lists `grok-imagine-image-quality`.
- **Operator docs pin** — Quick Start, User Guide, Upgrade Guide, CLI Reference, installation, CONTRIBUTING, and marketplace catalog fallback stamp **v3.11.3**.
- **Academy + Role Cards** — Imagine image examples and NSFW/quota routing tables use Image 2.0 (`quality=medium` for hero) instead of the retired quality slug.
- **Imagine bridge packets** — `image_model` quality/pro slugs rewrite to `grok-imagine-image-2.0` (`quality=low`, or `medium` when `image_quality` is set) so grok.com paste no longer names the retired product.
- **Image model pickers** — `ordered_image_model_slugs()` hides the retired quality slug (Streamlit Settings, API meta). `models list` still shows it tagged retired.
- **Persisted quality slug** — Streamlit session and React Settings prefs remap `grok-imagine-image-quality` / `pro` to Image 2.0 so hidden picker values do not snap back to draft 1.0.
- **Studio version** — `VERSION` / `STUDIO_COMPATIBILITY_VERSION` / handoff `PROTOCOL_OK` include **3.11.3**.

### Added
- **`--extra-image-url`** — repeatable extra stills for `imagine submit image_edit` (Image 2.0: up to 5 total). `--reference-image-url` still works as a fallback.
- **Quality-slug copy scan** — `tests/test_image_quality_retirement_copy.py` fails if skills, personas, or slash commands recommend sending `grok-imagine-image-quality` as a live hero model.
- **AUP on planning paths** — `nsfw extend plan|chain|prompt`, `generate-prompt`, Imagine Execution Bridge / Agent Mode packets, and `handoff validate` now run the same fail-closed SpaceXAI AUP gate as Imagine spend (CSAM always; attestation when intimate; no intimate+still-ref).
- **Doctor AUP section** — `cinematic-studio doctor --quick` reports attestation idle/valid/FAIL and 403/429 no-hop.
- **API `/v1/meta/aup`** — attestation status (`valid` / `present` / `attested_at` / `aup_url`) for cockpits. Never returns flag values; SPA cannot write attestation.
- **React NSFW opt-in** — four AUP checkboxes + server attestation required; a single Settings checkbox no longer unlocks the NSFW nav.
- **`aup-audit` workflow** — `.grok/workflows/aup-audit.rhai` (read-only spend / planning / attestation scan + adversarial verify). Run `/aup-audit` or `/workflow aup-audit`.
- **`github-safety-aup` workflow** — `.grok/workflows/github-safety-aup.rhai` (secrets, GitHub Actions, AUP code/docs). Run `/github-safety-aup`.

### Fixed
- **AUP on DNA emit** — `load_character_dna`, prompt blocks, markdown, handoff packets, and `inject_into_prompt` run `gate_dna` / `gate_imagine_prompt`. `dna init --output` no longer writes JSON without the gate.
- **AUP on NSFW still-ref extend** — `plan_nsfw_extension` default is `short_clip`; `reference_frame` / i2v from a source still is fail-closed (`gate_imagine_prompt(..., has_reference_image=True)`).
- **AUP skill shims** — DNA `--file` inject uses `compose_injected_prompt`; NSFW `plan_extension.py` defaults to `short_clip` and exits 1 on AUP refuse.
- **AUP on handoff paste fields** — bridge + `handoff validate` scan `last_frame_recap`, `sound_layer` / dialogue, momentum, and `nsfw_notes` (not prompt-only). Sequence-extend / intimacy packets are Imagine-bound.
- **Doctor AUP idle** — WARN when committed `nsfw_batches/*.json` templates exist without attestation (operator `*/batch.json` still FAIL).
- **CI least privilege** — `cinematic-agent-workflow-ci.yml` sets `permissions: contents: read` and `persist-credentials: false`; `monitor-forks.yml` documents why it needs write.
- **AUP copy** — NSFW pack description, SECURITY.md, and DISCLAIMER.md name the four `nsfw attest` flags and the AUP URL.
- **`.env.*` gitignore** — ignore `.env.local` / `.env.production` (keep `**/.env.example`).
- **Auto-pin main-only** — `auto-repin-plugin-catalog.yml` requires `github.ref == refs/heads/main` before `git push origin HEAD:main`.
- **Write-job owner guard** — `monitor-forks.yml` and auto-pin skip unless `github.repository` is `FineComputer14451/Grok-Imagine-Cinematic-Studio`.
- **Bridge paste re-gate** — `build_handoff` re-runs `gate_planning_subject` after `dna_inject`; markdown/clipboard paste is gated too.
- **AUP on video edit/extend** — `submit_video_edit` and `submit_video_extension` now run the same fail-closed Imagine prompt gate as generate/edit/i2v (CSAM always; attestation when intimate). Sequence extend and `imagine submit` video_edit/video_extend can no longer skip AUP.

## [3.11.2] - 2026-09-03

### Changed
- **Imagine Image Quality retirement** — `grok-imagine-image-quality` (and `pro` aliases) stay in the registry as **deprecated** (`retired_on: 2026-11-02`) but Imagine spend rewrites to **`grok-imagine-image-2.0` with `quality=low`**, matching the [xAI redirect](https://docs.x.ai/developers/migration/imagine-image-quality-nov-2). Hero plates should pin `--model grok-imagine-image-2.0 --quality medium`. Image 1.0 draft default is unchanged.
- **Image 2.0 `quality`** — allowed values `low | medium | auto` (omit = API auto: low for generate, medium for edit). CLI `--quality` help and quota math follow that split. Quality-slug estimates bill as 2.0 low ($0.04), not the old $0.05 list.
- **Image 2.0 edits** — up to **five** source images; `imagine submit image_edit` forwards `--quality`, `--aspect-ratio`, and `--resolution`.
- **Aspect presets** — `21:9` (cinematic ultra-wide) and `5:2` (wide banner) for Image 2.0 stills. Sequence default remains **16:9**.
- **Studio version** — `VERSION` / `STUDIO_COMPATIBILITY_VERSION` / handoff `PROTOCOL_OK` include **3.11.2**.

### Added
- `resolve_image_request()` / `normalize_image_quality()` / `image_max_edit_refs()` in `tools/models.py` (schema **1.6**).
- Doctor WARN when project `model_stack.imagine_image` is still locked to the quality slug.

## [3.11.1] - 2026-09-02

### Added
- **SpaceXAI AUP fail-closed gates** — `tools/aup_gate.py`, `nsfw attest`, 18+/imaginary-adult/no-real-person checks, R-rated cap, 403/429 no region hop
- **`commands` search** — `cinematic-studio commands [query]` lists visible command paths and one-line help; substring match on path + summary (Orient panel). Hidden ghosts stay hidden.
- **SFW / NSFW help panels** — `sfw --help` and `nsfw --help` group Plan / Readiness / Spend / Quality (NSFW adds Extend).
- **Wave A help panels** — `wave-a --help` groups Packets vs Gate (`validate` / `attach`).

### Fixed
- **Stale CLI help** — `list-agents` no longer says studio v3.7.1; `models list` says 4.6 / 1.0 first; `web` drops the PR6 label.
- **Doctor Method A skills** — `~/.grok/skills` overlap with the repo is PASS (Method A), not a declutter WARN, unless `grok plugin list` includes the studio plugin.
- **Installer fallback** — curl/one-liner path without a local `VERSION` file now falls back to **3.11.1** (was stuck on **3.10.0**).

### Changed
- **CLI help IA** — `cinematic-studio --help` groups commands into journey panels (Orient, Health, Produce, Spend, Gate, Deliver, Surfaces, Meta) with one example each. Nested `--help` on `dna`, `sequence`, `plugin`, `imagine`, and `quota` uses the same map (`tools/cli/help_ia.py`). Production argv is unchanged.
- **CLI ghost aliases** — hidden `plugin check` forwards to `plugin catalog check`; `dna extract` and `sequence extend` print the real verbs and exit 2.
- **CLI reference** — `docs/CLI_REFERENCE.md` matches live `--help` (studio v3.11.1, Grok Build ≥ 1.0.5, no fake `dna extract` / `sequence extend` / `validate --strict-handoff`).
- **Typer floor** — `requirements.txt` pins `typer>=0.12.0` (Rich help panels).
- **Studio version** — `VERSION` / `STUDIO_COMPATIBILITY_VERSION` / handoff `PROTOCOL_OK` include **3.11.1**; activation `Activate Grok Imagine Cinematic Studio v3.11.1`

## [3.11.0] - 2026-08-23

### Changed
- **Stack lock** — registry cinematic / Build / CLI agent default is **`grok-4.6`**. `grok-4.5` and `cinematic` / `build` / `coding` aliases resolve to 4.6. Specialist v9-4p5 / `grok-4-auto` still wrap the stack default. Optional 1M remains `grok-4.3`.
- **Grok Build CLI min** — **1.0.5** (`RECOMMENDED_GROK_BUILD_CLI_VERSION`, installer `CINEMATIC_MIN_GROK_CLI_DEFAULT`, doctor probe)
- **Doctor config** — `models.default` PASSes `grok-4.6` and aliases; `fork_secondary_model` PASSes `grok-build` or `grok-4.6`
- **Studio version** — `VERSION` / `STUDIO_COMPATIBILITY_VERSION` / handoff `PROTOCOL_OK` include **3.11.0**; activation `Activate Grok Imagine Cinematic Studio v3.11.0`
- **Operator surfaces** — CLI / TUI / Streamlit / NiceGUI / React / FastAPI banners and pickers lock Grok 4.6; plugin catalog + pack manifests regenerated for **3.11.0**
- **Skill stack defaults** — SKILL.md Model Layer pins and Wave A Role Card stack lines now say **`grok-4.6`** / CLI ≥ **1.0.5** (YAML titles not mass-rewritten; `grok-4.5` remains an alias)
- **Role Card stack tables** — leftover v3.7.1 orchestration rows (`grok-4.5`) on live cards now pin **`grok-4.6`** and point at `MODEL_LAYER_v4.5.md` (archive `MODEL_LAYER_v3.7.1.md` unchanged)
- **Model Layer headings** — live SKILL.md / Role Card sections now read **Model Layer (Grok 4.6 / v9-4p5)**; specialist v9-4p5 routing unchanged
- **Skill H1 / YAML / initiation phrases** — live display language is **Grok 4.6** (`grok-4.5` slug remains an alias); plugin catalog regenerated after YAML description edits

### Fixed
- **25-core identity** — published lists (`AGENTS.md`, `MASTER_PROMPT.md`, operator cheat sheet) now match `CORE_AGENT_CATEGORIES`: Character DNA Extractor is in the 25; ErosForge NSFW Director stays opt-in
- **Studio pin stamps** — `AGENT_INDEX.md` header + Full Studio preset, Wave A Role Card Studio lines, and `scripts/required_skills.manifest` header now say **v3.11.0**
- **Image 2.0 on stills Role Cards** — DNA, Identity Lock, Prompt Master, Key Art, both I2I, and Production Designer now route hero plates to `grok-imagine-image-2.0` and state there is no Video 2.0
- **Role Card `preferred_model` YAML** — nine table-only cards (I2I both, Localization, Narrative, Color, Production Designer, SFW Batch, Stunt, VFX) now declare `model_compatibility` + `preferred_model` (Localization `grok-4-auto`, SFW Batch `grok-v9-4p5-multi`, rest chat-expert)
- **Canonical Role Cards for meta/tools** — GitHub Repo Manager, Quota Dashboard, and Extend Frame to Video live in `references/agents/` (mapped 47); DNA/QA `_v3.5` filename aliases so skill pointers resolve
- **Narrative Arc activation** — primary command is `ACTIVATE NARRATIVE_ARC` (Role Card, skill, index, cheat sheet); `ACTIVATE NARRATIVE_STRATEGIST` kept as alias
- **Grok Doctor Explicit path** — NSFW Prompt Optimizer is documented as a Parallel Brief pattern, not a Role Card; report + handoff sections added
- **Role Card template v4.5** — `skill-agent-architect` scaffold pins studio v3.11.0 and `MODEL_LAYER_v4.5.md`
- **Skill `model_compatibility`** — `grok-imagine-image-tools` and `xai-grok-skill` declare the YAML block
- **AGENT_INDEX buckets** — Costume in Production Pipeline; Plate + Contact in Wave A (match CLI); DoP v3.3 noted as legacy skill only

## [3.10.0] - 2026-08-22

### Added
- **Imagine Image 2.0** — `grok-imagine-image-2.0` in the registry (hero stills / Quality Mode / Responses `image_generation` tool). Aliases: `2.0`, `image-2.0`
- **Official surface catalog** — `imagine_surface_catalog()` maps Image 1.0 / Quality / 2.0 + Video 1.0 / 1.5 to REST endpoints and Agent Mode surfaces A–E. Canonical doc: `references/agents/IMAGINE_SURFACES.md`
- **REST coverage** — `imagine submit` now supports `video_edit`, `video_extend`, `reference_to_video` plus `--resolution`, `--quality`, `--file-id`, `--reference-image-url`, `--voice-id`
- **Agent Mode surface E** — `xai_responses_tool` (aliases `responses`, `image_generation_tool`); mobile alias `grok_mobile_imagine` → `grok_com_imagine`
- **Execution modes** — `video_edit` and `video_extend` (Video 1.0 only)
- Control plane — API `production-options` exposes `image_models`, `imagine_surfaces`, `imagine_execution_modes`; Streamlit/React image pickers; dashboard `imagine` routing snapshot

### Changed
- Hero / pass-2 / Quality Mode stills route to **Image 2.0** (legacy `grok-imagine-image-quality` remains registered)
- Video 1.5 quota uses resolution rates (720p **$0.14/s**, 1080p **$0.25/s**); `VIDEO_PIPELINE_SPEC` emits `version` + resolution
- Studio version — `VERSION` → **3.10.0**; `STUDIO_COMPATIBILITY_VERSION` / `PROTOCOL_OK` include **3.10.0**; activation `Activate Grok Imagine Cinematic Studio v3.10.0`
- There is **no** `grok-imagine-video-2.0` — 2.0 is Image only

### Fixed
- **Method A CLI payload** — install/update copies `studio_core/` and the full `tools/` tree (including `cli/tui/`) so `cinematic-studio` can import after a Method A install
- **Release zip builder** — `build_release_bundle.sh` ships the same complete payload (was a shallow `*.py` glob)
- **Verify Python** — `models verify` uses the wrapper venv interpreter (`PROJECT_DIR/.venv`) instead of system `python3`
- **Doctor Method A** — missing Grok plugin is PASS when core Method A skills are present; high `~/.grok/skills` count is not a declutter warning
- **Curl install fallback** — if the GitHub release zip 404s, acquire the GitHub `main` archive (do not require a local clone)
- **Install next-steps** — do not `cp` over an existing `~/.grok/config.toml`; Kali recipe prefers `uv venv`
- **Spend-gate mode aliases** — `resolve_execution_mode` maps batch shorthand (`i2v`, `still`, `video`, …) to official modes so plate/motion readiness no longer silently skips when shots only set `recommended_mode: "i2v"`

## [3.9.1] - 2026-08-03

### Added
- **React / TanStack cockpit** (`web_react/`) — Streamlit page-parity SPA on FastAPI: Dashboard, Production, DNA, Sequences, Imagine, Quota, Guided Bible, Tools, Settings, NSFW (opt-in)
- **`cinematic-studio web-react`** — Vite dev/preview launcher (Node 20+); proxies `/v1` + `/health` to `studio_api`
- **API meta + guided Bible** — `GET /v1/meta/*` (env, options, agents, role cards); `GET/POST /v1/bible/stages|validate|guided` (never `--wizard`)
- **Bible → DNA/sequence handoff** — session seeds ActionSpec forms after guided generate
- **Smoke** — `web_react` unit tests, `npm run test:smoke` (HTTP), optional Playwright e2e

### Changed
- **Studio version** — `VERSION` → **3.9.1**; `STUDIO_COMPATIBILITY_VERSION` / `PROTOCOL_OK` include **3.9.1**
- **WEB_SHELLS** — multi-shell matrix documents Streamlit · NiceGUI · React · API

## [3.9.0] - 2026-08-02

### Added
- **`studio_core` service layer** — `build_studio_dashboard`, ActionSpec registry, `execute_action` (in-process + subprocess) shared by TUI / Streamlit / NiceGUI
- **NiceGUI web shell** — `cinematic-studio web` routes: Dashboard, Production, DNA, Sequences, Imagine, Quota (`web_nicegui/`, optional `requirements-nicegui.txt`)
- **Dual-run guide** — [`docs/guides/WEB_SHELLS.md`](docs/guides/WEB_SHELLS.md)
- **Streamlit ↔ studio_core** — dashboard + Tools ActionSpec actions via `execute_registered`
- **FastAPI control plane** — `cinematic-studio api` (`studio_api/`, optional `requirements-api.txt`)
- **Surface polish** — README/CI for `studio_api`; API `GET /` + CORS; `scripts/smoke_studio_surfaces.py`

### Changed
- **TUI command palette** — `/` or Ctrl+P opens allowlisted action search; KPI bar under status strip; `y` saves orient brief to `artifacts/tui_orient_brief.txt`; scroll preserved on refresh
- **TUI non-TTY fallback** — `cinematic-studio ui --print` (and bare `ui` without a TTY) prints the orient dashboard instead of hard-failing; optional `artifacts/tui_orient_brief.txt`
- **TUI runner** — delegates to `studio_core.services.execute` (`mode=subprocess`); `cli.tui.actions` re-exports core ActionSpec catalog

## [3.9.0] - 2026-07-26

### Changed
- **Studio version** — `VERSION` → **3.9.0**; activation `Activate Grok Imagine Cinematic Studio v3.9.0`
- **TUI Home view modes** — `1` compact / `2` ops / `3` full / Tab cycle; `p` pause auto-refresh; dual-column readiness|convergence; launcher/cockpit type-to-filter
- **Streamlit Dashboard view modes** — compact / ops / full density (TUI 1/2/3 parity); session-persisted radio; section visibility matches control-plane Home
- Handoff `PROTOCOL_OK` includes **3.9.0**; `STUDIO_COMPATIBILITY_VERSION` aligned

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
- **Suite size** — **62 skills** · **25** Role-Card core agents; packs core **21**, camera-image **11**, sequence-narrative **19**, nsfw **4**, delivery-post **7**
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
