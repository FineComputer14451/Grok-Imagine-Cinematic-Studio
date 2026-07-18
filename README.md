## 🎬 Grok Imagine Cinematic Studio

> **v3.8.3** — The most advanced multi-agent cinematic production system for Grok 4.5 Build + Grok 4.3 cinematic dual-stack

**Requires Grok Build ≥ 0.2.93** | **Native Imagine Video 1.5 support with synchronized audio**

<p align="center">
  <img src="assets/banner.jpg" alt="Grok Imagine Cinematic Studio - Premium Cinematic Banner" width="100%" style="max-width: 1200px; border-radius: 12px;">
</p>

<p align="center">
  <img src="assets/logo.jpg" alt="Grok Imagine Cinematic Studio Logo" width="260">
</p>

<p align="center">
  <strong>Logline → Production Bible → Character DNA Lock → Physics-Aware Sequences → Color Grade → AI Polish → Delivery</strong><br>
  <em>Emotionally powerful, identity-locked, production-ready cinematic content at Hollywood standards.</em>
</p>

<p align="center">
  <a href="https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License"></a>
  <img src="https://img.shields.io/badge/version-3.8.3-success.svg" alt="v3.8.3">
  <img src="https://img.shields.io/badge/Grok%20Build-%E2%89%A5%200.2.93-orange.svg" alt="Grok Build ≥ 0.2.93">
  <a href="https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/stargazers"><img src="https://img.shields.io/github/stars/FineComputer14451/Grok-Imagine-Cinematic-Studio?style=social" alt="GitHub Stars"></a>
</p>

---

## ✨ What is Grok Imagine Cinematic Studio?

**Grok Imagine Cinematic Studio** is a complete, production-grade multi-agent framework that turns creative ideas into locked, emotionally resonant cinematic sequences using Grok 4.5 (primary) + Grok 4.3 (1M context) dual-stack orchestration and xAI’s Imagine models (Image + native Video 1.5 with audio).

It combines:

- **48 specialized Grok skills** powering a **23+ agent cinematic department**
- Professional **Production Bible** workflow (CLI wizard + Streamlit Web UI)
- **Character DNA extraction + Identity Continuity Protocol** for zero-drift consistency across stills, clips, and long sequences
- **Imagine Agent Mode Handoff** — validated routing from planning agents into Grok’s native generation surfaces
- End-to-end pipeline: pre-production → principal photography (sequences) → post (color → polish) → delivery + marketing assets
- Full support for both blockbuster SFW and artistically justified R-rated / NSFW productions

Whether you’re crafting Marvel-style hero reveals, cyberpunk neon sequences, intimate character studies, or epic trailers — the studio gives you director-level control, specialist collaboration, strict QA gates, and quota intelligence in one cohesive system.

---

## 🚀 What’s New in v3.8.3

- **Plate Lock & Motion Brief Readiness** — Structured `plate_status` and `motion_vector` (action/camera/emotion) with soft/hard gates (`--strict-plate`, `--strict-motion`)
- **Specialist-Order Checklist** + **Color → Polish Handoff** — `sequence color-grade` → `polish --require-color-grade`; stamped manifests and readiness validators
- **Identity Continuity Protocol v1.0** — Drift evidence tracking, `--strict-identity` gates, multi-signal still comparison
- **Plugin Packs & Marketplace** (v3.8.0) — Full suite + modular satellite packs (core, nsfw, sequence-narrative, delivery-post, camera-image) with declutter policy
- **Imagine Agent Mode Handoff** (v3.7.1) — Canonical packet spec, surface routing (grok_build_tools / grok_agent_acp / grok_com_imagine / xai_api), strict handoff validation
- Streamlit Community Cloud deploy support + improved Web UI dashboard
- Continuous refinements to chain QA, quota orchestration, NSFW physics-aware pipelines, and final delivery polish (AI upscaler + face restoration)

See full details in [CHANGELOG.md](CHANGELOG.md).

---

## 🏗️ System Architecture (v3.8.3)

