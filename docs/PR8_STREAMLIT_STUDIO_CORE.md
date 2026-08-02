# PR8 — Wire Streamlit to `studio_core`

## Goal

Streamlit joins TUI + NiceGUI on the shared service layer:

| Surface | Dashboard | Actions |
|---------|-----------|---------|
| TUI | `studio_core` via shim | `execute` subprocess |
| NiceGUI | `studio_core` | `execute` in-process |
| Streamlit | `studio_core.services.dashboard` (preferred) | `execute_registered` / `run_cli_or_action` |

## Changes

- `web_ui/lib/runtime.py` — path to repo root; prefer core dashboard; add `execute_registered` + `run_cli_or_action`
- `web_ui/pages/tools.py` — Safe ActionSpec strip; handoff + bridge via ActionSpec
- `tests/test_web_ui_studio_core.py`

## Verify

```bash
pytest tests/test_web_ui_studio_core.py -q
```
