# Design: Guided Production Bible Wizard (v3.6.6)

**Date:** 2026-07-05  
**Revised:** 2026-07-09 (code-quality review — dual-schema and engine layer removed)  
**Topic:** Guided CLI + Web UI path for Production Bible creation  
**Status:** Design revised — ready for implementation planning  
**Approach:** Shared stage data + kwargs mapper; single Bible owner (`build_production_bible`)

## Summary of Decisions

- **Focus:** Production Bible creation only (not full production kickoff)
- **Interaction Style:** Step-by-step wizard (familiar, low-friction)
- **Stages:** 5 high-level stages with light guidance
- **Guidance Level:** Questions + examples only (no heavy AI drafting)
- **Output:** Existing structured Bible dict + human-friendly summary + next-steps text
- **Parity:** Strong — identical stage data and kwargs mapping in CLI and Web UI
- **CLI entry policy:** Direct path remains default when args are complete; wizard is opt-in or TTY-incomplete only
- **Implementation:** Pure stage data + `answers_to_kwargs` under `tools/cli/`; no second Bible builder

## Architecture

```
STAGES (pure data)          tools/cli/bible_stages.py
  id, title, questions, examples, validators
        │
        ▼
answers_to_kwargs(answers) → dict   # only kwargs for build_production_bible
        │
        ▼
build_production_bible(**kwargs)    # tools/cli/production.py — sole Bible owner
        │
        ▼
summary_and_next_steps(bible) → str # pure helper; no DNA/sequence side effects
        │
   ┌────┴────┐
   ▼         ▼
 CLI loop   Streamlit multi-step form
 (Rich)     (session_state stage index)
```

**Rules**

- No `BibleWizard` class. No parallel `build_bible()`.
- Stages never invent a nested schema (`project.*`, `style.*`, `technicals.*`).
- Final assembly always goes through `build_production_bible` in `tools/cli/production.py`.
- CLI and Web UI own navigation only (back/forward, progress, preview of **kwargs / resulting bible**).
- No new heavy dependencies (Rich + existing Typer / Streamlit only).

## Canonical Bible Contract

Wizard output **must** match what `build_production_bible` already emits (and what DNA / sequence / quota / skills already consume). Flat keys, not nested design fiction:

| Bible key | Source |
|-----------|--------|
| `project_title` | Stage 1 title |
| `genre` | Stage 2 genre |
| `director_signature` | Stage 2 tone / signature text (or default) |
| `target_duration_seconds` | Stage 4 duration |
| `complexity` | Stage 2 or default `"Medium"` |
| `chat_model` / `video_model` kwargs | Stage 4 (resolved via `tools/models.py`) |
| `notes` | Free-text rollup: logline, premise, characters, world, audio needs, aspect notes |
| `model_stack`, `video_pipeline_spec`, `locked_variables`, … | Produced only by `build_production_bible` / `production_context` |

**v1 does not add new top-level Bible keys.** Richer human fields (logline, character list, world rule, aspect ratio) are folded into `notes` (and optionally a short human summary) so downstream tools stay compatible.

If a future version needs structured logline/characters on the Bible dict, extend **`build_production_bible` once** in `production.py` with an explicit contract and update validators/examples in the same change — never only in the wizard layer.

## The 5 Stages (Light Guidance)

1. **Story Idea & Title**
   - Project title (required)
   - Core story / logline in 1–2 sentences (optional → `notes`)
   - **Kwargs:** `title`; contribute to `notes`

2. **Genre, Tone & Signature**
   - Primary genre
   - Overall tone / director signature phrase
   - Complexity (low / medium / high) optional
   - **Kwargs:** `genre`, `director_signature`, `complexity`

3. **Characters & World (light)**
   - 1–3 key character one-liners (text only; **not** DNA profiles)
   - Key setting / world rule (one short paragraph)
   - **Kwargs:** append to `notes` only in v1  
   - **Explicit:** does not call `dna init` or write character files

4. **Technical Specs**
   - Target duration (seconds)
   - Video model preference (1.0 default vs 1.5) — resolve only via `resolve_video_model` / `tools/models.py`
   - Optional chat model (default cinematic `grok-4.5`; `grok-4.3` for 1M opt-in)
   - Audio / aspect notes as free text (folded into `notes`; pipeline spec still owned by models layer)
   - **Kwargs:** `target_duration_seconds`, `video_model`, `chat_model`; notes append

