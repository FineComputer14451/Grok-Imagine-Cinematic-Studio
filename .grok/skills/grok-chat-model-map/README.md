# grok-chat-model-map

Grok skill: map **Chat** modes (Auto / Fast / Expert / Heavy / Build) to the **Grok 4.6** generation and keep Chat ≠ API ≠ Build ≠ Imagine.

## Install (Grok Build / grok.com skills)

```bash
# From this repo (plan branch or after merge):
mkdir -p ~/.grok/skills
cp -R .grok/skills/grok-chat-model-map ~/.grok/skills/

# Or unzip a release pack into ~/.grok/skills/grok-chat-model-map/
```

Then in Grok:

```text
ACTIVATE GROK_CHAT_MODEL_MAP
```

or `/grok-chat-model-map`

## Layout

```
grok-chat-model-map/
├── SKILL.md
├── README.md
├── DISCORD_POST.md
├── DISCORD_THREAD.md
└── references/
    ├── CHEAT_SHEET.md
    ├── mode-catalog.md
    └── PASTE_PACK.md
```

## Verify

1. Open https://grok.com Chat picker — expect Auto · Fast · Expert · Heavy · Build  
2. Activate skill → “Grok Chat model map locked…” + pick card  
3. Confirm it never recommends sending `Auto` as an API `model`

## Links

- PR: https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/pull/48  
- Docs: https://docs.x.ai/developers/models · https://docs.x.ai/developers/grok-4-6  
- Sibling: `.grok/skills/imagine-model-overrides`
