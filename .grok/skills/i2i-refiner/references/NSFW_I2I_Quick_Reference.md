# NSFW I2I Quick Reference v3.6 — I2I Refiner

**For use with:** `ACTIVATE I2I REFINER`  
**Purpose:** High-fidelity explicit image refinement while protecting anatomy, fluids, expressions, and skin detail.

---

## 1. Recommended Strength Curves (NSFW Optimized v3.6)

| Pass                        | Recommended Strength | Focus                                              | Notes for Explicit Work                          |
|-----------------------------|----------------------|----------------------------------------------------|--------------------------------------------------|
| **Composition Pass**        | 0.58 – 0.72          | Pose, body position, framing, major forms          | Slightly lower than general cinematic            |
| **Anatomy & Fluid Pass**    | 0.28 – 0.42          | Genitals, fluids, skin micro-texture, pores        | **Most critical pass** for explicit fidelity     |
| **Skin / Expression / Polish Pass** | 0.12 – 0.25    | Micro-expressions, eye state, specular highlights, cinematic look | Very low strength — protect fine details         |

**Strong Recommendation:** Bias toward the **lower half** of these ranges for close-up explicit, ahegao, or heavy fluid shots. Higher Composition strength only when pose stability is at risk.

**4-Pass Mode (Recommended for Difficult Explicit Frames)**

Use this when working with:
- Heavy fluids / creampie scenes
- Extreme close-ups on genitals or face
- Complex ahegao or intense expressions
- Previous 3-pass results had artifacts

| Pass                        | Strength Range     | Focus                                      |
|-----------------------------|--------------------|--------------------------------------------|
| 1. Composition Lock         | 0.55 – 0.68        | Pose + major forms                         |
| 2. Anatomy Lock             | 0.30 – 0.40        | Genitals, hands, facial structure          |
| 3. Fluids + Skin Detail     | 0.20 – 0.30        | Fluids, sheen, pores, micro-texture        |
| 4. Expression + Final Polish| 0.10 – 0.20        | Micro-expressions + cinematic look         |

**Activation:** `ACTIVATE I2I REFINER — 4-pass mode`

---

## 2. Core NSFW Prompt Additives (Copy-Paste)

Append this block to almost every explicit i2i prompt:

```
exact anatomical fidelity, no deformed or smoothed genitals, preserved fluid details and specular highlights on wet skin, micro skin texture and pores visible, locked micro-expression and eye state, cinematic erotic lighting, photorealistic intimate details, no extra limbs or fingers in contact areas
```

**Stronger / More Protective Version** (use on difficult frames):

```
exact anatomical fidelity, zero deformation on breasts/nipples/vulva/penis/anus/hands, preserved arousal fluids and wetness physics, visible skin pores and subtle veins, locked ahegao or pleasure micro-expression, specular highlights on oiled or sweaty skin, cinematic intimate close-up lighting, photorealistic genital texture and detail
```

---

## 3. Common Scene-Specific Additives

### Close-up Genital / Penetration
`, exact penetration detail, visible vaginal/anal stretching and grip, realistic internal texture, glistening fluids on shaft and entrance, no smoothing or melting of genital contact points`

### Ahegao / Heavy Pleasure Face
`, locked ahegao expression, rolled back eyes with visible whites, tongue out and drooling, heavy blush, tear lines, flushed skin, micro facial muscle tension`

### Heavy Fluids / Creampie / Cum Play
`, thick viscous semen and arousal fluids with realistic viscosity and stringing, cum dripping and pooling, wet skin sheen, preserved fluid placement across passes, no disappearing fluids`

### Oiled / Shiny Skin
`, heavily oiled glistening skin with strong specular highlights, visible oil droplets and streaks, enhanced skin reflectivity, cinematic erotic sheen`

### Wet Clothing / See-through
`, wet fabric clinging to skin, visible nipple and body detail through wet cloth, water droplets on fabric and skin, realistic wet fabric physics`

### BDSM / Restraint Elements
`, rope or restraint marks on skin, realistic pressure and indentation, skin bulging slightly around tight bindings, maintained hand/foot position and tension`

### Multi-Person / Complex Contact
`, clear separation of bodies and limbs, no merging of skin or anatomy at contact points, accurate hand placement and finger positioning on partner`

---

## 4. NSFW Artifact Guard Checklist (Run After Every Pass)

Before accepting a refined image, quickly check:

- [ ] Genitals not melted, fused, or smoothed
- [ ] No extra or missing fingers/hands in intimate contact
- [ ] Fluids still visible and correctly placed (not erased)
- [ ] Skin texture and pores still present (not plastic-looking)
- [ ] Eye expression and micro-details intact
- [ ] No color shifts on aroused skin or genitals
- [ ] Anatomy proportions stable from reference/DNA
- [ ] Fabric state (wet, pulled aside, stained) preserved

If any fail → run another low-strength Detail or Polish pass with stronger protective language.

---

## 5. Integration Notes

- **With Character DNA / Identity Lock:** Always pull key consistency anchors first. Explicit anatomy should be treated as part of the locked identity.
- **With ErosForge NSFW Director:** Use i2i-refiner for keyframe fidelity. Hand off to ErosForge when you need emotional performance, timing, or full sequence direction.
- **Before Video Extension:** Run full 3-pass NSFW i2i refinement on important explicit keyframes before sending to `cinematic-sequence-extender` or native video.
- **Close-up vs Wide:** Close-ups can usually take even lower strength in pass 2–3. Wide shots may need slightly higher composition strength to hold body pose.

---

## 6. Quick Activation Command Examples

```
ACTIVATE I2I REFINER on this keyframe with full NSFW protocol
ACTIVATE I2I REFINER — protect anatomy and fluids, lower mid-pass strength
I2I REFINER — ahegao close-up, heavy fluids, use strong protective additives
ACTIVATE I2I REFINER — 4-pass mode
```

---

**Version:** 3.6 | Compatible with ErosForge NSFW Director, Identity Lock Specialist, and Cinematic Sequence Extender

*Keep this file open or bookmarked during NSFW production sessions.*