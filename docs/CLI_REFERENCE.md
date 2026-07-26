# CLI Reference
## cinematic-studio (Grok Imagine Cinematic Studio v3.8.9)

Primary entry points:
- `cinematic-studio` (installed wrapper)
- `python tools/cinematic_studio_cli.py`
- `bash scripts/cinematic_studio.sh` (meta installer: install/update/verify/doctor/**grok**)

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
# Dashboard + safe launcher + production cockpit
```

### NSFW (requires prior ErosForge activation in chat)
```bash
cinematic-studio nsfw ...
```

### Generation Tracking
```bash
cinematic-studio generation log|list|summary|report|update
```

### Doctor / Health
```bash
cinematic-studio doctor          # or grok-doctor
```

---

## Common Flags

| Flag | Purpose |
|------|---------|
| `--strict-handoff` | Enforce full packet + specialist checklist |
| `--strict-plate` | Require plate lock |
| `--strict-motion` | Require motion vector / I2V readiness |
| `--format json\|markdown` | Output format for handoffs |
| `--surface <name>` | Target execution surface |

---

## Surfaces for Handoff

| Code | Meaning |
|------|---------|
| `grok_build_tools` | In-session tools (preferred) |
| `grok_agent_acp` | ACP / agent sessions |
| `grok_com_imagine` | Web UI paste (Classic Bridge) |
| `xai_api` | Live API jobs |

---

*Run any command with `--help` for full options. The CLI is the automation backbone of the Studio.*
