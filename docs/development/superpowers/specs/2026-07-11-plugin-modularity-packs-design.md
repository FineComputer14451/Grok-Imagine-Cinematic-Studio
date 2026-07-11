# Design: Plugin Modularity Packs (Hybrid + Additive)

**Date:** 2026-07-11  
**Topic:** Marketplace modularity — full suite + five satellite packs  
**Status:** Design approved — ready for implementation planning  
**Target version:** 3.8.0 (studio VERSION bump with this feature)  
**Approach:** Manifest-only packs (filtered views over a single skill/command tree)

## Summary of Decisions

| Decision | Choice |
|----------|--------|
| Primary goal | **Plugin modularity** (lighter installs + marketplace discovery) |
| Install story | **Hybrid + additive** — full suite remains recommended one-click install; satellite packs optional |
| Pack set (v1) | `core` · `camera-image` · `sequence-narrative` · `nsfw` · `delivery-post` |
| Duplicate skills | **Declutter-aware** — `full_suite_wins` when full suite and satellites coexist |
| Source layout | **Mono-repo filtered views** — one `.grok/skills/` and `commands/` tree; thin pack selectors |
| Commands | **Domain-mapped** per pack |
| Implementation approach | **Manifest-only packs** — `config/plugin_packs.yaml` drives generation; no skill file copies |
| New creative agents/skills | **Out of scope** for this design (structure only) |

## Problem

Today the studio ships as a single marketplace plugin (`grok-imagine-cinematic-studio`) with **48 skills** and **11 slash commands**. That is correct for power users and one-click onboarding, but:

- Lighter installs (core-only, delivery-only, NSFW opt-in pack) are not marketplace-discoverable.
- Dual Method A/B installs already create skill triple-load risk; modularity must not make that worse.
- Skill files must remain single-source (no forked pack trees).

## Goals

1. Keep **full suite** as the recommended install.
2. Publish **five satellite packs** in the same marketplace for modular installs.
3. Maintain **one skill tree** and **one command tree** in the repo.
4. Extend **declutter** so full suite supersedes overlapping satellite skills.
5. Fail closed in catalog generation if pack membership is inconsistent.
6. Preserve existing pin protocol (`plugin catalog pin` / content SHA).

## Non-goals (v1)

- Multi-repo pack releases
- Hard runtime package dependencies enforced by Grok (soft `requires` in docs + verify only, unless platform already supports depends_on)
- New Role Cards, agents, or production skills (content expansion is a separate design)
- New slash commands (`/sequence`, `/camera`) — optional follow-up
- Splitting Python CLI / pip packages per pack
- Shadow package roots or symlink skill trees

---

## Architecture

```text
                    ┌─────────────────────────────────────┐
                    │  Marketplace (single source)        │
                    │  finecomputer14451-cinematic-studio │
                    └──────────────┬──────────────────────┘
           ┌───────────┬───────────┼───────────┬───────────┬──────────┐
           ▼           ▼           ▼           ▼           ▼          ▼
     full-suite      core    camera-image  sequence-   nsfw    delivery-post
  (recommended)                               narrative
           │           │           │           │           │          │
           └───────────┴───────────┴─────┬─────┴───────────┴──────────┘
                                         ▼
                         config/plugin_packs.yaml  (selectors)
                                         │
                    generate → .grok-plugin/plugin.json
                             → pack plugin manifests
                             → marketplace.json (6 entries)
                             → plugin-index.json
                                         │
                                         ▼
                              .grok/skills/*  (single tree)
                              commands/*      (single tree)
```

### Principles

1. **Single skill/command source** — no copies, no shadow trees.
2. **Full suite = union** of all pack skill sets (generator verifies equality).
3. **Packs = filtered views** — thin YAML selectors only.
4. **Full suite wins** on declutter when both full suite and satellites are installed.
5. **Domain-mapped commands** — each pack ships only its slash commands; shared ops live on `core` + full suite.
6. **Soft dependency** — satellites declare `requires: [core]`; full suite does not require satellites.

### Versioning

- Studio release for this feature: **3.8.0**.
- All packs share the **same version string** as the full suite in v1.
- Marketplace pin: all six plugin entries use the **same content SHA** (current pin protocol generalized to multi-plugin entries).

---

## Pack membership

Skills stay in one tree. Each skill is assigned to **exactly one satellite pack**. Full suite includes **all 48**.

### 1. `core` — `grok-imagine-cinematic-core`

Orchestration, identity baseline, Imagine runtime, quota, QA gates, meta.

**Skills:**

- `grok-imagine-cinematic-studio`
- `studio-director`
- `mega-production-architect`
- `production-bible-workflow`
- `cinematic-studio-meta-installer`
- `skill-agent-architect`
- `github-repo-manager`
- `character-dna-extractor`
- `identity-lock-specialist`
- `multi-character-identity-arbiter`
- `imagine-prompt-master`
- `imagine-execution-bridge`
- `handoff-packet-validator`
- `workflow-quota-optimizer`
- `quality-assurance-guardian`
- `chain-qa-protocol`

