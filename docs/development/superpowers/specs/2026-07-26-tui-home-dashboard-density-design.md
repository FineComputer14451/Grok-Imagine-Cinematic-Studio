# Design: TUI Home Dashboard Density

**Date:** 2026-07-26  
**Topic:** Dense multi-panel Home for `cinematic-studio ui`  
**Status:** Design approved — ready for implementation planning  
**Target version:** Studio patch after implementation (no VERSION bump required by this design alone)  
**Approach:** Multi-panel Textual widgets over existing `build_studio_dashboard()` (Approach A)

## Summary of Decisions

| Decision | Choice |
|----------|--------|
| Surface | **CLI TUI** (`cinematic-studio ui`) only — Streamlit unchanged |
| Focus | **Home dashboard density** (scannable ops board) |
| Layout style | **Multi-panel widgets** (not denser single Markdown blob) |
| Data source | **`build_studio_dashboard()`** + existing `quota_alignment` attach on refresh |
| Chain QA | **Dedicated panel** from `snapshot["chain_qa"]`; rollup also on status strip |
| Recent jobs | **Show when non-empty**; hide section if no jobs |
| Wide layout | **Two-column Quota \| Studio** when width allows; single-column fallback on narrow terminals |
| Snapshot API | **Unchanged** (no plate/motion readiness enrich in this pass) |
| Cockpit / launcher | **Unchanged** |

## Problem

Home is a single Markdown document (`format_home_markdown` → one `#home-body` widget). Power users must scroll a wall of prose to answer production-critical questions:

- Are models compatible?
- What is quota risk / ledger alignment?
- How many DNA profiles are locked?
- Any chain QA no-gos?
- Which sequences exist and how healthy are they?

The Rich CLI dashboard (`cinematic-studio dashboard`) already uses multi-panel tables; the TUI Home does not match that density.

## Goals

1. Replace Home’s single Markdown body with **scannable panels** (status strip + quota + studio + sequences + chain QA + characters + optional jobs).
2. Keep business logic out of the TUI: still call **`build_studio_dashboard()`** only for content (plus `quota_alignment` as today).
3. Preserve pure formatters in `widgets.py` (testable without Textual / PTY).
4. Keep existing keybindings and navigation (`r` / `s` / `l` / `c` / `?` / `q`, auto-refresh on Home).
5. Explicit empty states for sequences, chain QA, characters, and jobs.
6. Within ~3 seconds on Home, an operator can answer: models OK?, quota risk?, DNA locks?, any QA no-go?, which sequences exist?

## Non-goals

- Extending `build_studio_dashboard()` with plate/motion/handoff readiness (Approach B — future)
- New cockpit or launcher actions
- Streamlit Web UI changes
- Imagine spend, wizard, or forbidden argv paths
- Full PTY E2E tests in CI
- Mandatory VERSION / marketing bump

## Architecture

```
cinematic-studio ui
        │
        ▼
┌─────────────────────────────┐
│  tools/cli/tui/app.py       │  CSS for panel chrome / risk colors
│  screens.HomeScreen         │  multi-widget compose + refresh
└─────────────┬───────────────┘
              │ reads
              ▼
┌─────────────────────────────┐
│  cli.dashboard              │  build_studio_dashboard()  (contract unchanged)
│  quota_sync (optional)      │  ledger_recon_alignment() → snap["quota_alignment"]
└─────────────┬───────────────┘
              │ pure format
              ▼
┌─────────────────────────────┐
│  cli.tui.widgets            │  strip + panel string/row builders
└─────────────────────────────┘
```

### Principles

1. **Single source of truth** — Home panels consume the same snapshot dict as CLI dashboard/JSON.
2. **Thin TUI** — Textual owns layout, keys, refresh; no production business rules in `tools/cli/tui/`.
3. **Pure formatters** — `widgets.py` must not import Textual; screens map formatter output → widgets.
4. **Backward-compatible helpers** — keep `format_error_panel` / `format_form_errors`; either retire `format_home_markdown` behind a thin adapter or keep it as a debug/compat path that concatenates panel formatters (tests updated either way).
5. **Fail soft** — snapshot errors still show a single error panel; partial empty lists show empty-state copy, not exceptions.

## Package impact

```
tools/cli/tui/
  app.py        # extend CSS (panel borders, risk classes, strip)
  screens.py    # HomeScreen compose + action_refresh multipanel update
  widgets.py    # split formatters; status strip + panels + empty states
```

No new modules required unless formatters grow large enough to warrant `widgets_home.py` (optional; prefer single `widgets.py` first).

## Home layout

```
┌ Header (clock) ──────────────────────────────────────────────────┐
│ #status-strip                                                     │
│   Project · Bible · Models · Risk · DNA locks · QA rollup         │
├────────────────────────────┬─────────────────────────────────────┤
│ #panel-quota               │ #panel-studio                       │
│ Tier, spent, left, risk,   │ Agents, skills, role cards,         │
│ recon, ledger alignment    │ models, chat/video stack            │
├────────────────────────────┴─────────────────────────────────────┤
│ #panel-sequences   name · clips · health · target duration       │
│ #panel-chain-qa    sequence · go · no-go · status · clip_count   │
│ #panel-characters  name · slug · status                          │
│ #panel-jobs        (only if recent_jobs non-empty)               │
│ #hints             r refresh · s quota sync · l · c · ? · q      │
└ Footer ──────────────────────────────────────────────────────────┘
```

