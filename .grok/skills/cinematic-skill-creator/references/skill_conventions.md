# Cinematic Skill Conventions (v4.5)

**Aligned with MODEL_LAYER_v4.5.md and tools/models.py schema 1.1**

## Naming
- Directory: `kebab-case`, 2–64 chars, starts/ends with letter or digit
- `name` in frontmatter must match directory exactly

## Description Field
- Single line plain text
- No colons (`:`)
- No angle brackets (`<` `>`)
- Max 1024 characters
- Include trigger phrases for auto-invocation

## Structure
```
.grok/skills/<name>/
├── SKILL.md          # Required
├── scripts/          # Optional executables
├── references/       # Optional long docs / Role Cards (local)
└── assets/           # Optional templates/images
```

## Model Layer Requirements (Mandatory for v4.5+)

Every new or migrated skill **must** include a **Model Layer** section (see `skill_template.md`).

Supported / required identifiers:

| Identifier                  | When to Prefer                                      |
|-----------------------------|-----------------------------------------------------|
| `grok-v9-4p5-chat-expert`   | Default for specialist creative, DNA, QA, prompts   |
| `grok-v9-4p5-multi`         | Team Leader, Studio Director (Full Studio), multi-agent orchestration, handoff synthesis |
| `grok-4-auto`               | Drafts, pre-vis, routine, quota-sensitive work      |

Skills should declare:

```yaml
model_compatibility:
  - grok-v9-4p5-chat-expert
  - grok-v9-4p5-multi
  - grok-4-auto
preferred_model: <one of the three>
```

Reference the canonical docs:
- `tools/models.py`
- `references/agents/MODEL_LAYER_v4.5.md`

## Agent Skills
- Must reference authoritative Role Card in `references/agents/` (v4.5 preferred)
- Declare activation command matching AGENT_INDEX
- Use **v4.5** in skill body title where possible
- Include Grok 4.6 / v9-4p5 Model Layer + Video 1.5 Native sections for relevant agents

## Versioning
- New skills: target **v4.5**
- Migration path: v3.6 → v4.0 → v4.5 (add Model Layer + update preferred models)
- Title pattern: `# <Name> v4.5 (Grok 4.6 / v9-4p5 + Grok Imagine Video 1.5 Native)`

## v4.5 Migration Notes
- Replace hard-coded “Grok 4.3” or generic “Grok 4.6” language with explicit v9-4p5 identifiers.
- Team Leader / multi-agent skills → prefer `grok-v9-4p5-multi`
- Prompt / DNA / QA / single-agent creative → prefer `grok-v9-4p5-chat-expert`
- Draft / Animatic / routine → `grok-4-auto` is acceptable

## Deprecated Patterns
- Do not create duplicate skills for the same agent
- Do not put Role Cards only in `.grok/skills/*/references/` — canonical path is `references/agents/`
- Do not use absolute `/home/workdir/` paths
- Avoid mixing pre-v4.5 model language without an explicit Model Layer section