**Commands:** `/cinematic` · `/dna` · `/imagine` · `/dashboard` · `/validate` · `/quota` · `/intelligence` · `/automation` · `/sfw`

**Requires:** none

---

### 2. `camera-image` — `grok-imagine-camera-image`

Lens, stills, i2i, key art, reference routing, i2v prep.

**Skills:**

- `director-of-photography`
- `director-of-photography-v3-3`
- `production-designer-set-decorator`
- `i2i-cinematic-refiner`
- `i2i-refiner`
- `ai-image-recreation`
- `key-art-poster-designer`
- `reference-asset-curator`
- `image-to-video-specialist`

**Commands:** none in v1 (activation via `/cinematic` + `/imagine` when core/full is present)

**Requires:** `core`

---

### 3. `sequence-narrative` — `grok-imagine-sequence-narrative`

Long-form story, extend, continuity, performance, audio, action/VFX, SFW batch orchestration.

**Skills:**

- `sequence-director`
- `cinematic-sequence-extender`
- `narrative-arc-pacing-strategist`
- `arc-replan-copilot`
- `animatic-director`
- `continuity-consistency-guardian`
- `performance-emotion-director`
- `trailer-teaser-director`
- `sonic-architect-native-audio-virtuoso`
- `foley-sound-design-specialist`
- `localization-subtitle-specialist`
- `stunt-action-choreographer`
- `vfx-sfx-supervisor`
- `sfw-batch-orchestrator`

**Commands:** none in v1

**Requires:** `core`

---

### 4. `nsfw` — `grok-imagine-nsfw`

Explicit opt-in only. Marketplace description must state consent requirement.

**Skills:**

- `erosforge-nsfw-director`
- `nsfw-quota-orchestrator`
- `nsfw-sequence-extender`
- `nsfw-chain-qa-protocol`

**Commands:** `/nsfw`

**Requires:** `core`

---

### 5. `delivery-post` — `grok-imagine-delivery-post`

Assembly, grade, polish, upscale, mux/social crops.

**Skills:**

- `assembly-editor`
- `post-production-color-grading-supervisor`
- `ai-polish-director`
- `ai-video-upscaler`
- `cinematic-ffmpeg`

**Commands:** `/delivery`

**Requires:** `core`

---

### Full suite — `grok-imagine-cinematic-studio` (unchanged name)

- **Skills:** all 48 (union of the five packs)
- **Commands:** all 11
- **Recommended:** `true` in marketplace

### Membership rules

| Rule | Detail |
|------|--------|
| Exclusive pack | Each skill appears in exactly one satellite pack |
| Full union | Full suite skill list equals union of five packs (hard verify) |
| Soft deps | Non-core packs declare `requires: ["core"]` |
| NSFW isolation | No NSFW skill appears outside the `nsfw` pack |
| Legacy DoP | `director-of-photography-v3-3` remains in `camera-image` |

### Role Cards / agents

- Role Cards remain in `references/agents/` (not packaged per satellite).
- Pack marketplace descriptions list primary activation phrases for included agents.
- Docs update: `SKILLS_TAXONOMY.md` and `AGENT_INDEX.md` gain pack affiliation notes (implementation plan).

---

## Catalog source of truth

**File:** `config/plugin_packs.yaml`

Conceptual schema:

```yaml
version: "1"
studio_version: "3.8.0"   # or read from VERSION at generate time
full_plugin:
  name: grok-imagine-cinematic-studio
  recommended: true
  # skills/commands may be "all" resolved as union at generate time
packs:
  core:
    name: grok-imagine-cinematic-core
    display_name: "Cinematic Studio Core"
    requires: []
    skills: [...]
    commands: [cinematic, dna, imagine, dashboard, validate, quota, intelligence, automation, sfw]
  camera-image:
    name: grok-imagine-camera-image
    requires: [core]
    skills: [...]
    commands: []
  sequence-narrative:
    name: grok-imagine-sequence-narrative
    requires: [core]
    skills: [...]
    commands: []
  nsfw:
    name: grok-imagine-nsfw
    requires: [core]
    skills: [...]
    commands: [nsfw]
  delivery-post:
    name: grok-imagine-delivery-post
    requires: [core]
    skills: [...]
    commands: [delivery]
declutter:
  full_suite_plugin: grok-imagine-cinematic-studio
  policy: full_suite_wins
```

### Generator outputs

