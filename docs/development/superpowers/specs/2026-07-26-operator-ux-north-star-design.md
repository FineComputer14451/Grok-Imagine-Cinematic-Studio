# Design: Operator UX North-Star (Studio Control Plane)

**Date:** 2026-07-26  
**Topic:** Full multi-surface operator UX vision for Grok Imagine Cinematic Studio  
**Status:** Design approved — ready for implementation planning (phased)  
**Studio baseline:** v3.8.7 (+ Unreleased TUI/Web density work as Phase 0 foundation)  
**Approach:** Journey-first control plane (Approach A)  
**Optimization:** Operator UX first (not pure quality or install-only)

## Summary of Decisions

| Decision | Choice |
|----------|--------|
| Goal | Operator UX north-star across TUI, Streamlit, CLI, grok.com |
| Structure | **Journey-first** jobs-to-be-done + shared control plane |
| Surfaces | Adapters of one snapshot / attention / action model |
| Scope of this doc | Vision + journeys + phases + metrics — **not** a single PR |
| Phase 0 | Already landed: denser TUI Home + Streamlit dashboard parity |
| Parallel Brief | **Journey J8** (Phase 3 primary; may accelerate later) |
| Non-goals | Replace Grok Build TUI; full in-browser Imagine; silent spend |

## Problem

Operators work across four surfaces (terminal TUI, Streamlit Web UI, classic CLI, grok.com chat/Imagine) that historically diverged in language, density, and safety gates. Recent work unified **severity + attention + multi-panel density** on TUI and Streamlit, but there is no written north-star for:

- Which operator jobs the studio owns end-to-end  
- How surfaces share state and actions  
- What ships next vs later  
- How Parallel Brief / multi-agent mode fits the operator loop  

Without that, UX work risks surface silos and incomplete journeys.

## Goals

1. Define a **Studio Control Plane** concept: snapshot + readiness signals + allowlisted actions + attention/severity.  
2. Name **eight operator journeys** with primary/secondary surfaces and success criteria.  
3. Phase work **0–3** so implementation plans can pick one phase without re-debating vision.  
4. Preserve **safe-by-default** production rules (no silent spend; ErosForge explicit; handoff packets validated).  
5. Keep surfaces **thin**: format and launch; business logic in `tools/`.

## Non-goals

- Replacing the official Grok Build interactive agent TUI  
- Building a full browser Imagine generation console (bridge + API remain)  
- Rewriting Typer commands into a second business layer inside Streamlit  
- One mega-PR that implements all phases  
- NSFW batch run UX without explicit opt-in  

## Architecture

```
Operator journeys (J1–J8)
        │
        ▼
┌──────────────────────────────────────────┐
│  Studio Control Plane (conceptual)       │
│  · Studio Snapshot  build_studio_dashboard│
│  · Attention + severity (pure formatters)│
│  · Readiness signals (plate/motion/      │
│    identity/chain QA/quota/handoff)      │
│  · Action registry (TUI allowlist + CLI) │
└──────────────────┬───────────────────────┘
                   │ adapters
     ┌─────────────┼──────────────┬──────────────┐
     ▼             ▼              ▼              ▼
  TUI           Streamlit       CLI            grok.com
  ui Home+      web_ui/         cinematic-     Activate +
  Cockpit       pages           studio …       Imagine Bridge
```

### Principles

1. **One vocabulary** — severity, attention, chain QA, DNA locks mean the same on every surface.  
2. **Thin surfaces** — no production business rules in `tools/cli/tui/` or `web_ui/` beyond presentation and subprocess/CLI calls.  
3. **Safe by default** — confirm mutating cockpit actions; never emit forbidden spend/wizard tokens from TUI.  
4. **Keyboard-first shell / scan-first web** — TUI for SSH/Termux power users; Streamlit for overview and guided wizards.  
5. **Handoff, don’t fork** — planning context survives as packets (`imagine_agent_mode_handoff`, Execution Bridge).  
6. **YAGNI per phase** — each phase delivers usable journey improvements; north-star is not a big-bang rewrite.

