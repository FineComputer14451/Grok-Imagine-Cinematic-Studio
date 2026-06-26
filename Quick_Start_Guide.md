# Grok Imagine Cinematic Studio v3.6 — Quick Start Guide

**Version:** 3.6.5 | **Last Updated:** June 24, 2026

---

## 0. Model Stack (Grok 4.3 + Imagine 1.5 + Grok Build)

| Where | Model | Purpose |
|-------|-------|---------|
| Grok chat / API | `grok-4.3` | 1M-context orchestration, Production Bibles |
| Grok Build CLI | `grok-composer-2.5-fast` | Local agent sessions |
| Grok Build fork | `grok-build` | Code, skills, repo tooling |
| xAI Build API | `grok-build-0.1` | Agentic automation |
| Imagine Video | `grok-imagine-video-1.5` | Native audio video ($0.08/sec) |
| Imagine Image | `grok-imagine-image` | Reference stills |

Verify compatibility: `python tools/cinematic_studio_cli.py models verify`  
Full reference: `references/MODELS_v3.6.md`

Grok Build config (`~/.grok/config.toml`):
```toml
[ui]
fork_secondary_model = "grok-build"
```

---

## 1. Getting Started

### Activate the Full Studio (Recommended)

```
Activate Grok Imagine Cinematic Studio v3.6
```

or

```
start cinematic production
```

This loads the complete **v3.6 "Odyssey Native"** system with full native Grok Imagine Video 1.5 support (image-to-video + one-pass synchronized audio).

### Start a New Project

```
Start new project
```

or

```
Full production mode
```

---

## 2. How to Use Individual Specialists

You can activate any agent directly:

| Specialist                              | Activation Command                  | Best For                                      |
|-----------------------------------------|-------------------------------------|-----------------------------------------------|
| **Studio Director**                     | `ACTIVATE STUDIO_DIRECTOR`          | Overall direction & orchestration             |
| **Mega Production Architect**           | `ACTIVATE MEGA_PRODUCTION_ARCHITECT`| Full Production Bible + execution roadmap     |
| **Identity Lock Specialist**            | `ACTIVATE IDENTITY_LOCK`            | Character consistency & DNA                   |
| **Imagine Prompt Master**               | `ACTIVATE IMAGINE_PROMPT_MASTER`    | High-quality prompt engineering (1.5 native)  |
| **Director of Photography (DoP)**       | `ACTIVATE DOP`                      | Lighting, camera, visual language             |
| **Performance & Emotion Director**      | `ACTIVATE PERFORMANCE_EMOTION`      | Micro-expressions & emotional acting          |
| **Sequence Director**                   | `ACTIVATE SEQUENCE_DIRECTOR`        | Long-form sequencing & 1.5 chaining           |
| **Cinematic Sequence Extender**         | `ACTIVATE SEQUENCE_EXTENDER`        | Long-form sequence expansion (60–180s+)       |
| **Continuity & Consistency Guardian**   | `ACTIVATE CONTINUITY_GUARDIAN`      | Timeline & prop consistency                   |
| **Quality Assurance Guardian**          | `ACTIVATE QA_GUARDIAN`              | Final 16-point QA review                      |
| **ErosForge NSFW Director**             | `ACTIVATE EROSFORGE`                | Artistic R-rated / erotic scenes              |
| **Key Art & Poster Designer**           | `ACTIVATE KEY_ART_DESIGNER`         | Posters, thumbnails, marketing visuals        |
| **Trailer & Teaser Director**           | `ACTIVATE TRAILER_DIRECTOR`         | Trailers, teasers, highlight reels            |
| **Production Designer**                 | `ACTIVATE PRODUCTION_DESIGNER`      | Environments, props, world-building           |
| **Sonic Architect**                     | `ACTIVATE SONIC_ARCHITECT`          | Native audio & sound design                   |
| **Foley Sound Design Specialist**       | `ACTIVATE FOLEY_SPECIALIST`         | Realistic foley & hard effects                |
| **Stunt & Action Choreographer**        | `ACTIVATE STUNT_CHOREOGRAPHER`      | Fights, chases, stunts                        |
| **VFX & SFX Supervisor**                | `ACTIVATE VFX_SFX_SUPERVISOR`       | Creatures, destruction, particles             |
| **Workflow & Quota Optimizer**          | `ACTIVATE WORKFLOW_OPTIMIZER`       | Real-time quota & efficiency management       |

**Tip:** You can also use natural language, for example:
- "Create key art for this scene"
- "Make a cinematic trailer from this sequence"
- "Choreograph this fight scene with emotional weight"

---

## 3. Recommended Production Workflow (v3.6)

### Phase 1: Activation & Planning
1. **Activate the Full Studio**  
   `Activate Grok Imagine Cinematic Studio v3.6`

