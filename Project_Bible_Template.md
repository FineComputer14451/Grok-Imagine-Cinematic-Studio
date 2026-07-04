# PROJECT BIBLE — [FILM TITLE]

**Version:** 1.0  
**Date:** [DATE]  
**Studio:** Grok Imagine Cinematic Studio v3.6.5 "Odyssey Native"  
**Status:** [Pre-Production / Production / Post]

**Model Stack (locked):**
- Grok Build CLI: `grok-composer-2.5-fast` (fork: `grok-build`)
- xAI Chat: `grok-4.3` (or `grok-build-0.1` for automation)
- Imagine Video: `grok-imagine-video` (1.0 default; use `grok-imagine-video-1.5` for native audio)
- Imagine Image: `grok-imagine-image`

**VIDEO_PIPELINE_SPEC:**
```
[VIDEO_PIPELINE_SPEC: model="grok-imagine-video", resolution="720p", clip_length="8-12s preferred", native_audio=false, reference_image_fidelity=high, extend_protocol="LAST_FRAME + MOTION_VECTOR + AUDIO_CUE", stitch_priority=high]
```

> **Note:** Use `grok-imagine-video-1.5` + `native_audio=true` only when one-pass synchronized audio (lip-sync + SFX + music) is required. Default 1.0 is preferred for most work ($0.05/sec).

---

## 1. CORE CONCEPT
**Logline (1-2 sentences):**  
[One-sentence hook + emotional core]

**Genre & Tone:**  
[Primary genre + tone descriptors]

**Target Audience:**  
[Demographics + emotional hooks]

---

## 2. STORY & STRUCTURE
**Act Breakdown:**
- **Act 1 (Setup):** 
- **Act 2 (Confrontation):** 
- **Act 3 (Resolution):** 

**Key Themes:**
- Theme 1:
- Theme 2:

**Central Conflict:**

---

## 3. CHARACTERS (with Identity Lock Variables)

| Character Name | Role | Key Traits | Physical Description | Voice/Dialogue Style | Fighting Style / Movement DNA | Injury/Fatigue Notes |
|----------------|------|------------|----------------------|----------------------|-------------------------------|----------------------|
|                |      |            |                      |                      |                               |                      |
|                |      |            |                      |                      |                               |                      |

**Locked Variables:** `[CHARACTER_NAME]`, `[AGE]`, `[OCCUPATION]`, etc.

---

## 4. VISUAL LANGUAGE
**Color Palette:**  
[Primary, Secondary, Accent colors + emotional meaning]

**Lighting Style:**  
[High-key / Low-key / Practical / Neon / etc.]

**Camera Philosophy:**  
[Handheld, Steadicam, Static, Dutch angles, etc.]

**Aspect Ratio:** `2.39:1` (or other)

---

## 5. ACTION & STUNT DNA
**Recurring Fight Styles:**
- [Character]: [Style description]

**Signature Moves / Weapons:**

**Practical vs Digital Preference:**

---

## 6. VFX & SFX DNA
**Recurring Elements (with locked variables):**
- [Element 1]: [Description + locked variables]
- [Element 2]:

**Practical-First Priorities:**

---

## 7. AUDIO DNA
**Sonic Signature:**  
[Overall sound world description]

**Recurring Sound DNA:**
- [Character/Prop/Location]: [Signature sound]

---

## 8. MARKETING & KEY ART DIRECTION
**Tone for Key Art & Trailers:**  
[Dark / Epic / Intimate / Mysterious / etc.]

**Primary Tagline Ideas:**

**Poster Concepts Priority:**
1. Character-focused
2. Action / Environment
3. Emotional / Mystery

---

## 9. PRODUCTION NOTES
**Current Phase:**  
**Next Milestones:**  
**Active Agents:** (list which specialists are currently engaged)

**Studio Tooling:**
- Use `cinematic-studio` CLI for bible generation, validation, quota estimates, and plugin catalog maintenance.
- Regenerate plugin index (if contributing): `cinematic-studio plugin catalog pin`

**Open Questions / Risks:**

---

## 10. VARIABLE LEGEND
All locked variables used across the production (e.g. `[PROTAGONIST_NAME]`, `[LOCATION]`, `[YEAR]`).

---

**This Project Bible is the single source of truth. All agents must reference and update it continuously.**