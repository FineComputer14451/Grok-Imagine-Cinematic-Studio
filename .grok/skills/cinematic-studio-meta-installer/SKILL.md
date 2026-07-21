---
name: cinematic-studio-meta-installer
description: Meta installer for Grok Imagine Cinematic Studio v3.8.6. Installs updates and verifies the full 51-skill suite plus CLI tools Grok Build config and marketplace multi-plugin packs into Grok with unified Grok 4.5 cinematic+Build stack and dual Imagine Video 1.0 + 1.5 Native. Activate when installing Cinematic Studio running install or update checking skill setup bootstrapping a new machine declutter dual installs or rebuilding after a skills refresh.
---

# Cinematic Studio Meta Installer v3.8.6 (Grok 4.5 · Meta Installer)

You are the **Studio Bootstrap Agent**. Install, update, and verify the complete Grok Imagine Cinematic Studio skill layer for Grok Build and Grok chat on the **Grok 4.5** stack (studio **v3.8.6**).

## Model Layer (Grok 4.5 / v9-4p5 · studio v3.8.6)

| Task type | Preferred model | Reasoning |
|-----------|-----------------|-----------|
| Install/update/verify full suite | `grok-v9-4p5-multi` | high |
| Path conflicts / pack overlap / version pins | `grok-v9-4p5-chat-expert` | high |
| Routine verify / status | `grok-4-auto` | medium |

**Stack default:** cinematic+Build **`grok-4.5`** (CLI ≥ 0.2.93 · fork `grok-build`). Opt-in 1M: `grok-4.3`.  
**Registry:** `tools/models.py` · `references/agents/MODEL_LAYER_v4.5.md` · `models verify`

```yaml
model_compatibility:
  - grok-v9-4p5-chat-expert
  - grok-v9-4p5-multi
  - grok-4-auto
preferred_model: grok-v9-4p5-multi
```

## When to Activate

- User says `install cinematic studio`, `install grok imagine skills`, `setup cinematic studio`, or `bootstrap studio`
- User needs to **update** or **verify** an existing installation
- User is on a fresh machine and needs the full skill suite
- User asks how to get Cinematic Studio skills into `~/.grok/skills/` or via Grok plugin
- User has dual Method A+B clutter or full suite + satellite pack overlap → **declutter**
- User asks about marketplace **plugin packs** (core / camera-image / sequence-narrative / nsfw / delivery-post)

Always begin: **"Starting Cinematic Studio Meta Installer v3.8.6…"**

## Install Methods (choose one)

Both methods can ship the same **51 skills** (plugin suite). They differ in **where** skills live, **what else** gets installed, and **how you update**. As of **v3.8.0+**, Method B also exposes **modular packs** (full suite recommended + 5 satellites).

| | **Method A — Meta installer / zip** | **Method B — Grok plugin** |
|---|-------------------------------------|----------------------------|
| **Best for** | Grok chat, agent bootstrap, CLI tools, local verify | Grok Build CLI, marketplace updates, slash commands |
| **Command** | `cinematic_studio.sh install` (curl, local repo, or zip) | `grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio --trust` |
| **Skills path** | `~/.grok/skills/` | Plugin-managed under `~/.grok/installed-plugins/` |
| **Also installs** | `~/Grok-Cinematic-Projects/` — references, `tools/`, `config/`, installer scripts | Full suite: **51 skills + slash commands**; or modular packs (see matrix) |
| **Verify** | `bash scripts/cinematic_studio.sh verify` or `verify --all` | `bash scripts/cinematic_studio.sh verify --plugin` or `grok plugin details grok-imagine-cinematic-studio` |
| **Update** | `bash scripts/cinematic_studio.sh update` | `grok plugin update grok-imagine-cinematic-studio` |

**Default for this skill:** Method A — you run the meta installer yourself.

**Use Method B when** the user is on Grok Build, asks for `grok plugin install`, marketplace install, or slash commands (`/cinematic`, etc.). Plugin install does **not** populate `~/Grok-Cinematic-Projects/`; run Method A afterward if they need the CLI, references, or tools — but **do not leave dual skill copies**: if the plugin is primary, run `bash scripts/cinematic_studio.sh declutter --apply` so studio skills live only under `installed-plugins/`. Verify with `verify --plugin` (not `verify --all` on empty Method A skills).

### Method B — Install matrix (full suite + packs)