**Core Philosophy**: A modular "studio" of specialized agents that collaborate under the **Studio Director**, with strong handoff protocols, identity locking, and production gates. The system bridges high-level creative direction (Grok chat / Build) with low-level execution (Imagine Image/Video 1.5).

### Visual Architecture (Illustrative)

> **Note**: Architecture diagrams below reflect core modularity (v3.3 concept). The fundamental structure — Studio Director orchestration, Role Cards, plugin marketplace, CLI + Web UI, and 48 runtime skills — remains the foundation of v3.8.3.

![System Architecture](assets/system_architecture_v3.3.png)

![Orchestration Flow](assets/orchestration_flow_v3.3.png)

``` 
Grok Imagine Cinematic Studio v3.8.3  (Studio Director + 23+ Agents · Grok 4.5 primary)
├── .grok-plugin/                 # Marketplace manifests + plugin packs (full suite + 5 satellites)
├── references/agents/            # 23+ Role Cards, AGENT_INDEX, MODEL_LAYER_v3.7.1+, handoff protocols, IDENTITY_CONTINUITY_PROTOCOL
├── tools/                        # character_dna, sequence_chain, quota_optimizer, nsfw_*, models.py, bible_stages, imagine_bridge, handoff_schema, cli/
├── tools/cinematic_studio_cli.py   # Unified CLI: create-bible --wizard, dna, sequence, quota, nsfw, imagine, models, plugin, validate...
├── references/MODELS_v3.6.md   # Dual-stack registry (grok-4.5 cinematic default + Grok Build)
├── web_ui/app.py                 # Streamlit dashboard: Guided Bible, DNA bank, sequence mgmt, live cost estimation
├── examples/                     # Production Bible templates & sample projects
├── MASTER_PROMPT.md              # Primary activation prompt (v3.8+ compatible)
├── scripts/                      # Release helpers, verify, thin shims
└── .grok/skills/                 # 48 custom Grok skills (runtime engine for all agents)
```

**Key v3.8.3 Components**
- `references/agents/` — Authoritative Role Cards + protocols (Studio Director owns orchestration & handoff decisions)
- `references/agents/MODEL_LAYER_v3.7.1.md` + `IDENTITY_CONTINUITY_PROTOCOL_v3.8.md` — Operating rules + drift detection for every skill/agent
- `MASTER_PROMPT.md` — Activation entrypoint with Grok 4.5 stack + Imagine Agent Mode Handoff
- `tools/cli/bible_stages.py` + Web UI — Guided Production Bible wizard (multi-stage TTY or beautiful form UI)
- `tools/imagine_bridge.py` + handoff validators — Build validated `imagine_agent_mode_handoff` packets
- `.grok-plugin/` + `config/plugin_packs.yaml` — Full marketplace + pack system with `full_suite_wins` declutter
- `cinematic-studio` CLI — Power-user automation, plugin catalog management, preflight checks

---

## 🎨 Visual Identity & Branding

The studio presents a premium Hollywood-grade aesthetic with a custom cinematic banner featuring a massive camera lens, holographic AI elements, gold/teal accents, and film-production elegance.

The included `assets/logo.jpg` and `assets/favicon.jpg` complete the visual identity for Web UI and repository presentation.

### Cinematic Output Philosophy

Every generation targets:
- **Locked character identity** (DNA extraction → injection → continuity protocol)
- **Physics-aware motion** (especially native Imagine Video 1.5)
- **Native synchronized audio** & immersive sound design
- **Emotional micro-expression timing** and performance authenticity
- **Cinematic lighting, composition, and color** ready for color-grade → polish pipeline
- **Strict QA gates** before delivery (plate lock, motion brief, identity drift, specialist checklists)

---

## 🚀 Getting Started

### 1. Prerequisites
- Grok Build CLI ≥ **0.2.93**
- Access to Grok 4.5 (cinematic) and/or Grok 4.3 (1M context)
- xAI Imagine access (Image + Video 1.0 / 1.5)
- Python 3.12+ environment (for CLI + Web UI)

### 2. Activate the Studio (Primary Workflow)

