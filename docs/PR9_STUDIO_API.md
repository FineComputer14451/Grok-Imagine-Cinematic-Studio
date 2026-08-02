# PR9 — FastAPI control plane (`studio_api`)

## Goal

Expose `studio_core` over HTTP for automation / custom UIs.

## Install / run

```bash
pip install -r requirements-api.txt
cinematic-studio api --port 8090
# docs: http://127.0.0.1:8090/docs
```

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Liveness + action count |
| GET | `/v1/dashboard` | `build_studio_dashboard()` |
| GET | `/v1/actions` | ActionSpec catalog |
| GET | `/v1/actions/{id}` | One action + fields |
| POST | `/v1/actions/{id}/execute` | `execute_action` body: `{answers, mode, timeout}` |

## Safety

Same ActionSpec validation + forbidden tokens as TUI/NiceGUI. No free-form argv.

## Verify

```bash
pytest tests/test_studio_api.py -q
```
