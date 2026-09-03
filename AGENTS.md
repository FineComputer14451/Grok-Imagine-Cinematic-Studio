# AGENTS.md

**This file provides context and instructions for AI coding agents and assistants working in this workspace.**

**Version:** September 2026 (Updated for Grok Imagine Cinematic Studio **v3.11.3**, official Image 2.0 `images[]` edits + served-`model` logs, Imagine Image Quality retirement → Image **2.0** `quality=low`, SpaceXAI AUP fail-closed gates, official Imagine Image **2.0** + Video **1.0 / 1.5** surface map, multi-surface control plane **`studio_core` + TUI / Streamlit / NiceGUI / FastAPI / React**, unified **Grok 4.6** registry defaults + **v9-4p5 / grok-4-auto** specialist Model Layer, optional **Grok 4.3** 1M, Imagine Agent Mode Handoff, Identity Continuity Protocol, Parallel Brief Protocol, interactive CLI TUI, guided Production Bible wizard, Grok Build ≥ **1.0.5**, **plugin marketplace multi-plugin packs**, AI Polish Director)  
**Canonical Source:** https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/blob/main/AGENTS.md

> [!NOTE]
> **Grok Imagine Cinematic Studio** is an **independent community project**. It is **not affiliated with, endorsed by, sponsored by, or officially connected to xAI**. Agents must not claim official xAI partnership. Full notice: `DISCLAIMER.md`.

Think of this as the single source of truth for how to interact with this Grok/xAI agent environment. Paths below are **repo-relative** unless noted; sandboxes may root at `/home/workdir/` or a local clone (e.g. `~/Grok-Imagine-Cinematic-Studio`).

**Version legend (read once):**

| Stamp | Meaning |
|-------|---------|
| **Studio v3.11.3** | Current product / packaging version — use this for activation and docs |
| **Model Layer v4.5** | Canonical chat + Imagine routing (`MODEL_LAYER_v4.5.md`) |
| **Feature history (3.7.1 / 3.8.x)** | When a capability landed (e.g. Handoff in 3.7.1); not the operating studio pin |
| **Role Card labels (v3.6.5–v4.5)** | Per-card revision tags; AGENT_INDEX is authoritative |

## Workspace Overview

This workspace is designed for advanced **Grok 4.5** agent workflows, with heavy emphasis on:

- Custom skill development and orchestration (Grok Build skills + plugin suite)
- High-quality cinematic image/video generation pipelines (Grok Imagine 1.0 / 1.5)
- Document, presentation, and media production
- GitHub repository management and open-source contribution

**Core principle:** Use the appropriate skill or tool for every task. Do not reinvent wheels that skills already handle. Prefer existing skills over ad-hoc scripts. Prefer **skill directory slugs** (e.g. `studio-director`) over display titles when activating.

**Orchestration default (registry):** Multi-agent direction, Production Bibles, coding, and Grok Build sessions lock **`grok-4.6`** via `tools/models.py` unless the user or Studio Director opts into **`grok-4.3`** for 1M-context memory banks. `grok-4.5` aliases wrap 4.6.

**Specialist Model Layer (Role Cards / skills):** When v9-4p5 identifiers are available in the session, prefer them per `MODEL_LAYER_v4.5.md` — multi-agent → `grok-v9-4p5-multi`; specialist craft → `grok-v9-4p5-chat-expert`; draft/quota → `grok-4-auto`. Registry default remains **`grok-4.6`** for stack locks and Build CLI.

## Directory Structure

```
<repo-root>/
├── .grok/
│   └── skills/                  # Project skills (one per subdirectory)
│       ├── <skill-name>/
│       │   ├── SKILL.md         # Required: YAML frontmatter + imperative instructions
│       │   ├── scripts/         # Optional: executable helpers
│       │   ├── references/      # Optional: long-form docs, production bibles, agent defs
│       │   └── assets/          # Optional: templates, reference images, etc.
├── .grok-plugin/                # Marketplace multi-plugin (full suite + 5 packs), plugin.json, plugin-index.json, packs/
├── artifacts/                   # Generated outputs (gitignored contents; keep .gitkeep)
├── scripts/                     # Install/verify/update helpers + thin shims
├── studio_core/                 # UI-agnostic services (dashboard · ActionSpec · execute_action)
├── web_ui/                      # Streamlit dashboard (Bible wizard, DNA, quota, Tools)
├── web_nicegui/                 # NiceGUI shell (cinematic-studio web)
├── web_react/                   # React/TanStack SPA (cinematic-studio web-react + API)
├── studio_api/                  # FastAPI control plane (cinematic-studio api)
├── tools/                       # CLI + model registry (models.py is canonical stack)
├── references/                  # MODELS.md · MODELS_v3.6.md · agents/ Role Cards
├── docs/                        # Human docs: guides/, templates/, releases/, archive/
├── commands/                    # Slash commands for Grok Build plugin
├── characters/ · sequences/     # Runtime DNA / sequence state (gitignored contents)
├── sfw_batches/ · nsfw_batches/ # Runtime batch plans (gitignored contents)
├── AGENTS.md                    # This file (you are here)
├── README.md · MASTER_PROMPT.md # Overview + chat activation (Grok 4.5)
├── CHANGELOG.md · VERSION
└── (other: config/, examples/, tests/, assets/)
```

