# Cinematic Studio Meta Installer — Paths Reference v3.8.5 (Grok 4.5 · plugin suite + packs)

## Model stack (post-install)

| Layer | Slug |
|-------|------|
| Orchestration + Build default | `grok-4.5` |
| 1M opt-in | `grok-4.3` |
| Grok Build CLI | ≥ **0.2.93** · default `grok-4.5` · fork `grok-build` |
| Imagine Video | `grok-imagine-video` (1.0) / `1.5` native audio |
| Imagine Image | `grok-imagine-image` / quality |

Config: `config/grok-build.example.toml` → `~/.grok/config.toml`  
Verify: `python tools/cinematic_studio_cli.py models verify`  
Model Layer: `references/agents/MODEL_LAYER_v3.7.1.md`  
Studio release: **v3.8.5** (`VERSION`)

## Install Methods

Both paths can deliver the same skill suite (`scripts/required_skills.manifest` ≡ `.grok-plugin/plugin-index.json`, **51 skills**). Method B also lists **6 marketplace plugins** (full suite + 5 packs) from `config/plugin_packs.yaml`.

### Method A — Meta installer / release zip

Installs skills to `~/.grok/skills/` and project payload to `~/Grok-Cinematic-Projects/`.

```bash
# One-liner (curl)
bash <(curl -fsSL https://raw.githubusercontent.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/main/scripts/cinematic_studio.sh) install

# Local repo
bash scripts/cinematic_studio.sh install

# Bootstrap zip (meta-installer only)
unzip grok-imagine-cinematic-studio-meta-installer-v3.8.5.zip && ./bootstrap.sh
```

Update: `bash scripts/cinematic_studio.sh update` (timestamped backup under `~/.grok/skills-backup-*`).

Verify: `bash scripts/cinematic_studio.sh verify` (7 core + models) or `verify --all` (full manifest).

### Method B — Grok plugin (marketplace)

Installs the plugin-managed skill bundle plus slash commands from `commands/`. Prefer **full suite**.

```bash
# Direct from GitHub (recommended full suite)
grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio --trust

# Or via marketplace source (after marketplace add)
grok plugin install grok-imagine-cinematic-studio@finecomputer14451/grok-imagine-cinematic-studio --trust
```

| Plugin | Pack id | Role |
|--------|---------|------|
| `grok-imagine-cinematic-studio` | full suite (51) | Recommended |
| `grok-imagine-cinematic-core` | `core` | Orchestration base |
| `grok-imagine-camera-image` | `camera-image` | Camera / image |
| `grok-imagine-sequence-narrative` | `sequence-narrative` | Sequence / narrative |
| `grok-imagine-nsfw` | `nsfw` | Opt-in NSFW |
| `grok-imagine-delivery-post` | `delivery-post` | Delivery / polish |

Update: `grok plugin update grok-imagine-cinematic-studio`

Verify: `bash scripts/cinematic_studio.sh verify --plugin`, or `grok plugin details grok-imagine-cinematic-studio` + refresh Skills in Grok.

List packs (CLI required): `cinematic-studio plugin packs`

### Declutter

```bash
bash scripts/cinematic_studio.sh declutter --dry-run
bash scripts/cinematic_studio.sh declutter --apply --keep-backups 1
```

- Dual Method A+B → remove Method A studio skill copies (plugin wins)
- Full suite + satellite packs → policy **`full_suite_wins`** (drop satellite skill dupes)

## Release assets

| Asset | Notes |
|-------|--------|
| Meta-installer zip | `grok-imagine-cinematic-studio-meta-installer-v3.8.5.zip` — skill + scripts; run `./bootstrap.sh` |
| Full skills zip (latest) | `.../releases/latest/download/grok-imagine-cinematic-studio-skills-install-v3.8.5.zip` |
| Full skills zip (versioned) | `.../releases/download/v3.8.5/grok-imagine-cinematic-studio-skills-install-v3.8.5.zip` |

If a versioned zip is not published yet, use `latest` or install from a local clone of `main`.

## Paths after Method A

| Path | Purpose |
|------|---------|
| `~/.grok/skills/` | Installed skills |
| `~/.grok/config.toml` | Grok Build models (`grok-4.5` default) |
| `~/Grok-Cinematic-Projects/` | CLI tools, references, config templates |
| `~/Grok-Cinematic-Projects/tools/models.py` | Canonical model registry |

## Paths after Method B

| Path | Purpose |
|------|---------|
| `~/.grok/installed-plugins/` | Plugin-managed skills + commands |
| (optional) `~/Grok-Cinematic-Projects/` | Only if Method A or clone also run — CLI / references |

## Activation

```
Activate Grok Imagine Cinematic Studio v3.8.5
```

Or slash command `/cinematic` after plugin install.
