---
name: grok-chat-model-map
description: >-
  Map Grok Chat modes (Auto / Fast / Expert / Heavy / Build) to the Grok 4.6
  generation and keep Chat vs API vs Build vs Imagine surfaces straight. Use
  when the user asks which Chat mode to pick, confuses modes with API model
  ids, or mixes Chat with Imagine/Build. Activate with ACTIVATE GROK_CHAT_MODEL_MAP
  or /grok-chat-model-map.
when-to-use: >-
  ACTIVATE GROK_CHAT_MODEL_MAP; Grok Chat mode picker; Auto vs Fast vs Expert;
  Heavy mode; Build from Chat; grok-4.6 chat mapping; do not send Auto as API model
argument-hint: "[auto|fast|expert|heavy|build|tree|api]"
user-invocable: true
metadata:
  author: FineComputer14451
  short-description: Map Grok Chat modes to Grok 4.6 (not API ids)
  version: "1.1.0"
  verified-picker: "2026-09-06"
---

# Grok Chat Model Map

```yaml
model_compatibility:
  - grok-4.6
preferred_model: grok-4.6
```

Canonical **Chat mode** skill for [grok.com](https://grok.com) Chat (also iOS / Android / X Grok).

**Verified picker (2026-09-06 ET):** `Auto` · `Fast` · `Expert` · `Heavy` · `Build`

Begin every activation with: **"Grok Chat model map locked…"**  
Then emit the pick card (Mode / Why / Not).

Supporting files:
- `references/CHEAT_SHEET.md` — paste-ready user card
- `references/mode-catalog.md` — modes + API ids + aliases
- `references/PASTE_PACK.md` — short share paste blocks
- `README.md` — install into `~/.grok/skills`

## Hard rules

1. **Never invent picker labels.** Only: Auto, Fast, Expert, Heavy, Build.
2. **Never send Chat mode names as API `model` strings.** `Auto` / `Expert` ≠ `grok-4.6`.
3. **Grok 4.6** (`grok-4.6`) is the Chat/Code generation on [docs.x.ai/models](https://docs.x.ai/developers/models) (“Chat: Grok 4.6” / “Code: Grok 4.6”) — **not** a fifth depth tile in the verified Chat picker. Docs also: Images → Image **2.0**, Videos → Video **1.5**.
4. **Build** in the Chat picker is a **surface hop** to Grok Build, not a reasoning depth.
5. **Imagine** stills/video → skill `imagine-model-overrides` (sidebar Imagine). Docs default stills: **`grok-imagine-image-2.0`** (Quality Mode); not this skill.
6. **Cinematic Studio** `tools/models.py` is a different registry (do not merge).

## Mode catalog (Chat UI)

| Mode | Kind | When to use | Relation to Grok 4.6 |
|------|------|-------------|----------------------|
| **Auto** | Router | Everyday default | Routes Fast-like vs Expert-like; not an API id |
| **Fast** | Latency path | Quick facts, short asks | Same Chat product family; lighter route — API id not shown in UI |
| **Expert** | Deep reasoning | Hard analysis, long reasoning | Best match for flagship Chat on **4.6** generation |
| **Heavy** | Multi-agent max | Hardest multi-step depth | Separate Heavy stack (not “slow Expert”) |
| **Build** | Product switch | Coding agent / repo work | Opens Grok Build; Build default intelligence also **grok-4.6** |

Full tables: `references/mode-catalog.md`.

## Argument shortcuts

| Arg | Action |
|-----|--------|
| `auto` / `fast` / `expert` / `heavy` / `build` | Lock that mode + why |
| `tree` | Print surface decision tree only |
| `api` | Print API id reminder (never mode names as `model`) |
| _(empty)_ | Ask goal in one line, then recommend |

## Quick picks

| You want… | Pick |
|-----------|------|
| Default / mixed day | **Auto** |
| Speed | **Fast** |
| Depth / hard reasoning | **Expert** |
| Max multi-agent depth | **Heavy** |
| Coding agent | **Build** |
| Stills / video | **Imagine** (other skill) |
| HTTP API call | API id e.g. `grok-4.6` — not a Chat mode |

## Surface tree

```
Chat thread          → Auto | Fast | Expert | Heavy
Chat picker → Build  → Grok Build coding agent
Sidebar Imagine      → Imagine image/video models
api.x.ai / SDK       → grok-4.6 (grok-4.5 is a resolve alias that wraps 4.6), …
Grok Build TUI       → /model aliases (host config)
Studio registry      → tools/models.py (separate)
```

## Output card (always)

```markdown
## Grok Chat pick
- Mode: …
- Why: …
- Not: API id / Imagine / Studio registry
```

## Tier note

Verified session 2026-09-06: all five modes visible with **no lock badges**. Quotas can still differ by plan (Heavy often needs SuperGrok Heavy for full compute).

## References

- Plan / pack PR: https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/pull/48
- Docs: https://docs.x.ai/developers/models · https://docs.x.ai/developers/grok-4-6
- Sibling skill: `imagine-model-overrides` (Imagine Quality/Fast · Video 1.0/1.5)
