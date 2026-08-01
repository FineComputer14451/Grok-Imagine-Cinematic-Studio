# Operator UX — Studio Control Plane

**Studio:** v3.8.9 · Grok 4.5 stack  
**Surfaces:** CLI · interactive TUI · Streamlit Web UI · grok.com (Activate / Imagine bridge)  
**Design north-star:** `docs/development/superpowers/specs/2026-07-26-operator-ux-north-star-design.md`

This guide folds the control-plane model into day-to-day operator language: one **snapshot**, shared **severity/attention**, **readiness gates**, and **surface-specific actions**.

---

## 1. One control plane, four adapters

```text
Operator journeys (orient → health → produce → gate → converge → deliver)
        │
        ▼
┌────────────────────────────────────────────┐
│  Studio Control Plane                      │
│  · Snapshot: build_studio_dashboard()      │
│  · Attention + severity (pure formatters)  │
│  · Readiness: identity · plate/motion ·    │
│    chain QA · converge · delivery          │
│  · Actions: TUI allowlist · Web pages ·    │
│    full CLI automation                     │
└──────────────────┬─────────────────────────┘
         ┌─────────┼──────────┬──────────────┐
         ▼         ▼          ▼              ▼
       TUI      Streamlit    CLI          grok.com
    cinematic-  web_ui/   cinematic-    Activate +
    studio ui   app.py    studio …      Imagine Bridge
```

| Surface | Best for | Safe default |
|---------|----------|--------------|
| **TUI** (`cinematic-studio ui`) | SSH / Termux / keyboard ops | No live spend tokens (`run`/`submit`/…) |
| **Web** (`streamlit run web_ui/app.py`) | Scan dashboard, Bible wizard, DNA forms | Dashboard orient; Imagine pages can spend if key set |
| **CLI** | Automation, strict gates, batches, sequences | Full power — use `--strict-*` before video |
| **grok.com** | Chat multi-agent + manual Imagine paste | Bridge / agent-handoff packets |

**Principle:** surfaces are thin. Business logic lives under `tools/`; UIs format and launch.

---

## 2. Shared studio snapshot

Built by `tools/cli/dashboard.py` → `build_studio_dashboard()`.

Same object powers:

```bash
cinematic-studio dashboard [--json] [--compact] [--watch]
cinematic-studio ui          # Home panels
cinematic-studio ui --print  # non-TTY orient dump
streamlit run web_ui/app.py  # Dashboard page + sidebar severity
```

### Top-level keys

| Key | Role |
|-----|------|
| `project` | Title, genre, bible loaded |
| `studio` | Agents, role cards, skills, model compatibility |
| `quota` | Spend, tier, risk, reconciliation |
| `production` | Counts: sequences, DNA, batches, jobs |
| `readiness` | Phase 2 rollup (identity · plate/motion · chain QA · next_actions) |
| `chain_qa` | Per-sequence go/no-go summaries |
| `sequences` / `characters` / batches / `recent_jobs` | Capped lists for density |
| `parallel_briefs` | Discovered Wave A brief logs |
| `convergence` | Checklist before agent-mode handoff |
| `delivery` | Soft polish/deliver readiness per sequence |
| `artifacts` / `production_report` | Artifact pipeline summary |

Optional attach: **`quota_alignment`** (ledger recon) on TUI refresh and Web `attach_quota_alignment`.

### Severity and attention

| Severity | Meaning |
|----------|---------|
| **ok** | No blocking ops signals |
| **warn** | Review attention items (risk, unlock DNA, …) |
| **critical** | Models broken, chain QA no-go flood, etc. |

Derived by pure formatters in `tools/cli/tui/widgets.py` (`strip_severity`, `collect_home_alerts`) — reused by Streamlit via `web_ui/lib/dashboard_ui.py`.

---

## 3. Operator loop (daily)

Matches Quick Start control-plane section; expanded for production.

### Phase 1 — Orient + health

