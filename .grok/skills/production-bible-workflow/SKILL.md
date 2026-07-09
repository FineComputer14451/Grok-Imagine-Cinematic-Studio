---
name: production-bible-workflow
description: End-to-end Production Bible onboarding workflow for Grok Imagine Cinematic Studio. Guides create-bible DNA init sequence planning quota setup and validate through the CLI. Activate when starting a new project bootstrapping the studio or onboarding a production from zero.
---

# Production Bible Workflow v1.0

**Pipeline skill** — new project bootstrap using CLI + Project Bible.


## Model Layer (Grok 4.5 · studio v3.6.7)

| Layer | Slug | When |
|-------|------|------|
| Orchestration (default) | `grok-4.5` | Bibles, direction, agent loops |
| Long-context (opt-in) | `grok-4.3` | 1M memory banks (`--chat-model grok-4.3`) |
| Grok Build CLI | `grok-4.5` · `grok-build` | Skills / coding (≥ 0.2.93) |
| Imagine Video | `grok-imagine-video` / `1.5` | 1.0 cost · 1.5 native audio |
| Imagine Image | `grok-imagine-image` / quality | Stills / hero plates |

Prefer stable `prompt_cache_key` on multi-turn `grok-4.5` loops. Full stack: `references/agents/MODEL_LAYER_v3.6.7.md` · `tools/models.py`.

## Activation

`START PRODUCTION BIBLE WORKFLOW` · `BOOTSTRAP NEW PROJECT`

## Phase 1 — Foundation

```bash
python tools/cinematic_studio_cli.py validate
python tools/cinematic_studio_cli.py models verify
python tools/cinematic_studio_cli.py status
```

Create bible + activation prompt (direct path — preferred for scripts):
```bash
python tools/cinematic_studio_cli.py create-bible "Project Title" \
  --genre "Sci-Fi" --chat-model grok-4.5 --video-model 1.5

python tools/cinematic_studio_cli.py generate-prompt "Opening scene description" \
  --chat-model grok-4.5 --video-model 1.5 -o artifacts/activation_prompt.txt
```

Optional guided wizard (interactive TTY only; same Bible shape):
```bash
python tools/cinematic_studio_cli.py create-bible --wizard
# Web UI: Production → Guided Bible Creator
```

## Phase 2 — Characters

```bash
python tools/cinematic_studio_cli.py dna init "Lead Character" \
  --core "Core identity" --anchor "Distinctive visual anchor"

python tools/cinematic_studio_cli.py dna handoff "Lead Character"
python .grok/skills/handoff-packet-validator/scripts/validate_handoff.py \
  characters/lead-character/handoff.json

python tools/cinematic_studio_cli.py dna lock "Lead Character"
```

## Phase 3 — Sequence + Quota

```bash
python tools/cinematic_studio_cli.py quota budget --tier supergrok_pro
python tools/cinematic_studio_cli.py quota estimate --duration 120 --images 10

python tools/cinematic_studio_cli.py sequence init "Act 1" --duration 90 --genre "Thriller"
python tools/cinematic_studio_cli.py sequence show "Act 1"
```

## Phase 4 — Pre-vis (optional)

```
ACTIVATE ANIMATIC DIRECTOR
```

## Phase 5 — Production activation

```
Activate Grok Imagine Cinematic Studio v3.6.7
ACTIVATE REFERENCE_CURATOR
ACTIVATE SFW_BATCH_ORCHESTRATOR   # multi-shot
# or
ACTIVATE SEQUENCE_DIRECTOR        # long-form chain
```

## Phase 6 — Delivery path

```
RUN QA REVIEW
ACTIVATE ASSEMBLY_EDITOR
ACTIVATE AI_POLISH_DIRECTOR
# cinematic-ffmpeg for final mux
```

## Project Bible Must Include

- `VIDEO_PIPELINE_SPEC` with `grok-imagine-video-1.5`
- Model stack from `tools/models.py`
- Character DNA slugs + locked anchors
- Sequence slug(s) + chain QA status
- Quota tier + session budget

## Report

```bash
python tools/cinematic_studio_cli.py report -o artifacts/production_report.pdf
python tools/cinematic_studio_cli.py validate
```

## Integration

Runs once per new production; Studio Director maintains bible after bootstrap.