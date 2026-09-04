# Web shells — Streamlit · NiceGUI · React (multi-run)

Grok Imagine Cinematic Studio exposes **multiple browser UIs** that share one service layer (`studio_core`). They are complementary, not mutually exclusive.

| | **Streamlit** (`web_ui/`) | **NiceGUI** (`web_nicegui/`) | **React** (`web_react/`) |
|--|---------------------------|------------------------------|---------------------------|
| Install | `requirements.txt` | `requirements-nicegui.txt` | Node 20+ · `web_react/package.json` |
| Start | `streamlit run web_ui/app.py` | `cinematic-studio web --port 8088` | `cinematic-studio api` + `cinematic-studio web-react` |
| Best for | Live xAI batch, Community Cloud, PDF tools, full NSFW planners | Fast ActionSpec forms, TUI safety in-browser | SPA cockpit + guided Bible on HTTP; TanStack Query/Form |
| Backend | `studio_core` in-process | `studio_core` in-process | **FastAPI** `studio_api` → `studio_core` |
| Cloud | [Streamlit Community Cloud](streamlit_cloud_deploy.md) | Self-host | Self-host (API + static SPA) |

## Shared core

```text
studio_core/
  services/
    dashboard.py   # build_studio_dashboard() → JSON snapshot
    actions.py     # ActionSpec registry, validate_answers, answers_to_argv
    execute.py     # execute_action(mode="inprocess"|"subprocess")
```

- **TUI** (`cinematic-studio ui`) uses `mode="subprocess"`.
- **NiceGUI / React** prefer ActionSpec execute (in-process via API or NiceGUI).
- Forbidden argv tokens (`--wizard`, `run`, `submit`, …) are enforced in `studio_core`.

## Quick start

```bash
# Streamlit (default web UI)
pip install -r requirements.txt
streamlit run web_ui/app.py

# NiceGUI (optional second shell)
pip install -r requirements-nicegui.txt
cinematic-studio web --host 127.0.0.1 --port 8088

# React SPA + API (optional third shell)
pip install -r requirements-api.txt
cinematic-studio api --host 127.0.0.1 --port 8090   # Terminal A
cinematic-studio web-react                            # Terminal B → :5173
```

## Route matrix

### NiceGUI (`cinematic-studio web`)

| Path | Role |
|------|------|
| `/` | Dashboard (compact / ops / full) |
| `/production` | status · validate · stack · doctor · models · bible · handoff |
| `/dna` | list · init · lock · show · handoff |
| `/sequences` | list · init · add-clip · show · handoff · quota estimate |
| `/imagine` | jobs · Files API · bridge · handoffs |
| `/quota` | dashboard · sync · budget · estimate |

### React (`cinematic-studio web-react`)

| Path | Role |
|------|------|
| `/` | Dashboard (compact / ops / full) |
| `/production` … `/quota` | ActionSpec cockpit (NiceGUI parity) |
| `/bible` | Guided Production Bible (Streamlit/CLI stages; HTTP, no `--wizard`) |
| `/tools` | Models/health, Files list, handoff, bridge, wave-a, Role Cards, roster |
| `/settings` | localStorage prefs · API key presence · NSFW opt-in |
| `/nsfw` | Opt-in batch inventory only (live plan/spend stays Streamlit/CLI) |

## When to use which

| Need | Prefer |
|------|--------|
| Live Imagine batch / Streamlit Cloud | **Streamlit** (Imagine → Files tab for `file_id`) |
| Thin ActionSpec cockpit, Python-only | **NiceGUI** |
| SPA + guided Bible over HTTP / custom UI fork base | **React** + **API** |
| SSH / no browser | **TUI** (`cinematic-studio ui`) |
| Automation / OpenAPI | **FastAPI** only |

## HTTP control plane

```bash
pip install -r requirements-api.txt
cinematic-studio api --port 8090
# OpenAPI → http://127.0.0.1:8090/docs
```

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Liveness + action count + `xai_api_key_set` |
| GET | `/v1/dashboard` | Studio snapshot |
| GET | `/v1/actions[/{id}]` | ActionSpec catalog |
| POST | `/v1/actions/{id}/execute` | Allowlisted execute |
| GET | `/v1/meta/*` | Env, options, agents, role cards |
| GET/POST | `/v1/bible/*` | Guided Bible stages / validate / generate |

See `docs/PR9_STUDIO_API.md`.

## React smoke

```bash
cd web_react && npm run test:unit && npm run test:smoke
# optional UI e2e (Chromium + free RAM): CI=1 npm run test:e2e
# or: bash scripts/smoke_web_react_e2e.sh
```

Details: `web_react/README.md`.

## Migration notes

- PR1–PR11: `studio_core` extract, NiceGUI, Streamlit wiring, FastAPI, polish (`docs/PR*.md`).
- **v3.10.0:** Imagine Image 2.0 + Video 1.0/1.5 surface catalog on API `production-options` and Imagine pickers.
- **v3.9.1:** React SPA + meta/bible HTTP endpoints (PR #21).
