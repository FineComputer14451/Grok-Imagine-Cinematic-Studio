# PR10 — Surface polish (README · CI · API · smoke)

## Changes

- README: FastAPI control plane in What's new, architecture, CLI, Web section
- CI: track `studio_api/**` + py_compile `studio_api/app.py`
- API: permissive CORS for local custom UIs; `GET /` index JSON
- `scripts/smoke_studio_surfaces.py` — no long-running servers

## Verify

```bash
pytest tests/test_studio_api.py -q
python scripts/smoke_studio_surfaces.py
```
