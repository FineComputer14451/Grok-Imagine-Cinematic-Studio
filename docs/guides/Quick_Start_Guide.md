# Grok Imagine Cinematic Studio v3.11.0 — Quick Start Guide

**Version:** 3.10.0 | **Last Updated:** August 22, 2026  
**Suite:** 25+ Role-Card core agents · **64 skills** · marketplace full suite + 5 packs

> [!NOTE]
> **Grok Imagine Cinematic Studio** is an **independent community project**. It is **not affiliated with, endorsed by, sponsored by, or officially connected to xAI**. Grok / Imagine access, quotas, and billing remain solely with your xAI (or host) account. Full notice: [DISCLAIMER.md](../../DISCLAIMER.md).

---

## 0. Model Stack (Unified Grok 4.6 cinematic+Build · optional 4.3 1M · Imagine)

| Where | Model | Purpose |
|-------|-------|---------|
| Grok chat / API (cinematic) | `grok-4.6` | Production Bibles, multi-agent direction (default); `grok-4.3` for **1M** opt-in |
| Grok Build CLI (default) | `grok-4.6` | Coding, agentic sessions (min CLI **1.0.5**) |
| Grok Build fork | `grok-build` | Code, skills, repo tooling |
| Specialist routing (when available) | `grok-v9-4p5-multi` · `grok-v9-4p5-chat-expert` · `grok-4-auto` | Multi-agent / craft / draft — see `references/agents/MODEL_LAYER_v4.5.md` |
| Imagine Video | `grok-imagine-video` (1.0) / `1.5` | $0.05/sec default; 1.5 native audio $0.08/sec |
| Imagine Image | `grok-imagine-image` | Reference stills |

Every studio skill locks **Stack default** `grok-4.6` (opt-in 1M: `grok-4.3`) plus a specialist `preferred_model`.

Verify compatibility: `cinematic-studio models verify` (or `python tools/cinematic_studio_cli.py models verify`)  
Full reference: `references/MODELS_v3.6.md` · Model Layer: `references/agents/MODEL_LAYER_v4.5.md`

Grok Build config (`~/.grok/config.toml`):
```toml
[models]
default = "grok-4.6"

[ui]
fork_secondary_model = "grok-build"
```

Check CLI version: `grok --version` (recommend ≥ 1.0.5).

---

## 1. Getting Started

### Where you run (surfaces)

