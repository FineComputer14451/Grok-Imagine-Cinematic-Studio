# Pricing Model v3.7.1 — xAI Imagine & Grok Build (Grok 4.6)

Official xAI per-second/per-image pricing for quota planning. Skill: `workflow-quota-optimizer`.  
Canonical registry: `tools/models.py` and `references/MODELS_v3.6.md`.

**Prefer video 1.0 ($0.05/s) unless native audio requires 1.5 ($0.08/s).**  
Override via `.quota_config.json` in project root.

---

## xAI Imagine Rates (USD)

| Model | Rate |
|-------|------|
| `grok-imagine-video-1.5` | **$0.080 / second** |
| `grok-imagine-video` | $0.050 / second |
| `grok-imagine-image` | $0.02 / image |
| `grok-imagine-image-2.0` | 1K low $0.04 / medium $0.06; 2K low $0.06 / medium $0.08; input $0.01 |
| `grok-imagine-image-quality` | Retired 2026-11-02 — billed as 2.0 `quality=low` |

Native audio is included in 1.5 per-second pricing (no surcharge).

---

## Credit Conversion

Quota dashboard uses abstract credits for subscription tier compatibility:

| Unit | Value |
|------|-------|
| 1 credit | $0.01 |
| 1.5 video (10s) | 80 credits ($0.80) |
| 1.0 video (10s) | 50 credits ($0.50) |
| Standard image | 2 credits ($0.02) |
| Image 2.0 1K medium | 6 credits ($0.06) |

---

## Production Overhead (Configurable)

| Resource | Rate |
|----------|------|
| Extend/stitch overhead | +3 credits/clip (after clip 1) |
| Fast mode | 55% of base rate |
| Quality pass (after fast) | +100% of base for hero shots |
| Retry buffer | ×1.15 on estimates |

---

## xAI Chat Models (Agent Orchestration — Grok 4.6 default)

| Model | Input / 1M | Output / 1M | Context | Role |
|-------|------------|-------------|---------|------|
| `grok-4.6` | $2.00 ($0.50 cached) | $6.00 | 500k | **Cinematic + Build default** |
| `grok-4.3` | $1.25 | $2.50 | 1M | **Opt-in** long Bibles / memory banks |
| `grok-build-0.1` | $1.00 | $2.00 | 256k | Legacy (prefer 4.6) |

**4.6 cost tip:** set a stable `prompt_cache_key` (project slug) on multi-turn agent loops — cached input is $0.50/1M.

## Grok Build CLI

| Model | Role |
|-------|------|
| `grok-4.6` | Default agent + cinematic (recommend CLI ≥ 1.0.5); `grok-4.5` aliases wrap 4.6 |
| `grok-build` | Fork secondary (coding) |
| `grok-composer-2.5-fast` | Creative / multi-agent direction |
| `grok-4.3` | Optional 1M sessions inside Build |

Full registry: `tools/models.py`, `references/MODELS_v3.6.md`

---

## Subscription Tiers

| Tier | Monthly Credits | Daily Soft Cap |
|------|-----------------|----------------|
| SuperGrok Pro | 10,000 | 500 |
| SuperGrok Heavy | 50,000 | 2,500 |
| Custom | user-defined | user-defined |

## Risk Levels

| Budget % Used | Risk |
|---------------|------|
| < 25% | Low |
| 25–49% | Medium |
| 50–79% | High |
| ≥ 80% | Critical |

## CLI

```bash
python tools/cinematic_studio_cli.py models list
python tools/cinematic_studio_cli.py quota estimate --duration 90 --clips 9 --video-model 1.5
python tools/cinematic_studio_cli.py quota clip 10 --video-model grok-imagine-video
python tools/cinematic_studio_cli.py quota sequence "Neon Alley Chase"
python tools/cinematic_studio_cli.py quota dashboard
python tools/cinematic_studio_cli.py quota budget --tier supergrok_heavy
python tools/cinematic_studio_cli.py quota record --credits 80 --note "clip_001 10s 1.5"
python tools/cinematic_studio_cli.py quota optimize --duration 90 --clips 9 --fast-mode
```

## Fast Mode → Quality Pass Strategy

1. Iterate all clips in Fast mode (~45% savings)
2. Chain QA on each clip
3. Quality pass only on hero shots and failed QA clips
4. Typical savings: 30–40% vs full-quality-every-clip

## Custom Config Example (`.quota_config.json`)

```json
{
  "imagine_video": {
    "grok-imagine-video-1.5": {"usd_per_second": 0.08},
    "grok-imagine-video": {"usd_per_second": 0.05}
  },
  "imagine_image": {
    "grok-imagine-image": {"usd_per_image": 0.02},
    "grok-imagine-image-2.0": {"usd_per_image": 0.04}
  },
  "default_video_model": "grok-imagine-video-1.5",
  "fast_mode_multiplier": 0.55,
  "usd_per_credit": 0.01
}
```