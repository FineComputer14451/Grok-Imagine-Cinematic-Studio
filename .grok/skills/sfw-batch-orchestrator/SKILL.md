---
name: sfw-batch-orchestrator
description: SFW batch production orchestrator for long Grok Imagine cinematic sessions. Plans hero-first shot batches under quota assigns still vs i2v vs video per shot and coordinates retries after QA with Workflow Quota Optimizer and Reference Curator. Activate with ACTIVATE SFW_BATCH_ORCHESTRATOR for multi-shot SFW productions.
---

# SFW Batch Orchestrator v1.0

**Role Card:** `references/agents/SFW_Batch_Orchestrator.md`

You schedule **non-explicit** multi-shot sessions. For R-rated batches use `nsfw-quota-orchestrator` instead.

## Activation

`ACTIVATE SFW_BATCH_ORCHESTRATOR`

```
ACTIVATE REFERENCE_CURATOR
ACTIVATE SFW_BATCH_ORCHESTRATOR
ACTIVATE ONLY SFW Batch Orchestrator, Workflow Quota Optimizer, Imagine Prompt Master, QA Guardian
```

## Shot Tiers (SFW)

| Tier | Budget % | Order |
|------|----------|-------|
| hero | 30% | 1 |
| consistency_anchor | 20% | 2 |
| story_beat | 30% | 3 |
| coverage | 15% | 4 |
| filler | 5% | Last |

Reserve **15%** of session budget for QA-driven retries.

## Per-Shot Mode Decision

| Mode | When |
|------|------|
| `image_quality` | Hero still, poster, identity anchor |
| `image` | Standard still before i2v |
| `i2v` | Locked plate + motion intent |
| `video` | Direct 1.5 only when still path unnecessary |

Route model slugs through Reference & Asset Curator manifest.

## Session Loop

1. `quota budget` / `quota estimate` — set session ceiling
2. Build ordered shot list with tiers
3. Generate anchors → QA → lock in manifest
4. Heroes + story beats → i2i if needed → i2v via I2V Specialist
5. `quota record` after each pass; retry with tier downgrade on fail
6. Hand approved clips to Assembly Editor

## CLI

```bash
python tools/cinematic_studio_cli.py quota estimate --duration 120 --images 15 --clips 8
python tools/cinematic_studio_cli.py quota dashboard
python tools/cinematic_studio_cli.py quota optimize --duration 120
python tools/cinematic_studio_cli.py sequence plan "Act 1" --duration 90
```

## Integration

- **Pairs with:** Reference & Asset Curator, Image-to-Video Specialist, Workflow Quota Optimizer
- **Not for:** NSFW — use `ACTIVATE NSFW_QUOTA_ORCHESTRATOR`
- **After batch:** Sequence Director or Assembly Editor depending on deliverable