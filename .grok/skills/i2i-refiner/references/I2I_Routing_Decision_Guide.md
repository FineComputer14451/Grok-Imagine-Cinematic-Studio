# I2I Routing Decision Guide v3.6

**Purpose:** Quick reference for Studio Director, Mega Production Architect, and human operators to choose the correct i2i refinement agent.

---

## Quick Decision Table

| Scene / Prompt Content                          | Use This Agent                  | Notes |
|------------------------------------------------|----------------------------------|-------|
| Any genital contact, penetration, or explicit nudity | **i2i-refiner**                 | Anatomy lock + fluid preservation critical |
| Ahegao, heavy pleasure faces, rolled eyes, drooling | **i2i-refiner**                 | Micro-expression protection required |
| Visible arousal fluids, sweat, oil, cum, saliva strings | **i2i-refiner**                 | Specular highlights + viscosity must survive passes |
| Erotic close-ups or intimate posing            | **i2i-refiner**                 | Lower strength in mid/late passes |
| Standard dialogue, action, emotional, or establishing shots | **i2i-cinematic-refiner**     | Clean cinematic quality focus |
| Lighting continuity or general keyframe polish | **i2i-cinematic-refiner**     | Balanced strength curves |
| Mixed or borderline content                    | Start with `i2i-cinematic-refiner`, escalate to `i2i-refiner` if explicit elements appear | Safer default |

---

## Routing Rules (For Agents)

### Studio Director & Mega Production Architect
1. Analyze the current shot description, prompt, and any reference images.
2. Apply the table above.
3. In the **Execution Roadmap** or **Production Bible**, explicitly state:
   > i2I Routing: `i2i-refiner` (reason: explicit genital contact + fluids)
4. Pass relevant Character DNA / Identity Lock anchors to the chosen agent.
5. After refinement, always send to `quality-assurance-guardian`.

### When in Doubt
Default to **`i2i-cinematic-refiner`** first.  
It is safer and faster. Escalate to `i2i-refiner` only when explicit elements are clearly present.

---

## Recommended Activation Commands

```bash
# Clean cinematic work
ACTIVATE I2I CINEMATIC REFINER on this keyframe with DNA anchors

# Explicit / NSFW work
ACTIVATE I2I REFINER on this keyframe — full NSFW protocol, protect fluids and anatomy

# Let Studio Director decide automatically
ACTIVATE STUDIO DIRECTOR — build execution roadmap with correct i2i routing
```

---

## Complementary Pair

| Skill                    | Best For                              | Strength Profile                  | NSFW Handling          |
|--------------------------|---------------------------------------|-----------------------------------|------------------------|
| `i2i-cinematic-refiner`  | Most narrative & visual work          | Balanced cinematic                | Minimal / None         |
| `i2i-refiner`            | Explicit, intimate, erotic scenes     | Lower mid/late passes             | Full specialized protocol |

Use both together in complex productions. The Studio Director and Mega Production Architect now understand when to call each one.

---

**Version:** 3.6 | Maintained as part of Grok Imagine Cinematic Studio

*Keep this guide bookmarked or open during production planning.*