### Status strip (rollup)

| Signal | Source | Display |
|--------|--------|---------|
| Project title | `project.title` | short name |
| Bible | `project.has_bible` | loaded / not started |
| Models | `studio.models_compatible` | OK / ISSUES |
| Risk | `quota.risk_level` | low / medium / high / critical (CSS color) |
| DNA locks | `production.identity_locked` / `production.characters` | e.g. `2/4 locked` |
| Chain QA rollup | sum go/no-go over `chain_qa` list | e.g. `QA 5 go · 1 no-go` |

### Panel details

| Panel | Source | Empty state |
|-------|--------|-------------|
| Quota | `quota` + `quota_alignment` | N/A (always show tier/risk with “—” when missing) |
| Studio | `studio` | N/A |
| Sequences | `sequences` | “No sequences yet” |
| Chain QA | `chain_qa` | “No sequence QA data” |
| Characters | `characters` | “No DNA profiles yet” |
| Jobs | `recent_jobs` | **omit panel entirely** if empty |

**Sequences vs Chain QA:** Sequences show structural fields only (name, clips, health, target_duration). Chain QA owns go/no-go and `chain_qa_status` from the dedicated `chain_qa` summaries (join by slug only if needed for labels; prefer fields already on each summary row: `sequence_name`, `slug`, `go_count`, `no_go_count`, `chain_qa_status`, `clip_count`).

### Responsive columns

- Prefer a horizontal container for Quota | Studio when the terminal is wide enough for readable dual panes.
- On narrow terminals, stack Quota above Studio (single column). Implementation may use Textual layout primitives or a simple always-stacked layout if dual-column CSS is fragile; dual-column is preferred but not a ship blocker if single-column density is already clearly better than Markdown.

## Refresh policy

- Unchanged: app interval (default 5s) calls `HomeScreen.action_refresh` only when Home is the active screen.
- Refresh rebuilds all panel text from a fresh snapshot (full repaint; correct and simple).
- Keys `r` and `s` unchanged (`s` still launches async `quota_sync` via RunningScreen).

## Widget technology choice

| Option | Use when |
|--------|----------|
| **`Static` + preformatted text** (recommended default) | Simpler interval updates; formatters return multi-line strings; matches pure-widget tests |
| **`DataTable`** | Only if implementer prefers native selection; must still keep pure row builders for unit tests |

Default recommendation: **Static panels** with monospace-friendly columns (pad with spaces or use simple `|` separators). Avoid Markdown-only home body.

## CSS / visual polish (minimal)

In `StudioTUI.CSS`:

- Panel titles / borders via existing `$accent` / `$surface` tokens
- Risk classes: `.risk-low`, `.risk-medium`, `.risk-high`, `.risk-critical` (or status classes on strip segments)
- Muted secondary lines for timestamps and hints
- No heavy animation; keep Termux/SSH-friendly

Exact colors may follow Textual theme variables rather than hard-coded hex.

## Testing

| Test | Expectation |
|------|-------------|
| `tests/test_tui_widgets.py` | Cover strip formatter, each panel formatter, empty states, risk/models badges, chain QA rollup, alignment line |
| Existing `test_tui_*` | Remain green (screens/actions/runner/forms) |
| Live snapshot test | Optional: `build_studio_dashboard()` → all formatters return non-empty strip/quota/studio |
| PTY E2E | Not required |

Compat: if `format_home_markdown` is kept, it may concatenate denser panel formatters so older tests still pass, **or** tests migrate fully to new APIs (`format_status_strip`, `format_quota_panel`, …). Prefer explicit new functions + updated tests over a permanent dual path.

## Documentation

- Short note in `CHANGELOG.md` under Unreleased / next patch: denser TUI Home multi-panel dashboard.
- README already documents `cinematic-studio ui`; no structural README rewrite required unless key hints change.

## Success criteria

1. Home is multi-panel (not one Markdown wall).
2. Status strip answers models / risk / DNA locks / QA rollup without scrolling.
3. Dedicated Chain QA panel uses `snapshot["chain_qa"]`.
4. Snapshot contract unchanged; no new spend surfaces.
5. Widget unit tests cover formatters and empty states.
6. Manual: `cinematic-studio ui` remains usable on a typical 80×24 and wider terminal.

## Follow-ups (out of scope)

- **Approach B:** readiness rollup on snapshot (plate/motion/handoff aggregates).
- Cockpit shortcuts from Home (e.g. jump to sequence handoff).
- Align Streamlit Dashboard page visual density with TUI strip vocabulary.

## Implementation notes for planning

1. Add pure formatters in `widgets.py` first + unit tests (TDD-friendly).
2. Rewire `HomeScreen.compose` / `action_refresh`.
3. Extend `app.py` CSS lightly.
4. Run `pytest tests/test_tui_*.py` (and full suite if practical).
5. Manual smoke on TTY: `python tools/cinematic_studio_cli.py ui` or `cinematic-studio ui`.

---

*Approved design — CLI TUI Home density · 2026-07-26 · Approach A multi-panel + dedicated Chain QA*
