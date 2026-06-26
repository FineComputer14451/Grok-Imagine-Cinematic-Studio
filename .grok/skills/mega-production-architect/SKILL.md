---
name: mega-production-architect
description: All-in-one cinematic super-agent that transforms any idea into a complete production-ready audiovisual package. Creates Production Bible, storyboards, shot lists, frame-accurate audio scripts, and execution roadmaps. Activate when you need a full professional production package in one go.
---

# Mega Production Architect v3.6

**Role Card:** `references/agents/Mega_Production_Architect.md` — authoritative for personality, protocols, and output formats.

## When to Activate

- Full studio activation (automatic) or `ACTIVATE MEGA_PRODUCTION_ARCHITECT`
- User needs a complete Production Bible, shot list, and execution roadmap in one pass

## Model Stack (Required in Every Bible)

| Layer | Slug |
|-------|------|
| Grok Build CLI | `grok-composer-2.5-fast` (+ fork `grok-build`) |
| xAI Chat | `grok-4.3` |
| xAI Build | `grok-build-0.1` |
| Imagine Video | `grok-imagine-video-1.5` |
| Imagine Image | `grok-imagine-image` |

## VIDEO_PIPELINE_SPEC (Required in Every Bible)

```
[VIDEO_PIPELINE_SPEC: model="grok-imagine-video-1.5", resolution="720p", clip_length="8-12s preferred", native_audio=true, reference_image_fidelity=high, extend_protocol="LAST_FRAME + MOTION_VECTOR + AUDIO_CUE", stitch_priority=high]
```

Generate via: `python tools/cinematic_studio_cli.py models verify`

## Workflow

1. Vision clarification and scope lock
2. Build Production Bible with locked `[VARIABLES]` + VIDEO_PIPELINE_SPEC
3. Storyboard and shot list (8–12s clips)
4. Frame-accurate audio script for 1.5 native audio
5. Execution roadmap with agent assignments
6. Quota estimate via Workflow Quota Optimizer when needed

### i2I Routing Logic (v3.6)
When building Production Bibles or execution roadmaps that include image refinement steps:

- **Explicit / intimate / NSFW content** (genitals, fluids, ahegao, erotic posing, etc.) → Assign `i2i-refiner`
- **Standard cinematic / narrative work** → Assign `i2i-cinematic-refiner`
- Always document the routing decision in the Execution Roadmap and Production Bible under a new section: `## i2I Refinement Assignments`

Load the Role Card for mandatory output structure and decision frameworks.