| Surface | What works |
|---------|------------|
| **[grok.com](https://grok.com) chat** | Activate phrase / paste `MASTER_PROMPT.md` — no `grok` binary |
| **[grok.com/imagine](https://grok.com/imagine)** | Paste Execution Bridge packets (`cinematic-studio imagine bridge` from shell) |
| **Grok mobile app** | Same as chat + in-app Imagine |
| **Desktop / Android shell** | Full Method A + `cinematic-studio grok` + Grok Build CLI |
| **Streamlit Web UI** | `streamlit run web_ui/app.py` — live batch, DNA bank, NSFW planners (see [WEB_SHELLS.md](WEB_SHELLS.md)) |
| **NiceGUI Web shell** | `cinematic-studio web` — ActionSpec pages on `studio_core` (optional) |
| **React SPA** | `cinematic-studio api` + `cinematic-studio web-react` — TanStack cockpit + guided Bible (optional) |
| **Textual TUI** | `cinematic-studio ui` — terminal dashboard + launcher + cockpit |

### Activate the Full Studio (Recommended)

**On grok.com or mobile chat** — new conversation:

```
Activate Grok Imagine Cinematic Studio v3.11.0
```

or

```
start cinematic production
```

For a full lock-in on the web, paste `MASTER_PROMPT.md` first, then Activate.

This loads the complete **v3.11.0** system: unified Grok 4.6 cinematic+Build stack (optional 4.3 1M), dual Imagine Video 1.0/1.5, guided Bible wizard, Imagine Agent Mode Handoff, Identity Continuity, and the **64-skill** suite.

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
| **Costume & Wardrobe Continuity**       | `ACTIVATE COSTUME_WARDROBE`         | Outfit DNA lock & clothing continuity         |
| **Imagine Prompt Master**               | `ACTIVATE IMAGINE_PROMPT_MASTER`    | High-quality prompt engineering (1.5 native)  |
| **Director of Photography (DoP)**       | `ACTIVATE DOP`                      | Lighting, camera, visual language             |
| **Performance & Emotion Director**      | `ACTIVATE PERFORMANCE_EMOTION`      | Micro-expressions & emotional acting          |
| **Sequence Director**                   | `ACTIVATE SEQUENCE_DIRECTOR`        | Long-form sequencing & 1.5 chaining           |
| **Cinematic Sequence Extender**         | `ACTIVATE SEQUENCE_EXTENDER`        | Long-form sequence expansion (60–180s+)       |
| **Continuity & Consistency Guardian**   | `ACTIVATE CONTINUITY_GUARDIAN`      | Timeline & prop consistency                   |
| **Quality Assurance Guardian**          | `ACTIVATE QA_GUARDIAN`              | Final 16-point QA review                      |
| **ErosForge NSFW Director**             | `ACTIVATE EROSFORGE`                | Artistic R-rated / erotic scenes (explicit)   |
| **Key Art & Poster Designer**           | `ACTIVATE KEY_ART_DESIGNER`         | Posters, thumbnails, marketing visuals        |
| **Trailer & Teaser Director**           | `ACTIVATE TRAILER_DIRECTOR`         | Trailers, teasers, highlight reels            |
| **Production Designer**                 | `ACTIVATE PRODUCTION_DESIGNER`      | Environments, props, world-building           |
| **Sonic Architect**                     | `ACTIVATE SONIC_ARCHITECT`          | Native audio & sound design                   |
| **Foley Sound Design Specialist**       | `ACTIVATE FOLEY_SPECIALIST`         | Realistic foley & hard effects                |
| **Stunt & Action Choreographer**        | `ACTIVATE STUNT_CHOREOGRAPHER`      | Fights, chases, stunts                        |
| **VFX & SFX Supervisor**                | `ACTIVATE VFX_SFX_SUPERVISOR`       | Creatures, destruction, particles             |
| **Workflow & Quota Optimizer**          | `ACTIVATE WORKFLOW_OPTIMIZER`       | Real-time quota & efficiency management       |
| **AI Polish Director**                  | `ACTIVATE AI_POLISH_DIRECTOR`       | Final upscale / face restore after QA         |
| **Imagine Agent Mode Handoff**          | `ACTIVATE IMAGINE_AGENT_MODE_HANDOFF` | Planning → generation handoff               |

**Tip:** You can also use natural language, for example:
- "Create key art for this scene"
- "Make a cinematic trailer from this sequence"
- "Choreograph this fight scene with emotional weight"

Full activation table: `references/agents/AGENT_INDEX.md`

---

## 3. Recommended Production Workflow (v3.11.0)

### Phase 1: Activation & Planning
1. **Activate the Full Studio**  
   `Activate Grok Imagine Cinematic Studio v3.11.0`

2. **Start a New Project**  
   Provide title, logline, genre, tone, target length, and key characters.

3. **Generate & Lock the Production Bible**  
   Include `model_stack` + `VIDEO_PIPELINE_SPEC` (1.0 default or 1.5 for native audio).  
   CLI: `create-bible "Title"` or `create-bible --wizard` (guided TTY stages).  
   Web UI: Production → Export Bible or **Guided Bible Creator**.

### Phase 2: Pre-Production
4. **Generate Reference Materials** (Recommended)  
   Request character references, environment concepts, or mood boards early.

5. **Activate Key Specialists Early**  
   - `ACTIVATE IDENTITY_LOCK` for recurring characters  
   - `ACTIVATE COSTUME_WARDROBE` when outfits must survive stills → i2v → extend  
   - `ACTIVATE PRODUCTION_DESIGNER` for world-building  
   - `ACTIVATE DOP` for visual language

### Phase 3: Production
6. **Execute Scenes / Sequences**  
   - Single scenes: Describe clearly  
   - Long sequences: Use `ACTIVATE SEQUENCE_DIRECTOR` + `ACTIVATE SEQUENCE_EXTENDER`  
   - Before video spend: lock plates + motion briefs (CLI: `--strict-plate`, `--strict-motion`, `--strict-handoff` when enforcing)

7. **Collaborate Mid-Production**  
   Activate specialists as needed (Stunts, VFX, Sound, etc.).

### Phase 4: Review & Polish
8. **Run QA Review**  
   `RUN QA REVIEW` or let the Quality Assurance Guardian evaluate outputs.  
   Long-form: Identity Continuity (`references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md`) + Chain QA.

9. **Final Delivery Polish** (after QA Go)  
   `ACTIVATE AI_POLISH_DIRECTOR` or `RUN FINAL POLISH PASS` — upscales 720p clips with optional face restoration via `ai-video-upscaler`.

10. **Request Director’s Cut** (if needed)  
    `GENERATE DIRECTOR'S CUT`

### Phase 5: Delivery
11. **Generate Marketing Assets**  
    `ACTIVATE KEY_ART_DESIGNER` + `ACTIVATE TRAILER_DIRECTOR`

12. **Localize** (if needed)  
    `ACTIVATE LOCALIZATION_SPECIALIST`

---

**Pro Tip:** You can combine steps in one message:  
> `"Activate Grok Imagine Cinematic Studio v3.11.0, start new project called 'Neon Eclipse Heist', generate the full Production Bible with VIDEO_PIPELINE_SPEC for 1.5, and create the first sequence."`

---

## 4. Operator loop (Orient + Health)

Before long generations, run the **control plane** loop (same signals on TUI Home and Streamlit Dashboard):

1. **Orient** — Open `cinematic-studio ui` or `streamlit run web_ui/app.py` → Dashboard. Read the status strip severity (**OK / WARN / CRITICAL**) and the **Attention** list.
2. **Act (safe health only)**  
   - TUI: **d** doctor · **v** validate · **s** quota sync · **m** models · **k** stack  
   - Web: Dashboard **Health actions** (Doctor / Validate / Quota sync / Models verify)  
   - CLI: `cinematic-studio doctor --quick` · `validate` · `quota sync` · `models verify`
3. **Refresh** — TUI auto-refreshes Home; Web use **Refresh snapshot**. Re-check Attention until clear or accepted risk.
4. **Produce** — Then Bible / DNA / sequences / Imagine (spend stays on CLI or Web Imagine pages, not TUI).
5. **Gate (Phase 2)** — Check Dashboard **READINESS** (identity · chain QA · plate/motion). On No-Go: fix → re-QA before extend. After DNA lock / sequence handoff: `cinematic-studio handoff validate <path>` (TUI Launcher/Cockpit or Web Tools).
6. **Converge & deliver (Phase 3)** — Dashboard **Convergence** checklist before agent-mode handoff; **Parallel Brief** logs (`wave-a briefs`); **Delivery** polish/deliver readiness; preview bridge via `imagine bridge` or Web Tools (paste to grok.com/imagine). TUI Cockpit: polish/deliver **--dry-run** only.

Full guide: [OPERATOR_CONTROL_PLANE.md](OPERATOR_CONTROL_PLANE.md).  
North-star: `docs/development/superpowers/specs/2026-07-26-operator-ux-north-star-design.md` (Phases 1–3).

---

## 5. Pro Tips for Best Results (v3.11.0)

- **Be specific** — Include genre, tone, emotional goals, character details, and references.
- **Use the Project Bible** — Lock `model_stack` + `VIDEO_PIPELINE_SPEC` (1.0 cost default; 1.5 when audio/physics need it).
- **Activate specialists early** when you need focused work (trailers, key art, stunts, etc.).
- **Let agents collaborate** — Full studio mode automatically coordinates between specialists.
- **Identity before extend** — DNA → Identity Lock → drift evidence before long chains.
- **Monitor quota** — Workflow Quota Optimizer + `/quota` / `/dashboard` when on Method B.
- **Reference Role Cards** — `references/agents/` is authoritative for each agent.
- **Health check** — `grok-doctor` or `cinematic-studio doctor` after install/update.
- **Plugin catalog (contributors)** — Content commit → pin → catalog-only commit (see below).

---

## 6. Quick Reference Commands

| Command                                           | Result                                      |
|---------------------------------------------------|---------------------------------------------|
| `Activate Grok Imagine Cinematic Studio v3.11.0`   | Load full v3.11.0 studio (Grok 4.6 + 1.0/1.5) |
| `create-bible --wizard`                           | Guided Production Bible (TTY interactive)   |
| `Start new project`                               | Begin fresh production                      |
| `GENERATE DIRECTOR'S CUT`                         | Refined version with notes                  |
| `SHOW STUDIO DASHBOARD`                           | Current project status                      |
| `RUN QA REVIEW`                                   | Full 16-point quality check                 |
| `ACTIVATE EROSFORGE`                              | Enable NSFW specialist mode (explicit)      |
| `Exit cinematic studio`                           | Leave studio mode                           |
| `cinematic-studio plugin catalog pin`             | Regenerate + pin the Grok plugin catalog    |
| `cinematic-studio plugin catalog check --release` | Pre-publish catalog gate                    |
| `bash scripts/verify_plugins.sh --release`        | Manifest + release pin (from a **git clone**) |

### Contributor: plugin catalog pin (correct order)

1. Commit skill/command/content changes first  
2. From a **git clone** of this repo:  
   `bash scripts/release_plugin_catalog.sh`  
   (or `python3 -m tools.cinematic_studio_cli plugin catalog pin`)  
3. Commit **only** `.grok-plugin/` (pin-only tip; install SHA = content revision)  
4. Gate: `bash scripts/verify_plugins.sh --release` or `plugin catalog check --release`

**Why the scripts?** PATH `cinematic-studio` often points at `~/Grok-Cinematic-Projects` (install tree, not always a git repo). Repo scripts prefer the in-repo CLI so pin/check resolve **this** checkout’s `HEAD`.

### Automated re-pin on `main`

After content merges to `main`, GitHub Actions workflow **Auto re-pin plugin catalog** (`.github/workflows/auto-repin-plugin-catalog.yml`) runs `plugin catalog check --release`. If the pin is stale it:

1. Runs `plugin catalog pin` against that clone’s `HEAD`
2. Commits **only** `.grok-plugin/**` with message `chore(plugins): re-pin catalog to HEAD [auto-pin]`
3. Dispatches the main CI workflow on the new tip (token pushes do not auto-retrigger Actions)

You can also run it manually: **Actions → Auto re-pin plugin catalog → Run workflow**. Local contributors should still pin before release tags; the bot is a safety net so docs/asset commits do not leave `main` red.

---

## 7. Available Supporting Resources

| Resource                        | Location                              | Purpose                                           |
|---------------------------------|---------------------------------------|---------------------------------------------------|
| **Role Cards (Authoritative)**  | `references/agents/`                  | Personality, protocols, Model Layer               |
| **Agent Index**                 | `references/agents/AGENT_INDEX.md`    | Activation table for all agents                   |
| **Model Layer v4.5**            | `references/agents/MODEL_LAYER_v4.5.md` | Specialist + stack routing                      |
| **Identity Continuity**         | `references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md` | Long-form drift gates            |
| **Skills taxonomy / packs**     | `references/SKILLS_TAXONOMY.md`       | Groups, packs, declutter rules                    |
| **Master Prompt**               | `MASTER_PROMPT.md`                    | Complete master prompt for new chats              |
| **Skill Files**                 | `.grok/skills/`                       | 64-skill suite (agent-only; no README in skill dirs) |
| **Production Bible Template**   | `docs/templates/Project_Bible_Template.md` | Professional Bible template                  |
| **Install guide**               | `docs/guides/installation_guide.md`   | Method A / B + packs                              |
| **CLI Toolkit**                 | `cinematic-studio` / `tools/cinematic_studio_cli.py` | Bible, DNA, sequence, catalog, doctor    |
| **Web UI**                      | `web_ui/app.py`                       | Streamlit dashboard                               |

---

**You are now ready to create professional cinematic productions with Grok 4.5 orchestration + Imagine Video 1.0/1.5 support.**

Just say **"Activate Grok Imagine Cinematic Studio v3.11.0"** and begin.

---

*Grok Imagine Cinematic Studio v3.11.0 — Grok 4.6 / Model Layer v4.5 · 64 skills · August 2026*
