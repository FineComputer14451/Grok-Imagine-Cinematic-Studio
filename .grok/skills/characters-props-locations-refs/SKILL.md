---
name: characters-props-locations-refs
description: >-
  Automatically create Characters / Props / Locations reference images for Grok
  Imagine (Quality Mode / grok-imagine-image-2.0 hero locks). Use when onboarding
  a project, locking identity plates before sequences, or when the user wants
  ref plates generated without an explanation-only pause. Activate with
  ACTIVATE CHARACTERS_PROPS_LOCATIONS_REFS or /characters-props-locations-refs.
when-to-use: >-
  ACTIVATE CHARACTERS_PROPS_LOCATIONS_REFS; auto-create character prop location
  reference images; generate ref plates; identity lock board; hero stills before i2v
argument-hint: "[auto|checklist|order|models|board|check|<project-slug>]"
user-invocable: true
metadata:
  author: FineComputer14451
  short-description: Auto-create Characters / Props / Locations reference images
  version: "1.3.1"
---

# Characters / Props / Locations — Auto Reference Images

Canonical skill to **automatically create** reusable Imagine reference plates
(Characters · Props · Locations) before motion.

Begin: **"Ref workflow locked — auto-creating plates…"**  
Default mode: **generate** (not explanation-only).

Args: `auto` (default) · `checklist` · `order` · `models` · `board` · `check` · `<project-slug>`  
`explain` or `checklist-only` = docs only, no generation. `check` / `board` = post-board cross-ref check.

## Activation commands

```text
ACTIVATE CHARACTERS_PROPS_LOCATIONS_REFS
ACTIVATE CHARACTERS_PROPS_LOCATIONS_REFS auto
ACTIVATE CHARACTERS_PROPS_LOCATIONS_REFS explain
/characters-props-locations-refs
/characters-props-locations-refs <project-slug>
```

Companions:

```text
ACTIVATE IMAGINE_MODEL_OVERRIDES hero
ACTIVATE CHARACTER_DNA_EXTRACTOR
ACTIVATE GROK_CHAT_MODEL_MAP
```

Paste card: `references/ACTIVATION.md`.


Supporting files:
- `references/GENERATE.md` — auto-create plate recipe
- `references/CHECKLIST.md` — day checklist
- `references/WORKFLOW.md` — prose workflow
- `references/NAMING.md` — folder + file naming
- `references/CROSS_REF_CHECK.md` — post-board consistency check
- `samples/onboarding-demo/` — demo board + DNA for onboarding
- `README.md` — install

## Hard rules

1. **Auto-create by default.** On activate (or `auto`), run the generate pipeline. Only skip if user says `explain` / `checklist-only` / `don't generate`.
2. **Locks before motion.** Characters / props / locations plates first; video last.
3. **Hero locks use Quality / Image 2.0** (`grok-imagine-image-2.0`, prefer `quality=medium`). Fast / 1.0 is exploration only — never lock DNA on Fast.
4. **Pin models via** `imagine-model-overrides` (`hero` / `balanced` / `draft`).
5. **Reuse plates** (edit / multi-ref / i2v). Do not re-describe identity from a blank prompt every shot.
6. **Video later:** plate→audio = **1.5**; edit/extend = **1.0 only**. No Video 2.0.
7. **DNA first for characters:** `dna_init` / `ACTIVATE CHARACTER_DNA_EXTRACTOR` before hero locks when refs or description exist.

## Auto-create pipeline (default)

Run in order. If project / asset lists are missing, ask once for names — then generate.

0. **Pin** `ACTIVATE IMAGINE_MODEL_OVERRIDES hero` (Image 2.0 Quality).
1. **Locations** — for each location: establish + 2 coverage angles on Quality.
2. **Characters** — for each character: `dna init` → 3–6 plates (front, 3/4, profile, full body ± expression/wardrobe) → pick 1–2 heroes.
3. **Props** — for each prop: hero + reverse (± detail) on Quality.
4. **Board** — save under `characters/` · `props/` · `locations/` per `references/NAMING.md`.
5. **Cross-ref check** — run `scripts/cross_ref_check.py` (see `references/CROSS_REF_CHECK.md`). Fix failures before lock/motion.
6. **Stop before video** unless user asked for motion.

Full plate prompts + counts: `references/GENERATE.md`.

## Order (always)

1. Locations (establish + coverage)  
2. Characters (DNA → plates → hero lock)  
3. Props (hero + reverse ± detail)  
4. Board review  
5. Cross-ref check (`check`)  
6. Sequence stills (optional)  
7. Video (only if asked)

## Model layer (Grok 4.6 + Imagine)

| Job | Mode / preset | Wire |
|-----|---------------|------|
| Hero / identity lock | Quality · `hero` or `balanced` | `grok-imagine-image-2.0` |
| Throwaway exploration | Fast · `draft` | `grok-imagine-image` |
| Plate → video + audio | — | `grok-imagine-video-1.5` |
| Edit / extend clip | — | `grok-imagine-video` |

DNA / planning text: Chat **Expert** or API `grok-4.6`.

## Output card

```markdown
## Ref workflow — auto-create
- Project: <name>
- Mode: generate (Image 2.0 / Quality)
- Phase: locations → characters → props → board → cross-ref check
- Assets queued: …
- Plates written: …
- Cross-ref: pass | fail (list)
- Next: fix failures | Identity Lock | sequence stills | video (if asked)
```

## Cross-skills

| Need | Skill |
|------|-------|
| Model pin Quality/Fast · Video 1.0/1.5 | `imagine-model-overrides` |
| Chat modes Auto/Fast/Expert/Heavy/Build | `grok-chat-model-map` |
| Character DNA extract / inject | `character-dna-extractor` |
| DNA scaffold (`dna init`) | `character-dna-extractor/scripts/dna_init.py` |
| Sample DNA packets | `character-dna-extractor/samples/onboarding-demo/` |
| Post-board consistency | `scripts/cross_ref_check.py` |
| Imagine Agent Mode pairing | `docs/guides/IMAGINE_MODELS_MAP.md` + `references/CROSS_REF_CHECK.md` |

## References

- Auto-create recipe: `references/GENERATE.md`
- Workflow detail: `references/WORKFLOW.md`
- Day checklist: `references/CHECKLIST.md`
- Naming: `references/NAMING.md`
- Cross-ref check: `references/CROSS_REF_CHECK.md`
