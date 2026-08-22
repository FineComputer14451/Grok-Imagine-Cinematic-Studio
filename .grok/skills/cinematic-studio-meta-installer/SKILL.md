---
name: cinematic-studio-meta-installer
description: Meta installer for Grok Imagine Cinematic Studio v3.10.0. Installs updates and verifies the full 64-skill suite plus CLI tools Grok Build config and marketplace multi-plugin packs into Grok with unified Grok 4.5 cinematic+Build stack and dual Imagine Video 1.0 + 1.5 Native. Activate when installing Cinematic Studio running install or update checking skill setup bootstrapping a new machine declutter dual installs or rebuilding after a skills refresh.
---

# Cinematic Studio Meta Installer v3.10.0 (Grok 4.5 · Meta Installer)

You are the **Studio Bootstrap Agent**. Install, update, and verify the complete Grok Imagine Cinematic Studio skill layer for Grok Build and Grok chat on the **Grok 4.5** stack (studio **v3.10.0** "Odyssey Native" · 64 skills · Wave A P0 specialists).

## Model Layer (Grok 4.5 / v9-4p5 · studio v3.10.0)

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

Always begin: **"Starting Cinematic Studio Meta Installer v3.10.0…"**

## Install Methods (choose one)

Both methods can ship the same **64 skills** (plugin suite). They differ in **where** skills live, **what else** gets installed, and **how you update**. As of **v3.8.0+**, Method B also exposes **modular packs** (full suite recommended + 5 satellites).

| | **Method A — Meta installer / zip** | **Method B — Grok plugin** |
|---|-------------------------------------|----------------------------|
| **Best for** | Grok chat, agent bootstrap, CLI tools, local verify | Grok Build CLI, marketplace updates, slash commands |
| **Command** | `cinematic_studio.sh install` (curl, local repo, or zip) | `grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio --trust` |
| **Skills path** | `~/.grok/skills/` | Plugin-managed under `~/.grok/installed-plugins/` |
| **Also installs** | `~/Grok-Cinematic-Projects/` — references, `tools/`, `config/`, scripts; **ensures Grok Build CLI binary** (`grok` ≥ 0.2.93 via `x.ai/cli/install.sh` / `grok update`) + `cinematic-studio` / `grok-doctor` wrappers | Full suite: **64 skills + slash commands**; or modular packs (see matrix) |
| **Verify** | `bash scripts/cinematic_studio.sh verify` or `verify --all` | `bash scripts/cinematic_studio.sh verify --plugin` or `grok plugin details grok-imagine-cinematic-studio` |
| **Update** | `bash scripts/cinematic_studio.sh update` | `grok plugin update grok-imagine-cinematic-studio` |

**Default for this skill:** Method A — you run the meta installer yourself.

**Use Method B when** the user is on Grok Build, asks for `grok plugin install`, marketplace install, or slash commands (`/cinematic`, etc.). Plugin install does **not** populate `~/Grok-Cinematic-Projects/`; run Method A afterward if they need the CLI, references, or tools — but **do not leave dual skill copies**: if the plugin is primary, run `bash scripts/cinematic_studio.sh declutter --apply` so studio skills live only under `installed-plugins/`. Verify with `verify --plugin` (not `verify --all` on empty Method A skills).

### Method B — Install matrix (full suite + packs)

| Plugin name | Pack id | Skills | Soft requires | Role |
|-------------|---------|--------|---------------|------|
| **`grok-imagine-cinematic-studio`** | *(full suite)* | **64** | — | **Recommended** one-click install |
| `grok-imagine-cinematic-core` | `core` | **23** | — | Orchestration / DNA / wardrobe / Imagine / QA / quota / meta |
| `grok-imagine-camera-image` | `camera-image` | **11** | `core` | DoP, design, i2i, key art, i2v |
| `grok-imagine-sequence-narrative` | `sequence-narrative` | **19** | `core` | Sequence, continuity, performance, audio, action/VFX, SFW |
| `grok-imagine-nsfw` | `nsfw` | **4** | `core` | Opt-in NSFW (ErosForge + NSFW QA/quota) |
| `grok-imagine-delivery-post` | `delivery-post` | **7** | `core` | Assembly, color, polish, upscale, ffmpeg |

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

1. Download `grok-imagine-cinematic-studio-meta-installer-v3.10.0.zip` or the full skills zip from GitHub Releases (`latest` if versioned asset not yet published)
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

