# Grok Imagine Cinematic Studio
# Official Documentation

**Version:** 3.10.0  
**Status:** Canonical product manual (draft refresh — August 2026)  
**Repository:** [FineComputer14451/Grok-Imagine-Cinematic-Studio](https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio)

> [!NOTE]
> **Grok Imagine Cinematic Studio** is an **independent community project**. It is **not affiliated with, endorsed by, sponsored by, or officially connected to [xAI](https://x.ai)**. “Official Documentation” means this project’s own documentation — not an xAI publication. Grok, Grok Build, Grok Imagine, and related marks are trademarks of their respective owners. Full notice: [DISCLAIMER.md](../DISCLAIMER.md).

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Independence & Disclaimer](#2-independence--disclaimer)
3. [Requirements](#3-requirements)
4. [Installation](#4-installation)
5. [Activation](#5-activation)
6. [Production Workflow](#6-production-workflow)
7. [Operator Control Plane](#7-operator-control-plane)
8. [Agents & Skills](#8-agents--skills)
9. [CLI Reference (Summary)](#9-cli-reference-summary)
10. [Web UI & TUI](#10-web-ui--tui)
11. [Plugin Packs](#11-plugin-packs)
12. [Models & Video Pipelines](#12-models--video-pipelines)
13. [Protocols & Gates](#13-protocols--gates)
14. [Wave A Multi-Agent Scaffold](#14-wave-a-multi-agent-scaffold)
15. [NSFW / R-Rated (Opt-in)](#15-nsfw--r-rated-opt-in)
16. [Repository Map](#16-repository-map)
17. [Examples & Templates](#17-examples--templates)
18. [Upgrading](#18-upgrading)
19. [Contributing](#19-contributing)
20. [License](#20-license)
21. [Document Index](#21-document-index)

---

## 1. Introduction

**Grok Imagine Cinematic Studio** is a production-grade multi-agent framework that turns creative ideas into locked, emotionally resonant cinematic sequences using:

- **Grok 4.5** (primary cinematic + Build) with optional **Grok 4.3** (1M context)
- **xAI Imagine** Image **1.0 / 2.0** + Video **1.0 / 1.5 Native** (synchronized audio on 1.5; **no Video 2.0**)
- A **virtual film department**: Studio Director, 25+ specialists, readiness gates, and delivery polish

### Core Promise

```text
Logline → Production Bible → Character DNA Lock
       → Physics-Aware Sequences → Color Grade → AI Polish → Delivery
```

Emotionally powerful, identity-locked, production-ready content — directed, not merely generated.

### What You Get

| Surface | Purpose |
|---------|---------|
| **Grok chat activation** | Full multi-agent department via `MASTER_PROMPT` / Activate phrase |
| **`cinematic-studio` CLI** | Bible, DNA, sequence, quota, handoff, plugins, Wave A, doctor, validate |
| **Interactive TUI** | Live dashboard + safe launcher + production cockpit (density modes) |
| **Streamlit Web UI** | Guided Bible, DNA bank, sequences, Imagine, cost estimation, dashboard |
| **Plugin marketplace** | Full suite (64 skills) + 5 modular satellite packs |

**Short pitch:** [OFFICIAL_OVERVIEW.md](OFFICIAL_OVERVIEW.md)  
**System design:** [ARCHITECTURE.md](ARCHITECTURE.md)

---

## 2. Independence & Disclaimer

| Topic | Meaning |
|-------|---------|
| **Independence** | Community-maintained orchestration suite — not an official xAI product |
| **Trademarks** | “Grok,” “Grok Build,” “Grok Imagine,” “xAI” used only for interoperability |
| **APIs & billing** | Keys, quotas, pricing, and access are solely between you and xAI / host platform |
| **No warranty** | MIT **as is** — always QA outputs before delivery |
| **Your responsibility** | Laws, platform policies, copyright of references, age rules, optional NSFW use |

Canonical text: **[DISCLAIMER.md](../DISCLAIMER.md)**.

---

## 3. Requirements

| Requirement | Notes |
|-------------|-------|
| **Grok Build CLI ≥ 1.0.5** | `cinematic-studio grok ensure` can install/upgrade |
| **Grok 4.5 access** | Cinematic default; optional Grok 4.3 for 1M context |
| **xAI Imagine** | Image + Video 1.0 / 1.5 |
| **Python 3.12+** | CLI + Streamlit Web UI |
| **Account tier** | SuperGrok / Heavy recommended for serious video quotas |

**Surfaces without the Grok Build binary:** [grok.com](https://grok.com) web chat and the Grok mobile app. Use chat Activate / `MASTER_PROMPT.md` there; use a shell for full CLI.

| Surface | What works |
|---------|------------|
| **grok.com chat** | Activate phrase / paste `MASTER_PROMPT.md` |
| **grok.com/imagine** | Paste Execution Bridge packets from shell |
| **Grok mobile app** | Same as chat + in-app Imagine |
| **Desktop / Android shell** | Full Method A + `cinematic-studio` + Grok Build CLI |

---

## 4. Installation

Two supported paths (both can ship the full skill suite):

### Method A — Local CLI install (power users)

```bash
git clone https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio.git
cd Grok-Imagine-Cinematic-Studio
bash scripts/cinematic_studio.sh install
# or: bash scripts/install_cinematic_studio.sh

cinematic-studio grok ensure
cinematic-studio models verify
cinematic-studio doctor --quick
```

### Method B — Grok plugin marketplace

```bash
grok plugin install grok-imagine-cinematic-studio
# or update:
grok plugin update grok-imagine-cinematic-studio
```

As of **v3.8.0+**, modular **packs** are available (full suite recommended). See [§11 Plugin Packs](#11-plugin-packs).

**Detailed guide:** [guides/installation_guide.md](guides/installation_guide.md).

### Python dependencies (CLI / Web)

```bash
pip install -r requirements.txt
# Web UI extras:
pip install -r requirements-streamlit.txt
```

---

## 5. Activation

### Primary (any Grok chat)

```text
Activate Grok Imagine Cinematic Studio v3.11.0
```

or

```text
start cinematic production
```

On the web, for full lock-in: paste [`MASTER_PROMPT.md`](../MASTER_PROMPT.md), then Activate.

### Start a project

```text
Start new project
```

or combine steps:

```text
Activate Grok Imagine Cinematic Studio v3.11.0, start new project called 'VOIDWALKER',
generate the full Production Bible with VIDEO_PIPELINE_SPEC for 1.5,
lock the lead character DNA, and create the hero reveal key art.
```

### Exit

```text
Exit cinematic studio
```

---

## 6. Production Workflow

### Phase 1 — Activation & Planning

1. Activate the studio (v3.11.0).
2. Start a new project (title, logline, genre, tone, length, cast).
3. **Build & lock the Production Bible** with:
   - `model_stack`
   - `VIDEO_PIPELINE_SPEC` (1.0 cost default · 1.5 when native audio / physics / intimacy matter)

```bash
cinematic-studio create-bible --wizard
# or
cinematic-studio create-bible "My Epic Project Title"
```

Web: **Production → Guided Bible Creator**.

### Phase 2 — Pre-Production

4. Character DNA extract → lock → inject; wardrobe lock when outfits must survive stills → i2v → extend.
5. Environment concepts, mood boards, DoP visual language.
6. Reference Asset Curator: tiers + plate policy.
7. Plate & Motion Readiness before video spend.

```bash
cinematic-studio dna init --name "Hero Name"
cinematic-studio dna lock
```

### Phase 3 — Principal Photography

8. Sequence Director + specialists (Stunts, VFX, Sound, Performance, Wave A crafts).
9. Imagine Agent Mode Handoff → generate on chosen surface.
10. Long-form: Sequence Extender, memory bank, Chain QA, continuity evidence.

```bash
cinematic-studio sequence init my-sequence
cinematic-studio sequence add-clip ...
cinematic-studio sequence handoff
cinematic-studio imagine agent-handoff --surface grok_build_tools --format markdown
```

### Phase 4 — Review & Polish

11. QA Guardian (16-point) + Chain QA on extends.
12. Color grade handoff → **AI Polish Director** (upscale + face restore).
13. Delivery readiness gates.

```bash
cinematic-studio sequence qa
cinematic-studio sequence color-grade
cinematic-studio sequence polish
cinematic-studio sequence deliver
```

### Phase 5 — Marketing

14. Key Art Designer + Trailer Director for posters, hero reveals, teasers.
15. Optional Localization Specialist.

**Expanded walkthrough:** [guides/Quick_Start_Guide.md](guides/Quick_Start_Guide.md) · [guides/USER_GUIDE.md](guides/USER_GUIDE.md) · [guides/OPERATOR_CONTROL_PLANE.md](guides/OPERATOR_CONTROL_PLANE.md).

---

## 7. Operator Control Plane

Before long generations, run the shared **Orient → Health → Produce → Gate → Deliver** loop (TUI Home, Streamlit Dashboard, CLI).

| Step | Actions |
|------|---------|
| **Orient** | Open `cinematic-studio ui` or Streamlit Dashboard; read severity strip (OK / WARN / CRITICAL) + Attention list |
| **Health** | Doctor · validate · quota sync · models verify / stack |
| **Produce** | Bible / DNA / sequences / Imagine (spend stays off TUI launcher) |
| **Gate** | Identity · chain QA · plate/motion · `handoff validate` |
| **Converge & deliver** | Convergence checklist · Wave A parallel briefs · polish/deliver readiness · Imagine bridge preview |

### TUI Home (v3.9.0)

| Key | Action |
|-----|--------|
| `1` / `2` / `3` | Compact / ops / full density |
| `Tab` | Cycle view modes |
| `p` | Pause auto-refresh |
| Type | Filter action lists (Launcher / Cockpit) |
| `d` `v` `s` `m` `k` | Doctor · validate · quota sync · models · stack |
| `c` | Cockpit (scaffold; dry-run polish/deliver) |
| `l` | Launcher |

Operator guide: [guides/OPERATOR_CONTROL_PLANE.md](guides/OPERATOR_CONTROL_PLANE.md).  
North-star design: `docs/development/superpowers/specs/2026-07-26-operator-ux-north-star-design.md`.

---

## 8. Agents & Skills

### Scale (v3.9.0)

| Metric | Count |
|--------|-------|
| **Skills runtime** | ~62 (full suite, including Wave A) |
| **Role-Card core agents** | 25+ |
| **Plugin packs** | Full suite + 5 satellites |

### Core leadership

| Specialist | Activation | Primary strength |
|------------|------------|------------------|
| Studio Director | `ACTIVATE STUDIO_DIRECTOR` | Orchestration & handoff decisions |
| Mega Production Architect | `ACTIVATE MEGA_PRODUCTION_ARCHITECT` | Production Bible + roadmap |
| Identity Lock Specialist | `ACTIVATE IDENTITY_LOCK` | DNA continuity & drift |
| Imagine Prompt Master | `ACTIVATE IMAGINE_PROMPT_MASTER` | Photoreal prompt engineering |
| Director of Photography | `ACTIVATE DOP` | Lighting & camera |
| Sequence Director | `ACTIVATE SEQUENCE_DIRECTOR` | Long-form sequencing |
| Cinematic Sequence Extender | `ACTIVATE SEQUENCE_EXTENDER` | 60–180s+ seamless expand |
| AI Polish Director | `ACTIVATE AI_POLISH_DIRECTOR` | Upscale / face restore |
| Quality Assurance Guardian | `ACTIVATE QA_GUARDIAN` | 16-point + chain QA |
| Workflow Quota Optimizer | `ACTIVATE WORKFLOW_OPTIMIZER` | Cost & budget |
| Sonic Architect | `ACTIVATE SONIC_ARCHITECT` | Native audio design |
| Parallel Brief Dispatcher | `ACTIVATE PARALLEL_BRIEF_DISPATCHER` | Concurrent specialist briefs (Wave A) |
| ErosForge NSFW Director | `ACTIVATE EROSFORGE` | Opt-in R-rated work |

### Presets (examples)

| Preset | Command |
|--------|---------|
| Full Studio | `Activate Grok Imagine Cinematic Studio v3.11.0` |
| 1.5 Native Video | `ACTIVATE IMAGINE_VIDEO_1.5_FULL` |
| Character Onboarding | `ACTIVATE CHARACTER_DNA_EXTRACTOR` + `ACTIVATE IDENTITY_LOCK` |
| Long-Form Sequence | `ACTIVATE SEQUENCE_DIRECTOR` + `ACTIVATE SEQUENCE_EXTENDER` |
| QA + Delivery | `RUN QA REVIEW` → `ACTIVATE AI_POLISH_DIRECTOR` |
| Marketing Package | `ACTIVATE KEY_ART_DESIGNER` + `ACTIVATE TRAILER_DIRECTOR` |
| Studio Health | `ACTIVATE GROK_DOCTOR` · `RUN STUDIO_HEALTH_CHECK` |

**Authoritative tables:** [`references/agents/AGENT_INDEX.md`](../references/agents/AGENT_INDEX.md)  
**Role Cards:** `references/agents/*.md`  
**Skills:** `.grok/skills/*/SKILL.md`

---

## 9. CLI Reference (Summary)

**Entry points**

- `cinematic-studio` (installed wrapper)
- `python tools/cinematic_studio_cli.py`
- `bash scripts/cinematic_studio.sh` (install / update / verify / doctor / grok)

```bash
cinematic-studio --help
cinematic-studio <command> --help
```

### Essential commands

```bash
# Grok Build binary
cinematic-studio grok status|ensure|update|install

# Production Bible
cinematic-studio create-bible --wizard
cinematic-studio create-bible "Project Title"

# DNA
cinematic-studio dna init --name "Name"
cinematic-studio dna lock|handoff|inject

# Sequences
cinematic-studio sequence init <name>
cinematic-studio sequence add-clip|handoff|extend-prompt|qa|color-grade|polish|deliver

# Imagine / handoff
cinematic-studio imagine agent-handoff --surface grok_build_tools --format json|markdown
cinematic-studio imagine bridge
cinematic-studio handoff validate <path>

# Quota
cinematic-studio quota estimate -d 45
cinematic-studio quota dashboard|optimize|sync

# Generation ledger
cinematic-studio generation log|list|summary|report|update

# Wave A multi-agent packets
cinematic-studio wave-a --help
cinematic-studio wave-a briefs
cinematic-studio wave-a validate

# Models & health
cinematic-studio models verify|stack
cinematic-studio validate
cinematic-studio handoff validate <path> --strict-handoff
cinematic-studio doctor [--quick]

# Plugins
cinematic-studio plugin catalog|packs
cinematic-studio plugin catalog pin
cinematic-studio plugin catalog check --release

# TUI
cinematic-studio ui

# NSFW (after ErosForge activation in chat)
cinematic-studio nsfw ...
```

### Common strict flags

| Flag | Purpose |
|------|---------|
| `--strict-handoff` | Full packet + specialist checklist |
| `--strict-plate` | Require plate lock |
| `--strict-motion` | Require motion vector / I2V readiness |
| `--strict-identity` | Hard-fail identity gate on extend path |
| `--strict-wave-a` | Enforce Wave A packet completeness |

**Full CLI manual:** [CLI_REFERENCE.md](CLI_REFERENCE.md).

---

## 10. Web UI & TUI

### Streamlit Web UI

```bash
streamlit run web_ui/app.py
```

Features: Guided Bible Creator · Character DNA Bank · Sequence dashboard · Imagine page · Quota estimator · Tools (handoff validate, bridge) · Settings · **Dashboard view modes** (compact / ops / full).

Cloud: [guides/streamlit_cloud_deploy.md](guides/streamlit_cloud_deploy.md).

### Terminal UI

```bash
cinematic-studio ui
# optional: python tools/cinematic_studio_cli.py ui --interval 5
```

Live studio dashboard, safe command launcher (no Imagine spend), production cockpit (Bible/DNA/sequence scaffold, validate, stack, dry-run polish/deliver). **v3.9.0:** density modes + list filter + pause refresh.

---

## 11. Plugin Packs

Defined in [`config/plugin_packs.yaml`](../config/plugin_packs.yaml).

| Pack | Plugin ID | Includes |
|------|-----------|----------|
| **Full Suite** (recommended) | `grok-imagine-cinematic-studio` | Entire skill + command tree |
| Core | `grok-imagine-cinematic-core` | Director, DNA, Imagine, QA, quota, meta |
| Camera & Image | `grok-imagine-camera-image` | DoP, i2i, key art, plate/motion, i2v |
| Sequence & Narrative | `grok-imagine-sequence-narrative` | Sequence, continuity, audio, action/VFX, SFW batch |
| NSFW (opt-in) | `grok-imagine-nsfw` | ErosForge, NSFW quota/extend/chain QA |
| Delivery & Post | `grok-imagine-delivery-post` | Assembly, color, polish, ffmpeg, distribution |

**Declutter policy:** `full_suite_wins` — installing the full suite takes precedence over satellites.

Contributor pin order:

1. Commit skill/command content  
2. `bash scripts/release_plugin_catalog.sh` (or `plugin catalog pin`)  
3. Commit only `.grok-plugin/`  
4. `bash scripts/verify_plugins.sh --release`

---

## 12. Models & Video Pipelines

| Layer | Preferred | Use |
|-------|-----------|-----|
| Stack default | `grok-4.6` | Production Bibles, multi-agent direction |
| 1M opt-in | `grok-4.3` | Very long context |
| Multi-agent / leader | `grok-v9-4p5-multi` | Studio Director full mode, synthesis |
| Specialist craft | `grok-v9-4p5-chat-expert` | DNA, prompts, QA, DoP, Sonic, ErosForge |
| Draft / routine | `grok-4-auto` | Fast iteration, animatic, standard tier |
| Video default | Imagine **1.0** | Most sequences (cost default); edit/extend |
| Video critical | Imagine **1.5 Native** | Native audio, physics, intimacy, r2v, 1080p |
| Image default | `grok-imagine-image` | Draft / volume stills |
| Image hero | **`grok-imagine-image-2.0`** | Quality Mode, Identity plates, Agent image tool |

Every Production Bible must lock **`model_stack` + `VIDEO_PIPELINE_SPEC`**. There is **no** `grok-imagine-video-2.0`.

Sources of truth:

- [`references/agents/IMAGINE_SURFACES.md`](../references/agents/IMAGINE_SURFACES.md)
- [`references/agents/MODEL_LAYER_v4.5.md`](../references/agents/MODEL_LAYER_v4.5.md)
- [`references/MODELS_v3.6.md`](../references/MODELS_v3.6.md)

```bash
cinematic-studio models verify
cinematic-studio models stack
```

> Pricing and model availability can change. Verify against official xAI docs and your account before production spend.

---

## 13. Protocols & Gates

| Protocol | Document |
|----------|----------|
| Imagine surfaces (1.0 / 1.5 / 2.0) | [`IMAGINE_SURFACES.md`](../references/agents/IMAGINE_SURFACES.md) |
| Imagine Agent Mode Handoff | [`IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md`](../references/agents/IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md) |
| Identity Continuity | [`IDENTITY_CONTINUITY_PROTOCOL_v3.8.md`](../references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md) |
| Parallel Brief Protocol | [`Parallel_Brief_Protocol.md`](../references/agents/Parallel_Brief_Protocol.md) |
| Stitch artifact lexicon | [`references/stitch_artifact_lexicon.md`](../references/stitch_artifact_lexicon.md) |

### Execution surfaces (handoff)

| Code | Meaning |
|------|---------|
| `grok_build_tools` | In-session tools (preferred) |
| `grok_agent_acp` | ACP / agent sessions |
| `grok_com_imagine` | Web UI paste (Classic Bridge); Quality Mode = Image 2.0 |
| `xai_api` | Live API jobs |
| `xai_responses_tool` | Responses API `image_generation` (Image 2.0 stills) |

### Readiness gates (CLI)

| Gate | Soft default | Strict flag |
|------|--------------|-------------|
| Handoff packet completeness | warn | `--strict-handoff` |
| Plate lock | warn | `--strict-plate` |
| Motion vector / I2V readiness | warn | `--strict-motion` |
| Identity continuity | warn | `--strict-identity` |
| Wave A packets | optional | `--strict-wave-a` |
| Spend preflight | advisory | spend-readiness tools |
| Delivery polish readiness | advisory | delivery-readiness tools |

Handoff `protocol_version` accepts **3.7.1–3.10.0**.

---

## 14. Wave A Multi-Agent Scaffold

Wave A (v3.8.8+) adds eight specialists for plate/motion readiness, micro-physics, hair/makeup, dialogue/ADR, score/temp music, titles, distribution crops, and parallel brief dispatch.

```bash
cinematic-studio wave-a --help
cinematic-studio wave-a plate-motion ...
cinematic-studio wave-a briefs
cinematic-studio wave-a validate
cinematic-studio wave-a attach   # attach Wave A packets to Imagine handoff
```

Packets live in `tools/wave_a_packets.py`. Design notes: Parallel Brief Protocol + Operator UX north-star specs under `docs/development/superpowers/`.

---

## 15. NSFW / R-Rated (Opt-in)

- **Never auto-activated.** Requires explicit `ACTIVATE EROSFORGE` (or equivalent consent).
- Agents: ErosForge NSFW Director · NSFW Sequence Extender · NSFW Quota Orchestrator · NSFW Chain QA.
- Pack: `grok-imagine-nsfw`.
- Prefer **Imagine Video 1.5** for authenticity.
- Templates: [templates/Kink_Specific_Cinematic_Template_Library.md](templates/Kink_Specific_Cinematic_Template_Library.md).
- You remain solely responsible for lawful, consensual, age-appropriate, and platform-compliant use. See [DISCLAIMER.md](../DISCLAIMER.md).

---

## 16. Repository Map

```text
Grok Imagine Cinematic Studio v3.11.0
├── .grok-plugin/              # Marketplace manifests + packs
├── .grok/skills/              # Skill runtime (64 SKILL.md trees)
├── references/agents/         # Role Cards, AGENT_INDEX, protocols, MODEL_LAYER
├── tools/                     # DNA, sequence, quota, imagine_bridge, doctor, CLI
│   ├── cinematic_studio_cli.py
│   └── cli/                   # Typer commands + TUI
├── web_ui/                    # Streamlit app + pages
├── config/plugin_packs.yaml   # Pack membership
├── commands/                  # Slash-command docs for plugins
├── examples/                  # Production Bibles & genre samples
├── docs/                      # This documentation tree
├── scripts/                   # Install, verify, release, wrappers
├── tests/                     # Pytest suite
├── MASTER_PROMPT.md           # Canonical chat activation prompt
├── VERSION                    # 3.10.0
└── README.md                  # Public front door
```

Runtime path helpers: `tools/studio_paths.py`. Layout notes: [REPOSITORY_LAYOUT.md](REPOSITORY_LAYOUT.md).

---

## 17. Examples & Templates

| Resource | Path |
|----------|------|
| Production Bible template | [templates/Project_Bible_Template.md](templates/Project_Bible_Template.md) |
| Example Bibles | [`examples/production_bibles/`](../examples/production_bibles/) |
| Genre samples | [`examples/`](../examples/) (sci-fi, thriller, drama, action, …) |
| NSFW cinematic templates | [templates/Kink_Specific_Cinematic_Template_Library.md](templates/Kink_Specific_Cinematic_Template_Library.md) |

---

## 18. Upgrading

```bash
grok plugin update grok-imagine-cinematic-studio
# or from a git checkout:
bash scripts/cinematic_studio.sh update

cinematic-studio models verify
cinematic-studio doctor --quick
```

Activation after upgrade:

```text
Activate Grok Imagine Cinematic Studio v3.11.0
```

**Migration notes:** [guides/UPGRADE_GUIDE.md](guides/UPGRADE_GUIDE.md)  
**Release notes:** [releases/RELEASE_NOTES_v3.11.0.md](releases/RELEASE_NOTES_v3.11.0.md)  
**Changelog:** [CHANGELOG.md](../CHANGELOG.md)

### v3.11.0 highlight

Official Imagine **Image 2.0** + Video **1.0 / 1.5** surface map (there is **no Video 2.0**). Hero stills / Quality Mode route to `grok-imagine-image-2.0`. Agent Mode surface **E** is `xai_responses_tool`. REST `imagine submit` covers `video_edit` / `video_extend` / `reference_to_video`. Canonical: [../references/agents/IMAGINE_SURFACES.md](../references/agents/IMAGINE_SURFACES.md).

### v3.9.0 highlight

TUI + Streamlit **view density modes** (compact / ops / full) on top of the v3.8.8 operator control plane and Wave A multi-agent scaffold.

---

## 19. Contributing

Contributions welcome: new Role Cards, prompt engineering, CLI/Web features, docs, examples, gates, and tests.

1. Read [CONTRIBUTING.md](../CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md).
2. For major architecture changes, open an issue first.
3. Keep skills free of per-skill READMEs; follow skill conventions in `cinematic-skill-creator`.
4. Plugin catalog changes must follow pin order (content → pin → verify).

---

## 20. License

**MIT License** — see [LICENSE](../LICENSE).

Software and documentation are provided **as is**, without warranty. Generated media requires your own QA before public or client delivery.

---

## 21. Document Index

| Document | Role |
|----------|------|
| **[OFFICIAL_DOCUMENTATION.md](OFFICIAL_DOCUMENTATION.md)** | This manual (canonical) |
| [OFFICIAL_OVERVIEW.md](OFFICIAL_OVERVIEW.md) | Short product overview |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture |
| [CLI_REFERENCE.md](CLI_REFERENCE.md) | CLI command reference |
| [guides/Quick_Start_Guide.md](guides/Quick_Start_Guide.md) | Onboarding + operator loop |
| [guides/USER_GUIDE.md](guides/USER_GUIDE.md) | Creator end-to-end guide (v3.11.0) |
| [guides/OPERATOR_CONTROL_PLANE.md](guides/OPERATOR_CONTROL_PLANE.md) | Orient → Health → Produce → Gate → Deliver |
| [guides/installation_guide.md](guides/installation_guide.md) | Install Method A / B |
| [guides/UPGRADE_GUIDE.md](guides/UPGRADE_GUIDE.md) | Version migration |
| [releases/](releases/) | Per-version release notes |
| [../README.md](../README.md) | Repository front door |
| [../MASTER_PROMPT.md](../MASTER_PROMPT.md) | Chat activation prompt |
| [../DISCLAIMER.md](../DISCLAIMER.md) | Independence & liability |
| [../references/agents/AGENT_INDEX.md](../references/agents/AGENT_INDEX.md) | Full agent activation index |

---

**Ready to direct your next production?**

```text
Activate Grok Imagine Cinematic Studio v3.11.0
```

---

*Grok Imagine Cinematic Studio v3.11.0 — Official Documentation · Independent community project · Not affiliated with xAI · MIT License*
