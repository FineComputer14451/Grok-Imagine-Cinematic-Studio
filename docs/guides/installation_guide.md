# Grok Imagine Cinematic Studio v3.7.1 — Installation Guide

Two supported install paths. Both ship the same **48 skills**; choose based on how you use Grok.

## Choose Your Install Method

| | **Method A — Meta installer / zip** | **Method B — Grok plugin** |
|---|-------------------------------------|----------------------------|
| **Best for** | Grok chat, agent sessions, CLI tools, scripted verify | Grok Build CLI, marketplace updates, slash commands |
| **Skills location** | `~/.grok/skills/` | `~/.grok/installed-plugins/` (plugin-managed) |
| **Also installs** | `~/Grok-Cinematic-Projects/` — references, `tools/`, `config/`, scripts | 48 skills + 11 slash commands (`/cinematic`, etc.) |
| **Verify** | `cinematic_studio.sh verify` / `verify --all` | `cinematic_studio.sh verify --plugin` or `grok plugin details grok-imagine-cinematic-studio` |
| **Update** | `cinematic_studio.sh update` | `grok plugin update grok-imagine-cinematic-studio` |

You can use **both**: plugin for Grok Build slash commands, Method A for CLI tools and Production Bible references.

**Skill parity:** `scripts/required_skills.manifest` lists the same 48 skills as `.grok-plugin/plugin-index.json`.

### Path overrides (Method A)

```bash
SKILLS_DIR=~/.grok/skills PROJECT_DIR=~/my-projects bash scripts/cinematic_studio.sh install
```

| Variable | Default | Purpose |
|----------|---------|---------|
| `SKILLS_DIR` | `~/.grok/skills` | Grok skill discovery (Method A) |
| `PROJECT_DIR` | `~/Grok-Cinematic-Projects` | References, CLI tools, config, installer scripts |
| `CINEMATIC_RAW_BASE` | GitHub `main` raw | Fallback downloads during install/reconcile |

---

## Method A — Meta Installer / Release Zip

### One-command install (recommended for chat + CLI)

```bash
bash <(curl -sL https://raw.githubusercontent.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/main/scripts/cinematic_studio.sh) install
```

Legacy alias (same behavior):

```bash
bash <(curl -sL https://raw.githubusercontent.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/main/scripts/install_cinematic_studio.sh)
```

### Local repository

```bash
./scripts/cinematic_studio.sh install
```

### Bootstrap / release zips

- **Meta bootstrap:** `grok-imagine-cinematic-studio-meta-installer-v3.7.1.zip` → extract, run `./bootstrap.sh`
- **Full skills bundle:** `grok-imagine-cinematic-studio-skills-install-v3.7.1.zip` → extract, run `bash scripts/cinematic_studio.sh install`

The installer reconciles missing manifest skills from GitHub `main` when needed.

### Updating (Method A)

```bash
bash <(curl -sL https://raw.githubusercontent.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/main/scripts/cinematic_studio.sh) update
```

Creates a timestamped backup at `~/.grok/skills-backup-*` before replacing skills.

### Verification (Method A)

```bash
./scripts/cinematic_studio.sh verify          # core skills (7) + model registry
./scripts/cinematic_studio.sh verify --all    # full manifest (48 skills)
```

Legacy wrapper: `./scripts/verify_cinematic_studio.sh`

### Manual zip (Method A)

1. Download the latest `.zip` from GitHub Releases (`grok-imagine-cinematic-studio-skills-install-v3.7.1.zip` or current release)
2. Extract it (release zips may use a nested root folder — the meta installer handles this automatically)
3. Copy `.grok/skills/*` → `~/.grok/skills/`
4. Copy `references/`, `tools/`, `config/`, and prompt files to `~/Grok-Cinematic-Projects/` (or your `PROJECT_DIR`)
5. Optional: `cp config/grok-build.example.toml ~/.grok/config.toml`

---

## Method B — Grok Plugin (Marketplace)

### Install

```bash
grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio --trust
```

Or via marketplace source:

```bash
grok plugin marketplace add FineComputer14451/Grok-Imagine-Cinematic-Studio
grok plugin install grok-imagine-cinematic-studio@finecomputer14451/grok-imagine-cinematic-studio --trust
```

### Updating (Method B)

```bash
grok plugin marketplace update
grok plugin update grok-imagine-cinematic-studio
```

### Verification (Method B)

```bash
bash scripts/cinematic_studio.sh verify --plugin
```

Checks all 48 plugin skills, 11 slash commands (`/cinematic`, `/dna`, etc.), and model registry when CLI tools are present in the plugin checkout.

Registry cross-check (optional):

```bash
grok plugin details grok-imagine-cinematic-studio
```

Refresh the Skills page in Grok and confirm slash commands are available.

**CLI gap:** Plugin install does not populate `~/Grok-Cinematic-Projects/`. Run Method A or clone the repo if you need the full `cinematic-studio` CLI (including `plugin catalog` commands), references, or local scripts. The core `cinematic-studio plugin catalog check` etc. work when the studio CLI is available.

---

## After Either Method

1. Refresh the Skills page in Grok
2. Start a new chat
3. Type: `Activate Grok Imagine Cinematic Studio v3.7.1` (or use `/cinematic` with Method B)

Optional Grok Build config:

```bash
cp ~/Grok-Cinematic-Projects/config/grok-build.example.toml ~/.grok/config.toml
```

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Skills missing after Method A | Re-run `install`; reconciles gaps from GitHub `main` |
| Nested zip from GitHub Releases | Handled automatically — do not manually flatten |
| `models verify` fails | Ensure `~/Grok-Cinematic-Projects/tools/` exists; re-run Method A |
| Old skills after update | Method A `update` backs up to `~/.grok/skills-backup-*` first |
| Plugin installed but no CLI | Run Method A or clone repo to `~/Grok-Cinematic-Projects/` |
| Curl blocked in sandbox | Use local repo: `bash scripts/cinematic_studio.sh install` |

## Verify tiers

- **core** (default) — 7 manifest skills marked `# core` in `required_skills.manifest`, plus `models verify`
- **all** — all 48 manifest skills in `~/.grok/skills/` (Method A)
- **plugin** — all 48 skills + 11 commands in the Grok plugin checkout (Method B; `verify --plugin`)

Core skills: `grok-imagine-cinematic-studio`, `ai-video-upscaler`, `cinematic-sequence-extender`, `studio-director`, `quality-assurance-guardian`, `identity-lock-specialist`, `workflow-quota-optimizer`

**Plugin catalog management (for contributors):**

After editing skills or commands:

```bash
cinematic-studio plugin catalog pin
```

Pre-publish gate:

```bash
cinematic-studio plugin catalog check --release
```

## See also

- Agent/bootstrap workflows: `.grok/skills/cinematic-studio-meta-installer/SKILL.md`
- Paths and release URLs: `.grok/skills/cinematic-studio-meta-installer/references/install_paths.md`
- Main overview: `README.md`