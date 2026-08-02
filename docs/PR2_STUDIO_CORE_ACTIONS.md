# PR2 — Extract `studio_core.services.actions`

## Goal

Move the unified **ActionSpec** registry (launcher + cockpit) out of
`tools/cli/tui/actions.py` so Textual TUI, Streamlit/NiceGUI, and a future API
share one catalog for safe argv building and form validation.

## What changed

| Path | Change |
|------|--------|
| `studio_core/services/actions.py` | Full ActionSpec registry (pure Python) |
| `tools/cli/tui/actions.py` | Compatibility re-export shim |
| `studio_core/services/__init__.py` | Exports key action + dashboard APIs |
| `tests/test_studio_core_actions.py` | Shim identity + safety guards |
| `docs/PR2_STUDIO_CORE_ACTIONS.md` | This note |

## Compatibility

```python
from cli.tui.actions import ACTIONS, answers_to_argv, validate_answers  # shim
from studio_core.services.actions import ACTIONS, answers_to_argv       # preferred
```

`cli.tui.catalog` still re-exports launcher catalog via the shim.

## Out of scope

- In-process `execute_action()` (PR3)
- Streamlit wiring to ActionSpec
- FastAPI `/actions/{id}`

## Verify

```bash
pytest tests/test_studio_core_actions.py tests/test_tui_actions.py tests/test_tui_forms.py tests/test_tui_catalog.py tests/test_tui_runner.py -q
```
