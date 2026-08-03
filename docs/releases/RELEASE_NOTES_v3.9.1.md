# Release Notes — v3.9.1

**Date:** 2026-08-03  
**Codename:** React / TanStack operator cockpit

## Highlights

Grok Imagine Cinematic Studio **v3.9.1** adds a fifth complementary browser surface: a **React + TanStack SPA** on the existing FastAPI control plane. Domain logic stays in `studio_core`; the SPA never free-forms argv.

| Surface | Command | Role |
|---------|---------|------|
| Textual TUI | `cinematic-studio ui` | Terminal ops board + cockpit |
| Streamlit | `streamlit run web_ui/app.py` | Live batch, Community Cloud, PDF tools |
| NiceGUI | `cinematic-studio web` | Fast ActionSpec browser shell |
| FastAPI | `cinematic-studio api` | HTTP dashboard + ActionSpec + meta + guided Bible |
| **React** | `cinematic-studio web-react` | TanStack SPA (Streamlit page parity on API) |

## React cockpit (`web_react/`)

**Pages:** Dashboard · Production · DNA · Sequences · Imagine · Quota · **Bible** (guided) · Tools · Settings · NSFW (opt-in).

**Stack:** React + Vite · TanStack Router / Query / Form / Table · proxies `/v1` + `/health` to `:8090`.

**Notable flows:**

- ActionSpec forms with Settings prefs seeding and confirm gates
- Guided Production Bible (`GET/POST /v1/bible/*`) — same stages as Streamlit/CLI wizard, never `--wizard`
- Post-generate handoff cards → DNA / sequence / quota forms pre-seeded (session)

## API extensions

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/v1/meta/env` | API key presence (non-secret) |
| GET | `/v1/meta/production-options` | Settings option lists |
| GET | `/v1/meta/agents` | Agent roster |
| GET | `/v1/meta/role-cards[/{stem}]` | Role Card list + preview |
| GET | `/v1/bible/stages` | Wizard stage schema |
| POST | `/v1/bible/validate` | Per-stage validation |
| POST | `/v1/bible/guided` | Build/write Production Bible |

## Still Streamlit-primary

Live xAI batch execute · full NSFW plan/queue/execute · PDF report download.

## Install / run

```bash
pip install -r requirements-api.txt
cinematic-studio api --port 8090

# Node 20+
cinematic-studio web-react
# → http://127.0.0.1:5173
```

## Smoke

```bash
python scripts/smoke_studio_surfaces.py
cd web_react && npm run test:unit && npm run test:smoke
# optional Playwright: CI=1 npm run test:e2e
```

## Compatibility

- `STUDIO_COMPATIBILITY_VERSION` / handoff protocol: **3.9.1** (accepts prior **3.9.0** packets)
- Grok Build CLI ≥ **0.2.93**
- Grok 4.5 cinematic+Build stack unchanged

## Docs

- [WEB_SHELLS.md](../guides/WEB_SHELLS.md) — multi-shell matrix (Streamlit · NiceGUI · React · API)
- [web_react/README.md](../../web_react/README.md)
- [PR9_STUDIO_API.md](../PR9_STUDIO_API.md)
