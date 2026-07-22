# User Guide
## Grok Imagine Cinematic Studio v3.8.6

Complete end-to-end guide for creators.

---

## 1. Activation

In any Grok conversation:

```
Activate Grok Imagine Cinematic Studio v3.8.6
```

Alternative triggers:
- `start cinematic production`
- `ACTIVATE GROK_IMAGINE_CINEMATIC_STUDIO`

This loads the full agent suite, protocols, and Studio Director.

---

## 2. Recommended Production Workflow

### Phase 1 — Project Setup
1. Activate the Studio
2. Create / lock Production Bible  
   (`cinematic-studio create-bible --wizard` or ask Studio Director)
3. Declare `VIDEO_PIPELINE_SPEC` (prefer 1.5 for hero work)

### Phase 2 — Character & Identity
1. `ACTIVATE CHARACTER_DNA_EXTRACTOR` (or CLI `dna init / extract`)
2. `ACTIVATE IDENTITY_LOCK_SPECIALIST` → lock DNA
3. Confirm inject block is available for future handoffs

### Phase 3 — Pre-Production
- Mood boards / concept stills
- Director of Photography visual language
- Reference Asset Curator plate tiers
- (Optional) Animatic Director for pacing tests

### Phase 4 — Principal Photography
1. Sequence Director breaks work into clips
2. Specialists activated as needed (Stunts, VFX, Performance, Sound, ErosForge…)
3. Prompt Master + I2V Specialist prepare generation packages
4. Studio Director emits **Imagine Agent Mode Handoff**
5. Generation executes
6. Results return → QA Guardian / Chain QA

### Phase 5 — Post & Delivery
1. Color grade handoff
2. `ACTIVATE AI_POLISH_DIRECTOR` (upscale + face restoration)
3. Assembly Editor for rough cut / EDL if multi-clip
4. Key Art / Trailer Director for marketing assets
5. Final delivery readiness check

---

## 3. Key Concepts You Must Understand

### Imagine Agent Mode Handoff
The formal contract that moves planned work into generation surfaces without losing DNA, pipeline spec, sound layer, or return path.

Always prefer a validated handoff over raw pasting into the web UI for important shots.

### Specialist Order (Mandatory before video handoff)
```
DNA → Identity Lock → Reference Curator → Prompt Master → I2V Specialist → Handoff
```

### Explicitness Levels
- Level 1–2: Standard cinematic (SFW path)
- Level 3–4: Requires `ACTIVATE EROSFORGE` first

### Video Versions
- **1.0** — Cost-efficient default / drafts
- **1.5 Native** — Preferred for synchronized audio, physics, micro-expression, intimacy

Never mix 1.0 and 1.5 inside one continuous chain without Continuity Guardian + Studio Director approval.

---

## 4. Common Commands (Chat)

| Intent | Command |
|--------|---------|
| Start Studio | `Activate Grok Imagine Cinematic Studio v3.8.6` |
| New Project / Bible | Ask Studio Director or use CLI wizard |
| Lock Character | `ACTIVATE IDENTITY_LOCK` / DNA tools |
| Long Sequence | `ACTIVATE SEQUENCE_DIRECTOR` |
| Intimate / R-rated | `ACTIVATE EROSFORGE` (explicit only) |
| Final Polish | `ACTIVATE AI_POLISH_DIRECTOR` |
| Handoff to Generation | `ACTIVATE IMAGINE_AGENT_MODE_HANDOFF` |
| Quota Check | `ACTIVATE WORKFLOW_OPTIMIZER` or CLI |

---

## 5. CLI Power Users

```bash
cinematic-studio create-bible --wizard
cinematic-studio dna init --name "Kael Voss"
cinematic-studio dna lock
cinematic-studio sequence init reveal-arc
cinematic-studio imagine agent-handoff --surface grok_build_tools
cinematic-studio quota estimate --video-seconds 60
cinematic-studio ui                    # Interactive TUI
cinematic-studio validate
```

See [CLI Reference](../CLI_REFERENCE.md) for the full command set.

---

## 6. Best Practices

- Lock DNA early and reuse inject blocks
- Always declare VIDEO_PIPELINE_SPEC before first video spend
- Use readiness gates (`--strict-handoff`, `--strict-plate`, etc.) on hero work
- Prefer still → image-to-video on locked plates
- Capture LAST_FRAME_RECAP + MOMENTUM_VECTOR + AUDIO_MOMENTUM_VECTOR after every clip intended for extension
- Route explicit content through ErosForge — never silent
- Let Studio Director own surface selection

---

## 7. Getting Help

- Role Cards: `references/agents/`
- Quick Start: `docs/guides/Quick_Start_Guide.md`
- Architecture: `docs/ARCHITECTURE.md`
- Issues / Discussions: GitHub repository

---

*You are the director. The Studio exists to execute your vision with professional discipline.*
