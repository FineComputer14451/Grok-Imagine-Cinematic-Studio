# Plate Lock Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Opt-in plate lock gate so `image_to_video` / `reference_to_video` spend requires `plate_status` in {approved, locked}, soft by default.

**Architecture:** Pure `evaluate_plate_lock_readiness` in `tools/plate_readiness.py`. CLI `--strict-plate` on batch run/session; handoff readiness folds plate blockers under `--strict-handoff`. Shot fields only (no required manifest).

**Tech Stack:** Python 3.11+, existing SFW/NSFW CLI, imagine_bridge, handoff_readiness, pytest.

**Design:** [docs/development/superpowers/specs/2026-07-11-plate-lock-readiness-design.md](../specs/2026-07-11-plate-lock-readiness-design.md)

---

## File map

| Path | Action |
|------|--------|
| `tools/plate_readiness.py` | Create |
| `tests/test_plate_readiness.py` | Create |
| `tools/handoff_readiness.py` | Integrate |
| `tests/test_handoff_readiness.py` | Plate cases |
| `tools/imagine_bridge.py` | Stamp plate fields |
| `tools/cli/sfw_commands.py` | plate set/show + `--strict-plate` |
| `tools/cli/nsfw_commands.py` | `--strict-plate` |
| `tools/session_runner.py` | `strict_plate` kwarg |
| Role Cards / skills (thin) | Curator, I2V, sfw-batch |
| `CHANGELOG.md` | Unreleased |

---

### Task 1: Helper + tests (TDD)

- [ ] Write `tests/test_plate_readiness.py` (PL-01–05 cases)
- [ ] Implement `tools/plate_readiness.py`
- [ ] `pytest tests/test_plate_readiness.py -v`

### Task 2: Handoff integration

- [ ] Stamp `plate_status` / optional plate fields from subject in `build_agent_mode_handoff` / core content
- [ ] Call plate readiness from `evaluate_imagine_handoff_readiness` for plate-required modes
- [ ] Extend `tests/test_handoff_readiness.py`

### Task 3: CLI batch surfaces

- [ ] `sfw plate set` / `sfw plate show`
- [ ] `--strict-plate` on `sfw run` / `sfw session` and NSFW twins
- [ ] Preflight: evaluate → print → exit 1 if strict and not pass

### Task 4: Docs + CHANGELOG

- [ ] Thin notes on Curator / I2V / sfw-batch skill or Role Card
- [ ] CHANGELOG Unreleased bullet

### Task 5: Verify

- [ ] `pytest tests/test_plate_readiness.py tests/test_handoff_readiness.py -q`
- [ ] Smoke: `python tools/cinematic_studio_cli.py sfw --help` (or plate help)

---

*Plate Lock Readiness implementation plan — 2026-07-11*
