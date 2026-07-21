# Release Notes — v3.8.6

**Date:** 2026-07-21  
**Theme:** Clean release pin — full dual-model suite complete

## Why 3.8.6?

v3.8.5 introduced the **v4.5 Dual-Model Wave**. After that tag, main received:

- Full **51-skill** `model_compatibility` coverage (not only the initial 16)
- Restored `tools/models.py` registry API for CLI / handoff
- Generation Tracker CLI (`cinematic-studio generation …`)
- Full meta-installer skill body restore
- Docs / activation / Method A+B cascade

**3.8.6** packages that completed state as a clean GitHub Release (fresh zips, no reliance on clobbered 3.8.5 assets).

## Highlights

| Item | Detail |
|------|--------|
| Studio | **v3.8.6** |
| Skills | **51** + 11 slash commands |
| Model layer | Grok 4.5 default · opt-in v9-4p5 multi/chat-expert/auto · dual Imagine 1.0/1.5 |
| Install | Method A zip / Method B plugin · packs + declutter `full_suite_wins` |

## Install / Update

```bash
# Plugin (recommended)
grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio --trust
# or update
grok plugin update grok-imagine-cinematic-studio

# Meta installer
bash <(curl -sL https://raw.githubusercontent.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/main/scripts/cinematic_studio.sh) update
```

### Release assets

- `grok-imagine-cinematic-studio-skills-install-v3.8.6.zip` — full 51 skills
- `grok-imagine-cinematic-studio-meta-installer-v3.8.6.zip` — bootstrap skill + installer

## Verify

```bash
python tools/cinematic_studio_cli.py version   # 3.8.6
python tools/cinematic_studio_cli.py models verify
bash scripts/cinematic_studio.sh verify --plugin
```

## Activation

```
Activate Grok Imagine Cinematic Studio v3.8.6
```

Or `/cinematic` after refreshing Skills.
