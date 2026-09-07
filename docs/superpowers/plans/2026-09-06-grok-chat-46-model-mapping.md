# Grok Chat 4.6 Model Mapping Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Document and keep current a faithful map of **Grok Chat** (grok.com / iOS / Android / X Grok) consumer model **modes** and how they relate to **Grok 4.6** and other xAI backends — not the Cinematic Studio registry.

**Architecture:** Treat Chat UI labels (Auto / Fast / Expert / Heavy / Build) as the product surface. Map each label to the best-known routing behavior and API-adjacent model family. Separate **Chat modes** from **API model IDs** (`grok-4.6`, etc.). Prefer live picker verification over third-party blogs.

**Tech Stack:** Markdown plan + optional cheat-sheet skill for grok.com; verify against live grok.com picker and https://docs.x.ai/developers/models.

## Global Constraints

- Surface: **Grok Chat** only (grok.com, iOS Grok, Android Grok, X-integrated Grok) — not Cinematic Studio `tools/models.py`, not GrokHunter V9 host pickers (except as optional cross-links)
- Flagship chat intelligence (Aug 2026+): **Grok 4.6** per xAI (“Chat: Grok 4.6” on docs.x.ai/models)
- Consumer picker uses **modes** (Auto/Fast/Expert/Heavy) more than raw API slugs
- Tier gates matter: free vs SuperGrok / Premium+ vs SuperGrok Heavy
- Never invent live picker labels — verify on grok.com when logged in
- Do not print account secrets or subscription receipts

---

## Working map (baseline — verify live)

### A. Chat UI modes (consumer)

**Verified live on grok.com: 2026-09-06 (ET)** — picker shows exactly:

`Auto` · `Fast` · `Expert` · `Heavy` · `Build`

| UI mode | Behavior | Likely routing | Notes |
|---------|----------|----------------|-------|
| **Auto** | Default router by query complexity | Chooses Fast-like or Expert-like path | Do not assume a single API slug |
| **Fast** | Low-latency, light answers | Non-/low-reasoning path | Good for facts, short asks |
| **Expert** | Forced deeper reasoning | Flagship reasoning stack (4.6-era Expert) | Super / Premium+ often required for full access |
| **Heavy** | Multi-agent / max depth | Heavy / multi-agent stack | SuperGrok Heavy |
| **Build** | Coding agent entry from Chat | Grok Build surface (not a chat reasoning depth) | Distinct from Auto/Fast/Expert/Heavy |

No separate “Grok 4.6” named pin was visible in this picker snapshot — 4.6 is the generation behind Chat/Expert (per docs.x.ai), not a fifth depth mode in this UI.

### A2. Mode → Grok 4.6 generation (relationship)

Sources: live picker 2026-09-06 · https://docs.x.ai/developers/models (“Chat: Grok 4.6”) · https://docs.x.ai/developers/grok-4-6

| Mode | Kind | Relation to Grok 4.6 |
|------|------|----------------------|
| **Auto** | **Router** (not a model id) | Picks a Fast-like or Expert-like path per query; does not expose `grok-4.6` as a slug |
| **Fast** | Latency / light path | Same Chat product generation family; may use a lighter or non-/low-reasoning route — **exact API id not exposed in UI** |
| **Expert** | Forced deep reasoning | Best match for flagship Chat intelligence on the **4.6 generation** (docs: Chat → Grok 4.6) |
| **Heavy** | Multi-agent / max depth | Separate product path (Heavy stack); not “Expert but slower” |
| **Build** | Product switch | Opens **Grok Build** coding agent — not a Chat reasoning depth. Build’s default API/coding model is also **grok-4.6** (docs / Grok Build), but the Chat picker entry is a surface hop |

**Rule of thumb:** In Grok Chat, you pick a **mode**. On the API, you pick an **id** like `grok-4.6`. Do not treat `Auto`/`Fast`/`Expert`/`Heavy` as API model strings.

### A3. Tier matrix (access)

| Mode | Verified on this grok.com session (2026-09-06) | Typical gate (product docs / common knowledge — confirm on account) |
|------|-----------------------------------------------|---------------------------------------------------------------------|
| Auto | Available (selected) | Broad / default |
| Fast | Available (no lock badge in screenshot) | Broad |
| Expert | Available (no lock badge in screenshot) | Often SuperGrok / X Premium+ for full quotas |
| Heavy | Available (no lock badge in screenshot) | Commonly SuperGrok Heavy for full Heavy compute |
| Build | Available (no lock badge in screenshot) | Build entitlement / plan-dependent |

**Observed:** On the verified account snapshot, all five options appeared selectable with **no lock/upgrade badges** in the open picker. Tier **quotas** and rate limits can still differ even when the label is unlocked — do not equate “visible” with “unlimited.”

**TBD (do not invent):** Exact free-tier vs paid locks for other accounts/regions; iOS/Android parity; X-in-app picker differences.

### A4. Surface decision tree (stop the PR #47 mix-up)

```
Where are you working?
│
├─ grok.com / iOS / Android / X → Chat thread
│     → Use Chat modes: Auto | Fast | Expert | Heavy
│     → Build in that picker → hop to Grok Build (coding agent)
│     → Sidebar Imagine → Imagine image/video models (not Chat modes)
│
├─ api.x.ai / console / SDK
│     → Use API ids: grok-4.6, grok-4.5, grok-4.3, grok-4.20-*, grok-build-0.1, …
│     → Do NOT send "Auto" / "Expert" as model strings
│
├─ Grok Build TUI / CLI (`grok`, host ~/.grok/config.toml)
│     → Use Build catalog + optional /model aliases (chat-expert, multi, auto)
│     → Default coding intelligence: grok-4.6
│
└─ Cinematic Studio / Imagine Cinematic registry
      → tools/models.py ROLE_DEFAULTS (separate product map; closed PR #47)
```

