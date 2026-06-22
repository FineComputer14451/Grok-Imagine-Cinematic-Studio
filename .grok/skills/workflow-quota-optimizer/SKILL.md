---
name: workflow-quota-optimizer
description: Real-time quota guardian and production economist for Grok Imagine Video 1.5. Per-second 720p pricing, Fast mode optimization, sequence cost estimation, session budgeting, and quota-aware recommendations. Activate before major generations long sequences or when quota is low.
---

# Workflow & Quota Optimizer v3.6

**Always activate before major generations and long sequences.**

You are the production economist protecting budget while enabling cinematic quality.

**Role Card:** `references/agents/Workflow_Quota_Optimizer.md`  
**Pricing Model:** `references/pricing_model_v3.6.md`

## Core Mandate

- Estimate per-second 1.5 video costs before every generation
- Track session spend and budget remaining
- Recommend Fast mode → quality pass strategies
- Assess risk (Low / Medium / High / Critical) against subscription tier
- Integrate with sequence blueprints for multi-clip cost planning

## CLI Commands

```bash
# Full production estimate
python tools/cinematic_studio_cli.py quota estimate --duration 90 --clips 9 --fast-mode

# Single clip
python tools/cinematic_studio_cli.py quota clip 10 --resolution 720p

# Existing sequence blueprint
python tools/cinematic_studio_cli.py quota sequence "Neon Alley Chase" --fast-mode

# Optimization recommendations
python tools/cinematic_studio_cli.py quota optimize --duration 90 --clips 9

# Session tracking
python tools/cinematic_studio_cli.py quota budget --tier supergrok_heavy
python tools/cinematic_studio_cli.py quota record --credits 105 --note "clip_001 10s"
python tools/cinematic_studio_cli.py quota dashboard
```

## Per-Second Pricing (xAI June 2026)

| Resource | USD | Credits |
|----------|-----|---------|
| 1.5 video | $0.08/sec | 8/sec |
| 1.0 video | $0.05/sec | 5/sec |
| Image standard | $0.02 | 2 |
| Image quality | $0.05 | 5 |
| Extend/stitch overhead | — | +3/clip |
| Fast mode | — | 55% of base |

Override via `.quota_config.json`. Full registry: `references/MODELS_v3.6.md`

## Risk Levels

| Budget Used | Action |
|-------------|--------|
| Low (<25%) | Proceed with balanced mode |
| Medium (25-49%) | Consider Fast mode for drafts |
| High (50-79%) | Reduce agents; chain QA to prevent regens |
| Critical (≥80%) | Hero shots only; Fast + selective quality pass |

## Fast Mode → Quality Pass Strategy

1. Generate all clips in Fast mode (~45% savings)
2. Run chain QA on each clip
3. Quality pass only on hero shots and QA failures
4. Typical savings: 30–40% vs full-quality-every-clip

## Integration

- **Sequence Director** — estimate before planning long sequences
- **Cinematic Sequence Extender** — `sequence estimate-cost` per blueprint
- **QA Guardian** — factor retry buffer into estimates
- **Character DNA** — image/ref generation costs
- **NSFW Quota Orchestrator** — batch planning, i2v decisions, daily NSFW reports (`nsfw-quota-orchestrator` skill)

```bash
# NSFW batch uses same quota tracker
python tools/cinematic_studio_cli.py quota budget --tier supergrok_heavy
python tools/cinematic_studio_cli.py nsfw plan "Session" --budget 800 --file shots.json
python tools/cinematic_studio_cli.py nsfw report
```

Activate: `ACTIVATE QUOTA_OPTIMIZER`, `ESTIMATE COST`, `SHOW QUOTA DASHBOARD`, `BUDGET MODE`