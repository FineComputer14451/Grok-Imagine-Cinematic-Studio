---
name: characters-props-locations-refs
description: >-
  Run the Characters / Props / Locations reference-plate workflow for Grok
  Imagine and Cinematic Studio. Use when locking identity plates before
  sequences, building a ref board, or choosing Quality vs Fast for hero refs.
  Activate with ACTIVATE CHARACTERS_PROPS_LOCATIONS_REFS or /characters-props-locations-refs.
when-to-use: >-
  ACTIVATE CHARACTERS_PROPS_LOCATIONS_REFS; character reference plates; prop
  sheets; location establish; identity lock; ref board; hero stills before i2v
argument-hint: "[checklist|order|models|board|<project-slug>]"
user-invocable: true
metadata:
  author: FineComputer14451
  short-description: Characters / Props / Locations reference plate workflow
  version: "1.0.0"
---

# Characters / Props / Locations — Reference Workflow

Canonical **explanation + checklist** skill for building reusable Imagine reference plates before motion.

Begin: **"Ref workflow locked…"** then either emit the full checklist or the section asked for (`checklist` · `order` · `models` · `board`).

If the user names a project, substitute `<project>` and suggested asset ids; do **not** generate images unless they explicitly ask to generate.

Supporting files:
- `references/CHECKLIST.md` — paste-ready day checklist
- `references/WORKFLOW.md` — full prose workflow
- `references/NAMING.md` — folder + file naming
- `README.md` — install into `~/.grok/skills`

## Hard rules

1. **Locks before motion.** Characters / props / locations plates first; video last.
2. **Hero locks use Quality / Image 2.0** (`grok-imagine-image-2.0`, often `quality=medium`). Fast / 1.0 is exploration only.
3. **Pin models via** `imagine-model-overrides` (`hero` / `balanced` / `draft`) — this skill does not invent slugs.
4. **Reuse plates** (edit / multi-ref / i2v). Do not re-describe identity from a blank prompt every shot.
5. **Video:** plate→audio motion = **1.5**; edit/extend = **1.0 only**. No Video 2.0.
6. Explanation-only until the user says **generate**.

## Order (always)

1. Locations (establish + coverage)  
2. Characters (DNA → plates → hero lock)  
3. Props (hero + reverse ± detail)  
4. Board review  
5. Sequence stills  
6. Video  

## Model layer (overrides)

| Job | Mode / preset | Wire |
|-----|---------------|------|
| Hero / identity lock | Quality · `hero` or `balanced` | `grok-imagine-image-2.0` |
| Throwaway exploration | Fast · `draft` | `grok-imagine-image` |
| Plate → video + audio | — | `grok-imagine-video-1.5` |
| Edit / extend clip | — | `grok-imagine-video` |

Activate overrides separately: `ACTIVATE IMAGINE_MODEL_OVERRIDES hero`

## Output card

```markdown
## Ref workflow
- Project: <name or TBA>
- Phase: locations | characters | props | board | stills | video
- Model pin: hero | balanced | draft
- Next asset ids: …
- Generate?: no (unless user asked)
```

## Cross-skills

| Need | Skill |
|------|-------|
| Model pin Quality/Fast · Video 1.0/1.5 | `imagine-model-overrides` |
| Chat modes Auto/Fast/Expert/Heavy/Build | `grok-chat-model-map` |
| Character DNA extract / inject | `character-dna-extractor` (co-bundled in skills pack; `ACTIVATE CHARACTER_DNA_EXTRACTOR`) |
| DNA scaffold (`dna init`) | `character-dna-extractor/scripts/dna_init.py` (portable) or Studio CLI — see `references/DNA_INIT.md` |

## References

- Workflow detail: `references/WORKFLOW.md`
- Day checklist: `references/CHECKLIST.md`
- Naming: `references/NAMING.md`
