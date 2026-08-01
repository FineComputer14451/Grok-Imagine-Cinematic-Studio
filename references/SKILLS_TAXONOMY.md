# Skills & Plugin Taxonomy — v3.9.0

Canonical **install layout** stays flat: `.grok/skills/<name>/SKILL.md` (required by Grok plugin format). This file is the **mental model** for browsing, declutter, and docs — not a second on-disk hierarchy.

## Canonical suite headcounts (v3.8.9)

Single source of truth for marketing and verify gates:

| Metric | Count | Source |
|--------|------:|--------|
| **Skills (full suite)** | **62** | `.grok/skills/*/SKILL.md` ≡ `scripts/required_skills.manifest` ≡ `.grok-plugin/plugin.json` |
| **Slash commands** | **11** | `commands/` ≡ `plugin.json` `commands` |
| **Role-Card core agents** | **25** | `AGENTS.md` core table · `tools/cli/shared.py` `core_agent_count()` |
| **Role cards (mapped)** | **44** | `AGENT_ROLE_CARDS` (core + pipeline + Wave A + i2i + NSFW) |
| **Marketplace plugins** | **6** | full suite + 5 packs (`config/plugin_packs.yaml`) |
| **Pack sizes** | 21 · 11 · 19 · 4 · 7 | core · camera-image · sequence-narrative · nsfw · delivery-post (exclusive; union = 62) |

Do **not** invent skill counts in docs. After adding/removing a skill: update the manifest, regenerate the plugin catalog, and re-check this table.

## Install surfaces (do not dual-load studio skills)

| Surface | Path | What belongs here |
|---------|------|-------------------|
| **Plugin (Method B)** | `~/.grok/installed-plugins/grok-imagine-cinematic-studio-*/` | All **62** studio skills + slash commands (full suite; Wave A P0) |
| **Plugin packs (satellites)** | `~/.grok/installed-plugins/grok-imagine-*-*/` | Filtered pack views of the same skill tree (see Marketplace packs) |
| **User-global skills** | `~/.grok/skills/` | Non-plugin skills only (`help`, `create-skill`, `docx`, `imagine`, …) |
| **Repo / workspace** | `<clone>/.grok/skills/` | Authoritative source for development |
| **Method A projects** | `~/Grok-Cinematic-Projects/` | CLI tools, references, config — **not** a second skill tree when plugin is primary |

**Rule:** If the plugin is installed, do **not** also keep Method A copies of the same 62 skills under `~/.grok/skills/`. That triple-loads skills in Grok Build (workspace + plugin + user).

Declutter:

```bash
bash scripts/cinematic_studio.sh declutter --dry-run
bash scripts/cinematic_studio.sh declutter --apply --keep-backups 1
# or: python tools/cinematic_studio_cli.py plugin declutter --apply
```

When full suite + satellite packs are both present, policy **`full_suite_wins`** keeps the full suite and removes satellite skill duplicates.

## Marketplace

Single marketplace source for this product (multi-plugin catalog):

- **Source name:** `Grok-Imagine-Cinematic-Studio` (git URL of this repo)
- **Full suite (recommended):** `grok-imagine-cinematic-studio`
- **Catalog:** `.grok-plugin/marketplace.json` + root `plugin.json` + `plugin-index.json` + pack manifests under `.grok-plugin/packs/`

Pin protocol: github-repo-manager / `plugin catalog pin` (content commit → pin → catalog-only commit).

## Marketplace packs (v3.8.0+)

Pack definitions and declutter policy live in **`config/plugin_packs.yaml`**. Catalog generation emits **6 marketplace plugins** (1 full suite + 5 satellites) that share one git SHA. Skills remain exclusive across packs (validated at generate time).

