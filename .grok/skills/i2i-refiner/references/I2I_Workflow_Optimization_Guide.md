# I2I Workflow Optimization Guide v3.6

**Goal:** Maximize quality, consistency, and efficiency when using `i2i-cinematic-refiner` and `i2i-refiner`.

---

## 1. Current Workflow Analysis

### Standard 3-Pass Chain (Current)

| Pass                        | i2i-cinematic-refiner     | i2i-refiner (NSFW)        | Primary Focus                     |
|-----------------------------|---------------------------|---------------------------|-----------------------------------|
| Composition                 | 0.62 – 0.78               | 0.58 – 0.72               | Pose, framing, major forms        |
| Detail / Anatomy & Fluid    | 0.32 – 0.50               | 0.28 – 0.42               | Skin, texture, anatomy, fluids    |
| Polish                      | 0.15 – 0.30               | 0.12 – 0.25               | Cinematic grade, final look       |

**Strengths:** Clear structure, good NSFW protection.  
**Weaknesses:** No preparation step, limited adaptability, no targeted refinement.

---

## 2. Prioritized Optimizations (Highest Impact)

### A. Pre-i2i Composition Lock Pass (Recommended)

Add a very light **pre-pass** before the main 3-pass chain when:
- Pose is complex or dynamic
- Strong DNA anchors are available
- Working with difficult camera angles

**Recommended Settings:**
- Strength: **0.40 – 0.52**
- Focus: Only pose, framing, and major body position
- Goal: Give the main passes a much better starting point

This often reduces the number of total passes needed and improves final consistency.

### B. 4-Pass Mode for Difficult / Explicit Frames

For challenging explicit close-ups, heavy fluid scenes, or ahegao shots, use this **4-Pass Protocol**:

| Pass                        | Strength Range     | Focus                                      | Notes |
|-----------------------------|--------------------|--------------------------------------------|-------|
| 1. Composition Lock         | 0.55 – 0.68        | Pose + major forms                         | Slightly lower than normal |
| 2. Anatomy Lock             | 0.30 – 0.40        | Genitals, hands, facial structure          | Critical protection pass |
| 3. Fluids + Skin Detail     | 0.20 – 0.30        | Fluids, sheen, pores, micro-texture        | Protect specular highlights |
| 4. Expression + Final Polish| 0.10 – 0.20        | Micro-expressions, cinematic look          | Very light final pass |

**When to trigger 4-Pass Mode:**
- Heavy fluid / creampie scenes
- Extreme close-ups on genitals or face
- Ahegao or complex pleasure expressions
- Previous 3-pass results had visible artifacts

### C. Prompt Additive Strategy

Instead of writing additives from scratch every time, use these curated blocks:

**Core Protective Additives (always use with i2i-refiner):**
```
exact anatomical fidelity, no deformed or smoothed genitals, preserved fluid details and specular highlights on wet skin, micro skin texture and pores visible, locked micro-expression and eye state
```

**Scene-Specific Additives:**

- **Heavy Fluids / Creampie:**
  `thick viscous fluids with realistic stringing and pooling, preserved fluid placement across passes`

- **Ahegao / Intense Pleasure:**
  `locked ahegao expression, rolled back eyes, tongue out and drooling, heavy blush and tear lines`

- **Oiled / Shiny Skin:**
  `heavily oiled glistening skin with strong specular highlights, visible oil droplets and streaks`

- **Close-up Penetration:**
  `exact penetration detail, visible stretching and grip, realistic internal texture, no melting at contact points`

### D. Smart Routing + Agent Handoff

- Always run **Character DNA Extractor** or **Identity Lock Specialist** *before* i2i when working with recurring characters.
- After i2i refinement, send directly to `quality-assurance-guardian` with a note about which i2i agent + mode was used.
- For long explicit sequences: `erosforge-nsfw-director` → `i2i-refiner` (keyframes) → `cinematic-sequence-extender`

---

## 3. Recommended Workflows

### Standard Cinematic Workflow (Most Shots)
1. Character DNA / Identity Lock (if needed)
2. `i2i-cinematic-refiner` (standard 3-pass)
3. Quality Assurance Guardian

### High-Quality Explicit Workflow
1. Character DNA / Identity Lock
2. **Pre-i2i Composition Lock** (optional but recommended)
3. `i2i-refiner` using **4-Pass Mode** for difficult frames
4. Quality Assurance Guardian
5. (Optional) Light final polish with `i2i-cinematic-refiner` if needed

### Quota-Conscious Workflow
- Use `i2i-cinematic-refiner` by default
- Only escalate to `i2i-refiner` + 4-Pass when explicit content is clearly present
- Prefer lower strength ranges in later passes

---

## 4. Future Improvements (Next Phase)

- Automated pass skipping based on previous pass quality
- Region-specific refinement prompts (e.g., "only refine the face and hands")
- i2i result scoring system before sending to QA
- Better integration with `workflow-quota-optimizer`

---

**Version:** 3.6  
**Maintained with:** `i2i-refiner`, `i2i-cinematic-refiner`, `studio-director`, and `mega-production-architect`

*This guide will continue to evolve as we test and refine the workflows.*