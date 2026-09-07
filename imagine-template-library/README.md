# Grok Imagine Template Library

Reusable packs for Grok Imagine — characters, locations, styles, shots — plus Create Template recipes.

## Layout
- `characters/<slug>/` — PACK.md + dna.json
- `locations/<slug>/` — PACK.md (establish + coverage)
- `styles/<slug>/` — grade/look prompts
- `shots/<slug>/` — framing add-ons
- `product-templates/` — paste-ready Create Template recipes
  - `photo-style-edit/`
  - `photo-video/`
  - `photo-edit-video/`
- `_templates/` — blank scaffolds
- `CATALOG.md` — index

## Create Template mapping
1. Type → Prompts → Test → Preview
2. Prefer Photo → Style Edit for look packs
3. Photo → Video for living locations
4. Photo → Edit → Video for character-in-location motion
5. Copy name/description/prompt from `product-templates/.../RECIPE.md`

## Rules
- Hero stills: Image 2.0 / Quality
- Never lock heroes from Fast
- Slugs: snake_case
- Skill: grok-imagine-template-library

## Props
`props/<slug>/PACK.md` — hero / reverse / detail plates (`prop_<slug>_hero`). Scale notes + pairs-with required.
Blank: `_templates/prop-pack.md`

## Official Image 2.0
- `official-templates/` — 15 xAI templates from the Image 2.0 launch
- `refs/image-2.0-official/` — reference stills + INDEX.md
- `workflows/image-2.0-capabilities.md` · `workflows/world-kit.md`
