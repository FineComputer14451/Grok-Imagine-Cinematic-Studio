# TUI Home Dashboard Density Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace `cinematic-studio ui` Home’s single Markdown body with a multi-panel ops dashboard (status strip, quota, studio, sequences, dedicated chain QA, characters, optional jobs).

**Architecture:** Pure formatters in `tools/cli/tui/widgets.py` turn `build_studio_dashboard()` snapshots into plain text panels. `HomeScreen` composes Static widgets and refreshes them on interval. No snapshot API changes.

**Tech Stack:** Python 3, Textual, pytest, existing `cli.dashboard.build_studio_dashboard()`

## Global Constraints

- Data only from `build_studio_dashboard()` + optional `quota_alignment` attach (unchanged)
- `widgets.py` must not import Textual
- No spend / wizard / forbidden argv changes
- Keep Home keys: `r` `s` `l` `c` `?` `q`
- Dedicated Chain QA panel from `snapshot["chain_qa"]`
- Omit jobs panel when `recent_jobs` empty
- Spec: `docs/development/superpowers/specs/2026-07-26-tui-home-dashboard-density-design.md`

## File map

| File | Responsibility |
|------|----------------|
| `tools/cli/tui/widgets.py` | Pure panel formatters + compat `format_home_markdown` |
| `tools/cli/tui/screens.py` | Multi-widget `HomeScreen` compose/refresh |
| `tools/cli/tui/app.py` | CSS for panels / risk |
| `tests/test_tui_widgets.py` | Formatter unit tests |
| `CHANGELOG.md` | Unreleased note |

---

### Task 1: Pure panel formatters + tests

**Files:**
- Modify: `tools/cli/tui/widgets.py`
- Modify: `tests/test_tui_widgets.py`

**Interfaces (produce):**
- `format_status_strip(snapshot: dict[str, Any]) -> str`
- `format_quota_panel(snapshot: dict[str, Any]) -> str`
- `format_studio_panel(snapshot: dict[str, Any]) -> str`
- `format_sequences_panel(snapshot: dict[str, Any]) -> str`
- `format_chain_qa_panel(snapshot: dict[str, Any]) -> str`
- `format_characters_panel(snapshot: dict[str, Any]) -> str`
- `format_jobs_panel(snapshot: dict[str, Any]) -> str | None`  # None when empty
- `format_home_hints() -> str`
- `format_home_error(message: str) -> str`  # plain Static error (no Markdown required)
- `format_home_markdown(snapshot)` — keep as concatenation of panels for compatibility

- [x] **Step 1: Expand tests for strip, panels, empty states, rollup**
- [x] **Step 2: Implement formatters in widgets.py**
- [x] **Step 3: `pytest tests/test_tui_widgets.py -v` PASS**
- [x] **Step 4: Commit**

### Task 2: HomeScreen multi-panel layout + CSS

**Files:**
- Modify: `tools/cli/tui/screens.py` (`HomeScreen`)
- Modify: `tools/cli/tui/app.py` (CSS)

**Interfaces (consume):** Task 1 formatters

- [x] **Step 1: Compose Home with Static panels in VerticalScroll**
- [x] **Step 2: action_refresh updates each panel; error path fills error Static**
- [x] **Step 3: CSS for panel titles / strip / muted hints**
- [x] **Step 4: `pytest tests/test_tui_*.py -v` PASS**
- [x] **Step 5: Commit + CHANGELOG note**

---

## Success criteria (from spec)

1. Multi-panel Home (not one Markdown wall)
2. Status strip: models / risk / DNA locks / QA rollup without scrolling
3. Dedicated Chain QA panel
4. Snapshot contract unchanged
5. Widget unit tests green
