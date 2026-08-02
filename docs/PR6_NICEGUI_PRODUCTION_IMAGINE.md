# PR6 — NiceGUI Production + Imagine

## Routes

| Path | Actions |
|------|---------|
| `/production` | `status`, `validate`, `stack`, `doctor_quick`, `models_*`, `bible_create`, `handoff_validate` |
| `/imagine` | `imagine_list`, `imagine_bridge`, `sequence_handoff`, `dna_handoff` |

All via `execute_action(..., mode="inprocess")`.

Streamlit keeps the full multi-stage bible wizard and live xAI batch execute.

## Run

```bash
pip install -r requirements-nicegui.txt
cinematic-studio web --port 8088
```

## Verify

```bash
pytest tests/test_web_nicegui_production_imagine.py tests/test_web_nicegui_pages.py -q
```
