# Grok Imagine Cinematic Studio — Agent Index

> [!NOTE]
> Independent community project — **not affiliated with or endorsed by xAI**. Full notice: [DISCLAIMER.md](../../DISCLAIMER.md).

**Enhanced for:** `grok-4-auto` · `grok-v9-4p5-multi` · `grok-v9-4p5-chat-expert` + **Imagine Video 1.0 & 1.5 Native**  
**Version:** 3.11.3 (Role Cards carry v3.6.5–v4.5 labels) · **Studio:** v3.11.3 · Grok 4.6 stack · Full v4.5 dual-model wave  
**Date:** 2026-09-02  
**Canonical Model Layer:** `references/agents/MODEL_LAYER_v4.5.md` (v4.5.1)

> All agents below now reference the enhanced Model Layer. Prefer the three explicit v9-4p5 identifiers. Video work must declare `VIDEO_PIPELINE_SPEC` (1.0 default, 1.5 when native audio / physics / intimacy required).

Authoritative Role Cards: `references/agents/*.md`  
Shared model rules: `references/agents/MODEL_LAYER_v4.5.md`  
Imagine Agent Mode Handoff: `references/agents/IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md`  
Identity Continuity: `references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md`  
**Parallel Brief Protocol:** `references/agents/Parallel_Brief_Protocol.md` (Studio Director concurrent specialist briefs under MAXIMUM AGENTIC MODE)

---

## Model Compatibility (Required)

| Layer | Preferred Identifier | Use |
|-------|----------------------|-----|
| Highest quality specialist | `grok-v9-4p5-chat-expert` | DNA, prompts, QA, DoP, Sonic, ErosForge |
| Multi-agent / Team Leader | `grok-v9-4p5-multi` | Studio Director full mode, Sequence orchestration, synthesis |
| Draft / quota / routine | `grok-4-auto` | Animatic, standard tier, fast iteration |
| Video default | Imagine **1.0** | Most sequences |
| Video when audio/physics critical | Imagine **1.5 Native** | Native audio, intimate, complex motion |

Every Production Bible must lock `model_stack` + a `VIDEO_PIPELINE_SPEC`.

---

## Core Leadership

| Agent | Role Card | Preferred Model | Activation |
|-------|-----------|-----------------|------------|
| Studio Director | `Studio_Director.md` | multi (full) / chat-expert (creative) | `ACTIVATE STUDIO DIRECTOR` · `ACTIVATE IMAGINE_AGENT_MODE_HANDOFF` |
| Mega Production Architect | `Mega_Production_Architect.md` | multi | `ACTIVATE MEGA_PRODUCTION_ARCHITECT` |

## Visual & Camera

| Agent | Role Card | Preferred Model | Activation |
|-------|-----------|-----------------|------------|
| Director of Photography | `Director_of_Photography_DoP_v3.5.md` | chat-expert | `ACTIVATE DOP` · `CINEMATIC LIGHTING MODE` |

Legacy skill `director-of-photography-v3-3` is not a second Role Card — prefer `director-of-photography` for new work.
| Color Grading Supervisor | `Post_Production_Color_Grading_Supervisor_v3.5.md` | chat-expert | `ACTIVATE COLOR_GRADING` |
| Production Designer | `Production_Designer_Set_Decorator_v3.5.md` | chat-expert | `ACTIVATE PRODUCTION_DESIGNER` |

## Story & Performance

| Agent | Role Card | Preferred Model | Activation |
|-------|-----------|-----------------|------------|
| Character DNA Extractor | `Character_DNA_Extractor_v3.5.md` | chat-expert | `ACTIVATE CHARACTER_DNA_EXTRACTOR` |
| Performance & Emotion Director | `Performance_Emotion_Director.md` | chat-expert | `ACTIVATE PERFORMANCE_EMOTION` |
| Identity Lock Specialist | `Identity_Lock_Specialist.md` | chat-expert | `ACTIVATE IDENTITY_LOCK` |
| Narrative Arc Strategist | `Narrative_Arc_Pacing_Strategist_v3.5.md` | chat-expert | `ACTIVATE NARRATIVE_ARC` · `ACTIVATE NARRATIVE_STRATEGIST` |
| Sequence Director | `Sequence_Director.md` | multi | `ACTIVATE SEQUENCE_DIRECTOR` |
| Cinematic Sequence Extender | `Cinematic_Sequence_Extender.md` | multi | `ACTIVATE SEQUENCE_EXTENDER` |

