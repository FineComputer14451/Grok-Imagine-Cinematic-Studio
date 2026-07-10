# AGENTS.md

**This file provides context and instructions for AI coding agents and assistants working in this workspace.**

**Version:** July 2026 (Updated for Grok Imagine Cinematic Studio **v3.7.1**, unified **Grok 4.5** cinematic+Build stack with optional **Grok 4.3** 1M, Imagine Agent Mode Handoff, guided Production Bible wizard, Grok Build ≥ **0.2.93**, plugin marketplace, AI Polish Director)  
**Canonical Source:** https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/blob/main/AGENTS.md

Think of this as the single source of truth for how to interact with this Grok/xAI agent environment. Paths below are **repo-relative** unless noted; sandboxes may root at `/home/workdir/` or a local clone (e.g. `~/Grok-Imagine-Cinematic-Studio`).

## Workspace Overview

This workspace is designed for advanced **Grok 4.5** agent workflows, with heavy emphasis on:

- Custom skill development and orchestration (Grok Build skills + plugin suite)
- High-quality cinematic image/video generation pipelines (Grok Imagine 1.0 / 1.5)
- Document, presentation, and media production
- GitHub repository management and open-source contribution
- Animal welfare legal research & advocacy tooling (supporting user's ongoing work)

**Core principle:** Use the appropriate skill or tool for every task. Do not reinvent wheels that skills already handle. Prefer existing skills over ad-hoc scripts.

**Orchestration default:** All multi-agent direction, Production Bibles, coding, and Grok Build sessions use **`grok-4.5`** unless the user or Studio Director explicitly opts into **`grok-4.3`** for 1M-context memory banks.

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
├── .grok-plugin/                # Plugin manifests (marketplace.json, plugin.json, plugin-index.json — 46 skills + commands)
├── artifacts/                   # All generated outputs (images, docs, videos, code)
├── scripts/                     # Install/verify/update helpers + thin shims
├── web_ui/                      # Streamlit dashboard (model pickers, quota sim, DNA/sequence tools)
├── tools/                       # CLI + model registry (models.py is canonical stack)
├── references/                  # MODELS_v3.6.md, agents/, handoff protocols
├── commands/                    # Slash commands for Grok Build plugin
├── AGENTS.md                    # This file (you are here)
├── README.md                    # Human-facing overview (keep in sync)
├── CHANGELOG.md
├── RELEASE_NOTES_v3.6.md
├── Quick_Start_Guide.md
└── (other: config/, examples/, VERSION, etc.)
```

User-global skills (all projects): `~/.grok/skills/`.  
User config: `~/.grok/config.toml`.

## Grok 4.5 Model Layer (Required Knowledge)

Canonical registry: `tools/models.py` · `references/MODELS_v3.6.md` · `references/agents/MODEL_LAYER_v3.7.1.md`.

Verify:

```bash
python tools/cinematic_studio_cli.py models list
python tools/cinematic_studio_cli.py models verify
```

| Layer | Default Slug | When to Use |
|-------|--------------|-------------|
| **Orchestration (default)** | `grok-4.5` | Production Bibles, multi-agent direction, agent loops (500k context) |
| **Long-context (opt-in)** | `grok-4.3` | 1M memory banks only — `--chat-model grok-4.3` or alias `long-context` |
| **Grok Build CLI** | `grok-4.5` | Default agent (coding / agentic); min CLI **0.2.93** |
| **Grok Build fork** | `grok-build` | Code, skills, repo tooling (`fork_secondary_model`) |
| **xAI Build / coding API** | `grok-4.5` | Agentic automation (legacy: `grok-build-0.1`) |
| **Creative fast (optional)** | `grok-composer-2.5-fast` | Fast multi-agent cinematic direction in Build picker |
| **Imagine Video** | `grok-imagine-video` (1.0 default) | $0.05/sec; use `grok-imagine-video-1.5` for native audio ($0.08/sec) |
| **Imagine Image** | `grok-imagine-image` | Reference stills ($0.02/image); quality tier `$0.05` for hero plates |

**Aliases:** `cinematic` / `build` / `coding` / `4.5` / `grok-4.5-latest` / `grok-build-latest` → **`grok-4.5`**.  
**1M aliases:** `long-context` / `4.3` / `grok-4` → **`grok-4.3`**.

### Grok 4.5 operating rules

1. **Default all orchestration** to `grok-4.5` unless the user or Studio Director explicitly needs 1M context.
2. **Reasoning:** prefer **high** for Bibles, QA, Identity Lock, Sequence Director; **medium** for routine prompt drafts; **low** only for trivial routing. Grok 4.5 defaults to high.
3. **Prompt cache:** use a stable `prompt_cache_key` per production (project slug) on multi-turn agent loops to reduce cost.
4. **Do not** treat Imagine models as chat models — video/image spend is `grok-imagine-*` only.
5. Every Production Bible must lock `model_stack` + `VIDEO_PIPELINE_SPEC` from the registry helpers.
6. Opt into `grok-4.3` only when memory banks / long chains exceed ~400k effective context.
7. Do **not** treat CLI version `0.2.93` as an API model slug — it is the **Grok Build binary** version.

Local config (`~/.grok/config.toml`) — see `config/grok-build.example.toml`:

```toml
[models]
default = "grok-4.5"

[ui]
fork_secondary_model = "grok-build"
```

CLI note (0.2.93+): **Esc no longer cancels a turn** — use **Ctrl+C**. Double-Esc rewind works while focused on scrollback.

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
6. Studio skills should embed the **Model Layer (Grok 4.5)** block (see `references/agents/MODEL_LAYER_v3.7.1.md`).
7. Validate after creation / change: `bash scripts/verify_cinematic_studio.sh` (and skill-specific validators when available).

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
- **Refine / iterate on previously generated images**: `generated-image-editor`
- **Upscale video for final delivery** (720p → 1080p/4K, face restoration): Activate `ai-video-upscaler`
- Video / audio processing: Activate `cinematic-ffmpeg` or use `ffmpeg` / bash
- **Full cinematic production**: Activate `grok-imagine-cinematic-studio` (23-agent + specialist suite, **v3.7.1**)
- **Planning → generation handoff**: Studio Director **Imagine Agent Mode Handoff** (see below)

If native Imagine tools are unavailable, use `imagine-execution-bridge` / CLI (`imagine submit`, `sfw run`, `sequence run`) with a locked `VIDEO_PIPELINE_SPEC`.

### Document Tasks

- PDF: `pdf` skill
- Word (.docx): `docx` skill
- PowerPoint (.pptx): `pptx` skill
- Excel (.xlsx): `xlsx` skill

### GitHub & Connected Services

- All GitHub operations: Activate `github-repo-manager` skill first (or GitHub MCP tools when connected)
- Discover connected / MCP services as available in the session; use schemas from tool discovery before calling

### Grok Plugins & Marketplace

- Install/update the full Cinematic Studio: `grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio --trust`
- Or via marketplace: `grok plugin marketplace add FineComputer14451/Grok-Imagine-Cinematic-Studio` then install by name
- Regenerate index after skill changes: `cinematic-studio plugin catalog pin` (or `python scripts/generate_plugin_index.py` for plain generation only)
- Validate plugin: `bash scripts/verify_plugins.sh` (or `cinematic-studio plugin catalog check`)
- Release catalog pin: commit content first → `cinematic-studio plugin catalog pin` (or `bash scripts/release_plugin_catalog.sh`) → commit **only** `.grok-plugin/` (install SHA = content revision; pin-only tip is expected)
- Pre-publish plugin gate: `cinematic-studio plugin catalog check --release` or `bash scripts/verify_plugins.sh --release` (passes when pin == HEAD or pin is ancestor with only catalog paths after it)
- Dev/test deps: `pip install -r requirements-dev.txt` then `pytest`
- Use `cinematic-studio-meta-installer` skill for full bootstrap/verify in agent sessions
- The **46 skills + slash commands** (in `commands/`) are the primary way to extend Grok Build with studio capabilities

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
`Activate Grok Imagine Cinematic Studio v3.7.1` or `Start cinematic production`

This engages the full **23 specialized agents** (v3.6.5 Role Cards under studio **v3.7.1**; Studio Director owns **Imagine Agent Mode Handoff**) including:

- Studio Director, Mega Production Architect
- Director of Photography, Production Designer, Color Grading Supervisor
- Performance & Emotion Director, Identity Lock Specialist, Narrative Arc Pacing Strategist
- Sequence Director, Cinematic Sequence Extender, Continuity Guardian
- Imagine Prompt Master, Quality Assurance Guardian, Workflow Quota Optimizer
- Sonic Architect, Foley Specialist
- Stunt Action Choreographer, VFX & SFX Supervisor
- Key Art Designer, Trailer Director, Localization Specialist
- **AI Polish Director** (final post-production upscale & restoration)
- ErosForge NSFW Director (when appropriate)

Specialist activation patterns: cinematic studio skill references and `references/agents/AGENT_INDEX.md`.  
Model Layer for Role Cards: `references/agents/MODEL_LAYER_v3.7.1.md`.

## Imagine Agent Mode Handoff (v3.7.1)

Studio Director routes planning → generation so pipeline context is never dropped.

| Surface | How generation runs |
|---------|---------------------|
| **A. Grok Build tools** | `image_gen` / `image_edit` / `image_to_video` / `reference_to_video` in session |
| **B. Grok agent mode (ACP)** | `grok agent` / IDE ACP — skills + shell + tools |
| **C. grok.com/imagine** | Manual paste (Execution Bridge packet) |
| **D. xAI Imagine API** | `imagine submit` / `sfw run` / `sequence run` with `XAI_API_KEY` |

**Activation:** `ACTIVATE IMAGINE_AGENT_MODE_HANDOFF` · `HANDOFF TO IMAGINE AGENT MODE` · `ROUTE TO IMAGINE EXECUTION`

Packet type: `imagine_agent_mode_handoff` (validated by `handoff-packet-validator`).  
Canonical doc: `references/agents/IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md`.  
CLI: `cinematic-studio imagine agent-handoff` (or `python tools/cinematic_studio_cli.py imagine agent-handoff`).

**Rules:** Prefer tools when available; block video without I2V motion block on locked plates; never silent NSFW handoff (route ErosForge first).

## AI Polish Director (Post-Production)

The **AI Polish Director** is the final post-production agent, activated after QA approval and color grading. It handles delivery-ready video enhancement using the `ai-video-upscaler` skill.

**When to activate:**

- Final delivery upscale (720p native 1.5 → 1080p or 4K)
- Face restoration on character close-ups
- Artifact cleanup before client delivery or festival submission

**Activation commands:**

- `ACTIVATE AI_POLISH_DIRECTOR`
- `RUN FINAL POLISH PASS`
- `UPSCALE FOR DELIVERY`

**Workflow:**

1. Confirm QA Guardian has issued Go/No-Go approval
2. Run `bash .grok/skills/ai-video-upscaler/scripts/install_models.sh` if models are not yet installed
3. Execute upscale via the skill scripts (GPU path preferred, pure-Python fallback available):
   ```bash
   python .grok/skills/ai-video-upscaler/scripts/ai_video_upscale.py \
     --input artifacts/source_clip.mp4 \
     --output artifacts/polished_clip.mp4 \
     --scale 2 --face-restore
   ```
4. For batch or long sequences, use the async variant:
   ```bash
   python .grok/skills/ai-video-upscaler/scripts/ai_video_upscale_async.py \
     --input artifacts/sequence/ --output artifacts/polished/ --scale 2
   ```
5. Hand polished output back to Studio Director for final sign-off

**Role Card:** `references/agents/AI_Polish_Director.md`

## When to Load Specific Skills

| Category | Skill | When to Activate |
|----------|-------|------------------|
| **Skill Development** | `create-skill`, `cinematic-skill-creator` | Creating, updating, or validating skills (generic vs studio) |
| **Cinematic Production** | `grok-imagine-cinematic-studio` | Full multi-agent film-style workflows, production bibles, long sequences |
| **Imagine Handoff** | `imagine-execution-bridge`, Studio Director handoff | grok.com/imagine packets or Agent Mode routing |
| **Video Upscale & Polish** | `ai-video-upscaler` | Final delivery upscale, face restoration, artifact cleanup |
| **Image Recreation & Editing** | `ai-image-recreation`, `generated-image-editor` | Style transfer, enhancement, variation, iterative refinement |
| **Character Consistency** | `character-dna-extractor` | Forensic DNA extraction, Identity Lock handoff, prompt injection |
| **Sequence Extension** | `cinematic-sequence-extender`, `extend-frame-to-video` | Extending stills into video, rough-cut animatics, continuing clips |
| **Custom Agents** | `custom-grok-cinematic-agent`, `skill-agent-architect` | Drafting Role Cards / bespoke agents |
| **Quota & Efficiency** | `workflow-quota-optimizer` | Long-form sessions, cost/quota management, production planning |
| **NSFW Batch Orchestration** | `nsfw-quota-orchestrator` | Quota-aware erotic image+video batches (with ErosForge) |
| **NSFW Sequence Extension** | `nsfw-sequence-extender` | Sensual 30–120s+ extension, erotic pacing, artifact QA |
| **GitHub Management** | `github-repo-manager` | Create repo, push, PRs, issues, file operations on GitHub |
| **Video / Audio** | `cinematic-ffmpeg`, `ffmpeg` | Trimming, merging, subtitles, compression, GIFs, storyboards |
| **Documents** | `pdf`, `docx`, `pptx`, `xlsx` | Professional document or presentation creation |
| **Memory** | `memory-edit` | Personal facts/preferences worth remembering |
| **Grok Plugin & Meta** | `cinematic-studio-meta-installer` | Bootstrap/install/update the full **46-skill** plugin suite |
| **AI Polish & Delivery** | `ai-polish-director`, `assembly-editor`, `cinematic-ffmpeg` | Post-QA upscale, EDL assembly, social crops |
| **Pre-viz & Assets** | `animatic-director`, `reference-asset-curator`, `image-to-video-specialist` | Previs, hero routing, i2v before 1.5 spend |
| **Batch Orchestration** | `sfw-batch-orchestrator` | Quota-aware SFW hero-first shot batches |
| **Chain QA & Handoffs** | `chain-qa-protocol`, `handoff-packet-validator` | 10-point extend/stitch QA gates; JSON handoff validation |
| **Production Bible** | `production-bible-workflow` | Guided create-bible / DNA / sequence / quota onboarding |

## Project-Specific Notes

- Primary project: **Grok Imagine Cinematic Studio** **v3.7.1** — unified **Grok 4.5** stack + Imagine Agent Mode Handoff + guided Bible wizard + related skills.
- All generated artifacts **must** be saved under `artifacts/` (repo root).
- Project skills live in `.grok/skills/`; user-global skills in `~/.grok/skills/`.
- Plugin marketplace lives in `.grok-plugin/` (46 skills + commands). Install via `grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio --trust`.
- Workspace supports SFW cinematic work and NSFW/erotic pipelines (**ErosForge only when explicitly activated**).
- **Model stack:** cinematic + Build/coding default **`grok-4.5`**; optional 1M **`grok-4.3`**; Imagine **1.0** default; `VIDEO_PIPELINE_SPEC` wired everywhere; **1.5** for native-audio workflows.
- Full suite: **46/46** skills + Role Cards on Grok 4.5 orchestration default.
- Recent **3.7.1:** Imagine Agent Mode Handoff (Studio Director + main skill + CLI). **3.6.7:** guided Bible wizard, catalog pin hygiene, cinematic chat default unified on `grok-4.5`.
- Keep this `AGENTS.md` in sync with the GitHub repository and other canonical docs (README, CHANGELOG, RELEASE_NOTES, MODELS, Quick Start).

## Quick Start for New Tasks

1. Clarify the goal with the user if ambiguous.
2. Confirm model stack: default **`grok-4.5`**; only use **`grok-4.3`** when 1M context is required.
3. Check if an existing skill covers it (`ls .grok/skills/` or `ls ~/.grok/skills/`, or read relevant SKILL.md). For plugin users: `.grok-plugin/plugin-index.json` or `grok plugin details grok-imagine-cinematic-studio`.
4. If no skill exists and the task is repeatable/specialized → create one with `create-skill` / `cinematic-skill-creator` (or extend via cinematic-studio-meta-installer).
5. Execute with the correct tools / skill activation. Prefer native Grok plugin commands (`grok plugin ...`) and studio CLI (`cinematic-studio` / `python tools/cinematic_studio_cli.py ...`).
6. For generation: prefer in-session Imagine tools; otherwise handoff packet (Agent Mode Handoff / Execution Bridge) or API CLI.
7. Save all outputs to `artifacts/`.
8. In the **final response**, use appropriate render components (when available) and provide clear, actionable output.

**Pro tip:** After any skill or plugin change, re-validate with `bash scripts/verify_cinematic_studio.sh` (it runs `models verify` too).

---

**This AGENTS.md is the canonical reference for all AI agents operating in this environment.**  
Update it whenever workflows, skills, or best practices evolve (e.g. new skills, plugin changes, model updates, or doc releases).

*Maintained for SuperGrokPro cinematic & development workflows — July 2026 (v3.7.1 · Grok 4.5)*
