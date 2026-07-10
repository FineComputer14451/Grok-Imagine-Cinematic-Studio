# Model Layer — Grok Imagine Cinematic Studio v3.7.1

Canonical stack for **all** Role Cards and skills. Implemented in `tools/models.py` · documented in `references/MODELS_v3.6.md`.

**Verify:** `python tools/cinematic_studio_cli.py models verify`

**Studio release:** v3.7.1 · **Orchestration default:** Grok 4.5 · **1M opt-in:** Grok 4.3 · **CLI:** ≥ 0.2.93

---

## Stack (required knowledge for every agent)

| Layer | Slug | When |
|-------|------|------|
| **Orchestration (default)** | `grok-4.5` | Production Bibles, multi-agent direction, agent loops (500k context; reasoning low/medium/**high**) |
| **Long-context (opt-in)** | `grok-4.3` | 1M memory banks only — `--chat-model grok-4.3` or alias `long-context` |
| **Grok Build CLI** | `grok-4.5` · fork `grok-build` | Skills, coding, local agent (CLI ≥ **0.2.93**) |
| **xAI Build / coding API** | `grok-4.5` | Structured automation (legacy: `grok-build-0.1`) |
| **Creative fast (optional)** | `grok-composer-2.5-fast` | Fast multi-agent cinematic direction in Build picker |
| **Imagine Video** | `grok-imagine-video` (1.0) / `grok-imagine-video-1.5` | 1.0 cost default ($0.05/s); 1.5 native audio ($0.08/s) |
| **Imagine Image** | `grok-imagine-image` / `grok-imagine-image-quality` | Stills ($0.02); hero plates ($0.05) |

**Aliases:** `cinematic` / `build` / `coding` / `4.5` / `grok-4.5-latest` / `grok-build-latest` → **`grok-4.5`**  
**1M aliases:** `long-context` / `4.3` / `grok-4` → **`grok-4.3`**

---

## Grok 4.5 operating rules (agents & skills)

1. **Default all orchestration** to `grok-4.5` unless the user or Studio Director explicitly needs 1M context.
2. **Reasoning:** prefer **high** for Bibles, QA, Identity Lock, Sequence Director; **medium** for routine prompt drafts; **low** only for trivial routing. Grok 4.5 defaults to high.
3. **Prompt cache:** use a stable `prompt_cache_key` per production (project slug) on multi-turn agent loops to reduce cost.
4. **Do not** treat Imagine models as chat models — video/image spend is `grok-imagine-*` only.
5. Every Production Bible must lock `model_stack` + `VIDEO_PIPELINE_SPEC` from the registry helpers.
6. Opt into `grok-4.3` only when memory banks / long chains exceed ~400k effective context.
7. Do **not** treat CLI version `0.2.93` as an API model slug — it is the **Grok Build binary** version.
8. **Imagine Agent Mode Handoff (v3.7.1):** Studio Director owns routing to Build tools / ACP / grok.com/imagine / xAI API. Prefer in-session tools (`image_gen`, `image_edit`, `image_to_video`) when available.

---

## Markdown block (embed in Role Cards & skills)

Copy this section into Role Cards and SKILL.md files under the title (after Core Mission if preferred):

```markdown
## Model Layer (Grok 4.5 · studio v3.7.1)

| Layer | Slug | When |
|-------|------|------|
| Orchestration (default) | `grok-4.5` | Bibles, direction, agent loops |
| Long-context (opt-in) | `grok-4.3` | 1M memory banks only |
| Grok Build CLI | `grok-4.5` · `grok-build` | Skills / coding (≥ 0.2.93) |
| Imagine Video | `grok-imagine-video` / `1.5` | 1.0 cost · 1.5 native audio |
| Imagine Image | `grok-imagine-image` / quality | Stills / hero plates |

Prefer stable `prompt_cache_key` on multi-turn `grok-4.5` loops. Reasoning **high** for Bibles/QA/locks; opt into `grok-4.3` only for 1M. Imagine tools: `image_gen` / `image_edit` / `image_to_video` (not chat models). Registry: `tools/models.py` · `references/MODELS_v3.6.md` · `references/agents/MODEL_LAYER_v3.7.1.md` · `models verify`.
```

---

## Role Card authoring checklist

When creating or revising an agent Role Card:

- [ ] Embed **Model Layer (Grok 4.5 · studio v3.7.1)** block (above)
- [ ] Orchestration defaults to `grok-4.5` (never market `grok-4.3` as cinematic default)
- [ ] Mention `VIDEO_PIPELINE_SPEC` if the agent touches video/generation
- [ ] Prefer reasoning **high** for go/no-go, DNA, Bible, and QA agents
- [ ] List activation commands and handoff partners
- [ ] Point to this file for full stack rules

---

*Grok Imagine Cinematic Studio v3.7.1 — unified cinematic+Build default on Grok 4.5*
