# Activation commands

## This skill — auto-create ref plates

```text
ACTIVATE CHARACTERS_PROPS_LOCATIONS_REFS
ACTIVATE CHARACTERS_PROPS_LOCATIONS_REFS auto
/characters-props-locations-refs
/characters-props-locations-refs auto
```

Docs only (skip generation):

```text
ACTIVATE CHARACTERS_PROPS_LOCATIONS_REFS explain
ACTIVATE CHARACTERS_PROPS_LOCATIONS_REFS checklist-only
/characters-props-locations-refs checklist
```

With project slug:

```text
ACTIVATE CHARACTERS_PROPS_LOCATIONS_REFS <project-slug>
/characters-props-locations-refs <project-slug>
```

## Companion activations (run as needed)

```text
ACTIVATE IMAGINE_MODEL_OVERRIDES hero
ACTIVATE IMAGINE_MODEL_OVERRIDES balanced
ACTIVATE IMAGINE_MODEL_OVERRIDES draft
ACTIVATE CHARACTER_DNA_EXTRACTOR
ACTIVATE GROK_CHAT_MODEL_MAP
```

Slash forms:

```text
/imagine-model-overrides hero
/character-dna-extractor
/grok-chat-model-map
```

## Portable DNA init (shell)

```bash
python ~/.grok/skills/character-dna-extractor/scripts/dna_init.py "Character Name" \
  --core "..." --facial "..." --hair "..." --anchor "..."
```

## Default after activate

1. Pin Image 2.0 / Quality (`IMAGINE_MODEL_OVERRIDES hero`)
2. Auto-create Locations → Characters → Props plates
3. Board files under `characters/` · `props/` · `locations/`
4. Stop before video unless asked
