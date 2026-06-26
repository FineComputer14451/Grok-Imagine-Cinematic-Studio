---
name: handoff-packet-validator
description: Validates JSON handoff packets between Cinematic Studio agents including identity lock sequence extend and asset manifest entries. Run before activating downstream agents or extend generation. Use when validating handoff.json packets or debugging chain QA failures.
---

# Handoff Packet Validator v1.0

**Tool skill** — schema checks for agent handoff JSON.

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