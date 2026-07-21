---
name: ai-image-recreation
description: AI recreation editing style transfer enhancement and variation of user-uploaded images via Grok Imagine image_edit and image_gen. Activate when an uploaded image is recreated restyled enhanced varied transformed into storyboards mockups design sheets or restored. Grok 4.5 orchestration with multi-pass refinement Identity Lock handoff and pre-video plate prep for SuperGrokPro and Cinematic Studio. Optimized for grok-4-auto grok-v9-4p5-multi grok-v9-4p5-chat-expert with dual Imagine Video 1.0 and 1.5 Native.
---

# AI Image Recreation v3.8.6 (Grok 4.5 / v9-4p5 · Imagine Image)

**Scope:** User-uploaded (or path-provided) reference images → faithful recreation, style transfer, enhancement, restoration, variation, and production-ready plates.

**Sibling skills:** `generated-image-editor` (session Grok outputs by ID/path) · `i2i-cinematic-refiner` / `i2i-refiner` (multi-pass cinematic / explicit polish) · `imagine` (core tool craft) · `character-dna-extractor` (identity lock from refs)

## Model Layer (Grok 4.5 / v9-4p5)

| Task type | Preferred model | Reasoning |
|-----------|-----------------|-----------|
| Multi-agent orchestration / handoff synthesis | `grok-v9-4p5-multi` | high |
| Specialist deep craft / QA / identity-critical | `grok-v9-4p5-chat-expert` | high |
| Routine status / draft passes | `grok-4-auto` | medium |

**Stack default:** cinematic+Build API/chat **`grok-4.5`** (CLI ≥ 0.2.93 · fork `grok-build`). Opt-in 1M: `grok-4.3`.  
**Registry:** `tools/models.py` · `references/agents/MODEL_LAYER_v4.5.md` · `models verify`

```yaml
model_compatibility:
  - grok-v9-4p5-chat-expert
  - grok-v9-4p5-multi
  - grok-4-auto
preferred_model: grok-v9-4p5-chat-expert
```

### Imagine Video dual-path (when this skill touches video)
- **1.5 Native** — preferred for hero / final motion with audio when budget allows
- **1.0** — cost default / draft / pre-viz; label outputs so downstream agents do not assume 1.5 capabilities

## When to Activate

- Uploaded or path-referenced image + recreate / edit / restyle / enhance / vary / transform / restore
- Cinematic storyboard frames, product mockups, character design sheets, environmental immersion
- Archival / low-res restoration and commercial retouch
- Pre-video hero plates from user photos before `image_to_video` or Studio pipeline
- User says: `ACTIVATE AI_IMAGE_RECREATION`, `RECREATE THIS IMAGE`, `STYLE TRANSFER`, `ENHANCE THIS PHOTO`, `VARIATIONS FROM UPLOAD`

## When NOT to Use

| Situation | Use instead |
|-----------|-------------|
| Pure text-to-image, no reference | `image_gen` + `imagine` skill |
| Iterate on **Grok-generated** session assets | `generated-image-editor` |
| Multi-pass cinematic polish with strength curves | `i2i-cinematic-refiner` (SFW) or `i2i-refiner` (explicit) |
| Forensic DNA + long-sequence identity | `character-dna-extractor` → Identity Lock |
| Basic crop/resize/mux only | `ffmpeg` / `cinematic-ffmpeg` |
| Full multi-agent film production | `grok-imagine-cinematic-studio` / Studio Director |

## Activation

```
ACTIVATE AI_IMAGE_RECREATION
```

Begin work with: **"Initiating AI Image Recreation Protocol v3.8.6 (Grok 4.5 / v9-4p5)…"**

## Tool Map (Grok Build Imagine)

| Goal | Tool | Notes |
|------|------|--------|
| Recreate / restyle / enhance from upload | **`image_edit`** | Primary path. Pass absolute path, attachment token, or `data:image/...;base64,...` |
| New composition loosely inspired by description only | **`image_gen`** | Only when pixel reference is not required |
| Multiple variations | Multiple parallel **`image_edit`** calls | No `n`/`count` param — one call per variation |
| Still → motion | **`image_to_video`** | After plate is approved; prefer 6s shots |
| Multi-ref motion | **`reference_to_video`** | When user needs multi-image style/content blend |
| Named real person | **`image_edit` + real reference** | Never pure `image_gen` for real likeness |

**Rules aligned with `imagine` skill:**
1. Prefer `image_edit` whenever a source image exists.
2. For real people: reference-first; never non-consensual sexualized or minor-involving likenesses.
3. Describe what to **change** and what must **stay**; front-load subject and intent.
4. On moderation block: stop, do not paraphrase to evade; offer a different direction.
5. Save outputs under `artifacts/` (or session artifacts path) with descriptive names.

### `image_edit` contract

