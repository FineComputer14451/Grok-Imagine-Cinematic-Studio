---
name: production-bible-workflow
description: End-to-end Production Bible onboarding workflow for Grok Imagine Cinematic Studio. Guides create-bible DNA init sequence planning quota setup and validate through the CLI. Activate when starting a new project bootstrapping the studio or onboarding a production from zero. Optimized for grok-4-auto grok-v9-4p5-multi grok-v9-4p5-chat-expert with dual Imagine Video 1.0 and 1.5 Native.
---

# Production Bible Workflow v3.8.5 (Grok 4.5 / v9-4p5 · Bible Onboarding)

**New project bootstrap** — guided path from zero to a locked Production Bible, DNA, sequence, quota, and generation-ready handoff. Studio Director maintains the Bible after bootstrap.

**CLI:** `create-bible` · `dna` · `sequence` · `quota` · `validate` · `models verify`  
**Companions:** Mega Production Architect · Studio Director · production wizard (Web)

## Model Layer (Grok 4.5 / v9-4p5)

| Task type | Preferred model | Reasoning |
|-----------|-----------------|-----------|
| Multi-agent orchestration / handoff synthesis | `grok-v9-4p5-multi` | high |
| Specialist deep craft / QA / identity-critical | `grok-v9-4p5-chat-expert` | high |
| Routine status / draft passes | `grok-4-auto` | medium |

**Stack default:** cinematic+Build API/chat **`grok-4.5`** (CLI ≥ 0.2.93 · fork `grok-build`). Opt-in 1M: `grok-4.3`.  
**Registry:** `tools/models.py` · `references/agents/MODEL_LAYER_v4.5.md` · `models verify`

```yaml
model_compatibility:
  - grok-v9-4p5-chat-expert
  - grok-v9-4p5-multi
  - grok-4-auto
preferred_model: grok-v9-4p5-multi
```

### Imagine Video dual-path (when this skill touches video)
- **1.5 Native** — preferred for hero / final motion with audio when budget allows
- **1.0** — cost default / draft / pre-viz; label outputs so downstream agents do not assume 1.5 capabilities

## When to Activate

- Greenfield project / first session on a machine  
- Onboarding a production from zero  
- User says: `START PRODUCTION BIBLE WORKFLOW`, `BOOTSTRAP NEW PROJECT`, `CREATE BIBLE WIZARD`

Begin: **"Starting Production Bible Workflow v3.8.5 (Grok 4.5 / v9-4p5)…"**

## Project Bible Must Lock

| Field | Rule |
|-------|------|
| `model_stack` | chat/build **`grok-4.5`**; 1M opt-in `grok-4.3` only |
| `VIDEO_PIPELINE_SPEC` | 1.0 cost default or 1.5 for native audio |
| Character DNA | slugs + locked anchors |
| Sequence | slug(s) + chain QA status |
| Quota | tier + session budget |
| `prompt_cache_key` | project slug for multi-turn loops |

## Phase 1 — Foundation

```bash
python tools/cinematic_studio_cli.py validate
python tools/cinematic_studio_cli.py models verify
python tools/cinematic_studio_cli.py status
```

Create Bible (script-friendly path):

```bash
python tools/cinematic_studio_cli.py create-bible "Project Title" \
  --genre "Sci-Fi" --chat-model grok-4.5 --video-model 1.0 \
  --output artifacts/bibles/project_bible.json

python tools/cinematic_studio_cli.py generate-prompt "Opening scene description" \
  --chat-model grok-4.5 --video-model 1.0 -o artifacts/activation_prompt.txt
```

Guided wizard (interactive TTY) / Web Guided Bible Creator:

```bash
python tools/cinematic_studio_cli.py create-bible --wizard
```

Optional 1M: `--chat-model grok-4.3` (alias `long-context`) only when Bible+memory will exceed ~400k.

## Phase 2 — Characters

```bash
python tools/cinematic_studio_cli.py dna init "Lead Character" \
  --core "Core identity" --anchor "Distinctive visual anchor"
python tools/cinematic_studio_cli.py dna handoff "Lead Character"
python .grok/skills/handoff-packet-validator/scripts/validate_handoff.py \
  characters/lead-character/handoff.json
python tools/cinematic_studio_cli.py dna lock "Lead Character"
```

Multi-cast: plan arbiter after ≥2 locks → `ACTIVATE MULTI_CHARACTER_ARBITER`.

## Phase 3 — Sequence + Quota

```bash
python tools/cinematic_studio_cli.py quota budget --tier supergrok_pro
python tools/cinematic_studio_cli.py quota estimate --duration 120 --images 10
python tools/cinematic_studio_cli.py sequence init "Act 1" --duration 90 --genre "Thriller"
python tools/cinematic_studio_cli.py sequence show "Act 1"
```

Activate **Workflow Quota Optimizer** before major spend.

## Phase 4 — Pre-vis (optional ≤20% budget)

```
ACTIVATE ANIMATIC DIRECTOR
```

Validate pacing with draft stills / short motion probes (prefer video **1.0**).

## Phase 5 — Production activation

```
Activate Grok Imagine Cinematic Studio v3.8.5
ACTIVATE STUDIO_DIRECTOR
ACTIVATE REFERENCE_CURATOR
ACTIVATE SFW_BATCH_ORCHESTRATOR   # multi-shot SFW
# or
ACTIVATE SEQUENCE_DIRECTOR        # long-form chain
# R-rated only when explicit:
ACTIVATE EROSFORGE
ACTIVATE NSFW_QUOTA_ORCHESTRATOR
```

When ready to generate (not only plan):

```
ACTIVATE IMAGINE_AGENT_MODE_HANDOFF
```

## Phase 6 — Delivery path

```
RUN QA REVIEW
ACTIVATE ASSEMBLY_EDITOR
ACTIVATE AI_POLISH_DIRECTOR
# cinematic-ffmpeg for final mux / social crops
```

## Report

```bash
python tools/cinematic_studio_cli.py report -o artifacts/production_report.pdf
python tools/cinematic_studio_cli.py validate
```

## Hard Blocks

| Condition | Action |
|-----------|--------|
| No `models verify` | Fix stack before spend |
| Bible without `model_stack` | Re-run create-bible |
| Video without locked DNA (hero) | Phase 2 first |
| Silent NSFW | Route ErosForge first |

## Output Format

```text
PRODUCTION BIBLE WORKFLOW · v3.7.1
Project: … | model_stack: grok-4.5 | video: 1.0|1.5
Bible: artifacts/bibles/…
DNA locked: […] | Sequence: … | Quota tier: …
prompt_cache_key: <slug>
Next: Studio Director | Animatic | Batch | Agent Mode Handoff
```

## Integration

| Partner | Role |
|---------|------|
| Mega Production Architect | One-pass full package alternative |
| Studio Director | Owns Bible after bootstrap |
| Identity Lock / DNA | Cast integrity |
| Quota Optimizer | Session envelope |
| Imagine Agent Mode Handoff | First generation surface |

## Reasoning (Grok 4.5)

| Task | Reasoning |
|------|-----------|
| Wizard step copy | medium |
| Bible lock / model_stack / VIDEO_PIPELINE_SPEC | **high** |
| 1.0 vs 1.5 decision | **high** |

---

*Production Bible Workflow v3.8.5 — Grok 4.5 / v9-4p5 · zero to locked Bible · still before video*
