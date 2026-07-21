# Grok Build Workflow: NSFW Outfit Batch Generation

**Project:** NSFW Outfit Prompt Library  
**Goal:** Generate high-quality, consistent R-rated NSFW images across 33 professional/roleplay outfits.  
**Model:** Grok Imagine (text-to-image + optional i2i refinement)  
**Library (explicit):** `prompts/NSFW_Outfit_Library.md`  
**Library (suggestive R):** `prompts/NSFW_Outfit_Library_Suggestive_R.md` — **33/33** (in-session path)  
**Negatives:** `prompts/NSFW_Outfit_Negatives.md`  
**Artifacts:** `artifacts/nsfw_outfits/batch_XX/`  
**Status:** Dual-track ready · **Suggestive R 33/33 generated**  
**Created:** 2026-07-19  
**Updated:** 2026-07-19 — Batches 1–6 suggestive R complete (`artifacts/nsfw_outfits/`)

## Active cell

- NSFW Quota Orchestrator  
- Workflow Quota Optimizer  
- ErosForge NSFW Director (adults 18+ only)  
- Identity Lock Specialist (only if same face across outfits)  
- Imagine Prompt Master  

## Batch map (Option B)

| Batch | Outfits | Count |
|-------|---------|-------|
| 1 | Schoolgirl, Hotwife, Nurse, French Maid, Secretary | 5 |
| 2 | Police Officer, Teacher, Flight Attendant, Cheerleader, Librarian | 5 |
| 3 | Waitress, Yoga Instructor, Pizza Delivery Girl, Mechanic, Bartender | 5 |
| 4 | Cowgirl, Personal Trainer, Lifeguard, Pilot, Chef | 5 |
| 5 | Artist, Firefighter, Veterinarian, Military, Race Car Driver | 5 |
| 6 | Photographer, Florist, Scuba Instructor, News Reporter, Ballerina, Pharmacist, Archaeologist, Astronaut | 8 |

## CLI

```bash
# Plan batch
python tools/cinematic_studio_cli.py nsfw plan "NSFW Outfit Library" \
  --budget 200 --file nsfw_batches/outfit_library_shots.json

# Next shots
python tools/cinematic_studio_cli.py nsfw next "nsfw-outfit-library" --count 5

# After each gen (example)
python tools/cinematic_studio_cli.py nsfw record "nsfw-outfit-library" shot_id \
  --score 8.0 --credits 5
```

## QC checklist

- [ ] Clear adult (18+) appearance  
- [ ] Correct outfit recognition  
- [ ] Anatomical accuracy (hands, breasts, proportions)  
- [ ] No major artifacts  
- [ ] Lighting / detail acceptable  
- [ ] Matches intended explicit level  

## Dual-track generation

| Track | When | Prompts |
|-------|------|---------|
| Suggestive R | In-session `image_gen` (moderation-safe) | `NSFW_Outfit_Library_Suggestive_R.md` |
| Explicit | grok.com/imagine bridge or API with credits | `NSFW_Outfit_Library.md` + `BRIDGE_PACKETS.md` |

Batch 1 suggestive R artifacts: `artifacts/nsfw_outfits/batch_01/*_suggestive_r.jpg`

## i2i refinement path

1. Select best stills under `artifacts/nsfw_outfits/`  
2. `image_edit` + i2i-refiner (strength from Negatives doc)  
3. Optional Identity Lock if consistent character across outfits  
