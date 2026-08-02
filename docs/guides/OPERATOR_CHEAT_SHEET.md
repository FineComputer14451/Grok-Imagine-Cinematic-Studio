# Operator Cheat Sheet — Grok Imagine Cinematic Studio v3.9.0

**One-pager for activation, agents, skills, packs, and CLI.**  
Community project — not affiliated with xAI. Canonical detail: `AGENTS.md` · `references/agents/AGENT_INDEX.md` · `references/SKILLS_TAXONOMY.md`.

| Stamp | Value |
|-------|--------|
| Studio | **v3.9.0** |
| Skills | **62** |
| Role-Card core agents | **25** |
| Wave A (P0) | **8** specialists |
| Marketplace | Full suite + 5 packs |
| Registry default | `grok-4.5` (+ specialist v9-4p5 / `grok-4-auto` when available) |
| Imagine | **1.0** default · **1.5** native audio / physics / intimacy |

---

## 60-second activate

```text
Activate Grok Imagine Cinematic Studio v3.9.0
```

| Surface | How |
|---------|-----|
| Grok Build / plugin | `/cinematic` |
| grok.com chat | Activate phrase (or paste `MASTER_PROMPT.md`) |
| Shell CLI | `cinematic-studio …` / `python tools/cinematic_studio_cli.py …` |
| TUI | `cinematic-studio ui` · `ui --print` |
| Streamlit | `streamlit run web_ui/app.py` |
| NiceGUI | `cinematic-studio web --port 8088` |
| FastAPI | `cinematic-studio api --port 8090` |

**Rule:** activate by **skill slug** (kebab-case), not display title.

---

## Model stack (lock every Bible)

| Layer | Slug | When |
|-------|------|------|
| Orchestration / Build | `grok-4.5` | Bibles, multi-agent direction, CLI |
| Multi-agent specialist | `grok-v9-4p5-multi` | Handoffs, sequences, synthesis |
| Craft specialist | `grok-v9-4p5-chat-expert` | DNA, prompts, QA, DoP, Sonic |
| Draft / quota | `grok-4-auto` | Animatic, routine routing |
| 1M context (opt-in) | `grok-4.3` | Memory banks only |
| Video | `grok-imagine-video` / `…-1.5` | 1.0 cost default · 1.5 audio |
| Image | `grok-imagine-image` | Stills / plates |

```bash
python tools/cinematic_studio_cli.py models verify
```

Every Production Bible locks `model_stack` + `VIDEO_PIPELINE_SPEC`.

---

## Slash commands (11)

| Command | Purpose |
|---------|---------|
| `/cinematic` | Full studio activate v3.9.0 |
| `/dna` | Character DNA extract / lock / inject |
| `/imagine` | Preflight → plan → generate → QA / bridge |
| `/dashboard` | Health, quota, sequences, DNA |
| `/validate` | Skills, models, project health |
| `/quota` | Cost estimate & risk |
| `/intelligence` | Regions, aspect, quota sync |
| `/automation` | Batch / artifact / reports |
| `/sfw` | SFW multi-shot batches |
| `/nsfw` | **Opt-in** ErosForge path |
| `/delivery` | Polish → EDL → deliver |

---

## 25 Role-Card core agents

Display name → **skill slug** → primary activation.

