# Implementation Plan: Guided Production Bible Wizard

**Date:** 2026-07-09  
**Design:** [docs/superpowers/specs/2026-07-05-guided-production-bible-wizard-design.md](../specs/2026-07-05-guided-production-bible-wizard-design.md)  
**Studio:** v3.6.6  
**Goal:** Ship guided CLI + Web UI bible creation without a second schema or second builder.

## Principles (non-negotiable)

1. **Single Bible owner:** only `build_production_bible` in `tools/cli/production.py` assembles the dict.
2. **No dual schema:** stages produce kwargs (and free-text `notes`), never nested `project.*` / `style.*` / `technicals.*`.
3. **Script-safe CLI:** existing `create-bible "Title" …` stays default and non-interactive.
4. **No new deps:** Rich + Typer + Streamlit only.
5. **No resume / session files** in v1.
6. **Thin UI layers:** CLI and Web own navigation only; pure logic lives in `tools/cli/bible_stages.py`.

## Out of scope (do not implement)

- `BibleWizard` class or parallel `build_bible()`
- `--direct` / making wizard the default for all invocations
- `--resume` or partial session persistence
- DNA init / sequence / quota execution from the wizard
- New top-level Bible JSON keys
- questionary or other prompt libraries
- New Streamlit page module if Production can host the multi-step form cleanly

---

## Work packages

### WP0 — Fixtures & baseline (small, first)

**Why first:** lock the current bible shape so wizard work cannot regress it.

| Task | Detail |
|------|--------|
| 0.1 | Add `tests/test_production_bible.py` covering `build_production_bible` key set and `locked_variables` / `video_pipeline_spec` / `model_stack` presence |
| 0.2 | Snapshot required top-level keys as a frozenset constant in the test (or shared test helper) — wizard tests will assert subset equality against this set |

**Done when:** `pytest tests/test_production_bible.py` green on current code with no wizard yet.

**Files:** `tests/test_production_bible.py` only.

---

### WP1 — Shared stage module (core)

**Module:** `tools/cli/bible_stages.py`  
**Keep under ~200 lines.** Data + pure functions only. No I/O, no Typer, no Streamlit, no project_state.

#### 1.1 Data model

```python
# Conceptual shape (implement with TypedDict or simple dataclasses)
StageField = {
    "key": str,           # answer key, e.g. "title", "genre", "logline"
    "prompt": str,        # human question
    "example": str,       # shown as hint
    "required": bool,
    "default": str | int | None,
}

Stage = {
    "id": str,            # "story" | "genre" | "characters" | "technicals" | "review"
    "title": str,
    "fields": list[StageField],
}
```

#### 1.2 Stage content (5 stages)

| Stage id | Fields (answer keys) | Required |
|----------|----------------------|----------|
| `story` | `title`, `logline` | title |
| `genre` | `genre`, `director_signature`, `complexity` | genre |
| `characters` | `characters_text`, `world_text` | none |
| `technicals` | `target_duration_seconds`, `video_model`, `chat_model`, `tech_notes` | duration |
| `review` | (no collect fields — preview/confirm only) | — |

Defaults: genre `"Cinematic"`, duration `60`, complexity `"Medium"`, video/chat from `models.DEFAULT_*`.

#### 1.3 Pure API

| Function | Contract |
|----------|----------|
| `STAGES: list[Stage]` | Ordered, length 5 |
| `stage_by_id(id) -> Stage` | Lookup |
| `validate_answers(stage_id, answers) -> list[str]` | Empty = ok; messages for missing required |
| `answers_to_kwargs(answers: dict) -> dict` | Keys only: `title`, `genre`, `director_signature`, `target_duration_seconds`, `complexity`, `chat_model`, `video_model`, `notes` (optional omit None) |
| `build_notes(answers) -> str` | Deterministic rollup of logline, characters, world, tech_notes into one notes string |
| `summary_and_next_steps(bible: dict) -> str` | Human text; CLI-style next commands as **text only** (`dna init`, `quota budget`, `sequence init`) |

**`answers_to_kwargs` rules:**

- `title` ← answers["title"]
- `genre` ← answers.get("genre") or default
- `director_signature` ← answers.get("director_signature") or None (builder default)
- `target_duration_seconds` ← int(answers["target_duration_seconds"])
- `complexity` ← answers.get("complexity") or "Medium"
- `video_model` / `chat_model` ← pass through if set; let builder/models resolve
- `notes` ← `build_notes(answers)` if any free-text present, else omit

**Never return:** nested dicts, unknown kwargs, DNA structures, pipeline strings (builder owns those).

#### 1.4 Tests — `tests/test_bible_stages.py`

