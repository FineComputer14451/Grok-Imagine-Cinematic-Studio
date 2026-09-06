# Cinematic Studio — React / TanStack cockpit (v1)

NiceGUI-parity **browser SPA** on the shared FastAPI control plane (`studio_api` → `studio_core`).

**Parity target:** six routes only (Dashboard, Production, DNA, Sequences, Imagine, Quota).  
**Out of scope v1:** Streamlit Settings / Tools / Guided Bible wizard / NSFW planners / live xAI batch.

## Stack

| Layer | Library |
|-------|---------|
| UI | React 19 + Vite |
| Routing | TanStack Router |
| Server state | TanStack Query |
| Action forms | TanStack Form |
| Tables | TanStack Table |
| Backend | `GET /v1/dashboard`, `GET /v1/actions`, `POST /v1/actions/{id}/execute` |

No business logic is reimplemented in the SPA — only snapshot + ActionSpec execute.

## Prerequisites

```bash
# API (from repo root)
pip install -r requirements-api.txt
cinematic-studio api --host 127.0.0.1 --port 8090
# OpenAPI: http://127.0.0.1:8090/docs
```

Node.js 20+ recommended.

## Develop

**CLI (recommended):**

```bash
# Terminal A
cinematic-studio api --port 8090

# Terminal B
cinematic-studio web-react
# → http://127.0.0.1:5173  (proxies /v1 and /health → :8090)

cinematic-studio web-react --install          # force npm install
cinematic-studio web-react --port 5174
cinematic-studio web-react --api-url http://127.0.0.1:8090
cinematic-studio web-react --preview --port 4173
cinematic-studio web-react --open
```

**Manual:**

```bash
cd web_react
npm install
npm run dev
# → http://127.0.0.1:5173  (proxies /v1 and /health → :8090)
```

Optional: point at a remote API without the Vite proxy:

```bash
export VITE_STUDIO_API_URL=http://127.0.0.1:8090
npm run dev
```

## Build

```bash
npm run build    # dist/
npm run preview  # serve dist (preview proxy still → :8090 unless VITE_STUDIO_API_URL set at build)
# or: cinematic-studio web-react --preview
```

## Routes

| Path | Role |
|------|------|
| `/` | Dashboard (compact / ops / full density) |
| `/production` | status · validate · stack · doctor · models · bible · handoff |
| `/dna` | list · init · lock · show · handoff |
| `/sequences` | list · init · add-clip · show · handoff · quota estimate |
| `/imagine` | jobs · bridge · handoffs (no live spend) |
| `/quota` | dashboard · sync · budget · sequence estimate |
| `/bible` | **Guided Bible** — multi-step wizard (same stages as Streamlit / CLI wizard); `POST /v1/bible/guided` |
| `/tools` | **Phase 2** — models/health, handoff, bridge, wave-a briefs, polish/deliver dry-run, Role Cards, agent roster |
| `/settings` | **Phase 2** — model/production prefs (localStorage), API key presence, NSFW opt-in |
| `/nsfw` | **Phase 2** — opt-in only; batch snapshot (no live plan/spend) |

### Phase 2 notes

- **Settings** prefs are browser-local (Streamlit `session_state` analogue). They do **not** inject `XAI_API_KEY` into the API process.
- **Prefs → ActionSpec forms:** saved Settings seed matching field keys (`genre`, `chat_model`, `video_model`, `image_model`, `director`, `duration`, `tier` / `quota_tier`, …) via `src/lib/prefsToAnswers.ts`. Forms remount on save (`PREFS_UPDATED_EVENT`).
- **Tools** uses ActionSpec + `GET /v1/meta/*` (role cards / agents). PDF report download remains Streamlit/CLI.
- **NSFW** live plan/execute stays Streamlit/CLI; SPA shows dashboard `nsfw_batches` only.
- **Guided Bible** on `/bible` uses `cli.bible_stages` + `build_production_bible` over HTTP (never ActionSpec `--wizard`). Quick `bible_create` ActionSpec remains on Production.
- **Post-generate handoff:** after Generate, session seeds DNA / Sequence / Quota forms (`bibleHandoff.ts`). Links open e.g. `/dna?action=dna_init&from=bible` with pre-filled ActionSpec fields.

```bash
npm run test:unit    # prefs → form defaults
npm run test:smoke   # recommended: API + SPA HTML + proxy (no Chromium; builds + starts stack)
npm run test:smoke:api  # API-only if studio_api already on :8090
npm run test:e2e     # optional Playwright (needs Chromium + ~2GB free RAM)
npm run build
```

Playwright (optional UI route checks):

```bash
npx playwright install chromium
CI=1 npm run test:e2e
# stack: e2e/start-stack.sh · proxy via VITE_API_PROXY_TARGET
```

Low-memory hosts: prefer `test:smoke` over `test:e2e`.

## Safety

- Execute is **ActionSpec-allowlisted only** (same as TUI / NiceGUI).
- Confirm dialog when `needs_confirm` is true.
- Forbidden argv tokens stay on the server (`studio_core.services.actions`).

## Related docs

- `docs/PR9_STUDIO_API.md` — HTTP contract  
- `docs/guides/WEB_SHELLS.md` — Streamlit + NiceGUI dual-run  
- `AGENTS.md` — multi-surface control plane rules  
