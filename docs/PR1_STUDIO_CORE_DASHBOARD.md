# PR1 — Extract `studio_core.services.dashboard`

## Goal

Move **UI-agnostic** studio dashboard snapshot aggregation out of
`tools/cli/dashboard.py` so CLI (Rich), TUI (Textual), Streamlit, and future
NiceGUI/API shells share one contract.

## What changed

| Path | Change |
|------|--------|
| `studio_core/` | New package (path helpers + services) |
| `studio_core/services/dashboard.py` | `build_studio_dashboard()` (pure dict) |
| `tools/cli/dashboard.py` | Re-exports builder; keeps Rich renderers |
| `tools/cinematic_studio_cli.py` | Adds repo root to `sys.path` for `studio_core` |
| `tests/test_studio_core_dashboard.py` | Shape + shim identity + no-UI-import guard |

## Compatibility

Existing imports keep working:

```python
from cli.dashboard import build_studio_dashboard  # shim → studio_core
```

Preferred for new code:

```python
from studio_core.services.dashboard import build_studio_dashboard
```

## Out of scope (later PRs)

- Move `ActionSpec` registry (`cli.tui.actions`) → `studio_core.services.actions`
- Move agent/version helpers out of `cli.shared`
- Streamlit → NiceGUI page port
- FastAPI control plane

## Verify

```bash
pytest tests/test_studio_core_dashboard.py tests/test_cli_dashboard.py -q
python tools/cinematic_studio_cli.py dashboard --compact
python tools/cinematic_studio_cli.py ui --print
```
