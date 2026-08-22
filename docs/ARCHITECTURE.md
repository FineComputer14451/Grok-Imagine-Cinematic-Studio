# Architecture
## Grok Imagine Cinematic Studio v3.10.0

> [!NOTE]
> Independent community project — **not affiliated with or endorsed by xAI**. Full notice: [DISCLAIMER.md](../DISCLAIMER.md).

---

## High-Level Architecture

The studio is organized as a layered multi-agent system:

```
User / Grok Chat / Build CLI / Streamlit / TUI
        ↓
Orchestration Layer (Studio Director + Mega Production Architect)
        ↓
Specialist Agents (23+) + Core Protocols + Wave A
        ↓
Tools & CLI + Skills Runtime + Plugin Packs
        ↓
Execution Layer (xAI Imagine Image + Video 1.0/1.5)
        ↓
Post-Production & Delivery (Color → Polish → Assets)
```

**Live diagrams** (Mermaid) also ship in the root [README.md](../README.md).

---

## Core Layers

### 1. Orchestration Layer

| Agent | Responsibility |
|-------|----------------|
| **Studio Director** | Central commander. Surface selection, specialist activation order, handoff decisions, final creative authority. |
| **Mega Production Architect** | Complete Production Bibles and execution roadmaps. |
| **Parallel Brief Dispatcher** | Concurrent specialist briefs under MAXIMUM AGENTIC MODE (Wave A). |

### 2. Specialist Agents (Selected)

| Category | Agents |
|----------|--------|
| **Identity & Continuity** | Character DNA Extractor, Identity Lock Specialist, Multi-Character Identity Arbiter, Continuity & Consistency Guardian, Multi-Clip Continuity Orchestrator, Costume & Wardrobe Continuity, Hair & Makeup Continuity |
| **Visual & Camera** | Director of Photography, Production Designer / Set Decorator, Key Art & Poster Designer, Plate & Motion Readiness Lead, Contact & Micro-Physics Specialist |
| **Sequence & Narrative** | Sequence Director, Cinematic Sequence Extender, Narrative Arc & Pacing Strategist, Performance & Emotion Director, Arc Replan Copilot, Animatic Director |
| **Prompt & Generation** | Imagine Prompt Master, Image-to-Video Specialist, I2I Refiners, AI Image Recreation |
| **Audio** | Sonic Architect (Native Audio Virtuoso), Foley Sound Design Specialist, Dialogue & ADR Director, Score & Temp Music Supervisor |
| **Post & Delivery** | AI Polish Director, Assembly Editor, Color Grading Supervisor, Quality Assurance Guardian, Title & Motion Graphics Lead, Distribution & Crop Strategist |
| **NSFW (Opt-in)** | ErosForge NSFW Director, NSFW Sequence Extender, NSFW Quota Orchestrator |
| **Ops** | Workflow Quota Optimizer, Reference Asset Curator, Grok Doctor, SFW Batch Orchestrator |

Full activation table: [`references/agents/AGENT_INDEX.md`](../references/agents/AGENT_INDEX.md).

### 3. Core Protocols

| Protocol | Role |
|----------|------|
| **Imagine Agent Mode Handoff** (`IMAGINE_AGENT_MODE_HANDOFF_v3.7.1`) | Validated packet routing planned work into execution surfaces |
| **Identity Continuity Protocol** (`IDENTITY_CONTINUITY_PROTOCOL_v3.8`) | DNA extract → lock → inject → drift detection across stills and sequences |
| **Specialist Order** | DNA → Identity Lock → Reference Curator → Prompt Master → I2V (video) → Handoff |
| **Readiness Gates** | Plate lock, motion brief, identity, spend, delivery (`--strict-*` flags) |
| **VIDEO_PIPELINE_SPEC** | Explicit 1.0 vs 1.5 Native (audio momentum vector when 1.5) |
| **Parallel Brief Protocol** | Concurrent specialist briefs under Studio Director |
| **Chain QA / NSFW Chain QA** | Extend/stitch Go/No-Go with evidence overlays |