1. Open **TUI** (`ui`) or **Web Dashboard** (view **Ops** / radio **2**).  
2. Read **status strip** severity and **Attention** list.  
3. Health actions:
   - TUI: **d** doctor · **v** validate · **s** quota sync · **m** models · **k** stack  
   - Web: Dashboard **Health actions**  
4. Refresh until Attention is clear or risk is accepted.

```bash
cinematic-studio doctor --quick
cinematic-studio models verify
cinematic-studio validate
cinematic-studio quota sync
```

### Phase 2 — Produce + gate

1. Bible / DNA / sequences (Web Production·DNA, TUI Cockpit, or CLI).  
2. Check **READINESS**: identity locked · chain QA · plate/motion scan.  
3. Before video spend: lock plates + motion briefs; prefer CLI strict flags.  
4. Validate handoff packets after DNA lock / sequence handoff / agent-mode emit.

```bash
cinematic-studio sfw plate set <batch> <shot> --status locked --reference-image-id …
cinematic-studio sfw motion set <batch> <shot> --action "…" --camera "…" --emotion "…"
cinematic-studio sfw run … --strict-plate --strict-motion
cinematic-studio handoff validate path.json --strict-handoff
```

### Phase 3 — Converge + deliver

1. **Convergence** checklist → agent-mode handoff when gates OK.  
2. **Parallel Brief** logs (`wave-a briefs`) for multi-agent sessions.  
3. **Delivery** soft polish/deliver readiness; dry-run from TUI Cockpit.  
4. Bridge preview for grok.com/imagine when API tools unavailable.

```bash
cinematic-studio wave-a briefs <session> -o artifacts/briefs_<session>.json
cinematic-studio imagine agent-handoff -b … --shot … --strict-handoff -f json -o artifacts/handoff.json
cinematic-studio imagine bridge -b … --shot … -f markdown
cinematic-studio sequence polish "Act 1" --dry-run
cinematic-studio sequence deliver "Act 1" --dry-run
```

---

## 4. Density modes (TUI ↔ Web)

| Mode | TUI | Web Dashboard | Intent |
|------|-----|---------------|--------|
| **compact** | key **1** | radio Compact | Orient: strip, KPI, attention, readiness |
| **ops** | key **2** (default) | radio Ops | Gates + quota/studio + chain QA |
| **full** | key **3** | radio Full | + sequences, DNA, jobs, briefs, JSON |

TUI also: **Tab** cycle · **p** pause refresh · **y** save orient brief · **/** palette.

---

## 5. TUI action safety

Registry: `tools/cli/tui/actions.py`.

**Forbidden argv tokens** (never emitted):

```
--wizard  run  submit  record  cancel  declutter
```

| Surface | Role |
|---------|------|
| **Launcher** | Read/inspect: status, lists, doctor, validate, bridge, handoff validate |
| **Cockpit** | Scaffold bible/DNA/sequence, quota budget/estimate, dry polish/deliver, briefs |
| **Palette** | Union of both (`/` / Ctrl+P) |

Execution path: `run_action(id, answers)` → validate form → build argv → reject forbidden → subprocess CLI.

Live video spend is **CLI or Web Imagine**, not TUI.

Full command tree: [CLI Reference](../CLI_REFERENCE.md).

---

## 6. Spend gates (before video credits)

| Gate | Soft default | Hard flags |
|------|--------------|------------|
| **Plate** (still→video) | Warn if not approved/locked | `--strict-plate` · `--strict-wave-a` · agent `--strict-handoff` |
| **Motion** (all video modes) | Free-text cues OK | `--strict-motion` / wave-a / agent strict (full triple) |
| **Wave A field shapes** | Warnings | `--strict-wave-a` |

Modules: `plate_readiness.py` · `motion_readiness.py` · `spend_readiness.py`.  
Prefer official modes (`image_to_video`, not raw alias `i2v`) on batch shots so gates apply.

Deep detail: plate PL-* codes, motion MB-* codes — see those modules and [CLI Reference — Common flags](../CLI_REFERENCE.md).

---

## 7. Handoff packets (planning → generation)

| Packet | CLI | Purpose |
|--------|-----|---------|
| `imagine_agent_mode_handoff` | `imagine agent-handoff` | Multi-surface generation contract |
| Classic bridge | `imagine bridge` | grok.com/imagine paste only |
| `sequence_extend_handoff` | `sequence handoff` | Clip N → N+1 extend chain |

Surfaces: `grok_build_tools` · `grok_agent_acp` · `grok_com_imagine` · `xai_api`.

```bash
cinematic-studio imagine agent-handoff \
  -b <batch> --shot <id> \
  --surface grok_build_tools \
  --strict-handoff -f json -o artifacts/handoff.json
cinematic-studio handoff validate artifacts/handoff.json --strict-handoff
```

Canonical protocol: `references/agents/IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md`.

---

## 8. Sequences (long-form)

On disk: `sequences/<slug>/sequence.json` (schema 1.1).

| Concept | Rule of thumb |
|---------|----------------|
| Chain QA | 10 weighted checks; pass **≥ 7.0**; critical fails → **no_go** |
| Extend | Needs previous `last_frame_recap` + momentum / AMV |
| Regen | Default **2** attempts/clip, **20**/sequence (`sequence regen plan|apply|run`) |
| Identity drift | Pass when score **&lt; 2.5** |
| Health | `sequence health` aggregates QA · drift · seam · AMV · regen · temp |

