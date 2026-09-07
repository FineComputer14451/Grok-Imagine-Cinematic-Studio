# Grok Chat 4.6 Model Mapping Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Document and keep current a faithful map of **Grok Chat** (grok.com / iOS / Android / X Grok) consumer model **modes** and how they relate to **Grok 4.6** and other xAI backends — not the Cinematic Studio registry.

**Architecture:** Treat Chat UI labels (Auto / Fast / Expert / Heavy / named pins) as the product surface. Map each label to the best-known routing behavior and API-adjacent model family. Separate **Chat modes** from **API model IDs** (`grok-4.6`, etc.). Prefer live picker verification over third-party blogs.

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

| UI mode | Behavior | Likely routing | Notes |
|---------|----------|----------------|-------|
| **Auto** | Default router by query complexity | Chooses Fast-like or Expert-like path | Do not assume a single API slug |
| **Fast** | Low-latency, light answers | Non-/low-reasoning path | Good for facts, short asks |
| **Expert** | Forced deeper reasoning | Flagship reasoning stack (4.6-era Expert) | Super / Premium+ often required for full access |
| **Heavy** | Multi-agent / max depth | Heavy / multi-agent stack | SuperGrok Heavy |
| **Named pin** (when shown) | Force a generation label | e.g. “Grok 4.6” or older 4.x | Rollout / region / tier dependent |

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
| Optional later: Discord / community cheat sheet | Same map, paste-ready |

---

## Task 1: Live-verify Chat picker labels

**Goal:** Replace third-party mode lists with a dated screenshot-backed inventory from grok.com.

- [ ] Open grok.com while logged into the user’s Grok account (or document auth block)
- [ ] Open the Chat model/mode picker; list every label exactly
- [ ] Note tier badges / locked items (Heavy, Expert, etc.)
- [ ] Capture screenshot(s) into PR assets or attach to the plan PR description
- [ ] Update the Working map table with **Verified (YYYY-MM-DD)** column
- [ ] Commit: `docs(chat): verify grok.com Chat mode picker labels`

---

## Task 2: Mode → Grok 4.6 relationship note

**Goal:** One clear paragraph + table: which modes are “on the 4.6 generation,” which are routers, which are Heavy-only.

- [ ] Write: Auto = router (not a model id)
- [ ] Write: Expert ≈ flagship reasoning on current Chat generation (**4.6** as of Aug 2026 docs)
- [ ] Write: Fast ≈ latency path (may share generation or use a lighter sibling — mark **uncertain until verified**)
- [ ] Write: Heavy = separate multi-agent product path
- [ ] Cross-link https://docs.x.ai/developers/models (“Chat: Grok 4.6”) and https://docs.x.ai/developers/grok-4-6
- [ ] Commit: `docs(chat): map Auto/Fast/Expert/Heavy to Grok 4.6 generation`

---

## Task 3: Tier matrix

**Goal:** Who can pick what.

- [ ] Free / X basic: which modes visible
- [ ] SuperGrok / X Premium+: Expert / named 4.6 pins
- [ ] SuperGrok Heavy: Heavy
- [ ] Mark unknowns as TBD from live account rather than guessing prices
- [ ] Commit: `docs(chat): Chat mode access by subscription tier`

---

## Task 4: Chat vs API vs Build vs Imagine — decision tree

**Goal:** Stop future mix-ups (the PR #47 failure mode).

- [ ] One-page decision tree:
  - Talking in grok.com chat → Chat modes map
  - Calling api.x.ai → API ids
  - Grok Build TUI `/model` → Build aliases
  - Imagine stills/video → Imagine models
- [ ] Commit: `docs(chat): surface decision tree Chat vs API vs Build vs Imagine`

---

## Task 5: Optional cheat sheet skill / community pack

**Goal:** Paste-ready card for Discord / grok.com skills if the user wants distribution.

- [ ] Only if requested after Tasks 1–4
- [ ] Mirror the verified table; no Studio registry content
- [ ] Commit or ship via Selector teammate patterns as needed

---

## Task 6: Close the loop on PR #47

**Goal:** History is clear.

- [x] Close PR #47 with comment that Studio plan was wrong target
- [ ] Link this Chat plan PR from that comment (or new PR body references #47)
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
