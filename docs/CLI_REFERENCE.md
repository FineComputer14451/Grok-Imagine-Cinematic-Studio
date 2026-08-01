# CLI Reference

## cinematic-studio (Grok Imagine Cinematic Studio v3.8.9)

Primary entry points:

| Entry | Role |
|-------|------|
| `cinematic-studio` | Installed wrapper (`~/.grok/bin`, often on `PATH` via `~/.local/bin`) |
| `python tools/cinematic_studio_cli.py` | Python CLI from a clone (no wrapper required) |
| `bash scripts/cinematic_studio.sh` | Meta installer: install / update / verify / declutter / doctor / **grok** |

**Wrapper env:**

| Variable | Purpose |
|----------|---------|
| `CINEMATIC_PROJECT_DIR` | Project root (default `$HOME/Grok-Cinematic-Projects`) |
| `CINEMATIC_CLI_PY` | Override path to `cinematic_studio_cli.py` |

**Runtime state dirs** (fixed in `tools/studio_paths.py` — do not relocate without updating that module):

`characters/` · `sequences/` · `sfw_batches/` · `nsfw_batches/` · `artifacts/` · `.cinematic_project_state.json` · `.quota_config.json`

---

## Global

```bash
cinematic-studio --help
cinematic-studio <command> --help
cinematic-studio version
cinematic-studio status
cinematic-studio stack [--json]
cinematic-studio dashboard [--json] [--compact] [--watch] [--interval 5]
```

Live help is authoritative when this doc lags. Framework: **Typer** + **Rich**; wiring in `tools/cinematic_studio_cli.py`, commands under `tools/cli/`.

---

## Grok Build CLI binary

Manage the official **Grok Build** binary (min **0.2.93**). Method A install also ensures this automatically. This is **not** the Studio Python CLI.

```bash
cinematic-studio grok status              # path + version vs min
cinematic-studio grok ensure              # install/upgrade if below min
cinematic-studio grok ensure --force      # refresh even when OK
cinematic-studio grok update              # grok update --stable
cinematic-studio grok install             # force https://x.ai/cli/install.sh

# Meta installer passthrough (no wrapper required):
bash scripts/cinematic_studio.sh grok status
bash scripts/cinematic_studio.sh grok ensure
```

On **Android shell** (Termux / Kali NetHunter): keep `~/.grok/bin` on `PATH`.  
**grok.com** and the **Grok mobile app cannot host this binary** — use shell for CLI; on the web use Activate / `MASTER_PROMPT.md` and **grok.com/imagine** bridge packets (`grok_com_imagine`).

Env: `CINEMATIC_SKIP_GROK_CLI`, `CINEMATIC_FORCE_GROK_CLI`, `CINEMATIC_MIN_GROK_CLI`, `CINEMATIC_GROK_INSTALL_URL`.

---

## Studio overview

```bash
cinematic-studio activate                 # Print activation phrase + stack
cinematic-studio list-agents              # Core + specialist roster by category
cinematic-studio list-role-cards
cinematic-studio show-role-card <name>
cinematic-studio doctor [--quick] [--json] [--strict]
cinematic-studio validate                 # Docs, skills, models, workspace paths
cinematic-studio report [-o production_report.pdf]
```

Agent roster in CLI: **25 core** + pipeline / Wave A / opt-in specialists (see `list-agents`). Skills suite size is tracked separately (plugin index / AGENTS.md).

---

## Production Bible & memory

```bash
cinematic-studio create-bible --wizard              # Guided stages (requires TTY)
cinematic-studio create-bible "Project Title" \
  --genre Cinematic \
  --chat-model grok-4.5 \
  --video-model grok-imagine-video \
  -o production_bible.json

cinematic-studio generate-prompt "story beat..." \
  --signature default \
  --chat-model grok-4.5 \
  --video-model grok-imagine-video

cinematic-studio cost-simulate --duration 60 --complexity medium

cinematic-studio memory add --name key --value "..."
cinematic-studio memory list
cinematic-studio memory load <name>
```