| # | Display name | Skill slug | Activate |
|---|--------------|------------|----------|
| 1 | Studio Director | `studio-director` | `ACTIVATE STUDIO DIRECTOR` · `ACTIVATE IMAGINE_AGENT_MODE_HANDOFF` |
| 2 | Mega Production Architect | `mega-production-architect` | `ACTIVATE MEGA_PRODUCTION_ARCHITECT` |
| 3 | Director of Photography | `director-of-photography` | `ACTIVATE DOP` |
| 4 | Production Designer | `production-designer-set-decorator` | `ACTIVATE PRODUCTION_DESIGNER` |
| 5 | Color Grading Supervisor | `post-production-color-grading-supervisor` | `ACTIVATE COLOR_GRADING` |
| 6 | Performance & Emotion Director | `performance-emotion-director` | `ACTIVATE PERFORMANCE_EMOTION` |
| 7 | Identity Lock Specialist | `identity-lock-specialist` | `ACTIVATE IDENTITY_LOCK` |
| 8 | Narrative Arc Pacing Strategist | `narrative-arc-pacing-strategist` | `ACTIVATE NARRATIVE_ARC` |
| 9 | Sequence Director | `sequence-director` | `ACTIVATE SEQUENCE_DIRECTOR` |
| 10 | Cinematic Sequence Extender | `cinematic-sequence-extender` | `ACTIVATE SEQUENCE_EXTENDER` |
| 11 | Continuity Guardian | `continuity-consistency-guardian` | `ACTIVATE CONTINUITY_GUARDIAN` |
| 12 | Multi-Clip Continuity Orchestrator | `multi-clip-continuity-orchestrator` | `ACTIVATE MULTI_CLIP_CONTINUITY_ORCHESTRATOR` |
| 13 | Imagine Prompt Master | `imagine-prompt-master` | `ACTIVATE IMAGINE_PROMPT_MASTER` |
| 14 | Quality Assurance Guardian | `quality-assurance-guardian` | `ACTIVATE QA_GUARDIAN` · `RUN QA REVIEW` |
| 15 | Grok Doctor | `grok-doctor` | `ACTIVATE GROK_DOCTOR` · `RUN STUDIO_HEALTH_CHECK` |
| 16 | Workflow Quota Optimizer | `workflow-quota-optimizer` | `ACTIVATE WORKFLOW_OPTIMIZER` |
| 17 | Sonic Architect | `sonic-architect-native-audio-virtuoso` | `ACTIVATE SONIC_ARCHITECT` |
| 18 | Foley Specialist | `foley-sound-design-specialist` | `ACTIVATE FOLEY_SPECIALIST` |
| 19 | Stunt Action Choreographer | `stunt-action-choreographer` | `ACTIVATE STUNT_CHOREOGRAPHER` |
| 20 | VFX & SFX Supervisor | `vfx-sfx-supervisor` | `ACTIVATE VFX_SFX_SUPERVISOR` |
| 21 | Key Art Designer | `key-art-poster-designer` | `ACTIVATE KEY_ART_DESIGNER` |
| 22 | Trailer Director | `trailer-teaser-director` | `ACTIVATE TRAILER_DIRECTOR` |
| 23 | Localization Specialist | `localization-subtitle-specialist` | `ACTIVATE LOCALIZATION_SPECIALIST` |
| 24 | AI Polish Director | `ai-polish-director` | `ACTIVATE AI_POLISH_DIRECTOR` · `RUN FINAL POLISH PASS` |
| 25 | ErosForge NSFW Director | `erosforge-nsfw-director` | `ACTIVATE EROSFORGE` (**explicit opt-in only**) |

Role Cards: `references/agents/`. Index: `references/agents/AGENT_INDEX.md`.

---

## Wave A specialists (8 · P0 scaffold)

| Skill slug | Activate |
|------------|----------|
| `plate-motion-readiness-lead` | `ACTIVATE PLATE_MOTION_READINESS` · `LOCK PLATES` |
| `contact-micro-physics-specialist` | `ACTIVATE CONTACT_MICRO_PHYSICS` |
| `hair-makeup-continuity` | `ACTIVATE HAIR_MAKEUP_CONTINUITY` · `LOCK HMU` |
| `dialogue-adr-director` | `ACTIVATE DIALOGUE_ADR` |
| `score-temp-music-supervisor` | `ACTIVATE SCORE_TEMP_MUSIC` |
| `title-motion-graphics-lead` | `ACTIVATE TITLE_MOTION_GRAPHICS` |
| `distribution-crop-strategist` | `ACTIVATE DISTRIBUTION_CROP` |
| `parallel-brief-dispatcher` | `ACTIVATE PARALLEL_BRIEF_DISPATCHER` |

---

## Pipeline specialists (high traffic · not all in the “25”)

