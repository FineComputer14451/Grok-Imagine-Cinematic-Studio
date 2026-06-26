---
description: Post-QA polish and delivery pipeline — upscale, EDL export, concat, and social crops for festival-ready output.
---

# Delivery Pipeline (Tier 2)

Polish and deliver QA-approved sequences after generation.

## Workflow

```
sequence run → qa-assist --apply → polish → edl → deliver
```

## Chain QA assist

```bash
python tools/cinematic_studio_cli.py sequence qa-assist "Act 1" --clip clip_002
python tools/cinematic_studio_cli.py sequence qa-assist "Act 1" --clip clip_002 --apply
python tools/cinematic_studio_cli.py sequence qa-assist "Intimate" --clip clip_002 --nsfw --apply
```

## Assembly EDL

```bash
python tools/cinematic_studio_cli.py sequence edl "Act 1"
python tools/cinematic_studio_cli.py sequence edl "Act 1" --output artifacts/edl/custom.json
```

## AI Polish

```bash
python tools/cinematic_studio_cli.py sequence polish "Act 1" --scale 2 --face-restore
python tools/cinematic_studio_cli.py sequence polish "Act 1" --dry-run
```

## Delivery

```bash
python tools/cinematic_studio_cli.py sequence deliver "Act 1" --formats 16:9,9:16,1:1
```

Requires `ffmpeg` on PATH. Outputs under `artifacts/delivery/{slug}/`.

## Animatic pre-vis

```bash
python tools/cinematic_studio_cli.py animatic plan "Act 1 Previs" \
  --beat "draft:Wide establish:6" --beat "hero:Anchor portrait:4"

python tools/cinematic_studio_cli.py animatic promote "act-1-previs" --frame frame_002 --tier hero
```

## Skills

- `assembly-editor`, `ai-polish-director`, `cinematic-ffmpeg`, `animatic-director`