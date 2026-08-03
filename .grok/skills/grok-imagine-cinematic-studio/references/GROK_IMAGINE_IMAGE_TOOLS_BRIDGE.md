# Grok Imagine Image Tools Bridge Note

**For Imagine Agent Mode Handoff surface `grok_build_tools` (Surface A) and any in-session image/video generation**

When Studio Director or any agent is about to call the build-time tools `image_gen`, `image_edit`, `image_to_video`, or related Imagine tools, load and follow the **`grok-imagine-image-tools`** skill.

This bridge ensures consistent, high-quality prompting, correct tool choice, reference-first handling of real people, and the critical decision of when to build visuals with code instead of generating them.

## When to load this skill

- Any time an `image_gen` or `image_edit` call is being considered or is about to be made.
- Before generating plates, keyframes, or stills that will later become video.
- When maintaining character / prop / environment consistency across multiple stills.
- When the request involves exact text, numbers, charts, diagrams, or labeled structure (prefer code).

## Core reminders (from `grok-imagine-image-tools`)

1. **Code first for accuracy** — If the output must contain correct text, numbers, data, or precise structure, build it with HTML/CSS (or other code). Do not rely on the image model.
2. **Reference-first for real people** — Never pure `image_gen` for named real people. Use `image_edit` with a verified reference.
3. **Own the prompt** — Front-load subject → action → setting → style → lighting. Natural prose, 2–5 sentences, positive framing.
4. **Consistency** — Generate one strong base image, then use `image_edit` for variations. Do not re-generate the same character from scratch.
5. **Verify discrete accuracy** — After generation, inspect the actual image. Fix or rebuild if text/numbers/structure are wrong.
6. **Video starts from a still** — Create the source frame carefully, then animate with `image_to_video`. Prefer short 6s shots.

## Distinction from the xAI API surface

| Concern | `grok_build_tools` (this bridge) | `xai_api` surface |
|---------|----------------------------------|-------------------|
| When | Local / in-session generation with the Imagine tools | Live remote jobs via the injected API key |
| Skill | `grok-imagine-image-tools` | `xai-grok-skill` + `XAI_API_SURFACE_BRIDGE.md` |
| Key concern | Prompt craft, tool choice, consistency, code-vs-image decision | Real key, server-only, Responses API, quota protection |

## Integration

- Studio Director and Imagine Prompt Master should load `grok-imagine-image-tools` automatically when preparing or executing any still generation step under the `grok_build_tools` surface.
- Sequence Director / Continuity Guardian benefit from the consistency rules when locking plates.
- Always prefer this skill over ad-hoc prompting when the tools are available.

**Canonical skill:** `grok-imagine-image-tools`  
**Related:** `imagine-prompt-master`, `xai-grok-skill` (for the live API surface)
