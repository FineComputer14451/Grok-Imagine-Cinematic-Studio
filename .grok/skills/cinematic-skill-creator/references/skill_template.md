# <Skill Name> v4.5 (Grok 4.5 / v9-4p5 + Grok Imagine Video 1.5 Native)

**Role Card (if agent):** `references/agents/<Card_Name>.md` (v4.5 preferred)

> Always load and follow the Role Card before major decisions when this is an agent skill.

## Model Layer (Grok 4.5 / v9-4p5)

| Task type                         | Preferred model               | Reasoning   |
|-----------------------------------|-------------------------------|-------------|
| Standard specialist / creative    | `grok-v9-4p5-chat-expert`     | high        |
| Multi-agent / handoff / synthesis | `grok-v9-4p5-multi`           | high        |
| Draft / quota-sensitive / routine | `grok-4-auto`                 | medium      |

**Registry:** `tools/models.py` (schema 1.1+) · `references/agents/MODEL_LAYER_v4.5.md` · `models verify`

```yaml
model_compatibility:
  - grok-v9-4p5-chat-expert
  - grok-v9-4p5-multi
  - grok-4-auto
preferred_model: grok-v9-4p5-chat-expert   # change to multi or auto as appropriate
```

## When to Activate

- ...
- Trigger phrases: `ACTIVATE <NAME>`, ...

## Core Protocols

1. ...
2. ...

## Output Formats

- ...

## Integration & Handoff Rules

- ...
- Always produce valid Handoff Packet v1.2 / typed packets when handing off.
- Reference MODEL_LAYER_v4.5 for model selection on complex tasks.

## Grok Imagine Video 1.5 Native (include if relevant)

- Enforce VIDEO_PIPELINE_SPEC
- Carry AUDIO_MOMENTUM_VECTOR on sequence handoffs
- Prefer native 1.5 when audio or physics fidelity is required

---

*Generated from cinematic-skill-creator template v4.5 — optimized for grok-v9-4p5-chat-expert / multi / auto*
