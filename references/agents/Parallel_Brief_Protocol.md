# Parallel Brief Protocol v1.0

**Status:** Official  
**Studio:** Grok Imagine Cinematic Studio v3.8.6+  
**Model Layer:** `grok-v9-4p5-multi` (orchestration) · `grok-v9-4p5-chat-expert` (specialist craft)  
**Pairs with:** `Studio_Director.md` · `IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md` · specialist Role Cards · `AUDIO_MOMENTUM_VECTOR` · Identity Continuity Protocol

---

## Purpose

Define the **Parallel Brief** as the primary live multi-agent coordination primitive for concurrent specialist work under **MAXIMUM AGENTIC MODE** and **HIGH REASONING MODE**.

A Parallel Brief is a structured, simultaneous task packet issued by the Cinematic Studio Director (or Grok Team Leader) to one or more specialists. It enables true parallelism while locking Continuity, Character DNA, Explicitness Level, physics fidelity, and quality gates.

It is the operational realization of the Studio Director’s dynamic agent activation and Director’s Notes responsibilities.

---

## When to Issue Parallel Briefs

- New user content that benefits from concurrent specialist work
- Pre-handoff preparation (DNA, densification, Foley, DoP, Continuity)
- BUILD / CODING MODE scaffolding
- Any situation where sequential blocking would slow quality or speed

Prefer Parallel Briefs whenever two or more specialists can contribute independently.

---

## Canonical Parallel Brief Template

```markdown
## Parallel Brief — [ID / Timestamp]
**From:** Cinematic Studio Director
**To:** [Specialist(s)]
**Priority:** High | Normal | Low
**Mode:** HIGH REASONING | MAXIMUM AGENTIC | CODING/BUILD
**Constraints:** DNA protection · Continuity GREEN · Intensity never dilute · Physics fidelity · etc.

### Scope
[One clear sentence]

### Required Deliverable
- Exact expected output

### Integration Points
- How this feeds Production Bible / imagine_agent_mode_handoff / AMV / Continuity Flags / QA Pre-Check

### Explicitness / NSFW Notes (when relevant)
- Confirmed Level: 3 or 4
- ErosForge required: yes / no
- Non-Negotiable Explicitness Anchors must remain undiluted

### Standby / Deadline
Immediate | After [X] | Silent standby until next brief
```

---

## Workflow Sequence

1. Director analyzes user request + current Production Bible + Continuity state.
2. Director issues one or more Parallel Briefs concurrently.
3. Specialists acknowledge and execute in parallel.
4. Specialists return structured responses.
5. Director synthesizes results, updates Production Bible / Continuity, and either issues next briefs or closes.
6. When generation-ready: contributions converge into a validated `imagine_agent_mode_handoff` packet.
7. Grok Team Leader performs final user-facing synthesis.

---

## NSFW Prompt Optimizer Consumption Pattern

### Required Fields in Every NSFW Parallel Brief
- Source Material (raw prompt / scene brief / beat)
- Confirmed Explicitness Level (3 | 4)
- ErosForge Active / Required status
- Character DNA / Identity Lock Status
- Camera / Composition Notes (if available)
- Incoming Continuity Flags
- **Mandatory Constraints:** Never dilute Level 3–4 intensity · Character DNA inviolable under high anatomical / fluid / interaction detail · Explicitness Anchors terminal and non-negotiable · Prefer `grok-v9-4p5-chat-expert`

### Standard Input Template

