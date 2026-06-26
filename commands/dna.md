---
description: Character DNA workflow — extract, save, lock identity, and inject prompt blocks for Grok Imagine consistency.
---

# Character DNA

Manage Character DNA profiles for visual identity lock across images and Imagine Video 1.5 clips.

## Preflight

1. **CLI available?** — From the repo root:
   ```bash
   python tools/cinematic_studio_cli.py dna --help
   ```
2. **Character context** — If "$ARGUMENTS" names a character, use it. Otherwise list existing profiles first.
3. **Reference images** — If the user uploaded reference stills, activate `character-dna-extractor` for forensic extraction before manual scaffold edits.

## Plan

1. List existing DNA profiles.
2. If "$ARGUMENTS" is provided:
   - **Existing character** → show profile, offer lock + inject.
   - **New character** → scaffold DNA from user description or reference analysis.
3. Propose Identity Lock handoff when the profile is production-ready.

## Commands

### List profiles

```bash
python tools/cinematic_studio_cli.py dna list
```

### Initialize new DNA (when "$ARGUMENTS" is a new name)

```bash
python tools/cinematic_studio_cli.py dna init "$ARGUMENTS" \
  --core "Core identity traits" \
  --facial "Facial structure, eyes, skin tone" \
  --hair "Hair and grooming"
```

### Show and lock existing profile

```bash
python tools/cinematic_studio_cli.py dna show "$ARGUMENTS"
python tools/cinematic_studio_cli.py dna lock "$ARGUMENTS"
```

### Generate injectable prompt block

```bash
python tools/cinematic_studio_cli.py dna inject "$ARGUMENTS" --mode cinematic
```

Modes: `cinematic`, `compact`, `close_up`, `sequence_starter`, `video_1.5`

### Identity Lock handoff packet

```bash
python tools/cinematic_studio_cli.py dna handoff "$ARGUMENTS"
```

## Verification

- `dna list` shows the character with expected status.
- After lock, project state includes the character in `identity_lock`.
- Inject output contains DNA blocks suitable for Imagine 1.5 prompts.

## Summary

```
## Result
- **Action**: Character DNA workflow
- **Status**: success | partial | failed
- **Character**: <name from $ARGUMENTS or newly created>
- **Profiles**: <count>
- **Identity Locked**: yes | no
```

## Next Steps

- Use injected blocks in `/cinematic` production prompts or sequence extend chains.
- Run `/validate` before long sequences with recurring characters.
- Activate `identity-lock-specialist` if drift appears across clips.