Full map: `docs/REPOSITORY_LAYOUT.md`. Dual-run web shells: `docs/guides/WEB_SHELLS.md`.

User-global skills (all projects): `~/.grok/skills/`.  
User config: `~/.grok/config.toml`.

## Multi-Surface Control Plane (v3.11.0)

All operator surfaces share **`studio_core`** so dashboard snapshots, ActionSpec allowlists, and `execute_action` stay consistent. Prefer extending `studio_core.services` over duplicating logic in a single UI.

| Surface | Path / entry | When to use |
|---------|--------------|-------------|
| **Shared core** | `studio_core/services/` — `dashboard.py`, `actions.py`, `execute.py` | Any control-plane feature (new ActionSpec, dashboard fields, execute modes) |
| **CLI** | `cinematic-studio` / `python tools/cinematic_studio_cli.py` | Scripts, CI, agents, headless production (Bible, DNA, sequence, handoff, doctor) |
| **TUI** | `cinematic-studio ui` (Textual; optional `ui --print` non-TTY) | SSH / no-browser; live dashboard + launcher/cockpit; `execute` via **subprocess** |
| **Streamlit** | `streamlit run web_ui/app.py` (`requirements.txt`) | Community Cloud, live Imagine batch when `XAI_API_KEY` is set, PDF tools, full NSFW planners |
| **NiceGUI** | `cinematic-studio web --port 8088` (`requirements-nicegui.txt`) | Browser cockpit parity with ActionSpec forms; low-latency **in-process** execute |
| **React** | `cinematic-studio web-react` (`web_react/` · Node 20+) | TanStack SPA on FastAPI; guided Bible + Tools/Settings; same ActionSpec safety |
| **FastAPI** | `cinematic-studio api --port 8090` (`requirements-api.txt`) | Automation / React / custom UIs; OpenAPI at `/docs`; dashboard + ActionSpec + meta + bible |

**Rules for agents:**

1. Do **not** invent parallel dashboard/action registries per surface — wire through `studio_core`.
2. TUI, NiceGUI, and React (via API) enforce the ActionSpec allowlist + forbidden argv tokens; keep that invariant.
3. Surfaces are complementary: Streamlit + NiceGUI + React may run together on different ports; none replace the CLI.
4. Smoke without long-running servers: `python scripts/smoke_studio_surfaces.py` · React: `cd web_react && npm run test:smoke`.
5. Full multi-shell matrix: `docs/guides/WEB_SHELLS.md`.

```bash
# Orient (TUI)
cinematic-studio ui
cinematic-studio ui --print          # non-TTY fallback

# Browser shells
streamlit run web_ui/app.py
pip install -r requirements-nicegui.txt && cinematic-studio web --host 127.0.0.1 --port 8088
pip install -r requirements-api.txt     && cinematic-studio api --host 127.0.0.1 --port 8090
# React SPA (needs API above + Node)
cinematic-studio web-react             # → http://127.0.0.1:5173
```

## Grok 4.6 Model Layer (Required Knowledge)

Canonical registry: `tools/models.py` · `references/MODELS_v3.6.md` · **`references/agents/MODEL_LAYER_v4.5.md`** (v4.5.1).  
Legacy archive only: `references/agents/MODEL_LAYER_v3.7.1.md` (do not use for new work).  
Agent slug / Role Card map: `references/agents/AGENT_INDEX.md`.

Verify:

```bash
python tools/cinematic_studio_cli.py models list
python tools/cinematic_studio_cli.py models verify
```

### Registry defaults (stack lock / Build / Bible)

| Layer | Default Slug | When to Use |
|-------|--------------|-------------|
| **Orchestration (registry default)** | `grok-4.6` | Production Bible `model_stack`, multi-agent direction lock, agent loops |
| **Long-context (opt-in)** | `grok-4.3` | 1M memory banks only — `--chat-model grok-4.3` or alias `long-context` |
| **Grok Build CLI** | `grok-4.6` | Default agent (coding / agentic); min CLI **1.0.5** |
| **Grok Build fork** | `grok-build` | Code, skills, repo tooling (`fork_secondary_model`) |
| **xAI Build / coding API** | `grok-4.6` | Agentic automation (legacy: `grok-build-0.1`) |
| **Creative fast (optional)** | `grok-composer-2.5-fast` | Fast multi-agent cinematic direction in Build picker |
| **Imagine Video** | `grok-imagine-video` (1.0 default, edit/extend) | $0.05/sec 480p; `grok-imagine-video-1.5` for native audio / r2v / 1080p. **No video 2.0** |
| **Imagine Image** | `grok-imagine-image` (draft) · **`grok-imagine-image-2.0` (hero / Quality Mode)** | $0.02 draft; from $0.04 Image 2.0 (`quality` low \| medium \| auto); `grok-imagine-image-quality` retires 2026-11-02 → 2.0 `quality=low` |

