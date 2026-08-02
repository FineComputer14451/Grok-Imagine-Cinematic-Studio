# MASTER_PROMPT v3.8.9 Factual Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align `MASTER_PROMPT.md` and `MASTER_PROMPT_v3.6.md` product stamps with studio **v3.8.9** and **25** core agents without redesigning content or renaming Role Card heritage labels.

**Architecture:** Docs-only checklist patch (design Approach 1). Four targeted string edits across two files. No code, no generators, no verify-script changes. Verification is manual `rg` plus a short allowlist of intentional `v3.7.1` leftovers.

**Tech Stack:** Markdown source files; `rg` (ripgrep) for verification; git for commits.

**Spec:** `docs/development/superpowers/specs/2026-08-02-master-prompt-alignment-design.md`

## Global Constraints

- Studio product pin: **v3.8.9** (must match `VERSION` file content `3.8.9`)
- Core agent headcount stamp: **25** (not 23)
- **Forbidden:** bulk replace of every `v3.7.1` occurrence
- **Must leave:** agent name suffixes like `Studio Director v3.6`; `AI Polish Director v3.7.1`; Handoff history `v3.7.1 / v3.8.9`
- **Must not change:** structure, A–E workflows, protocols, model pricing table, Method 2 `streamlit run web_ui/app.py`
- **Files only:** `MASTER_PROMPT.md`, `MASTER_PROMPT_v3.6.md` (do not edit AGENTS.md, README, CHANGELOG, CLI in this plan)
- Commit scope: only the two prompt files in the implementation commit (plan/spec already committed separately if needed)

---

## File map

| File | Role | Action |
|------|------|--------|
| `MASTER_PROMPT.md` | Canonical chat activation paste | Modify 3 strings (heading, Model Layer footer, closing banner) |
| `MASTER_PROMPT_v3.6.md` | Compatibility stub | Modify 1 string (studio version in pointer sentence) |
| `VERSION` | Source of truth for product pin | **Read only** — confirm `3.8.9`; do not edit |
| Design spec | Approved requirements | **Read only** |

---

### Task 1: Align MASTER_PROMPT.md product stamps

**Files:**
- Modify: `MASTER_PROMPT.md` (three exact lines)
- Read-only: `VERSION`

**Interfaces:**
- Consumes: Design change list (crew heading, Model Layer footer, closing banner)
- Produces: `MASTER_PROMPT.md` with no incorrect product pin of v3.7.1 in closing banner; 25-Agent heading; Model Layer studio v3.8.9

- [ ] **Step 1: Confirm VERSION source of truth**

```bash
cat VERSION
```

Expected stdout (exact):

```
3.8.9
```

If not `3.8.9`, **stop** and re-open the design with the user before editing.

- [ ] **Step 2: Apply crew headcount heading fix**

In `MASTER_PROMPT.md`, replace this exact line:

```markdown
## 🧠 23-Agent Professional Film Crew (v3.6 Upgrades)
```

with:

```markdown
## 🧠 25-Agent Professional Film Crew (v3.6 Upgrades)
```

Do not change any agent body lines under this heading.

- [ ] **Step 3: Apply Model Layer footer studio pin**

In `MASTER_PROMPT.md`, replace this exact line:

```markdown
> **All agents have complete Role Cards** stored in `references/agents/`. These are the authoritative definitions. Every card embeds the **Model Layer (Grok 4.5 · studio v3.7.1)** block; v3.6 cards also include "Imagine Video 1.5 Integration" and Grok 4.5 operating rules (optional 4.3 for 1M only).
```

with:

```markdown
> **All agents have complete Role Cards** stored in `references/agents/`. These are the authoritative definitions. Every card embeds the **Model Layer (Grok 4.5 · studio v3.8.9)** block; v3.6 cards also include "Imagine Video 1.5 Integration" and Grok 4.5 operating rules (optional 4.3 for 1M only).
```

Only the `studio v3.7.1` → `studio v3.8.9` token changes. Do not expand the footnote into a new section.

- [ ] **Step 4: Apply closing banner product pin**

In `MASTER_PROMPT.md`, replace this exact line:

```markdown
**You are now running the full Grok Imagine Cinematic Studio v3.7.1 "Odyssey Native". **
```

with:

```markdown
**You are now running the full Grok Imagine Cinematic Studio v3.8.9 "Odyssey Native". **
```

Preserve trailing space before the closing `**` if present (match surrounding style; the important token is `v3.8.9`).

- [ ] **Step 5: Spot-check the three edits**

```bash
rg -n '25-Agent Professional Film Crew|studio v3\.8\.9|running the full Grok Imagine Cinematic Studio v3\.8\.9' MASTER_PROMPT.md
```

Expected: three matching lines (heading ~80, footer ~123, banner ~194 — line numbers may shift by 0).

- [ ] **Step 6: Commit MASTER_PROMPT.md only (optional intermediate)**