- All stage ids unique; 5 stages
- Required title missing → validation error
- Full answers → kwargs keys ⊆ allowed set
- `build_production_bible(**answers_to_kwargs(sample))` succeeds
- Result keys ⊇ WP0 required key set (exact compatibility)
- `summary_and_next_steps` non-empty and mentions dna or next steps
- Notes rollup includes logline + characters when provided

**Done when:** pure module + tests green; no CLI/UI changes yet.

---

### WP2 — CLI wiring

**File:** `tools/cli/bible_commands.py`  
**Do not** change `build_production_bible` signature unless a real bug appears.

#### 2.1 `create-bible` signature changes

Keep:

- `title: str | None = typer.Argument(None, …)` — **change from required to optional** so `--wizard` works without a positional title
- Existing options: `--genre`, `--chat-model`, `--video-model`, `--output`

Add:

- `--wizard / -w`: force interactive wizard

**Do not add:** `--direct`, `--resume`.

#### 2.2 Dispatch policy (single function)

```text
should_run_wizard(wizard_flag, title, stdin_isatty) -> bool

True when:
  - wizard_flag is True, OR
  - title is None/empty AND stdin is a TTY

False when:
  - title is provided (direct path), even on TTY
  - not a TTY and no --wizard  → if title missing, Exit(2) with clear message
  - --wizard and not a TTY → Exit(2) "wizard requires an interactive terminal"
```

Put `should_run_wizard` in `bible_stages.py` or a tiny helper in `bible_commands.py` — prefer **pure function in `bible_stages.py`** so tests do not need Typer.

#### 2.3 Direct path (unchanged behavior)

When not wizard:

- Require title (error if missing)
- Call `build_production_bible(title, genre=…, chat_model=…, video_model=…)` as today
- Write output + project state as today
- Optionally print `summary_and_next_steps(bible)` at the end (small UX win; keep messages non-breaking)

#### 2.4 Wizard path (interactive)

Implement `_run_bible_wizard(...)` in `bible_commands.py` (or `cli/bible_wizard_cli.py` if `bible_commands.py` would exceed ~250 lines — prefer keep in same file if under ~220 total):

1. `answers: dict = {}` seed defaults from CLI flags where present (genre, models)
2. `index = 0`
3. Loop stages:
   - Print progress `Stage i/5: title`
   - For each field: show prompt + example; read line; apply default if empty and not required
   - `validate_answers`; re-prompt field or stage on error
   - Commands: empty enter accepts default; `b` previous stage; `q` abort Exit(1)
4. On `review` stage: print kwargs preview (and optional dry bible via builder); confirm y/N
5. `bible = build_production_bible(**answers_to_kwargs(answers))`
6. Same persist path as direct; print summary

Use `console` from `cli.shared` and plain `input()` or Rich prompt — **no new packages**.

#### 2.5 Tests

| Test | Method |
|------|--------|
| Help lists `--wizard` | `test_cli_smoke` or new CLI test |
| Direct `create-bible Title` still works | subprocess + temp output path; assert JSON keys |
| Non-TTY without title fails cleanly | subprocess without TTY |
| `should_run_wizard` unit matrix | pure unit tests |

Avoid full interactive stdin wizard E2E in CI unless easy; unit-test policy + kwargs path thoroughly.

**Done when:** direct path regression-free; `--wizard` documented in help; non-TTY safe.

---

### WP3 — Web UI multi-step form

**Files:**

- `web_ui/pages/production.py` — UI
- `web_ui/lib/runtime.py` — re-export stages helpers if pages should not import `cli.*` deeply (pages already go through `rt` for production)

#### 3.1 Session state

Keys (prefix `bible_wizard_` to avoid collisions):

- `bible_wizard_step` (int index)
- `bible_wizard_answers` (dict)
- Keep existing `last_bible` for download compatibility

#### 3.2 UX

On Production page, add a section **Guided Bible Creator** (above or beside current one-shot Export):

1. Progress indicator (step / 5)
2. Render fields for `STAGES[step]` with Streamlit widgets (text_input, number_input, selectbox for model aliases)
3. Back / Next buttons; Next runs `validate_answers`
4. Final step: preview JSON (build on preview button), Confirm builds bible → `st.session_state.last_bible`, success + download (reuse existing download block)
5. Show `summary_and_next_steps` as markdown

**Preserve** existing one-shot Export Bible + Master Prompt buttons (Advanced / quick path). Do not remove them in v1.

#### 3.3 Runtime exports

If needed:

```python
# runtime.py
from cli.bible_stages import STAGES, answers_to_kwargs, summary_and_next_steps, validate_answers
```

Gate behind same try/import pattern as `PRODUCTION_AVAILABLE` or a dedicated `BIBLE_STAGES_AVAILABLE`.

#### 3.4 Tests

- Extend `tests/test_web_ui_imports.py`: import stages via runtime or cli
- Pure tests already cover mapping; no Streamlit E2E required for v1

