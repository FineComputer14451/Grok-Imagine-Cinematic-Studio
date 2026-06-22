# Pricing Model v3.6 — Grok Imagine Video 1.5

Estimated per-second credit model for quota planning. Override via `.quota_config.json` in project root.

---

## Default Rates (Credits)

| Resource | Rate |
|----------|------|
| Video 1.5 @ 720p | 10 credits/second |
| Video 1.5 @ 480p | 6 credits/second |
| Native audio surcharge | +2 credits/second |
| Image generation | 5 credits/image |
| Extend/stitch overhead | +3 credits/clip (after clip 1) |
| Fast mode | 55% of base rate |
| Quality pass (after fast) | +100% of base for hero shots |
| Retry buffer | ×1.15 on estimates |

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
python tools/cinematic_studio_cli.py quota estimate --duration 90 --clips 9
python tools/cinematic_studio_cli.py quota sequence "Neon Alley Chase"
python tools/cinematic_studio_cli.py quota dashboard
python tools/cinematic_studio_cli.py quota budget --tier supergrok_heavy
python tools/cinematic_studio_cli.py quota record --credits 105 --note "clip_001 10s 720p"
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
  "imagine_video_1.5": {
    "720p": {"credits_per_second": 10},
    "480p": {"credits_per_second": 6}
  },
  "fast_mode_multiplier": 0.55,
  "usd_per_credit": 0.01
}
```