#### Execution surfaces (handoff)

| Code | Meaning |
|------|---------|
| `grok_build_tools` | In-session tools (preferred) |
| `grok_agent_acp` | ACP / agent sessions |
| `grok_com_imagine` | Web UI paste (Classic Bridge) |
| `xai_api` | Live API jobs |

### 4. Runtime & Tools

| Component | Location / Entry |
|-----------|------------------|
| Skills runtime | `.grok/skills/` |
| Unified CLI | `cinematic-studio` · `tools/cinematic_studio_cli.py` |
| Interactive TUI | `cinematic-studio ui` (Textual; density modes 1/2/3) |
| Streamlit Web UI | `web_ui/app.py` |
| Plugin marketplace | `.grok-plugin/` + `config/plugin_packs.yaml` |
| Model registry | `tools/models.py` · `references/agents/MODEL_LAYER_v4.5.md` |
| Imagine bridge | `tools/imagine_bridge.py` · handoff validators |
| Control plane | `tools/control_plane_readiness.py` · phase3 helpers |
| Doctor | `tools/doctor.py` · `cinematic-studio doctor` |

### 5. Plugin Pack Architecture

Recommended install: **full suite**. Satellite packs filter the same skill tree (`full_suite_wins` declutter):

| Pack | Plugin name | Focus |
|------|-------------|-------|
| **Full Suite** | `grok-imagine-cinematic-studio` | Everything (recommended) |
| **Core** | `grok-imagine-cinematic-core` | Orchestration, DNA, Imagine, QA, quota |
| **Camera & Image** | `grok-imagine-camera-image` | DoP, i2i, key art, plate/motion, i2v |
| **Sequence & Narrative** | `grok-imagine-sequence-narrative` | Long-form, continuity, audio, action/VFX |
| **NSFW (opt-in)** | `grok-imagine-nsfw` | ErosForge + NSFW quota/extend/QA |
| **Delivery & Post** | `grok-imagine-delivery-post` | Assembly, color, polish, ffmpeg, distribution |

---

## Data Flow (Typical Hero Shot)

1. User activates Studio / creates Production Bible (`model_stack` + `VIDEO_PIPELINE_SPEC`)
2. DNA extracted and locked for character(s); wardrobe lock when needed
3. Reference Asset Curator assigns tier and plate policy
4. Plate & Motion Readiness Lead locks plates + motion vectors before video spend
5. Imagine Prompt Master crafts Ultimate Template prompt
6. (Video) Image-to-Video Specialist builds motion block
7. Studio Director emits validated Imagine Agent Mode Handoff packet
8. Generation executes on chosen surface
9. Results return via declared `return_path`
10. QA Guardian + Chain QA (if extend) + identity/continuity evidence
11. Color grade → AI Polish Director → Delivery readiness → marketing assets

---

## Operator Control Plane (v3.8.8+)

Surfaces share the same health signals (TUI Home, Streamlit Dashboard, CLI):

```
Orient → Health (doctor / validate / quota sync / models)
      → Produce (Bible / DNA / sequence / Imagine)
      → Gate (identity · plate · motion · chain QA · handoff validate)
      → Converge & Deliver (polish / deliver readiness · Wave A briefs)
```

**v3.10.0 density:** TUI and Streamlit expose compact / ops / full view modes so operators can scale detail without changing workflow.

---

## Design Principles

1. **Context preservation** is non-negotiable
2. **Gates before generation spend**
3. **Explicit surface routing** (never silent handoff)
4. **1.5 Native preferred** when audio, physics, or intimacy matter
5. **ErosForge is opt-in only**
6. **Studio Director has final authority** on creative and technical routing
7. **Evidence over vibes** for long-form Go/No-Go (drift, seam, AMV, temperature)

---

*Role Cards: `references/agents/` · Skills: `.grok/skills/` · Official manual: [OFFICIAL_DOCUMENTATION.md](OFFICIAL_DOCUMENTATION.md)*
