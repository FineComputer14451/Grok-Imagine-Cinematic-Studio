---
name: imagine-execution-bridge
description: Grok chat to grok.com/imagine handoff bridge for Grok Imagine Cinematic Studio. Emits copy-paste VIDEO_PIPELINE_SPEC reference hints and native audio Sound Layer blocks when API generation is unavailable. Activate with ACTIVATE IMAGINE_BRIDGE or when user needs grok.com/imagine copy-paste packets.
---

# Imagine Execution Bridge v1.0

**Pairs with:** `imagine-prompt-master`, `image-to-video-specialist`, `reference-asset-curator`

When the studio runs inside Grok chat (not xAI API), this bridge emits **copy-paste-ready** Imagine prompts for [grok.com/imagine](https://grok.com/imagine).

## Activation

`ACTIVATE IMAGINE_BRIDGE`

```
ACTIVATE IMAGINE_PROMPT_MASTER
ACTIVATE IMAGINE_BRIDGE
```

## When to Use

- User has no `XAI_API_KEY` but wants to generate in Grok Imagine UI
- Hero shot needs manual review before API spend
- Client handoff: paste packet into grok.com/imagine
- After `sfw plan` or `sequence add-clip` — bridge before `sfw run`

## CLI

```bash
python tools/cinematic_studio_cli.py imagine verify
python tools/cinematic_studio_cli.py imagine bridge --batch my-batch --shot shot_hero_001
python tools/cinematic_studio_cli.py imagine bridge --sequence "Act 1" --clip clip_002 --format clipboard
python tools/cinematic_studio_cli.py imagine workflow --batch my-batch
```

## Packet Contents (Required)

Every bridge packet MUST include:

1. **VIDEO_PIPELINE_SPEC** — `grok-imagine-video-1.5`, 720p, `native_audio=true`
2. **Prompt** — Ultimate Template body from Imagine Prompt Master
3. **Reference hints** — `reference_image_id`, attach URL, lock status
4. **Sound Layer** — `Sound Layer: dialogue, SFX, ambience, music cue at t=Xs`
5. **Handoff steps** — numbered grok.com/imagine workflow

For sequence clips also include **LAST_FRAME_RECAP** and **MOMENTUM_VECTOR**.

## Workflow Loop

1. `imagine verify` — model preflight
2. `sfw plan` or `sequence add-clip` — scaffold
3. `imagine bridge` — copy-paste packet
4. User generates in grok.com/imagine
5. `sfw record` or `sequence run` — log QA + quota

## Output Format

Prefer `--format clipboard` for single-block paste. Use `--format markdown` for client docs.

Never omit native audio Sound Layer on video prompts.