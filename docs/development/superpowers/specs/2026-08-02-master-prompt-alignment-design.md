# Design: MASTER_PROMPT.md factual alignment (v3.8.9)

**Date:** 2026-08-02  
**Topic:** Align classic chat activation paste + stub with studio product stamps  
**Status:** Design approved in brainstorming — ready for implementation planning after user reviews this file  
**Target version:** Studio **v3.8.9** (docs-only; no VERSION bump required)  
**Approach:** Checklist patch (Approach 1) — targeted string fixes only

## Summary of Decisions

| Decision | Choice |
|----------|--------|
| Goal | **Alignment pass** only (not activation redesign or split system) |
| Files | `MASTER_PROMPT.md` + `MASTER_PROMPT_v3.6.md` stub |
| Drift vs heritage | **Factual studio stamps only**; keep Role Card–style `v3.6` / AI Polish `v3.7.1` name labels |
| Method | Hand-edit fixed checklist; no generators or verify lint |
| Structure / length | Unchanged (no new workflow sections, Wave A narrative, or TUI docs) |
| Spec location | `docs/development/superpowers/specs/` (repo convention) |

## Problem

`MASTER_PROMPT.md` is the canonical **paste-to-activate** document for grok.com / Grok chat (Method 3 in the file; referenced from `AGENTS.md`, installers, and release bundles). Product marketing and CLI status already pin **v3.8.9** and **25** Role-Card core agents, but the prompt still contains contradictory product stamps:

| Drift | Example |
|-------|---------|
| Closing banner product pin | “running … **v3.7.1** Odyssey Native” while activation line says **v3.8.9** |
| Crew heading headcount | “**23-Agent** Professional Film Crew” while Current State says **25** Role-Card core |
| Model Layer footer | “studio **v3.7.1**” vs current studio pin **v3.8.9** / Model Layer v4.5 |
| Stub | `MASTER_PROMPT_v3.6.md` still describes the canonical prompt as **v3.7.1** |

This confuses chat activation (“which version am I running?”) and fails release-doc consistency after v3.8.x stamps landed elsewhere.

## Goals

1. Product **studio pin** in the master prompt matches `VERSION` (**3.8.9**) and the activation command `Activate Grok Imagine Cinematic Studio v3.8.9`.
2. Core agent **headcount heading** matches AGENTS / Current State (**25**, not 23).
3. Model Layer footer studio pin matches **v3.8.9** (and remains compatible with `MODEL_LAYER_v4.5.md` wording).
4. Compatibility stub points at **v3.8.9** as the canonical activation prompt version.
5. Diff stays small (~3–5 lines of content change); no redesign of A–E workflows, protocols, or agent body text.

## Non-goals

- Activation redesign (brainstorm option B) or split short/long system (option C)
- Renaming agent personality suffixes (`Studio Director v3.6`, etc.)
- Changing **AI Polish Director v3.7.1** Role Card–style label
- Expanding the agent list for Wave A / Grok Doctor / etc.
- Rewriting Handoff history note `v3.7.1 / v3.8.9` (landed-vs-current is intentional)
- Changing Method 2 Web UI (already `streamlit run web_ui/app.py`; no `cinematic-studio web` invent)
- New verify/CI lint, generators, or release automation
- Edits to `AGENTS.md`, `README.md`, CHANGELOG (unless a later release notes pass)

## Architecture / units

This is a **docs-only** change. Two files, no runtime code.

```
VERSION (3.8.9)          AGENTS.md (25 core, activation)
        │                         │
        └──────────┬──────────────┘
                   ▼
         MASTER_PROMPT.md  ← factual stamps only
                   ▲
         MASTER_PROMPT_v3.6.md  (stub pointer)
```

| Unit | Responsibility | Depends on |
|------|----------------|------------|
| `MASTER_PROMPT.md` | Canonical chat activation paste | Human-maintained; must match `VERSION` + core headcount |
| `MASTER_PROMPT_v3.6.md` | Compatibility redirect | Points only to `MASTER_PROMPT.md` |

No CLI, TUI, Streamlit, or skill behavior changes.

## Exact change list

### `MASTER_PROMPT.md`

| Location (as of design date) | From | To |
|------------------------------|------|-----|
| Section heading crew | `## 🧠 23-Agent Professional Film Crew (v3.6 Upgrades)` | `## 🧠 25-Agent Professional Film Crew (v3.6 Upgrades)` |
| Role Cards footer Model Layer | `Model Layer (Grok 4.5 · studio v3.7.1)` | `Model Layer (Grok 4.5 · studio v3.8.9)` — may add short `MODEL_LAYER_v4.5.md` mention only if it fits the same sentence without expanding the section |
| Closing banner | `…Cinematic Studio v3.7.1 "Odyssey Native"` | `…Cinematic Studio v3.8.9 "Odyssey Native"` |

### Explicit non-edits in `MASTER_PROMPT.md`

| Leave as-is | Reason |
|-------------|--------|
| Title / Current State already v3.8.9 | Already aligned |
| “25 Role-Card core agents” bullet | Already aligned |
| `streamlit run web_ui/app.py` | Already correct surface |
| Handoff activation: `v3.7.1 / v3.8.9` | Historical landed/current |
| All `… v3.6` agent name labels | Heritage Role Card labels |
| `AI Polish Director v3.7.1` | Heritage Role Card label |
| Protocols, model table, pricing, A–E | Content, not stamp drift |

### `MASTER_PROMPT_v3.6.md`

| From | To |
|------|-----|
| `studio **v3.7.1** activation prompt` | `studio **v3.8.9** activation prompt` |

Link to `MASTER_PROMPT.md` and stub purpose text remain unchanged.

## Error handling / edge cases

- **Bulk replace of `v3.7.1` is forbidden.** That would corrupt intentional heritage/history strings. Use targeted line edits only.
- **Heading “25-Agent” vs listed agents:** Do not expand the roster in this pass even if Wave A agents are missing from the list; headcount fix is stamp-only.
- **Installers:** Scripts already ship both filenames; stub remains valid after pointer pin fix.

## Testing / verification (manual)

1. After edit:
   ```bash
   rg -n 'v3\.7\.1|23-Agent' MASTER_PROMPT.md MASTER_PROMPT_v3.6.md
   ```
   **Allowed leftovers only:**
   - Handoff history phrase `v3.7.1 / v3.8.9` (if still present)
   - `AI Polish Director v3.7.1` (Role Card label)
2. Confirm closing banner and activation command both say **v3.8.9**.
3. Confirm crew heading says **25-Agent**.
4. Confirm stub says **v3.8.9**.
5. `cat VERSION` → `3.8.9`.
6. No code tests required (docs-only).

## Implementation plan handoff (next skill)

When the user approves this written spec, invoke **writing-plans** to produce a short implementation plan that:

1. Applies the three `MASTER_PROMPT.md` edits and one stub edit.
2. Runs the `rg` verification above.
3. Commits **only** those two files (plus this design doc if not already committed).

## Out of band (follow-ups, not this work)

- Optional future: docs lint that fails if MASTER_PROMPT product pin ≠ `VERSION`.
- Optional future: activation redesign or short-paste + companion split (brainstorm B/C).
- Optional future: `cinematic-studio web` alias (product change; not MASTER_PROMPT alignment).
