---
description: Activate Grok Imagine Cinematic Studio v3.6.7 with the full 23-agent production suite, dual model stack, and native Imagine Video 1.0/1.5 pipeline.
---

# Activate Cinematic Studio

Start a full multi-agent cinematic production session with dual Grok 4.5 Build + Grok 4.3 cinematic stack, Character DNA, sequence extension, quota-aware orchestration, and optional guided Production Bible wizard.

## Preflight

1. **Plugin installed?** — Confirm the Cinematic Studio plugin is available:
   ```bash
   grok plugin details grok-imagine-cinematic-studio
   ```
   If missing: `grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio --trust`  
   If outdated: `grok plugin update` (or update the install id from `grok plugin list`)
2. **Repo context** — If working from a clone, ensure `references/agents/` and `.grok/skills/` are present.
3. **Project brief** — If "$ARGUMENTS" is non-empty, treat it as the user's story or project title. Otherwise ask for a one-paragraph cinematic vision before proceeding.

## Plan

1. Activate the `grok-imagine-cinematic-studio` skill (read its SKILL.md if not already loaded).
2. Engage **Studio Director** + **Mega Production Architect** as primary orchestrators.
3. Lock `VIDEO_PIPELINE_SPEC` (1.0 cost default, or 1.5 with native audio when needed; 720p, 6–15s clips, extend/stitch strategy).
4. If the user provided "$ARGUMENTS", scaffold a Production Bible outline and propose the first 3 production phases.
5. Optional: `create-bible --wizard` (TTY) or Web UI Guided Bible Creator for multi-step Bible capture.

State the activation phrase explicitly:

> **Activate Grok Imagine Cinematic Studio v3.6.7**

## Commands

### Studio status (optional CLI)

```bash
python tools/cinematic_studio_cli.py status
python tools/cinematic_studio_cli.py models verify
```

### Production Bible

```bash
python tools/cinematic_studio_cli.py create-bible "Project Title" --genre "Sci-Fi"
python tools/cinematic_studio_cli.py create-bible --wizard   # guided TTY only
```

### Generate activation prompt (optional)

```bash
python tools/cinematic_studio_cli.py generate-prompt "$ARGUMENTS" \
  --chat-model grok-4.3 --video-model grok-imagine-video
```

### Specialist activations (use as needed)

- `ACTIVATE IMAGINE_VIDEO_1.5_FULL` — full native 1.5 video + audio mode
- `ACTIVATE CHARACTER_DNA_EXTRACTOR` — DNA extraction and Identity Lock
- `ACTIVATE NSFW_QUOTA_ORCHESTRATOR` — Heavy batch planning (explicit opt-in only)
- `ACTIVATE AI_POLISH_DIRECTOR` — final delivery upscale pass

## Verification

Confirm the session is in studio mode:

- Studio Director acknowledges the project brief and names the active agent roster.
- `VIDEO_PIPELINE_SPEC` is stated (model, resolution, clip length, native_audio).
- Model stack noted: cinematic `grok-4.3`, Build/coding `grok-4.5`, CLI ≥ 0.2.93.
- Next concrete action is proposed (Bible, DNA, or first clip plan).

## Summary

```
## Result
- **Action**: Cinematic Studio v3.6.7 activated
- **Status**: success
- **Project**: <title or brief from $ARGUMENTS>
- **Pipeline**: Imagine Video 1.0 default / 1.5 when native audio
- **Stack**: grok-4.3 cinematic + grok-4.5 Build
- **Agents**: 23 core (+ ErosForge opt-in)
```

## Next Steps

- Run `/dna` to onboard recurring characters before long sequences.
- Run `/quota` to estimate credits before generation.
- Run `/validate` before client delivery or extension final stitch.
