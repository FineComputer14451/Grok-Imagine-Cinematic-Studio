---
description: Submit and track Imagine API generation jobs, reference plates, and sequence clip runs with chain QA gates.
---

# Imagine Production

Bridge the studio planner to live xAI Imagine generation — image, video, job queue, and `sequence run`.

## Preflight

```bash
python tools/cinematic_studio_cli.py imagine --help
python tools/cinematic_studio_cli.py sequence run --help
export XAI_API_KEY=...   # omit for dry-run mock mode
```

## Job queue

```bash
python tools/cinematic_studio_cli.py imagine submit video \
  --prompt "Slow dolly through rain-soaked alley, neon reflections" \
  --duration 10

python tools/cinematic_studio_cli.py imagine list
python tools/cinematic_studio_cli.py imagine status job_20260626_120000_123456
```

## Sequence run (with chain QA)

```bash
python tools/cinematic_studio_cli.py sequence init "Act 1" --duration 60
python tools/cinematic_studio_cli.py sequence add-clip "Act 1" \
  --prompt "Wide establishing shot..." --recap "Hero at window, rain on glass"

python tools/cinematic_studio_cli.py sequence run "Act 1" --clip clip_001
# Dry-run without API key:
python tools/cinematic_studio_cli.py sequence run "Act 1" --clip clip_001 --dry-run
```

`no_go` chain QA blocks extension to the next clip until resolved.

## Web UI

Open **Imagine** page: job queue, SFW batch planner, reference plates, sequence run.

## Skills

- `sfw-batch-orchestrator`
- `reference-asset-curator`
- `image-to-video-specialist`
- `chain-qa-protocol`