**Aliases:** `cinematic` / `build` / `coding` / `4.5` / `grok-4.5` / `grok-4.5-latest` / `grok-build-latest` / `4.6` → **`grok-4.6`**.  
**1M aliases:** `long-context` / `4.3` / `grok-4` → **`grok-4.3`**.

### Specialist Model Layer (v4.5 dual-model wave)

When the session exposes these identifiers, **prefer them for Role Card work** (skills already embed this table). Registry default for Bibles/Build remains **`grok-4.6`**.

| Task type | Preferred model | Reasoning |
|-----------|-----------------|-----------|
| Multi-agent orchestration, handoffs, sequence chains | `grok-v9-4p5-multi` | high |
| Specialist craft (DNA, prompts, QA, DoP, Sonic, ErosForge) | `grok-v9-4p5-chat-expert` | high |
| Draft / animatic / quota-sensitive / routine routing | `grok-4-auto` | medium |

**Aliases (specialist):** `v9-4p5-multi` / `4p5-multi` · `v9-4p5-chat-expert` / `chat-expert` · `4-auto` / `auto`.

### Grok 4.6 operating rules

1. **Lock the stack** to `grok-4.6` (registry) unless the user or Studio Director needs 1M context (`grok-4.3`).
2. **Route specialists** with Model Layer v4.5 when v9-4p5 / `grok-4-auto` are available; fall back to `grok-4.6` when they are not.
3. **Reasoning:** prefer **high** for Bibles, QA, Identity Lock, Sequence Director; **medium** for routine prompt drafts; **low** only for trivial routing. Grok 4.6 defaults to high.
4. **Prompt cache:** use a stable `prompt_cache_key` per production (project slug) on multi-turn agent loops to reduce cost.
5. **Do not** treat Imagine models as chat models — video/image spend is `grok-imagine-*` only.
6. Every Production Bible must lock `model_stack` + `VIDEO_PIPELINE_SPEC` from the registry helpers (`build_video_pipeline_spec` in `tools/models.py`).
7. Opt into `grok-4.3` only when memory banks / long chains exceed ~400k effective context.
8. Do **not** treat CLI version `1.0.5` as an API model slug — it is the **Grok Build binary** version.
9. **Identity Continuity:** apply `references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md` on multi-clip character work (drift gates before extend/stitch spend).
10. **Plate & motion readiness:** before video spend, prefer locked plates + motion briefs (`plate_status`, `motion_vector`; CLI gates `--strict-plate`, `--strict-motion`, `--strict-handoff` when enforcing).

Local config (`~/.grok/config.toml`) — see `config/grok-build.example.toml`:

```toml
[models]
default = "grok-4.6"

[ui]
fork_secondary_model = "grok-build"
```

CLI note (1.0.5+): **Esc no longer cancels a turn** — use **Ctrl+C**. Double-Esc rewind works while focused on scrollback.

## Skill System Rules (Critical)

When working with or creating skills:

1. **Prefer studio skill creators** in this repo:
   - Project cinematic skills → `cinematic-skill-creator` (Role Card + validate conventions)
   - Generic Grok skills → `create-skill` (`~/.grok/skills/create-skill/SKILL.md` or `/create-skill`)
2. Every skill **must** have a `SKILL.md` with strict YAML frontmatter:
   - `name`: kebab-case, matches directory name exactly
   - `description`: single-line plain text (no colons, no `<`/`>`, max 1024 chars) describing **when to use** this skill
3. **Never** create `README.md`, `CHANGELOG.md`, or human-facing docs inside skill directories — skills are agent-only.
4. Keep `SKILL.md` concise (< ~500 lines). Move detailed content, agent personalities, production bibles, and long references to `references/`.
5. New **project** skills go in `.grok/skills/<name>/`. User-global skills go in `~/.grok/skills/<name>/`.
6. Studio skills should embed the **Model Layer (Grok 4.6 / v9-4p5)** block (see `references/agents/MODEL_LAYER_v4.5.md`).
7. Validate after creation / change: `bash scripts/verify_cinematic_studio.sh` (and skill-specific validators when available).

## Core Agent Skill Slugs

**25 Role-Card core agents** power the department; **64 skills** power agents + specialists (i2i, batch, chain QA, polish, Wave A P0, packs, etc.). Full activation table: `references/agents/AGENT_INDEX.md`.