## Technical & Continuity

| Agent | Role Card | Preferred Model | Activation |
|-------|-----------|-----------------|------------|
| Continuity Guardian | `Continuity_Consistency_Guardian.md` | multi | `ACTIVATE CONTINUITY_GUARDIAN` |
| Multi-Clip Continuity Orchestrator | `Multi_Clip_Continuity_Orchestrator.md` | multi | `ACTIVATE MULTI_CLIP_CONTINUITY_ORCHESTRATOR` · `RUN MULTI_CLIP_CONTINUITY_AUDIT` |
| QA Guardian | `Quality_Assurance_Guardian_v3.5.md` | chat-expert | `ACTIVATE QA_GUARDIAN` · `RUN QA REVIEW` |
| Grok Doctor | `Grok_Doctor.md` | multi | `ACTIVATE GROK_DOCTOR` · `RUN STUDIO_HEALTH_CHECK` · `DIAGNOSE STUDIO` |
| Imagine Prompt Master | `Imagine_Prompt_Master.md` | chat-expert | `ACTIVATE IMAGINE_PROMPT_MASTER` |
| Workflow & Quota Optimizer | `Workflow_Quota_Optimizer.md` | multi / auto | `ACTIVATE WORKFLOW_OPTIMIZER` |

## Audio (Native 1.5)

| Agent | Role Card | Preferred Model | Activation |
|-------|-----------|-----------------|------------|
| Sonic Architect | `Sonic_Architect_Native_Audio_Virtuoso.md` | chat-expert | `ACTIVATE SONIC_ARCHITECT` · `ACTIVATE NATIVE_AUDIO` |
| Foley Specialist | `Foley_Sound_Design_Specialist_v3.5.md` | chat-expert / auto | `ACTIVATE FOLEY_SPECIALIST` |

## Action, VFX & Marketing

| Agent | Role Card | Preferred Model | Activation |
|-------|-----------|-----------------|------------|
| Stunt Choreographer | `Stunt_Action_Choreographer_v3.5.md` | chat-expert | `ACTIVATE STUNT_CHOREOGRAPHER` |
| VFX & SFX Supervisor | `VFX_and_SFX_Supervisor_v3.5.md` | chat-expert | `ACTIVATE VFX_SFX_SUPERVISOR` |
| Key Art Designer | `Key_Art_Poster_Designer_v3.5.md` | chat-expert | `ACTIVATE KEY_ART_DESIGNER` |
| Trailer Director | `Trailer_Teaser_Director_v3.5.md` | multi | `ACTIVATE TRAILER_DIRECTOR` |
| Localization Specialist | `Localization_Subtitle_Specialist_v3.5.md` | auto | `ACTIVATE LOCALIZATION_SPECIALIST` |

## Post-Production

| Agent | Role Card | Preferred Model | Activation |
|-------|-----------|-----------------|------------|
| AI Polish Director | `AI_Polish_Director.md` | chat-expert | `ACTIVATE AI_POLISH_DIRECTOR` · `RUN FINAL POLISH PASS` |

---

## Production Pipeline (Tier 1)

| Agent | Role Card | Preferred Model | Activation |
|-------|-----------|-----------------|------------|
| Reference & Asset Curator | `Reference_Asset_Curator.md` | auto / chat-expert | `ACTIVATE REFERENCE_CURATOR` |
| Image-to-Video Specialist | `Image_to_Video_Specialist.md` | chat-expert | `ACTIVATE I2V_SPECIALIST` |
| SFW Batch Orchestrator | `SFW_Batch_Orchestrator.md` | multi | `ACTIVATE SFW_BATCH_ORCHESTRATOR` |
| Assembly Editor | `Assembly_Editor.md` | multi | `ACTIVATE ASSEMBLY_EDITOR` |
| Multi-Character Identity Arbiter | `Multi_Character_Identity_Arbiter.md` | chat-expert | `ACTIVATE MULTI_CHARACTER_ARBITER` |
| Costume & Wardrobe Continuity | `Costume_Wardrobe_Continuity.md` | chat-expert | `ACTIVATE COSTUME_WARDROBE` · `LOCK WARDROBE` |

