# Studio Snapshot API (FastAPI sketch)

HTTP surface over pure `tools/` so **Streamlit**, **TUI**, and **React `web_dashboard`** share one backend.

```text
React / Streamlit  →  FastAPI (this package)  →  tools/* + cinematic_studio_cli
```

## Run (from monorepo root)

```bash
# from Grok-Imagine-Cinematic-Studio/
pip install -r api/requirements.txt
uvicorn api.app.main:app --reload --host 0.0.0.0 --port 8787
```

Open docs: `http://127.0.0.1:8787/docs`

## Contract principles

1. **Dashboard snapshot** is the same object shape as `cli.dashboard.build_studio_dashboard()` (+ optional `quota_alignment`).
2. **Severity / attention** reuse TUI pure helpers when available (`strip_severity`, `collect_home_alerts`).
3. **CLI health** actions map 1:1 to Streamlit `run_cli` / TUI keys (`doctor`, `validate`, `quota sync`, `models verify`).
4. **Graceful degradation** — if `tools/` imports fail, endpoints return demo payloads with `"source": "mock"` (local sketch / CI).
5. Mutations that touch DNA/sequences call pure modules (or CLI) — no second schema in the UI.

## Auth (sketch)

- Optional `X-API-Key` header matching `STUDIO_API_KEY` env (disabled when unset).
- xAI key for Imagine is **not** stored in this API layer long-term; pass via env `XAI_API_KEY` on the server process (same cascade idea as Streamlit secrets → environ).

## React wiring (next step)

```ts
const res = await fetch(`${import.meta.env.VITE_STUDIO_API}/api/v1/dashboard/snapshot`);
const snap = await res.json();
```

Point `VITE_STUDIO_API=http://127.0.0.1:8787` in `web_dashboard/.env.local`.
