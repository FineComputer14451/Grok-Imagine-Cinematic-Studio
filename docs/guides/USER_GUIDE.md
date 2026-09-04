# User Guide
## Grok Imagine Cinematic Studio v3.11.4

Complete end-to-end guide for creators — from first Activate through delivery.

> [!NOTE]
> **Grok Imagine Cinematic Studio** is an **independent community project**. It is **not affiliated with, endorsed by, sponsored by, or officially connected to xAI**. Full notice: [DISCLAIMER.md](../../DISCLAIMER.md).

**Version:** 3.11.4 · **Last updated:** September 2026  
**Suite:** 25+ Role-Card agents · **64 skills** · full suite + 5 packs  
**Canonical manual:** [OFFICIAL_DOCUMENTATION.md](../OFFICIAL_DOCUMENTATION.md)

---

## 1. Activation

### Primary (any Grok chat)

```text
Activate Grok Imagine Cinematic Studio v3.11.4
```

Alternative triggers:

- `start cinematic production`
- `ACTIVATE GROK_IMAGINE_CINEMATIC_STUDIO`

On **grok.com** or mobile: paste [`MASTER_PROMPT.md`](../../MASTER_PROMPT.md) first for full lock-in, then Activate.

### Surfaces

| Surface | What works |
|---------|------------|
| **grok.com chat** | Activate / MASTER_PROMPT — no binary required |
| **grok.com/imagine** | Paste Execution Bridge packets from shell |
| **Grok mobile app** | Chat + in-app Imagine |
| **Desktop / Android shell** | Full CLI, TUI, Method A install, Grok Build ≥ 1.0.5 |

### Exit

```text
Exit cinematic studio
```

---

## 2. Recommended Production Workflow

### Phase 1 — Project Setup

1. Activate the Studio (**v3.11.4**).
2. Create / lock the **Production Bible**  
   (`cinematic-studio create-bible --wizard` or ask Studio Director / Guided Bible in Streamlit).
3. Declare **`model_stack`** + **`VIDEO_PIPELINE_SPEC`**:
   - **1.0** — cost-efficient drafts and most sequences
   - **1.5 Native** — synchronized audio, physics, intimacy, micro-expression hero work

### Phase 2 — Character & Identity

1. `ACTIVATE CHARACTER_DNA_EXTRACTOR` (or CLI `dna init` / `extract`)
2. `ACTIVATE IDENTITY_LOCK` → lock DNA
3. Optional: `ACTIVATE COSTUME_WARDROBE` when outfits must survive stills → i2v → extend
4. Confirm inject block is available for handoffs
5. Multi-character casts: `ACTIVATE MULTI_CHARACTER_ARBITER`

### Phase 3 — Pre-Production

- Mood boards / concept stills (Key Art, Production Designer, DoP)
- Director of Photography visual language
- Reference Asset Curator plate tiers + plate policy
- **Plate & Motion Readiness** before any video spend  
  (`ACTIVATE PLATE_MOTION_READINESS` · CLI `--strict-plate` / `--strict-motion`)
- Optional: Animatic Director for pacing tests

### Phase 4 — Principal Photography

1. Sequence Director breaks work into clips
2. Specialists as needed (Stunts, VFX, Performance, Sound, Wave A crafts, ErosForge…)
3. Parallel briefs under MAXIMUM AGENTIC MODE: `ACTIVATE PARALLEL_BRIEF_DISPATCHER`
4. Prompt Master + I2V Specialist prepare generation packages
5. Studio Director emits **Imagine Agent Mode Handoff**
6. Validate: `cinematic-studio handoff validate <path>` (add `--strict-handoff` / `--strict-wave-a` for hero work)
7. Generation executes on chosen surface
8. Results return → QA Guardian / Chain QA

### Phase 5 — Post & Delivery

1. Color grade handoff
2. `ACTIVATE AI_POLISH_DIRECTOR` (upscale + face restoration)
3. Assembly Editor for rough cut / EDL if multi-clip
4. Title & Motion Graphics + Distribution & Crop Strategist (Wave A)
5. Key Art / Trailer Director for marketing assets
6. Final delivery readiness check (Dashboard **Delivery** / TUI panels)

---

## 3. Operator Control Plane (do this before long spend)

Shared loop on **TUI Home**, **Streamlit Dashboard**, and **CLI**:

```text
Orient → Health → Produce → Gate → Converge & Deliver
```

| Step | What to do |
|------|------------|
| **Orient** | Open `cinematic-studio ui` or Streamlit Dashboard; read severity strip + Attention list |
| **Health** | Doctor · validate · quota sync · models verify / stack |
| **Produce** | Bible / DNA / sequences / Imagine (**spend is not on TUI launcher**) |
| **Gate** | Identity · plate/motion · chain QA · `handoff validate` |
| **Deliver** | Convergence checklist · Wave A briefs · polish/deliver readiness · bridge preview |

**TUI density:** `1` compact · `2` ops · `3` full · `Tab` cycle · `p` pause refresh.

**Deep dive:** [OPERATOR_CONTROL_PLANE.md](OPERATOR_CONTROL_PLANE.md).

---

## 4. Key Concepts You Must Understand

### Imagine Agent Mode Handoff

Formal contract that moves planned work into generation surfaces without losing DNA, pipeline spec, sound layer, or return path.

Always prefer a **validated** handoff over raw pasting into the web UI for important shots.

### Specialist order (mandatory before video handoff)