- **prompt** — desired outcome + fidelity anchors (2–6 sentences; natural prose)
- **image** — one or more refs (prefer one clean primary for reliability)
- **aspect_ratio** — multi-image edits / reframe; single-image edits often preserve source AR

### `image_gen` contract

- **prompt** — full scene description
- **aspect_ratio** — e.g. `1:1`, `16:9`, `9:16`, `4:3`, `3:4`, `auto`

## Core Principles

1. **User intent first** — faithful copy, style transfer, targeted edit, enhancement, or exploratory variations.
2. **Fidelity anchors** — composition, subjects, poses, camera angle, lighting direction, identity markers unless the user wants change.
3. **Multi-pass by default for “pro / hero / delivery”** — do not burn quota on one-shot hopes for hard jobs.
4. **Consistency tokens** — for series work, lock face/body/style phrases; escalate to DNA Extractor when characters will recur in video.
5. **Artifact hygiene** — descriptive filenames, paths reported, ready for DNA / i2i / i2v handoff.
6. **Safety** — follow platform safety; adult content only when clearly requested by adults; escalate cinematic NSFW sequences to ErosForge.

## Step-by-Step Workflow

### 1. Identify the source

Confirm accessibility:

- Attachment / render token (e.g. session image reference)
- Absolute path (`…/artifacts/upload.jpg`, `/home/workdir/artifacts/…`)
- Prior recreation path for chained passes

If unclear, ask once for the path or re-upload.

### 2. Classify the job

| Mode | Intent signals | Default tool plan |
|------|----------------|-------------------|
| **Faithful** | “exact”, “same”, “restore”, “upscale detail” | 1–2× `image_edit` fidelity + polish |
| **Style transfer** | “as Ghibli / oil / cyberpunk / …” | Fidelity anchors + style layer; optional 2nd polish |
| **Targeted edit** | change bg, outfit, expression, remove object | Describe **only** changes + preserve list |
| **Enhance / restore** | low-res, old photo, noise | Restoration templates; light second pass if needed |
| **Variations** | “3 looks”, “outfit pack” | N parallel `image_edit` with shared anchors |
| **Env immersion** | place subject in new world | Subject lock + environment rewrite |
| **Design sheet** | turnaround, expressions | Multi-call grid of views from same DNA anchors |
| **Storyboard plate** | pre-video, cinematic still | Photoreal cinematic template + AR for shot |
| **Product / mockup** | e-commerce, packaging | Studio lighting + material accuracy templates |

### 3. Craft the prompt

Layer in order:

1. **Intent lead** — recreate / restyle / enhance / vary…
2. **Fidelity anchors** (from `references/prompt-library.md` §1)
3. **Creative layer** — style, mood, environment, product brief
4. **Quality boosters** — detail, sharpness, anatomy, lighting (avoid empty keyword spam)
5. **Hard constraints** — “preserve text exactly”, “anatomically correct hands”, “identical eye color and freckle pattern”

Load ready templates from:

- `references/prompt-library.md` — full library (styles, restore, storyboard, product, adult intensity tiers)
- `references/adult-cheat-sheet.md` — fast R-rated intensity + category keywords

### 4. Execute

```text
image_edit(
  prompt = "<layered prompt>",
  image = ["<source path or attachment>"],
  aspect_ratio = "<if reframing / multi-ref>"
)
```

For **variations**, fire distinct prompts in parallel (one call each).  
For **multi-pass**, chain: pass-1 output path → pass-2 `image_edit` input.

### 5. Multi-Pass Refinement Protocol (v3.7.1)

Trigger when user asks high quality / hero / pro grade, or first pass fails QA.

| Pass | Focus | Prompt bias |
|------|--------|-------------|
| **1 · Structure** | Composition, pose, identity, major lighting | High fidelity anchors; allow intended style change |
| **2 · Identity / material** | Face, hands, materials, text, product edges | “Preserve pass-1 layout; refine only …” |
| **3 · Polish** | Sharpness, color harmony, film/cinematic grade, artifact cleanup | Minimal structural change |

**Pass count guidance:**

- Simple enhance or mild style: **1** pass
- Style transfer + identity: **2** passes
- Hero plate / design sheet / pre-video: **2–3** passes
- After 3 fails on identity → hand off to `character-dna-extractor` + `i2i-cinematic-refiner`

### 6. Consistency Engine (series & cast)

When producing ≥2 related images:

1. Write **3–7 consistency anchors** (face shape, hair, scars, wardrobe color, lens feel).
2. Inject the same anchor block into every prompt.
3. Prefer **edit-from-best-plate** rather than fresh `image_gen` for each frame.
4. For recurring characters entering Studio video:  
   `ACTIVATE Character DNA Extractor` → Identity Lock → then more recreations.

### 7. Review & QA (before presenting)

