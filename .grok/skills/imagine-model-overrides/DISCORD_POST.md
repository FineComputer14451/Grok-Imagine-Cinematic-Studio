**Imagine quality feeling soft / wrong? Use the model selector (Quality vs Fast)**

A lot of “bad Imagine quality” is just being on **Fast Mode** (Image 1.0) when you wanted **Quality Mode** (Image **2.0**).

### Quick map — https://grok.com/imagine
• **Sharp stills / text / faces** → **Quality Mode** = `grok-imagine-image-2.0`
• **Cheap drafts / volume** → **Fast Mode** = `grok-imagine-image`
• **Final video + native audio** → Video **1.5** = `grok-imagine-video-1.5`
• **Edit or extend a clip** → Video **1.0 only** = `grok-imagine-video` (there is **no** Video 2.0)

### 3-step rescue when quality is struggling
1. Open https://grok.com/imagine and check you’re on **Quality Mode** *before* Generate
2. Regenerate once with the **same** prompt (don’t rewrite yet)
3. Need audio / lip-sync → Video **1.5**; extending a clip → switch back to **1.0**

### Free skill for Grok (pin presets)
Ship **`imagine-model-overrides`** — Activate with:

`ACTIVATE IMAGINE_MODEL_OVERRIDES`

Presets: `hero` · `balanced` (default) · `draft` · `audio-final` · `edit-extend`

Links:
• Imagine UI: https://grok.com/imagine
• Studio PR: https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/pull/45
• Skill folder: https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/tree/feat/imagine-model-overrides-skill/.grok/skills/imagine-model-overrides
• SKILL.md: https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/blob/feat/imagine-model-overrides-skill/.grok/skills/imagine-model-overrides/SKILL.md
• Official model names: https://docs.x.ai/docs/models
• Image 2.0 notes: https://x.ai/news/grok-imagine-image-2
• This Discord: https://discord.gg/grok-community

Not affiliated with xAI — community tooling that mirrors public model names from docs.x.ai.

If gens look muddy, drop a screenshot of your **Quality/Fast** toggle + image vs video and we can point you at the right preset.