5. **Review & Generate**
   - Show preview of kwargs + draft bible shape (call builder on confirm, or dry-run preview if safe)
   - Allow edit / back
   - Confirm → `build_production_bible(**kwargs)` + `summary_and_next_steps(bible)`
   - Persist same as today: write JSON output path + update project state when CLI does

## CLI + Web UI Implementation (Strong Parity)

**Shared logic (`tools/cli/bible_stages.py`)**

- `STAGES: list[Stage]` — data only
- `answers_to_kwargs(answers: dict) -> dict` — kwargs for `build_production_bible` only
- `summary_and_next_steps(bible: dict) -> str` — e.g. “Next: `dna init …`, `quota budget …`”
- Optional: `validate_stage(stage_id, answers) -> list[str]` for required fields

**CLI (`tools/cli/bible_commands.py`)**

- Keep existing non-interactive `create-bible TITLE --genre …` as the **default script-safe path**
- Launch wizard when:
  - explicit `--wizard`, **or**
  - interactive TTY **and** required title missing / incomplete invocation
- Never block non-TTY on prompts (CI/scripts keep working without `--direct`)
- Navigation: stage index + Rich prompts; `[b]` back, `[n]` next, `[q]` quit — no questionary / new prompt library
- On success: same write path as today (`--output`, project state)

**Web UI (`web_ui/pages/production.py` + thin re-exports in `web_ui/lib/runtime.py` if needed)**

- Extend existing Production / Export Bible flow with multi-step form using the same `STAGES`
- Progress bar + live preview of kwargs / bible JSON
- On finish: call `build_production_bible` via runtime (same as current Export Bible), show summary + download
- Do **not** add a second independent Export path that builds a different dict shape

## Integration & Replacement

| Path | Behavior |
|------|----------|
| `create-bible "Title" --genre …` | Unchanged direct build (scripts / skills) |
| `create-bible --wizard` (or TTY incomplete) | Interactive stages → same builder |
| Web UI guided form | Same stages → same builder |
| `--resume` | **Out of scope for v1** (no partial session files) |

On completion (both surfaces):

- Bible saved as today (CLI file + project state; Web download / session)
- Human-readable summary + next-steps text (DNA init, sequence, quota — **text only**, not executed)
- 100% key-compatible with existing DNA, sequence, quota, and `production-bible-workflow`
- `VIDEO_PIPELINE_SPEC` / model stack always from `production_context` / `tools/models.py`

## Scope & Non-Goals (Explicitly Light)

**In Scope**

- Guided step-by-step Bible creation
- Light examples and structure help
- Strong CLI / Web parity via shared stage data
- Output: existing Bible shape + summary + guidance
- Opt-in / incomplete-TTY wizard without breaking scripts

**Out of Scope (Non-Goals)**

- Heavy AI drafting or conversational co-pilot inside steps
- Automatic DNA profiles, sequences, or quota plans inside the wizard
- New nested Bible schema or second builder
- New heavy dependencies (e.g. questionary)
- Complex state machines beyond linear stage index + back/forward
- Session resume / partial-file persistence (v1)
- Replacing or removing the direct CLI path

## Success Criteria

- New users can create a consistent Production Bible in under 5 minutes via wizard
- Existing `create-bible "Title"` invocations and skill docs keep working unchanged
- CLI and Web UI share the same stages and kwargs mapping
- Output is immediately usable by DNA, sequences, quota, and validate flows
- No second JSON contract appears in artifacts or tests

## Open Questions / Future Work (Not Part of This Design)

- Optional structured Bible fields (logline, characters[], world) owned by `build_production_bible` v2
- Optional deeper AI suggestions in a later “smart mode”
- Templates gallery integration
- Progress persistence across sessions (atomic format, only if needed)

## Next Steps After Approval

See the implementation plan:

**[docs/superpowers/plans/2026-07-09-guided-production-bible-wizard-implementation.md](../plans/2026-07-09-guided-production-bible-wizard-implementation.md)**

Summary:

1. WP0 baseline bible tests → WP1 `tools/cli/bible_stages.py` + unit tests  
2. WP2 CLI `--wizard` + TTY-incomplete policy (direct path default)  
3. WP3 Web UI multi-step form on Production page  
4. WP4 skill/docs → WP5 verification gate  

---

**Design validated through iterative visual feedback; revised after strict code-quality review (2026-07-09).**  
Single Bible owner, no dual schema, no engine class, script-safe CLI default.  
Implementation plan ready.