| Pack id | Plugin name | Role |
|---------|-------------|------|
| *(full)* | `grok-imagine-cinematic-studio` | Recommended — all 62 skills + commands |
| `core` | `grok-imagine-cinematic-core` | Orchestration, DNA, Imagine runtime, QA, quota, meta |
| `camera-image` | `grok-imagine-camera-image` | DoP, production design, i2i, key art, i2v (requires `core`) |
| `sequence-narrative` | `grok-imagine-sequence-narrative` | Sequence, continuity, performance, audio, action/VFX, SFW (requires `core`) |
| `nsfw` | `grok-imagine-nsfw` | Opt-in ErosForge + NSFW tools (requires `core`) |
| `delivery-post` | `grok-imagine-delivery-post` | Assembly, color, polish, upscale, ffmpeg (requires `core`) |

```bash
cinematic-studio plugin packs
```

Satellite manifests: `.grok-plugin/packs/<pack_id>/plugin.json`.

## Skill groups (62)

Browse with: `cinematic-studio plugin list --grouped`

### Core / Orchestration
`grok-imagine-cinematic-studio` · `studio-director` · `mega-production-architect` · `production-bible-workflow` · `cinematic-studio-meta-installer` · `cinematic-skill-creator` · `skill-agent-architect` · `github-repo-manager` · `grok-doctor` · `parallel-brief-dispatcher`

### Camera & Image
`director-of-photography` · `director-of-photography-v3-3` *(legacy; prefer primary DoP)* · `imagine-prompt-master` · `i2i-cinematic-refiner` *(SFW)* · `i2i-refiner` *(explicit)* · `ai-image-recreation` · `key-art-poster-designer` · `reference-asset-curator` · `plate-motion-readiness-lead` · `contact-micro-physics-specialist`

### Identity & Continuity
`character-dna-extractor` · `identity-lock-specialist` · `costume-wardrobe-continuity` · `hair-makeup-continuity` · `multi-character-identity-arbiter` · `continuity-consistency-guardian` · `multi-clip-continuity-orchestrator` · `performance-emotion-director` · `production-designer-set-decorator`

### Sequence & Narrative
`sequence-director` · `cinematic-sequence-extender` · `extend-frame-to-video` · `narrative-arc-pacing-strategist` · `arc-replan-copilot` · `animatic-director` · `image-to-video-specialist` · `trailer-teaser-director`

### Audio
`sonic-architect-native-audio-virtuoso` · `foley-sound-design-specialist` · `dialogue-adr-director` · `score-temp-music-supervisor` · `localization-subtitle-specialist`

### Action & VFX
`stunt-action-choreographer` · `vfx-sfx-supervisor`

### Batch & Quota
`workflow-quota-optimizer` · `quota-dashboard` · `sfw-batch-orchestrator` · `nsfw-quota-orchestrator`

### NSFW (explicit activation only)
`erosforge-nsfw-director` · `nsfw-sequence-extender` · `nsfw-chain-qa-protocol`

### QA, Handoff & Delivery
`quality-assurance-guardian` · `chain-qa-protocol` · `handoff-packet-validator` · `imagine-execution-bridge` · `assembly-editor` · `post-production-color-grading-supervisor` · `ai-polish-director` · `ai-video-upscaler` · `cinematic-ffmpeg` · `title-motion-graphics-lead` · `distribution-crop-strategist`

## Slash commands (11)

`automation` · `cinematic` · `dashboard` · `delivery` · `dna` · `imagine` · `intelligence` · `nsfw` · `quota` · `sfw` · `validate`

## Legacy notes

| Item | Status |
|------|--------|
| `director-of-photography-v3-3` | Kept for old activation phrases; new work → `director-of-photography` |
| `i2i-refiner` vs `i2i-cinematic-refiner` | Complementary (explicit vs SFW), not duplicates |
| Method A `skills-backup-*` | Created on `update`; prune with `declutter --apply` |

## Related

- Manifest: `scripts/required_skills.manifest`
- Pack config: `config/plugin_packs.yaml`
- Plugin pin: `.grok/skills/github-repo-manager/references/plugin_catalog_release.md`
- Install: `docs/guides/installation_guide.md`

*v3.9.0 · Grok 4.5 / v9-4p5 · July 2026*