Chat model defaults to **`grok-4.5`**. Use `--chat-model grok-4.3` (or long-context aliases) only when 1M context is required.

---

## Character DNA

```bash
cinematic-studio dna init "Character Name" \
  [--core ...] [--facial ...] [--hair ...] [--clothing ...] \
  [--movement ...] [--emotion ...] [--motion ...] [--anchor ...] [-o path]

cinematic-studio dna save <profile-or-path>
cinematic-studio dna list
cinematic-studio dna show <slug> [--inject]
cinematic-studio dna handoff <slug>
cinematic-studio dna lock <slug>
cinematic-studio dna inject <slug>
```

Profiles live under `characters/{slug}/`. There is no `dna extract` subcommand — extraction is a **chat skill** (`character-dna-extractor`); CLI owns scaffold / lock / inject.

---

## Sequences (long-form)

```bash
cinematic-studio sequence init <name>
cinematic-studio sequence list
cinematic-studio sequence show <name>
cinematic-studio sequence add-clip <name> ...

# Extend / stitch path
cinematic-studio sequence handoff <name> ...
cinematic-studio sequence extend-prompt <name> ...   # not "sequence extend"
cinematic-studio sequence qa <name> ...
cinematic-studio sequence qa-assist <name> ...
cinematic-studio sequence run <name> ...             # API submit + poll + chain QA
cinematic-studio sequence estimate-cost <name>
cinematic-studio sequence health <name>

# Evidence loops
cinematic-studio sequence drift-score ...
cinematic-studio sequence seam-report ...
cinematic-studio sequence amv-check ...
cinematic-studio sequence continuity-diff ...

# Post
cinematic-studio sequence edl <name>
cinematic-studio sequence color-grade set|show ...
cinematic-studio sequence polish <name> [--scale 2] [--face-restore] [--dry-run]
cinematic-studio sequence deliver <name> ...

# Nested tools
cinematic-studio sequence memory show|sync ...
cinematic-studio sequence regen plan|apply|run ...     # after chain QA No-Go
cinematic-studio sequence temp set|show|gate ...
cinematic-studio sequence cast arbitrate|inject ...
cinematic-studio sequence artifact-lexicon list|pack|suggest ...
cinematic-studio sequence replan plan|apply ...
```

---

## Imagine jobs & handoff

```bash
cinematic-studio imagine verify
cinematic-studio imagine submit ...
cinematic-studio imagine status <job-id>
cinematic-studio imagine list
cinematic-studio imagine cancel <job-id>
cinematic-studio imagine region ...
cinematic-studio imagine workflow ...
cinematic-studio imagine artifact ...
cinematic-studio imagine artifacts
cinematic-studio imagine report

# Official Imagine Agent Mode Handoff (protocol v3.7.1 · studio v3.8.9)
cinematic-studio imagine agent-handoff \
  [--batch <slug> --shot <id>] \
  [--sequence <slug> --clip <id>] \
  --surface grok_build_tools \
  --format markdown|json|clipboard \
  [--strict-handoff] [--strict-wave-a] \
  [--checklist dna,lock,curator,prompt,i2v] \
  [-o path]

# Classic Surface C (grok.com/imagine paste)
cinematic-studio imagine bridge ...

# Packet validation (not root validate)
cinematic-studio handoff validate path/to/handoff.json \
  [--strict-handoff] [--strict-wave-a]
```

### Surfaces

| Code | Meaning |
|------|---------|
| `grok_build_tools` | In-session tools (preferred) |
| `grok_agent_acp` | ACP / agent sessions |
| `grok_com_imagine` | Web UI paste (Classic Bridge) |
| `xai_api` | Live API jobs |

---

## SFW / NSFW batches

SFW and NSFW share a similar command shape. NSFW tooling is for **explicit ErosForge-activated** pipelines only (chat policy still applies).