```text
DNA → Identity Lock → Reference Curator → Plate/Motion → Prompt Master → I2V Specialist → Handoff
```

### Explicitness levels

- **Level 1–2:** Standard cinematic (SFW path)
- **Level 3–4:** Requires `ACTIVATE EROSFORGE` first — never silent

### Video versions

| Version | Use |
|---------|-----|
| **1.0** | Cost-efficient default / drafts |
| **1.5 Native** | Preferred for synchronized audio, physics, micro-expression, intimacy |

Never mix 1.0 and 1.5 inside one continuous chain without Continuity Guardian + Studio Director approval.

### Readiness gates (CLI)

| Flag | Enforces |
|------|----------|
| `--strict-handoff` | Full packet + specialist checklist |
| `--strict-plate` | Plate lock |
| `--strict-motion` | Motion vector / I2V readiness |
| `--strict-identity` | Identity gate on extend path |
| `--strict-wave-a` | Wave A packet completeness |

### Wave A (v3.8.8+)

Eight specialists for plate/motion, micro-physics, HMU, dialogue/ADR, score/temp music, titles, distribution crops, and parallel brief dispatch.

```bash
cinematic-studio wave-a --help
cinematic-studio wave-a briefs
cinematic-studio wave-a validate
```

---

## 5. Common Commands (Chat)

| Intent | Command |
|--------|---------|
| Start Studio | `Activate Grok Imagine Cinematic Studio v3.11.4` |
| New project / Bible | Ask Studio Director or CLI wizard |
| Lock character | `ACTIVATE IDENTITY_LOCK` / DNA tools |
| Wardrobe lock | `ACTIVATE COSTUME_WARDROBE` |
| Long sequence | `ACTIVATE SEQUENCE_DIRECTOR` + `ACTIVATE SEQUENCE_EXTENDER` |
| Parallel briefs | `ACTIVATE PARALLEL_BRIEF_DISPATCHER` |
| Intimate / R-rated | `ACTIVATE EROSFORGE` (explicit only) |
| Final polish | `ACTIVATE AI_POLISH_DIRECTOR` |
| Handoff to generation | `ACTIVATE IMAGINE_AGENT_MODE_HANDOFF` |
| Quota check | `ACTIVATE WORKFLOW_OPTIMIZER` or CLI |
| Studio health | `ACTIVATE GROK_DOCTOR` · `RUN STUDIO_HEALTH_CHECK` |

Full activation table: [`references/agents/AGENT_INDEX.md`](../../references/agents/AGENT_INDEX.md).

---

## 6. CLI Power Users

```bash
# Health
cinematic-studio grok ensure
cinematic-studio models verify
cinematic-studio doctor --quick
cinematic-studio validate

# Bible & DNA
cinematic-studio create-bible --wizard
cinematic-studio dna init --name "Kael Voss"
cinematic-studio dna lock

# Sequences
cinematic-studio sequence init reveal-arc
cinematic-studio sequence add-clip ...
cinematic-studio sequence handoff
cinematic-studio sequence qa
cinematic-studio sequence color-grade
cinematic-studio sequence polish
cinematic-studio sequence deliver

# Imagine / gates
cinematic-studio imagine agent-handoff --surface grok_build_tools --format markdown
cinematic-studio handoff validate path/to/packet.json --strict-handoff
cinematic-studio wave-a validate

# Quota & ledger
cinematic-studio quota estimate --video-seconds 60 --tier heavy
cinematic-studio quota dashboard
cinematic-studio generation summary

# Control plane
cinematic-studio ui
# streamlit run web_ui/app.py
```

See [CLI_REFERENCE.md](../CLI_REFERENCE.md) for the full command set (including TUI keys).

---

## 7. Best Practices

- Lock DNA **early** and reuse inject blocks
- Always declare `VIDEO_PIPELINE_SPEC` before first video spend
- Use readiness gates on hero work (`--strict-handoff`, `--strict-plate`, `--strict-motion`, `--strict-identity`)
- Prefer still → image-to-video on **locked plates**
- Capture `LAST_FRAME_RECAP` + `MOMENTUM_VECTOR` + `AUDIO_MOMENTUM_VECTOR` after every clip intended for extension
- Route explicit content through **ErosForge** — never silent
- Let Studio Director own **surface selection**
- Run Orient + Health before long generations (TUI / Dashboard)
- Prefer **1.5 Native** when audio, physics, or intimacy matter
- Track spend with `generation` ledger + quota tools

---

## 8. Getting Help

| Resource | Path |
|----------|------|
| Official Documentation | [docs/OFFICIAL_DOCUMENTATION.md](../OFFICIAL_DOCUMENTATION.md) |
| Official Overview | [docs/OFFICIAL_OVERVIEW.md](../OFFICIAL_OVERVIEW.md) |
| Quick Start | [Quick_Start_Guide.md](Quick_Start_Guide.md) |
| Operator Control Plane | [OPERATOR_CONTROL_PLANE.md](OPERATOR_CONTROL_PLANE.md) |
| Architecture | [docs/ARCHITECTURE.md](../ARCHITECTURE.md) |
| CLI Reference | [docs/CLI_REFERENCE.md](../CLI_REFERENCE.md) |
| Role Cards | `references/agents/` |
| Changelog | [CHANGELOG.md](../../CHANGELOG.md) |
| Issues | GitHub repository |

---

*You are the director. The Studio exists to execute your vision with professional discipline.*

*Grok Imagine Cinematic Studio v3.11.4 — User Guide · Independent community project · Not affiliated with xAI*
