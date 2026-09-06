# Imagine Model Selector Cheat Sheet
**For https://grok.com/imagine — when Quality looks weak, muddy, or “wrong model”**

Quick pin skill: `ACTIVATE IMAGINE_MODEL_OVERRIDES`  
Studio PR: https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/pull/45  
Skill folder: https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/tree/feat/imagine-model-overrides-skill/.grok/skills/imagine-model-overrides  
Official models list: https://docs.x.ai/docs/models  
Grok Community Discord: https://discord.gg/grok-community

---

## 30-second fix

| You want… | Click / use on [grok.com/imagine](https://grok.com/imagine) | Wire model |
|-----------|-----------------------------------------------|------------|
| Sharp hero stills, text, faces, detail | **Quality Mode** | `grok-imagine-image-2.0` |
| Cheap drafts / volume | **Fast Mode** | `grok-imagine-image` |
| Final video + native audio | Video **1.5** | `grok-imagine-video-1.5` |
| Cheap / silent / **edit or extend** | Video **1.0** | `grok-imagine-video` |

**There is no Video 2.0.** Edit/extend must stay on Video **1.0**.

Image 2.0 announcement: https://x.ai/news/grok-imagine-image-2

---

## Quality Mode vs Fast Mode

| | **Quality Mode** (Image 2.0) | **Fast Mode** (Image 1.0) |
|--|------------------------------|---------------------------|
| Best for | Hero plates, typography, client stills | Thumbnails, storyboard spam |
| Detail / text | Higher | Softer / cheaper |
| Edit refs | Up to **5** | Up to **3** |
| Quality param (API) | `low` \| `medium` \| `auto` | n/a |
| Hero tip | Prefer `quality=medium` for finals | Use for drafts only |

If stills look soft, plastic, or text is broken → you are probably on **Fast**. Switch to **Quality Mode** on https://grok.com/imagine and regenerate.

Legacy “Image Quality / Pro” → treat as **Image 2.0** with `quality=low` (legacy slug retires **2026-11-02**).

---

## Video 1.0 vs 1.5

| | **1.0** | **1.5 Native** |
|--|---------|----------------|
| Audio | Silent | Native audio / Sound Layer |
| Cost | Lower | Higher |
| Edit / extend | **Yes — required** | **No** |
| Final motion | Draft / pre-viz | Finals with dialogue/SFX |

---

## Presets (skill)

| Preset | Image | Video | Use when |
|--------|-------|-------|----------|
| `hero` | 2.0 `medium` | 1.5 | Finals |
| `balanced` *(default)* | 2.0 `auto` | 1.0 | Hero stills, thrifty video |
| `draft` | 1.0 | 1.0 | Volume / quota save |
| `audio-final` | 2.0 `medium` | 1.5 | Locked plate → i2v + audio |
| `edit-extend` | keep plate | **1.0 only** | Edit / extend |

```text
ACTIVATE IMAGINE_MODEL_OVERRIDES hero
ACTIVATE IMAGINE_MODEL_OVERRIDES draft
```

Skill markdown: https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/blob/feat/imagine-model-overrides-skill/.grok/skills/imagine-model-overrides/SKILL.md

---

## Troubleshooting “struggling quality”

1. **Confirm mode** on https://grok.com/imagine — Quality vs Fast *before* Generate
2. **One change at a time** — switch mode first; don’t rewrite the whole prompt yet
3. **Hero stills** — Quality Mode + shorter, concrete prompt; add 1–2 refs first (up to 5 on 2.0)
4. **Text in image** — Quality Mode; put exact copy in quotes; avoid Fast
5. **Video soft / mute** — need audio → **1.5**; editing → **1.0**
6. **Don’t mix** 1.0 and 1.5 in one continuous chain without a continuity pass
7. **Never invent slugs** — only the table above / https://docs.x.ai/docs/models

---

## Install

```bash
unzip imagine-model-overrides-skill.zip -d ~/.grok/skills
# new Grok session → ACTIVATE IMAGINE_MODEL_OVERRIDES
```

Or browse the skill on the PR branch: https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/tree/feat/imagine-model-overrides-skill/.grok/skills/imagine-model-overrides