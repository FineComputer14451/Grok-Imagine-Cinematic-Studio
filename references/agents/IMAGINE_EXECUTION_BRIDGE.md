# Imagine Execution Bridge (Classic Surface C) — Enhanced v4.5

**Status:** Supporting protocol (subset of Imagine Agent Mode Handoff)  
**Owner:** Studio Director  
**Canonical full protocol:** `IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md`  
**Model Layer:** `MODEL_LAYER_v4.5.md` (v4.5.1)

---

## Purpose

Provide a clean, copy-paste ready bridge packet for **surface C** (`grok.com/imagine` web UI) when tools or API are unavailable. This is the classic “Execution Bridge” path.

For all other surfaces (A/B/D) use the full **Imagine Agent Mode Handoff**.

---

## Model Layer (Grok 4.5 / v9-4p5)

| Task type                         | Preferred model               | Reasoning |
|-----------------------------------|-------------------------------|-----------|
| Bridge packet assembly            | `grok-v9-4p5-chat-expert`     | high      |
| Multi-shot bridge planning        | `grok-v9-4p5-multi`           | high      |
| Quick refresh                     | `grok-4-auto`                 | medium    |

```yaml
model_compatibility:
  - grok-v9-4p5-chat-expert
  - grok-v9-4p5-multi
  - grok-4-auto
preferred_model: grok-v9-4p5-chat-expert
```

---

## Imagine Video Protocol

- Default: **1.0**
- Escalate to **1.5** only when native audio / physics / intimacy required
- Always include the full `VIDEO_PIPELINE_SPEC` in the paste block
- On 1.5: include Sound Layer notes

---

## Activation

```
ACTIVATE IMAGINE_BRIDGE
BRIDGE TO CLIPBOARD
EMIT EXECUTION BRIDGE
```

(Also available via `python tools/cinematic_studio_cli.py imagine bridge ...`)

---

## Standard Bridge Packet (Markdown for paste)

```markdown
## Imagine Execution Bridge — Surface C (grok.com/imagine)

**Project / Shot:** <subject_id>
**Mode:** image_prompt | image_to_video | video_prompt
**Video Version:** 1.0 | 1.5
**Preferred Chat Model (planning):** grok-v9-4p5-chat-expert / multi / auto

### VIDEO_PIPELINE_SPEC
[VIDEO_PIPELINE_SPEC: model="grok-imagine-video" or "grok-imagine-video-1.5", version="1.0|1.5", ...]

### Prompt
<Ultimate Template body from Imagine Prompt Master / I2V Specialist>

### References
- Primary plate: <path or description>
- DNA inject (if any): <block or slug>

### Sound Layer (required for 1.5 / audio)
<notes or “none”>

### Instructions for User
1. Paste the entire block into grok.com/imagine
2. Attach reference images if available
3. Generate
4. Download result → return via: <return_path>
```

---

## Studio Director Rules

1. Prefer full Imagine Agent Mode Handoff (surfaces A/B/D) when tools or API are available.
2. Use this classic bridge only when the user must work in the web UI.
3. Still enforce specialist order (DNA → Lock → Curator → Prompt → I2V) before emitting the bridge.
4. Always declare video version and preferred planning model.
5. Require return_path so the result re-enters the studio pipeline (QA, record, etc.).

---

*Enhanced 2026-07-21 for grok-4-auto · grok-v9-4p5-multi · grok-v9-4p5-chat-expert + Imagine Video 1.0 / 1.5 Native*  
*Classic surface-C subset of the official Imagine Agent Mode Handoff Protocol.*
