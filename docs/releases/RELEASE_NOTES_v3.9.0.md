# Release Notes — v3.9.0

**Date:** 2026-08-02  
**Codename:** Multi-surface control plane

## Highlights

Grok Imagine Cinematic Studio **v3.9.0** completes the **UI-agnostic service layer** and ships four complementary operator surfaces on one ActionSpec catalog:

| Surface | Command | Role |
|---------|---------|------|
| Textual TUI | `cinematic-studio ui` | Terminal ops board + cockpit |
| Streamlit | `streamlit run web_ui/app.py` | Guided Bible, DNA bank, live batch, Community Cloud |
| NiceGUI | `cinematic-studio web` | Fast ActionSpec browser shell |
| FastAPI | `cinematic-studio api` | Automation / custom UIs (`/v1/*`) |

All surfaces share:

- `studio_core.services.dashboard` — `build_studio_dashboard()`
- `studio_core.services.actions` — ActionSpec registry, validation, argv
- `studio_core.services.execute` — `execute_action(mode=inprocess|subprocess)`

## Install extras

```bash
pip install -r requirements.txt              # CLI + Streamlit + TUI
pip install -r requirements-nicegui.txt      # + NiceGUI
pip install -r requirements-api.txt          # + FastAPI control plane
```

## Smoke

```bash
python scripts/smoke_studio_surfaces.py
cinematic-studio models verify
cinematic-studio status
```

## Compatibility

- `STUDIO_COMPATIBILITY_VERSION` / handoff protocol: **3.9.0**
- Grok Build CLI ≥ **0.2.93**
- Grok 4.5 cinematic+Build stack unchanged

## Docs

- [WEB_SHELLS.md](../guides/WEB_SHELLS.md)
- [PR1–PR10 notes](../) under `docs/PR*.md`
