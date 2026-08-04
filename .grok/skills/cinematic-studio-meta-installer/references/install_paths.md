# Cinematic Studio Meta Installer — Paths Reference v3.9.1 (Grok 4.5 · 64-skill suite + packs)

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
Model Layer: `references/agents/MODEL_LAYER_v4.5.md`  
Studio release: **v3.9.1** (`VERSION`) · codename **Odyssey Native**

## Install Methods

Both paths can deliver the same skill suite (`scripts/required_skills.manifest` ≡ `.grok-plugin/plugin-index.json`, **64 skills** in-tree). Method B marketplace install resolves to the **catalog pin SHA** in `.grok-plugin/marketplace.json` — skill count matches the tree only **after** `cinematic-studio plugin catalog pin` (or equivalent) for this branch. Method B also lists **6 marketplace plugins** (full suite + 5 packs) from `config/plugin_packs.yaml`.

### Method A — Meta installer / release zip

Installs skills to `~/.grok/skills/` and project payload to `~/Grok-Cinematic-Projects/`.

```bash
# One-liner (curl)
bash <(curl -fsSL https://raw.githubusercontent.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/main/scripts/cinematic_studio.sh) install

# Local repo
bash scripts/cinematic_studio.sh install

# Via this skill's wrapper
bash .grok/skills/cinematic-studio-meta-installer/scripts/install.sh install

# Bootstrap zip (meta-installer only)
unzip grok-imagine-cinematic-studio-meta-installer-v3.9.1.zip && ./bootstrap.sh
```

Update: `bash scripts/cinematic_studio.sh update` (timestamped backup under `~/.grok/skills-backup-*`).

Verify: `bash scripts/cinematic_studio.sh verify` (7 core + models) or `verify --all` (full 64-skill manifest).

### Method B — Grok plugin (marketplace)

Installs the plugin-managed skill bundle plus slash commands from `commands/`. Prefer **full suite**.

```bash
# Direct from GitHub (recommended full suite)
grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio --trust

# Or via marketplace source (after marketplace add)
grok plugin install grok-imagine-cinematic-studio@finecomputer14451/grok-imagine-cinematic-studio --trust
```

| Plugin | Pack id | Skills | Role |
|--------|---------|--------|------|
| `grok-imagine-cinematic-studio` | full suite | **64** | Recommended one-click |
| `grok-imagine-cinematic-core` | `core` | **23** | Orchestration base |
| `grok-imagine-camera-image` | `camera-image` | **11** | Camera / image |
| `grok-imagine-sequence-narrative` | `sequence-narrative` | **19** | Sequence / narrative |
| `grok-imagine-nsfw` | `nsfw` | **4** | Opt-in NSFW |
| `grok-imagine-delivery-post` | `delivery-post` | **7** | Delivery / polish |

Source of truth: `config/plugin_packs.yaml` (packs partition the 64-skill tree: 23+11+19+4+7 = 64).

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

### Grok Build CLI binary

Method A ensures `grok` ≥ **0.2.93**:

```bash
cinematic-studio grok status
cinematic-studio grok ensure
cinematic-studio grok ensure --force
cinematic-studio grok update
```

| Variable | Default | Purpose |
|----------|---------|---------|
| `CINEMATIC_SKIP_GROK_CLI` | unset | `1` = skip binary ensure |
| `CINEMATIC_FORCE_GROK_CLI` | unset | `1` = reinstall/refresh even if OK |
| `CINEMATIC_MIN_GROK_CLI` | `0.2.93` | Min Grok Build binary version |
| `CINEMATIC_GROK_INSTALL_URL` | `https://x.ai/cli/install.sh` | Override installer URL |

## Release assets

| Asset | Notes |
|-------|--------|
| Meta-installer zip | `grok-imagine-cinematic-studio-meta-installer-v3.9.1.zip` — skill + scripts; run `./bootstrap.sh` |
| Full skills zip (latest) | `.../releases/latest/download/grok-imagine-cinematic-studio-skills-install-v3.9.1.zip` |
| Full skills zip (versioned) | `.../releases/download/v3.9.1/grok-imagine-cinematic-studio-skills-install-v3.9.1.zip` |

If a versioned zip is not published yet, use `latest` or install from a local clone of `main`.

## Paths after Method A

| Path | Purpose |
|------|---------|
| `~/.grok/skills/` | Installed skills (64 from manifest) |
| `~/.grok/bin/grok` | Grok Build CLI binary (≥ 0.2.93) |
| `~/.grok/bin/cinematic-studio` | Studio CLI wrapper |
| `~/.grok/bin/grok-doctor` | Doctor entrypoint |
| `~/.grok/config.toml` | Grok Build models (`grok-4.5` default) |
| `~/Grok-Cinematic-Projects/` | CLI tools, references, config templates |
| `~/Grok-Cinematic-Projects/tools/models.py` | Canonical model registry |

## Paths after Method B

| Path | Purpose |
|------|---------|
| `~/.grok/installed-plugins/` | Plugin-managed skills + commands |
| (optional) `~/Grok-Cinematic-Projects/` | Only if Method A or clone also run — CLI / references |

## Path overrides

```bash
SKILLS_DIR=~/.grok/skills PROJECT_DIR=~/my-projects bash scripts/cinematic_studio.sh install
CINEMATIC_SKIP_GROK_CLI=1 bash scripts/cinematic_studio.sh install
CINEMATIC_FORCE_GROK_CLI=1 bash scripts/cinematic_studio.sh install
```

| Variable | Default | Purpose |
|----------|---------|---------|
| `SKILLS_DIR` | `~/.grok/skills` | Grok skill discovery (Method A) |
| `PROJECT_DIR` | `~/Grok-Cinematic-Projects` | References, CLI tools, config, installer scripts |
| `CINEMATIC_RAW_BASE` | GitHub `main` raw | Fallback downloads during install/reconcile |

## Surfaces (where binaries work)

| Want | grok.com chat | grok.com/imagine | Grok mobile app | Android/desktop shell |
|------|---------------|------------------|-----------------|------------------------|
| Multi-agent studio chat | ✅ Activate + Method A skills | — | ✅ when skills load | ✅ Full skills + Build TUI |
| `cinematic-studio` CLI | ❌ | ❌ | ❌ | ✅ after Method A |
| `grok` binary | ❌ | ❌ | ❌ | ✅ Grok Build CLI |
| Imagine stills/video | Plan → handoff | ✅ paste bridge packet | In-app Imagine | tools / API / bridge |

## Activation

```
Activate Grok Imagine Cinematic Studio v3.9.1
```

Or slash command `/cinematic` after plugin install.

## Verify tiers

| Tier | Command | Checks |
|------|---------|--------|
| core | `verify` | 7 `# core` skills + `models verify` |
| all | `verify --all` | All **64** manifest skills (Method A) |
| plugin | `verify --plugin` | All **64** skills + slash commands (Method B) |

Core skills: `grok-imagine-cinematic-studio`, `ai-video-upscaler`, `cinematic-sequence-extender`, `studio-director`, `quality-assurance-guardian`, `identity-lock-specialist`, `workflow-quota-optimizer`

## Health check

```bash
grok-doctor
cinematic-studio doctor
bash scripts/grok_doctor.sh --quick
cinematic-studio grok status
bash .grok/skills/cinematic-studio-meta-installer/scripts/install.sh meta-version
```

---

*Paths reference v3.9.1 — Grok 4.5 / v9-4p5 · 64 skills · plugin packs · declutter full_suite_wins · Odyssey Native*
