# Design: CLI TUI Cockpit v3 — Scaffold Expansion

**Date:** 2026-07-19  
**Topic:** Expand `cinematic-studio ui` Cockpit with more **non-spend** production scaffold actions  
**Status:** Implemented (registry + forms + tests; still no spend)  
**Depends on:** v2 cockpit ([2026-07-19-cli-tui-full-cockpit-design.md](./2026-07-19-cli-tui-full-cockpit-design.md)) + post-v2 polish (`6e926b2`: I1 re-confirm fix, I2 async workers, M1/M4 form UX)  
**Approach:** Extend unified `ActionSpec` registry + existing Form → Confirm → Running → Output path

## Summary of Decisions

| Decision | Choice |
|----------|--------|
| Scope | **Scaffold + read-only only** — still no generation spend |
| Architecture | Same as v2: pure argv mappers in `actions.py`, Textual forms, `run_action` worker |
| Navigation | Home `c` → Cockpit (grouped list) · Home `l` → Launcher (more read-only) |
| Spend / wizard / NSFW run / imagine submit | **Still out of scope** |
| Async | Reuse `RunningScreen` (I2) for all CLI execution |
| Stack safety | Reuse confirm-form dismiss (I1) for every mutating confirm |

## Problem

v2 Cockpit can create a Bible, init DNA, init a sequence, and set quota budget — but operators still drop to the classic CLI for the **next** scaffold steps (lock DNA, add sequence clips, handoff packets, validate, cost estimate). Those steps do not spend Imagine credits and fit the allowlisted runner model.

## Goals

1. Add **mutating scaffold** cockpit actions that already exist on the CLI without `run` / `submit` / `record` / `--wizard`.
2. Add **read-only** launcher (or cockpit) actions useful during setup: `validate`, `stack`, `dna show`, `sequence show`, `sequence estimate-cost` / `quota estimate`.
3. Keep a single `ACTIONS` registry; new entries declare `surfaces` + `fields` + `needs_confirm`.
4. Preserve forbidden-token gate (`--wizard`, `run`, `submit`, `record`, `cancel`, `declutter`).
5. Group cockpit menu for scanability (Setup · DNA · Sequence · Quota · Health).

## Non-goals (v3)

- `sequence run`, `sfw run`, `nsfw run`, `imagine submit`, `quota record`
- `create-bible --wizard` or any PTY wizard
- DNA extract from images (needs media tooling / multi-file UX)
- Polish / deliver / color-grade writes (post pipeline; later v4)
- Streamlit changes
- In-process Typer invoke

## Architecture

```
Home
  l → Launcher (read-only; expanded)
  c → Cockpit (mutating + a few health checks)
        Setup:     bible_create · quota_budget
        DNA:       dna_init · dna_lock · dna_handoff
        Sequence:  sequence_init · sequence_add_clip · sequence_handoff
        Health:    models_verify · validate · stack  (immediate / no confirm)
```

Execution path (unchanged from post-polish v2):

```
Form? → Confirm? → RunningScreen (worker) → CommandOutput → parent menu
```

## New / extended actions

### Mutating (cockpit · confirm)

| id | Label | CLI argv pattern |
|----|--------|------------------|
| `dna_lock` | Lock Character DNA | `dna lock <name>` |
| `dna_handoff` | DNA Identity Handoff | `dna handoff <name>` [optional flags if CLI supports] |
| `sequence_add_clip` | Add Sequence Clip | `sequence add-clip <name> -p … -d …` + optional `-r -a --ref -t --action --emotion --dialogue` |
| `sequence_handoff` | Sequence Clip Handoff | `sequence handoff <name>` + clip selector if required by CLI |

Verify exact flags during implementation (`--help` is source of truth). Omit empty optional flags (same as v2 DNA init).

### Read-only (launcher and/or cockpit · no confirm)

