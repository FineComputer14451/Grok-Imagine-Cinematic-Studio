# PR4 — NiceGUI read-only dashboard shell

## Goal

Scaffold a **NiceGUI** web shell that reuses `studio_core.services.dashboard`
(same snapshot as CLI / TUI / Streamlit) without rewriting the pipeline.

Streamlit (`web_ui/`) remains the default / Community Cloud UI.

## Install

```bash
pip install -r requirements-nicegui.txt
cinematic-studio web --port 8088
# open http://127.0.0.1:8088/
```

## Layout

```
web_nicegui/
  app.py                 # ui.run entry
  pages/dashboard.py     # compact / ops / full density
  lib/snapshot.py        # load_snapshot() → studio_core
tools/cli/web_commands.py
requirements-nicegui.txt
```

## What is intentionally missing (later PRs)

- DNA / Sequences / Quota mutating pages
- Wiring to `execute_action(..., mode="inprocess")`
- Replacing Streamlit

## Verify

```bash
pytest tests/test_web_nicegui_dashboard.py -q
cinematic-studio web --help
```
