# Design: CLI TUI Full Cockpit (v2)

**Date:** 2026-07-19  
**Topic:** Production workflow suite inside `cinematic-studio ui` (Textual)  
**Status:** Design approved — ready for implementation planning  
**Depends on:** v1 TUI ([2026-07-19-cli-interactive-tui-design.md](./2026-07-19-cli-interactive-tui-design.md)) — shipped  
**Approach:** Form screens + pure argv mappers + confirm → existing `run_cli_command` / CLI

## Summary of Decisions

| Decision | Choice |
|----------|--------|
| Scope | **A — Production workflow suite** (forms + confirms; no generation spend) |
| Architecture | **Form screens + shared CLI runner** (extend v1) |
| Bible path | **Non-interactive** `create-bible` args only — never `--wizard` |
| Execution | Reuse **`run_cli_command`** + Command Output screen |
| Navigation | Home key **`c`** → Cockpit menu → form/confirm/output |
| Spend / NSFW run / imagine submit | **Out of scope** |

## Problem

v1 TUI is read-heavy: live dashboard + safe launcher. Operators still leave the TUI for common write workflows (Bible, DNA, sequence scaffold, quota budget). A full cockpit should host those workflows as forms without reimplementing studio business logic or opening generation spend.

## Goals

1. Cockpit menu with five production actions (Bible, DNA init, Sequence init, Quota budget, Models verify).
2. Textual forms with validation and confirm-before-write for mutating actions.
3. Pure `answers → argv` mappers testable without Textual/PTY.
4. Reuse v1 runner, output screen, Home/Launcher/Help.
5. Keep forbidden spend tokens out of cockpit (no `run` / `submit` / wizard / NSFW spend).

## Non-goals (v2)

- Imagine submit, SFW/NSFW batch run, sequence run, quota record
- `create-bible --wizard` or PTY-attached interactive CLI
- DNA lock / multi-anchor / sequence add-clip
- In-process Typer invoke (subprocess remains)
- Streamlit changes
- Replacing the classic CLI

## Architecture

```
Home ──r── refresh snapshot
  │
  ├─ l ── Launcher (v1 safe read-only list)
  ├─ c ── Cockpit menu
  │         ├─ Create Bible      → Form → Confirm → CLI
  │         ├─ DNA init          → Form → Confirm → CLI
  │         ├─ Sequence init     → Form → Confirm → CLI
  │         ├─ Quota budget      → Form → Confirm → CLI
  │         └─ Models verify     → run immediately (read-only)
  └─ ? / q ── help / quit
```

### Principles

1. **Thin TUI** — forms collect fields only; no second Bible/DNA schema.
2. **Argv mappers** — pure functions in `forms.py`; unit-tested.
3. **Execute** via existing `run_cli_command` + `CommandOutputScreen`.
4. **Confirm** before any write (Bible, DNA, sequence, budget).
5. **Models verify** may run without a form (read-only); optional confirm not required.
6. **Never** pass `--wizard` or launcher-forbidden spend tokens from cockpit.

### Package layout (additive)

```
tools/cli/tui/
  catalog.py       # v1 launcher unchanged; optional COCKPIT_ACTION ids
  forms.py         # NEW: WorkflowSpec, validate_answers, answers_to_argv, summarize_action
  screens.py       # + CockpitMenuScreen, FormScreen, ConfirmScreen
  widgets.py       # optional; form error banner helpers if needed
  runner.py        # unchanged contract
  app.py           # bind c → cockpit; help CSS as needed
```

## Cockpit actions

| id | Label | Form | CLI |
|----|--------|------|-----|
| `bible_create` | Create Production Bible | yes | `create-bible TITLE --genre … --chat-model … --video-model … -o …` |
| `dna_init` | Init Character DNA | yes | `dna init NAME` + optional DNA flags |
| `sequence_init` | Init Sequence | yes | `sequence init NAME -d SECS` + optional `-g` |
| `quota_budget` | Set Quota Budget | yes | `quota budget --tier …` + optional `--remaining` |
| `models_verify` | Models Verify | no | `models verify` |

## Form fields

### bible_create

| key | required | default |
|-----|----------|---------|
| `title` | yes | — |
| `genre` | no | `Cinematic` |
| `chat_model` | no | `grok-4.5` |
| `video_model` | no | `grok-imagine-video` |
| `output` | no | `production_bible.json` |

Argv:

```text
["create-bible", <title>, "--genre", <genre>, "--chat-model", <chat>,
 "--video-model", <video>, "-o", <output>]
```

### dna_init

| key | required | default |
|-----|----------|---------|
| `name` | yes | — |
| `core` | no | `""` |
| `facial` | no | `""` |
| `hair` | no | `""` |
| `clothing` | no | `""` |
| `emotion` | no | `""` |

Argv: `["dna", "init", <name>]` plus `--core` / `--facial` / `--hair` / `--clothing` / `--emotion` only when non-empty.

### sequence_init