```text
PARALLEL BRIEF · NSFW PROMPT OPTIMIZER
ID: [brief-id]
From: Cinematic Studio Director
Priority: [normal | high]
Source Material: [raw prompt / scene brief / beat description / previous packet]
Confirmed Explicitness Level: 3 | 4
ErosForge Active: [true | required]
Character DNA / Identity Lock Status: [locked slug(s) | pending extract]
Camera / Composition Notes: [from DoP if available]
Continuity Flags Incoming: [list or none]
Required Deliverables:
  - Hierarchical densified prompt (Ultimate Template structure)
  - Non-Negotiable Explicitness Anchors (terminal locked section)
  - Continuity Flags (outgoing)
  - QA Pre-Check notes
  - Ready-to-embed package for imagine_agent_mode_handoff
Constraints (MANDATORY):
  - Never dilute Level 3–4 intensity
  - Character DNA remains inviolable under high anatomical / fluid / interaction detail
  - Explicitness Anchors must be non-negotiable and terminal
  - Prefer model: grok-v9-4p5-chat-expert
  - Route through ErosForge if not already active
```

### Convergence Path
Parallel Brief → hierarchical densified prompt + Non-Negotiable Explicitness Anchors + Continuity Flags + QA Pre-Check  
→ Creative Handoff Packet v1.3 semantic layer  
→ mapped into official `imagine_agent_mode_handoff` fields (`prompt`, `dna_inject`, `qa_gate`, Continuity notes, preferred_chat_model)  
→ validated by handoff-packet-validator  
→ ready for generation surface.

**Intensity is never diluted. DNA remains inviolable.**

---

## Foley Sound Design Specialist Consumption Pattern

### Required Fields in Every Foley Parallel Brief
- Clip / Beat (id + concise physical action description)
- Perspective (ECU | CU | MS | WS | EWS)
- Materials / Props (with material tags)
- Body / Cloth (weight, gait, fabric layers)
- Continuity State (dry | wet | damaged | fatigued | clean | dirty | custom)
- Emotional Temperature (1–10 or low/mid/high)
- Intimate / ErosForge Active (false | true)
- AMV Target (sfx_timing required; emotional_tone_audio optional)
- Sound DNA Bank instruction (use existing IDs | create new)
- Constraints (physics accuracy, perspective match, intimate rules)

### Standard Input Template

```markdown
## Parallel Brief — Foley Sound Design Specialist
**ID:** [brief-id]
**From:** Cinematic Studio Director
**Priority:** High | Normal | Low
**Clip / Beat:** [id + concise physical action description]
**Perspective:** ECU | CU | MS | WS | EWS
**Materials / Props:** [list with material tags]
**Body / Cloth:** [weight, gait, fabric layers]
**Continuity State:** dry | wet | damaged | fatigued | clean | dirty | [custom]
**Emotional Temperature:** 1–10 or low / mid / high
**Intimate / ErosForge Active:** false | true
**AMV Target:** sfx_timing (required) · emotional_tone_audio (optional)
**Sound DNA Bank:** use existing IDs | create new
**Constraints:**
- Physics accuracy is mandatory
- Mic perspective must match camera distance
- Intimate SFX only when ErosForge=true; authentic and restrained
- Never compete with dialogue or score
```

### Standard Output Structure

```markdown
## FOLEY RESPONSE · [brief-id]
**Clip:** …
**Perspective:** …
**Actions → Sounds:**
- [visible physical contact] → [physics-true description]
**Sound DNA Touched / Created:**
- `id`: material=… · signature=… · state_variants={…} · perspective={…} · continuity_rule=…
**sfx_timing (AMV-ready):**
`[concise phrase], [state variant], [perspective note]`
**Continuity Flags:**
- [state change] → sound must change to [variant]
**Risks:** material mismatch | perspective wrong | over-loud
**Next:** Sonic Architect (Sound Layer) · Continuity · Sequence Extender
**Self-eval:** C / EP / TF / QE / CE / CI / Conf /10
```

### SoundDNA Mapping
Every Foley response that touches recurring materials must update or create entries in the SoundDNA bank (material, signature, state_variants, perspective, continuity_rule). The `sfx_timing` string is produced from the selected SoundDNA variant + current perspective and is consumed by AUDIO_MOMENTUM_VECTOR integrity scoring.

