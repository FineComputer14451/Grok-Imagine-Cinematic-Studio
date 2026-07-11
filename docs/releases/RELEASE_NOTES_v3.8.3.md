# Release Notes — v3.8.3

**Date:** 2026-07-11  
**Theme:** Specialist order + color→polish handoff + still-compare polish

## Highlights

1. **Specialist-order checklist** — confirm DNA → Identity Lock → Reference Curator → Prompt Master → I2V before spend via `specialist_checklist` / `imagine agent-handoff --checklist` (GHR-09/10 under `--strict-handoff`).
2. **Color → polish handoff** — `sequence color-grade set/show`, structured `color_grade`, CG-01 readiness, `sequence polish --require-color-grade`, grade stamped into polish manifest.
3. **Still compare** — Pillow `get_flattened_data()` (no `getdata` deprecation warning).

## Install / update

```bash
grok plugin update grok-imagine-cinematic-studio
# or
bash scripts/cinematic_studio.sh update
```

## Verify

```bash
python tools/cinematic_studio_cli.py version
python tools/cinematic_studio_cli.py validate
bash scripts/verify_plugins.sh --release
```

## Activation

`Activate Grok Imagine Cinematic Studio v3.8.3`

## Quick usage

```bash
# Specialist order + strict handoff
python tools/cinematic_studio_cli.py imagine agent-handoff \
  --batch … --shot … --checklist dna,lock,curator,prompt,i2v --strict-handoff

# Color then polish
python tools/cinematic_studio_cli.py sequence color-grade set "Seq" \
  --notes "teal shadows, warm skin" --lut "SoftPrint" --status approved
python tools/cinematic_studio_cli.py sequence polish "Seq" --require-color-grade
```