| Display name | Skill slug (activate this) |
|--------------|----------------------------|
| Studio Director | `studio-director` |
| Mega Production Architect | `mega-production-architect` |
| Director of Photography | `director-of-photography` |
| Production Designer | `production-designer-set-decorator` |
| Color Grading Supervisor | `post-production-color-grading-supervisor` |
| Character DNA Extractor | `character-dna-extractor` |
| Performance & Emotion Director | `performance-emotion-director` |
| Identity Lock Specialist | `identity-lock-specialist` |
| Narrative Arc Pacing Strategist | `narrative-arc-pacing-strategist` |
| Sequence Director | `sequence-director` |
| Cinematic Sequence Extender | `cinematic-sequence-extender` |
| Continuity Guardian | `continuity-consistency-guardian` |
| Multi-Clip Continuity Orchestrator | `multi-clip-continuity-orchestrator` |
| Imagine Prompt Master | `imagine-prompt-master` |
| Quality Assurance Guardian | `quality-assurance-guardian` |
| Grok Doctor | `grok-doctor` |
| Workflow Quota Optimizer | `workflow-quota-optimizer` |
| Sonic Architect | `sonic-architect-native-audio-virtuoso` |
| Foley Specialist | `foley-sound-design-specialist` |
| Stunt Action Choreographer | `stunt-action-choreographer` |
| VFX & SFX Supervisor | `vfx-sfx-supervisor` |
| Key Art Designer | `key-art-poster-designer` |
| Trailer Director | `trailer-teaser-director` |
| Localization Specialist | `localization-subtitle-specialist` |
| AI Polish Director | `ai-polish-director` |

Core membership matches `tools/cli/shared.py` `CORE_AGENT_CATEGORIES` (includes Character DNA Extractor). **ErosForge NSFW Director** is opt-in, not in the 25.

**High-traffic specialists (not all are in the “25” core list):** `erosforge-nsfw-director` (explicit opt-in), `costume-wardrobe-continuity`, `multi-character-identity-arbiter`, `image-to-video-specialist`, `reference-asset-curator`, `animatic-director`, `assembly-editor`, `sfw-batch-orchestrator`, `nsfw-quota-orchestrator`, `nsfw-sequence-extender`, `chain-qa-protocol`, `nsfw-chain-qa-protocol`, `handoff-packet-validator`, `imagine-execution-bridge`, `ai-video-upscaler`, `cinematic-ffmpeg`, `i2i-refiner`, `i2i-cinematic-refiner`, `ai-image-recreation`, `arc-replan-copilot`, `quota-dashboard`, `production-bible-workflow`, `skill-agent-architect`, `cinematic-skill-creator`, `cinematic-studio-meta-installer`, `github-repo-manager`, `extend-frame-to-video`, `grok-imagine-cinematic-studio`.

**Wave A (P0 scaffold · 8 agents):** `plate-motion-readiness-lead`, `contact-micro-physics-specialist`, `hair-makeup-continuity`, `dialogue-adr-director`, `score-temp-music-supervisor`, `title-motion-graphics-lead`, `distribution-crop-strategist`, `parallel-brief-dispatcher` — Role Card + skill only; suite **64** skills after register.

## Common Workflows & Commands

### File Operations (Grok Build tools)

- Read: `read_file` (supports `offset` + `limit`)
- Write / create: `write`
- Edit in place: `search_replace`
- Explore: shell `ls`, `find`, `rg` / `grep` tool; prefer dedicated file tools over `cat` for large reads

### Image & Media Tasks (Grok Imagine)

- **Generate new images**: `image_gen` (detailed prompt + aspect ratio)
- **Edit existing / generated images**: `image_edit` (prompt + reference image path or attachment)
- **Still → video**: `image_to_video` (when available in session)
- **Multi-ref → video**: `reference_to_video` (when available)
- **AI recreation / style transfer / enhancement** of uploaded images: Activate `ai-image-recreation`
- **Extract Character DNA** for consistency: Activate `character-dna-extractor`
- **Extend cinematic sequences** (60–120s+): Activate `cinematic-sequence-extender` or `extend-frame-to-video`
- **Refine / iterate on previously generated images**: `generated-image-editor` (user-global when present)
- **Upscale video for final delivery** (720p → 1080p/4K, face restoration): Activate `ai-video-upscaler`
- Video / audio processing: Activate `cinematic-ffmpeg` or use `ffmpeg` / bash
- **Full cinematic production**: Activate `grok-imagine-cinematic-studio` (25-agent core + specialist suite, **studio v3.11.3**)
- **Planning → generation handoff**: Studio Director **Imagine Agent Mode Handoff** (see below)

If native Imagine tools are unavailable, use `imagine-execution-bridge` / CLI (`imagine submit`, `sfw run`, `sequence run`) with a locked `VIDEO_PIPELINE_SPEC`.

