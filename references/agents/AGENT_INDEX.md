# Grok Imagine Cinematic Studio — Agent Index (v3.6)

**Location:** `references/agents/`
**Purpose:** Authoritative source for all specialized Role Cards (v3.6)
**Last Updated:** June 21, 2026

> **Note:** These are the **official and maintained** Role Cards. All filenames are now clean (no version suffix). Legacy files have been removed.

---

## Most Common Production Presets

Quick-start activation patterns for the workflows you use most often.

| # | Preset | Goal | Key Agents | Activation Command | Notes |
|---|--------|------|------------|--------------------|-------|
| 1 | **New Character Onboarding** | Extract DNA + lock identity | Identity Lock Specialist<br>Studio Director | `ACTIVATE ONLY Identity Lock Specialist, Studio Director` | Start here for any new project |
| 2 | **Standard Cinematic Scene** | High-quality cinematic shot or short sequence | Studio Director<br>Imagine Prompt Master<br>Director of Photography<br>Identity Lock Specialist | `ACTIVATE ONLY Studio Director, Imagine Prompt Master, Director of Photography, Identity Lock Specialist` | Core everyday workflow |
| 3 | **NSFW / Erotic Scene** | Artistic erotic or intimate sequences | ErosForge NSFW Director<br>Identity Lock Specialist<br>Director of Photography | `ACTIVATE ONLY ErosForge NSFW Director, Identity Lock Specialist, Director of Photography` | Use `ACTIVATE EROSFORGE` first |
| 4 | **Long-Form Sequence / Video** | Build or extend longer sequences (native 1.5) | Sequence Director<br>Cinematic Sequence Extender<br>Continuity Guardian<br>Identity Lock Specialist | `ACTIVATE ONLY Sequence Director, Cinematic Sequence Extender, Continuity Guardian, Identity Lock Specialist` | Use for 1.5 native chaining |
| 5 | **Trailer or Teaser** | High-impact short-form content | Trailer & Teaser Director<br>Studio Director<br>Imagine Prompt Master | `ACTIVATE ONLY Trailer & Teaser Director, Studio Director, Imagine Prompt Master` | Great for `HIGH IMPACT HOOK` |
| 6 | **Full Production Kickoff** | Start complete multi-scene project | Studio Director<br>Workflow & Quota Optimizer<br>Imagine Prompt Master<br>Identity Lock Specialist | `ACTIVATE ONLY Studio Director, Workflow & Quota Optimizer, Imagine Prompt Master, Identity Lock Specialist` | Add specialists as needed |
| 7 | **Key Art + Marketing** | Theatrical key art and posters | Key Art & Poster Designer<br>Studio Director<br>Director of Photography | `ACTIVATE ONLY Key Art & Poster Designer, Studio Director, Director of Photography` | Excellent for covers and marketing |
| 8 | **Quota-Efficient Large Batch** | Maximize quality while controlling usage | Workflow & Quota Optimizer<br>Studio Director<br>Imagine Prompt Master | `ACTIVATE ONLY Workflow & Quota Optimizer, Studio Director, Imagine Prompt Master` | Activate first on big sessions |
| 10 | **NSFW Quota Batch (Heavy)** | Erotic image+video batches under Heavy limits | NSFW Quota Orchestrator<br>ErosForge NSFW Director<br>Workflow & Quota Optimizer<br>Identity Lock Specialist | `ACTIVATE EROSFORGE` then `ACTIVATE NSFW_QUOTA_ORCHESTRATOR` | Hero-first scheduling, i2v decisions, daily reports |
| 11 | **NSFW Sequence Extension** | Extend reference frame/clip to 30–120s+ sensual sequence | NSFW Sequence Extender<br>Cinematic Sequence Extender<br>ErosForge NSFW Director<br>Identity Lock Specialist | `ACTIVATE EROSFORGE` then `ACTIVATE NSFW_SEQUENCE_EXTENDER` | Prompt chains, extend-from-frame, erotic pacing, artifact QA |
| 9 | **Final Delivery Polish** | Upscale + face restore for delivery | AI Polish Director<br>Quality Assurance Guardian<br>Studio Director | `ACTIVATE ONLY AI Polish Director, Quality Assurance Guardian, Studio Director` | Run after QA Go + color grade |

