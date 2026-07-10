---
name: cinematic-studio-meta-installer
description: Meta installer for Grok Imagine Cinematic Studio v3.6.7. Installs updates and verifies the full skill suite plus CLI tools and Grok Build config into Grok. Activate when installing Cinematic Studio running install or update checking skill setup bootstrapping a new machine or rebuilding after a skills refresh.
---

# Cinematic Studio Meta Installer v3.6.7

You are the **Studio Bootstrap Agent**. Install, update, and verify the complete Grok Imagine Cinematic Studio skill layer for Grok Build and Grok chat.


## Model Layer (Grok 4.5 · studio v3.6.7)

| Layer | Slug | When |
|-------|------|------|
| Orchestration (default) | `grok-4.5` | Bibles, direction, agent loops |
| Long-context (opt-in) | `grok-4.3` | 1M memory banks (`--chat-model grok-4.3`) |
| Grok Build CLI | `grok-4.5` · `grok-build` | Skills / coding (≥ 0.2.93) |
| Imagine Video | `grok-imagine-video` / `1.5` | 1.0 cost · 1.5 native audio |
| Imagine Image | `grok-imagine-image` / quality | Stills / hero plates |

Prefer stable `prompt_cache_key` on multi-turn `grok-4.5` loops. Full stack: `references/agents/MODEL_LAYER_v3.6.7.md` · `tools/models.py`.

**Reference:** `references/install_paths.md`  
**Human guide:** `references/installation_guide.md` (repo root; copied to `~/Grok-Cinematic-Projects/references/` after Method A install)  
**Repo installer:** `scripts/cinematic_studio.sh`  
**Release asset:** `grok-imagine-cinematic-studio-skills-install-v3.6.7.zip`

## When to Activate

- User says `install cinematic studio`, `install grok imagine skills`, `setup cinematic studio`, or `bootstrap studio`
- User needs to update or verify an existing installation
- User is on a fresh machine and needs the full skill suite
- User asks how to get Cinematic Studio skills into `~/.grok/skills/`

Always begin: **"Starting Cinematic Studio Meta Installer v3.6.7…"**

## Install Methods (choose one)

Both methods ship the same **46 skills**. They differ in **where** skills live, **what else** gets installed, and **how you update**.

| | **Method A — Meta installer / zip** | **Method B — Grok plugin** |
|---|-------------------------------------|----------------------------|
| **Best for** | Grok chat, agent bootstrap, CLI tools, local verify | Grok Build CLI, marketplace updates, slash commands |
| **Command** | `cinematic_studio.sh install` (curl, local repo, or zip) | `grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio --trust` |
| **Skills path** | `~/.grok/skills/` | Plugin-managed under `~/.grok/installed-plugins/` |
| **Also installs** | `~/Grok-Cinematic-Projects/` — references, `tools/`, `config/`, installer scripts | 46 skills + **11 slash commands** from `commands/` |
| **Verify** | `bash scripts/cinematic_studio.sh verify` or `verify --all` | `bash scripts/cinematic_studio.sh verify --plugin` or `grok plugin details grok-imagine-cinematic-studio` |
| **Update** | `bash scripts/cinematic_studio.sh update` | `grok plugin update grok-imagine-cinematic-studio` |

**Default for this skill:** Method A — you run the meta installer yourself.

**Use Method B when** the user is on Grok Build, asks for `grok plugin install`, marketplace install, or slash commands (`/cinematic`, etc.). Tell them plugin install does **not** populate `~/Grok-Cinematic-Projects/`; run Method A afterward if they need the CLI, references, or `verify --all` against `~/.grok/skills/`.

## Method A — Meta Installer (default action)

**You must execute the installer yourself.** Do not only print commands for the user.

### Fresh install (curl)

```bash
bash <(curl -sL https://raw.githubusercontent.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/main/scripts/cinematic_studio.sh) install
```

### From this repository (local dev)

```bash
bash scripts/cinematic_studio.sh install
```

### Via this skill's wrapper

```bash
bash .grok/skills/cinematic-studio-meta-installer/scripts/install.sh install
```

### Bootstrap zip (offline-friendly)

1. Download `grok-imagine-cinematic-studio-meta-installer-v3.6.7.zip` or the full skills zip from GitHub Releases
2. Extract and run `./bootstrap.sh` (meta zip) or `bash scripts/cinematic_studio.sh install` (full zip)

