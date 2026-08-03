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

## React / TanStack cockpit (optional · Streamlit page parity)

Experimental SPA under `web_react/` on FastAPI (`studio_api` → `studio_core`).

**Pages:** Dashboard · Production · DNA · Sequences · Imagine · Quota · **Bible** (guided) · **Tools** · **Settings** · **NSFW** (opt-in).  
**Still Streamlit-primary:** live xAI batch execute, PDF report download, full NSFW plan/execute.

```bash
# Terminal A
pip install -r requirements-api.txt
cinematic-studio api --host 127.0.0.1 --port 8090

# Terminal B
cinematic-studio web-react
# → http://127.0.0.1:5173  (Vite proxies /v1 and /health → :8090)

# Or manual: cd web_react && npm install && npm run dev
# Preview build: cinematic-studio web-react --preview --port 4173
```

```bash
# Smoke (no Chromium — recommended)
cd web_react && npm run test:smoke

# Optional Playwright UI routes (needs free RAM + chromium)
cd web_react && npx playwright install chromium && CI=1 npm run test:e2e
# or: bash scripts/smoke_web_react_e2e.sh
```

Details: `web_react/README.md`.

