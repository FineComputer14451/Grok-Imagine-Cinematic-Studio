---
name: ai-video-upscaler
description: AI video upscaling and face restoration for cinematic delivery. Upscale Grok Imagine 720p clips to 1080p or 4K with Real-ESRGAN GPU path or pure-Python fallback. Includes async batch processing and automatic face restoration. Activate for final delivery polish, upscale for festival submission, face restore on close-ups, or when AI Polish Director runs a polish pass. Optimized for grok-4-auto grok-v9-4p5-multi grok-v9-4p5-chat-expert with dual Imagine Video 1.0 and 1.5 Native.
---

# AI Video Upscaler v3.8.6 (Grok 4.6 / v9-4p5 · Local Upscale)

**Local delivery upscale** for Grok Imagine 720p masters. Used by **AI Polish Director** after QA Go and color grade. This is **not** Imagine API spend — orchestration plans on `grok-4.5`; pixels run on GPU/CPU scripts.

**Skill scripts:** `.grok/skills/ai-video-upscaler/scripts/`  
**Agent:** `ai-polish-director` · CLI: `sequence polish`

## Model Layer (Grok 4.6 / v9-4p5)

| Task type | Preferred model | Reasoning |
|-----------|-----------------|-----------|
| Multi-agent orchestration / handoff synthesis | `grok-v9-4p5-multi` | high |
| Specialist deep craft / QA / identity-critical | `grok-v9-4p5-chat-expert` | high |
| Routine status / draft passes | `grok-4-auto` | medium |

**Stack default:** cinematic+Build API/chat **`grok-4.6`** (CLI ≥ 1.0.5 · fork `grok-build` or `grok-4.6`; `grok-4.5` aliases wrap 4.6). Opt-in 1M: `grok-4.3`.  
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

- Final delivery 1080p / 4K-class from native 720p  
- Face restore on character close-ups  
- Festival / client masters after grade  
- User says: `UPSCALE FOR DELIVERY`, `FACE RESTORE PASS`, `RUN FINAL POLISH PASS` (via AI Polish Director)

Begin: **"Initiating Local Upscale Protocol v3.8.6 (Grok 4.6 / v9-4p5)…"**

## Prerequisites

```bash
sudo apt-get install -y ffmpeg
pip install realesrgan basicsr gfpgan opencv-python-headless numpy pillow
bash .grok/skills/ai-video-upscaler/scripts/install_models.sh
```

If GPU libraries are unavailable, pure-Python fallback runs automatically.

## Quick Start

### Prefer sequence CLI (when sequence exists)

```bash
python tools/cinematic_studio_cli.py sequence polish "Act 1" --scale 2 --face-restore
python tools/cinematic_studio_cli.py sequence polish "Act 1" --dry-run
```

### Single clip

```bash
python .grok/skills/ai-video-upscaler/scripts/ai_video_upscale.py \
  --input artifacts/source_clip.mp4 \
  --output artifacts/polished/clip.mp4 \
  --scale 2 --face-restore
```

### Batch / async

```bash
python .grok/skills/ai-video-upscaler/scripts/ai_video_upscale_async.py \
  --input artifacts/clips/ --output artifacts/polished/ \
  --scale 2 --workers 4
```

### Force pure-Python fallback

```bash
python .grok/skills/ai-video-upscaler/scripts/ai_video_upscale_pure.py \
  --input artifacts/source_clip.mp4 \
  --output artifacts/polished/clip.mp4 --scale 2
```

## Options

| Flag | Default | Notes |
|------|---------|--------|
| `--scale` | `2` | 2× typical for 720p→~1440p / 1080p-class delivery |
| `--face-restore` | off | GFPGAN on detected faces — **high reasoning** if identity-critical |
| `--model` | `realesrgan-x4plus` | Real-ESRGAN model name |
| `--workers` | `4` | Async only |
| `--crf` | `18` | Encode quality (18–23 typical) |

## Workflow Integration

1. QA Guardian **Go** (and color grade or Director waiver)  
2. `ACTIVATE AI_POLISH_DIRECTOR`  
3. Install models if needed  
4. Upscale approved clips only (never No-Go sources)  
5. Spot-check faces vs DNA anchors after face-restore  
6. Studio Director sign-off → `sequence deliver` / `cinematic-ffmpeg`  

Log `[POLISH_SPEC: …]` in Project Bible.

## Identity-Safe Face Restore

- Prefer face-restore on hero close-ups only when needed  
- After restore, Identity Lock spot-check: eyes, freckles, scars, hairline  
- If restore morphs identity → disable face-restore, re-upscale, or re-gen still  

## Output

- Upscaled MP4 with original audio preserved  
- Console report: method (GPU/fallback), resolution, frames, elapsed  
- Save under `artifacts/polished/`  

## Output Format

```text
UPSCALE COMPLETE · v3.7.1
Method: GPU|fallback | Scale: 2 | Face restore: on|off
Input: … → Output: artifacts/polished/…
Identity check: pass|recheck
Next: cinematic-ffmpeg | Studio sign-off | re-run without face-restore
```

## Hard Blocks

| Condition | Action |
|-----------|--------|
| Source not QA Go | Reject |
| Face-restore morphs DNA | Disable FR or re-gen plate |
| Missing ffmpeg | Install before batch |

## Reasoning (Grok 4.6)

| Task | Reasoning |
|------|-----------|
| Routine 2× batch | medium |
| Face restore / 4K hero | **high** |
| Path select GPU vs pure | medium–high |

---

*AI Video Upscaler v3.8.6 — Grok 4.6 / v9-4p5 orchestration · local GPU/CPU · not Imagine spend*
