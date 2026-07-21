---
name: imagine-execution-bridge
description: Grok chat to grok.com/imagine handoff bridge for Grok Imagine Cinematic Studio. Emits copy-paste VIDEO_PIPELINE_SPEC reference hints and native audio Sound Layer blocks when API generation is unavailable. Activate with ACTIVATE IMAGINE_BRIDGE or when user needs grok.com/imagine copy-paste packets. Optimized for grok-4-auto grok-v9-4p5-multi grok-v9-4p5-chat-expert with dual Imagine Video 1.0 and 1.5 Native.
---

# Imagine Execution Bridge v3.8.5 (Grok 4.5 / v9-4p5 · Web Handoff)

**Web UI subset** of Imagine execution (surface `grok_com_imagine`). Emits copy-paste-ready packets for [grok.com/imagine](https://grok.com/imagine) when API or in-session tools are unavailable.

**Official multi-surface protocol:** Studio Director **Imagine Agent Mode Handoff**  
**Canonical:** `references/agents/IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md`  
**CLI:** `imagine bridge` · `imagine agent-handoff` · `imagine verify`

## Model Layer (Grok 4.5 / v9-4p5)

| Task type | Preferred model | Reasoning |
|-----------|-----------------|-----------|
| Multi-agent orchestration / handoff synthesis | `grok-v9-4p5-multi` | high |
| Specialist deep craft / QA / identity-critical | `grok-v9-4p5-chat-expert` | high |
| Routine status / draft passes | `grok-4-auto` | medium |

**Stack default:** cinematic+Build API/chat **`grok-4.5`** (CLI ≥ 0.2.93 · fork `grok-build`). Opt-in 1M: `grok-4.3`.  
**Registry:** `tools/models.py` · `references/agents/MODEL_LAYER_v4.5.md` · `models verify`

```yaml
model_compatibility:
  - grok-v9-4p5-chat-expert
  - grok-v9-4p5-multi
  - grok-4-auto
preferred_model: grok-v9-4p5-chat-expert
```

### Imagine Video dual-path (when this skill touches video)
- **1.5 Native** — preferred for hero / final motion with audio when budget allows
- **1.0** — cost default / draft / pre-viz; label outputs so downstream agents do not assume 1.5 capabilities

## When to Activate

- No `XAI_API_KEY` but user will generate in Grok Imagine UI  
- Hero shot needs manual review before API spend  
- Client handoff: paste packet into grok.com/imagine  
- After `sfw plan` / `sequence add-clip` before web generation  
- User says: `ACTIVATE IMAGINE_BRIDGE`, `EXPORT IMAGINE PACKET`

Prefer full protocol when not web-only:

```
ACTIVATE IMAGINE_AGENT_MODE_HANDOFF
```

Begin: **"Preparing Imagine Bridge packet v3.8.5 (Grok 4.5 / v9-4p5)…"**

## Activation Stack

```
ACTIVATE IMAGINE_PROMPT_MASTER
ACTIVATE IMAGINE_BRIDGE
# Multi-surface (preferred):
ACTIVATE IMAGINE_AGENT_MODE_HANDOFF
```

## Packet Contents (Required)

Every bridge packet MUST include:

1. **`model_stack`** — chat/build `grok-4.5` unless 1M opt-in explicit  
2. **`VIDEO_PIPELINE_SPEC`** — from registry helpers (never invent slugs)  
3. **Prompt** — Ultimate Template body from Prompt Master  
4. **Reference hints** — `reference_image_id`, attach path, lock status  
5. **Sound Layer** — when video + audio path (`dialogue, SFX, ambience, music at t=…`)  
6. **Handoff steps** — numbered grok.com/imagine workflow  
7. **Return path** — where results re-enter QA / `sfw record` / artifacts  

For sequence clips also include **LAST_FRAME_RECAP** + **MOMENTUM_VECTOR** (and audio cue when 1.5).

**Video blocks** if I2V path: motion block + plate policy from I2V Specialist / Curator.

## CLI Workflow

```bash
python tools/cinematic_studio_cli.py imagine verify
python tools/cinematic_studio_cli.py imagine bridge --batch my-batch --shot shot_hero_001
python tools/cinematic_studio_cli.py imagine bridge --sequence "Act 1" --clip clip_002 --format clipboard
python tools/cinematic_studio_cli.py imagine workflow --batch my-batch

# Multi-surface (preferred when available)
python tools/cinematic_studio_cli.py imagine agent-handoff \
  --batch my-batch --shot shot_hero_001 --surface grok_com_imagine --format markdown
```

Formats: `--format clipboard` (single paste) · `markdown` (client docs) · `json` (automation).

## Workflow Loop

1. `imagine verify` — model preflight  
2. `sfw plan` or `sequence add-clip` — scaffold  
3. Specialists: DNA → Identity → Curator → Prompt → I2V (if video)  
4. `imagine bridge` — copy-paste packet  
5. User generates in grok.com/imagine  
6. `sfw record` / sequence log — QA + quota  
7. Continuity / Chain QA before extend  

## Hard Blocks

| Condition | Action |
|-----------|--------|
| Incomplete video packet (no pipeline / no plate policy) | Fix — no paste |
| Silent NSFW | Route ErosForge first |
| Invented model slugs | Rebuild from `models` helpers |
| Missing Sound Layer on 1.5 video | Add Sonic notes |

## Output Format

```text
IMAGINE BRIDGE PACKET · v3.7.1
Surface: grok_com_imagine
model_stack: grok-4.5 | VIDEO_PIPELINE_SPEC: 1.0|1.5
Shot/clip: …
Refs: locked|missing
Sound Layer: yes|n/a
Return path: …
Paste format: clipboard|markdown
Next: user generate → sfw record → QA
```

## Integration

| Partner | Role |
|---------|------|
| Studio Director | Owns multi-surface Agent Mode Handoff |
| Imagine Prompt Master | Prompt body |
| I2V Specialist | Motion block for video |
| Reference Curator | Plate tier + ref ids |
| Sonic Architect | Sound Layer for 1.5 |
| Handoff Packet Validator | JSON gate when exporting structured packets |
| Workflow Quota Optimizer | Cost note in packet |

## Reasoning (Grok 4.5)

| Task | Reasoning |
|------|-----------|
| Template fill | medium |
| Full production packet for web spend | **high** |
| Incomplete packet triage | **high** |

---

*Imagine Execution Bridge v3.8.5 — Grok 4.5 / v9-4p5 · grok.com/imagine subset · registry-locked specs*
