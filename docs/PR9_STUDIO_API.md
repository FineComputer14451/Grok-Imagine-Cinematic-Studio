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
| GET | `/health` | Liveness + action count + `xai_api_key_set` |
| GET | `/v1/dashboard` | `build_studio_dashboard()` |
| GET | `/v1/actions` | ActionSpec catalog |
| GET | `/v1/actions/{id}` | One action + fields |
| POST | `/v1/actions/{id}/execute` | `execute_action` body: `{answers, mode, timeout}` |
| GET | `/v1/meta/env` | Non-secret env signals (API key presence only) |
| GET | `/v1/meta/production-options` | Static Settings option lists / defaults |
| GET | `/v1/meta/agents` | Agent roster groups |
| GET | `/v1/meta/role-cards` | Role Card file list |
| GET | `/v1/meta/role-cards/{stem}` | Role Card text preview (path-safe) |
| GET | `/v1/bible/stages` | Guided Bible stage schema (`cli.bible_stages.STAGES`) |
| POST | `/v1/bible/validate` | Validate one stage: `{stage_id, answers}` |
| POST | `/v1/bible/guided` | Build bible: `{answers, write?, output?}` — never `--wizard` |

## Safety

Same ActionSpec validation + forbidden tokens as TUI/NiceGUI. No free-form argv.

## Verify

```bash
pytest tests/test_studio_api.py -q
```