| Artifact | Role |
|----------|------|
| `.grok-plugin/plugin.json` | Full suite manifest (current consumers) |
| `.grok-plugin/packs/<pack-id>.plugin.json` | Generated pack manifests (or equivalent layout required by Grok multi-plugin mono-repo) |
| `.grok-plugin/marketplace.json` | Six plugin entries; shared git URL; shared pin SHA |
| `.grok-plugin/plugin-index.json` | Index of all plugins + skill/command lists |

Generator lives in **`tools/plugin_catalog.py`**, invoked by existing `plugin catalog` / `generate_plugin_index` flows.

**Install path spike (implementation):** confirm how Grok Build resolves multiple plugins from one git source with different skill subsets; if platform requires distinct package roots, generate thin package roots that **reference** shared skill paths without copying skill bodies (no permanent dual content).

---

## Declutter policy (`full_suite_wins`)

```text
IF full suite installed AND any satellite pack installed:
  → compute skill name intersection
  → remove satellite-installed duplicates (prefer full suite install path)
  → report dry-run / apply via existing declutter CLI
```

Extend:

- `scripts/cinematic_studio.sh declutter`
- `cinematic-studio plugin declutter` (and related Python helpers)
- `references/SKILLS_TAXONOMY.md`
- `AGENTS.md` install/declutter notes

When only satellites are installed (no full suite), declutter does not remove pack skills; soft-dep warnings may still list missing `core`.

---

## User flows

| User action | Result |
|-------------|--------|
| Install full suite only | Current recommended experience |
| Install `core` only | Lean orchestration + DNA + Imagine + QA + quota |
| Install `core` + `delivery-post` | Lean production + polish/mux |
| Install `core` + `nsfw` | Opt-in explicit pipeline without camera/delivery bulk |
| Install full + any satellite | Declutter removes overlapping satellite skills; full suite retained |
| Install satellite without `core` | Docs + `validate` / catalog check warn on soft dep (v1 non-blocking) |

---

## Error handling

| Case | Behavior |
|------|----------|
| Skill listed in two packs | Generator **fails** (hard error) |
| Full suite skill set ≠ pack union | Generator **fails** |
| Unknown skill name in YAML | Generator **fails** |
| Command assigned to two packs | Generator **fails** |
| Command path missing | Generator **fails** |
| Marketplace missing pack entry | `plugin catalog check` **fails** |
| Pin SHA missing on any plugin entry | `validate_marketplace_pins` **fails** |
| Declutter dual install | Soft remove satellite dups; never delete full-suite skills |

---

## Testing

1. **Unit — packs YAML:** parse; exclusive skill membership; exclusive command ownership (outside full suite); union equals full 48; every skill in `required_skills.manifest` appears exactly once across packs.
2. **Catalog generation:** temp dir generate; marketplace has 6 plugins; shared SHA field present after pin; pack manifests list correct skill counts.
3. **Declutter dry-run:** mock full + satellite install → expects satellite skill removals only.
4. **Regression:** existing `verify_plugins` / `plugin catalog check` / full suite install paths still pass.
5. **Docs smoke:** pack names and install matrix appear in taxonomy / install guide section.

---

## Documentation & release touchpoints

- `VERSION` → 3.8.0
- `CHANGELOG.md` — modularity section
- `README.md` — install matrix (full vs packs)
- `docs/guides/installation_guide.md` / `UPGRADE_GUIDE.md`
- `references/SKILLS_TAXONOMY.md` — pack column / groups
- `AGENTS.md` — marketplace multi-plugin + declutter
- `.grok/skills/cinematic-studio-meta-installer` — pack-aware install notes
- `github-repo-manager` pin docs — multi-entry pin

---

## Implementation touchpoints (for writing-plans)

1. Author `config/plugin_packs.yaml` with the membership tables above.
2. Extend `tools/plugin_catalog.py` to load packs, validate, generate multi-plugin marketplace + pack manifests.
3. Extend pin/check/release scripts for six entries.
4. Extend declutter for `full_suite_wins`.
5. Docs + VERSION/CHANGELOG.
6. Tests under `tests/test_plugin_catalog_pin.py` (or new `tests/test_plugin_packs.py`).
7. Spike Grok multi-plugin mono-repo install layout; document result in plan if layout tweak needed.

---

## Success criteria

- Marketplace lists **6** plugins from this repo; full suite still recommended.
- A user can install **core-only** and receive only core skills + core commands.
- Generator refuses inconsistent pack definitions.
- Dual full+satellite install can be cleaned with declutter (`full_suite_wins`).
- No skill file duplication in git.
- Existing full-suite verify and pin release path remain green.

## Open implementation detail (non-blocking for design)

Exact on-disk multi-plugin package layout under `.grok-plugin/` depends on Grok Build plugin format for multiple plugins from one git URL. Design constraint: **do not duplicate skill file bodies**; prefer generated manifests that select paths from the shared tree. Resolve during implementation spike; if platform forces separate roots, use generated path lists that still read from shared `.grok/skills/` without forking content.
