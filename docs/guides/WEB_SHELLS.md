# Web shells — Streamlit + NiceGUI (dual-run)

Grok Imagine Cinematic Studio exposes **two browser UIs** that share one service layer.
They are complementary, not mutually exclusive.

| | **Streamlit** (`web_ui/`) | **NiceGUI** (`web_nicegui/`) |
|--|---------------------------|------------------------------|
| Install | `requirements.txt` | `pip install -r requirements-nicegui.txt` |
| Start | `streamlit run web_ui/app.py` | `cinematic-studio web --port 8088` |
| Best for | Guided Bible wizard, DNA bank forms, live xAI batch execute, Community Cloud | Fast ActionSpec forms, same safety model as Textual TUI, light shell |
| Cloud | [Streamlit Community Cloud](streamlit_cloud_deploy.md) | Self-host / local (FastAPI under NiceGUI) |
| Core API | `studio_core` via `lib.runtime` (`build_studio_dashboard`, `execute_registered`) | `studio_core.services.{dashboard,actions,execute}` |

## Shared core

```text
studio_core/
  services/
    dashboard.py   # build_studio_dashboard() → JSON snapshot
    actions.py     # ActionSpec registry, validate_answers, answers_to_argv
    execute.py     # execute_action(mode="inprocess"|"subprocess")
```

- **TUI** (`cinematic-studio ui`) uses `mode="subprocess"` for isolation.
- **NiceGUI** uses `mode="inprocess"` (Typer invoke) for low latency.
- Forbidden argv tokens and static allowlists are enforced in both paths.

## Quick start

```bash
# Streamlit (default web UI)
pip install -r requirements.txt
streamlit run web_ui/app.py

# NiceGUI (optional second shell — separate port)
pip install -r requirements-nicegui.txt
cinematic-studio web --host 127.0.0.1 --port 8088
```

NiceGUI routes:

| Path | Role |
|------|------|
| `/` | Dashboard (compact / ops / full) |
| `/production` | status · validate · stack · doctor · models · bible · handoff validate |
| `/dna` | list · init · lock · show · handoff |
| `/sequences` | list · init · add-clip · show · handoff · quota estimate |
| `/imagine` | jobs · bridge · DNA/sequence handoff |
| `/quota` | dashboard · sync · budget · sequence estimate |

## When to use which

- **Streamlit** — first-time producers, multi-stage Bible wizard, Streamlit Cloud deploy, live Imagine batch when an API key is present.
- **NiceGUI** — operators who already know the CLI ActionSpec catalog, want cockpit-parity forms in a browser, or want a thin shell on top of `execute_action`.
- **TUI** — SSH / no-browser environments (`cinematic-studio ui`).

## Migration notes (PR1–PR6)

See `docs/PR1_STUDIO_CORE_DASHBOARD.md` … `docs/PR6_NICEGUI_PRODUCTION_IMAGINE.md` for the extract-and-shim history. Existing `cli.tui.actions` / `cli.tui.runner` imports remain stable.

## HTTP control plane (optional)

```bash
pip install -r requirements-api.txt
cinematic-studio api --port 8090
```

OpenAPI docs at `/docs`. See `docs/PR9_STUDIO_API.md`.

