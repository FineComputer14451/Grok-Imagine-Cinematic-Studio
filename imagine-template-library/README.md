# Grok Imagine Template Library

Reusable **SFW** packs for Grok Imagine — characters, locations, styles, shots — plus Create Template recipes.

**Home in this repo:** `imagine-template-library/` (paths below are relative to this folder).

See [`CATALOG.md`](CATALOG.md) for the full index (7 characters · 7 locations · 3 styles · 2 shots · 6 product recipes).

> **Not the NSFW doc.** Studio also ships `docs/templates/Kink_Specific_Cinematic_Template_Library.md` (ErosForge). That is a separate adult template set — do not mix the two.

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

## Optional agent mirror
An agent-disk copy may exist for offline authoring; **this repo tree is the source of truth** for Studio clones and PRs.