### Document Tasks

Document skills are typically **session / user-global** (not always in the 64-skill project suite). Use when available:

- PDF: `pdf` skill
- Word (.docx): `docx` skill
- PowerPoint (.pptx): `pptx` skill
- Excel (.xlsx): `xlsx` skill

### GitHub & Connected Services

- All GitHub operations: Activate `github-repo-manager` skill first (or GitHub MCP tools when connected)
- Discover connected / MCP services as available in the session; use schemas from tool discovery before calling

### Grok Build CLI binary + grok.com surfaces

- Manage the official Grok Build binary (min **1.0.5**): `cinematic-studio grok status|ensure|update|install`
- Method A meta installer ensures the binary and ships `tools/grok_build_cli.py` + `cli/grok_cli_commands.py`
- **Android / Termux / NetHunter / desktop shell:** `export PATH="$HOME/.grok/bin:$HOME/.local/bin:$PATH"`; Method A from a clone
- **grok.com chat:** no binary — `Activate Grok Imagine Cinematic Studio v3.11.3` or paste `MASTER_PROMPT.md`; Method A skills in `~/.grok/skills/` support chat ecosystems (skip declutter if you need both chat Method A + plugin)
- **grok.com/imagine:** surface `grok_com_imagine` — `imagine-execution-bridge` / `cinematic-studio imagine bridge` copy-paste packets
- **Grok mobile chat app:** same as grok.com (Activate / Imagine only); shell for CLI
- Meta path without wrapper: `bash scripts/cinematic_studio.sh grok ensure`

### Grok Plugins & Marketplace

- Install/update the full Cinematic Studio (recommended): `grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio --trust`
- Or via marketplace: `grok plugin marketplace add FineComputer14451/Grok-Imagine-Cinematic-Studio` then install by name
- **Multi-plugin packs (v3.8.0):** marketplace lists **6 plugins** (full suite + 5 packs) from `config/plugin_packs.yaml`. Prefer full suite; list packs with `cinematic-studio plugin packs`. See `references/SKILLS_TAXONOMY.md` and install matrix in `docs/guides/installation_guide.md`.
- Regenerate index after skill changes: `cinematic-studio plugin catalog pin` (or `python scripts/generate_plugin_index.py` for plain generation only)
- Validate plugin: `bash scripts/verify_plugins.sh` (or `cinematic-studio plugin catalog check`)
- Declutter dual Method A+B skill installs: `bash scripts/cinematic_studio.sh declutter --apply` (or `cinematic-studio plugin declutter --apply`) — see `references/SKILLS_TAXONOMY.md`
- Declutter **full suite + satellite packs:** policy **`full_suite_wins`** keeps the full suite and removes satellite skill dupes
- Browse skill groups: `cinematic-studio plugin list --grouped`
- Release catalog pin: commit content first → `cinematic-studio plugin catalog pin` (or `bash scripts/release_plugin_catalog.sh`) → commit **only** `.grok-plugin/` (install SHA = content revision; pin-only tip is expected)
- Pre-publish plugin gate: `cinematic-studio plugin catalog check --release` or `bash scripts/verify_plugins.sh --release` (passes when pin == HEAD or pin is ancestor with only catalog paths after it)
- Dev/test deps: `pip install -r requirements-dev.txt` then `pytest`
- Use `cinematic-studio-meta-installer` skill for full bootstrap/verify in agent sessions
- The **64 skills + slash commands** (in `commands/`) are the primary way to extend Grok Build with studio capabilities

### Memory & Personalization

- When the user shares personal facts, preferences, or life updates that may warrant remembering: Use the `memory-edit` skill (consult its SKILL.md).

### Render Components (Final Response Only)

Use these in the **final response** (never inside function calls), when the runtime supports them:

- Image render helpers for generated/edited/searched assets
- `render_inline_citation` (for web / X / collection results)
- File/download render helpers for local artifacts

## Cinematic Studio & Multi-Agent Workflows

For any complex visual storytelling, film-style image sequences, video production, or NSFW cinematic work:

**Primary activation command:**  
`Activate Grok Imagine Cinematic Studio v3.11.3` or `Start cinematic production`

This engages the full **25 specialized agents** (Role Cards labeled v3.6.5–v4.5 under studio **v3.11.3**; Studio Director owns **Imagine Agent Mode Handoff**) plus pipeline specialists and **Wave A** scaffolds. **64 skills** implement the department. Core list (`CORE_AGENT_CATEGORIES` — DNA in, ErosForge opt-in):

