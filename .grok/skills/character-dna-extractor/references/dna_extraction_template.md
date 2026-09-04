# Character DNA Extraction Template v3.7.1 (Grok 4.6)

Use this template when building a DNA profile from reference images. Persist as `characters/{slug}/dna.json` via `dna save` after filling.

**Orchestration:** `grok-4.6` · reasoning **high** · `prompt_cache_key` = project slug  
**Video pipeline:** lock `video_pipeline_spec` from registry (1.0 cost default; 1.5 for native audio)

---

## Character: [NAME]

**Slug:** `[auto-slug]`  
**Version:** `1`  
**Cinematic Viability Score:** [1-10] — rationale:  
**Source References:** [count] images (list paths / Imagine IDs)  
**Extraction Mode:** [lite | forensic | multi-ref synthesis | nsfw]  
**Identity Lock Status:** pending  
**Extracted at:** [ISO-8601]

### Core Identity
- Age range:
- Ethnicity / skin tone (visible only):
- Body type / height / build:
- Signature recognizability (one sentence):

### Facial DNA
- Eye color / shape / spacing / catchlights:
- Nose / lips / jawline / cheek structure:
- Scars / tattoos / piercings (**visible only**):
- Micro-asymmetries:
- Skin texture / undertone:

### Hair & Grooming
- Color / length / texture:
- Style / parting / accessories:
- Motion behavior (wind, turn, run):

### Clothing & Style
- Current outfit (visible):
- Fabric / fit / color palette:
- Signature wardrobe elements (series-stable only):

### Movement & Posture
- Default posture:
- Gait / gesture tendencies:
- Physical presence / energy:

### Emotional Baseline
- Default emotional temperature:
- How emotion manifests physically:
- Micro-expression tendencies:

### Motion DNA (Video / I2V)
- Fabric dynamics:
- Hair response to motion:
- Weight / momentum feel:
- Camera-facing behavior:
- LAST_FRAME_RECAP-friendly notes:

### Key Consistency Anchors (non-negotiable, 3–7)
1.
2.
3.
4.
5.

### Reference Weights
- primary_ref_weight: `0.85`
- secondary_ref_weight: `0.15`
- primary_ref_id / path:
- secondary_ref_ids / paths:

### Variant Notes (multi-ref only)
- Hero ref (elected):
- Ref 1 contributes:
- Ref 2 contributes:
- Conflicts resolved by:
- Irreconcilable (flag for user):

### NSFW Consistency Notes (opt-in, visible content only)
- Include **only** if erotic/suggestive content is clearly visible.
- Clinical anchors only; no invented anatomy.

### Inferences (not confirmed)
- List any `inferred — confirm with user` items separately from fact fields.

### Prompt Injection Modes to Generate
- [ ] compact
- [ ] cinematic
- [ ] close_up
- [ ] sequence_starter
- [ ] video_1.0 (cost default)
- [ ] video_1.5 (native audio / physics)

### Ready for Chaining
- Recommended next agents: Identity Lock Specialist · Studio Director · Imagine Prompt Master
- Optional: Multi-Character Identity Arbiter · ai-image-recreation (design sheets) · I2V Specialist · ErosForge
- Identity Lock handoff:
  ```bash
  python tools/cinematic_studio_cli.py dna handoff --name "[NAME]"
  python tools/cinematic_studio_cli.py dna lock --name "[NAME]"
  python tools/cinematic_studio_cli.py dna inject --name "[NAME]" --mode cinematic
  ```

### Design Sheet Prompt Seeds (optional → ai-image-recreation)
- Front orthographic:
- Three-quarter:
- Side profile:
- Back:
- Expression set (neutral / smile / intense):

Use shared Key Consistency Anchors in every sheet prompt.
