---
name: ai-video-upscaler
description: AI video upscaling and face restoration for cinematic delivery. Upscale Grok Imagine 720p clips to 1080p or 4K with Real-ESRGAN GPU path or pure-Python fallback. Includes async batch processing and automatic face restoration. Activate for final delivery polish, upscale for festival submission, face restore on close-ups, or when AI Polish Director runs a polish pass.
---

# AI Video Upscaler

Upscale generated video clips for final delivery. Used by the **AI Polish Director** agent in the post-production pipeline.

## Prerequisites

```bash
# System dependencies
sudo apt-get install -y ffmpeg

# Python dependencies (GPU path)
pip install realesrgan basicsr gfpgan opencv-python-headless numpy pillow

# Install model weights (one-time)
bash scripts/install_models.sh
```

If GPU libraries are unavailable, the pure-Python fallback runs automatically.

## Quick Start

### Single clip (auto-detects GPU or fallback)

```bash
python scripts/ai_video_upscale.py \
  --input /path/to/source.mp4 \
  --output /path/to/upscaled.mp4 \
  --scale 2 \
  --face-restore
```

### Batch / async (directory of clips)

```bash
python scripts/ai_video_upscale_async.py \
  --input /path/to/clips/ \
  --output /path/to/polished/ \
  --scale 2 \
  --workers 4
```

### Force pure-Python fallback (no GPU models)

```bash
python scripts/ai_video_upscale_pure.py \
  --input /path/to/source.mp4 \
  --output /path/to/upscaled.mp4 \
  --scale 2
```

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--scale` | `2` | Upscale factor (2 = 720p→1440p, use 2 for 1080p delivery) |
| `--face-restore` | off | Enable GFPGAN face restoration on detected faces |
| `--model` | `realesrgan-x4plus` | Real-ESRGAN model name |
| `--workers` | `4` | Parallel frame workers (async mode only) |
| `--crf` | `18` | Output video quality (lower = better, 18–23 typical) |

## Workflow Integration

Run after QA Guardian approval and color grading:

1. `ACTIVATE AI_POLISH_DIRECTOR`
2. Install models if needed: `bash scripts/install_models.sh`
3. Upscale approved clips
4. Hand polished output to Studio Director for sign-off

## Output

- Upscaled MP4 with original audio preserved
- Console report: method used (GPU/fallback), resolution, frame count, elapsed time

Save all outputs to `artifacts/`.