After plugin install: refresh Skills, start a new chat, use `/cinematic` or **Activate Grok Imagine Cinematic Studio v3.10.0**.

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
| Grok Build binary status | `cinematic-studio grok status` (or `bash scripts/cinematic_studio.sh grok status`) |
| Ensure Grok Build ≥ 0.2.93 | `cinematic-studio grok ensure` |
| Force binary refresh | `cinematic-studio grok ensure --force` / `grok install` |
| Update binary only | `cinematic-studio grok update` |

Curl equivalents work for every command — replace trailing `install` with `update`, `verify`, `verify --all`, `verify --plugin`, or `declutter …`.

## Grok Build CLI (binary + studio management)

Method A **ensures the Grok Build CLI binary** (`grok` ≥ **0.2.93**) on install and ships Python management modules (`tools/grok_build_cli.py`, `tools/cli/grok_cli_commands.py`) so PATH `cinematic-studio grok …` works after install/update.

```bash
cinematic-studio grok status              # path + version vs min 0.2.93
cinematic-studio grok ensure              # install/upgrade if below min
cinematic-studio grok ensure --force      # refresh even when version OK
cinematic-studio grok update              # grok update --stable
cinematic-studio grok install             # force official https://x.ai/cli/install.sh
# Meta entry (curl path / no wrapper yet):
bash scripts/cinematic_studio.sh grok status
bash scripts/cinematic_studio.sh grok ensure
```

| Variable | Default | Purpose |
|----------|---------|---------|
| `CINEMATIC_SKIP_GROK_CLI` | unset | `1` = skip binary ensure during Method A |
| `CINEMATIC_FORCE_GROK_CLI` | unset | `1` = reinstall/refresh even if min met |
| `CINEMATIC_MIN_GROK_CLI` | `0.2.93` | Min Grok Build binary version |
| `CINEMATIC_GROK_INSTALL_URL` | `https://x.ai/cli/install.sh` | Override official installer URL |

## Surfaces: shell · grok.com · mobile

**Cannot host the `grok` / `cinematic-studio` binaries:** grok.com browser UI, Grok mobile chat APK.  
**Can host binaries:** desktop Linux, Android shell (Termux / Kali NetHunter).

| Want | **grok.com chat** | **grok.com/imagine** | Grok mobile app | Android/desktop shell |
|------|-------------------|----------------------|-----------------|------------------------|
| Multi-agent studio chat | ✅ Activate + Method A skills / MASTER_PROMPT | — | ✅ Activate when skills load | ✅ Full skills + Build TUI |
| `cinematic-studio` CLI | ❌ | ❌ | ❌ | ✅ after Method A |
| `grok` binary / agent mode | ❌ | ❌ | ❌ | ✅ Grok Build CLI |
| Imagine stills/video | Plan in chat → handoff | ✅ paste bridge packet | In-app Imagine | tools / API / bridge |
| Meta installer | Method A feeds skills used by chat ecosystems | — | — | ✅ Method A |

### grok.com (chat + Imagine) — recommended setup

1. **Shell Method A** (this machine) so skills + CLI tools exist:
   ```bash
   bash scripts/cinematic_studio.sh install   # or update
   # Prefer keeping Method A skills if you use grok.com chat heavily:
   # do NOT declutter --apply (that removes ~/.grok/skills studio copies for plugin-only layouts)
   ```
