---
description: Model and quota intelligence — region routing, aspect presets, live quota sync, and two-pass quality scheduling.
---

# Model & Quota Intelligence

Tier 3 tooling for region-aware Imagine routing, aspect/orientation presets, estimated-vs-actual quota reconciliation, and fast→hero two-pass batch planning.

## Preflight

1. **CLI available?**
   ```bash
   python tools/cinematic_studio_cli.py imagine region --help
   python tools/cinematic_studio_cli.py quota sync --help
   python tools/cinematic_studio_cli.py sfw plan --help
   ```
2. **Activate** `workflow-quota-optimizer` for long sessions; `reference-asset-curator` when planning delivery formats.

## Region routing

Set primary region (env `IMAGINE_REGION` overrides project state):

```bash
python tools/cinematic_studio_cli.py imagine region
python tools/cinematic_studio_cli.py imagine region set us-east-1
python tools/cinematic_studio_cli.py imagine region list
```

Failover chain: primary → configured alternates on HTTP 403/429/5xx.

## Aspect presets

Inline shot specs support aspect prefixes:

```bash
# aspect:tier:description
python tools/cinematic_studio_cli.py sfw plan "Social Pack" \
  --shot "9:16:hero:Vertical cover" --shot "1:1:filler:Square hook"

# Sequence clip aspect
python tools/cinematic_studio_cli.py sequence add-clip "Act 1" \
  --prompt "..." --aspect 9:16
```

Presets: `16:9` (cinematic), `9:16` (vertical social), `1:1` (square). Handoff targets flow to Trailer Director and Key Art Designer.

## Quota sync

Track estimated vs actual spend and burn-rate risk:

```bash
python tools/cinematic_studio_cli.py quota sync
python tools/cinematic_studio_cli.py quota sync --entries
python tools/cinematic_studio_cli.py quota sync --json
python tools/cinematic_studio_cli.py quota dashboard
python tools/cinematic_studio_cli.py quota dashboard --json
python tools/cinematic_studio_cli.py quota reconcile
python tools/cinematic_studio_cli.py dashboard --compact
```

`quota sync` runs exclusive cascade (ledger → jobs with actuals → history `est:N`) and prints **cascade source**, **ledger alignment** (same check as Grok Doctor), burn-rate multiplier, and risk. Use `--entries` for per-row notes; `--json` for summary + `alignment` + entries.

Burn-rate risk (`low` / `medium` / `high` / `critical`) feeds `decide_generation_mode()` in SFW and NSFW orchestrators.

## Two-pass quality scheduler

Plan fast pass 1, promote to hero 1.5 after QA ≥7:

```bash
python tools/cinematic_studio_cli.py sfw plan "Hero Session" \
  --shot "hero:Opening" --two-pass

python tools/cinematic_studio_cli.py sfw record "Hero Session" shot_001 --score 8 --credits 6
python tools/cinematic_studio_cli.py sfw quality-pending "Hero Session"
python tools/cinematic_studio_cli.py sfw promote "Hero Session" shot_001
```

NSFW equivalent: `nsfw plan --two-pass`, `nsfw promote`, `nsfw quality-pending`.

## Verification

- `imagine region` shows active region and failover chain.
- `quota sync` reports cascade source, variance %, and burn-rate multiplier.
- `--two-pass` batches set `grok-imagine-video` on pass 1; promotion upgrades to `grok-imagine-video-1.5`.
- Dashboard quota panel shows reconciliation when entries exist.

## Summary

```
## Result
- **Action**: Model & quota intelligence
- **Region**: <active>
- **Burn risk**: <level>
- **Two-pass**: <enabled|disabled>
- **Aspects**: 16:9 | 9:16 | 1:1
```