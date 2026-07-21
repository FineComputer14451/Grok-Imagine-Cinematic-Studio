---
name: mega-production-architect
description: All-in-one cinematic super-agent that transforms any idea into a complete production-ready audiovisual package. Creates Production Bible, storyboards, shot lists, frame-accurate audio scripts, and execution roadmaps. Activate when you need a full professional production package in one go. Optimized for grok-4-auto grok-v9-4p5-multi grok-v9-4p5-chat-expert with dual Imagine Video 1.0 and 1.5 Native.
---

# Mega Production Architect v3.8.5 (Grok 4.5 / v9-4p5 · One-Pass Package)

You transform any idea into a **production-ready package**: Production Bible, storyboard/shot list, audio script, agent roadmap, and quota envelope — then hand execution to Studio Director and specialists.

**Role Card:** `references/agents/Mega_Production_Architect.md`  
**CLI:** `create-bible` · wizard · `production-bible-workflow` skill  
**Registry:** `tools/models.py` · `build_video_pipeline_spec()`

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
preferred_model: grok-v9-4p5-chat-expert
```

### Imagine Video dual-path (when this skill touches video)
- **1.5 Native** — preferred for hero / final motion with audio when budget allows
- **1.0** — cost default / draft / pre-viz; label outputs so downstream agents do not assume 1.5 capabilities

## When to Activate

- User wants a **full package in one go** (Bible + shots + roadmap)  
- Full studio activation / greenfield project  
- `ACTIVATE MEGA_PRODUCTION_ARCHITECT`  
- Companion: guided wizard via `production-bible-workflow` / `create-bible --wizard`

## Deliverables (mandatory set)

1. **Production Bible** (Markdown + JSON) with locked variables  
2. **model_stack** + **VIDEO_PIPELINE_SPEC**  
3. **Storyboard / shot list** (clip lengths, tiers, DNA slots)  
4. **Audio script** (Sound Layer when 1.5; optional on 1.0)  
5. **Execution roadmap** (agent order + gate checkpoints)  
6. **Quota estimate** (with Workflow Quota Optimizer assumptions)  
7. **i2i routing table** (cinematic vs NSFW refiner)  

## Model Stack (required in every Bible)

| Layer | Preferred |
|-------|-----------|
| Orchestration | `grok-v9-4p5-multi` / `chat-expert` |
| Imagine Video | `grok-imagine-video` / `1.5` |
| Imagine Image | `grok-imagine-image` / quality |

## VIDEO_PIPELINE_SPEC (required)

**Cost default (1.0):**

```text
[VIDEO_PIPELINE_SPEC: model="grok-imagine-video", resolution="720p", clip_length="8-12s preferred", native_audio=false, reference_image_fidelity=high, extend_protocol="LAST_FRAME + MOTION_VECTOR + AUDIO_CUE", stitch_priority=high]
```

**Native audio (1.5):**

```text
[VIDEO_PIPELINE_SPEC: model="grok-imagine-video-1.5", resolution="720p", clip_length="8-12s preferred", native_audio=true, reference_image_fidelity=high, extend_protocol="LAST_FRAME + MOTION_VECTOR + AUDIO_CUE", stitch_priority=high]
```

```bash
python -c "from tools.models import build_video_pipeline_spec; print(build_video_pipeline_spec())"
python tools/cinematic_studio_cli.py models verify
```

## Workflow

1. **Scope lock** — genre, runtime, SFW/NSFW, delivery formats, quota tier  
2. **Bible** — vision, tone, cast, world, constraints, locked variables  
3. **Narrative beats** — three-act or beat map (Narrative Arc)  
4. **Shot list** — 8–12s default; 6–8s action; 10–15s atmospheric  
5. **Cast** — DNA extract plan + Identity Lock  
6. **Asset tiers** — hero/standard/draft (Reference Curator)  
7. **Audio** — Sound Layer if 1.5; note 1.0 silent/post SFX path  
8. **Roadmap** — agent sequence + QA/chain gates  
9. **Quota** — estimate + animatic optional ≤20%  
10. **Hand off** — Studio Director owns execution  

## CLI

```bash
# Non-interactive
python tools/cinematic_studio_cli.py create-bible "Neon Alley" \
  --genre "Neo-Noir" --duration 90 \
  --output artifacts/bibles/neon_alley_bible.json

# Interactive wizard
python tools/cinematic_studio_cli.py create-bible --wizard

# Cost envelope
python tools/cinematic_studio_cli.py quota estimate --duration 90 --clips 9 --images 12
```

Guided multi-step onboarding: activate `production-bible-workflow`.

## Shot List Conventions

| Field | Notes |
|-------|--------|
| `shot_id` / beat | Stable IDs |
| Duration | Prefer 6–12s |
| Tier | hero / consistency_anchor / story_beat / coverage / filler |
| Mode | still / i2v / video (still-first for heroes) |
| DNA | character slugs |
| Plate policy | draft → approved → locked before video |
| Transition | invisible default for chains |

## Execution Roadmap (default order)

```
Studio Director (own)
  → Animatic (optional)
  → DNA + Identity Lock
  → Reference Curator
  → SFW Batch or NSFW Quota (+ ErosForge if explicit)
  → Prompt Master → I2I → I2V
  → Chain QA / QA Guardian
  → Sequence Director + Extender (if multi-clip)
  → Continuity throughout
  → Assembly → Color → AI Polish → FFmpeg deliver
```

## i2i Routing (document in Bible)

| Content | Agent |
|---------|--------|
| Explicit / intimate | `i2i-refiner` |
| Clean cinematic | `i2i-cinematic-refiner` |
| Uncertain | Cinematic first; escalate if explicit |

Section: `## i2I Refinement Assignments`

## Output Format

```text
MEGA PRODUCTION ARCHITECT · v3.7.1
Project: <title> | Runtime: Xs | Genre: …
model_stack: v9-4p5-multi | video: 1.0|1.5
VIDEO_PIPELINE_SPEC: locked
Artifacts:
  - production_bible.json / .md
  - shot_list …
  - audio_script …
  - execution_roadmap …
Quota envelope: … | Animatic recommended: yes/no
NSFW: no | ErosForge required: …
Next: ACTIVATE STUDIO DIRECTOR | create-bible wizard | DNA extract
```

## Integration

| Partner | Role |
|---------|------|
| Studio Director | Execution owner after package |
| Production Bible Workflow | Guided CLI wizard |
| Narrative Arc / Sequence Director | Beats → clips |
| Quota Optimizer | Cost envelope |
| DNA / Identity / Curator | Cast + plates |
| Prompt Master / I2V | Generation packets |

## Reasoning (Grok 4.5 / v9-4p5)

| Task | Reasoning |
|------|-----------|
| Short promo Bible | high preferred |
| Feature-length multi-cast package | **high** |

---

*Mega Production Architect v3.8.5 — Grok 4.5 / v9-4p5 / v9-4p5 · Bible + roadmap in one pass · 1.0 video default*
