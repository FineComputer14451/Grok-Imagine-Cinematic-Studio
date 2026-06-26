---
name: animatic-director
description: Low-cost animatic and previsualization workflow before Grok Imagine Video 1.5 spend. Plans storyboard beats still tiers and timing using draft image models and short motion tests to validate pacing under quota. Activate with ACTIVATE ANIMATIC DIRECTOR before long-form or hero batch sessions.
---

# Animatic Director v1.0

**Pipeline skill** — quota-saving pre-vis before full 1.5 production.

## Activation

`ACTIVATE ANIMATIC DIRECTOR`

Typical stack:
```
ACTIVATE ANIMATIC DIRECTOR
ACTIVATE ONLY Animatic Director, Narrative Arc Strategist, Reference Asset Curator, Workflow Quota Optimizer
```

## Goal

Validate **story rhythm, shot coverage, and identity anchors** at ~10–20% of final video cost before hero 1.5 spend.

## Tier Strategy (via Reference Curator)

| Phase | Asset tier | Model |
|-------|------------|-------|
| Storyboard stills | draft | `grok-imagine-image` |
| Layout / composition | standard | `grok-imagine-image` |
| Hero anchor lock | hero | `grok-imagine-image-quality` |
| Motion test (optional) | draft | `grok-imagine-video` short clips |

## Workflow

1. **Beat map** — Narrative Arc heatmap → 8–15 storyboard frames
2. **Still pass** — draft/standard images only; no 1.5 video yet
3. **Timing board** — assign seconds per beat (target sequence duration)
4. **Identity check** — lock 1–2 anchor stills per character (hero tier)
5. **Optional motion probe** — 3–5s `grok-imagine-video` tests for complex camera only
6. **Go/No-Go** — proceed to SFW Batch Orchestrator or Sequence Director

## Cost Gate

```bash
python tools/cinematic_studio_cli.py quota estimate --duration 90 --images 12
python tools/cinematic_studio_cli.py cost-simulate --duration 90 --complexity medium
```

Animatic budget should stay **≤ 20%** of full production estimate unless Director overrides.

## Deliverables

1. **Animatic board** — frame list with duration hints
2. **Locked anchors** — asset IDs approved for i2v
3. **Risk list** — shots needing stunt/VFX/extend planning
4. **Handoff** — Sequence Director or SFW Batch Orchestrator with approved beat map

## Integration

- **Before:** Mega Production Architect bible, Narrative Arc Strategist
- **After:** Reference Curator → I2V Specialist / Sequence Director
- **Skip animatic when:** Single hero shot or trailer under 15s total