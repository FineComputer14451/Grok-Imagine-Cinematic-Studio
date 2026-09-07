# Auto-create reference images

Default when `ACTIVATE CHARACTERS_PROPS_LOCATIONS_REFS` (or `auto`).

## Preconditions

1. Project name (or slug)
2. Lists: locations · characters · props (ask once if missing)
3. Model pin: `ACTIVATE IMAGINE_MODEL_OVERRIDES hero` → `grok-imagine-image-2.0` / Quality Mode

Chat/planning: **Expert** or API `grok-4.6`.

## Per location

Generate on **Quality / Image 2.0**:

| Plate | Purpose | Suggested id |
|-------|---------|--------------|
| Establish | Wide lock, time/weather/architecture | `loc_<slug>_establish` |
| Coverage A | Mid / opposite angle, same grade | `loc_<slug>_cov_a` |
| Coverage B | Detail / practical landmark | `loc_<slug>_cov_b` |

Prompt skeleton: *cinematic still, [bible one-liner], consistent grade, no characters unless specified, Imagine Quality Mode.*

## Per character

1. Scaffold DNA:  
   `python scripts/dna_init.py "<Name>" --core "..." --facial "..." --hair "..." --anchor "..."`  
   or `ACTIVATE CHARACTER_DNA_EXTRACTOR` if refs uploaded.
2. Generate on **Quality / Image 2.0** (inject DNA block):

| Plate | Suggested id |
|-------|--------------|
| Front | `char_<slug>_front` |
| 3/4 | `char_<slug>_three_quarter` |
| Profile | `char_<slug>_profile` |
| Full body | `char_<slug>_full` |
| Optional expression / wardrobe | `char_<slug>_expr_*` / `char_<slug>_ward_*` |

3. Pick **1–2 hero locks** → rename/copy to `char_<slug>_hero_01` (etc.).

Never lock heroes from Fast / Image 1.0.

## Per prop

| Plate | Suggested id |
|-------|--------------|
| Hero | `prop_<slug>_hero` |
| Reverse | `prop_<slug>_reverse` |
| Detail (optional) | `prop_<slug>_detail` |

One-liner in prompt: what / scale / material / era / marks. Keep scale consistent with characters.

## Board write

```
<project>/
  characters/<slug>/{dna.json,DNA.md,*.png}
  props/<slug>/{*.png,NOTE.md}
  locations/<slug>/{*.png,BIBLE.md}
```

## Stop conditions

- After board write → present Output card + checklist ticks.
- Do **not** start video unless user asked.
- If Imagine UI/API unavailable, emit paste-ready prompts + filenames and say what blocked generation.