### Existing foundations (do not reimplement)

| Building block | Location |
|----------------|----------|
| Snapshot | `tools/cli/dashboard.py` → `build_studio_dashboard()` |
| TUI density + severity + attention | `tools/cli/tui/widgets.py`, `screens.py`, `app.py` |
| TUI action registry | `tools/cli/tui/actions.py` |
| Streamlit density | `web_ui/pages/dashboard.py`, `web_ui/lib/dashboard_ui.py` |
| Doctor | `tools/doctor.py`, `cinematic-studio doctor` |
| Parallel Brief protocol | `references/agents/Parallel_Brief_Protocol.md` |
| Imagine handoff | `references/agents/IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md` |

## Operator journeys (J1–J8)

| ID | Journey | Operator question | Primary surface | Secondary | Success |
|----|---------|-------------------|-----------------|-----------|---------|
| **J1** | Orient | What’s wrong / ready? | TUI Home / Web Dashboard | `doctor --quick` | Severity + attention ≤3s |
| **J2** | Bootstrap production | Start a Bible + stack | Web Production / CLI wizard | TUI Cockpit create-bible | Bible on disk; stack locked |
| **J3** | Lock identity | Characters consistent? | TUI Cockpit DNA / Web DNA | CLI `dna` | Locked DNA + handoff path |
| **J4** | Gate video spend | Safe to generate video? | Dashboard attention + plate/motion (future) | CLI strict flags | No i2v on unlocked plates when strict |
| **J5** | Extend & stitch | Can we extend? | CLI sequence + chain QA | TUI handoff actions | Chain QA visible; no-go blocks careless extend |
| **J6** | Quota & health | Can we afford this? | TUI Home / Web Quota | `quota sync`, doctor | Risk + alignment + recon visible |
| **J7** | Deliver | Ship polish + crops | CLI polish / ffmpeg / Web tools | AI Polish Director | Delivery path documented in UX |
| **J8** | Parallel Brief | Run multi-agent without chaos? | Studio Director / dispatcher skill | TUI/Web log + converge | Briefs logged; converge → handoff; no silent NSFW |

### Journey notes

- **J1** is the hub: every other journey should deep-link or keybind from Home/Dashboard when practical.  
- **J4** readiness enrichment on the snapshot is **not** Phase 0; it is a candidate Phase 1–2 extension (optional `readiness` rollup on dashboard).  
- **J8** uses existing Parallel Brief Protocol; UX work is visibility, templates, and convergence status—not inventing a new agent runtime.

## Phases

### Phase 0 — Foundation (done / Unreleased)

- TUI multi-panel Home, attention board, strip severity, doctor/validate keys  
- Streamlit dashboard TUI-parity strip, attention, chain QA table, sidebar severity  
- Shared pure helpers (`cli.tui.widgets` + `web_ui/lib/dashboard_ui.py`)

### Phase 1 — Orient + Health (next implementation plan candidate)

**Journeys:** J1, J6  

Suggested work packages (planning will split):

1. Shared attention/severity contract tests (single source of truth documented).  
2. TUI Home deep-links or one-key jumps to high-signal actions already allowlisted.  
3. Web Dashboard action strip (run doctor/validate/quota sync via existing `run_cli` patterns where safe).  
4. Optional: doctor section that echoes control-plane severity summary.  
5. Docs: Quick Start “operator loop” (Orient → act → refresh).

### Phase 2 — Produce + Gate (mid)

**Journeys:** J2, J3, J4, J5  

Suggested work packages:

1. Web/TUI tighter DNA lock feedback after cockpit actions.  
2. Snapshot readiness rollup (plate/motion/identity) when cheap and correct.  
3. Chain QA prominence + clear next action on no-go.  
4. Handoff packet validate entry from TUI/Web tools (read-only validate first).

### Phase 3 — Multi-agent + Deliver (later)

**Journeys:** J7, J8  

Suggested work packages:

