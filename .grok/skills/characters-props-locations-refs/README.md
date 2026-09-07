# characters-props-locations-refs

**Auto-creates** Characters / Props / Locations reference images for Grok Imagine
(Quality Mode / `grok-imagine-image-2.0`), then boards them for later i2v/edit.

## Activate

```text
ACTIVATE CHARACTERS_PROPS_LOCATIONS_REFS
ACTIVATE CHARACTERS_PROPS_LOCATIONS_REFS auto
ACTIVATE CHARACTERS_PROPS_LOCATIONS_REFS explain
/characters-props-locations-refs
```

Companions: `ACTIVATE IMAGINE_MODEL_OVERRIDES hero` · `ACTIVATE CHARACTER_DNA_EXTRACTOR` · `ACTIVATE GROK_CHAT_MODEL_MAP`

Full card: `references/ACTIVATION.md`.

## Install

```bash
unzip characters-props-locations-refs-skill.zip -d ~/.grok/skills/
```

## Companion skills

- `imagine-model-overrides` — pin Image 2.0 / Video 1.0·1.5
- `character-dna-extractor` — DNA + portable `dna_init.py`
- `grok-chat-model-map` — Chat modes vs `grok-4.6`

## Default pipeline

Locations → Characters (DNA → plates) → Props → Board. Video only if asked.