If using frequent commits per the writing-plans skill:

```bash
git add MASTER_PROMPT.md
git commit -m "$(cat <<'EOF'
docs: align MASTER_PROMPT product stamps to v3.8.9 and 25 agents

Fix crew heading headcount, Model Layer studio pin, and closing
banner so the chat activation paste matches VERSION.
EOF
)"
```

Alternatively, skip this commit and combine with Task 2 into a single docs commit (preferred if the branch should stay compact).

---

### Task 2: Align stub + full verification

**Files:**
- Modify: `MASTER_PROMPT_v3.6.md`
- Verify: `MASTER_PROMPT.md`, `MASTER_PROMPT_v3.6.md`, `VERSION`

**Interfaces:**
- Consumes: Task 1 edits already applied to `MASTER_PROMPT.md`
- Produces: Stub pointing at v3.8.9; verification report with only allowed `v3.7.1` leftovers

- [ ] **Step 1: Apply stub version pointer**

Replace the full contents of `MASTER_PROMPT_v3.6.md` with exactly:

```markdown
# Moved → MASTER_PROMPT.md

The canonical Grok 4.5 / studio **v3.8.9** activation prompt is:

**[MASTER_PROMPT.md](MASTER_PROMPT.md)**

This filename is kept as a compatibility stub for older installers and docs that still reference `MASTER_PROMPT_v3.6.md`.
```

(Only change from prior content is `v3.7.1` → `v3.8.9` in the second line of body text.)

- [ ] **Step 2: Run full drift scan**

```bash
rg -n 'v3\.7\.1|23-Agent' MASTER_PROMPT.md MASTER_PROMPT_v3.6.md
```

**Expected matches (allowlist only):**

| Pattern | File | Why allowed |
|---------|------|-------------|
| `v3.7.1 / v3.8.9` on Handoff activation line | `MASTER_PROMPT.md` | Historical landed/current |
| `AI Polish Director v3.7.1` | `MASTER_PROMPT.md` | Role Card heritage label |

**Must NOT appear:**

- `23-Agent`
- Closing banner with `v3.7.1`
- `studio v3.7.1` in Model Layer footer
- `v3.7.1` in `MASTER_PROMPT_v3.6.md`

- [ ] **Step 3: Confirm positive stamps**

```bash
rg -n 'v3\.8\.9|25-Agent|25 Role-Card' MASTER_PROMPT.md MASTER_PROMPT_v3.6.md
cat VERSION
```

Expected: multiple `v3.8.9` hits including activation command, closing banner, stub; `25-Agent` heading; `VERSION` = `3.8.9`.

- [ ] **Step 4: Confirm heritage labels untouched**

```bash
rg -n 'Studio Director v3\.6|AI Polish Director v3\.7\.1|ACTIVATE IMAGINE_AGENT_MODE_HANDOFF' MASTER_PROMPT.md
```

Expected: all three still present (or Studio Director line + Polish + Handoff as in current file).

- [ ] **Step 5: Commit implementation files**

```bash
git add MASTER_PROMPT.md MASTER_PROMPT_v3.6.md
git commit -m "$(cat <<'EOF'
docs: align MASTER_PROMPT and stub to studio v3.8.9

Factual stamp pass: 25-agent crew heading, Model Layer pin, closing
banner, and v3.6 stub pointer. Leave Role Card heritage labels alone.
EOF
)"
```

If Task 1 already committed `MASTER_PROMPT.md`, only stage `MASTER_PROMPT_v3.6.md` here and adjust the message to “align MASTER_PROMPT stub to v3.8.9”.

- [ ] **Step 6: Show final status**

```bash
git status -sb
git log -2 --oneline
```

Expected: clean of the two prompt files (other unrelated WIP may remain; do not stage `docs/CLI_REFERENCE.md`, `tools/generate_cli_reference.py`, etc. unless the user asks).

---

## Spec coverage checklist (plan self-review)

| Spec requirement | Task |
|------------------|------|
| Crew heading 23 → 25 | Task 1 Step 2 |
| Model Layer studio v3.7.1 → v3.8.9 | Task 1 Step 3 |
| Closing banner v3.7.1 → v3.8.9 | Task 1 Step 4 |
| Stub pointer v3.8.9 | Task 2 Step 1 |
| No bulk replace / allowlist leftovers | Task 2 Step 2 |
| Leave AI Polish / Handoff / v3.6 names | Task 2 Step 4 |
| Manual rg verification | Task 2 Steps 2–4 |
| Docs-only commit of two files | Task 2 Step 5 |

**Placeholder scan:** none.  
**Out of scope confirmed:** no CLI `web` command, no AGENTS rewrite, no Wave A expansion, no lint automation.

---

## Execution handoff

After this plan is saved, implementers choose:

1. **Subagent-Driven (recommended)** — superpowers:subagent-driven-development, one task per subagent  
2. **Inline Execution** — superpowers:executing-plans in this session with checkpoints  
