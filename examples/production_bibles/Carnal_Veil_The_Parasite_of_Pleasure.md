# PROJECT BIBLE — The Parasite of Pleasure

**Locked title:** **The Parasite of Pleasure** (Title Vote #2 — locked)  
**Former working title:** Carnal Veil: The Parasite of Pleasure  
**Optional card subtitle / series tag:** Carnal Veil  

**Version:** 1.0 (Level 1 Export)  
**Date:** 2026-07-22  
**Studio:** Grok Imagine Cinematic Studio v3.8.6 "Odyssey Native"  
**Status:** Active — **Level 1 Locked (Elegant Tease Mode)** · **Title Locked**  
**Continuity:** DNA Enforced · Identity Lock ON  
**Activation:** `CarnalVeil Level1` · `ActivateBible CarnalVeil` · `ActivateBible ParasiteOfPleasure`  
**prompt_cache_key:** `carnal-veil`

---

## Model Stack (locked)

| Layer | Slug |
|-------|------|
| Orchestration / chat | `grok-4.6` |
| Build fork | `grok-build` |
| Multi-agent craft (opt) | `grok-v9-4p5-multi` / `grok-v9-4p5-chat-expert` |
| Imagine Video (Level 1 default) | `grok-imagine-video` **1.0** |
| Imagine Video (hero breath/horror ambient later) | `grok-imagine-video-1.5` opt-in |
| Imagine Image | `grok-imagine-image` (hero plates: quality tier) |

```
[VIDEO_PIPELINE_SPEC: model="grok-imagine-video", version="1.0", resolution="720p",
 aspect="2.39:1 framed within 16:9 plate", clip_length="8-12s preferred",
 native_audio=false, reference_image_fidelity=high,
 extend_protocol="LAST_FRAME + MOTION_VECTOR", stitch_priority=high,
 explicit_level=1, content_mode="elegant_tease"]
```

**Quota:** SuperGrok Heavy · ~50k session budget model · daily soft-cap aware  
**API note:** xAI API team may be spend-blocked — prefer Grok Build tools / Imagine Bridge / app.

---

## 1. CORE CONCEPT

**Logline:**  
A repressed grad student rents a decaying brothel-asylum for her thesis. A parasitic entity turns every orgasm into a gateway for possession — ecstasy, gore, and madness become one.

**Genre & Tone:**  
R-rated NSFW Horror · 2010s **A24 elevated** · practical FX aesthetic · slow dread · erotic dread (not porn pacing).

**Explicit Level Ladder (hard lock):**

| Level | Mode | Status |
|-------|------|--------|
| **1** | Elegant Tease | **ACTIVE / LOCKED** |
| 2 | Artistic Nude | Locked until user unlock |
| 3 | Erotic Tension | Locked |
| 4 | Full Uncensored | Locked |

**Level 1 rules (non-negotiable):**
- No genitals, no penetration, no explicit sex acts
- Sheer / torn lingerie OK; strategic coverage; silhouette + implication
- Sweat, blood *smudges*, fear-arousal micro-expressions OK
- Gore = suggestion (shadow, residue, practical texture) — no full body horror yet
- Parasite = presence via atmosphere, reflections, fabric movement — not full reveal

**Target audience:** Adult horror / elevated erotic-horror fans; festival-adjacent short-form.

---

## 2. STORY & STRUCTURE (Level 1 = Act 1 Tease Arc)

**Act 1 (this batch):** Arrival → threshold → first infection of *desire as dread*  
**Act 2 (later levels):** Escalation of possession through pleasure  
**Act 3 (later levels):** Ecstasy/gore fusion · identity collapse or transcendence  

**Themes:**
- Intellectual control vs bodily betrayal  
- Architecture of trauma as haunted space  
- Pleasure as parasite / consent under influence (frame carefully)

**Central conflict:** Elena seeks academic mastery of the site; the site seeks her body as host.

---

## 3. CHARACTERS — Identity Lock

### Lead — Elena Voss (slug: `elena-voss`)

| Field | Locked value |
|-------|----------------|
| Age | Mid-20s (adult) |
| Body | Athletic-curvy |
| Skin | Pale, glistening (sweat sheen) |
| Hair | Long raven-black |
| Eyes | Striking green |
| Mouth | Full lips |
| Marks | Freckles (face) |
| Wardrobe L1 | Progressive torn sheer black/red lingerie over residual academic layers |
| Expression DNA | Fear-arousal continuum; sweat/blood smudges |
| Anchors | **Green eyes + freckles + raven hair + pale sweat-sheen face — NEVER change** |

**DNA status:** `locked` · drift threshold 2.5  
**Files:** `characters/elena-voss/dna.json` · `handoff.json`  
**Inject tag:** `[CHARACTER_DNA:ELENA_VOSS_v1]`

### Entity — The Parasite (non-human)

| Field | Level 1 portrayal |
|-------|-------------------|
| Form | Unseen / partial: wet shadow, red filament glint, wrong reflection |
| Desire | Entry via climax gateways (not shown L1 — only foreshadow) |
| Continuity | Always cold humidity + sweet-rot undertone in environment DNA |

**No secondary human cast locked in Level 1.**

---

## 4. VISUAL LANGUAGE

| Element | Spec |
|---------|------|
| Aspect | **2.39:1** cinematic (letterbox or anamorphic feel in 16:9 gen) |
| Grain | Fine film grain · slight halation |
| Color | Sickly amber practicals · teal-black shadows · arterial red accents |
| Lighting | Low-key · motivated practicals (bare bulbs, EXIT signs, candle stubs) |
| Camera | Slow push-ins · locked-off dread · occasional handheld micro-tremor |
| Lens feel | 35–50mm intimacy; rare 85mm portrait for fear-arousal CU |
| Production design | Decaying brothel-asylum: peeling wallpaper, iron beds, damp tile, velvet rot |

**Negative (global L1):** modern phone UI, clean hotel, daylight cheerful, cartoon, CGI plastic skin, underage, hardcore sex acts, exposed genitals, facial deformity drift on Elena

---

## 5. AUDIO (Level 1 — design only; 1.0 video default)

- Building creak · distant wet drip · low infrasound bed  
- Breath as lead instrument (Elena)  
- Parasite: sub-bass pulse when she flushes  
- **1.5 upgrade** later for synced breath / entity whisper  

---

## 6. EROSFORGE STATE (Level 1)

```yaml
EROSFORGE_STATE:
  project: carnal-veil
  explicit_level: 1
  mode: elegant_tease
  consent_frame: "adult character; horror-possession metaphor; no non-con sex shown at L1"
  intimacy_physics: fabric_friction_only
  post_scene_body: "elevated breath, damp skin, intact lingerie (progressive tear)"
  post_scene_emotion: "shame-curiosity-fear cocktail"
  identity_priority: absolute
  gore_budget: suggestion_only
```

**Agents active:** Studio Director · ErosForge · Identity Lock · Imagine Prompt Master · Continuity · QA · NSFW Quota (plan) · Reference Curator  

---

## 7. TEN KEY SHOTS — Level 1 Elegant Tease

Hero-first order for batch: **01, 03, 07, 10** then support.

### Shot 01 — Arrival Tease (HERO plate)
**Beat:** Elena at threshold of the brothel-asylum; academic coat open; lingerie edge revealed.  
**Camera:** Slow push from exterior rain to doorway CU face.  
**Prompt summary:**  
`[CHARACTER_DNA:ELENA_VOSS_v1] mid-20s woman Elena Voss at night doorway of decaying Victorian brothel-asylum, long raven hair rain-damp, striking green eyes, freckles, pale skin with sweat sheen, coat parting to sheer black-red lingerie silhouette, A24 elevated horror, 2.39:1, film grain, amber practical light vs teal shadows, fear-curiosity micro-expression, elegant tease not explicit --ar 16:9`

### Shot 02 — Key Turns
**Beat:** Skeleton key in rusted lock; her breath fogs; corridor waits.  
**Camera:** Extreme CU key + rack focus to green eyes.  
**Prompt summary:** CU pale freckled hand + key, shallow DOF, her green eye reflection in brass, damp wallpaper, dread stillness.

### Shot 03 — Corridor Procession (HERO env + body)
**Beat:** She walks the long hallway; sheer robe trails; doors breathe.  
**Camera:** Tracking reverse, 35mm, slow.  
**Prompt summary:** full-body athletic-curvy silhouette in torn sheer black/red lingerie under open coat, long corridor, peeling wallpaper, wet floor reflections, A24 horror elegance, no nudity.

### Shot 04 — Room Selection
**Beat:** Iron bed, velvet rot, red filament glint under mattress edge (parasite tease).  
**Camera:** Wide establishing then slow tilt to filament.  
**Prompt summary:** decaying bedroom asylum-brothel hybrid, iron bed, Elena sits edge of frame, red wet glint under mattress — implication only.

### Shot 05 — Mirror Doubt
**Beat:** Mirror reflection delays half a beat; freckles/eyes locked; smile she did not make.  
**Camera:** Split composition mirror / true.  
**Prompt summary:** identity-critical CU, green eyes freckles raven hair exact, wrong delayed smile in mirror, sweat sheen, horror micro-expression.

### Shot 06 — Academic Armor Falls
**Beat:** Coat drops; thesis notebook on floor; lingerie primary wardrobe.  
**Camera:** Medium, static dread.  
**Prompt summary:** athletic-curvy Elena Voss sheer black-red lingerie, coat at ankles, notebook open to diagrams of rooms, pale glistening skin, elegant tease coverage maintained.

### Shot 07 — First Flush (HERO performance)
**Beat:** Unexplained arousal — breath hitch, pupils, fabric cling from sweat; she fights it.  
**Camera:** 85mm portrait push.  
**Prompt summary:** fear-arousal expression, full lips parted, green eyes wide, freckles, sweat/blood smudge at collarbone, sheer fabric, NO explicit, A24 intimate horror.

### Shot 08 — Wall Vein
**Beat:** Wallpaper pulse; she presses palm; red damp transfers to skin.  
**Camera:** CU hand on wall → tilt to face.  
**Prompt summary:** blood-smudge practical FX on pale skin, freckled face, horror sensuality, elegant not gore-porn.

### Shot 09 — Bed Threshold
**Beat:** She half-reclines; iron bars; lingerie progressive tear; entity humidity thick.  
**Camera:** High angle slight Dutch.  
**Prompt summary:** iron bed, sheer torn lingerie strategic coverage, athletic-curvy, raven hair fanned, green eyes to camera, fear-arousal, film grain 2.39:1 feel.

### Shot 10 — Gateway Tease / Button (HERO endcard still)
**Beat:** Eyes roll almost to pleasure then snap to terror; red filament reflected in iris.  
**Camera:** Extreme CU eye.  
**Prompt summary:** extreme close-up striking green eye freckles edge of frame, red filament reflection, sweat, A24 title-card energy, elegant tease cliffhanger for Level 2.

---

## 8. BATCH / QUOTA PLAN (Heavy)

| Tier | Shots | Mode |
|------|-------|------|
| Hero still | 01, 03, 07, 10 | `grok-imagine-image` quality when available |
| Standard still | 02, 04, 05, 06, 08, 09 | standard image |
| Motion tests (optional L1) | 03, 07 | video **1.0** 6–8s after plate lock |
| Hold 1.5 | until Level 2+ or user `ACTIVATE IMAGINE_VIDEO_1.5_FULL` |

**Rough L1 still package:** ~10 images · hero-first · i2v only after Identity Lock QA on plates.

---

## 9. PIPELINE GATES

1. DNA inject on every prompt  
2. Plate QA (identity + L1 coverage) before any video  
3. Chain QA if extend  
4. No Level 2+ content without user unlock  
5. ErosForge sign-off on any wardrobe drop below L1  

**Post:** QA → grade (sickly amber/teal) → AI Polish only on Go masters  

---

## 10. TITLE VOTE — **LOCKED**

| # | Title | Result |
|---|--------|--------|
| 1 | Carnal Veil | — (optional subtitle / series tag) |
| **2** | **The Parasite of Pleasure** | **SELECTED · LOCKED** |
| 3 | Ecstasy's Curse | — |
| 4 | Brothel Entity | — |
| 5 | Orgasmic Possession | — |

**On-screen / marketing primary:** *The Parasite of Pleasure*  
**Optional secondary line:** *A Carnal Veil story* (or omit)

---

## 11. FILES & STATE

| Asset | Path |
|-------|------|
| CLI Bible JSON | `artifacts/bibles/carnal_veil_bible.json` |
| This export | `artifacts/bibles/Carnal_Veil_Level1_v1.md` |
| DNA | `characters/elena-voss/` |
| Sequence | `sequences/carnalveil-level1/` |
| Example seed | `examples/production_bibles/Carnal_Veil_The_Parasite_of_Pleasure.md` |

---

## 12. DIRECTOR'S NOTES — ranked

1. **Title locked** — *The Parasite of Pleasure* (vote #2); optional subtitle “Carnal Veil”  
2. **Generate Shot 01 hero plate** with DNA inject (still first)  
3. Lock plate → optional 1.0 motion on 03/07  
4. Do **not** escalate past L1 without unlock  
5. API path blocked → use session tools or Imagine Bridge  

---

*Carnal Veil Level 1 v1 — Elegant Tease · Identity Lock · SuperGrok Heavy · Studio v3.8.6*