- Studio Director (`studio-director`), Mega Production Architect (`mega-production-architect`)
- Director of Photography, Production Designer, Color Grading Supervisor
- Character DNA Extractor (`character-dna-extractor`), Performance & Emotion Director, Identity Lock Specialist, Narrative Arc Pacing Strategist
- Sequence Director, Cinematic Sequence Extender, Continuity Guardian, Multi-Clip Continuity Orchestrator
- Imagine Prompt Master, Quality Assurance Guardian, **Grok Doctor** (`grok-doctor`), Workflow Quota Optimizer
- Sonic Architect, Foley Specialist
- Stunt Action Choreographer, VFX & SFX Supervisor
- Key Art Designer, Trailer Director, Localization Specialist
- **AI Polish Director** (`ai-polish-director`) — final post-production upscale & restoration

Opt-in NSFW (not in the 25): ErosForge NSFW Director (`erosforge-nsfw-director`) — only when explicitly activated.

Specialist activation patterns: cinematic studio skill references and **`references/agents/AGENT_INDEX.md`**.  
Model Layer for Role Cards: **`references/agents/MODEL_LAYER_v4.5.md`**.  
Identity Continuity: **`references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md`**.  
**Parallel Brief Protocol:** Concurrent multi-agent coordination under MAXIMUM AGENTIC MODE. Canonical: `references/agents/Parallel_Brief_Protocol.md`. Studio Director issues Parallel Briefs; specialist outputs converge into validated `imagine_agent_mode_handoff` packets.

## Imagine Agent Mode Handoff (landed v3.7.1 · current studio v3.11.3)

Studio Director routes planning → generation so pipeline context is never dropped.

| Surface | How generation runs |
|---------|---------------------|
| **A. Grok Build tools** | `image_gen` / `image_edit` / `image_to_video` / `reference_to_video` in session |
| **B. Grok agent mode (ACP)** | `grok agent` / IDE ACP — skills + shell + tools |
| **C. grok.com/imagine** | Manual paste (Execution Bridge packet); Quality Mode = Image 2.0 |
| **D. xAI Imagine API** | `imagine submit` / `sfw run` / `sequence run` with `XAI_API_KEY` |
| **E. Responses `image_generation`** | Server-side tool (Image 2.0 stills); `target_surface: xai_responses_tool` |

**Activation:** `ACTIVATE IMAGINE_AGENT_MODE_HANDOFF` · `HANDOFF TO IMAGINE AGENT MODE` · `ROUTE TO IMAGINE EXECUTION`

Packet type: `imagine_agent_mode_handoff` (validated by `handoff-packet-validator`).  
Canonical doc: `references/agents/IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md`.  
CLI: `cinematic-studio imagine agent-handoff` (or `python tools/cinematic_studio_cli.py imagine agent-handoff`).

**Rules:** Prefer tools when available; block video without I2V motion block on locked plates; never silent NSFW handoff (route ErosForge first). Enforce plate/motion/handoff readiness when CLI strict flags or Production Bible require it.

## AI Polish Director (Post-Production · Grok 4.6)

The **AI Polish Director** is the final post-production agent, activated after QA approval and color grading. It handles delivery-ready video enhancement using the `ai-video-upscaler` skill and `sequence polish` CLI. Orchestration on **`grok-4.6`** (or specialist chat-expert when available); upscale is local (not Imagine API).

**When to activate:**

- Final delivery upscale (720p native → 1080p or 4K-class)
- Face restoration on character close-ups
- Artifact cleanup before client delivery or festival submission

**Activation commands:**

- `ACTIVATE AI_POLISH_DIRECTOR`
- `RUN FINAL POLISH PASS`
- `UPSCALE FOR DELIVERY` · `POLISH HERO SHOTS ONLY` · `FACE RESTORE PASS`

**Workflow:**

1. Confirm QA Guardian has issued Go (and color grade or Director waiver)
2. Prefer sequence CLI when a sequence exists:
   ```bash
   python tools/cinematic_studio_cli.py sequence polish "Act 1" --scale 2 --face-restore
   python tools/cinematic_studio_cli.py sequence polish "Act 1" --dry-run
   ```
3. Or install models once and run upscaler scripts:
   ```bash
   bash .grok/skills/ai-video-upscaler/scripts/install_models.sh
   python .grok/skills/ai-video-upscaler/scripts/ai_video_upscale.py \
     --input artifacts/source_clip.mp4 \
     --output artifacts/polished/clip.mp4 \
     --scale 2 --face-restore
   ```
4. Batch/async: `ai_video_upscale_async.py` on a directory; pure-Python fallback: `ai_video_upscale_pure.py`
5. Log `[POLISH_SPEC: …]` in the Project Bible; hand polished masters to Studio Director for sign-off (then `sequence deliver` / `cinematic-ffmpeg`)

**Role Card:** `references/agents/AI_Polish_Director.md` · **Skill:** `.grok/skills/ai-polish-director/SKILL.md` · **Presets:** `references/polish_presets.md`

## When to Load Specific Skills

