# Architecture
## Grok Imagine Cinematic Studio v3.8.6

---

## High-Level Architecture

The studio is organized as a layered multi-agent system:

```
User / Grok Chat / Build CLI
        ↓
Orchestration Layer (Studio Director + Mega Production Architect)
        ↓
Specialist Agents (23+) + Core Protocols
        ↓
Tools & CLI + Skills Runtime
        ↓
Execution Layer (xAI Imagine Image + Video 1.0/1.5)
        ↓
Post-Production & Delivery (Color → Polish → Assets)
```

---

## Core Layers

### 1. Orchestration Layer
- **Studio Director** — Central commander. Owns surface selection, specialist activation order, handoff decisions, and final creative authority.
- **Mega Production Architect** — Builds complete Production Bibles and execution roadmaps.

### 2. Specialist Agents (Selected)

| Category | Agents |
|----------|--------|
| **Identity & Continuity** | Character DNA Extractor, Identity Lock Specialist, Multi-Character Identity Arbiter, Continuity & Consistency Guardian |
| **Visual & Camera** | Director of Photography, Production Designer / Set Decorator, Key Art & Poster Designer |
| **Sequence & Narrative** | Sequence Director, Cinematic Sequence Extender, Narrative Arc & Pacing Strategist, Performance & Emotion Director |
| **Prompt & Generation** | Imagine Prompt Master, Image-to-Video Specialist, i2i Refiners |
| **Audio** | Sonic Architect (Native Audio Virtuoso), Foley Sound Design Specialist |
| **Post & Delivery** | AI Polish Director, Assembly Editor, Quality Assurance Guardian |
| **NSFW (Opt-in)** | ErosForge NSFW Director, NSFW Sequence Extender, NSFW Quota Orchestrator |
| **Ops** | Workflow Quota Optimizer, Reference Asset Curator, Generation Tracker |

### 3. Core Protocols

- **Imagine Agent Mode Handoff (v3.7.1 / Enhanced v4.5)**  
  Validated packet that routes planned work into four execution surfaces:  
  `grok_build_tools` · `grok_agent_acp` · `grok_com_imagine` · `xai_api`

- **Identity Continuity Protocol**  
  DNA extract → lock → inject → drift detection across stills and sequences.

- **Specialist Order**  
  DNA → Identity Lock → Reference Curator → Prompt Master → I2V (for video) → Handoff.

- **Readiness Gates**  
  Plate lock, motion brief, identity, spend, and delivery gates (`--strict-*` flags).

- **VIDEO_PIPELINE_SPEC**  
  Explicit declaration of 1.0 vs 1.5 Native (with audio momentum vector requirements).

### 4. Runtime & Tools

- **52 Skills** under `.grok/skills/`
- **Unified CLI** (`cinematic-studio` / `tools/cinematic_studio_cli.py`)
- **Streamlit Web UI** for guided Bible, DNA bank, quota, sequences
- **Plugin Marketplace** (`.grok-plugin/`) with full suite + satellite packs
- **Model Registry** (`tools/models.py`) — Grok 4.5 primary + v9-4p5 multi/chat-expert + Imagine dual path

---

## Data Flow (Typical Hero Shot)

1. User activates Studio / creates Production Bible
2. DNA extracted and locked for character(s)
3. Reference Asset Curator assigns tier and plate policy
4. Imagine Prompt Master crafts Ultimate Template prompt
5. (Video) Image-to-Video Specialist builds motion block
6. Studio Director emits validated Imagine Agent Mode Handoff packet
7. Generation executes on chosen surface
8. Results return via declared `return_path`
9. QA Guardian + Chain QA (if extend)
10. Color grade → AI Polish Director → Delivery

---

## Design Principles

1. **Context preservation** is non-negotiable
2. **Gates before generation spend**
3. **Explicit surface routing** (never silent handoff)
4. **1.5 Native preferred** when audio, physics, or intimacy matter
5. **ErosForge is opt-in only**
6. **Studio Director has final authority** on creative and technical routing decisions

---

*For Role Card details see `references/agents/AGENT_INDEX.md` and individual agent files.*
