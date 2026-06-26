# Grok Imagine Cinematic Studio — Agent Index v3.6.5

**23 core agents** · **+9 specialists** (pipeline + i2i + NSFW opt-in) · **Grok 4.3 + Grok Build + Imagine 1.5** · June 2026

Authoritative Role Cards: `references/agents/*.md`  
Model registry: `tools/models.py`, `references/MODELS_v3.6.md`

---

## Model Compatibility (Required)

| Layer | Slug | Use |
|-------|------|-----|
| Grok Build CLI | `grok-composer-2.5-fast` | Local agent orchestration |
| Grok Build fork | `grok-build` | Code, skills, repo tooling |
| xAI Chat | `grok-4.3` | 1M-context Production Bibles |
| xAI Build API | `grok-build-0.1` | Agentic automation |
| Imagine Video | `grok-imagine-video-1.5` | Native audio video |
| Imagine Image | `grok-imagine-image` | Reference stills |
| Imagine Image Quality | `grok-imagine-image-quality` | Hero keyframes |

Every Production Bible must include:

```
[VIDEO_PIPELINE_SPEC: model="grok-imagine-video-1.5", resolution="720p", clip_length="8-12s preferred", native_audio=true, reference_image_fidelity=high, extend_protocol="LAST_FRAME + MOTION_VECTOR + AUDIO_CUE", stitch_priority=high]
```

Verify: `python tools/cinematic_studio_cli.py models verify`

---

## Core Leadership

| Agent | Role Card | Activation |
|-------|-----------|------------|
| Studio Director v3.6.5 | `Studio_Director.md` | `ACTIVATE STUDIO DIRECTOR` |
| Mega Production Architect v3.6.5 | `Mega_Production_Architect.md` | `ACTIVATE MEGA_PRODUCTION_ARCHITECT` |

## Visual & Camera

| Agent | Role Card | Activation |
|-------|-----------|------------|
| Director of Photography v3.6.5 | `Director_of_Photography_DoP_v3.5.md` | `ACTIVATE DOP` |
| Color Grading Supervisor v3.6.5 | `Post_Production_Color_Grading_Supervisor_v3.5.md` | `ACTIVATE COLOR_GRADING` |
| Production Designer v3.6.5 | `Production_Designer_Set_Decorator_v3.5.md` | `ACTIVATE PRODUCTION_DESIGNER` |

## Story & Performance

| Agent | Role Card | Activation |
|-------|-----------|------------|
| Character DNA Extractor v3.6.5 | `Character_DNA_Extractor_v3.5.md` | `ACTIVATE CHARACTER_DNA_EXTRACTOR` |
| Performance & Emotion Director v3.6.5 | `Performance_Emotion_Director.md` | `ACTIVATE PERFORMANCE_EMOTION` |
| Identity Lock Specialist v3.6.5 | `Identity_Lock_Specialist.md` | `ACTIVATE IDENTITY_LOCK` |
| Narrative Arc Strategist v3.6.5 | `Narrative_Arc_Pacing_Strategist_v3.5.md` | `ACTIVATE NARRATIVE_ARC` |
| Sequence Director v3.6.5 | `Sequence_Director.md` | `ACTIVATE SEQUENCE_DIRECTOR` |
| Cinematic Sequence Extender v3.6.5 | `Cinematic_Sequence_Extender.md` | `ACTIVATE SEQUENCE_EXTENDER` |

## Technical & Continuity

| Agent | Role Card | Activation |
|-------|-----------|------------|
| Continuity Guardian v3.6.5 | `Continuity_Consistency_Guardian.md` | `ACTIVATE CONTINUITY_GUARDIAN` |
| QA Guardian v3.6.5 | `Quality_Assurance_Guardian_v3.5.md` | `ACTIVATE QA_GUARDIAN` |
| Imagine Prompt Master v3.6.5 | `Imagine_Prompt_Master.md` | `ACTIVATE IMAGINE_PROMPT_MASTER` |
| Workflow & Quota Optimizer v3.6.5 | `Workflow_Quota_Optimizer.md` | `ACTIVATE WORKFLOW_OPTIMIZER` |

## Audio (Native 1.5)

| Agent | Role Card | Activation |
|-------|-----------|------------|
| Sonic Architect v3.6.5 | `Sonic_Architect_Native_Audio_Virtuoso.md` | `ACTIVATE SONIC_ARCHITECT` |
| Foley Specialist v3.6.5 | `Foley_Sound_Design_Specialist_v3.5.md` | `ACTIVATE FOLEY_SPECIALIST` |

## Action, VFX & Marketing

| Agent | Role Card | Activation |
|-------|-----------|------------|
| Stunt Choreographer v3.6.5 | `Stunt_Action_Choreographer_v3.5.md` | `ACTIVATE STUNT_CHOREOGRAPHER` |
| VFX & SFX Supervisor v3.6.5 | `VFX_and_SFX_Supervisor_v3.5.md` | `ACTIVATE VFX_SFX_SUPERVISOR` |
| Key Art Designer v3.6.5 | `Key_Art_Poster_Designer_v3.5.md` | `ACTIVATE KEY_ART_DESIGNER` |
| Trailer Director v3.6.5 | `Trailer_Teaser_Director_v3.5.md` | `ACTIVATE TRAILER_DIRECTOR` |
| Localization Specialist v3.6.5 | `Localization_Subtitle_Specialist_v3.5.md` | `ACTIVATE LOCALIZATION_SPECIALIST` |

## Post-Production

| Agent | Role Card | Activation |
|-------|-----------|------------|
| AI Polish Director v3.6.5 | `AI_Polish_Director.md` | `ACTIVATE AI_POLISH_DIRECTOR` |

---

