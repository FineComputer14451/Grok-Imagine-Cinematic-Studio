# Release Notes — v3.11.3

**Date:** 2026-09-03  
**Codename:** Official Image 2.0 edit payload

## Highlights

Grok Imagine Cinematic Studio **v3.11.3** matches the official xAI Image 2.0 edit REST shape and keeps the API `model` field so operators can confirm the [Quality-slug redirect](https://docs.x.ai/developers/migration/imagine-image-quality-nov-2) after **2026-11-02**.

| Area | Pin |
|------|-----|
| Studio / packaging | **3.11.3** |
| Cinematic / Build / CLI agent | `grok-4.6` (unchanged) |
| Imagine Image draft | `grok-imagine-image` (1.0, unchanged) |
| Imagine Image hero | `grok-imagine-image-2.0` + `quality` low \| medium \| auto |
| Multi-edit REST | `images[]` (up to 5); single-ref stays `image` |
| Quality slug | Deprecated; wire rewrite → 2.0 `quality=low` |

## Operator behavior

```bash
# Hero plates
cinematic-studio imagine submit image -p "…" --model grok-imagine-image-2.0 --quality medium --dry-run

# Multi-ref edit (official images[])
cinematic-studio imagine submit image_edit -p "…" \
  --image-url https://example.com/primary.png \
  --extra-image-url https://example.com/a.png \
  --model grok-imagine-image-2.0 --quality medium --dry-run
```

- Live image responses keep xAI’s `model` and add `request_model` (the slug we sent).
- grok.com paste steps say **up to 5** refs on Image 2.0 edit.
- `cinematic-studio doctor --quick` WARNs if project `model_stack.imagine_image` is still the quality slug.

## Upgrade

```bash
grok plugin update grok-imagine-cinematic-studio
# or
bash scripts/cinematic_studio.sh update

cinematic-studio models verify
cinematic-studio doctor --quick
```

Activation: **`Activate Grok Imagine Cinematic Studio v3.11.3`**

## Compatibility

- `VERSION` / `STUDIO_COMPATIBILITY_VERSION`: **3.11.3**
- Handoff `PROTOCOL_OK` includes **3.11.3** (prior 3.7.1–3.11.2 packets still accepted)
- Builds on **v3.11.2** Quality retirement + **v3.11.1** AUP gates