```bash
cinematic-studio sequence run "Act 1" --clip clip_001
cinematic-studio sequence qa-assist "Act 1" --clip clip_001
cinematic-studio sequence health "Act 1"
```

---

## 9. Journey cheat sheet (J1–J8 style)

| Journey | Primary surface | Success |
|---------|-----------------|---------|
| Orient | TUI Home / Web Dashboard | Severity understood; Attention empty or accepted |
| Health | TUI keys / Web Health actions / `doctor` | Models OK, validate clean |
| Bible | Web wizard / `create-bible` / Cockpit | Project state + stack locked |
| DNA | Web DNA / Cockpit / `dna *` | Cast locked; inject ready |
| Produce stills | CLI / Web Imagine | Plates approved/locked |
| Video spend | CLI (`--strict-*`) | Plate + motion pass; no silent NSFW |
| Handoff | CLI agent-handoff / Tools bridge | Packet validates; return_path set |
| Deliver | `sequence polish` / `deliver` | Soft delivery readiness green; masters built |

---

## 10. Quick commands

```bash
# Orient
cinematic-studio ui
cinematic-studio ui --print
cinematic-studio dashboard --compact
streamlit run web_ui/app.py

# Health
cinematic-studio doctor --quick
cinematic-studio models verify

# Produce
cinematic-studio create-bible "Title" --wizard
cinematic-studio dna init "Hero" && cinematic-studio dna lock hero
cinematic-studio sequence init "Act 1"

# Gate + spend
cinematic-studio sfw plate set … --status locked …
cinematic-studio sfw motion set … --action … --camera … --emotion …
cinematic-studio sfw run … --strict-plate --strict-motion

# Converge
cinematic-studio imagine agent-handoff … --strict-handoff -f json -o artifacts/handoff.json
cinematic-studio handoff validate artifacts/handoff.json --strict-handoff

# Deliver (preview then real)
cinematic-studio sequence polish "Act 1" --dry-run
cinematic-studio sequence deliver "Act 1" --dry-run
```

---

## 11. Related docs

| Doc | Use |
|-----|-----|
| [CLI Reference](../CLI_REFERENCE.md) | Full Typer command tree |
| [Quick Start](Quick_Start_Guide.md) | First-session loop |
| [User Guide](USER_GUIDE.md) | End-to-end production |
| [Streamlit Cloud](streamlit_cloud_deploy.md) | Hosted Web UI caveats |
| [Architecture](../ARCHITECTURE.md) | System layers |
| North-star design | `docs/development/superpowers/specs/2026-07-26-operator-ux-north-star-design.md` |
| Imagine handoff protocol | `references/agents/IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md` |
| Identity continuity | `references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md` |

---

*Operator UX control plane guide — studio v3.8.9 · shared snapshot across CLI · TUI · Web.*
