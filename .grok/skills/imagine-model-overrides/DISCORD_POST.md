# Discord post (#community-projects) — single message

**Imagine Model Selector — fix soft / muddy gens (Quality vs Fast)**

A lot of “bad Imagine quality” is just **Fast Mode** (Image 1.0) when you wanted **Quality Mode** (Image **2.0**).

**Quick map** — https://grok.com/imagine
• Sharp stills / text / faces → **Quality Mode** = `grok-imagine-image-2.0`
• Cheap drafts → **Fast Mode** = `grok-imagine-image`
• Final video + native audio → Video **1.5** = `grok-imagine-video-1.5`
• Edit / extend clip → Video **1.0 only** = `grok-imagine-video` (**no** Video 2.0)

**Cheat sheet**
• Soft / plastic / broken text? You’re on **Fast** → switch to **Quality**, regenerate same prompt
• Legacy “Image Quality / Pro” → Image **2.0** + `quality=low` (retires 2026-11-02)
• Video **1.0** = silent / cheaper / edit+extend · **1.5** = native audio / finals
• Don’t mix 1.0+1.5 in one chain without a continuity pass

**Presets** — `ACTIVATE IMAGINE_MODEL_OVERRIDES`
`hero` (2.0 medium + 1.5) · `balanced` default (2.0 auto + 1.0) · `draft` (1.0+1.0) · `audio-final` · `edit-extend` (1.0 only)

**3-step rescue:** (1) confirm Quality Mode before Generate (2) regenerate once unchanged (3) audio→1.5 / extend→1.0

**Links**
• PR: https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/pull/45
• Skill: https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/tree/feat/imagine-model-overrides-skill/.grok/skills/imagine-model-overrides
• Cheat sheet: https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/blob/feat/imagine-model-overrides-skill/.grok/skills/imagine-model-overrides/references/CHEAT_SHEET.md
• Models: https://docs.x.ai/docs/models · Image 2.0: https://x.ai/news/grok-imagine-image-2

Not affiliated with xAI — community project for #community-projects. Drop a Quality/Fast screenshot if still muddy.