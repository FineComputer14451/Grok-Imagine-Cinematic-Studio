# `.grok/skills` pack index

Synced for Grok 4.6 + Imagine Image 2.0 (auto-create refs, portable dna_init, post-board cross-ref check, sample DNA packets).

| Skill | Activate | Build zip | Upload zip (SKILL.md root) |
|-------|----------|-----------|----------------------------|
| characters-props-locations-refs | `ACTIVATE CHARACTERS_PROPS_LOCATIONS_REFS` | `*-skill.zip` | `*-upload.zip` |
| imagine-model-overrides | `ACTIVATE IMAGINE_MODEL_OVERRIDES hero` | same | same |
| grok-chat-model-map | `ACTIVATE GROK_CHAT_MODEL_MAP` | same | same |
| character-dna-extractor | `ACTIVATE CHARACTER_DNA_EXTRACTOR` | same | same |

Combined: `grok-imagine-skills-pack.zip` → `unzip -d ~/.grok/`

## Onboarding extras

| Asset | Path |
|-------|------|
| Post-board cross-ref check | `characters-props-locations-refs/scripts/cross_ref_check.py` |
| Sample board + DNA demo | `characters-props-locations-refs/samples/onboarding-demo/` |
| Sample DNA packets only | `character-dna-extractor/samples/onboarding-demo/` |

Agent Mode note: consumer Imagine Agent Mode is orchestration UI — use sample DNA + `cross_ref_check.py` around the canvas; see `docs/guides/IMAGINE_MODELS_MAP.md`.