1. Parallel Brief status panel / log viewer (read-only first).  
2. Convergence checklist into `imagine_agent_mode_handoff`.  
3. Delivery readiness surface (polish/ffmpeg presets as safe launches).  
4. grok.com bridge packet preview from Web Tools / TUI launcher.

## Surface adapter matrix

| Capability | TUI | Streamlit | CLI | grok.com |
|------------|-----|-----------|-----|----------|
| Live snapshot | Home panels | Dashboard | `dashboard` | Paste/status text |
| Attention/severity | Strip + ATTENTION | Strip + Attention | doctor/quota | Narrative in chat |
| Mutating scaffold | Cockpit + confirm | Production/DNA pages | create-bible / dna / sequence | Chat activation |
| Spend | Out of TUI | Opt-in Imagine pages | `imagine` / batches | Imagine UI |
| Multi-agent | Future J8 panel | Future J8 panel | skills / director | Activate + briefs |
| Handoff | Launcher/tools | Tools / bridge skill | `imagine agent-handoff` | Execution Bridge paste |

## Data flow

1. Project state + sequences + DNA + quota ledger → `build_studio_dashboard()`.  
2. Optional attach: `quota_alignment`, future readiness rollups.  
3. Pure functions: `strip_severity`, `collect_home_alerts` (and Web wrappers).  
4. Surfaces render; actions call allowlisted CLI argv or in-process tools APIs.  
5. After mutations, refresh snapshot (TUI interval / Web button / CLI re-run).

## Error handling

- Snapshot failure: single error panel/banner; do not crash the app process.  
- Missing modules on Cloud: degrade gracefully (existing Streamlit patterns).  
- Action failure: show stdout/stderr; keep navigation stack (TUI I1 confirm pop rules).  
- Parallel Brief failures: surface in log; never auto-route NSFW without ErosForge.

## Testing strategy

| Layer | Expectation |
|-------|-------------|
| Unit | Severity, attention, table/HTML helpers, action allowlist |
| Integration | `run_cli` doctor/validate smoke where CI allows |
| Manual matrix | TUI · Streamlit · CLI · bridge paste per phase |
| PTY E2E | Not required |

## Success metrics

| Metric | Target sense |
|--------|----------------|
| Time to “what’s wrong?” | ≤ 3s on TUI Home or Web Dashboard |
| Cross-surface parity | Same severity + attention family from one snapshot |
| Safe actions | No free-form spend from TUI; confirms for writes |
| Journey coverage | Each J1–J8 has primary surface + CLI escape hatch |
| J8 | Briefs logged; converge path to handoff; no silent NSFW |

## Documentation impacts (when implementing phases)

- `CHANGELOG.md` per shipped phase  
- `docs/guides/Quick_Start_Guide.md` operator loop section  
- Optional README pointer to this north-star  
- Keep `AGENTS.md` activation phrases in sync if VERSION changes  

## Implementation planning guidance

Do **not** implement the entire north-star in one plan. Recommended first plan after this spec:

1. **Phase 1 only** — Orient + Health (J1, J6)  
2. Explicit non-goals: J7/J8 UI, snapshot readiness schema expansion (unless tiny)  
3. Prefer extending shared pure helpers over copying alert rules into Streamlit  

Subsequent plans: Phase 2, then Phase 3.

## Open questions (resolved for this spec)

| Question | Resolution |
|----------|------------|
| Structure | Journey-first control plane |
| Priority | Operator UX |
| Deliverable size | Full north-star (phased) |
| Parallel Brief | J8 included |
| Readiness on snapshot | Not required for Phase 0/1 architecture; candidate Phase 2 |

## Related specs

- `2026-07-26-tui-home-dashboard-density-design.md`  
- `2026-07-19-cli-interactive-tui-design.md`  
- `2026-07-19-cli-tui-full-cockpit-design.md`  
- Parallel Brief Protocol · Imagine Agent Mode Handoff  

---

*Approved design — Operator UX North-Star · Journey-first Studio Control Plane · 2026-07-26*
