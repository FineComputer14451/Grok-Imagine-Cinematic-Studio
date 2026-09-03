# Release Notes — v3.11.2

**Date:** 2026-09-03  
**Codename:** Imagine Image Quality retirement

## Highlights

xAI retires **`grok-imagine-image-quality`** on **2026-11-02** ([migration guide](https://docs.x.ai/developers/migration/imagine-image-quality-nov-2)). After that date the slug still resolves, but the API serves **`grok-imagine-image-2.0` with `quality: "low"`**.

Grok Imagine Cinematic Studio **v3.11.2** switches spend **now**, so operators choose the quality they pay for instead of waiting for the silent redirect.

| Area | Pin |
|------|-----|
| Studio / packaging | **3.11.2** |
| Cinematic / Build / CLI agent | `grok-4.6` (unchanged) |
| Imagine Image draft | `grok-imagine-image` (1.0, unchanged) |
| Imagine Image hero | `grok-imagine-image-2.0` + `quality` low \| medium \| auto |
| Quality slug | Deprecated; wire rewrite → 2.0 `quality=low` |

## Operator behavior

```bash
# Draft stills — still Image 1.0, no quality param
cinematic-studio imagine submit image -p "…" --dry-run

# Hero plates — pin 2.0 + medium (do not use the quality slug)
cinematic-studio imagine submit image -p "…" --model grok-imagine-image-2.0 --quality medium --dry-run

# Legacy --model quality / pro — warning + 2.0 quality=low
cinematic-studio imagine submit image -p "…" --model quality --dry-run
```

- Image 2.0 edits accept up to **five** source images.
- Aspect presets add **`21:9`** and **`5:2`** (sequence default remains 16:9).
- Quota estimates for the quality slug match 2.0 low ($0.04), not the old $0.05 list.
- `cinematic-studio doctor --quick` WARNs if project `model_stack.imagine_image` is still locked to the quality slug.

## Upgrade

```bash
grok plugin update grok-imagine-cinematic-studio
# or
bash scripts/cinematic_studio.sh update

cinematic-studio models verify
cinematic-studio doctor --quick
```

Activation: **`Activate Grok Imagine Cinematic Studio v3.11.2`**

## Compatibility

- `VERSION` / `STUDIO_COMPATIBILITY_VERSION`: **3.11.2**
- Handoff `PROTOCOL_OK` includes **3.11.2** (prior 3.7.1–3.11.1 packets still accepted)
- Registry schema **1.6** (`resolve_image_request`, retirement metadata)
- Builds on **v3.11.1** AUP gates + **v3.11.0** Grok 4.6 stack lock
