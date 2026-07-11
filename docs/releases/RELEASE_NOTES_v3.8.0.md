# RELEASE NOTES — Grok Imagine Cinematic Studio v3.8.0

**Release Date:** July 11, 2026  
**Focus:** Plugin modularity — hybrid + additive marketplace packs

## Highlights

- **Full suite remains recommended** — `grok-imagine-cinematic-studio` (all 48 skills + 11 commands)
- **Five satellite packs** from `config/plugin_packs.yaml` (manifest-only filtered views, no skill file copies):
  - `grok-imagine-cinematic-core` (16 skills, 9 commands)
  - `grok-imagine-camera-image` (9 skills)
  - `grok-imagine-sequence-narrative` (14 skills)
  - `grok-imagine-nsfw` (4 skills, opt-in)
  - `grok-imagine-delivery-post` (5 skills)
- **`plugin packs` CLI** — list pack membership and soft `requires`
- **Pack-aware catalog** — six marketplace entries, shared pin SHA, per-plugin index
- **Declutter `full_suite_wins`** — when full suite + satellites coexist, remove satellite skill dupes

## Activation

```
Activate Grok Imagine Cinematic Studio v3.8.0
```

## Install

```bash
grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio --trust
# or marketplace install by plugin name (full suite recommended)
```

Pack membership source of truth: `config/plugin_packs.yaml`  
See also: `docs/guides/installation_guide.md` (install matrix + pack install notes)

## Verify

```bash
python tools/cinematic_studio_cli.py plugin packs
python tools/cinematic_studio_cli.py plugin catalog check --release
python tools/cinematic_studio_cli.py version
```
