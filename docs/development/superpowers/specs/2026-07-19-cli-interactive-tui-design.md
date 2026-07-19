# Design: Interactive CLI Terminal UI (Textual)

**Date:** 2026-07-19  
**Topic:** Terminal TUI for `cinematic-studio` — live dashboard + command launcher  
**Status:** Design approved — ready for implementation planning  
**Target version:** Studio minor/patch after implementation (no VERSION bump required by this design alone)  
**Approach:** Textual app (`cinematic-studio ui`) over existing `build_studio_dashboard()` and Typer commands

## Summary of Decisions

| Decision | Choice |
|----------|--------|
| Surface | **In-terminal TUI** (not Streamlit, not REPL-only) |
| v1 scope | **Studio launcher + live dashboard** (read-heavy; actions launch existing CLI) |
| Framework | **Textual** (Approach 1) |
| Data source | **`cli.dashboard.build_studio_dashboard()`** only for Home panels |
| Command execution | **Subprocess** to CLI (`cinematic-studio` / `tools/cinematic_studio_cli.py`) |
| Wizards / spend / NSFW run | **Out of scope** for v1 launcher |
| Optional dep | `textual` required for `ui`; clear install error if missing |
| Streamlit / existing `dashboard` | **Unchanged** |

## Problem

The studio CLI is powerful but command-oriented: users must remember subcommands and flags. There is already:

- `cinematic-studio dashboard` (+ `--watch` via Rich Live) for snapshots
- Streamlit `web_ui/` for browser dashboards
- Interactive bible wizard on TTY only

There is no **keyboard-driven in-terminal product surface** that combines a live studio snapshot with a safe command launcher. Power users on SSH/Termux/Kali benefit from a TUI that does not require a browser.

## Goals

1. Ship `cinematic-studio ui` that opens a Textual app on a TTY.
2. Show a **Home** screen with live studio data equivalent in content family to `dashboard --compact` / full dashboard panels (project, quota, models health, sequences, DNA, jobs).
3. Provide a **Launcher** of common **safe, non-interactive** CLI commands; run them and show captured output.
4. Keep business logic out of the TUI — reuse `build_studio_dashboard()` and existing Typer commands.
5. Fail gracefully: non-TTY, missing Textual, snapshot errors, failed subprocesses.
6. Stay testable without full PTY E2E in CI (catalog + pure builders + `--help` smoke).

## Non-goals (v1)

- In-TUI Production Bible wizard, DNA forms, or multi-step spend flows
- NSFW batch run / explicit generation from the launcher
- Replacing Streamlit or rewriting Typer command implementations
- Mouse-only UX requirements
- Editing project state or files in-place inside the TUI
- Full interactive PTY attach for long-running interactive subcommands

## Architecture

```
cinematic-studio ui
        │
        ▼
┌─────────────────────────────┐
│  tools/cli/tui/app.py       │  Textual App (StudioTUI)
│  screens: Home / Launcher   │
└─────────────┬───────────────┘
              │ reads
              ▼
┌─────────────────────────────┐
│  cli.dashboard              │  build_studio_dashboard()  (unchanged contract)
│  models / project_state /…  │  existing tools/*
└─────────────┬───────────────┘
              │ actions (v1)
              ▼
┌─────────────────────────────┐
│  runner.py → subprocess     │  python …/cinematic_studio_cli.py <argv>
│  existing Typer commands    │  status · dashboard · models · quota · dna · …
└─────────────────────────────┘
```

### Principles

1. **Single source of truth** — Home widgets call `build_studio_dashboard()` only (same snapshot as CLI/JSON).
2. **Thin TUI** — Textual owns layout, keys, refresh; no production business rules in `tools/cli/tui/`.
3. **Optional runtime dep** — if Textual is missing, exit non-zero with install hint.
4. **TTY required** — refuse non-interactive pipes/redirects (same spirit as `create-bible --wizard`).
5. **Escape hatch** — `q` / Ctrl+C exit cleanly; command failures never tear down the app process unexpectedly.

## Package layout

```
tools/cli/tui/
  __init__.py       # public run_tui() export
  app.py            # StudioTUI App, run_tui(interval=…)
  screens.py        # Home, Launcher, CommandOutput, Help overlay/screen
  widgets.py        # snapshot dict → Textual widgets / Static markdown panels
  catalog.py        # launcher entries: id, label, description, argv
  runner.py         # resolve CLI python path + subprocess capture
```

Registration: root Typer command `ui` via `tools/cli/studio_commands.py` **or** dedicated `tools/cli/tui_commands.py` registered from `cinematic_studio_cli.py` — prefer **`tui_commands.py`** to keep studio overview file focused.

## Screens and keybindings

### Screens

| Screen | Role |
|--------|------|
| **Home** (default) | Live dashboard panels from `build_studio_dashboard()` |
| **Launcher** | Scrollable list of catalog commands; Enter runs selected |
| **Command output** | Captured stdout/stderr + exit code; Esc dismisses |
| **Help** | Binding cheat-sheet overlay or simple screen |

### Global keys

| Key | Action |
|-----|--------|
| `r` | Refresh snapshot immediately |
| `l` | Open Launcher |
| `h` | Home (when not already there) |
| Esc | Back (Launcher/Output/Help → previous or Home) |
| `q` | Quit |
| `?` | Help |

### Refresh policy

