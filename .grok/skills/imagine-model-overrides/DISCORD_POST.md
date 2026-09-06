# Discord post pack (2 messages — paste in order)

## Message 1
**Imagine quality feeling soft / wrong? Use the model selector (Quality vs Fast)**

A lot of “bad Imagine quality” is just being on **Fast Mode** (Image 1.0) when you wanted **Quality Mode** (Image **2.0**).

### Quick map — https://grok.com/imagine
• **Sharp stills / text / faces** → **Quality Mode** = `grok-imagine-image-2.0`
• **Cheap drafts / volume** → **Fast Mode** = `grok-imagine-image`
• **Final video + native audio** → Video **1.5** = `grok-imagine-video-1.5`
• **Edit or extend a clip** → Video **1.0 only** = `grok-imagine-video` (**no** Video 2.0)

### 3-step rescue
1. Open https://grok.com/imagine → confirm **Quality Mode** *before* Generate
2. Regenerate once with the **same** prompt
3. Need audio → Video **1.5**; extending → Video **1.0**

### Free skill
`ACTIVATE IMAGINE_MODEL_OVERRIDES`
Presets: `hero` · `balanced` · `draft` · `audio-final` · `edit-extend`

• PR: https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/pull/45
• Skill: https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/tree/feat/imagine-model-overrides-skill/.grok/skills/imagine-model-overrides
• SKILL.md: https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/blob/feat/imagine-model-overrides-skill/.grok/skills/imagine-model-overrides/SKILL.md
• Models: https://docs.x.ai/docs/models
• Image 2.0: https://x.ai/news/grok-imagine-image-2
• Discord: https://discord.gg/grok-community

*(cheat sheet continues in next message ↓)*

---

## Message 2 (cheat sheet)
**📋 Imagine Model Selector Cheat Sheet** (full)

**Quality vs Fast**
• **Quality Mode** = Image **2.0** `grok-imagine-image-2.0` — hero stills, text, faces (up to 5 edit refs; API `quality`: low/medium/auto)
• **Fast Mode** = Image **1.0** `grok-imagine-image` — drafts / volume (up to 3 edit refs)
• Soft / plastic / broken text? You’re probably on **Fast** → switch to **Quality** on https://grok.com/imagine
• Legacy “Image Quality / Pro” → use Image **2.0** + `quality=low` (legacy retires 2026-11-02)

**Video 1.0 vs 1.5**
• **1.0** `grok-imagine-video` — cheaper, silent, **required for edit/extend**
• **1.5** `grok-imagine-video-1.5` — native audio / Sound Layer / finals
• **No Video 2.0.** Don’t mix 1.0+1.5 in one chain without a continuity pass

**Presets** (`ACTIVATE IMAGINE_MODEL_OVERRIDES <preset>`)
• `hero` → 2.0 medium + Video 1.5
• `balanced` *(default)* → 2.0 auto + Video 1.0
• `draft` → Image 1.0 + Video 1.0
• `audio-final` → 2.0 medium + Video 1.5 (locked plate → i2v)
• `edit-extend` → Video **1.0 only**

**Troubleshoot**
1. Confirm Quality/Fast before Generate
2. Change mode first, don’t rewrite the whole prompt yet
3. Text in image → Quality Mode + quoted copy
4. Never invent model slugs — stick to the map / https://docs.x.ai/docs/models

Markdown cheat sheet: https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/blob/feat/imagine-model-overrides-skill/.grok/skills/imagine-model-overrides/references/CHEAT_SHEET.md
UI: https://grok.com/imagine · PR: https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/pull/45

Not affiliated with xAI — community guide mirroring public model names.