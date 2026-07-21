# NSFW Outfit Library — Shared Negative Pack

> Use with every still from `NSFW_Outfit_Library.md`.  
> Adults only (18+). Last updated: 2026-07-19

## Core negatives (always)

minor, underage, child, teen, schoolgirl under 18, loli, young-looking minor,
deformed hands, extra fingers, fused fingers, extra limbs, missing limbs,
bad anatomy, distorted breasts, asymmetrical breasts, plastic skin, waxy skin,
blurry face, identity morph, face distortion, cross-eyed, extra nipples,
clothing clipping, floating clothes, watermark, text, logo, signature,
low resolution, oversharpen halos, jpeg artifacts

## Framing / quality

cropped head, cut-off limbs, awkward crop, fisheye distortion, muddy lighting,
underexposed face, overexposed skin, CGI look, doll-like eyes

## i2i strength defaults (refinement path)

| Goal | Strength | Notes |
|------|----------|--------|
| Light polish / color | 0.25–0.35 | Keep outfit + identity |
| Pose / crop change | 0.40–0.55 | Re-check hands + breasts |
| Sheer / more explicit variant | 0.45–0.60 | Same face anchors if DNA locked |
| Full restyle | 0.65–0.80 | Treat as new gen; re-QA |

**Tooling:** `image_edit` + `i2i-refiner` / `ai-image-recreation` (no separate `nsfw-i2i-model` skill).