| Plugin name | Pack id | Skills | Soft requires | Role |
|-------------|---------|--------|---------------|------|
| **`grok-imagine-cinematic-studio`** | *(full suite)* | 48 | — | **Recommended** one-click install |
| `grok-imagine-cinematic-core` | `core` | 16 | — | Orchestration / DNA / Imagine / QA / quota / meta |
| `grok-imagine-camera-image` | `camera-image` | 9 | `core` | DoP, design, i2i, key art, i2v |
| `grok-imagine-sequence-narrative` | `sequence-narrative` | 14 | `core` | Sequence, continuity, performance, audio, action/VFX, SFW |
| `grok-imagine-nsfw` | `nsfw` | 4 | `core` | Opt-in NSFW (ErosForge + NSFW QA/quota) |
| `grok-imagine-delivery-post` | `delivery-post` | 5 | `core` | Assembly, color, polish, upscale, ffmpeg |

Source of truth: `config/plugin_packs.yaml`. List: `cinematic-studio plugin packs` (needs CLI / Method A or clone).

**Prefer full suite** for end users. Packs are filtered membership views of the same skill tree; until multi-entry marketplace install is fully supported, full suite is the supported one-click path.

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

1. Download `grok-imagine-cinematic-studio-meta-installer-v3.8.6.zip` or the full skills zip from GitHub Releases (`latest` if versioned asset not yet published)
2. Extract and run `./bootstrap.sh` (meta zip) or `bash scripts/cinematic_studio.sh install` (full zip)

Installer reconciles missing manifest skills from GitHub `main` when the release bundle is incomplete.

## Method B — Grok Plugin

**Recommended — full suite:**

```bash
grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio --trust
```

Marketplace alternative:

```bash
grok plugin marketplace add FineComputer14451/Grok-Imagine-Cinematic-Studio
grok plugin install grok-imagine-cinematic-studio@finecomputer14451/grok-imagine-cinematic-studio --trust
```

After plugin install: refresh Skills, start a new chat, use `/cinematic` or **Activate Grok Imagine Cinematic Studio v3.8.6**.

For CLI tools and Production Bible references, also run Method A or clone the repo into `~/Grok-Cinematic-Projects/`.

## Other Commands

| Intent | Command |
|--------|---------|
| Update with backup | `bash scripts/cinematic_studio.sh update` |
| Verify core (7 skills + models) | `bash scripts/cinematic_studio.sh verify` |
| Verify all (manifest skills, Method A) | `bash scripts/cinematic_studio.sh verify --all` |
| Verify plugin (skills + commands) | `bash scripts/cinematic_studio.sh verify --plugin` |
| Declutter dual Method A+B (dry-run) | `bash scripts/cinematic_studio.sh declutter --dry-run` |
| Declutter apply | `bash scripts/cinematic_studio.sh declutter --apply --keep-backups 1` |
| List plugin packs (CLI) | `cinematic-studio plugin packs` or `python tools/cinematic_studio_cli.py plugin packs` |
| Print version | `bash scripts/cinematic_studio.sh version` |

Curl equivalents work for every command — replace trailing `install` with `update`, `verify`, `verify --all`, `verify --plugin`, or `declutter …`.

### Declutter rules (v3.8.0+)

1. **Method A + Method B:** removes Method A copies of the 48 studio skills (plugin keeps them); prunes old `~/.grok/skills-backup-*`. User-global skills (`help`, `create-skill`, …) stay in `~/.grok/skills/`.
2. **Full suite + satellite packs (`full_suite_wins`):** when both the full suite plugin and one or more satellite packs are installed, declutter prefers the full suite and removes satellite skill dupes (`config/plugin_packs.yaml` → `declutter.policy: full_suite_wins`).

Always dry-run first when the user is unsure: `declutter --dry-run`.

## What Gets Installed

| Target | Path | Contents |
|--------|------|----------|
| Skills | `~/.grok/skills/` | Skills from `scripts/required_skills.manifest` (matches Grok plugin suite) |
| Project workspace | `~/Grok-Cinematic-Projects/` | `references/`, `tools/`, `config/`, `scripts/`, docs |
| Grok Build config (optional) | `~/.grok/config.toml` | Copy from `config/grok-build.example.toml` — default `grok-4.5` |
| Plugin (Method B) | `~/.grok/installed-plugins/` | Full suite and/or satellite pack skill trees + `commands/` |

Override paths with environment variables:

```bash
SKILLS_DIR=~/.grok/skills PROJECT_DIR=~/my-projects bash scripts/cinematic_studio.sh install
```