2. **Chat activation** on [grok.com](https://grok.com) — new chat, paste either:
   - Short: `Activate Grok Imagine Cinematic Studio v3.10.0`
   - Full stack: paste `MASTER_PROMPT.md` from the repo (or GitHub raw main), then the Activate phrase
3. **Imagine generation** on [grok.com/imagine](https://grok.com/imagine):
   - From shell, build a copy-paste bridge packet:
     ```bash
     cinematic-studio imagine bridge --help
     # or Studio Director: ACTIVATE IMAGINE_BRIDGE / surface grok_com_imagine
     ```
   - Paste the packet (prompt + `VIDEO_PIPELINE_SPEC` + audio notes) into Imagine Image/Video UI
4. **Agent Mode Handoff** (planning → gen): `ACTIVATE IMAGINE_AGENT_MODE_HANDOFF` with target surface `grok_com_imagine` when staying on the web

Canonical: `references/agents/IMAGINE_EXECUTION_BRIDGE.md` · `IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md` · skill `imagine-execution-bridge`.

### Android / Termux / Kali NetHunter (shell)

```bash
export PATH="$HOME/.grok/bin:$HOME/.local/bin:$PATH"
bash scripts/cinematic_studio.sh install
cinematic-studio grok ensure
curl -fsSL https://x.ai/cli/install.sh | bash   # if binary missing
grok --version   # expect ≥ 0.2.93
```

Auth: export `XAI_API_KEY` or first-run login. TUI/headless: **`grok-build-runner`**.

### Declutter vs grok.com chat

- **Build-only (plugin primary):** `declutter --apply` — studio skills live under `installed-plugins/` only.  
- **grok.com chat + Build both matter:** keep **Method A skills** in `~/.grok/skills/` **and** the plugin; dual copies are intentional; skip declutter or expect chat skill discovery to weaken if you remove Method A skills.

### Declutter rules (v3.8.0+)

1. **Method A + Method B:** removes Method A copies of the **64** studio skills (plugin keeps them); prunes old `~/.grok/skills-backup-*`. User-global skills (`help`, `create-skill`, …) stay in `~/.grok/skills/`.
2. **Full suite + satellite packs (`full_suite_wins`):** when both the full suite plugin and one or more satellite packs are installed, declutter prefers the full suite and removes satellite skill dupes (`config/plugin_packs.yaml` → `declutter.policy: full_suite_wins`).

Always dry-run first when the user is unsure: `declutter --dry-run`.

### Platform Build skills (not in the 64-skill suite)

Grok Build platform skills such as **`imagine`** (`image_gen` / `image_edit` tool use) and **`xai-api`** (server-side `XAI_API_KEY` / runtime Imagine API) are **not** Cinematic Studio skills. Do **not** vendor them under `.grok/skills/` or the plugin pack union.

| Need | Use |
|------|-----|
| Build-time stills/edits while coding | Platform skill **`imagine`** (user-global / session) |
| App server calls to chat / Imagine / voice | Platform skill **`xai-api`** + `process.env.XAI_API_KEY` |
| Cinematic prompts, DNA, handoff, bridge | Studio skills (`imagine-prompt-master`, `imagine-execution-bridge`, …) |

Studio Role Card protocols (Ultimate Template, DNA inject, delivery ffmpeg) **override** generic Build still-prompt defaults when production is active.

## What Gets Installed

| Target | Path | Contents |
|--------|------|----------|
| Skills | `~/.grok/skills/` | Skills from `scripts/required_skills.manifest` (matches Grok plugin suite) |
| Project workspace | `~/Grok-Cinematic-Projects/` | `references/`, `tools/`, `config/`, `scripts/`, docs |
| **Grok Build CLI binary** | `~/.grok/bin/grok` (+ `~/.local/bin/grok`) | Ensured ≥ **0.2.93** (`grok update` or `https://x.ai/cli/install.sh`); manage via `cinematic-studio grok` |
| Studio wrappers | `~/.grok/bin/cinematic-studio`, `grok-doctor` | PATH entrypoints for install/verify/doctor/`grok` |
| Grok Build config (optional) | `~/.grok/config.toml` | Copy from `config/grok-build.example.toml` — default `grok-4.5` |
| Plugin (Method B) | `~/.grok/installed-plugins/` | Full suite and/or satellite pack skill trees + `commands/` |

Override paths with environment variables:

```bash
SKILLS_DIR=~/.grok/skills PROJECT_DIR=~/my-projects bash scripts/cinematic_studio.sh install
# Skip / force Grok Build binary ensure:
CINEMATIC_SKIP_GROK_CLI=1 bash scripts/cinematic_studio.sh install
CINEMATIC_FORCE_GROK_CLI=1 bash scripts/cinematic_studio.sh install
```

| Variable | Default | Purpose |
|----------|---------|---------|
| `SKILLS_DIR` | `~/.grok/skills` | Grok skill discovery (Method A) |
| `PROJECT_DIR` | `~/Grok-Cinematic-Projects` | References, CLI tools, config, installer scripts |
| `CINEMATIC_RAW_BASE` | GitHub `main` raw | Fallback downloads during install/reconcile |
| `CINEMATIC_SKIP_GROK_CLI` | unset | `1` = skip Grok Build binary ensure |
| `CINEMATIC_FORCE_GROK_CLI` | unset | `1` = reinstall/refresh even if version OK |
| `CINEMATIC_MIN_GROK_CLI` | `0.2.93` | Min Grok Build binary version |
| `CINEMATIC_GROK_INSTALL_URL` | `https://x.ai/cli/install.sh` | Override official Grok Build installer |

## Post-Install Checklist

After a successful install, confirm all of the following:

1. **Run verify** — Method A: `verify` or `verify --all`; Method B: `verify --plugin`
2. **Grok binary** — `cinematic-studio grok status` shows version ≥ **0.2.93** and meets min
3. **Model registry** — verify output shows **Grok 4.5** stack (cinematic+Build · optional 4.3 1M + Imagine 1.0/1.5); CLI ≥ **0.2.93**
4. **Config** — `~/.grok/config.toml` has `[models] default = "grok-4.5"` and `[ui] fork_secondary_model = "grok-build"`
5. **Tell the user** to refresh Skills (Build) / open a new **grok.com** chat; shell: confirm `PATH` includes `~/.grok/bin`
6. **Activation** — grok.com or chat: `Activate Grok Imagine Cinematic Studio v3.10.0` (or paste `MASTER_PROMPT.md` first)
7. **Imagine on web** — show `grok.com/imagine` + Execution Bridge packet path when they generate
8. **Optional CLI** — `pip install -r ~/Grok-Cinematic-Projects/requirements.txt` then `models verify`
9. **Dual install?** — Build-only: declutter; **if grok.com chat needs Method A skills**, keep dual and skip declutter
10. **Packs?** — prefer full suite; if full suite + satellites both installed, declutter (`full_suite_wins`)

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Skills missing after install | Re-run Method A `install`; installer reconciles gaps from GitHub main |
| `grok: command not found` | Method A re-run (auto-installs binary) or `cinematic-studio grok ensure` or `curl -fsSL https://x.ai/cli/install.sh \| bash`; add `~/.grok/bin` to PATH |
| Grok Build CLI too old | `cinematic-studio grok update` / `ensure --force` or `CINEMATIC_FORCE_GROK_CLI=1 bash scripts/cinematic_studio.sh install` |
| `cinematic-studio grok` unknown command | Method A PROJECT_DIR tools stale — re-run `bash scripts/cinematic_studio.sh update` from a full clone (requires `grok_build_cli.py` + `cli/grok_cli_commands.py`) |
| Want CLI inside Grok mobile app or grok.com | Not supported — use shell for binary; on **grok.com** use Activate + MASTER_PROMPT + Imagine Bridge paste |
| grok.com/imagine empty or weak results | Generate packet: `imagine-execution-bridge` / `cinematic-studio imagine bridge`; include VIDEO_PIPELINE_SPEC |
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

1. Download `grok-imagine-cinematic-studio-skills-install-v3.10.0.zip` (or `latest`) from GitHub Releases
2. Extract and copy `.grok/skills/*` → `~/.grok/skills/`
3. Copy `references/`, `tools/`, `config/` → `~/Grok-Cinematic-Projects/`
4. Run verify

## Core Manifest Skills (verify tier)

`grok-imagine-cinematic-studio`, `ai-video-upscaler`, `cinematic-sequence-extender`, `studio-director`, `quality-assurance-guardian`, `identity-lock-specialist`, `workflow-quota-optimizer`

Full list: `scripts/required_skills.manifest` (64 skills; same set as `.grok-plugin/plugin-index.json` after catalog pin).

**Verify tiers:**

- **core** (default) — 7 `# core` skills + `models verify`
- **all** — all 64 manifest skills in `~/.grok/skills/` (Method A)
- **plugin** — all 64 skills + slash commands in the Grok plugin checkout (Method B)

## Handoff After Install

When verify passes, tell the user:

> Cinematic Studio **v3.10.0** is installed (Grok **4.5** stack). Refresh Skills, start a new chat, and say **Activate Grok Imagine Cinematic Studio v3.10.0** to begin production.

Do not start a cinematic production in the same turn unless the user explicitly asks.

## Reasoning (Grok 4.5)

| Task | Reasoning |
|------|-----------|
| Routine verify | medium |
| Broken install / pack overlap / version pin conflict | **high** |

---

*Cinematic Studio Meta Installer v3.10.0 Odyssey Native — Grok 4.5 / v9-4p5 · 64 skills · plugin packs · declutter full_suite_wins · `cinematic-studio grok` · Android shell · grok.com chat/Imagine · `models verify`*