- [ ] Intent applied (style / edit / enhance) without unwanted side effects  
- [ ] Core subjects & composition preserved unless deliberately changed  
- [ ] Hands, eyes, text, logos checked when critical  
- [ ] No obvious melt / extra limbs / identity swap  
- [ ] File path noted under `artifacts/`  
- [ ] Ready for next step (iterate / DNA / i2v / documents)

### 8. Save & report

Prefer:

```text
artifacts/recreation_<mode>_<slug>_<passN>.png
```

End with a short **Recreation Report** (see Output Format).

## Mode Playbooks (quick)

### Faithful recreation / enhancement

> Ultra-faithful recreation of the reference. Exact composition, subjects, poses, camera angle, lighting direction. Only improve sharpness, detail, dynamic range, and remove noise. No content changes.

### Style transfer

> Exact scene and layout of the reference, reimagined in [STYLE]. Preserve subjects, poses, spatial relationships. [style descriptors]. Photoreal/illustration quality as appropriate.

### Environmental immersion

> Keep this exact subject identity and pose; fully replace environment with [WORLD]. Match lighting direction on subject to new environment; realistic contact shadows and color bounce.

### Character design sheet

Produce separate `image_edit` calls (or sequenced): front, 3/4, side, back, expression set — shared DNA anchors every call. Optional grid composite via later edit if needed.

### Cinematic storyboard keyframe

> Cinematic film still from the reference subject, [shot size], [lens feel], subtle grain, color grade for [genre], motion-ready clarity for image-to-video. Lock identity and wardrobe.

### Product / commercial

> Commercial product plate: accurate materials, controlled studio light, clean reflections, catalog-ready, preserve logo/text legibility.

## Reasoning & Cache (Grok 4.5)

| Task | Reasoning | Cache |
|------|-----------|--------|
| Trivial single restyle | medium | optional |
| Multi-pass hero / identity | **high** | `prompt_cache_key` = project slug |
| Design sheet batch | high | same key across batch |
| Long multi-ref memory | opt-in `grok-4.3` only if context > ~400k | long bank key |

## Integration Chain

```
User upload
  → AI Image Recreation (this skill)
      → optional Character DNA Extractor (recurring cast)
      → optional i2i-cinematic-refiner / i2i-refiner (polish)
      → Imagine Prompt Master (if entering full Studio prompts)
      → image_to_video / Sequence Director / Studio Director
      → Reference Asset Curator (hero vs draft tier)
```

| Downstream need | Activate |
|-----------------|----------|
| Motion from approved still | `image_to_video` or `ACTIVATE I2V_SPECIALIST` |
| Full production | `ACTIVATE STUDIO_DIRECTOR` / cinematic studio |
| Explicit sequence design | `ACTIVATE EROSFORGE` (after still recreation if needed) |
| Quota planning | `workflow-quota-optimizer` / `sfw-batch-orchestrator` |
| Docs / pitch | `pptx` / `pdf` with before/after artifacts |
| Imagine API / grok.com paste | `imagine-execution-bridge` / Agent Mode Handoff |

## NSFW / Adult Protocol

- Apply adult templates **only** when the user clearly requests adult content.
- Use intensity tiers (Light / Medium / Hardcore) from `references/adult-cheat-sheet.md`.
- Keep fidelity anchors so identity does not drift under style escalation.
- For multi-clip intimate **video** pipelines, hand off to **ErosForge** + NSFW sequence tools; this skill remains the still/upload recreation specialist.
- Never process sexual content involving minors; refuse clearly.

## Output Format

```text
AI IMAGE RECREATION COMPLETE · v3.7.1
Mode: <faithful|style|edit|enhance|variation|sheet|storyboard|product>
Passes: <n> | Reasoning: <medium|high>
Source: <path or attachment>
Outputs:
  - artifacts/...
Consistency anchors: <3–7 bullets or n/a>
QA: <pass / notes>
Next recommended: <iterate | DNA | i2i | i2v | Studio Director | done>
```

## References (load on demand)

| File | Use |
|------|-----|
| `references/prompt-library.md` | Templates: fidelity, styles, restore, variations, storyboard, product, adult |
| `references/adult-cheat-sheet.md` | Fast intensity + category keywords |
| `~/.grok/skills/imagine/SKILL.md` | Global image_gen / image_edit craft rules |
| Studio `MODEL_LAYER_v4.5.md` | Canonical model stack |

## Quality Bar

- Prefer **one strong pass** over five vague retries; escalate structure when stuck.
- Prefer **edit chain from best plate** for series consistency.
- Prefer **DNA + Identity Lock** before expensive video on a face from an upload.
- Never invent tool parameters; never treat Imagine image/video slugs as chat models.

---

*AI Image Recreation v3.8.6 — Grok 4.5 / v9-4p5 orchestration · Imagine image_edit / image_gen · SuperGrokPro + Cinematic Studio compatible*