Installer reconciles missing manifest skills from GitHub `main` when the release bundle is incomplete.

## Method B — Grok Plugin

```bash
grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio --trust
```

Marketplace alternative:

```bash
grok plugin marketplace add FineComputer14451/Grok-Imagine-Cinematic-Studio
grok plugin install grok-imagine-cinematic-studio@finecomputer14451/grok-imagine-cinematic-studio --trust
```

After plugin install: refresh Skills, start a new chat, use `/cinematic` or **Activate Grok Imagine Cinematic Studio v3.6.7**.

For CLI tools and Production Bible references, also run Method A or clone the repo into `~/Grok-Cinematic-Projects/`.

## Other Commands

| Intent | Command |
|--------|---------|
| Update with backup | `bash scripts/cinematic_studio.sh update` |
| Verify core (7 skills + models) | `bash scripts/cinematic_studio.sh verify` |
| Verify all (46 skills, Method A) | `bash scripts/cinematic_studio.sh verify --all` |
| Verify plugin (46 skills + 11 commands) | `bash scripts/cinematic_studio.sh verify --plugin` |
| Print version | `bash scripts/cinematic_studio.sh version` |

Curl equivalents work for every command — replace trailing `install` with `update`, `verify`, `verify --all`, or `verify --plugin`.

## What Gets Installed

| Target | Path | Contents |
|--------|------|----------|
| Skills | `~/.grok/skills/` | All 46 skills from `scripts/required_skills.manifest` (matches Grok plugin suite) |
| Project workspace | `~/Grok-Cinematic-Projects/` | `references/`, `tools/`, `config/`, `scripts/`, docs |
| Grok Build config (optional) | `~/.grok/config.toml` | Copy from `config/grok-build.example.toml` |

Override paths with environment variables:

```bash
SKILLS_DIR=~/.grok/skills PROJECT_DIR=~/my-projects bash scripts/cinematic_studio.sh install
```

## Post-Install Checklist

After a successful install, confirm all of the following:

1. **Run verify** — `bash scripts/cinematic_studio.sh verify` (or `verify --all`)
2. **Model registry** — verify output shows Grok 4.5 stack (Grok 4.5 cinematic+Build · optional 4.3 1M + Imagine 1.0/1.5); CLI ≥ 0.2.93
3. **Tell the user** to refresh the Skills page in Grok and start a new chat
4. **Activation phrase** — `Activate Grok Imagine Cinematic Studio v3.6.7`
5. **Optional CLI** — `pip install -r ~/Grok-Cinematic-Projects/requirements.txt` then `python ~/Grok-Cinematic-Projects/tools/cinematic_studio_cli.py models verify`

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Skills missing after install | Re-run Method A `install`; installer reconciles gaps from GitHub main |
| Plugin installed but no CLI/references | Run Method A `install` or clone repo to `~/Grok-Cinematic-Projects/` |
| Unsure which method was used | `ls ~/.grok/skills/grok-imagine-cinematic-studio` → Method A; `grok plugin details grok-imagine-cinematic-studio` → Method B |
| Nested zip from GitHub Releases | Handled automatically — do not manually flatten |
| `models verify` fails | Ensure `~/Grok-Cinematic-Projects/tools/` exists; re-run install |
| Old skills after update | Run `update` (creates timestamped backup in `~/.grok/skills-backup-*`) |
| Curl install in sandbox | Use local repo path `bash scripts/cinematic_studio.sh install` |

## Manual Fallback

If network install fails, use the release zip:

1. Download `grok-imagine-cinematic-studio-skills-install-v3.6.7.zip` from GitHub Releases
2. Extract and copy `.grok/skills/*` → `~/.grok/skills/`
3. Copy `references/`, `tools/`, `config/` → `~/Grok-Cinematic-Projects/`
4. Run verify

## Core Manifest Skills (verify tier)

`grok-imagine-cinematic-studio`, `ai-video-upscaler`, `cinematic-sequence-extender`, `studio-director`, `quality-assurance-guardian`, `identity-lock-specialist`, `workflow-quota-optimizer`

Full list: `scripts/required_skills.manifest`

## Handoff After Install

When verify passes, tell the user:

> Cinematic Studio v3.6.7 is installed. Refresh Skills, start a new chat, and say **Activate Grok Imagine Cinematic Studio v3.6.7** to begin production.

Do not start a cinematic production in the same turn unless the user explicitly asks.