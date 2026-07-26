# Release Notes — Grok Imagine Cinematic Studio v3.8.8

**Date:** 2026-07-26  
**Stack:** Grok 4.5 cinematic + Build · Model Layer v4.5 (v9-4p5 / `grok-4-auto`) · optional Grok 4.3 1M · dual Imagine Video 1.0 / 1.5  
**Activation:** `Activate Grok Imagine Cinematic Studio v3.8.8`

## Highlights

| Area | Change |
|------|--------|
| **Operator UX** | Journey-first **Studio Control Plane** (Phases 1–3) across TUI + Streamlit + CLI |
| **TUI / Web** | Dense multi-panel dashboards: severity, Attention, READINESS, Convergence, Parallel Briefs, Delivery |
| **Handoff** | `cinematic-studio handoff validate` + TUI/Web entry points |
| **Wave A** | 8 specialists + packets + CLI + `--strict-wave-a` (carried from Unreleased) |
| **Grok Build** | `cinematic-studio grok status\|ensure\|update\|install` |

## Operator UX (control plane)

1. **Orient (Phase 1)** — status strip severity · Attention board · doctor/validate/quota/models keys · Quick Start operator loop  
2. **Produce / Gate (Phase 2)** — readiness rollup (identity · plate/motion · chain QA) · next actions · DNA lock coaching · handoff validate  
3. **Multi-agent / Deliver (Phase 3)** — Parallel Brief log discovery · convergence checklist → agent-mode handoff · delivery polish/deliver readiness · dry-run cockpit actions · imagine bridge preview  

Canonical design: `docs/development/superpowers/specs/2026-07-26-operator-ux-north-star-design.md`

## Also in this release

- Wave A P0–P2 (specialists, packets, CLI, spend gates)
- Grok Build CLI management + Method A ensure
- Multi-surface install docs (shell · grok.com · Imagine bridge · mobile)

## Compatibility

- Grok Build CLI ≥ **0.2.93** (stable often 0.2.112+)
- Handoff `protocol_version` accepts **3.7.1–3.8.8**
- Registry default chat/build: **`grok-4.5`**; fork secondary: **`grok-build`**

## Upgrade

```bash
# Plugin (Method B)
grok plugin update grok-imagine-cinematic-studio
# or
grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio --trust

# Meta installer (Method A)
bash scripts/cinematic_studio.sh update
bash scripts/cinematic_studio.sh verify --all   # or --plugin

# Grok Build binary
cinematic-studio grok ensure

# Health / control plane
cinematic-studio doctor --quick
cinematic-studio ui
streamlit run web_ui/app.py
```

Activation: **`Activate Grok Imagine Cinematic Studio v3.8.8`**

## Assets

- `grok-imagine-cinematic-studio-skills-install-v3.8.8.zip` — full skills + tools/refs (when published)
- `grok-imagine-cinematic-studio-meta-installer-v3.8.8.zip` — bootstrap + installer scripts (when published)

## Notes

- **3.8.7** remains Wave A + Parallel Brief Protocol + Doctor + Multi-Clip Continuity.  
- **3.8.8** is the Operator UX control-plane release (TUI/Web density + Phases 1–3) plus Unreleased Wave A/Grok CLI packaging cleanup.  
- Catalog pin: commit content → `plugin catalog pin` → commit only `.grok-plugin/` when publishing marketplace.
