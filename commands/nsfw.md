---
description: Activate ErosForge NSFW pipeline with quota-aware batch planning, model routing, chain QA, and sensual sequence extension on SuperGrok Heavy.
---

# NSFW Production (Opt-in)

Start an explicit opt-in NSFW session with ErosForge, NSFW Quota Orchestrator, Reference Curator model routing, and NSFW Sequence Extender.

**Requires explicit user consent.** Do not activate without clear opt-in.

## Preflight

1. **Confirm opt-in** — User must explicitly request NSFW/erotic production.
2. **CLI available?**
   ```bash
   python tools/cinematic_studio_cli.py nsfw --help
   python tools/cinematic_studio_cli.py nsfw extend --help
   ```
3. **Parameters** — Parse "$ARGUMENTS" for optional batch title or sequence name.
4. **Activate skills:** `erosforge-nsfw-director`, `nsfw-quota-orchestrator`, `nsfw-sequence-extender`, `nsfw-chain-qa-protocol`.

State the activation phrase:

> **ACTIVATE EROSFORGE** → **ACTIVATE NSFW_QUOTA_ORCHESTRATOR**

## Plan

1. Engage **ErosForge NSFW Director** for scene design and intimacy physics.
2. Run **Reference Curator** NSFW tier routing (hero/anchor/key_explicit → Image 2.0 `quality=medium` + video 1.5).
3. Plan batch under Heavy daily cap with 15% retry reserve.
4. If "$ARGUMENTS" includes a sequence name, scaffold NSFW extension with tension profile.

## Commands

### Plan NSFW batch

```bash
python tools/cinematic_studio_cli.py nsfw plan "Session Title" \
  --shot "hero:Cover frame candlelit embrace" \
  --shot "consistency_anchor:Identity lock close-up" \
  --shot "key_explicit:high:Primary intimate beat" \
  --budget 800
```

### Next shots in queue

```bash
python tools/cinematic_studio_cli.py nsfw next "session-slug" --count 3
```

### i2v decision + retry

```bash
python tools/cinematic_studio_cli.py nsfw decide "session-slug" --shot shot_001
python tools/cinematic_studio_cli.py nsfw retry "session-slug" --shot shot_001 --reason identity_drift
```

### Daily quota report

```bash
python tools/cinematic_studio_cli.py nsfw report
```

### NSFW sequence extension

```bash
python tools/cinematic_studio_cli.py nsfw extend plan "Intimate Sequence" \
  --duration 90 --profile passionate
```

### NSFW chain QA (before every extend)

```bash
python tools/cinematic_studio_cli.py nsfw extend qa "Intimate Sequence" --clip clip_002
```

## Verification

- ErosForge acknowledges artistic justification and post-scene state tracking.
- Batch plan shows per-shot `image_model`, `video_model`, and `asset_tier`.
- NSFW chain QA scaffold runs before extension approval.
- Daily report reflects credits vs quality when session completes.

## Summary

```
## Result
- **Action**: NSFW pipeline activated (opt-in)
- **Status**: success
- **Session**: <title from $ARGUMENTS or TBD>
- **Routing**: Reference Curator NSFW tier map
- **Agents**: ErosForge + NSFW Quota Orchestrator (+ Sequence Extender if long-form)
```

## Next Steps

- Run `/quota` to confirm Heavy budget headroom.
- Run `/dna` for Character DNA before consistency anchors.
- Run `/validate` on intimacy handoff packets before extend.