---

## Core Production Agents

| Agent | File | Role |
|-------|------|------|
| Studio Director | `Studio_Director.md` | Central commander & full production orchestrator |
| Character DNA Extractor | `Character_DNA_Extractor_v3.5.md` | Forensic DNA extraction → Identity Lock handoff |
| Sequence Director | `Sequence_Director.md` | Long-form sequencing, native 1.5 extend/stitch |
| Imagine Prompt Master | `Imagine_Prompt_Master.md` | Elite cinematic prompt engineering |
| Director of Photography | `Director_of_Photography_DoP_v3.5.md` | Lighting, camera, color, cinematic look |
| Performance Emotion Director | `Performance_Emotion_Director.md` | Micro-expressions, emotional arcs, performance |
| Identity Lock Specialist | `Identity_Lock_Specialist.md` | Character consistency guardian |
| Cinematic Sequence Extender | `Cinematic_Sequence_Extender.md` | Video extension & long-form 1.5 chaining |
| Continuity & Consistency Guardian | `Continuity_Consistency_Guardian.md` | Cross-clip & multi-shot consistency |
| Quality Assurance Guardian | `Quality_Assurance_Guardian_v3.5.md` | Final 16-point quality gatekeeper |

---

## Specialized Directors

| Agent | File | Role |
|-------|------|------|
| ErosForge NSFW Director | `ErosForge_NSFW_Director.md` | Artistic R-rated / erotic cinematic sequences |
| Workflow & Quota Optimizer | `Workflow_Quota_Optimizer.md` | Real-time credit efficiency & production economics |
| Sonic Architect Native Audio Virtuoso | `Sonic_Architect_Native_Audio_Virtuoso.md` | Native audio & cinematic sound design |
| Foley Sound Design Specialist | `Foley_Sound_Design_Specialist_v3.5.md` | Hyper-realistic foley & environmental sound |
| Post-Production Color Grading Supervisor | `Post_Production_Color_Grading_Supervisor_v3.5.md` | Final visual polish & color harmony |
| Production Designer / Set Decorator | `Production_Designer_Set_Decorator_v3.5.md` | Environment DNA & prop memory bank |
| Narrative Arc & Pacing Strategist | `Narrative_Arc_Pacing_Strategist_v3.5.md` | Story rhythm, tension/release, emotional payoff |
| Stunt & Action Choreographer | `Stunt_Action_Choreographer_v3.5.md` | Professional stunt & fight choreography |
| VFX & SFX Supervisor | `VFX_and_SFX_Supervisor_v3.5.md` | Particles, creatures, destruction, effects |
| Key Art & Poster Designer | `Key_Art_Poster_Designer_v3.5.md` | Theatrical key art & marketing visuals |
| Trailer & Teaser Director | `Trailer_Teaser_Director_v3.5.md` | High-impact short-form promotional content |
| Localization & Subtitle Specialist | `Localization_Subtitle_Specialist_v3.5.md` | Cultural adaptation & accessibility subtitles |
| **AI Polish Director** | `AI_Polish_Director.md` | Final upscale, face restoration & delivery polish |

---

## Quota Orchestration (v3.6)

Per-second 1.5 pricing with session tracking and optimization recommendations.

```bash
python tools/cinematic_studio_cli.py quota estimate --duration 90 --clips 9 --fast-mode
python tools/cinematic_studio_cli.py quota sequence "Sequence Name"
python tools/cinematic_studio_cli.py quota optimize --duration 90 --clips 9
python tools/cinematic_studio_cli.py quota dashboard
python tools/cinematic_studio_cli.py quota budget --tier supergrok_heavy
```