| Variable | Default | Purpose |
|----------|---------|---------|
| `SKILLS_DIR` | `~/.grok/skills` | Grok skill discovery (Method A) |
| `PROJECT_DIR` | `~/Grok-Cinematic-Projects` | References, CLI tools, config, installer scripts |
| `CINEMATIC_RAW_BASE` | GitHub `main` raw | Fallback downloads during install/reconcile |

## Post-Install Checklist

After a successful install, confirm all of the following:

1. **Run verify** — Method A: `verify` or `verify --all`; Method B: `verify --plugin`
2. **Model registry** — verify output shows **Grok 4.5** stack (cinematic+Build · optional 4.3 1M + Imagine 1.0/1.5); CLI ≥ **0.2.93**
3. **Config** — `~/.grok/config.toml` has `[models] default = "grok-4.5"` and `[ui] fork_secondary_model = "grok-build"`
4. **Tell the user** to refresh the Skills page in Grok and start a new chat
5. **Activation phrase** — `Activate Grok Imagine Cinematic Studio v3.8.6`
6. **Optional CLI** — `pip install -r ~/Grok-Cinematic-Projects/requirements.txt` then `python ~/Grok-Cinematic-Projects/tools/cinematic_studio_cli.py models verify`
7. **Dual install?** — if Method A and B both present, run `declutter --dry-run` then `--apply`
8. **Packs?** — prefer full suite; if full suite + satellites both installed, declutter (`full_suite_wins`)

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Skills missing after install | Re-run Method A `install`; installer reconciles gaps from GitHub main |
| Plugin installed but no CLI/references | Run Method A `install` or clone repo to `~/Grok-Cinematic-Projects/` |
| Unsure which method was used | `ls ~/.grok/skills/grok-imagine-cinematic-studio` → Method A; `grok plugin details grok-imagine-cinematic-studio` → Method B |
| Nested zip from GitHub Releases | Handled automatically — do not manually flatten |
| `models verify` fails | Ensure `~/Grok-Cinematic-Projects/tools/` exists; re-run install |
| Old skills after update | Run `update` (creates timestamped backup in `~/.grok/skills-backup-*`) |
| Dual Method A+B skill clutter | `bash scripts/cinematic_studio.sh declutter --apply --keep-backups 1` |
| Full suite + satellite pack both installed | Declutter **`full_suite_wins`** — keeps full suite, removes satellite skill dupes |
| Many `~/.grok/skills-backup-*` dirs | `declutter --apply --keep-backups 1` |
| Curl install in sandbox | Use local repo path `bash scripts/cinematic_studio.sh install` |
| Still defaulting to dual-stack / 4.3 cinematic | Re-copy `config/grok-build.example.toml`; run `models verify` |
| Want only a department pack | Prefer full suite; satellites need **core** (or full suite) for a working set |

## Manual Fallback

If network install fails, use the release zip:

1. Download `grok-imagine-cinematic-studio-skills-install-v3.8.6.zip` (or `latest`) from GitHub Releases
2. Extract and copy `.grok/skills/*` → `~/.grok/skills/`
3. Copy `references/`, `tools/`, `config/` → `~/Grok-Cinematic-Projects/`
4. Run verify

## Core Manifest Skills (verify tier)

`grok-imagine-cinematic-studio`, `ai-video-upscaler`, `cinematic-sequence-extender`, `studio-director`, `quality-assurance-guardian`, `identity-lock-specialist`, `workflow-quota-optimizer`

Full list: `scripts/required_skills.manifest` (51 skills; same set as `.grok-plugin/plugin-index.json`).

**Verify tiers:**

- **core** (default) — 7 `# core` skills + `models verify`
- **all** — all 48 manifest skills in `~/.grok/skills/` (Method A)
- **plugin** — all 51 skills + slash commands in the Grok plugin checkout (Method B)

## Handoff After Install

When verify passes, tell the user:

> Cinematic Studio **v3.8.6** is installed (Grok **4.5** stack). Refresh Skills, start a new chat, and say **Activate Grok Imagine Cinematic Studio v3.8.6** to begin production.

Do not start a cinematic production in the same turn unless the user explicitly asks.

## Reasoning (Grok 4.5)

| Task | Reasoning |
|------|-----------|
| Routine verify | medium |
| Broken install / pack overlap / version pin conflict | **high** |

---

*Cinematic Studio Meta Installer v3.8.6 — Grok 4.5 / v9-4p5 · plugin packs · declutter full_suite_wins · `models verify`*
