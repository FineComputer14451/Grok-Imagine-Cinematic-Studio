# MODEL_LAYER_v4.5.md
**Grok Imagine Cinematic Studio — Canonical Model Layer**  
**Version:** 4.5 / v9-4p5 | **Schema:** tools/models.py 1.1  
**Date:** 2026-07-20  
**Owner:** Studio Director + Skill Agent Architect

---

## Purpose

This document is the single source of truth for how Cinematic Studio skills and agents should select, prefer, and declare compatibility with Grok models. All new and updated skills must reference this layer.

It introduces first-class support for the three primary surface identifiers:

| Identifier                    | Short Name     | Primary Role                              |
|-------------------------------|----------------|-------------------------------------------|
| `grok-v9-4p5-chat-expert`     | Chat Expert    | Highest-quality single-agent reasoning    |
| `grok-v9-4p5-multi`           | Multi          | Multi-agent orchestration & synthesis     |
| `grok-4-auto`                 | Auto           | Balanced / automatic routing              |

---

## Model Profiles

### 1. grok-v9-4p5-chat-expert  (Default for most specialist work)

- **Best for**: Deep reasoning, high-fidelity prompt engineering, Character DNA work, Identity Lock decisions, QA reviews, narrative architecture, single-agent creative direction.
- **Strengths**: Reasoning depth, prompt quality, long-context fidelity, character consistency.
- **Preferred agents**: Imagine Prompt Master, Character DNA Extractor, Identity Lock Specialist, Quality Assurance Guardian, Narrative Arc & Pacing Strategist, Director of Photography (detailed lighting design).
- **Reasoning recommendation**: **high** for Bibles, locks, QA, and complex creative judgments.
- **Aliases**: `v9-4p5-chat-expert`, `chat-expert`, `4p5-expert`, `grok-4.5-expert`

### 2. grok-v9-4p5-multi  (Default for Team Leader / Full Studio Mode)

- **Best for**: Multi-agent coordination, Team Leader synthesis, parallel specialist briefings, Handoff Packet assembly & Cross-Agent Consistency Audit, Sequence Director orchestration, Mega Production Architect planning.
- **Strengths**: Multi-agent awareness, handoff integrity, parallel reasoning, final synthesis quality.
- **Preferred agents**: Team Leader / Final Synthesizer, Studio Director (when in Full Studio or MAXIMUM_AGENTIC_MODE), Mega Production Architect, Sequence Director, Continuity & Consistency Guardian (cross-clip).
- **Reasoning recommendation**: **high** + agentic depth.
- **Aliases**: `v9-4p5-multi`, `4p5-multi`, `multi`, `grok-4.5-multi`

### 3. grok-4-auto

- **Best for**: Routine specialist tasks, draft / pre-vis passes, quota-sensitive sessions, rapid iteration where maximum reasoning is not required.
- **Strengths**: Balanced speed vs quality, lower cost profile, good generalist.
- **Preferred agents**: Animatic Director (draft boards), Reference Asset Curator (standard tier), Foley (routine), Localization (standard), any “draft” or “fast” mode.
- **Reasoning recommendation**: medium (escalate to chat-expert or multi when quality gates fail).
- **Aliases**: `4-auto`, `auto`, `grok-auto`

---

## Usage Rules for Skills

Every skill SKILL.md that performs non-trivial reasoning should contain a short **Model Layer** section, for example:

```markdown
## Model Layer (Grok 4.5 / v9-4p5)

| Task type                    | Preferred model              | Reasoning |
|-----------------------------|------------------------------|-----------|
| Standard specialist work    | grok-v9-4p5-chat-expert      | high      |
| Multi-agent / handoff work  | grok-v9-4p5-multi            | high      |
| Draft / quota-sensitive     | grok-4-auto                  | medium    |

Registry: `tools/models.py` · `references/agents/MODEL_LAYER_v4.5.md` · `models verify`
```

### Declaration in Frontmatter or Body (Recommended)

Skills may also declare:

```yaml
model_compatibility:
  - grok-v9-4p5-chat-expert
  - grok-v9-4p5-multi
  - grok-4-auto
preferred_model: grok-v9-4p5-chat-expert   # or multi / auto
```

---

## Routing Helpers (from tools/models.py)

```python
from tools.models import (
    resolve_chat_model,
    recommended_model_for_role,
    DEFAULT_XAI_CHAT_MODEL,      # → grok-v9-4p5-chat-expert
    DEFAULT_XAI_MULTI_MODEL,     # → grok-v9-4p5-multi
    DEFAULT_XAI_AUTO_MODEL,      # → grok-4-auto
)
```

- `resolve_chat_model("multi")` → `grok-v9-4p5-multi`
- `recommended_model_for_role("Team Leader")` → `grok-v9-4p5-multi`
- `recommended_model_for_role("Imagine Prompt Master")` → `grok-v9-4p5-chat-expert`

---

## Migration Notes

- Previous default `grok-4.3` is retained as a legacy entry only.
- Skills that hard-coded “Grok 4.5” or “grok-4.5” should now prefer the explicit v9-4p5 identifiers above.
- Team Leader / Final Synthesizer and any Full Studio Mode orchestration should default to **grok-v9-4p5-multi**.
- All Imagine Video / Image model selection remains unchanged (still driven by `IMAGINE_*_MODELS`).

---

## Validation

After updating skills or this registry:

```bash
python tools/models.py          # or via cinematic_studio_cli.py models verify
bash .grok/skills/cinematic-skill-creator/scripts/validate_skill.sh <skill> --v4
```

---

**End of MODEL_LAYER_v4.5.md**  
*Grok Imagine Cinematic Studio — Grok 4.5 / v9-4p5 Model Layer*
