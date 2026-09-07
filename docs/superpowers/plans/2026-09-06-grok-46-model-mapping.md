# Grok 4.6 Model Mapping Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every surface that names a Grok / Imagine model agree on the Grok 4.6 stack contract — same defaults, aliases, and resolve paths — with zero silent drift between `tools/models.py`, docs, host pickers, and web prefs.

**Architecture:** Keep `tools/models.py` as the only runtime source of truth. Treat MODEL_LAYER docs, Grok Build `~/.grok/config.toml` installers, React `settingsPrefs`, Streamlit session, and API `production_options` as mirrors that must resolve to the same slugs. Do not invent a second registry.

**Tech Stack:** Python (`tools/models.py`, `studio_api/meta.py`), Grok Build TOML pickers (`scripts/install_v9_grok_models.sh`), React prefs (`web_react/src/lib/settingsPrefs.ts`), Markdown model layer (`references/agents/MODEL_LAYER_v4.5.md`, `references/MODELS.md`).

## Global Constraints

- Studio version floor: **3.11.4** (`VERSION`)
- Registry schema: `tools/models.py` **SCHEMA_VERSION 1.6**
- Stack contract: cinematic / build / cli → **`grok-4.6`**
- Grok Build CLI min: **1.0.5** (binary version, not an API slug)
- Imagine image default: **`grok-imagine-image`** (1.0); hero: **`grok-imagine-image-2.0`**
- Imagine video default: **`grok-imagine-video`** (1.0); native audio: **`grok-imagine-video-1.5`**
- Legacy Quality image retires **2026-11-02** → wire **2.0 + quality=low**
- Never print secrets from `~/.grok/config.toml`
- Cloud Agents unavailable on current plan — land changes via `gh` Contents API / PR (same pattern as #44 / #46)

---

## Current map (baseline — verify, do not reinvent)

### Chat / Build stack

| Role | Canonical slug | Notes |
|------|----------------|-------|
| Cinematic + Build + CLI default | `grok-4.6` | `STACK_CONTRACT` |
| Legacy picker | `grok-4.5` | Alias → 4.6 |
| Fork / coding alias | `grok-build` | Secondary |
| Optional 1M | `grok-4.3` | Opt-in only |
| Craft specialist | `grok-v9-4p5-chat-expert` | Wraps 4.6; aliases include `chat-expert`, `grok-v9` |
| Multi / orchestration | `grok-v9-4p5-multi` | Wraps 4.6; aliases include `multi` |
| Auto / draft | `grok-4-auto` | Wraps 4.6; aliases include `auto` |

### Imagine stack

| Role | Canonical slug |
|------|----------------|
| Image cost/default | `grok-imagine-image` |
| Image hero / Quality Mode | `grok-imagine-image-2.0` |
| Image retired | `grok-imagine-image-quality` → 2.0 `quality=low` |
| Video cost/default + edit/extend | `grok-imagine-video` |
| Video native audio / r2v | `grok-imagine-video-1.5` |

### Surface → resolver

| Surface | Entry | Must resolve via |
|---------|-------|------------------|
| CLI | `models list/stack/verify` | `tools/models.py` |
| Host `/model` | `install_v9_grok_models.sh` | `[model.*]` → base `grok-4.6` |
| API Settings options | `studio_api/meta.py::production_options` | Same ROLE_DEFAULTS |
| React Settings | `settingsPrefs.ts` FALLBACK + live* remap | Same defaults + 4.5→4.6, quality→2.0 |
| Streamlit | `web_ui/lib/session.py` + `runtime.py` | Same |
| Wire I/O | `imagine_client.py` | `resolve_image_request` / `resolve_video_model` |
| Role Cards | MODEL_LAYER + `ROLE_MODEL_PREFERENCES` | expert/multi/auto |

### Known drift to close

1. `MODEL_LAYER_v4.5.md` header still says schema **1.1+** / studio **v3.11.0** while runtime is **1.6** / **3.11.4**
2. `config/grok-build.example.toml` header lag (was **v3.11.3**)
3. Academy scenarios still mention **v3.9.1** in places (see open #42)
4. `batch_runner` missing `video_model` fallback historically preferred **1.5** while ROLE_DEFAULTS is **1.0**
5. Web prefs ActionSpec seeding gaps handled in #44 / #46 — do not re-litigate unless mapping docs mention them

---

## File map (create / modify)

| File | Responsibility |
|------|----------------|
| `tools/models.py` | Canonical registry — only change if a real slug bug is found |
| `tests/test_models_*.py` (or existing model tests) | Lock STACK_CONTRACT + alias → 4.6 + Imagine defaults |
| `references/agents/MODEL_LAYER_v4.5.md` | Bump version stamps; keep role routing tables accurate |
| `references/MODELS.md` | Point at registry; fix any 4.5-as-default wording |
| `config/grok-build.example.toml` | Header + default model comment = 4.6 |
| `scripts/install_v9_grok_models.sh` | Confirm every `[model.*] base_model` is 4.6 |
| `studio_api/meta.py` | `production_options().defaults` match ROLE_DEFAULTS |
| `web_react/src/lib/settingsPrefs.ts` | FALLBACK_DEFAULTS already aligned — verify only |
| `tools/batch_runner.py` | Align missing-video fallback with ROLE_DEFAULTS |
| `docs/superpowers/plans/2026-09-06-grok-46-model-mapping.md` | This plan (optional commit into repo) |

---

## Task 1: Lock the contract with tests

**Goal:** Fail CI if stack defaults or critical aliases drift off Grok 4.6 / Imagine ROLE_DEFAULTS.

**Files:**
- Modify: existing `tests/test_models_image.py` and/or add `tests/test_models_stack_contract.py`
- Read: `tools/models.py`

- [ ] Write failing assertions for `STACK_CONTRACT` values all `== "grok-4.6"`
- [ ] Assert `resolve_chat_model("grok-4.5") == "grok-4.6"` and short aliases `4.5` / `cinematic` / `build` / `coding` if present in alias map
- [ ] Assert `DEFAULT_IMAGINE_IMAGE_MODEL == "grok-imagine-image"` and `HERO_IMAGINE_IMAGE_MODEL == "grok-imagine-image-2.0"`
- [ ] Assert `DEFAULT_IMAGINE_VIDEO_MODEL == "grok-imagine-video"` and native audio model `== "grok-imagine-video-1.5"`
- [ ] Assert v9 specialist `base_model` entries are `grok-4.6`
- [ ] Run `python -m pytest tests/test_models_image.py tests/test_models_stack_contract.py -q` (adjust to actual filenames)
- [ ] Commit: `test(models): lock Grok 4.6 stack contract and Imagine defaults`

---

## Task 2: Audit resolve paths vs ROLE_DEFAULTS

**Goal:** Every silent fallback that can pick the wrong model is either fixed or explicitly documented.

**Files:**
- Read: `tools/models.py` (`resolve_*`, `live_image_model`)
- Modify if needed: `tools/batch_runner.py`, any ImportError fallback lists in `studio_api/meta.py`

- [ ] Grep for hardcoded `grok-4.5`, `grok-imagine-video-1.5` as bare fallbacks, and Quality image slugs outside redirect helpers
- [ ] Fix `batch_runner` missing-`video_model` fallback to `DEFAULT_IMAGINE_VIDEO_MODEL` (1.0) unless shot mode requires 1.5
- [ ] Confirm `meta.production_options().defaults` matches ROLE_DEFAULTS literals
- [ ] Add/adjust a unit test for the batch fallback if one exists
- [ ] Commit: `fix(models): align execute fallbacks with ROLE_DEFAULTS`

---

## Task 3: Refresh MODEL_LAYER + MODELS docs stamps

**Goal:** Docs stop advertising stale schema/studio versions while keeping the role→expert/multi/auto map.

**Files:**
- Modify: `references/agents/MODEL_LAYER_v4.5.md`
- Modify: `references/MODELS.md` (and archive pointers if needed)
- Modify: `config/grok-build.example.toml` header comment only

- [ ] Update MODEL_LAYER header: studio **3.11.4**, schema **1.6**, date today
- [ ] Keep the three specialist profiles and Imagine 1.0/2.0 + Video 1.0/1.5 tables; verify aliases match `GROK_BUILD_V9_MODELS` / `IMAGINE_*_MODELS`
- [ ] Explicit callout: **default image is 1.0; 2.0 is hero** — not a bug
- [ ] Explicit callout: **no Imagine Video 2.0**; `2.0` aliases mean Image 2.0
- [ ] Bump example.toml version comment to 3.11.4 / grok-4.6
- [ ] Commit: `docs(models): sync MODEL_LAYER stamps to studio 3.11.4 / schema 1.6`

---

## Task 4: Host picker install parity

**Goal:** `grok models` / `/model chat-expert|multi|auto|grok-v9` install against base `grok-4.6` only.

**Files:**
- Read/modify: `scripts/install_v9_grok_models.sh`
- Optional cross-check: GrokHunter `grok-models` skill / `install_grok_profile.sh` (separate repo — document only unless user asks)

- [ ] Confirm every generated `[model.*]` block uses `base_model` / underlying id `grok-4.6`
- [ ] Confirm `models.default` guidance is `grok-4.6` (4.5 alias acceptable if resolve wraps)
- [ ] Dry-run instructions in PR body: `bash scripts/install_v9_grok_models.sh` then `python tools/cinematic_studio_cli.py models verify`
- [ ] Commit only if script drift found: `fix(models): keep v9 installer base_model on grok-4.6`

---

## Task 5: Web + API mirror check (no behavior change unless broken)

**Goal:** React FALLBACK_DEFAULTS and live remaps match the registry; no second source of truth.

**Files:**
- Read: `web_react/src/lib/settingsPrefs.ts`
- Read: `studio_api/meta.py`
- Related (already open): PR #44 prefs seeding, PR #46 handoff/duration — reference, do not duplicate

- [ ] Assert FALLBACK chat/image/video match ROLE_DEFAULTS
- [ ] Assert `liveChatModel('grok-4.5') == 'grok-4.6'` and quality→2.0 remap still present
- [ ] If API ImportError hardcoded lists diverge, fix them or delete the dead branch
- [ ] Commit only if mismatch: `fix(web/api): mirror Grok 4.6 ROLE_DEFAULTS in prefs/meta`

---

## Task 6: Ship PR + verify commands

**Goal:** One reviewable PR (or stacked on #44/#46 if preferred) with a paste-ready verify checklist.

- [ ] Open PR titled roughly: `docs+test(models): lock Grok 4.6 mapping across registry mirrors`
- [ ] PR body includes the baseline map tables from this plan
- [ ] Checklist for reviewers:
  - [ ] `python tools/cinematic_studio_cli.py models stack`
  - [ ] `python tools/cinematic_studio_cli.py models verify`
  - [ ] `pytest` model contract tests
  - [ ] Optional: `bash scripts/install_v9_grok_models.sh` on a scratch profile

---

## Out of scope

- Changing Imagine image default from 1.0 → 2.0 (product decision; document only)
- NSFW ErosForge sampling temperatures (leave unless alias base ≠ 4.6)
- Academy full rewrite (tracked by #42)
- GrokHunter Termux installer rewrite (link from plan; separate agent/skill)

---

## Done when

1. Tests fail if STACK_CONTRACT or key aliases leave Grok 4.6
2. Docs stamps match studio 3.11.4 / schema 1.6
3. Execute-path fallbacks match ROLE_DEFAULTS
4. `models verify` is the human gate for host + registry agreement
