# AGENTS.md

**This file provides context and instructions for AI coding agents and assistants working in this workspace.**

**Version:** June 2026 (Updated for Grok Imagine Cinematic Studio v3.6 and AI Polish Director)  
**Canonical Source:** https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/blob/main/AGENTS.md

Think of this as the single source of truth for how to interact with this Grok/xAI agent environment in `/home/workdir/`.

## Workspace Overview

This is a persistent Linux sandbox environment (`/home/workdir/`) designed for advanced Grok agent workflows, with heavy emphasis on:

- Custom skill development and orchestration
- High-quality cinematic image/video generation pipelines (Grok Imagine)
- Document, presentation, and media production
- GitHub repository management and open-source contribution
- Animal welfare legal research & advocacy tooling (supporting user's ongoing work)

**Core principle:** Use the appropriate skill or tool for every task. Do not reinvent wheels that skills already handle. Prefer existing skills over ad-hoc scripts.

## Directory Structure

```
/home/workdir/
├── .grok/
│   └── skills/                  # All custom skills live here (one per subdirectory)
│       ├── <skill-name>/
│       │   ├── SKILL.md         # Required: YAML frontmatter + imperative instructions
│       │   ├── scripts/         # Optional: executable helpers
│       │   ├── references/      # Optional: long-form docs, production bibles, agent defs
│       │   └── assets/          # Optional: templates, reference images, etc.
├── artifacts/                   # All outputs go here (images, docs, videos, code, etc.)
├── AGENTS.md                    # This file (you are here)
└── (other project files as added)
```

## Skill System Rules (Critical)

When working with or creating skills:

1. **Always follow the official skill-creator guidelines** first — read `/root/.grok/skills/skill-creator/SKILL.md`.
2. Every skill **must** have a `SKILL.md` with strict YAML frontmatter:
   - `name`: kebab-case, matches directory name exactly
   - `description`: single-line plain text (no colons, no `<`/`>`, max 1024 chars) describing **when to use** this skill
3. **Never** create `README.md`, `CHANGELOG.md`, or human-facing docs inside skill directories — skills are agent-only.
4. Keep `SKILL.md` concise (< ~500 lines). Move detailed content, agent personalities, production bibles, and long references to `references/`.
5. New skills **must** be created in `/home/workdir/.grok/skills/<name>/` using the init script from skill-creator.
6. Validate after creation: `bash /root/.grok/skills/skill-creator/scripts/validate-skill.sh <skill-dir>`

## Common Workflows & Commands

### File Operations
- Read: `read_file` (supports `offset` + `limit`)
- Write/Edit: `write_file`, `edit_file`
- Explore: `bash ls -la`, `bash find`, `bash tree`

### Image & Media Tasks (Grok Imagine)
- **Generate new images**: `generate_image` (detailed prompt + orientation)
- **Edit existing / generated images**: `edit_image` (prompt + `file_path` or `image_id`)
- **AI-powered recreation / style transfer / enhancement** of uploaded images: Activate `ai-image-recreation`
- **Extract Character DNA** for consistency: Activate `character-dna-extractor`
- **Extend cinematic sequences** (60–120s+): Activate `cinematic-sequence-extender` or `extend-frame-to-video`
- **Refine / iterate on previously generated images**: `generated-image-editor`
- **Upscale video for final delivery** (720p → 1080p/4K, face restoration): Activate `ai-video-upscaler`
- Video / audio processing: Activate `ffmpeg` skill or use bash directly
- **Full cinematic production**: Activate `grok-imagine-cinematic-studio` (23-agent suite)

### Document Tasks
- PDF: `pdf` skill
- Word (.docx): `docx` skill
- PowerPoint (.pptx): `pptx` skill
- Excel (.xlsx): `xlsx` skill

### GitHub & Connected Services
- All GitHub operations: Activate `github-repo-manager` skill first
- Discover connected services (GitHub, Gmail, Outlook, Google Drive, Canva): `search_connected_tools`
- Then execute with `call_connected_tool`

### Memory & Personalization
- When the user shares personal facts, preferences, or life updates that may warrant remembering: Use the `memory-edit` skill (consult its SKILL.md).

### Render Components (Final Response Only)
Use these in the **final response** (never inside function calls):
- `render_generated_image`, `render_edited_image`, `render_searched_image`
- `render_inline_citation` (for web / X / collection results)
- `render_file` (for local artifacts the user can download)

## Cinematic Studio & Multi-Agent Workflows

For any complex visual storytelling, film-style image sequences, video production, or NSFW cinematic work:

**Primary activation command:**  
`Activate Grok Imagine Cinematic Studio v3.6` or `Start cinematic production`

This engages the full **23 specialized agents** (v3.6 personalities) including:
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

Specialist activation patterns are documented in the cinematic studio skill references and `references/agents/AGENT_INDEX.md`.

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

| Category                    | Skill                                      | When to Activate |
|-----------------------------|--------------------------------------------|------------------|
| **Skill Development**       | `skill-creator`                            | Creating, updating, or validating any new skill |
| **Cinematic Production**    | `grok-imagine-cinematic-studio`            | Full multi-agent film-style workflows, production bibles, long sequences |
| **Video Upscale & Polish**  | `ai-video-upscaler`                        | Final delivery upscale, face restoration, artifact cleanup on generated video |
| **Image Recreation & Editing** | `ai-image-recreation`, `generated-image-editor` | Style transfer, enhancement, variation, or iterative refinement of images |
| **Character Consistency**   | `character-dna-extractor`                  | Forensic DNA extraction, Identity Lock handoff, prompt injection (`dna lock`, `dna inject`) |
| **Sequence Extension**      | `cinematic-sequence-extender`, `extend-frame-to-video` | Extending stills into video, rough-cut animatics, or continuing clips |
| **Custom Agents**           | `custom-grok-cinematic-agent`              | Drafting or customizing bespoke cinematic production agents / role cards |
| **Quota & Efficiency**      | `workflow-quota-optimizer`                 | Long-form generation sessions, cost/quota management, production planning |
| **NSFW Batch Orchestration**| `nsfw-quota-orchestrator`                    | Quota-aware erotic image+video batches on Heavy, i2v decisions, daily reports (with ErosForge) |
| **NSFW Sequence Extension** | `nsfw-sequence-extender`                     | Sensual 30–120s+ extension from reference/clip, prompt chains, erotic pacing, artifact QA (with ErosForge) |
| **GitHub Management**       | `github-repo-manager`                      | Create repo, push, PRs, issues, file operations on GitHub |
| **Video / Audio**           | `ffmpeg`                                   | Trimming, merging, subtitles, compression, GIFs, storyboards |
| **Documents**               | `pdf`, `docx`, `pptx`, `xlsx`              | Professional document or presentation creation |
| **Memory**                  | `memory-edit`                              | User shares personal facts/preferences worth remembering or updating |

## Grok Build & xAI Model Registry

Canonical slugs live in `tools/models.py` and `references/MODELS_v3.6.md`. List via:

```bash
python tools/cinematic_studio_cli.py models list
```

| Layer | Default Slug | When to Use |
|-------|--------------|-------------|
| Grok Build CLI | `grok-composer-2.5-fast` | Default agent orchestration |
| Grok Build fork | `grok-build` | Code, skills, repo tooling |
| xAI Chat API | `grok-4.3` | Cinematic orchestration, 1M context |
| xAI Build API | `grok-build-0.1` | Agentic/coding automation |
| Imagine Video | `grok-imagine-video-1.5` | Native audio video ($0.08/sec) |
| Imagine Image | `grok-imagine-image` | Reference stills ($0.02/image) |

Local config: `~/.grok/config.toml` sets `fork_secondary_model = "grok-build"`.

## Project-Specific Notes

- Primary ongoing project: **Grok Imagine Cinematic Studio** (v3.6) and related custom skills.
- All generated artifacts **must** be saved to `/home/workdir/artifacts/`.
- Persistent state and custom skills live in `/home/workdir/.grok/skills/`.
- The workspace supports both SFW cinematic work and NSFW/erotic cinematic pipelines (via ErosForge when explicitly activated).
- Keep this `AGENTS.md` in sync with the GitHub repository.

## Quick Start for New Tasks

1. Clarify the goal with the user if ambiguous.
2. Check if an existing skill covers it (use `ls /home/workdir/.grok/skills/` or read relevant SKILL.md).
3. If no skill exists and the task is repeatable/specialized → create one with `skill-creator`.
4. Execute using the correct tool(s) / skill activation.
5. Save all outputs to `artifacts/`.
6. In the **final response**, use appropriate render components and provide clear, actionable output.

---

**This AGENTS.md is the canonical reference for all AI agents operating in this environment.**  
Update it whenever workflows, skills, or best practices evolve.

*Maintained for SuperGrokPro cinematic & development workflows — June 2026*