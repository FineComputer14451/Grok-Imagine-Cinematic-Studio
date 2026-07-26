# Operator UX Phase 2 — Produce + Gate Implementation Plan

> **For agentic workers:** Phase 2 of the Operator UX north-star (J2–J5).

**Goal:** Gate video/extend spend with readiness rollup, chain QA next actions, DNA lock feedback, and handoff packet validate.

**Status:** Implemented (2026-07-26)

## Delivered

| Item | Location |
|------|----------|
| Readiness rollup | `tools/control_plane_readiness.py` → `build_studio_dashboard()["readiness"]` |
| Chain QA next actions | `format_chain_qa_panel` + readiness `next_actions` in attention |
| DNA lock feedback | Web DNA page · TUI `format_produce_gate_next_steps` on CommandOutput |
| Handoff validate CLI | `cinematic-studio handoff validate PATH` |
| TUI action | `handoff_validate` launcher + cockpit |
| Web Tools | Handoff path + Validate button |
| Tests | `tests/test_control_plane_readiness.py` + widget/form updates |

## Non-goals (still Phase 3)

- Parallel Brief UI (J8)
- Delivery polish surface (J7)
- Full plate/motion CLI gates UI (strict flags remain CLI)