| Skill slug | Role |
|------------|------|
| `character-dna-extractor` | DNA from refs → Identity Lock handoff |
| `costume-wardrobe-continuity` | Wardrobe lock / inject |
| `multi-character-identity-arbiter` | Multi-cast DNA arbitration |
| `reference-asset-curator` | Hero/standard/draft tiers + model routing |
| `image-to-video-specialist` | i2v motion briefs on locked plates |
| `imagine-execution-bridge` | grok.com/imagine copy-paste packets |
| `handoff-packet-validator` | Validate handoff JSON before spend |
| `chain-qa-protocol` | 10-point extend/stitch gate |
| `nsfw-chain-qa-protocol` | NSFW chain gate (opt-in) |
| `sfw-batch-orchestrator` | SFW multi-shot under quota |
| `nsfw-quota-orchestrator` | NSFW batch economy (opt-in) |
| `nsfw-sequence-extender` | NSFW extend chains (opt-in) |
| `animatic-director` | Low-cost previs before video spend |
| `arc-replan-copilot` | Mid-sequence replan after No-Go |
| `assembly-editor` | Rough-cut EDL after QA |
| `ai-video-upscaler` | Local upscale / face restore |
| `cinematic-ffmpeg` | Concat / social crops |
| `i2i-cinematic-refiner` / `i2i-refiner` | Still refinement |
| `ai-image-recreation` | Upload restyle / recreation |
| `production-bible-workflow` | Guided Bible / DNA / sequence onboarding |
| `cinematic-skill-creator` | New studio skills |
| `cinematic-studio-meta-installer` | Install / update / declutter |
| `skill-agent-architect` | Custom agents / Role Cards |
| `github-repo-manager` | GitHub lifecycle |
| `quota-dashboard` | Visual quota reports |
| `extend-frame-to-video` | Still-sequence animatic / FFmpeg |
| `director-of-photography-v3-3` | Legacy DoP (prefer primary DoP) |
| `grok-imagine-cinematic-studio` | Full suite entry skill |

---

## All 62 skills by marketplace pack

Union of packs = full suite. Prefer **full suite** install.

### `core` (21) — `grok-imagine-cinematic-core`

`grok-imagine-cinematic-studio` · `studio-director` · `mega-production-architect` · `production-bible-workflow` · `cinematic-studio-meta-installer` · `skill-agent-architect` · `github-repo-manager` · `character-dna-extractor` · `identity-lock-specialist` · `multi-character-identity-arbiter` · `costume-wardrobe-continuity` · `imagine-prompt-master` · `imagine-execution-bridge` · `handoff-packet-validator` · `workflow-quota-optimizer` · `quota-dashboard` · `quality-assurance-guardian` · `chain-qa-protocol` · `cinematic-skill-creator` · `grok-doctor` · `parallel-brief-dispatcher`

Commands: `cinematic` · `dna` · `imagine` · `dashboard` · `validate` · `quota` · `intelligence` · `automation` · `sfw`

### `camera-image` (11) — requires core

`director-of-photography` · `director-of-photography-v3-3` · `production-designer-set-decorator` · `i2i-cinematic-refiner` · `i2i-refiner` · `ai-image-recreation` · `key-art-poster-designer` · `reference-asset-curator` · `image-to-video-specialist` · `plate-motion-readiness-lead` · `contact-micro-physics-specialist`

### `sequence-narrative` (19) — requires core

`sequence-director` · `cinematic-sequence-extender` · `extend-frame-to-video` · `narrative-arc-pacing-strategist` · `arc-replan-copilot` · `animatic-director` · `continuity-consistency-guardian` · `multi-clip-continuity-orchestrator` · `performance-emotion-director` · `trailer-teaser-director` · `sonic-architect-native-audio-virtuoso` · `foley-sound-design-specialist` · `localization-subtitle-specialist` · `stunt-action-choreographer` · `vfx-sfx-supervisor` · `sfw-batch-orchestrator` · `hair-makeup-continuity` · `dialogue-adr-director` · `score-temp-music-supervisor`

### `nsfw` (4) — requires core · **opt-in only**

`erosforge-nsfw-director` · `nsfw-quota-orchestrator` · `nsfw-sequence-extender` · `nsfw-chain-qa-protocol`  
Command: `nsfw`

### `delivery-post` (7) — requires core

