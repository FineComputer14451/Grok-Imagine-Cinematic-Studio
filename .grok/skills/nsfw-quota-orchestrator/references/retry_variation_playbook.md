# Retry & Variation Playbook

Smart recovery when NSFW QA scores fall below tier thresholds.

---

## Thresholds

| Tier | Min Pass Score |
|------|----------------|
| hero, consistency_anchor | 8.0 |
| key_explicit, support, filler | 7.0 |

---

## Failure → Strategy Matrix

| Failure Key | Max Retries | First Actions |
|-------------|-------------|---------------|
| `identity_drift` | 2 | Tighten DNA inject → regen anchor → i2v from still |
| `physics_failure` | 2 | One motion beat → 6–8s clip → Fast draft |
| `emotional_flat` | 1 | Micro-expression at t=2s, t=5s → warm rim light |
| `explicit_uncanny` | 2 | Suggestive framing → still → subtle i2v |
| `audio_sync_fail` | 1 | Shorten dialogue → SFX-only → split clip |
| `quota_pressure` | 0 | Defer non-hero; resume next session |

---

## Variation Techniques (Apply on Every Retry)

1. **Seed variation** — adjust lighting ratio ±15%, camera height ±10cm
2. **Prompt narrowing** — one body focus, one emotion, one motion beat
3. **Mode promotion** — failed video_prompt → image_prompt → i2v on pass
4. **State injection** — carry `post_scene_state` from ErosForge into next prompt
5. **Cost cap** — stop after max_retries; defer rather than burn quota

---

## When NOT to Retry

- Pass rate for session already <40%
- Daily cap >85% used
- Same failure reason 2× in a row on same shot → defer to next day
- Filler tier failure → skip entirely

---

## CLI

```bash
python tools/cinematic_studio_cli.py nsfw retry shot_key_002 --reason identity_drift --score 5.5 --attempts 1
```