In any Grok chat:

```
Activate Grok Imagine Cinematic Studio v3.8.3
```

or the shorter trigger:

```
start cinematic production
```

This loads the full **23+ agent department** with Production Bible support, Imagine Agent Mode Handoff, identity locking, and all specialists.

### 3. CLI Power Tools (Automation & Scripting)

```bash
# Verify model stack compatibility
cinematic-studio models verify

# Guided Production Bible (interactive wizard)
cinematic-studio create-bible --wizard

# Or non-interactive
cinematic-studio create-bible "My Epic Project Title"

# Character DNA pipeline
cinematic-studio dna init --name "Hero Name"
cinematic-studio dna lock

# Sequence management
cinematic-studio sequence init my-sequence
cinematic-studio sequence add-clip ...

# Quota intelligence & cost simulation
cinematic-studio quota estimate --video-seconds 45 --tier heavy

# Plugin marketplace
cinematic-studio plugin catalog
cinematic-studio plugin packs
```

See full command reference in the [Quick Start Guide](docs/guides/Quick_Start_Guide.md) and run `cinematic-studio --help`.

### 4. Web UI (Recommended for Guided Work)

```bash
streamlit run web_ui/app.py
```

Beautiful dashboard featuring:
- Multi-step Guided Bible Creator
- Character DNA Bank & injection blocks
- Live quota/cost estimator
- Sequence health dashboard
- Model pickers (grok-4.5 / 1.5 video)

Deployable to Streamlit Community Cloud (see `docs/guides/streamlit_cloud_deploy.md`).

### 5. Full Documentation

- **[Quick Start Guide](docs/guides/Quick_Start_Guide.md)** — Detailed activation, workflow phases, specialist table, pro tips
- **[UPGRADE_GUIDE.md](UPGRADE_GUIDE.md)** — Migration steps between versions
- **[CHANGELOG.md](CHANGELOG.md)** — Complete release history (highly recommended reading)
- **[MASTER_PROMPT.md](MASTER_PROMPT.md)** — The canonical activation prompt
- **Role Cards & Protocols**: `references/agents/AGENT_INDEX.md` and individual `.md` files
- **Production Bible Template**: `Project_Bible_Template.md` + `examples/`

---

## 📋 Recommended Production Workflow (High-Level)

1. **Activate Studio** → **Start New Project** → **Build & Lock Production Bible** (include `VIDEO_PIPELINE_SPEC` for 1.5 native audio)
2. **Pre-Production**: Character DNA extraction + lock, environment concepts, mood boards, DoP visual language
3. **Principal Photography**: Use Sequence Director + Extender for long-form; activate specialists (Stunts, VFX, Sound, Performance) as needed
4. **Review & Polish**: QA Guardian review → Color Grade handoff → AI Polish Director (upscale + face restore) → Delivery readiness gates
5. **Marketing Assets**: Key Art Designer + Trailer Director for posters, hero reveals, teasers

**Pro Tip**: Combine steps naturally, e.g.:
> "Activate Grok Imagine Cinematic Studio v3.8.3, start new project called 'VOIDWALKER', generate the full Production Bible with 1.5 video pipeline, lock the lead character DNA, and create the hero reveal key art."

---

## 🧠 Core Specialists (Activation Commands)