`assembly-editor` · `post-production-color-grading-supervisor` · `ai-polish-director` · `ai-video-upscaler` · `cinematic-ffmpeg` · `title-motion-graphics-lead` · `distribution-crop-strategist`  
Command: `delivery`

```bash
python tools/cinematic_studio_cli.py plugin packs
# 21 + 11 + 19 + 4 + 7 = 62
```

---

## Production order of operations

```text
Activate studio
  → Production Bible (model_stack + VIDEO_PIPELINE_SPEC)
  → Character DNA + Identity Lock (+ wardrobe / HMU)
  → Animatic (optional, low cost)
  → Reference Curator tiers
  → Plate + Motion readiness (LOCK PLATES)
  → i2i polish if needed
  → I2V Specialist → generate
  → QA / Chain QA
  → Extend / stitch (LAST_FRAME + MOMENTUM + audio)
  → Assembly EDL → Color → AI Polish → ffmpeg deliver
```

**Before video spend:** locked plates + motion briefs (`--strict-plate` / `--strict-motion` when enforcing).  
**Identity Continuity:** `references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md` on multi-clip character work.  
**Handoff packet:** validate before extend / Imagine Agent Mode (`handoff-packet-validator`).

---

## Activation presets (copy-paste)

| Intent | Phrase |
|--------|--------|
| Full studio | `Activate Grok Imagine Cinematic Studio v3.9.0` |
| 1.5 native | `ACTIVATE IMAGINE_VIDEO_1.5_FULL` |
| Long-form | `ACTIVATE SEQUENCE_DIRECTOR` + `ACTIVATE SEQUENCE_EXTENDER` |
| Character onboard | `ACTIVATE CHARACTER_DNA_EXTRACTOR` + `ACTIVATE IDENTITY_LOCK` |
| Plate → video | `ACTIVATE PLATE_MOTION_READINESS` → `ACTIVATE I2V_SPECIALIST` |
| QA + polish | `RUN QA REVIEW` → `ACTIVATE AI_POLISH_DIRECTOR` |
| Health | `ACTIVATE GROK_DOCTOR` · `RUN STUDIO_HEALTH_CHECK` |
| SFW batch | `ACTIVATE SFW_BATCH_ORCHESTRATOR` |
| NSFW (opt-in) | `ACTIVATE EROSFORGE` → quota / extender as needed |
| Parallel briefs | `ACTIVATE PARALLEL_BRIEF_DISPATCHER` |

---

## CLI quick reference

```bash
# Health
cinematic-studio doctor
cinematic-studio models verify
cinematic-studio plugin status
cinematic-studio plugin catalog check --release

# Bible / DNA / sequence
cinematic-studio create-bible "Title" --genre Sci-Fi
cinematic-studio create-bible --wizard
cinematic-studio dna --help
cinematic-studio sequence --help
cinematic-studio sequence health "Act 1" --json

# Imagine
cinematic-studio imagine verify
cinematic-studio imagine bridge --help
cinematic-studio sfw plan "Session" --shot "hero:Cover" --budget 300
cinematic-studio quota estimate --duration 60

# Surfaces smoke
python scripts/smoke_studio_surfaces.py
```

Install:

```bash
# Method A
bash scripts/cinematic_studio.sh install

# Method B (full suite recommended)
grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio --trust
```

---

## Canonical paths

| What | Path |
|------|------|
| Agent instructions | `AGENTS.md` |
| Agent index | `references/agents/AGENT_INDEX.md` |
| Model layer | `references/agents/MODEL_LAYER_v4.5.md` |
| Skills taxonomy | `references/SKILLS_TAXONOMY.md` |
| Skill tree | `.grok/skills/<slug>/SKILL.md` |
| Skill manifest | `scripts/required_skills.manifest` |
| Plugin packs | `config/plugin_packs.yaml` |
| Marketplace | `.grok-plugin/` |
| Generated outputs | `artifacts/` (this file) |

---

*Operator cheat sheet · studio **v3.9.0** · 25 core · Wave A 8 · **62 skills** · multi-surface control plane*  
*Regenerate after roster/pack changes: update from AGENT_INDEX + plugin_packs.yaml + required_skills.manifest.*
