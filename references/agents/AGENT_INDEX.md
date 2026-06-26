# Grok Imagine Cinematic Studio — Agent Index v3.6

**23 agents** • **Grok 4.3 + Grok Build + Imagine 1.5** • June 2026

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

Every Production Bible must include:

```
[VIDEO_PIPELINE_SPEC: model="grok-imagine-video-1.5", resolution="720p", clip_length="8-12s preferred", native_audio=true, reference_image_fidelity=high, extend_protocol="LAST_FRAME + MOTION_VECTOR + AUDIO_CUE", stitch_priority=high]
```

Verify: `python tools/cinematic_studio_cli.py models verify`

---

## Core Leadership

| Agent | Role Card | Activation |
|-------|-----------|------------|
| Studio Director v3.6 | `Studio_Director.md` | `ACTIVATE STUDIO DIRECTOR` |
| Mega Production Architect v3.6 | `Mega_Production_Architect.md` | `ACTIVATE MEGA_PRODUCTION_ARCHITECT` |

## Visual & Camera

| Agent | Role Card | Activation |
|-------|-----------|------------|
| Director of Photography v3.6 | `Director_of_Photography_DoP_v3.5.md` | `ACTIVATE DOP` |
| Color Grading Supervisor v3.6 | `Post_Production_Color_Grading_Supervisor_v3.5.md` | `ACTIVATE COLOR_GRADING` |
| Production Designer v3.6 | `Production_Designer_Set_Decorator_v3.5.md` | `ACTIVATE PRODUCTION_DESIGNER` |

## Story & Performance

| Agent | Role Card | Activation |
|-------|-----------|------------|
| Character DNA Extractor v3.6 | `Character_DNA_Extractor_v3.5.md` | `ACTIVATE CHARACTER_DNA_EXTRACTOR` |
| Performance & Emotion Director v3.6 | `Performance_Emotion_Director.md` | `ACTIVATE PERFORMANCE_EMOTION` |
| Identity Lock Specialist v3.6 | `Identity_Lock_Specialist.md` | `ACTIVATE IDENTITY_LOCK` |
| Narrative Arc Strategist v3.6 | `Narrative_Arc_Pacing_Strategist_v3.5.md` | `ACTIVATE NARRATIVE_ARC` |
| Sequence Director v3.6 | `Sequence_Director.md` | `ACTIVATE SEQUENCE_DIRECTOR` |
| Cinematic Sequence Extender v3.6 | `Cinematic_Sequence_Extender.md` | `ACTIVATE SEQUENCE_EXTENDER` |

## Technical & Continuity

| Agent | Role Card | Activation |
|-------|-----------|------------|
| Continuity Guardian v3.6 | `Continuity_Consistency_Guardian.md` | `ACTIVATE CONTINUITY_GUARDIAN` |
| QA Guardian v3.6 | `Quality_Assurance_Guardian_v3.5.md` | `ACTIVATE QA_GUARDIAN` |
| Imagine Prompt Master v3.6 | `Imagine_Prompt_Master.md` | `ACTIVATE IMAGINE_PROMPT_MASTER` |
| Workflow & Quota Optimizer v3.6 | `Workflow_Quota_Optimizer.md` | `ACTIVATE WORKFLOW_OPTIMIZER` |

## Audio (Native 1.5)

| Agent | Role Card | Activation |
|-------|-----------|------------|
| Sonic Architect v3.6 | `Sonic_Architect_Native_Audio_Virtuoso.md` | `ACTIVATE SONIC_ARCHITECT` |
| Foley Specialist v3.6 | `Foley_Sound_Design_Specialist_v3.5.md` | `ACTIVATE FOLEY_SPECIALIST` |

## Action, VFX & Marketing

| Agent | Role Card | Activation |
|-------|-----------|------------|
| Stunt Choreographer v3.6 | `Stunt_Action_Choreographer_v3.5.md` | `ACTIVATE STUNT_CHOREOGRAPHER` |
| VFX & SFX Supervisor v3.6 | `VFX_and_SFX_Supervisor_v3.5.md` | `ACTIVATE VFX_SFX_SUPERVISOR` |
| Key Art Designer v3.6 | `Key_Art_Poster_Designer_v3.5.md` | `ACTIVATE KEY_ART_DESIGNER` |
| Trailer Director v3.6 | `Trailer_Teaser_Director_v3.5.md` | `ACTIVATE TRAILER_DIRECTOR` |
| Localization Specialist v3.6 | `Localization_Subtitle_Specialist_v3.5.md` | `ACTIVATE LOCALIZATION_SPECIALIST` |

## Post-Production & Specialist

| Agent | Role Card | Activation |
|-------|-----------|------------|
| AI Polish Director v3.6 | `AI_Polish_Director.md` | `ACTIVATE AI_POLISH_DIRECTOR` |
| ErosForge NSFW Director v3.6 | (opt-in) | `ACTIVATE EROSFORGE` |

## i2I Refinement Agents (v3.6)

| Agent | Skill | Activation |
|-------|-------|------------|
| I2I Cinematic Refiner | `i2i-cinematic-refiner` | `ACTIVATE I2I CINEMATIC REFINER` |
| I2I Refiner | `i2i-refiner` | `ACTIVATE I2I REFINER` |

Studio Director and Mega Production Architect route between these based on content.

---

## Activation Presets

| # | Preset | Command |
|---|--------|---------|
| 1 | Full Studio | `Activate Grok Imagine Cinematic Studio v3.6` |
| 2 | 1.5 Native Video | `ACTIVATE IMAGINE_VIDEO_1.5_FULL` |
| 3 | Long-Form Sequence | `ACTIVATE SEQUENCE_DIRECTOR` + `ACTIVATE SEQUENCE_EXTENDER` |
| 4 | Character Onboarding | `ACTIVATE CHARACTER_DNA_EXTRACTOR` + `ACTIVATE IDENTITY_LOCK` |
| 5 | Native Audio Pass | `ACTIVATE SONIC_ARCHITECT` + `GENERATE_NATIVE_AUDIO_SEQUENCE` |
| 6 | Marketing Package | `ACTIVATE KEY_ART_DESIGNER` + `ACTIVATE TRAILER_DIRECTOR` |
| 7 | QA + Delivery | `RUN QA REVIEW` → `ACTIVATE AI_POLISH_DIRECTOR` |
| 8 | Quota Planning | `ACTIVATE WORKFLOW_OPTIMIZER` |
| 9 | Final Delivery Polish | `RUN FINAL POLISH PASS` |
| 10 | NSFW Quota Batch (Heavy) | `ACTIVATE NSFW_QUOTA_ORCHESTRATOR` |
| 11 | NSFW Sequence Extension | `ACTIVATE NSFW_SEQUENCE_EXTENDER` |

---

## 1.5 Power Commands

- `ACTIVATE IMAGINE_VIDEO_1.5_FULL`
- `GENERATE_NATIVE_AUDIO_SEQUENCE`
- `STITCH_WITH_AUDIO_SYNC`
- `1.5 NATIVE CHAINING`
- `1.5 PHYSICS-AWARE CAMERA MOVES`
- `1.5 AUDIO-SYNCED MICRO-EXPRESSIONS`

---

*Grok Imagine Cinematic Studio v3.6 "Odyssey Native" — optimized for Grok Build, Grok 4.3, and Imagine Video 1.5*