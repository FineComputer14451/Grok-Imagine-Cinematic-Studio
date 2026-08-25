# CLI Reference
## cinematic-studio (Grok Imagine Cinematic Studio v3.11.0)

Primary entry points:

- `cinematic-studio` (installed wrapper)
- `python tools/cinematic_studio_cli.py` (in-repo / tests / catalog pin)
- `bash scripts/cinematic_studio.sh` (meta installer: **install / update / verify / declutter / doctor / grok**)

`cinematic-studio install|update|verify|declutter` is handled by the **PATH wrapper**, not the Typer tree. `python tools/cinematic_studio_cli.py install` is not a Typer command.

PATH `cinematic-studio` often roots at `~/Grok-Cinematic-Projects`. Prefer in-repo `python tools/cinematic_studio_cli.py` when pinning the plugin catalog from this clone.

---

## Global

```bash
python tools/cinematic_studio_cli.py --help
python tools/cinematic_studio_cli.py <command> --help
python tools/cinematic_studio_cli.py commands extend
```

Bare invoke is `--help`. Commands are grouped into journey panels. `commands [query]` searches names and help text.

| Panel | Examples |
|-------|----------|
| Orient | `dashboard` `commands` `status` `version` `activate` |
| Health | `doctor` `validate` `models` `stack` `quota` `grok` |
| Produce | `create-bible` `dna` `sequence` `animatic` `wave-a` `memory` |
| Spend | `sfw` `nsfw` `imagine` `generation` `cost-simulate` |
| Gate | `handoff` |
| Deliver | `report` |
| Surfaces | `ui` `web` `web-react` `api` |
| Meta | `plugin` |

---

## Grok Build CLI binary

Manage the official **Grok Build** binary (min **1.0.5**). Method A install also ensures this automatically.

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
cinematic-studio dna save --file characters/<slug>/dna.json
cinematic-studio dna lock
cinematic-studio dna handoff
cinematic-studio dna inject
```

There is **no** `dna extract` CLI verb. Extraction is the `character-dna-extractor` chat skill; the hidden `dna extract` alias prints this hint and exits 2.

### Sequences

```bash
cinematic-studio sequence init <name>
cinematic-studio sequence add-clip ...
cinematic-studio sequence handoff
cinematic-studio sequence extend-prompt
cinematic-studio sequence qa
cinematic-studio sequence color-grade
cinematic-studio sequence polish
cinematic-studio sequence deliver
```

There is **no** `sequence extend` CLI verb. Use `sequence extend-prompt` (plan) or `sequence run` (Imagine spend). The hidden `sequence extend` alias prints this hint and exits 2.

### Imagine / Handoff

```bash
cinematic-studio imagine agent-handoff \
  --batch <slug> --shot <id> \
  --surface grok_build_tools \
  --format json|markdown

cinematic-studio imagine bridge                 # Classic Surface C bridge
cinematic-studio handoff validate <packet.json> --strict-handoff
```

### Quota & Cost

```bash
cinematic-studio quota estimate -d 45
cinematic-studio quota dashboard
cinematic-studio quota optimize
cinematic-studio quota sync
cinematic-studio cost-simulate --duration 30    # compact alias of quota estimate
```

### Models & Validation

```bash
cinematic-studio models verify
cinematic-studio models stack
cinematic-studio validate
cinematic-studio handoff validate <path> --strict-handoff
```

`--strict-handoff` is a flag on `handoff validate` / `imagine agent-handoff`, not on `validate`.

### Plugins

```bash
cinematic-studio plugin catalog --help          # group: check | pin
cinematic-studio plugin packs
cinematic-studio plugin catalog pin
cinematic-studio plugin catalog check --release
```

`plugin check` is a **hidden alias** of `plugin catalog check` (same `--release` / `--json`). Canonical verb is `plugin catalog check`.

### Interactive TUI

```bash
cinematic-studio ui
# optional:
python tools/cinematic_studio_cli.py ui --interval 5
```

Live studio dashboard + safe launcher + production cockpit. **No Imagine spend** from Launcher/Cockpit.

#### TUI keys

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
| `/` or `Ctrl+P` | Command palette (allowlisted action search) |
| KPI bar | Under status strip |
| `y` | Save orient brief → `artifacts/tui_orient_brief.txt` |
| `ui --print` | Non-TTY / CI: print orient dashboard instead of hard-fail |

Operator loop: [guides/OPERATOR_CONTROL_PLANE.md](guides/OPERATOR_CONTROL_PLANE.md).

### Browser shells & API

```bash
# Streamlit
streamlit run web_ui/app.py

# NiceGUI ActionSpec cockpit
pip install -r requirements-nicegui.txt
cinematic-studio web --host 127.0.0.1 --port 8088

# FastAPI control plane
pip install -r requirements-api.txt
cinematic-studio api --host 127.0.0.1 --port 8090
# OpenAPI → http://127.0.0.1:8090/docs

# React / TanStack SPA (needs API + Node 20+)
cinematic-studio web-react                 # dev :5173, proxies /v1 → :8090
cinematic-studio web-react --preview       # production build serve
cinematic-studio web-react --install       # force npm install
```

Multi-shell matrix: [guides/WEB_SHELLS.md](guides/WEB_SHELLS.md) · React README: `web_react/README.md`.

### SFW / NSFW batches

`sfw --help` and `nsfw --help` group Plan / Readiness / Spend / Quality. NSFW adds Extend.

```bash
cinematic-studio sfw --help
cinematic-studio sfw plan "Hero stills"
cinematic-studio nsfw --help
cinematic-studio nsfw extend plan
```

### Wave A multi-agent packets

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
| `--strict-handoff` | Enforce full packet + specialist checklist (`handoff validate`, `imagine agent-handoff`) |
| `--strict-plate` | Require plate lock (`sfw`/`nsfw` run/session) |
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
python tools/cinematic_studio_cli.py doctor --quick
python tools/cinematic_studio_cli.py models verify
python tools/cinematic_studio_cli.py quota sync
python tools/cinematic_studio_cli.py create-bible --wizard
python tools/cinematic_studio_cli.py dna init --name "Lead" && python tools/cinematic_studio_cli.py dna lock
python tools/cinematic_studio_cli.py sequence init hero-open
python tools/cinematic_studio_cli.py imagine agent-handoff --surface grok_build_tools --format markdown
python tools/cinematic_studio_cli.py handoff validate ./handoff.json --strict-handoff
python tools/cinematic_studio_cli.py ui
```

---

*Run any command with `--help` for full options. The CLI is the automation backbone of the Studio.*

*Grok Imagine Cinematic Studio v3.11.0 — CLI Reference · Independent community project · Not affiliated with xAI*
