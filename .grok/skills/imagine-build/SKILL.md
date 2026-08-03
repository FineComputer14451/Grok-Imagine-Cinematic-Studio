---
name: imagine-build
description: Wrapper for correct use of image_gen and image_edit tools inside Grok Build. Enforce code-first for exact text or data, reference-first for real people, strong prompting, base-image consistency, and careful video shot planning. Activate whenever image generation or editing is being considered in Build mode, or when the user asks about image_gen, image_edit, or visual assets while building.
metadata:
  type: wrapper
  version: "1.0"
  wraps: imagine
---

# Imagine Build Wrapper

Enforce high-quality, accurate, and consistent image (and video) generation while working in Grok Build.

## Critical Decision Rule

When the output requires exact text, numbers, labels, charts, diagrams, or precise structure, build it with code (prefer HTML + CSS). Do not rely on image models for discrete accuracy. Only use the image tools when the visual look itself is the goal (photos, illustrations, characters, scenes, style).

## Tool Selection

| Situation | Tool |
|-----------|------|
| New image, no source | `image_gen` |
| Edit, restyle, recolor, add, remove, or iterate on existing | `image_edit` |
| Named real person or group | `image_edit` with a verified real reference |
| Generic or invented subject | `image_gen` |

## Core Principles

1. **Own the prompt.** If the user supplies a detailed prompt, use it. Otherwise craft a clear 2–5 sentence prompt that leads with the subject and covers mood, composition, lighting, and style in natural prose.
2. **Reference-first for real people.** Never pure `image_gen` for a named real person. Always use `image_edit` with a real reference image after confirming identity via search when needed.
3. **Ground facts first.** Search for any real-world identity, brand, place, or current fact before generating. Put verified details into the prompt.
4. **Reuse base images.** For recurring characters, objects, or settings, generate one strong base image, then use `image_edit` for all subsequent variations.
5. **Handle blocks cleanly.** On moderation or safety blocks, stop and inform the user. Do not attempt to evade.
6. **Plan multi-step work.** Sequence steps deliberately. Only parallelize generations that belong to the same logical step.

## Prompt Structure (preferred order)

Subject → action/pose → setting → style → composition → lighting/mood → key details.

Write positively. Avoid negative prompts.

## Video Guidance (when tools are available)

- There is no pure text-to-video path in this context. Start from an image.
- Think in short shots (prefer 6s).
- Create clean, animation-friendly source frames first.
- Keep each shot to one clear subject and one simple camera or subject motion.
- Assemble final sequences with FFmpeg using stream copy (`-c copy`).

## Budget-Aware Notes

When the user is near weekly limits, prefer:
- 1k stills over 2k
- Edits over new generations
- Short 480p clips over longer or higher-resolution video

## References

See `references/original-imagine.md` for the full original skill content.
