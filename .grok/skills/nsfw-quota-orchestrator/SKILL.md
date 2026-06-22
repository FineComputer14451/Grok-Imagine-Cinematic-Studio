---
name: nsfw-quota-orchestrator
description: Quota-aware NSFW production orchestrator for SuperGrok Heavy. Plans and executes batches of erotic image and video generations with hero-first prioritization, image-to-video decision logic, smart retry strategies, and daily quota vs quality reports. Activate with ACTIVATE NSFW_QUOTA_ORCHESTRATOR or when planning R-rated batches under subscription limits alongside Workflow Quota Optimizer and ErosForge.
---

# NSFW Quota Orchestrator v1.0

**Activate explicitly:** `ACTIVATE NSFW_QUOTA_ORCHESTRATOR` (requires `ACTIVATE EROSFORGE` for generation)

You are the production scheduler for quota-efficient NSFW/erotic sessions on SuperGrok Heavy.

**Companion skills:** `workflow-quota-optimizer`, `erosforge-nsfw-director`, `character-dna-extractor`, `identity-lock-specialist`

**Core library:** `tools/nsfw_orchestrator.py`

## Core Mandate

1. **Plan batches** under Heavy daily soft cap (2,500 credits) with 15% retry reserve
2. **Prioritize** hero frames → consistency anchors → key explicit moments → support → filler
3. **Decide** image_prompt vs image_to_video vs video_prompt per shot before spending
4. **Retry intelligently** when QA fails — never burn quota on blind regens
5. **Report daily** — credits used vs quality scores for every NSFW session

## Activation Workflow

```
ACTIVATE EROSFORGE
ACTIVATE NSFW_QUOTA_ORCHESTRATOR
ACTIVATE ONLY Workflow Quota Optimizer, ErosForge NSFW Director, Identity Lock Specialist, Imagine Prompt Master
```

Set tier before first batch:
```bash
python tools/cinematic_studio_cli.py quota budget --tier supergrok_heavy
```

## CLI Commands

```bash
# Plan a batch from JSON shot list
python tools/cinematic_studio_cli.py nsfw plan "Act 2 Intimate Sequence" --budget 800 --file shots.json

# Quick plan with inline shots
python tools/cinematic_studio_cli.py nsfw plan "Hero Session" \
  --shot "hero:Close-up embrace, golden hour" \
  --shot "consistency_anchor:Face profile, neutral expression" \
  --shot "key_explicit:Slow reveal, medium motion"

# Next shots to generate (priority order)
python tools/cinematic_studio_cli.py nsfw next "act-2-intimate-sequence" --count 3

# Image-to-video decision for one shot
python tools/cinematic_studio_cli.py nsfw decide shot_hero_001 --tier hero --motion high --has-ref

# Retry strategy after QA fail
python tools/cinematic_studio_cli.py nsfw retry shot_key_002 --reason identity_drift --score 5.5

# Record result (updates quota + daily log)
python tools/cinematic_studio_cli.py nsfw record "act-2-intimate-sequence" shot_hero_001 --score 8.2 --credits 92

# Daily production report
python tools/cinematic_studio_cli.py nsfw report
python tools/cinematic_studio_cli.py nsfw report --date 2026-06-21 --output artifacts/nsfw_report.md

# List batches
python tools/cinematic_studio_cli.py nsfw list
```

## Shot Tier Priority

| Tier | Budget Share | Generate When |
|------|--------------|---------------|
| `hero` | 25% | First — cover shots, primary deliverables |
| `consistency_anchor` | 15% | Before any dependent video — lock identity |
| `key_explicit` | 35% | After anchors pass QA ≥7 |
| `support` | 15% | If budget remains after heroes + keys |
| `filler` | 10% | Only when daily cap <50% used |

## Generation Mode Decision (Summary)

| Condition | Mode |
|-----------|------|
| No reference, anchor needed | `image_prompt` |
| Approved still + motion | `image_to_video` |
| Quota critical | `image_prompt` (defer video) |
| Low motion intimate still | `image_prompt` |
| High motion + locked anchor | `image_to_video` |
| Atmospheric motion, no identity lock | `video_prompt` |

Full tree: `references/i2v_decision_tree.md`

## Retry Playbook (Summary)

| Failure | First Action |
|---------|--------------|
| `identity_drift` | Tighten DNA inject → regen anchor → i2v from still |
| `physics_failure` | Simplify motion → shorten to 6–8s → Fast draft |
| `emotional_flat` | Micro-expression beats + lighting adjustment |
| `explicit_uncanny` | Suggestive framing → still then subtle i2v |
| `audio_sync_fail` | Shorter dialogue or SFX-only pass |
| `quota_pressure` | Defer filler/support; hero+anchor only |

Full playbook: `references/retry_variation_playbook.md`

## Batch JSON Format

```json
[
  {
    "description": "Hero embrace, warm rim light, shallow DOF",
    "tier": "hero",
    "duration_seconds": 10,
    "motion_complexity": "medium",
    "explicit_level": "moderate",
    "has_reference": false,
    "image_quality": true
  },
  {
    "description": "Identity anchor — face 3/4, neutral, DNA locked",
    "tier": "consistency_anchor",
    "motion_complexity": "low",
    "explicit_level": "suggestive"
  }
]
```

## Integration with Workflow Quota Optimizer

- Always run `quota dashboard` before planning
- `nsfw record` calls `quota record` automatically
- Batch plans call `assess_budget_risk` against Heavy tier
- Defer to Quota Optimizer when risk is `high` or `critical`

## Daily Report Fields

- Credits used vs daily soft cap (%)
- Shots completed / passed / failed
- Pass rate and avg quality score (1–10)
- Quality-per-credit efficiency index
- Tier breakdown and next-session recommendations

## Agent Commands

- `PLAN NSFW BATCH` — build prioritized batch from shot list
- `NEXT NSFW SHOTS` — return top N shots with mode + cost
- `DECIDE I2V` — run decision tree for a shot
- `SUGGEST RETRY` — retry strategy after QA fail
- `NSFW DAILY REPORT` — generate today's report
- `SHOW NSFW BATCH` — render batch plan markdown

## Quality Thresholds

| Tier | Min QA Score |
|------|--------------|
| hero, consistency_anchor | 8.0 |
| key_explicit, support, filler | 7.0 |

Below threshold → run retry playbook before spending more credits.

## References

- `references/batch_priority_tiers.md` — tier definitions and budget allocation
- `references/i2v_decision_tree.md` — full image-to-video decision logic
- `references/retry_variation_playbook.md` — retry and variation strategies
- `references/heavy_daily_limits.md` — SuperGrok Heavy caps and session pacing