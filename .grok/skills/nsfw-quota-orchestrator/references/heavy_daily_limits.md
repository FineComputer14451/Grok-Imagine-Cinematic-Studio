# SuperGrok Heavy — Daily Limits & Session Pacing

Reference for NSFW batch planning under Heavy subscription.

---

## Tier Caps (Default)

| Metric | Value |
|--------|-------|
| Monthly credits | 50,000 |
| Daily soft cap | 2,500 |
| Recommended NSFW session | 800–1,000 credits (32–40% of daily) |
| Retry reserve | 15% of session budget |
| Max sessions per day | 2–3 (with cooldown between) |

---

## Session Pacing

| Daily Cap Used | Action |
|----------------|--------|
| <25% | Full batch — heroes + keys + support |
| 25–50% | Heroes + anchors + key_explicit only |
| 50–80% | Heroes + anchors only |
| >80% | Stop — generate daily report, resume tomorrow |

---

## Credit Quick Reference (xAI June 2026)

| Resource | Credits | USD |
|----------|---------|-----|
| Image standard | 2 | $0.02 |
| Image quality | 5 | $0.05 |
| Video 1.5 (10s) | 80–92 | $0.80–$0.92 |
| Image + i2v (10s) | 82–97 | $0.82–$0.97 |

---

## Integration Commands

```bash
python tools/cinematic_studio_cli.py quota budget --tier supergrok_heavy
python tools/cinematic_studio_cli.py quota dashboard
python tools/cinematic_studio_cli.py nsfw plan "Session Title" --budget 800
python tools/cinematic_studio_cli.py nsfw report
```