### Non-Blocking Parallel Rules
Foley executes entirely in parallel with other specialists. Outputs are pure structured metadata and paste-ready strings. These are later consumed by Sonic Architect (full Sound Layer ownership) and by Continuity / Sequence Extender (state consistency + AMV scoring). Foley never creates sequential dependencies and never blocks densification, visual language, DNA, or prompt work.

---

## Convergence Rules into Imagine Agent Mode Handoff

All Parallel Brief outputs must be designed so they can be cleanly embedded into a validated `imagine_agent_mode_handoff` packet without loss of:

- Character DNA / `dna_inject`
- Non-Negotiable Explicitness Anchors
- Continuity Flags / `last_frame_recap` / `momentum_vector` / `audio_momentum_vector`
- `sfx_timing` / Sound Layer notes
- QA Pre-Check / `qa_gate`
- Preferred model and `VIDEO_PIPELINE_SPEC`

Director owns the final assembly and surface decision.

---

## Continuity & Safety Constraints (Non-Negotiable)

- Continuity is Law
- Character DNA protection is absolute
- Explicitness Level 3–4 is never diluted
- Intimate / ErosForge content requires explicit activation
- Physics fidelity for Foley is mandatory
- No Parallel Brief may create sequential blocking dependencies between specialists

---

## BUILD MODE Notes

- Optional future tooling: `tools/parallel_brief.py` (dataclass + markdown emitter + logging)
- SoundDNA bank (proposed dataclass) is the recommended backing store for Foley continuity
- Protocol may be extended with additional specialist consumption patterns as needed

---

## Specialist Role Card Coverage (v1.0+)

| Role Card | Parallel Brief role |
|-----------|---------------------|
| `Studio_Director.md` | Issues briefs; synthesizes; owns handoff assembly |
| `Sequence_Director.md` | Issues/receives structure briefs; dependency graph |
| `Multi_Clip_Continuity_Orchestrator.md` | Receives multi-clip briefs; Cross-Agent Continuity Audits |
| `Continuity_Consistency_Guardian.md` | Folds Continuity Flags / memory bank |
| `Identity_Lock_Specialist.md` | Parallel lock / inject under DNA protection |
| `Character_DNA_Extractor_v3.5.md` | Concurrent onboarding DNA extraction |
| `Director_of_Photography_DoP_v3.5.md` | Camera / lighting handoff blocks |
| `Imagine_Prompt_Master.md` | Densification / NSFW optimizer consumption |
| `ErosForge_NSFW_Director.md` | Level 3–4 brief fields + non-dilution |
| `Foley_Sound_Design_Specialist_v3.5.md` | Foley consumption pattern (this doc) |
| `Sonic_Architect_Native_Audio_Virtuoso.md` | Sound Layer / AMV after Foley parallel |
| `Quality_Assurance_Guardian_v3.5.md` | QA Pre-Check + gate → `qa_gate` |
| `Cinematic_Sequence_Extender.md` | Gated consume of parallel prep packs |
| `Parallel_Brief_Dispatcher.md` | Co-pilot: templates, IDs, anti-block graph, convergence |
| `Plate_Motion_Readiness_Lead.md` | Parallel plate/motion gates before i2v |
| `Contact_Micro_Physics_Specialist.md` | Concurrent contact/physics briefs |
| `Hair_Makeup_Continuity.md` | Concurrent HMU lock |
| `Dialogue_ADR_Director.md` | Concurrent dialogue/ADR blocks |
| `Score_Temp_Music_Supervisor.md` | Concurrent music cues / AMV tone |
| `Title_Motion_Graphics_Lead.md` | Post-cut titles (parallel to polish prep) |
| `Distribution_Crop_Strategist.md` | Platform crop plans before ffmpeg |

Issuer of record: **Studio Director** (or Grok Team Leader). All paths converge to validated `imagine_agent_mode_handoff`.

---

## Changelog

- **v1.0 (2026-07-25)** — Initial formalization from live multi-agent practice under Grok Imagine Cinematic Studio v3.8.6