**Quick picks**
- Everyday chat → **Auto**
- Need speed → **Fast**
- Need depth → **Expert** (4.6-generation Chat)
- Need multi-agent max → **Heavy**
- Need coding agent → **Build** (or CLI), not Expert
- Need stills/video → **Imagine**, not Chat modes

### B. API / developer IDs (docs.x.ai — not the Chat dropdown)

| API id | Role vs Chat |
|--------|----------------|
| `grok-4.6` | Recommended for Chat + Code on API; Chat UI Expert/Auto often sit on this generation |
| `grok-4.5` | Prior flagship; may still appear in API / migrations |
| `grok-4.3` | Long-context / alternate stack |
| `grok-4.20-0309-reasoning` | Reasoning variant |
| `grok-4.20-0309-non-reasoning` | Non-reasoning / faster path analogue |
| `grok-4.20-multi-agent-0309` | Multi-agent analogue (Heavy-adjacent family) |
| `grok-build-0.1` | Build/coding agent model — **not** Chat mode |

### C. Explicit non-goals (wrong surface)

- Cinematic Studio `STACK_CONTRACT` / Imagine Image-Video ROLE_DEFAULTS → see closed PR #47
- Grok Build `/model chat-expert|multi|auto` host TOML aliases → GrokHunter / Build, not grok.com Chat
- Imagine Quality vs Fast stills → Imagine surface (Selector teammate / grok.com/imagine)

---

## File map

| File | Responsibility |
|------|----------------|
| `docs/superpowers/plans/2026-09-06-grok-chat-46-model-mapping.md` | This plan |
| Optional later: `docs/guides/GROK_CHAT_MODELS.md` or skill pack | User-facing cheat sheet for Chat modes |
| Optional later: community / share cheat sheet | Same map, paste-ready |

---

## Task 1: Live-verify Chat picker labels

**Goal:** Replace third-party mode lists with a dated screenshot-backed inventory from grok.com.

- [x] Open grok.com Chat model/mode picker (browser verify 2026-09-06)
- [x] List every label exactly: Auto, Fast, Expert, Heavy, Build
- [x] Note tier badges / locked items — none shown on verified 2026-09-06 snapshot (all five selectable); quotas may still differ
- [x] Capture screenshot (attached in PR / plan assets)
- [x] Update the Working map table with **Verified (2026-09-06)**
- [x] Commit: `docs(chat): verify grok.com Chat mode picker labels`

---

## Task 2: Mode → Grok 4.6 relationship note

**Goal:** One clear paragraph + table: which modes are “on the 4.6 generation,” which are routers, which are Heavy-only.

- [x] Write: Auto = router (not a model id)
- [x] Write: Expert ≈ flagship reasoning on current Chat generation (**4.6** as of Aug 2026 docs)
- [x] Write: Fast ≈ latency path (API id not exposed in UI — marked uncertain)
- [x] Write: Heavy = separate multi-agent product path; Build = surface hop
- [x] Cross-link docs.x.ai models + grok-4.6 pages
- [x] Commit: `docs(chat): map Auto/Fast/Expert/Heavy/Build to Grok 4.6 generation`

---

## Task 3: Tier matrix

**Goal:** Who can pick what.

- [x] Document verified-session availability (all five visible, no lock badges)
- [x] Note typical gates without inventing prices
- [x] Mark free-tier / other-platform parity as TBD
- [x] Commit: `docs(chat): Chat mode access by subscription tier`

---

## Task 4: Chat vs API vs Build vs Imagine — decision tree

**Goal:** Stop future mix-ups (the PR #47 failure mode).

- [x] One-page decision tree added (section A4)
- [x] Commit: `docs(chat): surface decision tree Chat vs API vs Build vs Imagine`

---

## Task 5: Optional cheat sheet skill / community pack

**Goal:** Paste-ready card for grok.com skills / sharing if the user wants distribution.

- [x] Skill pack: `.grok/skills/grok-chat-model-map/` (SKILL.md, README, CHEAT_SHEET, mode-catalog, PASTE_PACK)
- [x] Mirror verified Auto/Fast/Expert/Heavy/Build table; no Studio registry content
- [x] Commit on plan branch / PR #48

---

## Task 6: Close the loop on PR #47

**Goal:** History is clear.

- [x] Close PR #47 with comment that Studio plan was wrong target
- [x] Link this Chat plan PR from #47 comments / PR #48 body references #47
- [ ] Do **not** merge Studio mapping plan into main unless user later asks

---

## Done when

1. Live picker labels are listed with a verification date (or auth-block is documented)
2. Auto / Fast / Expert / Heavy vs Grok 4.6 relationship is explicit and non-contradictory with docs.x.ai
3. Chat vs API vs Build vs Imagine surfaces cannot be confused in the plan
4. PR #47 remains closed as the wrong-surface artifact

## Out of scope

- Changing Cinematic Studio `tools/models.py`
- Rewriting GrokHunter `install_v9_grok_models.sh`
- Imagine model overrides (owned by Imagine Selector / PR #45 track)