Reference: `.grok/skills/workflow-quota-optimizer/references/pricing_model_v3.6.md`

## NSFW Quota Orchestrator (v1.0)

Quota-aware batch planning for erotic image + video under SuperGrok Heavy.

```bash
python tools/cinematic_studio_cli.py nsfw plan "Act 2 Sequence" --shot "hero:Embrace, golden hour" --shot "key_explicit:Slow reveal:high"
python tools/cinematic_studio_cli.py nsfw next "act-2-sequence" --count 3
python tools/cinematic_studio_cli.py nsfw decide shot_001 --tier hero --motion high --has-ref
python tools/cinematic_studio_cli.py nsfw record "act-2-sequence" shot_001 --score 8.5 --credits 92
python tools/cinematic_studio_cli.py nsfw report --output artifacts/nsfw_daily_report.md
```

Skill: `.grok/skills/nsfw-quota-orchestrator/`

## NSFW Sequence Extension (v1.0)

Extend reference frames or short clips into 30–120+ second sensual sequences.

```bash
python tools/cinematic_studio_cli.py nsfw extend plan "Candlelit Embrace" --duration 90 --profile passionate \
  --reference "Silk robe, candlelit bedroom, warm amber, identity locked"
python tools/cinematic_studio_cli.py nsfw extend chain "candlelit-embrace"
python tools/cinematic_studio_cli.py nsfw extend prompt "candlelit-embrace" --clip clip_003
python tools/cinematic_studio_cli.py nsfw extend camera --phase escalation
python tools/cinematic_studio_cli.py nsfw extend qa "candlelit-embrace" --clip clip_002
```

Skill: `.grok/skills/nsfw-sequence-extender/`

## Long-Form Sequence Pipeline (v3.6)

```
Sequence Director (plan) → Generate clip → Chain QA (Go) → LAST_FRAME_RECAP
  → Continuity Guardian → extend-prompt → next clip → repeat → final stitch
```

CLI commands:
```bash
python tools/cinematic_studio_cli.py sequence init "Sequence Name" --duration 90
python tools/cinematic_studio_cli.py sequence add-clip "Sequence Name" --prompt "..." --recap "..."
python tools/cinematic_studio_cli.py sequence extend-prompt "Sequence Name" --clip clip_001 --beat "Next beat"
python tools/cinematic_studio_cli.py sequence qa "Sequence Name" --clip clip_002 --scores '{...}'
python tools/cinematic_studio_cli.py sequence health "Sequence Name"
```

References:
- `.grok/skills/cinematic-sequence-extender/references/extend_stitch_protocol_v3.6.md`
- `.grok/skills/cinematic-sequence-extender/references/chain_qa_checklist.md`

## Character Consistency Pipeline (v3.6)

```
Reference Images → Character DNA Extractor → dna.json → Identity Lock Specialist → Imagine Prompt Master
```

CLI commands:
```bash
python tools/cinematic_studio_cli.py dna init "Character Name" --core "..." --facial "..."
python tools/cinematic_studio_cli.py dna lock --name "Character Name"
python tools/cinematic_studio_cli.py dna inject --name "Character Name" --mode video_1.5
```

Skill: `.grok/skills/character-dna-extractor/`

## Post-Production Pipeline (v3.6)

```
Production → QA Guardian (Go/No-Go) → Color Grading Supervisor → AI Polish Director → Studio Director Sign-Off
```

The AI Polish Director uses the `ai-video-upscaler` skill for GPU or fallback upscaling with optional face restoration.

---

## How to Activate Agents

Use the standard activation syntax:

```
ACTIVATE ONLY Studio Director, Identity Lock Specialist, Imagine Prompt Master
```

**New in v3.6:** Many agents now have dedicated skill files in `.grok/skills/` for deeper integration.

---

**Last Updated:** June 21, 2026 — v3.6 "Odyssey Native" + AI Polish Director. 23 agents total.