**Done when:** guided form produces same key set as CLI direct path for equivalent answers.

---

### WP4 — Docs & skill touch-up

| File | Change |
|------|--------|
| `.grok/skills/production-bible-workflow/SKILL.md` | Note optional `create-bible --wizard`; keep existing direct examples as primary |
| `README.md` / `docs/guides/Quick_Start_Guide.md` | One short subsection if they document `create-bible` |
| Design spec | Status stays “ready”; optional link to this plan |

No plugin catalog pin required unless a skill file under `.grok/skills/` changes content that is indexed — if skill body changes, run usual verify; catalog pin only if plugin index content hashes change per project rules.

**Done when:** docs do not claim wizard is default; scripts in skill still use direct path.

---

### WP5 — Verification gate

Run in order:

```bash
pytest tests/test_production_bible.py tests/test_bible_stages.py -q
pytest tests/test_cli_smoke.py tests/test_web_ui_imports.py -q
python tools/cinematic_studio_cli.py create-bible "Wizard Plan Smoke" -o /tmp/bible_direct.json
python tools/cinematic_studio_cli.py create-bible --help   # shows --wizard
# manual: create-bible --wizard in a TTY once
```

Optional: `bash scripts/verify_cinematic_studio.sh` if skill docs changed.

**Done when:** all automated tests green; manual wizard smoke once.

---

## File change map

| Path | Action | Approx. size |
|------|--------|--------------|
| `tools/cli/bible_stages.py` | **Create** | ~120–180 lines |
| `tools/cli/bible_commands.py` | Edit create-bible + wizard loop | +80–120 lines; if file >250 lines, extract `_run_bible_wizard` to `tools/cli/bible_wizard_cli.py` |
| `tools/cli/production.py` | **No change** (v1) | — |
| `web_ui/lib/runtime.py` | Re-export stages API | +10–20 lines |
| `web_ui/pages/production.py` | Guided form section | +80–120 lines; if page >350 lines, extract `render_bible_wizard()` to `web_ui/pages/_bible_wizard.py` or `web_ui/lib/bible_wizard_ui.py` |
| `tests/test_production_bible.py` | **Create** | ~40 lines |
| `tests/test_bible_stages.py` | **Create** | ~80–100 lines |
| `tests/test_cli_smoke.py` | Optional help assertion | +5 lines |
| `tests/test_web_ui_imports.py` | Stages import smoke | +5–10 lines |
| Skill / README / Quick Start | Light docs | small |

**Hard limit:** do not push any single file past 1000 lines. Prefer extract if `production.py` page grows past ~350 lines.

---

## Suggested PR / commit slices

Prefer small reviewable commits (or stacked PRs):

1. **test+core:** WP0 + WP1 (`bible_stages` + tests)
2. **cli:** WP2
3. **web:** WP3
4. **docs:** WP4

Do not mix catalog pin noise with feature commits unless skill packaging requires it.

---

## Risk register

| Risk | Mitigation |
|------|------------|
| Optional `title` Argument breaks Typer help/scripts | Keep positional title working; tests for `create-bible "X"`; missing title without wizard → clear Exit |
| Wizard hang in CI | Non-TTY never enters wizard; no interactive test in pytest |
| Notes-only characters feel “lost” | Summary text tells user to run `dna init`; design non-goal |
| Web UI duplicates Export logic | Shared `answers_to_kwargs` + single `build_production_bible` call |
| Model slug typos in wizard | Pass through to `resolve_*` in builder/context; invalid → same behavior as CLI flags today |

---

## Implementation order (checklist)

- [x] WP0: baseline bible tests (`tests/test_production_bible.py`)
- [x] WP1: `bible_stages.py` + unit tests (`tools/cli/bible_stages.py`, `tests/test_bible_stages.py`)
- [x] WP2: CLI policy + wizard loop + direct regression (`bible_commands.py`, `bible_wizard_cli.py`, `test_create_bible_cli.py`)
- [x] WP3: Web guided form + runtime re-exports (`bible_wizard_ui.py`, runtime stages API, production page section)
- [x] WP4: skill/docs (production-bible-workflow, README, Quick_Start)
- [x] WP5: full verification gate

---

## Definition of done

1. `create-bible "Title"` behavior and JSON shape unchanged (plus optional summary print is OK).
2. `create-bible --wizard` works on TTY; fails cleanly off TTY.
3. Web guided form produces the same top-level bible keys as CLI.
4. No second builder, no new deps, no resume files, no nested schema.
5. Tests cover kwargs mapping and key compatibility.
6. Docs describe wizard as optional.

---

## After this plan

Implementation can start at WP0 without further design decisions.  
If mid-implementation a structured field (e.g. `logline`) must become a first-class Bible key, stop and extend `build_production_bible` + WP0 fixture in the same PR — do not special-case only the wizard.
