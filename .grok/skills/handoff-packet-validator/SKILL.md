---
name: handoff-packet-validator
description: Validates JSON handoff packets between Cinematic Studio agents including identity lock sequence extend and asset manifest entries. Run before activating downstream agents or extend generation. Use when validating handoff.json packets or debugging chain QA failures.
---

# Handoff Packet Validator v1.0

**Tool skill** — schema checks for agent handoff JSON.


## Model Layer (Grok 4.5 · studio v3.6.7)

| Layer | Slug | When |
|-------|------|------|
| Orchestration (default) | `grok-4.5` | Bibles, direction, agent loops |
| Long-context (opt-in) | `grok-4.3` | 1M memory banks (`--chat-model grok-4.3`) |
| Grok Build CLI | `grok-4.5` · `grok-build` | Skills / coding (≥ 0.2.93) |
| Imagine Video | `grok-imagine-video` / `1.5` | 1.0 cost · 1.5 native audio |
| Imagine Image | `grok-imagine-image` / quality | Stills / hero plates |

Prefer stable `prompt_cache_key` on multi-turn `grok-4.5` loops. Full stack: `references/agents/MODEL_LAYER_v3.6.7.md` · `tools/models.py`.

## Supported Packet Types

| `packet_type` | Used by |
|---------------|---------|
| `identity_lock_handoff` | Character DNA Extractor → Identity Lock |
| `sequence_extend_handoff` | Cinematic Sequence Extender → next clip |
| `asset_manifest_entry` | Reference & Asset Curator |

## CLI

```bash
python .grok/skills/handoff-packet-validator/scripts/validate_handoff.py handoff.json
python .grok/skills/handoff-packet-validator/scripts/validate_handoff.py characters/hero-slug/handoff.json
```

Exit `0` = valid · Exit `1` = validation errors · Exit `2` = usage/file error

## When to Run

- After `dna handoff` or `sequence handoff` CLI commands
- Before `ACTIVATE I2V_SPECIALIST` on a chained clip
- When chain QA fails on `last_frame_continuity` or `momentum_carryover`

## Generate Valid Handoffs

```bash
python tools/cinematic_studio_cli.py dna handoff "Character Name"
python tools/cinematic_studio_cli.py sequence handoff "Sequence Name" --clip clip_001
```

## Integration

- **chain-qa-protocol** — validate before scoring
- **image-to-video-specialist** — require locked `asset_manifest_entry`
- **Studio Director** — block downstream activation on invalid packets