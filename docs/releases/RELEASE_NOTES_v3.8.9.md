# Release Notes — Grok Imagine Cinematic Studio v3.8.9

**Date:** 2026-07-26  
**Stack:** Grok 4.5 cinematic + Build · Model Layer v4.5 · dual Imagine Video 1.0 / 1.5  
**Activation:** `Activate Grok Imagine Cinematic Studio v3.8.9`

## Highlights

| Area | Change |
|------|--------|
| **TUI Home** | View modes **1 compact / 2 ops / 3 full**, Tab cycle, **p** pause auto-refresh |
| **TUI lists** | Type-to-filter on Launcher and Cockpit |
| **Streamlit** | Matching compact / ops / full dashboard density (session-persisted) |
| **Layout** | Dual-column readiness \| convergence on TUI Home |

## Upgrade

```bash
grok plugin update grok-imagine-cinematic-studio
# or
bash scripts/cinematic_studio.sh update

cinematic-studio ui          # try 1 / 2 / 3 / p
streamlit run web_ui/app.py  # Dashboard view radio
cinematic-studio doctor --quick
```

Activation: **`Activate Grok Imagine Cinematic Studio v3.8.9`**

## Compatibility

- Grok Build CLI ≥ **0.2.93**
- Handoff `protocol_version` accepts **3.7.1–3.8.9**
- Builds on **v3.8.8** Operator UX control plane

## Assets

- `grok-imagine-cinematic-studio-skills-install-v3.8.9.zip`
- `grok-imagine-cinematic-studio-meta-installer-v3.8.9.zip`

## Notes

- **3.8.8** = full control-plane (Phases 1–3) + Wave A packaging  
- **3.8.9** = density UX polish (view modes) on TUI + Streamlit  