Entry points by task (not exhaustive). Prefer slugs; full map = `AGENT_INDEX.md` + `ls .grok/skills/`.

| Category | Skill | When to Activate |
|----------|-------|------------------|
| **Skill Development** | `create-skill`, `cinematic-skill-creator` | Creating, updating, or validating skills (generic vs studio) |
| **Full Studio / Director** | `grok-imagine-cinematic-studio`, `studio-director`, `mega-production-architect` | Full multi-agent workflows, Bibles, campaign orchestration |
| **Imagine Handoff** | `imagine-execution-bridge`, `handoff-packet-validator`, Studio Director handoff | grok.com/imagine packets, Agent Mode routing, packet validation |
| **Video Upscale & Polish** | `ai-polish-director`, `ai-video-upscaler` | Final delivery upscale, face restoration, artifact cleanup |
| **Image Recreation & Editing** | `ai-image-recreation`, `generated-image-editor`, `i2i-refiner`, `i2i-cinematic-refiner` | Style transfer, enhancement, variation, iterative refinement |
| **Character Consistency** | `character-dna-extractor`, `identity-lock-specialist`, `costume-wardrobe-continuity`, `multi-character-identity-arbiter` | DNA extraction, Identity Lock,wardrobe lock, multi-cast arbitration |
| **Sequence & Story** | `sequence-director`, `cinematic-sequence-extender`, `extend-frame-to-video`, `narrative-arc-pacing-strategist`, `arc-replan-copilot` | Long-form sequencing, extend/stitch, pacing, mid-chain replan |
| **Camera / Set / Performance** | `director-of-photography` (prefer over legacy `director-of-photography-v3-3`), `production-designer-set-decorator`, `performance-emotion-director` | Lighting, environments, acting beats |
| **Continuity & QA** | `continuity-consistency-guardian`, `multi-clip-continuity-orchestrator`, `costume-wardrobe-continuity`, `quality-assurance-guardian`, `chain-qa-protocol`, `nsfw-chain-qa-protocol` | Continuity, multi-clip audits, wardrobe seams, 16-point QA, extend/stitch gates |
| **Studio Health** | `grok-doctor` | Multi-agent roster / handoff / continuity / pipeline diagnostics (`ACTIVATE GROK_DOCTOR`) |
| **Prompts & Assets** | `imagine-prompt-master`, `reference-asset-curator`, `image-to-video-specialist`, `key-art-poster-designer` | Prompt craft, tiers, i2v motion, key art |
| **Audio** | `sonic-architect-native-audio-virtuoso`, `foley-sound-design-specialist` | Native audio layers, foley |
| **Action / VFX / Trailer** | `stunt-action-choreographer`, `vfx-sfx-supervisor`, `trailer-teaser-director` | Stunts, VFX, teasers |
| **Post & Delivery** | `assembly-editor`, `post-production-color-grading-supervisor`, `ai-polish-director`, `cinematic-ffmpeg` | EDL, grade, polish, social crops |
| **Pre-viz & Batch** | `animatic-director`, `sfw-batch-orchestrator`, `nsfw-quota-orchestrator` | Previs before 1.5 spend; SFW/NSFW batch plans |
| **NSFW (explicit only)** | `erosforge-nsfw-director`, `nsfw-sequence-extender`, `nsfw-quota-orchestrator`, `nsfw-chain-qa-protocol` | R-rated/intimate work only when user activates ErosForge |
| **Quota & Dashboard** | `workflow-quota-optimizer`, `quota-dashboard` | Cost/quota planning and visual reports |
| **Custom Agents** | `custom-grok-cinematic-agent`, `skill-agent-architect` | Drafting Role Cards / bespoke agents |
| **GitHub Management** | `github-repo-manager` | Git lifecycle, PRs, releases, skill/plugin catalog pin hygiene |
| **Documents** | `pdf`, `docx`, `pptx`, `xlsx` | Professional docs (session skills when available) |
| **Memory** | `memory-edit` | Personal facts/preferences worth remembering |
| **Grok Plugin & Meta** | `cinematic-studio-meta-installer` | Bootstrap/install/update the full **64-skill** suite (v3.11.3; packs + declutter `full_suite_wins`) |
| **Localization** | `localization-subtitle-specialist` | SDH, multi-language, cultural adaptation |
| **Production Bible** | `production-bible-workflow` | Guided create-bible / DNA / sequence / quota onboarding |

## Project-Specific Notes

