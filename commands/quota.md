---
description: Estimate production credits, assess budget risk, and get quota optimization recommendations for Imagine Video 1.5.
---

# Quota & Budget

Plan session spend with per-second Imagine Video 1.5 pricing, clip breakdown, and optimization recommendations.

## Preflight

1. **CLI available?**
   ```bash
   python tools/cinematic_studio_cli.py quota --help
   ```
2. **Parameters** — Parse "$ARGUMENTS" for optional flags:
   - `--duration <seconds>` (default 60)
   - `--complexity low|medium|high|extreme` (default medium)
   - `--fast-mode` for draft iteration pricing
   - `--tier supergrok_pro|supergrok_heavy|custom`
3. **Activate** `workflow-quota-optimizer` skill for deep planning on long sequences.

## Plan

1. Run production estimate for the parsed duration and complexity.
2. Show quota dashboard and budget risk level.
3. Present optimization recommendations (Fast mode, clip count, agent scope).
4. If sequence name appears in "$ARGUMENTS", also run sequence-level cost estimate.

## Commands

### Production estimate

```bash
python tools/cinematic_studio_cli.py quota estimate \
  --duration 60 --complexity medium --fast-mode
```

Adjust flags from "$ARGUMENTS" when provided.

### Quota dashboard

```bash
python tools/cinematic_studio_cli.py quota dashboard
```

### Set budget tier

```bash
python tools/cinematic_studio_cli.py quota budget --tier supergrok_pro
```

### Optimization recommendations

```bash
python tools/cinematic_studio_cli.py quota optimize --duration 90 --complexity high
```

### Sequence cost (when sequence name in "$ARGUMENTS")

```bash
python tools/cinematic_studio_cli.py quota sequence "Sequence Name"
```

## Verification

- Estimate returns `credits_low`/`credits_high`, `usd_low`/`usd_high`, and `clip_count`.
- Risk level is stated (low / medium / high / critical).
- At least one actionable optimization recommendation is shown when spend is elevated.

## Summary

```
## Result
- **Action**: Quota estimate
- **Status**: success
- **Duration**: <seconds>s
- **Credits**: <low>–<high>
- **USD**: $<low>–$<high>
- **Risk**: <level>
```

## Next Steps

- Enable Fast mode for iteration, then quality pass on hero shots only.
- Run `/cinematic` to begin production within budget.
- For NSFW batches on Heavy, activate `nsfw-quota-orchestrator` explicitly.