```bash
cinematic-studio sfw plan|list|next|decide|run|session|record|promote|quality-pending|retry
cinematic-studio nsfw plan|list|next|decide|run|session|record|promote|quality-pending|retry|report

# Plate + motion (both groups)
cinematic-studio sfw plate set <batch> <shot> --status draft|approved|locked ...
cinematic-studio sfw plate show ...
cinematic-studio sfw motion set <batch> <shot> ...
cinematic-studio sfw motion show ...

# Spend with hard gates
cinematic-studio sfw run ... --strict-plate --strict-motion [--strict-wave-a]
cinematic-studio nsfw run ... --strict-plate --strict-motion [--strict-wave-a]

# NSFW sensual extension (30–120s+)
cinematic-studio nsfw extend plan|chain|prompt|camera|qa|export ...
```

---

## Animatic

```bash
cinematic-studio animatic plan "Board title" [--beat ...] [--file beats.json] [-d 60]
cinematic-studio animatic list
cinematic-studio animatic show <name>
cinematic-studio animatic promote <name> --frame <id> [--tier hero]
```

---

## Quota & cost

```bash
cinematic-studio quota estimate --video-seconds 45 ...
cinematic-studio quota clip ...
cinematic-studio quota sequence <name>
cinematic-studio quota dashboard
cinematic-studio quota budget ...
cinematic-studio quota record ...
cinematic-studio quota optimize ...
cinematic-studio quota sync
cinematic-studio quota reconcile ...
```

---

## Models

```bash
cinematic-studio models list
cinematic-studio models stack
cinematic-studio models verify
```

Registry default: cinematic + Build **`grok-4.5`**; Imagine video **`grok-imagine-video`** (1.0 cost default); optional chat **`grok-4.3`** for 1M.

---

## Wave A packets

```bash
cinematic-studio wave-a plate-motion ...
cinematic-studio wave-a contact ...
cinematic-studio wave-a hmu ...
cinematic-studio wave-a dialogue ...
cinematic-studio wave-a score ...
cinematic-studio wave-a title ...
cinematic-studio wave-a crop ...
cinematic-studio wave-a briefs ...
cinematic-studio wave-a validate <packet.json>
cinematic-studio wave-a attach <handoff.json> ...   # merge onto agent-mode handoff
```

---

## Plugins & catalog

```bash
cinematic-studio plugin packs
cinematic-studio plugin status
cinematic-studio plugin list [--grouped]
cinematic-studio plugin declutter [--dry-run|--apply]
cinematic-studio plugin catalog check [--release]
cinematic-studio plugin catalog pin
```

Release flow: commit content first → `plugin catalog pin` → commit **only** `.grok-plugin/` as needed. Pre-publish: `plugin catalog check --release`.

---

## Generation ledger

```bash
cinematic-studio generation log ...
cinematic-studio generation list
cinematic-studio generation summary
cinematic-studio generation report
cinematic-studio generation update ...
cinematic-studio generation import-jobs
```

---

## Interactive TUI

```bash
cinematic-studio ui                    # Textual home + launcher + cockpit (TTY)
cinematic-studio ui --interval 5
cinematic-studio ui --print            # Non-TTY / agents / CI: orient dump
cinematic-studio ui --print --no-artifact
```

Without a TTY, bare `ui` falls back to a one-shot orient dump (writes `artifacts/tui_orient_brief.txt` unless `--no-artifact`). Launcher only allows an allowlisted argv set.

---

## Meta installer (shell)

```bash
bash scripts/cinematic_studio.sh install
bash scripts/cinematic_studio.sh update
bash scripts/cinematic_studio.sh verify [--all|--plugin]
bash scripts/cinematic_studio.sh declutter [--dry-run|--apply]
bash scripts/cinematic_studio.sh version
bash scripts/cinematic_studio.sh doctor [--quick]
bash scripts/cinematic_studio.sh grok status|ensure|update|install
```