- Primary project: **Grok Imagine Cinematic Studio** **v3.11.3** — registry default **`grok-4.6`** + specialist **v9-4p5 / grok-4-auto** Model Layer + dual Imagine Video **1.0 / 1.5** + Imagine Agent Mode Handoff + Identity Continuity + Parallel Brief Protocol + multi-surface control plane (`studio_core` · TUI · Streamlit · NiceGUI · FastAPI · React) + guided Bible wizard + **plugin modularity packs**.
- All generated artifacts **must** be saved under `artifacts/` (repo root).
- Project skills live in `.grok/skills/`; user-global skills in `~/.grok/skills/`.
- Plugin marketplace lives in `.grok-plugin/` (full suite + 5 packs, **64 skills** + commands; Wave A P0 included). Install full suite via `grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio --trust`.
- Workspace supports SFW cinematic work and NSFW/erotic pipelines (**ErosForge only when explicitly activated**).
- **Model stack:** cinematic + Build/coding registry default **`grok-4.6`**; specialist routing **v9-4p5 / grok-4-auto** when available; optional 1M **`grok-4.3`**; Imagine **1.0** default; `VIDEO_PIPELINE_SPEC` via registry helpers; **1.5** for native-audio / high-physics / intimacy workflows.
- **Control plane:** shared `studio_core` powers `cinematic-studio ui` · `streamlit run web_ui/app.py` · `cinematic-studio web` · `cinematic-studio api` — see Multi-Surface section above and `docs/guides/WEB_SHELLS.md`.
- Full suite: **64/64** skills + Role Cards (includes `grok-doctor`, `multi-clip-continuity-orchestrator`, `ai-image-recreation`).
- **Recent history:** **3.11.3** — official Image 2.0 multi-edit `images[]` + preserve served `model`. **3.11.2** — Imagine Image Quality retirement (slug → 2.0 `quality=low`). **3.11.1** — SpaceXAI AUP fail-closed gates + CLI help IA. **3.11.0** — Grok 4.6 stack lock + Grok Build ≥ 1.0.5 (`grok-4.5` aliases wrap 4.6). **3.10.0** — official Imagine Image 2.0 + Video 1.0/1.5 surface map (no Video 2.0); Agent Mode surface E; REST edit/extend/r2v. **3.9.1** — React/TanStack cockpit + API meta/guided Bible. **3.9.0** — multi-surface control plane (`studio_core` · NiceGUI · FastAPI + Streamlit wiring). **3.8.9** — TUI + Streamlit compact/ops/full view modes. **3.8.8** — Operator UX control plane. **3.8.7** — Wave A · Grok Doctor · Multi-Clip Continuity. **3.8.0** — plugin packs. **3.7.1** — Imagine Agent Mode Handoff.
- Keep this `AGENTS.md` in sync with the GitHub repository and other canonical docs (README, CHANGELOG, `docs/releases/`, `docs/guides/WEB_SHELLS.md`, `references/MODELS.md`, `references/agents/MODEL_LAYER_v4.5.md`, `docs/guides/Quick_Start_Guide.md`).

## Quick Start for New Tasks

1. Clarify the goal with the user if ambiguous.
2. Confirm model stack: registry default **`grok-4.6`**; specialist v9-4p5 / `grok-4-auto` when available; only use **`grok-4.3`** when 1M context is required.
3. Check if an existing skill covers it (`ls .grok/skills/` or `ls ~/.grok/skills/`, skill-slug table above, or `references/agents/AGENT_INDEX.md`). For plugin users: `.grok-plugin/plugin-index.json` or `grok plugin details grok-imagine-cinematic-studio`.
4. If no skill exists and the task is repeatable/specialized → create one with `create-skill` / `cinematic-skill-creator` (or extend via cinematic-studio-meta-installer).
5. Execute with the correct tools / skill activation. Prefer native Grok plugin commands (`grok plugin ...`) and studio CLI (`cinematic-studio` / `python tools/cinematic_studio_cli.py ...`). Operator UX changes go through **`studio_core`**, then surface UIs (TUI / Streamlit / NiceGUI / FastAPI) — not one-off forks.
6. For generation: prefer in-session Imagine tools; otherwise handoff packet (Agent Mode Handoff / Execution Bridge) or API CLI. Enforce plate/motion readiness before video spend.
7. Save all outputs to `artifacts/`.
8. In the **final response**, use appropriate render components (when available) and provide clear, actionable output.

**Pro tip:** After any skill or plugin change, re-validate with `bash scripts/verify_cinematic_studio.sh` (it runs `models verify` too).

**Health check:** `grok-doctor` or `cinematic-studio doctor` (full) · `grok-doctor --quick` · `bash scripts/grok_doctor.sh`. Skill activation: `ACTIVATE GROK_DOCTOR` / `RUN STUDIO_HEALTH_CHECK` (Role Card: `references/agents/Grok_Doctor.md`).

---

**This AGENTS.md is the canonical reference for all AI agents operating in this environment.**  
Update it whenever workflows, skills, or best practices evolve (e.g. new skills, plugin changes, model updates, or doc releases).

*Maintained for SuperGrokPro cinematic & development workflows — September 2026 (v3.11.3 · Grok 4.6 / Grok Build ≥ 1.0.5 · Model Layer v4.5)*