## Production Pipeline (Tier 1)

| Agent | Role Card | Skill | Activation |
|-------|-----------|-------|------------|
| Reference & Asset Curator v3.6.5 | `Reference_Asset_Curator.md` | `reference-asset-curator` | `ACTIVATE REFERENCE_CURATOR` |
| Image-to-Video Specialist v3.6.5 | `Image_to_Video_Specialist.md` | `image-to-video-specialist` | `ACTIVATE I2V_SPECIALIST` |
| SFW Batch Orchestrator v1.0 | `SFW_Batch_Orchestrator.md` | `sfw-batch-orchestrator` | `ACTIVATE SFW_BATCH_ORCHESTRATOR` |
| Assembly Editor v3.6.5 | `Assembly_Editor.md` | `assembly-editor` | `ACTIVATE ASSEMBLY_EDITOR` |

**Order of operations:** Reference Curator → (i2i if needed) → I2V Specialist → generation/QA → Assembly Editor → color → polish.

---

## Refinement (i2i)

| Agent | Role Card | Skill | Activation |
|-------|-----------|-------|------------|
| I2I Cinematic Refiner v3.6.5 | `I2I_Cinematic_Refiner.md` | `i2i-cinematic-refiner` | `ACTIVATE I2I CINEMATIC REFINER` |
| I2I Refiner v3.6.5 | `I2I_Refiner.md` | `i2i-refiner` | `ACTIVATE I2I REFINER` |

Studio Director routes standard refinement to I2I Cinematic Refiner; explicit/intimate content goes to I2I Refiner + ErosForge.

---

## Specialist (Opt-in)

| Agent | Role Card | Skill | Activation |
|-------|-----------|-------|------------|
| ErosForge NSFW Director v3.6.5 | `ErosForge_NSFW_Director.md` | `erosforge-nsfw-director` | `ACTIVATE EROSFORGE` |
| NSFW Quota Orchestrator v1.0 | `NSFW_Quota_Orchestrator.md` | `nsfw-quota-orchestrator` | `ACTIVATE NSFW_QUOTA_ORCHESTRATOR` |
| NSFW Sequence Extender v1.0 | `NSFW_Sequence_Extender.md` | `nsfw-sequence-extender` | `ACTIVATE NSFW_SEQUENCE_EXTENDER` |

Requires explicit opt-in. NSFW orchestrator and extender require `ACTIVATE EROSFORGE` first.

---

## Activation Presets

| # | Preset | Command |
|---|--------|---------|
| 1 | Full Studio | `Activate Grok Imagine Cinematic Studio v3.6.5` |
| 2 | 1.5 Native Video | `ACTIVATE IMAGINE_VIDEO_1.5_FULL` |
| 3 | Long-Form Sequence | `ACTIVATE SEQUENCE_DIRECTOR` + `ACTIVATE SEQUENCE_EXTENDER` |
| 4 | Character Onboarding | `ACTIVATE CHARACTER_DNA_EXTRACTOR` + `ACTIVATE IDENTITY_LOCK` |
| 5 | Native Audio Pass | `ACTIVATE SONIC_ARCHITECT` + `GENERATE_NATIVE_AUDIO_SEQUENCE` |
| 6 | Marketing Package | `ACTIVATE KEY_ART_DESIGNER` + `ACTIVATE TRAILER_DIRECTOR` |
| 7 | QA + Delivery | `RUN QA REVIEW` → `ACTIVATE AI_POLISH_DIRECTOR` |
| 8 | Quota Planning | `ACTIVATE WORKFLOW_OPTIMIZER` |
| 9 | Final Delivery Polish | `RUN FINAL POLISH PASS` |
| 10 | NSFW Quota Batch (Heavy) | `ACTIVATE EROSFORGE` → `ACTIVATE NSFW_QUOTA_ORCHESTRATOR` |
| 11 | NSFW Sequence Extension | `ACTIVATE EROSFORGE` → `ACTIVATE NSFW_SEQUENCE_EXTENDER` |
| 12 | Keyframe Polish | `ACTIVATE I2I CINEMATIC REFINER` |
| 13 | Asset + Model Routing | `ACTIVATE REFERENCE_CURATOR` |
| 14 | Still → Video | `ACTIVATE I2V_SPECIALIST` |
| 15 | SFW Batch Session | `ACTIVATE SFW_BATCH_ORCHESTRATOR` |
| 16 | Rough Cut Assembly | `ACTIVATE ASSEMBLY_EDITOR` |

---

## 1.5 Power Commands

- `ACTIVATE IMAGINE_VIDEO_1.5_FULL`
- `GENERATE_NATIVE_AUDIO_SEQUENCE`
- `STITCH_WITH_AUDIO_SYNC`
- `1.5 NATIVE CHAINING`
- `1.5 PHYSICS-AWARE CAMERA MOVES`
- `1.5 AUDIO-SYNCED MICRO-EXPRESSIONS`

---

## Supporting Skills (Tier 1)

| Skill | Type | Activation |
|-------|------|------------|
| `ai-polish-director` | Agent | `ACTIVATE AI_POLISH_DIRECTOR` |
| `chain-qa-protocol` | Pipeline | `RUN CHAIN QA REVIEW` |
| `cinematic-ffmpeg` | Tool | After Assembly Editor + polish |
| `animatic-director` | Pipeline | `ACTIVATE ANIMATIC DIRECTOR` |
| `handoff-packet-validator` | Tool | Before extend / i2v handoffs |
| `production-bible-workflow` | Pipeline | `START PRODUCTION BIBLE WORKFLOW` |

---

*Grok Imagine Cinematic Studio v3.6.5 "Odyssey Native" — 23 core agents + 9 specialists + 6 Tier 1 skills*