- Auto-refresh Home every **5 seconds** by default.
- CLI flag: `--interval FLOAT` (minimum 1.0s).
- Manual `r` always triggers an immediate rebuild.
- Implementation may use Textual `set_interval` / workers; sync rebuild is acceptable if snapshot remains fast.

## Launcher catalog (v1)

Only **non-interactive, safe-by-default** commands. Catalog is data in `catalog.py` (not scraped from Typer at runtime in v1).

| Label | argv |
|-------|------|
| Studio status | `["status"]` |
| Dashboard (compact) | `["dashboard", "--compact"]` |
| Models list | `["models", "list"]` |
| Models verify | `["models", "verify"]` |
| Quota dashboard | `["quota", "dashboard"]` |
| DNA list | `["dna", "list"]` |
| Sequences list | `["sequence", "list"]` |
| Imagine jobs | `["imagine", "list"]` |
| Plugin list | `["plugin", "list"]` |

**Explicitly excluded from v1 catalog:** `create-bible --wizard`, `sfw run`, `nsfw` spend/run, `sequence run`, `imagine submit`, any command requiring positional project/shot IDs without defaults.

### Command execution

1. Resolve interpreter + CLI entry:
   - Prefer `sys.executable` + `tools/cinematic_studio_cli.py` relative to repo root (same pattern as tests).
   - Optionally fall back to `cinematic-studio` on `PATH` if present.
2. `subprocess.run(..., capture_output=True, text=True, cwd=repo_root, timeout=…)`.
3. Default timeout: **60s** (configurable constant); on timeout show message, do not hang TUI forever.
4. Present exit code + combined or separate stdout/stderr on Command Output screen.
5. On success or failure, Esc returns to Launcher (if launched from there).

## CLI surface

```text
cinematic-studio ui [--interval FLOAT]
```

- Help: “Interactive terminal UI — live studio dashboard + command launcher”
- No `--json` (human TUI only)
- Exit codes:
  - `0` — normal quit
  - `1` — non-TTY, missing Textual, or fatal startup error before app runs

### Non-TTY and missing dependency messages

Match studio tone (Rich console when available):

- Non-TTY: `cinematic-studio ui requires an interactive terminal.`
- Missing Textual: `Textual is required for the TUI. Install with: pip install textual` (or point at `requirements.txt`).

## Widgets / rendering

- Map snapshot sections already produced by `build_studio_dashboard()` into Textual `Static` / `DataTable` / `Label` panels.
- Reuse field names from the existing dashboard dict (`project`, `studio`, `quota`, `sequences`, `characters`, jobs summary, etc.) so Streamlit/CLI stay aligned.
- Do **not** duplicate aggregation logic in `widgets.py`.
- Optional: thin adapter that turns existing Rich renderables into plain text via `Console.export_text` if faster for v1 — acceptable, but prefer structured widgets for key metrics.

## Error handling

| Case | Behavior |
|------|----------|
| Non-TTY | Exit 1 before App.run |
| Textual not installed | Exit 1 + install hint |
| Snapshot build raises | Home shows error panel; app stays up; `r` retries |
| Subprocess non-zero | Output screen shows code + text |
| Subprocess timeout | Output screen shows timeout message |
| Ctrl+C during app | Clean quit (Textual default / handled) |

## Testing

| Test | Assertion |
|------|-----------|
| `tests/test_tui_catalog.py` | Catalog non-empty; no argv contains `--wizard`; no empty argv lists |
| `tests/test_tui_widgets.py` | Build panels from real or fixture snapshot without raise |
| CLI smoke | `ui --help` returns 0 and mentions interactive/TUI |
| Import smoke | `from cli.tui.app import run_tui` (or guarded import path) works when Textual installed |
| CI | No mandatory full-screen Textual pilot run |

Dev dependency: ensure `textual` is listed so pytest environments that import TUI modules succeed (`requirements.txt` primary; `requirements-dev.txt` if split later).

## Dependencies

Add to root `requirements.txt` (used by CLI + Streamlit cloud):

```
textual>=0.47.0
```

(Exact lower bound may be adjusted during implementation to a current stable; pin only if CI requires it.)

## Documentation touchpoints (implementation plan, not this design alone)

- README CLI section: one-liner for `cinematic-studio ui`
- Optional CHANGELOG entry under Unreleased / next release
- AGENTS.md only if “Common Workflows” should mention TUI (optional)

## Success criteria

1. On a TTY with Textual installed, `cinematic-studio ui` opens Home with live project/quota/model/sequence-related data from `build_studio_dashboard()`.
2. Launcher runs every catalog command and displays output without crashing the TUI.
3. `r`, `l`, Esc, `q`, `?` behave as specified.
4. Non-TTY and missing-Textual paths exit non-zero with clear messages.
5. Existing `dashboard`, `dashboard --watch`, and Streamlit paths remain unchanged and green in existing tests.

## Implementation sketch (for planning skill)

1. Add `textual` dependency.
2. Scaffold `tools/cli/tui/` with catalog, runner, widgets, screens, app.
3. Register `ui` command; guard TTY + import.
4. Wire Home to snapshot + interval refresh.
5. Wire Launcher + Command Output.
6. Tests for catalog/widgets/help smoke.
7. README one-liner.

## Open points resolved in design

| Question | Resolution |
|----------|------------|
| Textual vs Rich Live menu | Textual |
| Full cockpit vs launcher | Launcher + dashboard only |
| In-process Typer invoke vs subprocess | Subprocess for isolation and fidelity to real CLI |
| Auto-refresh default | 5s |
| Interactive wizards in TUI | Deferred post-v1 |
