---
description: Imagine production slash command — preflight verify, plan-generate-QA workflow, batch and sequence execution, grok.com/imagine bridge handoff.
---

# Imagine Production (`/imagine`)

Full Imagine runtime for Grok Imagine Cinematic Studio — closes the planner-to-generation gap with API jobs, batch execution, sequence runs, and chat bridge handoffs.

## Preflight

1. **CLI available?**
   ```bash
   python tools/cinematic_studio_cli.py imagine --help
   python tools/cinematic_studio_cli.py imagine verify
   ```
2. **API key** — `export XAI_API_KEY=...` (omit for dry-run mock mode)
3. **Activate skills:** `imagine-prompt-master`, `imagine-execution-bridge`, `studio-director` (Imagine Agent Mode Handoff), `sfw-batch-orchestrator`, `reference-asset-curator`, `image-to-video-specialist`, `chain-qa-protocol`. For **user-uploaded** still recreation / style transfer before i2v: `ai-image-recreation`.

## Plan → Generate → QA Loop

### 1. Preflight

```bash
python tools/cinematic_studio_cli.py imagine verify
python tools/cinematic_studio_cli.py models verify
```

### 2. Plan batch or sequence

```bash
python tools/cinematic_studio_cli.py sfw plan "Hero Session" \
  --shot "hero:Cover frame golden hour" \
  --shot "story_beat:Reveal beat" --budget 300

python tools/cinematic_studio_cli.py sequence init "Act 1" --duration 60
python tools/cinematic_studio_cli.py sequence add-clip "Act 1" \
  --prompt "Wide establishing..." --recap "Hero at window"
```

### 3. Workflow overview

```bash
python tools/cinematic_studio_cli.py imagine workflow --batch hero-session
python tools/cinematic_studio_cli.py imagine workflow --sequence "Act 1" --clip clip_001
```

### 4. Generate

```bash
# Batch shot (image / i2v / video per Reference Curator routing)
python tools/cinematic_studio_cli.py sfw run hero-session shot_hero_001
python tools/cinematic_studio_cli.py sfw run hero-session shot_hero_001 --dry-run

# Sequence clip (chain QA gate)
python tools/cinematic_studio_cli.py sequence run "Act 1" --clip clip_001

# Direct job submit
python tools/cinematic_studio_cli.py imagine submit video \
  --prompt "Slow dolly, rain-soaked alley" --duration 10
```

### 5. QA record

```bash
python tools/cinematic_studio_cli.py sfw record hero-session shot_hero_001 \
  --score 8.5 --credits 12

python tools/cinematic_studio_cli.py sfw promote hero-session shot_hero_001  # two-pass
```

### 6. Chat bridge (no API key) + Agent Mode Handoff (v3.7.1 / v3.9.0)

```bash
# Classic web UI bridge (surface: grok_com_imagine)
python tools/cinematic_studio_cli.py imagine bridge --batch hero-session --shot shot_hero_001
python tools/cinematic_studio_cli.py imagine bridge --sequence "Act 1" --clip clip_001 --format clipboard

# Official multi-surface Imagine Agent Mode Handoff (Studio Director protocol)
python tools/cinematic_studio_cli.py imagine agent-handoff \
  --batch hero-session --shot shot_hero_001 --surface grok_build_tools --format markdown
python tools/cinematic_studio_cli.py imagine agent-handoff \
  --sequence "Act 1" --clip clip_001 --surface grok_agent_acp --format json
```

Paste bridge output into [grok.com/imagine](https://grok.com/imagine). Use `agent-handoff` for Grok Build tools / ACP / API with full return_path + quota context.
## Job Queue

```bash
python tools/cinematic_studio_cli.py imagine list
python tools/cinematic_studio_cli.py imagine status job_20260626_120000_123456
python tools/cinematic_studio_cli.py imagine cancel job_20260626_120000_123456
```

## Web UI

Open **Imagine** page:

- **Job queue** — submit and track jobs
- **SFW plan** — batch planner with model routing
- **Batch execute** — pick shot, generate, preview, record QA
- **Reference plates** — register and lock plates for i2v
- **Sequence run** — clip runner with bridge preview
- **Delivery** — polish and EDL export

## Verification

- `imagine verify` reports compatible model stack and LIVE/DRY-RUN mode
- `sfw run` returns job ID + result URL
- `sfw record` updates batch status and quota reconciliation
- `imagine bridge` includes VIDEO_PIPELINE_SPEC + Sound Layer + reference hints
- Dashboard shows active Imagine jobs

## Summary

```
## Result
- **Action**: Imagine production
- **Mode**: live | dry-run | bridge
- **Target**: <batch/shot> | <sequence/clip>
- **Job**: <job_id>
- **QA**: pass | fail | pending
```