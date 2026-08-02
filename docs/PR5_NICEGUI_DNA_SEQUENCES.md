# PR5 — NiceGUI DNA / Sequences / Quota + execute_action

## Goal

Wire mutating/read workflows into the NiceGUI shell using the shared
ActionSpec registry and `execute_action(..., mode="inprocess")`.

## Routes

| Path | Actions |
|------|---------|
| `/` | Dashboard (PR4) |
| `/dna` | `dna_list`, `dna_init`, `dna_lock`, `dna_show`, `dna_handoff` |
| `/sequences` | `sequence_list`, `sequence_init`, `sequence_add_clip`, `sequence_show`, `sequence_handoff`, `quota_sequence_estimate` |
| `/quota` | `quota_dashboard`, `quota_sync`, `quota_budget`, `quota_sequence_estimate` |

## Install / run

```bash
pip install -r requirements-nicegui.txt
cinematic-studio web --port 8088
```

## Safety

- Same `validate_answers` / forbidden-token rules as TUI
- Confirm dialogs for ActionSpec `needs_confirm=True`
- No free-form argv from the browser

## Verify

```bash
pytest tests/test_web_nicegui_pages.py tests/test_web_nicegui_dashboard.py -q
```
