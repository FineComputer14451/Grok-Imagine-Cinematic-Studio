---
name: cinematic-skill-creator
description: Create and validate Grok skills for the Cinematic Studio ecosystem (Grok 4.5 / v9-4p5 + Grok Imagine Video 1.5 Native). Scaffolds SKILL.md, scripts, and references with Role Card integration, MODEL_LAYER_v4.5 support, and validate checks. Activate when adding cinematic skills, forking agents, migrating legacy skills, or running skill hygiene.
---

# Cinematic Skill Creator v4.5 (Grok 4.5 / v9-4p5 + Grok Imagine Video 1.5 Native)

You create and validate skills specifically for **Grok Imagine Cinematic Studio v4.5+**.  

Optimized for:
- `grok-v9-4p5-chat-expert` (default high-quality specialist work)
- `grok-v9-4p5-multi` (multi-agent / Team Leader / Full Studio orchestration)
- `grok-4-auto` (draft / balanced / quota-sensitive)
- Native Grok Imagine Video 1.5 (image-to-video, native audio, physics-aware motion, extend-from-frame)

For general-purpose skills outside this repo, use the base `skill-creator`.

## Model Layer (Grok 4.5 / v9-4p5)

| Task type                    | Preferred model              | Reasoning |
|-----------------------------|------------------------------|-----------|
| Skill design & complex migration | `grok-v9-4p5-chat-expert` | high      |
| Multi-skill / suite architecture | `grok-v9-4p5-multi`       | high      |
| Quick scaffold / validation  | `grok-4-auto`                | medium    |

**Registry:** `tools/models.py` (schema 1.1+) · `references/agents/MODEL_LAYER_v4.5.md`

## When to Activate

- User wants a new cinematic skill (v4.5 native)
- User asks to validate an existing skill or migrate legacy skills to v4.5 / v9-4p5 model support
- User says `CREATE CINEMATIC SKILL`, `SCAFFOLD SKILL`, `VALIDATE SKILL`, `UPDATE SKILL TO v4.5`, `MIGRATE AGENT TO 4.5`, `CREATE V4.5 AGENT`, or `ADD MODEL LAYER`

## Conventions (Non-Negotiable)

1. **Location** — `<repo-root>/.grok/skills/<kebab-name>/`
2. **SKILL.md** — YAML frontmatter with `name` + `description` (single line, no colons, max 1024 chars)
3. **No human docs** — No README/CHANGELOG inside skill dirs
4. **Role Card link** — Production agents must reference `references/agents/<card>.md` (v4.5 preferred)
5. **Version** — New skills declare **v4.5**. Include Model Layer section with the three v9-4p5 identifiers.
6. **Scripts** — Prefer `python3 tools/cinematic_studio_cli.py` over duplicating pipeline logic.
7. **Model Layer** — Every skill must contain the standard Model Layer table and `model_compatibility` declaration (see template).

## Workflow

### Step 1 — Scaffold (or Migrate)

```bash
mkdir -p .grok/skills/<skill-name>/{scripts,references}
```

For legacy migration (v3.6 / v4.0 → v4.5):
- Add or replace the Model Layer section using the current template
- Update title and preferred_model
- Point to `MODEL_LAYER_v4.5.md`

### Step 2 — Write / Update SKILL.md

Follow `references/skill_template.md` (v4.5 template).  
Keep body focused. Always include:

- Model Layer table (chat-expert / multi / auto)
- `model_compatibility` YAML block
- Grok Imagine Video 1.5 Native section when the skill touches video, audio, or sequence work

### Step 3 — Validate

```bash
# Basic structure
bash .grok/skills/cinematic-skill-creator/scripts/validate_skill.sh .grok/skills/<skill-name>/

# Prefer also checking model layer presence manually or via future --v45 flag
```

### Step 4 — Register

- Add/update row in `AGENTS.md` if user-facing
- Update `references/agents/AGENT_INDEX.md` if agent-related
- Ensure Role Card (if any) references MODEL_LAYER_v4.5

## Skill Types

| Type            | Example                        | Requires Role Card | v4.5 Notes                                      |
|-----------------|--------------------------------|--------------------|-------------------------------------------------|
| Agent skill     | `sequence-director`, `studio-director` | Yes           | Must include Model Layer + Video 1.5 protocols  |
| Pipeline skill  | `cinematic-sequence-extender`  | No                 | Update for 1.5 + model preferences              |
| Tool skill      | `ai-video-upscaler`, `character-dna-extractor` | No      | Add model guidance where reasoning is involved  |
| Meta skill      | `cinematic-skill-creator`      | No                 | This skill — maintains v4.5 compatibility layer |

## Reference Files

- `references/skill_template.md` — v4.5 blank SKILL.md scaffold (includes Model Layer)
- `references/skill_conventions.md` — Naming, structure, Model Layer rules, migration guide
- `references/agents/MODEL_LAYER_v4.5.md` — Canonical model profiles and routing rules
- `tools/models.py` — Runtime registry (schema 1.1+)

## Quick Commands

- `CREATE CINEMATIC SKILL <name>`
- `SCAFFOLD SKILL <name>`
- `UPDATE SKILL TO v4.5 <path>`
- `ADD MODEL LAYER <skill>`
- `VALIDATE SKILL <path>`

---

*Cinematic Skill Creator v4.5 — Grok 4.5 / v9-4p5-chat-expert · multi · auto · Imagine Video 1.5 Native*