| Specialist                        | Activation Command                      | Primary Strength                          |
|-----------------------------------|-----------------------------------------|-------------------------------------------|
| Studio Director                   | `ACTIVATE STUDIO_DIRECTOR`              | Overall orchestration & handoff decisions |
| Mega Production Architect         | `ACTIVATE MEGA_PRODUCTION_ARCHITECT`    | Full Production Bible + execution roadmap |
| Identity Lock Specialist          | `ACTIVATE IDENTITY_LOCK`                | Character DNA, continuity, drift detection|
| Imagine Prompt Master             | `ACTIVATE IMAGINE_PROMPT_MASTER`        | Photorealistic prompt engineering (1.5)   |
| Director of Photography           | `ACTIVATE DOP`                          | Cinematic lighting, camera choreography   |
| Sequence Director                 | `ACTIVATE SEQUENCE_DIRECTOR`            | Long-form sequencing & 1.5 extend/stitch  |
| Cinematic Sequence Extender       | `ACTIVATE SEQUENCE_EXTENDER`            | 60–180s+ seamless expansions             |
| ErosForge NSFW Director           | `ACTIVATE EROSFORGE`                    | Artistic R-rated / intimate scenes        |
| AI Polish Director                | `ACTIVATE AI_POLISH_DIRECTOR`           | Final upscale, face restoration, delivery |
| Workflow Quota Optimizer          | `ACTIVATE WORKFLOW_OPTIMIZER`           | Real-time cost, risk, budget management   |
| Quality Assurance Guardian        | `ACTIVATE QA_GUARDIAN`                  | 16-point weighted QA + chain QA           |
| VFX & SFX Supervisor              | `ACTIVATE VFX_SFX_SUPERVISOR`           | Particles, creatures, destruction         |
| Sonic Architect / Foley           | `ACTIVATE SONIC_ARCHITECT`              | Native audio design & realistic foley     |

*Full list and detailed Role Cards in `references/agents/AGENT_INDEX.md`*

---

## 🔧 CLI & Tooling Highlights

- `cinematic-studio create-bible --wizard` — Interactive guided Production Bible
- `cinematic-studio dna ...` — Full character DNA lifecycle (init, extract, lock, handoff, inject)
- `cinematic-studio sequence ...` — Init, add clips, handoff, extend, qa, color-grade, polish, deliver
- `cinematic-studio quota ...` — Estimate, dashboard, optimize, record spend
- `cinematic-studio nsfw ...` — Dedicated NSFW batch planning, quota orchestration, physics QA
- `cinematic-studio imagine agent-handoff` — Emit validated handoff packets for native Imagine execution
- `cinematic-studio plugin catalog pin` / `check --release` — Release hygiene for the Grok plugin marketplace
- `cinematic-studio validate` — Project health & strict gate checks

All commands support `--help` and rich output. Many also have direct Python entrypoints under `tools/cli/`.

---

## 📄 Documentation & Further Reading

| Resource                              | Path                                              | Purpose                                      |
|---------------------------------------|---------------------------------------------------|----------------------------------------------|
| Quick Start Guide                     | `docs/guides/Quick_Start_Guide.md`                | Complete onboarding + workflow + tips        |
| UPGRADE_GUIDE                         | `UPGRADE_GUIDE.md`                                | Version migration notes                      |
| CHANGELOG                             | `CHANGELOG.md`                                    | Detailed release notes (start here)          |
| MASTER_PROMPT                         | `MASTER_PROMPT.md`                                | Primary chat activation prompt               |
| Agent Index & Role Cards              | `references/agents/AGENT_INDEX.md`                | Every specialist’s capabilities & triggers  |
| Production Bible Template             | `Project_Bible_Template.md`                       | Professional structured template             |
| Models Registry                       | `references/MODELS_v3.6.md`                       | Dual-stack model slugs & pricing             |
| Kink-Specific Cinematic Template      | `Kink_Specific_Cinematic_Template_Library_v3.3.md`| NSFW artistic standards & prompt library     |

---

## 🤝 Contributing

This project is under active development. Contributions are welcome!

- New specialist agents / Role Cards
- Prompt engineering improvements & MASTER_PROMPT refinements
- Additional CLI commands or Web UI features
- Documentation, examples, and Production Bible templates
- Bug reports, strict-gate test cases, and edge-case handling

Please read [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before submitting PRs.

For major architectural changes, open an issue first to discuss alignment with the Studio Director’s vision and handoff protocols.

---

## ⚖️ License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <strong>Built for creators who want cinematic AI that feels directed, not just generated.</strong><br>
  <em>Grok Imagine Cinematic Studio v3.8.3 — July 2026</em>
</p>

---

**Ready to direct your next masterpiece?**

Just say: **"Activate Grok Imagine Cinematic Studio v3.8.3"** and begin.
