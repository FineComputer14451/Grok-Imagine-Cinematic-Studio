# Operator UX Phase 1 — Orient + Health Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship Phase 1 of the Operator UX north-star — journeys **J1 Orient** and **J6 Quota/Health** across TUI + Streamlit + shared contract tests + short docs.

**Architecture:** Reuse pure control-plane helpers (`strip_severity`, `collect_home_alerts`, dashboard snapshot). Surfaces only launch allowlisted health actions and display the same severity/attention vocabulary.

**Tech Stack:** Python, Textual TUI, Streamlit, pytest, existing `run_cli` / TUI action registry

## Global Constraints

- Spec: `docs/development/superpowers/specs/2026-07-26-operator-ux-north-star-design.md` Phase 1 only
- No free-form spend; no wizard from TUI
- No J7/J8 UI; no full readiness schema expansion
- Shared severity/attention must stay in pure helpers (no duplicate rules in Streamlit)
- Thin surfaces; business logic in `tools/`

## File map

| File | Role |
|------|------|
| `tests/test_control_plane_contract.py` | Contract tests for severity + attention |
| `tools/cli/tui/screens.py` | Home keys for models verify + stack |
| `tools/cli/tui/widgets.py` | Hints text for new keys |
| `web_ui/pages/dashboard.py` | Health action strip (doctor / validate / quota sync) |
| `tools/doctor_checks.py` or doctor report | Optional severity one-liner |
| `docs/guides/Quick_Start_Guide.md` | Operator loop |
| `CHANGELOG.md` | Unreleased note |

---

### Task 1: Control-plane contract tests

**Files:**
- Create: `tests/test_control_plane_contract.py`

- [x] Cover severity levels + attention families from fixtures (`tests/test_control_plane_contract.py`)
- [x] Assert Web `dashboard_ui` uses same severity as TUI widgets for same snap

### Task 2: TUI Home health shortcuts

**Files:**
- Modify: `tools/cli/tui/screens.py`, `widgets.py`, tests

- [x] Keys: `m` models verify, `k` stack
- [x] Update hints + HelpScreen

### Task 3: Streamlit Dashboard health action strip

**Files:**
- Modify: `web_ui/pages/dashboard.py`

- [x] Buttons: Doctor (quick), Validate, Quota sync, Models verify via `rt.run_cli`
- [x] Show output expander; no spend commands

### Task 4: Doctor severity echo + docs

**Files:**
- Modify doctor if cheap; Quick Start; CHANGELOG

- [x] Doctor registry `control_plane` check (severity + attention)
- [x] Operator loop in Quick Start §4
- [x] CHANGELOG + commit
