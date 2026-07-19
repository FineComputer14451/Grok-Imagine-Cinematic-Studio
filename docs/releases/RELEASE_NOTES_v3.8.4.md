# Release Notes — v3.8.4

**Date:** 2026-07-19  
**Theme:** Interactive CLI TUI + spend readiness (plate/motion) + install hardening

## Highlights

1. **`cinematic-studio ui`** — Textual home dashboard, allowlisted launcher, and production Cockpit (Setup / Quota / DNA / Sequence / Health). Non-spend scaffold only; async RunningScreen; confirm re-run hazard fixed.
2. **Plate lock + motion brief readiness** — soft by default; hard gates via `--strict-plate`, `--strict-motion`, and `--strict-handoff`. SFW/NSFW `plate` / `motion` set/show.
3. **Spend readiness facade** — unified preflight for generation paths; no silent motion-key aliasing.
4. **Install hygiene** — static dispatcher + Method A VERSION/wrapper pin; marketplace catalog re-pinned for this release.

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
# Plugin-primary machines:
bash scripts/cinematic_studio.sh verify --plugin
```

## Activation

`Activate Grok Imagine Cinematic Studio v3.8.4`

## Quick usage

```bash
# Interactive TUI
python tools/cinematic_studio_cli.py ui

# Plate + motion before video spend
python tools/cinematic_studio_cli.py sfw plate set <batch> --shot <id> --status locked
python tools/cinematic_studio_cli.py sfw motion set <batch> --shot <id> \
  --action "slow walk to window" --camera "gentle push-in" --emotion "calm focus"

# Strict handoff gate (plate + motion + checklist)
python tools/cinematic_studio_cli.py imagine agent-handoff \
  --batch … --shot … --strict-handoff
```