| id | Label | CLI argv |
|----|--------|----------|
| `validate` | Studio validate | `validate` |
| `stack` | Model stack | `stack` |
| `dna_show` | Show DNA | `dna show <name>` — **form** for name only; treat as read (confirm optional; prefer no confirm) |
| `sequence_show` | Show sequence | `sequence show <name>` — form for name only |
| `quota_estimate` | Quota estimate (plan) | `quota estimate` + fields that match CLI (duration/clips/model) — **estimate only**, never `record` |

`dna_show` / `sequence_show` need a form but **not** spend; `needs_confirm=False` is acceptable (read-only side effect).

### Existing (unchanged)

`bible_create`, `dna_init`, `sequence_init`, `quota_budget`, `models_verify`, full launcher list from v1/v2.

## Form fields (proposed)

### dna_lock / dna_handoff

| key | required | default |
|-----|----------|---------|
| `name` | yes | — |

Argv: `["dna", "lock", name]` / `["dna", "handoff", name]` (+ flags only if present in CLI).

### sequence_add_clip

| key | required | default |
|-----|----------|---------|
| `name` | yes | sequence name/slug |
| `prompt` | yes | — |
| `duration` | no | `10` (int, positive) |
| `recap` | no | omit |
| `aspect` | no | `16:9` |
| `ref` | no | omit |
| `transition` | no | `invisible_edit` |
| `action` | no | omit |
| `emotion` | no | omit |
| `dialogue` | no | omit |

Argv built via `flag=` / `omit_if_empty` on `FormField` (registry already supports this).

### sequence_handoff

Inspect CLI; likely `sequence handoff NAME` plus `--clip` or index. Design: required `name` + `clip` (string id or index as CLI expects).

### quota_estimate

Map only to `quota estimate` / `quota clip` / `quota sequence` — **never** `quota record`. Prefer `quota sequence` when a sequence name is provided; else simple clip estimate fields.

## Menu grouping (display only)

Keep `COCKPIT_ORDER` as a flat ordered tuple; optional `ActionSpec.group: str` for Label separators in `CockpitMenuScreen`:

- `setup` · `dna` · `sequence` · `quota` · `health`

Launcher order appends: `validate`, `stack` after `models_verify` (or at end before plugin list).

## Safety

1. Extend tests: no new action emits forbidden tokens.  
2. Static allowlist remains **field-less only**; form actions use `run_action` only.  
3. Double-submit still blocked via Confirm `_started` + RunningScreen busy.  
4. Mutating actions still use `dismiss_confirm_form=True`.

## Testing

| File | Coverage |
|------|----------|
| `tests/test_tui_forms.py` / actions tests | New argv happy paths + validation |
| `tests/test_tui_confirm_stack.py` | Unchanged stack helpers still green |
| `tests/test_tui_actions.py` | New IDs in surfaces; forbidden tokens |

No PTY E2E required.

## Documentation

- README `ui` bullet: mention DNA lock / add-clip / validate if shipped.  
- CHANGELOG under Unreleased when implemented.  
- Optional implementation plan: `docs/development/superpowers/plans/2026-07-19-cli-tui-cockpit-v3-scaffold-implementation.md`.

## Success criteria

1. Cockpit can lock DNA and add a sequence clip without leaving the TUI.  
2. Launcher can run `validate` and `stack`.  
3. Zero cockpit path can emit spend tokens or `--wizard`.  
4. All new mappers unit-tested; existing 39+ TUI tests remain green.  
5. RunningScreen still used for every CLI invocation from UI.

## Implementation sketch

1. TDD: argv tests for `dna_lock`, `sequence_add_clip`, `validate`, `stack`.  
2. Register `ActionSpec`s + order/group.  
3. Wire cockpit/launcher lists (separator labels if group present).  
4. README + CHANGELOG.  
5. Manual pilot: Home → c → DNA lock / add-clip → Output → Esc → Cockpit.

## Open points

| Question | Default if unresolved |
|----------|------------------------|
| Confirm on read-only show forms? | No confirm |
| Group headers in ListView? | Yes if cheap; else flat order with naming prefixes |
| `quota_estimate` complexity | Ship `quota sequence <name>` only first |
| `sequence_handoff` clip picker | Single text field matching CLI |
