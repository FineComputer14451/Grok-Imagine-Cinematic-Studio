# I2I Test Prompt Templates v3.6

Ready-to-use commands for testing `i2i-cinematic-refiner` and `i2i-refiner`.

---

## 1. Basic Functionality Tests

### Clean Cinematic Test
```bash
ACTIVATE I2I CINEMATIC REFINER on this keyframe with DNA anchors
```

### Standard NSFW Test (3-Pass)
```bash
ACTIVATE I2I REFINER on this keyframe — full NSFW protocol, protect anatomy and fluids
```

### 4-Pass Mode Test (Difficult Explicit)
```bash
ACTIVATE I2I REFINER — 4-pass mode on this explicit close-up frame
```

---

## 2. Comparison Tests

### 3-Pass vs 4-Pass Comparison (Same Frame)
Use the **same difficult explicit frame** for both:

**Test A – 3-Pass:**
```bash
ACTIVATE I2I REFINER on this keyframe — full NSFW protocol
```

**Test B – 4-Pass:**
```bash
ACTIVATE I2I REFINER — 4-pass mode on this keyframe
```

**What to compare:**
- Fluid detail and physics
- Anatomical fidelity (especially genitals)
- Skin micro-texture and pores
- Micro-expression quality
- Overall cleanliness / artifact presence

### Clean vs NSFW Routing Test
Give the same cinematic (non-explicit) frame to both:

```bash
# Should feel clean and cinematic
ACTIVATE I2I CINEMATIC REFINER on this keyframe

# Should also work but may be slightly overkill
ACTIVATE I2I REFINER on this keyframe
```

---

## 3. Pre-i2i Composition Lock Test

**Step 1 – Light Pre-Pass:**
```bash
ACTIVATE I2I REFINER — composition lock only, strength 0.48 on this keyframe
```

**Step 2 – Full Refinement:**
```bash
ACTIVATE I2I REFINER on this keyframe — full NSFW protocol
```

Compare results with and without the pre-pass.

---

## 4. DNA Integration Test

```bash
# First extract DNA (if not already done)
ACTIVATE CHARACTER DNA EXTRACTOR on these reference images

# Then run i2i with DNA anchors
ACTIVATE I2I REFINER on this keyframe with DNA anchors — full NSFW protocol
```

**Check:** Identity consistency across multiple frames/shots.

---

## 5. Difficult Frame Test Suite

Use these when testing 4-Pass Mode:

- Heavy fluid / creampie close-up
- Extreme ahegao face close-up
- Complex multi-limb intimate position
- Oiled/shiny skin with strong specular highlights
- Wet fabric / see-through clothing

**Recommended command for difficult frames:**
```bash
ACTIVATE I2I REFINER — 4-pass mode, protect fluids and micro-expressions on this frame
```

---

## 6. Full Workflow Test (Recommended)

Test the complete recommended flow:

```bash
# 1. DNA (if new character)
ACTIVATE CHARACTER DNA EXTRACTOR

# 2. Pre-i2i Composition Lock (optional but recommended)
ACTIVATE I2I REFINER — composition lock pass, strength ~0.48

# 3. Main refinement
ACTIVATE I2I REFINER — 4-pass mode (if difficult) or normal NSFW protocol

# 4. Quality check
ACTIVATE QUALITY ASSURANCE GUARDIAN on the refined result
```

---

## 7. Quick One-Liner Tests

| Goal                        | Command |
|----------------------------|--------|
| Quick clean test           | `ACTIVATE I2I CINEMATIC REFINER on this keyframe` |
| Quick NSFW test            | `ACTIVATE I2I REFINER on this keyframe — full NSFW protocol` |
| Test 4-Pass                | `ACTIVATE I2I REFINER — 4-pass mode` |
| Test with DNA              | `ACTIVATE I2I REFINER with DNA anchors — full NSFW protocol` |
| Force clean routing        | `ACTIVATE I2I CINEMATIC REFINER` |
| Force NSFW routing         | `ACTIVATE I2I REFINER — explicit mode` |

---

**Tip:** When testing, always note:
- Which mode you used (3-pass vs 4-pass)
- Whether DNA anchors were used
- What specific issues you were trying to solve (fluids, anatomy, expressions, etc.)

---

**Version:** 3.6  
Use these templates to systematically test and compare the i2i skills.