| key | required | default |
|-----|----------|---------|
| `name` | yes | — |
| `duration` | no | `60` |
| `genre` | no | `""` |

Argv: `["sequence", "init", <name>, "-d", <duration>]` plus `["-g", <genre>]` if genre non-empty.  
`duration` must parse as positive int.

### quota_budget

| key | required | default |
|-----|----------|---------|
| `tier` | yes | `supergrok_pro` |
| `remaining` | no | empty → omit flag |

Argv: `["quota", "budget", "--tier", <tier>]` plus `["--remaining", <remaining>]` if remaining set.  
Valid tiers: `supergrok_pro`, `supergrok_heavy`, `custom` (match `quota_optimizer.SUBSCRIPTION_TIERS`).

## Pure API (`forms.py`)

```python
@dataclass(frozen=True)
class FormField:
    key: str
    label: str
    required: bool = False
    default: str = ""
    help: str = ""

@dataclass(frozen=True)
class WorkflowSpec:
    id: str
    label: str
    description: str
    fields: tuple[FormField, ...]  # empty for models_verify
    needs_confirm: bool = True

COCKPIT_WORKFLOWS: dict[str, WorkflowSpec]

def validate_answers(workflow_id: str, answers: dict[str, str]) -> list[str]:
    """Empty list = ok; else human-readable errors."""

def answers_to_argv(workflow_id: str, answers: dict[str, str]) -> list[str]:
    """Raises ValueError if invalid; callers should validate first."""

def summarize_action(workflow_id: str, answers: dict[str, str]) -> str:
    """Human summary for ConfirmScreen (includes argv preview)."""
```

Forbidden in any cockpit argv: `--wizard`, `run`, `submit`, `record`, `cancel`, `declutter` (same spirit as v1 `FORBIDDEN_ARGV_TOKENS`; assert in tests).

## Screens and keys

### New screens

| Screen | Role |
|--------|------|
| **CockpitMenuScreen** | List of 5 workflows; Enter selects |
| **FormScreen** | Stacked inputs per field; Submit / Cancel |
| **ConfirmScreen** | Summary + argv; `y`/Enter run, `n`/Esc cancel |

Reuse: Home, Launcher, CommandOutput, Help.

### Bindings

| Key | Action |
|-----|--------|
| `c` | Open Cockpit (from Home; prefer global if easy) |
| Enter | Select / submit / confirm |
| Esc | Back / cancel |
| `y` / `n` | Confirm run / cancel |
| `r` `l` `h` `?` `q` | Unchanged from v1 |

Help overlay text includes Cockpit (`c`) and form confirm keys.

### Form UX

- Single screen with one input per field (top→bottom focus).
- Defaults pre-filled from `FormField.default`.
- On Submit: `validate_answers`; if errors, stay on form with banner; else push Confirm.
- Confirm runs `run_cli_command(answers_to_argv(...))` then push Command Output.
- Cancel / Esc from Form → Cockpit; from Confirm → Form (or Cockpit if no form).
- After Output dismiss: return to Cockpit (not auto-close app).
- Home snapshot refresh remains manual/`r`/interval only when Home is focused.

### models_verify

- No form: selecting from Cockpit runs `["models", "verify"]` immediately (or via thin Confirm with empty answers). Prefer **immediate run** for speed; document in help.

## Error handling

| Case | Behavior |
|------|----------|
| Validation fail | Form stays; show error list |
| Confirm cancel | Pop to form or Cockpit |
| CLI fail / timeout | Output screen; app stays up |
| Unknown workflow id | Pure layer raises / UI skips |

## Testing

| File | Coverage |
|------|----------|
| `tests/test_tui_forms.py` | All workflows: happy argv; missing required; invalid tier/duration; no forbidden tokens; no `--wizard` |
| Existing TUI tests | Remain green |
| CLI smoke | `ui --help` still documents interactive UI (optional mention of cockpit in help string if short) |

No mandatory PTY/Textual pilot E2E in CI.

## Documentation

- README under `cinematic-studio ui`: note Cockpit (`c`) workflows.
- Optional CHANGELOG on next release cut (not required by this design alone).

## Success criteria

1. `c` opens Cockpit with five actions.
2. Bible, DNA, Sequence, Budget: form → validate → confirm → real CLI → output.
3. Models verify runs from Cockpit without a multi-field form.
4. No cockpit path emits `--wizard` or generation spend commands.
5. Pure form unit tests pass without `App.run()`.
6. v1 launcher/dashboard behavior preserved.

## Implementation sketch

1. `forms.py` + `test_tui_forms.py` (TDD).
2. CockpitMenuScreen + key `c` + Help update.
3. FormScreen + ConfirmScreen wired to runner.
4. models_verify path.
5. README + suite green.

## Open points resolved

| Question | Resolution |
|----------|------------|
| Scope A vs B vs C | A — workflows without spend |
| Architecture | Forms + argv + subprocess |
| Bible wizard in TUI | No — direct create-bible only |
| models_verify confirm | Immediate run (no form) |
