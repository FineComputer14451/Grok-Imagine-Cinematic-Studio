---
name: grok-imagine-template-library
description: >-
  Browse and apply the SFW Grok Imagine Template Library (characters, locations,
  styles, shots, Create Template recipes). Activate when the user wants reusable
  Imagine packs, DNA-ready character shells, location establishes, style grades,
  shot framing add-ons, or paste-ready product-template recipes. Not the NSFW
  kink template doc under docs/templates/.
when-to-use: >-
  ACTIVATE GROK_IMAGINE_TEMPLATE_LIBRARY; imagine template library; character
  pack; location pack; style grade; shot pack; Create Template recipe;
  product-templates; SFW template library
argument-hint: "[catalog|character|location|style|shot|recipe|<slug>]"
user-invocable: true
metadata:
  author: FineComputer14451
  short-description: SFW Imagine template packs + Create Template recipes
  version: "1.0.0"
---

# Grok Imagine Template Library

```yaml
model_compatibility:
  - grok-4.6
  - grok-imagine-image-2.0
  - grok-imagine-image
  - grok-imagine-video
  - grok-imagine-video-1.5
preferred_model: grok-imagine-image-2.0
```

**Canonical library path (repo root):** `imagine-template-library/`

Begin: **"Template library locked — loading packs from `imagine-template-library/`…"**

## What this skill does

- Point agents at reusable **SFW** packs: characters · locations · styles · shots · product-templates
- Prefer reading `imagine-template-library/CATALOG.md` then the matching `PACK.md` / `RECIPE.md`
- Do **not** confuse with `docs/templates/Kink_Specific_Cinematic_Template_Library.md` (NSFW / ErosForge)

## Quick map

| Need | Path |
|------|------|
| Index | `imagine-template-library/CATALOG.md` |
| Overview | `imagine-template-library/README.md` |
| Characters | `imagine-template-library/characters/<slug>/` |
| Locations | `imagine-template-library/locations/<slug>/` |
| Styles | `imagine-template-library/styles/<slug>/` |
| Shots | `imagine-template-library/shots/<slug>/` |
| Create Template recipes | `imagine-template-library/product-templates/` |
| Blank scaffolds | `imagine-template-library/_templates/` |

## Activation

```text
ACTIVATE GROK_IMAGINE_TEMPLATE_LIBRARY
ACTIVATE GROK_IMAGINE_TEMPLATE_LIBRARY catalog
/grok-imagine-template-library
/grok-imagine-template-library <slug>
```

## Rules (from library)

- Hero stills: Image 2.0 / Quality — never lock heroes from Fast
- Slugs: snake_case
- Copy Create Template fields from `product-templates/.../RECIPE.md`
