# Studio Academy — FAQ

Common beginner blockers for **Grok Imagine Cinematic Studio**.  
Pair with the [Delivery Checklist](./DELIVERY_CHECKLIST.md).

---

## Getting started

### Where do I begin if I’m overwhelmed by 25 agents?

Start **stills-first**, not full studio:

1. **Prompt lab / Ultimate Template** — one cinematic still  
2. **Character DNA** — lock the face before a second shot  
3. **DoP card** — one lighting + lens + grade system  
4. Only then activate Director + more agents  

Tier path: single still → two-agent (Director + Prompt Master) → full pipeline.

### Do I need every agent for a teaser?

No. A solid micro-teaser often needs:

- Imagine Prompt Master (or Lab)  
- Identity Lock / DNA  
- DoP (or a locked look card)  
- Optional: QA before any extend  

Activate more only when the problem appears (continuity, long-form, trailer cut, etc.).

---

## Character DNA & identity

### Why does the face change every shot?

Usually one of:

- DNA **not prepended** to the packet  
- Identity CU written as a **cropped wide** (use 50–85mm language)  
- `transform_allowed: true` when it should be frozen  
- Grade/lighting so different the face “reads” as another person  

**Fix:** inject DNA on every packet · lock plates · same DoP · identity stills before video.

### What goes in a DNA inject block?

Minimum:

- `character_id` / name  
- `face_lock` (age band, features, hair, marks)  
- `wardrobe_lock`  
- props if recurring  
- `transform_allowed: false` for frozen leads  

Prepend the block; don’t bury it at the end of a long prompt.

### Can I use a real celebrity face?

Keep educational and original-character workflows. For public demos and shared packs, prefer **fictional adults** with clear DNA — cleaner rights story and fewer policy edge cases.

---

## Plates, stills, and video

### What is a “plate lock”?

A **locked still** (composition, light, identity, grade) that is approved before image-to-video or extend spend.  

Rule: **no i2v / 6s hero clip until `plate_status = locked`.**

### Why stills-first?

- Cheaper iteration  
- Identity and lighting debug without burning video seconds  
- Still montage is a valid teaser delivery  
- Failed motion loops cost more than a second still pass  

### How many stills before video?

Typical Academy path:

- 1 identity / DNA check still  
- 1–2 hero plates (MS + optional CU)  
- 1 wide establish  
- **Then** optional single slow push-in from the best locked plate  

---

## Continuity & extends

### What is LAST_FRAME_RECAP?

A short record of the **last approved frame**: pose, wardrobe, prop side, light direction, framing, and **`motion_out`** (how energy leaves the frame).  

Clip N+1 must inherit that state or the chain drifts.

### Extend looks like a new scene. Why?

Common causes:

- Missing recap / wrong `motion_out`  
- New focal length or grade not in the DoP card  
- DNA omitted on the extend packet  
- Too many moves in one 6s clip  

**Fix:** one primary move · shared DoP · DNA on · recap filled · QA Go before stitch.

### When do I stop and replan?

Stop on **identity No-Go**. Do not stitch. Fix DNA/plate, then continue. Use arc replan only for remaining beats — don’t casually rewrite the Bible mid-chain.

---

## Lighting, lens, color

### My shots don’t feel like one film.

Lock a **DoP card** once:

- format / aspect  
- lens set (e.g. 35 + 50)  
- key / fill / practicals  
- grade look + skin protection line  

Every packet inherits it. Random 18mm then 135mm without coverage logic breaks the show.

### Skin looks wrong under a “cinematic” grade.

Always add a **skin protection** line when stylizing (teal shadows, neon gels, bleach). Faces fail before backgrounds do.

### Which focal length for faces?

- **50mm** — default identity / MCU  
- **85mm** — portrait isolation  
- Avoid ultra-wide for beauty/identity locks  

---

## Editing & sound

### What’s the simplest teaser structure?

**Wide → medium → close → button.**  
Hard cuts. Still montage at 1.5–3s per image is valid.

### Do I need music?

Not at first. **Silent-first** is allowed and often smarter until the picture spine works mute. Add a short sound brief after picture lock.

### Sound brief pattern

```text
duration · music · atmos · foley · sfx hits (timecodes) · vo · do_not
```

One hero sound event at a time. Trait-based music (mood/tempo), not “exactly like [famous track].”

---

## Quota, cost, and API

### How do I not blow quota?

- Stills before video  
- Standard stills for exploration; quality/hero only when locked  
- One simple move per short clip  
- No extends on No-Go plates  
- Use Budget / Quota tools before batch sessions  

### Are pricing numbers in Academy official?

Treat published **list rates** as reference; confirm current xAI pricing in official docs. Academy budget tools are educational estimators.

### Prompt Lab / enhance does nothing offline?

Graceful degradation: templates and copy still work without a live key. Enhance/generation needs a configured API path where available.

---

## Agents & activation

### Activation order?

Typical safe order:

1. Studio Director (if coordinating)  
2. Identity Lock / DNA  
3. DoP  
4. Prompt Master  
5. Generators / Sequence / QA as needed  

Locks before generators.

### What does “activation” actually do?

It loads a specialist Role Card and skill surface into the session. Re-activating refreshes context; it doesn’t create a second independent instance.

---

## Project pack & export

### What’s in a Project pack?

Optional bundle:

- Bible lite  
- Character DNA  
- DoP card  
- Shot list  
- Color / motion notes  
- Budget hint  
- Activation block  

Toggle sections; copy into chat or notes.

### Delivery checklist vs Project pack?

| Tool | Role |
|------|------|
| **Delivery checklist** | Go / No-Go before ship |
| **Project pack** | Paste-ready charter export |

Run checklist → fix reds → export pack.

---

## Graduate & learning

### How do I “graduate” in Academy?

Typical gates (local progress):

- All learn tiers marked complete  
- Quiz best score at threshold  
- Enough flashcards mastered  

Certificate is a **learning milestone**, not an official xAI credential.

### Craft path order?

Lighting → Framing → Aspect → Lenses → Movement → Color → Editing → Sound → DoP / Lab / Pack.

---

## Quick fixes cheat sheet

| Symptom | First check |
|---------|-------------|
| Face drift | DNA inject · 50–85mm · plate lock |
| “Different movies” | DoP card · one grade · lens set |
| Bad extend | Recap · motion_out · one move · QA |
| Expensive chaos | Stills-first · budget before batch |
| Weak teaser | Spine: wide → MS → CU → button |
| Muddy mix | One hero sound event · picture first |

---

## Related Academy docs

- `DELIVERY_CHECKLIST.md` — final ship gate  
- Craft hub modules 01–08  
- Project pack · DNA builder · Recap builder · Consistency algorithms  

---

*Studio Academy — educational companion for Cinematic Studio. Independent learning tool; not an official xAI product.*