**Order of operations:** Animatic (optional) → Reference Curator → Plate & Motion Readiness → (i2i if needed) → Contact physics (when needed) → I2V Specialist → generation/QA → Assembly Editor → color → polish.

---

## Wave A Specialists (P0 scaffold · landed v3.8.8 · studio v3.11.0)

| Agent | Role Card | Preferred Model | Activation |
|-------|-----------|-----------------|------------|
| Plate & Motion Readiness Lead | `Plate_Motion_Readiness_Lead.md` | chat-expert | `ACTIVATE PLATE_MOTION_READINESS` · `LOCK PLATES` |
| Contact & Micro-Physics Specialist | `Contact_Micro_Physics_Specialist.md` | chat-expert | `ACTIVATE CONTACT_MICRO_PHYSICS` |
| Parallel Brief Dispatcher | `Parallel_Brief_Dispatcher.md` | multi | `ACTIVATE PARALLEL_BRIEF_DISPATCHER` · `DISPATCH PARALLEL BRIEFS` |
| Hair & Makeup Continuity | `Hair_Makeup_Continuity.md` | chat-expert | `ACTIVATE HAIR_MAKEUP_CONTINUITY` · `LOCK HMU` |
| Dialogue & ADR Director | `Dialogue_ADR_Director.md` | chat-expert | `ACTIVATE DIALOGUE_ADR` |
| Score & Temp Music Supervisor | `Score_Temp_Music_Supervisor.md` | chat-expert / auto | `ACTIVATE SCORE_TEMP_MUSIC` |
| Title & Motion Graphics Lead | `Title_Motion_Graphics_Lead.md` | chat-expert | `ACTIVATE TITLE_MOTION_GRAPHICS` |
| Distribution & Crop Strategist | `Distribution_Crop_Strategist.md` | auto | `ACTIVATE DISTRIBUTION_CROP` |

Skills are **P1** (Role Card + SKILL.md + packet types in `tools/wave_a_packets.py`; validate via `handoff-packet-validator` / `--strict-wave-a`). Pack membership: core · camera-image · sequence-narrative · delivery-post.

---

## Refinement (i2i) & Upload Recreation

| Agent / Skill | Role Card | Preferred Model | Activation |
|---------------|-----------|-----------------|------------|
| AI Image Recreation | — | chat-expert | `ACTIVATE AI_IMAGE_RECREATION` |
| I2I Cinematic Refiner | `I2I_Cinematic_Refiner.md` | chat-expert | `ACTIVATE I2I CINEMATIC REFINER` |
| I2I Refiner | `I2I_Refiner.md` | chat-expert | `ACTIVATE I2I REFINER` |

---

## Specialist (Opt-in / NSFW)

| Agent | Role Card | Preferred Model | Activation |
|-------|-----------|-----------------|------------|
| ErosForge NSFW Director | `ErosForge_NSFW_Director.md` | chat-expert | `ACTIVATE EROSFORGE` |
| NSFW Quota Orchestrator | `NSFW_Quota_Orchestrator.md` | multi | `ACTIVATE NSFW_QUOTA_ORCHESTRATOR` |
| NSFW Sequence Extender | `NSFW_Sequence_Extender.md` | multi | `ACTIVATE NSFW_SEQUENCE_EXTENDER` |

Requires explicit opt-in. NSFW agents strongly prefer **Imagine 1.5** for authenticity.

---

## Activation Presets (Updated)

