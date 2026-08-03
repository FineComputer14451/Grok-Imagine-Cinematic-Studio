# Skill Validation Protocol

**Version:** 1.0 (agentskills.io + Cinematic Studio v4.5)  
**Status:** Official  
**Owner:** Skill Creator · Cinematic Skill Creator · GitHub Repo Manager (batch CI)  
**Last updated:** August 2026  

**Primary engine:** `.grok/skills/skill-creator/scripts/validate-skill.sh` (or agentskills-compatible validator)  
**Batch engine:** `.grok/skills/github-repo-manager/scripts/validate-all-skills.sh`  

---

## 1. Purpose

Invalid frontmatter or structure breaks agent loading, pollutes the system prompt, or fails CI. This protocol defines:

1. **Hard structure rules** for `SKILL.md`
2. **Cinematic Studio conventions** for v4.5 production agents
3. How skill validation relates to **handoff packet** validation at generation time

---

## 2. Skill layout

```
.grok/skills/<kebab-name>/
├── SKILL.md              # Required
├── scripts/              # Optional
├── references/           # Optional
└── assets/               # Optional
```

- Directory name = frontmatter `name`
- No README/CHANGELOG inside skill dirs

---

## 3. Hard validation rules

| Check | Rule |
|-------|------|
| File | `SKILL.md` exists, starts with ASCII `---` |
| `name` | 2–64 chars, kebab-case, matches directory, no quotes |
| `description` | Required, ≤1024 chars, plain YAML scalar (no quotes) |
| Description bans | No `TODO`, no `: ` (colon-space), no `<` / `>` |
| Frontmatter keys | Only: name, description, license, compatibility, metadata, allowed-tools |
| Body | Non-empty after frontmatter |
| Control tokens | No `<\|...\|>` in any `.md` under the skill |

---

## 4. How to run

```bash
bash .grok/skills/skill-creator/scripts/validate-skill.sh .grok/skills/<skill-name>
bash .grok/skills/github-repo-manager/scripts/validate-all-skills.sh
```

---

## 5. Cinematic conventions (v4.5)

- Model Layer section + `model_compatibility` for `grok-v9-4p5-chat-expert`, `grok-v9-4p5-multi`, `grok-4-auto`
- Production agents reference Role Cards under `references/agents/`
- Prefer studio CLI over duplicating pipeline logic

---

## 6. Relationship to handoff validation

| Layer | Tool | When |
|-------|------|------|
| Skill structure | `validate-skill.sh` | Create / edit / pre-commit |
| Packet schema | `validate_handoff.py` | Before Identity Lock, extend, i2v, Imagine spend |
| Surface bridges | `validate_surface.py` | Before Imagine Agent Mode execution |

---

## 7. Related

- `HANDOFF_PACKET_PROTOCOLS.md`
- `IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md`
- `SURFACE_BRIDGES_INDEX.md`

---

*Official Skill Validation Protocol — August 2026*
