---
name: grok-imagine-image-tools
description: Guidance for the image_gen and image_edit tools in Grok Build. Covers when to build accurate visuals with code instead of generating, strong prompt craft, reference-first rules for real people, factual grounding via search, and asset consistency across images. Load this whenever an image_gen or image_edit call is being considered or about to be made. Tool-usage-driven, not triggered by a user merely mentioning images.
metadata:
  short-description: Prompting and workflow guidance for Imagine image tools
---

# Grok Imagine Image Tools

Guidance for the two image tool calls in Grok Build (these hit **Imagine Image 2.0** on current Grok surfaces; REST default for volume stills remains `grok-imagine-image`):

- `image_gen` - generate a **new** image from a text prompt.
- `image_edit` - modify an **existing** image using a text prompt and source image.

Hero plates and Quality Mode should lock `grok-imagine-image-2.0`. There is no Video 2.0. Full map: `references/agents/IMAGINE_SURFACES.md`.

Apply this whenever you're considering or about to call either tool.

## Build accurate visuals with code, not the image tools

Image models are unreliable at exact text, numbers, and structure. When a result needs specific text, data, or structure to be correct, construct the asset with code (prefer HTML/CSS). When only the look matters, the image tools are the right choice.

## Core Principles

1. **You own the prompt.** Front-load subject → action → setting → style → lighting. Natural prose, 2–5 sentences, positive framing.
2. **Reference-first for real people.** Never pure `image_gen` for named real people. Use `image_edit` with a verified reference.
3. **Ground facts with search first.** Search before generating anything that depends on real-world identity or current events.
4. **Reuse a base image for consistency.** Generate one strong base, then `image_edit` for variations.
5. **Handle failures gracefully.** On moderation blocks, stop; do not retry to evade.
6. **Plan multi-step workflows.** Sequence steps; only parallelize independent generations.
7. **Review at the end.** Confirm intended generations ran and match the request.

## Choosing the Tool

| Situation | Tool |
|-----------|------|
| New image, no source image | `image_gen` |
| Edit / restyle / iterate | `image_edit` |
| Named real person | `image_edit` + real reference |
| Generic / invented subject | `image_gen` |

Rule of thumb: **no source image → `image_gen`; source image → `image_edit`.**

## Video

Video starts from an image. Prefer short 6s shots. Create source stills first, then animate with `image_to_video`. Assemble with FFmpeg stream-copy.