| # | Preset | Command |
|---|--------|---------|
| 1 | Full Studio | `Activate Grok Imagine Cinematic Studio v3.11.3` |
| 2 | 1.5 Native Video | `ACTIVATE IMAGINE_VIDEO_1.5_FULL` |
| 3 | Long-Form Sequence | `ACTIVATE SEQUENCE_DIRECTOR` + `ACTIVATE SEQUENCE_EXTENDER` |
| 4 | Character Onboarding | `ACTIVATE CHARACTER_DNA_EXTRACTOR` + `ACTIVATE IDENTITY_LOCK` |
| 4b | Wardrobe Lock | `ACTIVATE COSTUME_WARDROBE` + `ACTIVATE IDENTITY_LOCK` |
| 5 | Native Audio Pass | `ACTIVATE SONIC_ARCHITECT` + `GENERATE_NATIVE_AUDIO_SEQUENCE` |
| 6 | Marketing Package | `ACTIVATE KEY_ART_DESIGNER` + `ACTIVATE TRAILER_DIRECTOR` |
| 7 | QA + Delivery | `RUN QA REVIEW` → `ACTIVATE AI_POLISH_DIRECTOR` |
| 7b | Studio Health Diagnostic | `ACTIVATE GROK_DOCTOR` · `RUN STUDIO_HEALTH_CHECK` |
| 7c | Multi-Clip Continuity Audit | `ACTIVATE MULTI_CLIP_CONTINUITY_ORCHESTRATOR` · `RUN CROSS_AGENT_CONTINUITY_AUDIT` |
| 7d | Plate + Motion Gate | `ACTIVATE PLATE_MOTION_READINESS` → `ACTIVATE I2V_SPECIALIST` |
| 7e | Parallel Brief Wave | `ACTIVATE PARALLEL_BRIEF_DISPATCHER` + specialist briefs |
| 8 | Quota Planning | `ACTIVATE WORKFLOW_OPTIMIZER` |
| 9 | Final Delivery Polish | `RUN FINAL POLISH PASS` |
| 10 | NSFW Quota Batch | `ACTIVATE EROSFORGE` → `ACTIVATE NSFW_QUOTA_ORCHESTRATOR` |
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

**Identity Continuity Protocol:** `references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md` (required for Lock / Extender / Continuity / QA on long-form).

## Meta & Tools (supporting Role Cards)

Not in the 25-core. Canonical cards live in `references/agents/` (skills must not be the only copy).

| Agent | Role Card | Preferred Model | Activation |
|-------|-----------|-----------------|------------|
| GitHub Repo Manager | `GitHub_Repo_Manager.md` | chat-expert | `ACTIVATE GITHUB_REPO_MANAGER` |
| Quota Dashboard | `Quota_Dashboard.md` | chat-expert | `ACTIVATE QUOTA_DASHBOARD` |
| Extend Frame to Video | `Extend_Frame_to_Video.md` | multi | `ACTIVATE EXTEND_FRAME_TO_VIDEO` |

DNA / QA skill filenames `Character_DNA_Extractor.md` and `Quality_Assurance_Guardian.md` are **aliases** of the `_v3.5.md` canonical cards.

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
| `nsfw-chain-qa-protocol` | Pipeline (opt-in) | `RUN NSFW CHAIN QA REVIEW` |
| `grok-doctor` | Agent / diagnostic | `ACTIVATE GROK_DOCTOR` · `RUN STUDIO_HEALTH_CHECK` |
| `multi-clip-continuity-orchestrator` | Agent | `ACTIVATE MULTI_CLIP_CONTINUITY_ORCHESTRATOR` |
| `plate-motion-readiness-lead` | Agent (Wave A) | `ACTIVATE PLATE_MOTION_READINESS` |
| `contact-micro-physics-specialist` | Agent (Wave A) | `ACTIVATE CONTACT_MICRO_PHYSICS` |
| `hair-makeup-continuity` | Agent (Wave A) | `ACTIVATE HAIR_MAKEUP_CONTINUITY` |
| `dialogue-adr-director` | Agent (Wave A) | `ACTIVATE DIALOGUE_ADR` |
| `score-temp-music-supervisor` | Agent (Wave A) | `ACTIVATE SCORE_TEMP_MUSIC` |
| `title-motion-graphics-lead` | Agent (Wave A) | `ACTIVATE TITLE_MOTION_GRAPHICS` |
| `distribution-crop-strategist` | Agent (Wave A) | `ACTIVATE DISTRIBUTION_CROP` |
| `parallel-brief-dispatcher` | Agent (Wave A) | `ACTIVATE PARALLEL_BRIEF_DISPATCHER` |

---

*Grok Imagine Cinematic Studio — Enhanced Agent Index for grok-4-auto · grok-v9-4p5-multi · grok-v9-4p5-chat-expert + Imagine Video 1.0 / 1.5 Native · 2026-09-03 · studio v3.11.3 · 64 skills (Wave A P0)*
