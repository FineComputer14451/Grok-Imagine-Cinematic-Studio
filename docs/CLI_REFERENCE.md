# CLI Reference
## cinematic-studio (Grok Imagine Cinematic Studio v3.8.9)

Primary entry points:

- `cinematic-studio` (installed wrapper)
- `python tools/cinematic_studio_cli.py`
- `bash scripts/cinematic_studio.sh` (meta installer: install / update / verify / doctor / **grok**)

---

## Global

```bash
cinematic-studio --help
cinematic-studio <command> --help
```

---

## Grok Build CLI binary

Manage the official **Grok Build** binary (min **0.2.93**). Method A install also ensures this automatically.

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

## Core Commands

### Production Bible

```bash
cinematic-studio create-bible --wizard          # Interactive guided wizard
cinematic-studio create-bible "Project Title"   # Non-interactive
```

### Character DNA

```bash
cinematic-studio dna init --name "Character Name"
cinematic-studio dna extract
cinematic-studio dna lock
cinematic-studio dna handoff
cinematic-studio dna inject
```

### Sequences

```bash
cinematic-studio sequence init <name>
cinematic-studio sequence add-clip ...
cinematic-studio sequence handoff
cinematic-studio sequence extend
cinematic-studio sequence qa
cinematic-studio sequence color-grade
cinematic-studio sequence polish
cinematic-studio sequence deliver
```

### Imagine / Handoff

```bash
cinematic-studio imagine agent-handoff \
  --batch <slug> --shot <id> \
  --surface grok_build_tools \
  --format json|markdown

cinematic-studio imagine bridge                 # Classic Surface C bridge
```

### Quota & Cost

```bash
cinematic-studio quota estimate --video-seconds 45 --tier heavy
cinematic-studio quota dashboard
cinematic-studio quota optimize
cinematic-studio quota sync
```

### Models & Validation

```bash
cinematic-studio models verify
cinematic-studio models stack
cinematic-studio validate
cinematic-studio validate --strict-handoff
```

### Plugins

```bash
cinematic-studio plugin catalog
cinematic-studio plugin packs
cinematic-studio plugin catalog pin
cinematic-studio plugin check --release
```

### Interactive TUI

```bash
cinematic-studio ui
# optional:
python tools/cinematic_studio_cli.py ui --interval 5
```

Live studio dashboard + safe launcher + production cockpit. **No Imagine spend** from Launcher/Cockpit.

#### TUI keys (v3.8.9)

| Key | Action |
|-----|--------|
| `1` | Compact Home density |
| `2` | Ops Home density |
| `3` | Full Home density |
| `Tab` | Cycle density modes |
| `p` | Pause / resume auto-refresh |
| Type | Filter Launcher / Cockpit action lists |
| `d` | Doctor |
| `v` | Validate |
| `s` | Quota sync |
| `m` | Models verify |
| `k` | Models stack |
| `c` | Cockpit (Bible / DNA / sequence scaffold; dry-run polish/deliver) |
| `l` | Launcher (status, lists, validate, stack, show DNA/sequence) |

Operator loop: [guides/OPERATOR_CONTROL_PLANE.md](guides/OPERATOR_CONTROL_PLANE.md).

#### Unreleased (next) — see CHANGELOG `[Unreleased]`

| Feature | Notes |
|---------|--------|
| `/` or `Ctrl+P` | Command palette (allowlisted action search) |
| KPI bar | Under status strip |
| `y` | Save orient brief → `artifacts/tui_orient_brief.txt` |
| `ui --print` | Non-TTY / CI: print orient dashboard instead of hard-fail |

These ship with the next version bump; do not treat as part of 3.8.9 until `VERSION` advances.

### NSFW (requires prior ErosForge activation in chat)

```bash
cinematic-studio nsfw ...
```

### Handoff validation

```bash
cinematic-studio handoff validate <path-to-packet.json|markdown>
cinematic-studio handoff validate <path> --strict-handoff
cinematic-studio handoff validate <path> --strict-wave-a
```

### Wave A multi-agent packets (v3.8.8+)

Eight specialist packet builders for plate/motion, micro-physics, hair/makeup, dialogue/ADR, score/temp music, titles, distribution crops, and parallel briefs.

```bash
cinematic-studio wave-a --help
cinematic-studio wave-a plate-motion ...
cinematic-studio wave-a contact ...
cinematic-studio wave-a hmu ...
cinematic-studio wave-a dialogue ...
cinematic-studio wave-a score ...
cinematic-studio wave-a title ...
cinematic-studio wave-a crop ...
cinematic-studio wave-a briefs
cinematic-studio wave-a validate
cinematic-studio wave-a attach   # attach Wave A packets to Imagine handoff
```

Use `--strict-wave-a` on `sfw run`, `nsfw run`, and `imagine agent-handoff` when Wave A completeness is required.

### Generation ledger

Local Imagine spend / job tracking:

```bash
cinematic-studio generation log
cinematic-studio generation list
cinematic-studio generation summary
cinematic-studio generation report
cinematic-studio generation update
cinematic-studio generation import-jobs
```

### Doctor / Health

```bash
cinematic-studio doctor              # full health registry
cinematic-studio doctor --quick      # fast preflight
# alias: grok-doctor
```

---

## Common Flags

| Flag | Purpose |
|------|---------|
| `--strict-handoff` | Enforce full packet + specialist checklist |
| `--strict-plate` | Require plate lock |
| `--strict-motion` | Require motion vector / I2V readiness |
| `--strict-identity` | Hard-fail identity gate on extend path |
| `--strict-wave-a` | Enforce Wave A packet completeness |
| `--format json\|markdown` | Output format for handoffs |
| `--surface <name>` | Target execution surface |
| `--dry-run` | Scaffold / preview without mutating spend paths (where supported) |

---

## Surfaces for Handoff

| Code | Meaning |
|------|---------|
| `grok_build_tools` | In-session tools (preferred) |
| `grok_agent_acp` | ACP / agent sessions |
| `grok_com_imagine` | Web UI paste (Classic Bridge) |
| `xai_api` | Live API jobs |

---

## Quick operator sequence

```bash
cinematic-studio doctor --quick
cinematic-studio models verify
cinematic-studio quota sync
cinematic-studio create-bible --wizard
cinematic-studio dna init --name "Lead" && cinematic-studio dna lock
cinematic-studio sequence init hero-open
cinematic-studio imagine agent-handoff --surface grok_build_tools --format markdown
cinematic-studio handoff validate ./handoff.json --strict-handoff
cinematic-studio ui
```

---

*Run any command with `--help` for full options. The CLI is the automation backbone of the Studio.*

*Grok Imagine Cinematic Studio v3.8.9 — CLI Reference · Independent community project · Not affiliated with xAI*