2. **Start a New Project**  
   Provide title, logline, genre, tone, target length, and key characters.

3. **Generate & Lock the Production Bible**  
   Include `VIDEO_PIPELINE_SPEC` for 1.5 native settings.

### Phase 2: Pre-Production
4. **Generate Reference Materials** (Recommended)  
   Request character references, environment concepts, or mood boards early.

5. **Activate Key Specialists Early**  
   - `ACTIVATE IDENTITY_LOCK` for recurring characters  
   - `ACTIVATE PRODUCTION_DESIGNER` for world-building  
   - `ACTIVATE DOP` for visual language

### Phase 3: Production
6. **Execute Scenes / Sequences**  
   - Single scenes: Describe clearly  
   - Long sequences: Use `ACTIVATE SEQUENCE_DIRECTOR` + `ACTIVATE SEQUENCE_EXTENDER`

7. **Collaborate Mid-Production**  
   Activate specialists as needed (Stunts, VFX, Sound, etc.).

### Phase 4: Review & Polish
8. **Run QA Review**  
   `RUN QA REVIEW` or let the Quality Assurance Guardian evaluate outputs.

9. **Final Delivery Polish** (after QA Go)  
   `ACTIVATE AI_POLISH_DIRECTOR` or `RUN FINAL POLISH PASS` — upscales 720p clips to delivery resolution with optional face restoration via the `ai-video-upscaler` skill.

10. **Request Director’s Cut** (if needed)  
   `GENERATE DIRECTOR'S CUT`

### Phase 5: Delivery
11. **Generate Marketing Assets**  
    `ACTIVATE KEY_ART_DESIGNER` + `ACTIVATE TRAILER_DIRECTOR`

12. **Localize** (if needed)  
    `ACTIVATE LOCALIZATION_SPECIALIST`

---

**Pro Tip:** You can combine steps in one message:  
> `"Activate Grok Imagine Cinematic Studio v3.6, start new project called 'Neon Eclipse Heist', generate the full Production Bible with VIDEO_PIPELINE_SPEC for 1.5, and create the first sequence."`

---

## 4. Pro Tips for Best Results (v3.6)

- **Be specific** — Include genre, tone, emotional goals, character details, and references.
- **Use the Project Bible** — Include `VIDEO_PIPELINE_SPEC` for 1.5 native settings.
- **Activate specialists early** when you need focused work (trailers, key art, stunts, etc.).
- **Let agents collaborate** — Full studio mode automatically coordinates between specialists.
- **Use “Director’s Cut”** after important generations for refined versions.
- **Monitor quota** — The Workflow Quota Optimizer now supports per-second 1.5 video pricing.
- **Reference Role Cards** — Check `references/agents/[Agent].md` for each agent’s exact capabilities.
- **Use Skill Files** — Many agents now have enhanced skill files in `.grok/skills/` for deeper integration.

---

## 5. Quick Reference Commands

| Command                                           | Result                                      |
|---------------------------------------------------|---------------------------------------------|
| `Activate Grok Imagine Cinematic Studio v3.6`     | Load full v3.6 studio (1.5 native support)  |
| `Start new project`                               | Begin fresh production                      |
| `GENERATE DIRECTOR'S CUT`                         | Refined version with notes                  |
| `SHOW STUDIO DASHBOARD`                           | Current project status                      |
| `RUN QA REVIEW`                                   | Full 16-point quality check                 |
| `ACTIVATE EROSFORGE`                              | Enable NSFW specialist mode                 |
| `Exit cinematic studio`                           | Leave studio mode                           |

---

## 6. Available Supporting Resources

| Resource                        | Location                              | Purpose                                           |
|---------------------------------|---------------------------------------|---------------------------------------------------|
| **Role Cards (Authoritative)**  | `references/agents/`                  | Full Role Cards with v3.6 protocols               |
| **Agent Index**                 | `references/agents/AGENT_INDEX.md`    | Quick reference table for all agents              |
| **Master Prompt**               | `MASTER_PROMPT_v3.6.md`               | Complete master prompt for new chats              |
| **Skill Files**                 | `.grok/skills/`                       | Enhanced agent capabilities & integration         |
| **Production Bible Template**   | `Project_Bible_Template.md`           | Professional Production Bible template            |
| **Examples**                    | `examples/`                           | Ready-to-use Production Bible templates           |
| **CLI Toolkit**                 | `tools/cinematic_studio_cli.py`       | Memory, Bible generation, PDF reports             |
| **Web UI**                      | `web_ui/app.py`                       | Streamlit interface with Memory management        |

---

**You are now ready to create professional cinematic productions with full native Grok Imagine Video 1.5 support.**

Just say **"Activate Grok Imagine Cinematic Studio v3.6"** and begin. 🎥

---

*Built with Grok Imagine Cinematic Studio v3.6 "Odyssey Native" — June 2026*