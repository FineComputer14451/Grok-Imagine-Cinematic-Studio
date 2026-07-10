# Cinematic Studio Meta Installer — Paths Reference v3.6.7 (46-skill Grok plugin suite)

## Install Methods

Both paths deliver the same **46 skills** (`scripts/required_skills.manifest` ≡ `.grok-plugin/plugin-index.json`).

### Method A — Meta installer / release zip

Installs skills to `~/.grok/skills/` and project payload to `~/Grok-Cinematic-Projects/`.

```bash
# One-liner (curl)
bash <(curl -fsSL https://raw.githubusercontent.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/main/scripts/cinematic_studio.sh) install

# Local repo
bash scripts/cinematic_studio.sh install

# Bootstrap zip (meta-installer only)
unzip grok-imagine-cinematic-studio-meta-installer-v3.6.7.zip && ./bootstrap.sh
```

Update: `bash scripts/cinematic_studio.sh update` (timestamped backup under `~/.grok/skills-backup-*`).

Verify: `bash scripts/cinematic_studio.sh verify` (7 core + models) or `verify --all` (46 skills).

### Method B — Grok plugin (marketplace)

Installs the plugin-managed skill bundle plus **11 slash commands** from `commands/`.

```bash
# Direct from GitHub
grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio --trust

# Or via marketplace source (after marketplace add)
grok plugin install grok-imagine-cinematic-studio@finecomputer14451/grok-imagine-cinematic-studio --trust
```

Update: `grok plugin update grok-imagine-cinematic-studio`

Verify: `bash scripts/cinematic_studio.sh verify --plugin` (46 skills + 11 slash commands), or `grok plugin details grok-imagine-cinematic-studio` + refresh Skills in Grok.

**Note:** Plugin install does not create `~/Grok-Cinematic-Projects/`. Run Method A or clone the repo if you need `tools/cinematic_studio_cli.py`, references, or `cinematic_studio.sh verify`.

**Human-facing guide:** `references/installation_guide.md` (repo root)

## Canonical URLs

| Resource | URL |
|----------|-----|
| Meta installer script | `https://raw.githubusercontent.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/main/scripts/cinematic_studio.sh` |
| Shared library | `https://raw.githubusercontent.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/main/scripts/lib/cinematic_studio_common.sh` |
| Skill manifest | `https://raw.githubusercontent.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/main/scripts/required_skills.manifest` |
| Meta-installer zip (bootstrap) | `grok-imagine-cinematic-studio-meta-installer-v3.6.7.zip` — skill + scripts only; run `./bootstrap.sh` or `scripts/cinematic_studio.sh install` |
| Full skills zip (latest) | `https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/releases/latest/download/grok-imagine-cinematic-studio-skills-install-v3.6.7.zip` |
| Full skills zip (versioned) | `https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/releases/download/v3.6.7/grok-imagine-cinematic-studio-skills-install-v3.6.7.zip` |
| Build meta-installer | `bash scripts/build_meta_installer.sh` |
| Build full suite | `bash scripts/build_release_bundle.sh` |

## Default Install Paths

| Variable | Default | Purpose |
|----------|---------|---------|
| `SKILLS_DIR` | `~/.grok/skills` | Grok skill discovery |
| `PROJECT_DIR` | `~/Grok-Cinematic-Projects` | References, CLI tools, config, installer scripts |
| `CINEMATIC_RAW_BASE` | GitHub `main` raw | Fallback downloads |
| `CINEMATIC_RELEASE_BASE` | GitHub `releases/latest/download` | Release zip primary URL |

## PROJECT_DIR Layout After Install

```
~/Grok-Cinematic-Projects/
├── references/          # Role Cards, MODELS_v3.6.md, protocols
├── tools/               # cinematic_studio_cli.py + pipeline modules
├── tools/cli/           # models, bible, studio command modules
├── config/              # grok-build.example.toml
├── scripts/             # cinematic_studio.sh + lib (for local verify)
├── requirements.txt     # CLI dependencies
├── AGENTS.md
└── MASTER_PROMPT_v3.6.md
```

## Grok Build Config (Optional)

```bash
cp ~/Grok-Cinematic-Projects/config/grok-build.example.toml ~/.grok/config.toml
```

Sets `[models] default = "grok-4.5"` and `fork_secondary_model = "grok-build"` for cinematic+Build (recommend Grok Build CLI ≥ 0.2.93). Opt into `grok-4.3` only for 1M-context Bibles.

## Verify Tiers

- **core** — 7 manifest skills marked `# core` plus `models verify`
- **all** — full 46 skills from `required_skills.manifest` (Method A; checks `~/.grok/skills/`)
- **plugin** — full 46 skills + 11 slash commands under `~/.grok/installed-plugins/` (Method B; `verify --plugin`)
