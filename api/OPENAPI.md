# Snapshot API — route map (sketch)

Base URL example: `http://127.0.0.1:8787`

Optional auth: header `X-API-Key: $STUDIO_API_KEY` (only if env set).

| Method | Path | Purpose | Streamlit / tools twin |
|--------|------|---------|-------------------------|
| GET | `/health` | Liveness + tools available | — |
| GET | `/api/v1/meta` | Loaded module names | runtime capability flags |
| GET | `/api/v1/dashboard/snapshot` | Full ops snapshot + severity + attention | `build_studio_dashboard` + TUI widgets |
| GET | `/api/v1/dashboard/severity` | Lightweight poll | sidebar ops strip |
| GET | `/api/v1/cli/actions` | List health actions | dashboard buttons |
| POST | `/api/v1/cli/{action}` | doctor · validate · quota-sync · models-verify | `run_cli([...])` |
| GET | `/api/v1/dna` | List DNA profiles | `list_characters` |
| POST | `/api/v1/dna/lock` | Lock identity | `lock_to_identity_bank` |
| GET | `/api/v1/sequences` | List sequences | `list_sequences` |
| POST | `/api/v1/sequences/init` | Scaffold sequence | `create_sequence_scaffold` |
| GET | `/api/v1/quota/dashboard` | Quota rollup + alignment | `quota_dashboard` |
| POST | `/api/v1/quota/estimate` | Cost + risk estimate | `estimate_production` + `assess_budget_risk` |
| GET | `/api/v1/models/verify` | Stack compatibility | `verify_model_compatibility` |

## Snapshot response shape

```json
{
  "source": "live|mock",
  "studio_version": "3.8.9",
  "severity": "ok|warn|critical",
  "attention": ["…"],
  "snapshot": {
    "project": {},
    "studio": {},
    "quota": {},
    "production": {},
    "readiness": {},
    "convergence": {},
    "delivery": {},
    "sequences": [],
    "characters": [],
    "chain_qa": [],
    "recent_jobs": [],
    "quota_alignment": {}
  }
}
```

React should treat `snapshot` as opaque-compatible with Streamlit `dashboard.py` fields and only specialize presentation.
