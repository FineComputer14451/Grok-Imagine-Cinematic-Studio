# Characters / Props / Locations — reference workflow

**Default:** auto-create plates on Quality / Image **2.0** — see `GENERATE.md`.  
`explain` / `checklist-only` = docs only.

Refs are **identity locks**, not one-off pretty frames. Build a reusable plate set first; later shots edit or i2v from those plates.

## 0. Pin the model layer

- Hero / lock plates → Quality Mode = Image **2.0** (`ACTIVATE IMAGINE_MODEL_OVERRIDES hero` or `balanced`)
- Draft exploration → Fast = Image **1.0** (`draft`)
- Never lock DNA on Fast
- Planning / DNA text → Chat **Expert** or API `grok-4.6`

## 1. Characters (DNA → plates)

1. `dna init` / extract DNA: look, age, wardrobe, marks, vibe  
2. **Auto-generate** 3–6 stills on Quality: front, 3/4, profile, full body (± expression / wardrobe)  
3. Pick 1–2 hero plates as the lock; name them  
4. Later: image edit or i2v from the hero — not a blank prompt  

## 2. Props

1. One-liner: what / scale / material / era / marks  
2. **Auto-generate** hero angle + reverse (± detail/macro)  
3. Lock one clean plate; keep scale vs characters  
4. Reuse via edit / reference image  

## 3. Locations

1. Bible: time, weather, architecture, landmarks, grade  
2. **Auto-generate** establishing plate + 2–3 coverage angles (shared lighting language)  
3. Establish = location lock  
4. Action: i2v / edit / multi-ref composite into the space  

## 4. Board

Folders: `characters/` · `props/` · `locations/`  
Each asset: hero plate + optional variants + DNA one-liner. Hero tiers stay on Image **2.0**.  
Optional: `board/manifest.json` for automated cross-check.

## 4b. Post-board cross-ref check

```bash
python scripts/cross_ref_check.py .
```

Fail on missing DNA, slug mismatches, or plates listed in DNA/manifest that are not on disk.  
Details: `CROSS_REF_CHECK.md`. Demo pack: `samples/onboarding-demo/`.

## 5. Motion (after locks — only if asked)

- Plate → video + audio → Video **1.5**  
- Edit / extend → Video **1.0 only**  
- Don’t mix 1.0 + 1.5 in one chain without continuity  

## Order that works

**Location establish → character heroes → key props → board review → cross-ref check → sequence stills → video.**
