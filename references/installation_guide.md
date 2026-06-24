# Grok Imagine Cinematic Studio v3.6.4 — Installation Guide

## Recommended: One-Command Installation

```bash
bash <(curl -sL https://raw.githubusercontent.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/main/scripts/cinematic_studio.sh) install
```

Legacy alias (same behavior):

```bash
bash <(curl -sL https://raw.githubusercontent.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/main/scripts/install_cinematic_studio.sh)
```

After running:
1. Refresh Skills page
2. Type: `Activate Grok Imagine Cinematic Studio v3.6.4`

## Updating

```bash
bash <(curl -sL https://raw.githubusercontent.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/main/scripts/cinematic_studio.sh) update
```

## Verification

```bash
./scripts/cinematic_studio.sh verify          # core skills (7)
./scripts/cinematic_studio.sh verify --all    # full manifest (30; install syncs any bundle gaps from GitHub)
```

Legacy wrapper:

```bash
./scripts/verify_cinematic_studio.sh
```

## Manual Method

1. Download the latest `.zip` from GitHub Releases
2. Extract it
3. Copy `.grok/skills/*` → `~/.grok/skills/`
4. Copy `references/agents/` and prompt files to your project folder

For full details, see the meta-skill or the main repo README.