The `cinematic-studio` wrapper routes `install|update|verify|declutter` to this shell path when present under `CINEMATIC_PROJECT_DIR`.

---

## Common flags

| Flag | Where | Purpose |
|------|--------|---------|
| `--strict-plate` | `sfw`/`nsfw` run/session (and spend paths) | Require plate lock (`approved`/`locked`) |
| `--strict-motion` | same | Require full motion vector / I2V readiness |
| `--strict-wave-a` | batch run, `imagine agent-handoff`, `handoff validate` | Wave A plate+motion hard path |
| `--strict-handoff` | `imagine agent-handoff`, `handoff validate` | Exit 1 on readiness blockers (not root `validate`) |
| `--strict` | `doctor` | Exit 1 on warnings |
| `--format json\|markdown\|clipboard` | handoffs | Output format |
| `--surface <name>` | `imagine agent-handoff` | Target execution surface |
| `--chat-model` | bible / prompt | Default `grok-4.5`; `grok-4.3` for 1M |
| `--video-model` / `-m` | bible / prompt | Imagine video slug or alias |
| `--json` | dashboard, doctor, stack, … | Machine-readable output |
| `--quick` / `-q` | doctor | Skip pytest and full plugin verify |
| `--dry-run` | polish, declutter, … | Plan without side effects |

**Note:** Root `cinematic-studio validate` checks workspace docs/skills/models only. Packet strictness is `handoff validate --strict-handoff` or `imagine agent-handoff --strict-handoff`.

---

## Typical operator flows

### Greenfield

```bash
cinematic-studio create-bible "My Film" --wizard
cinematic-studio dna init "Hero"
cinematic-studio dna lock "hero"
cinematic-studio sequence init "Act 1"
cinematic-studio models verify
cinematic-studio doctor --quick
```

### Still → video (spend-safe)

```bash
cinematic-studio sfw plan ...
cinematic-studio sfw plate set <batch> <shot> --status locked ...
cinematic-studio sfw motion set <batch> <shot> ...
cinematic-studio sfw run ... --strict-plate --strict-motion
```

### Long-form extend

```bash
cinematic-studio sequence add-clip ...
cinematic-studio sequence handoff ...
cinematic-studio sequence extend-prompt ...
cinematic-studio sequence run ...
cinematic-studio sequence health ...
cinematic-studio sequence polish ...
cinematic-studio sequence deliver ...
```

### Planning → generation handoff

```bash
cinematic-studio imagine agent-handoff --surface grok_build_tools --strict-handoff
cinematic-studio handoff validate artifacts/handoff.json --strict-handoff
# or paste path:
cinematic-studio imagine bridge
```

---

## Architecture (for contributors)

```
tools/cinematic_studio_cli.py     # Typer app + group registration only
tools/cli/*.py                    # Command modules (register(app))
tools/cli/tui/                    # Textual TUI
tools/*.py                        # Domain engines (models, doctor, DNA, chain, …)
tools/studio_paths.py             # Canonical paths
```

| Module | Commands |
|--------|----------|
| `studio_commands` | dashboard, status, version, doctor, stack, agents, activate |
| `bible_commands` | create-bible, generate-prompt, cost-simulate, memory |
| `dna_commands` | dna.* |
| `sequence_commands` | sequence.* (largest surface) |
| `imagine_commands` | imagine.* |
| `handoff_commands` | handoff validate |
| `sfw_commands` / `nsfw_commands` | batches + plate/motion (+ nsfw extend) |
| `quota_commands` / `models_commands` | quota.*, models.* |
| `plugin_commands` / `wave_a_commands` | plugin.*, wave-a.* |
| `generation_commands` / `report_commands` | generation.*, report, validate |
| `grok_cli_commands` / `tui_commands` | grok.*, ui |
| `animatic_commands` | animatic.* |
| `spend_preflight` | Shared plate/motion/--strict-* helpers for batch run |

---

*Run any command with `--help` for full options. The CLI is the automation backbone of the Studio.*
