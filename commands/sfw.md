---
description: Plan SFW multi-shot batches with hero-first tiers, Reference Curator model routing, and quota-aware scheduling.
---

# SFW Batch Production

Non-explicit multi-shot sessions under SuperGrok Pro/Heavy quota limits.

## Activation

`ACTIVATE SFW_BATCH_ORCHESTRATOR` + `ACTIVATE REFERENCE_CURATOR`

## CLI

```bash
python tools/cinematic_studio_cli.py sfw plan "Hero Session" \
  --shot "hero:Cover frame, golden hour" \
  --shot "consistency_anchor:Profile neutral" \
  --shot "story_beat:Reveal beat" \
  --budget 400

python tools/cinematic_studio_cli.py sfw next "hero-session" --count 3
python tools/cinematic_studio_cli.py sfw decide shot_001 --tier hero --has-ref
python tools/cinematic_studio_cli.py sfw record "hero-session" shot_001 --score 8.5 --credits 45
python tools/cinematic_studio_cli.py sfw list
```

## Shot tiers

| Tier | Budget % | Order |
|------|----------|-------|
| hero | 30% | 1 |
| consistency_anchor | 20% | 2 |
| story_beat | 30% | 3 |
| coverage | 15% | 4 |
| filler | 5% | Last |

For R-rated batches use `/nsfw` instead.