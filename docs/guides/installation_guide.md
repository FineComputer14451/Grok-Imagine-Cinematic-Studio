# Grok Imagine Cinematic Studio v3.8.4 — Installation Guide

Two supported install paths. Both can ship the same **48 skills**; choose based on how you use Grok. As of **v3.8.0**, Method B also exposes **modular packs** (full suite recommended + 5 satellites).

## Choose Your Install Method

| | **Method A — Meta installer / zip** | **Method B — Grok plugin** |
|---|-------------------------------------|----------------------------|
| **Best for** | Grok chat, agent sessions, CLI tools, scripted verify | Grok Build CLI, marketplace updates, slash commands |
| **Skills location** | `~/.grok/skills/` | `~/.grok/installed-plugins/` (plugin-managed) |
| **Also installs** | `~/Grok-Cinematic-Projects/` — references, `tools/`, `config/`, scripts | Full suite: 48 skills + 11 slash commands; or modular packs (see matrix) |
| **Verify** | `cinematic_studio.sh verify` / `verify --all` | `cinematic_studio.sh verify --plugin` or `grok plugin details grok-imagine-cinematic-studio` |
| **Update** | `cinematic_studio.sh update` | `grok plugin update grok-imagine-cinematic-studio` |

You can use **both**, but **do not dual-load the 48 studio skills**:

| Goal | Use |
|------|-----|
| Skills + slash commands in Grok Build | **Method B only** for skills |
| CLI tools, references, Production Bibles | Method A **or** a git clone (`~/Grok-Cinematic-Projects` / this repo) |
| Avoid skill triple-loading | Keep studio skills out of `~/.grok/skills/` when the plugin is installed |

If you already ran Method A **and** installed the plugin, declutter:

```bash
bash scripts/cinematic_studio.sh declutter --dry-run
bash scripts/cinematic_studio.sh declutter --apply --keep-backups 1
```

That removes Method A copies of the 48 studio skills (plugin keeps them) and prunes old `~/.grok/skills-backup-*` folders. User-global skills (`help`, `create-skill`, `docx`, …) stay in `~/.grok/skills/`.

**Pack overlap (`full_suite_wins`):** if both the **full suite** plugin and one or more **satellite packs** are installed, declutter prefers the full suite and removes satellite skill duplicates (`config/plugin_packs.yaml` → `declutter.policy: full_suite_wins`).

**Skill parity:** `scripts/required_skills.manifest` lists the same 48 skills as `.grok-plugin/plugin-index.json`.  
**Taxonomy (browse groups):** `references/SKILLS_TAXONOMY.md` · `cinematic-studio plugin list --grouped` · `cinematic-studio plugin packs`

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

- **Meta bootstrap:** `grok-imagine-cinematic-studio-meta-installer-v3.8.4.zip` → extract, run `./bootstrap.sh`
- **Full skills bundle:** `grok-imagine-cinematic-studio-skills-install-v3.8.4.zip` → extract, run `bash scripts/cinematic_studio.sh install`

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

1. Download the latest `.zip` from GitHub Releases (`grok-imagine-cinematic-studio-skills-install-v3.8.4.zip` or current release)
2. Extract it (release zips may use a nested root folder — the meta installer handles this automatically)
3. Copy `.grok/skills/*` → `~/.grok/skills/`
4. Copy `references/`, `tools/`, `config/`, and prompt files to `~/Grok-Cinematic-Projects/` (or your `PROJECT_DIR`)
5. Optional: `cp config/grok-build.example.toml ~/.grok/config.toml`

---

## Method B — Grok Plugin (Marketplace)

### Install matrix (full suite + modular packs)

| Plugin name | Pack id | Skills | Soft requires | Role |
|-------------|---------|--------|---------------|------|
| **`grok-imagine-cinematic-studio`** | *(full suite)* | 48 | — | **Recommended** one-click install |
| `grok-imagine-cinematic-core` | `core` | 16 | — | Orchestration / DNA / Imagine / QA / quota / meta |
| `grok-imagine-camera-image` | `camera-image` | 9 | `core` | DoP, design, i2i, key art, i2v |
| `grok-imagine-sequence-narrative` | `sequence-narrative` | 14 | `core` | Sequence, continuity, performance, audio, action/VFX, SFW |
| `grok-imagine-nsfw` | `nsfw` | 4 | `core` | Opt-in NSFW (ErosForge + NSFW QA/quota) |
| `grok-imagine-delivery-post` | `delivery-post` | 5 | `core` | Assembly, color, polish, upscale, ffmpeg |

Source of truth: `config/plugin_packs.yaml`. List from a checkout: `cinematic-studio plugin packs`.

### Install

**Recommended — full suite:**

```bash
grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio --trust
```

Or via marketplace source:

```bash
grok plugin marketplace add FineComputer14451/Grok-Imagine-Cinematic-Studio
grok plugin install grok-imagine-cinematic-studio@finecomputer14451/grok-imagine-cinematic-studio --trust
```

Satellite packs (when multi-entry marketplace install is supported) share the same git repo SHA; non-core packs expect **core** (or full suite) for a working department set.

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
cinematic-studio plugin packs
```

Refresh the Skills page in Grok and confirm slash commands are available.

**CLI gap:** Plugin install does not populate `~/Grok-Cinematic-Projects/`. Run Method A or clone the repo if you need the full `cinematic-studio` CLI (including `plugin catalog` / `plugin packs` commands), references, or local scripts. The core `cinematic-studio plugin catalog check` etc. work when the studio CLI is available.

### Pack install notes (spike / layout)

- **Packs are filtered views** of the same mono-repo skill tree (`.grok/skills/<name>/`) — not separate skill copies in git.
- **Marketplace lists 6 plugins** sharing one git SHA (full suite + 5 satellites in `.grok-plugin/marketplace.json`).
- **Satellite manifests** live under `.grok-plugin/packs/<id>/plugin.json` (ids: `core`, `camera-image`, `sequence-narrative`, `nsfw`, `delivery-post`).
- **Soft requires:** non-core packs declare `requires: [core]`; tooling treats this as advisory membership, not a hard install-time dependency graph unless Grok Build enforces it.
- **If Grok install only resolves root `plugin.json`:** install the **full suite** (current one-click path). Use packs as catalog membership for studio tooling (`plugin packs`, generators, declutter). When both full suite and a satellite are installed, run declutter — policy **`full_suite_wins`** drops satellite skill dupes.
- **Spike status:** skill paths in manifests are repo-root-relative (`.grok/skills/…`). Multi-plugin mono-repo install depends on Grok Build marketplace multi-entry support; until then, full suite remains the supported end-user path.

---

## After Either Method

1. Refresh the Skills page in Grok
2. Start a new chat
3. Type: `Activate Grok Imagine Cinematic Studio v3.8.4` (or use `/cinematic` with Method B)

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
| Skills appear twice / Grok skill list is huge | Dual Method A+B — run `declutter --apply` |
| Full suite + satellite pack both installed | Declutter **`full_suite_wins`** — keeps full suite, removes satellite skill dupes |
| Many `~/.grok/skills-backup-*` dirs | `declutter --apply --keep-backups 1` |
| Plugin installed but no CLI | Run Method A **without** needing skill copies, or clone repo to `~/Grok-Cinematic-Projects/` |
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