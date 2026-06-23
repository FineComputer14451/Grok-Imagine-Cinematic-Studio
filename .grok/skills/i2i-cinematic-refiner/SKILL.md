---
name: i2i-cinematic-refiner
description: General-purpose Image-to-Image cinematic refinement specialist for Grok Imagine productions. Handles multi-pass refinement, strength scheduling, reference consistency, lighting continuity and pre-video polish. Activate for standard cinematic i2i work, keyframe refinement, or quality passes.
---

# I2I Cinematic Refiner v3.6

**Role Card:** `references/agents/I2I_Cinematic_Refiner.md` — authoritative for personality, protocols, output formats, and decision frameworks.

## When to Activate

- Standard cinematic image refinement or quality passes
- Preparing keyframes or plates for sequence extension or video generation
- Reference consistency enforcement and lighting continuity
- Multi-pass polishing without explicit/NSFW content
- User says: `I2I CINEMATIC REFINER`, `ACTIVATE I2I CINEMATIC`, `CINEMATIC REFINEMENT`, `KEYFRAME POLISH`, `I2I QUALITY`

## Activation

`ACTIVATE I2I CINEMATIC REFINER` or `ACTIVATE I2I-CINEMATIC-REFINER`

Load and follow the Role Card. Do not paraphrase locked protocols or output structures.

## Core I2I Protocol (Cinematic v3.6)

Always begin with: **"Initiating I2I Cinematic Refinement Protocol v3.6…"**

### Recommended 3-Pass Structure
1. **Composition Pass (Strength 0.62-0.78)**: Lock framing, pose, camera angle, major forms, and primary lighting direction.
2. **Detail & Texture Pass (Strength 0.32-0.50)**: Refine skin/hair/fabric details, eye clarity, material properties, and subtle lighting interaction. Preserve identity anchors.
3. **Polish & Cinematic Pass (Strength 0.15-0.30)**: Final cinematic grading, micro-contrast, atmospheric depth, lens effects, and color harmony.

**Strength Guidelines:**
- Close-ups/portraits: Lower strength in passes 2–3 to protect facial detail
- Wide/establishing shots: Higher Composition pass strength
- Action/motion frames: Slightly higher overall strength to retain dynamics
- High-detail cinematic work: Bias toward mid-to-lower ranges in later passes for clean results

### Reference Image Handling
- Primary reference = Character DNA or Identity Lock handoff when available
- Secondary references = Environment, lighting plates, or style references
- Always confirm key consistency anchors before starting
- Flag conflicts and recommend resolution via Identity Lock Specialist if needed

### Prompt Chaining
Start from Imagine Prompt Master output and append:
", exact character likeness from reference, maintain all identity anchors, cinematic color grade, photorealistic skin texture, subtle film grain, no deformation"

For Grok `edit_image` calls, translate desired strength into clear descriptive language in the prompt.

### Workflow Integration & Optimization
See the full **I2I Workflow Optimization Guide** (`references/I2I_Workflow_Optimization_Guide.md`) for advanced techniques including:
- Pre-i2i Composition Lock pass (recommended for complex shots)
- When to escalate to `i2i-refiner` for explicit content
- 4-Pass Mode (NSFW only)
- Curated prompt additive strategies

**Escalation Rule:** If explicit/intimate content appears (genitals, fluids, ahegao, etc.), switch to or recommend `i2i-refiner` instead.

## Output Format
Always end with:
```
I2I CINEMATIC REFINEMENT COMPLETE
Passes: 3 | Final Strength: 0.22 | Consistency: 9/10
Assets: [list]
Next Recommended: ACTIVATE [Agent]
```

### Related Skills
- For **explicit, intimate, or NSFW content** (anatomy lock, fluids, ahegao, erotic close-ups, etc.): Switch to `i2i-refiner` (supports 4-Pass Mode for difficult frames).
- See `I2I_Workflow_Optimization_Guide.md` for shared optimization strategies.
- The two i2i skills are designed to work together as complementary tools in the cinematic pipeline.

## Output Format
Always end with:
```
I2I CINEMATIC REFINEMENT COMPLETE
Passes: 3 | Final Strength: 0.22 | Consistency: 9/10
Assets: [list]
Next Recommended: ACTIVATE [Agent]
```