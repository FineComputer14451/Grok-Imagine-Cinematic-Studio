---
name: cinematic-ffmpeg
description: Cinematic ffmpeg delivery toolkit for Grok Imagine Studio. Concatenates trims and social-crops polished clips after Assembly Editor and AI Polish Director. Activate when building delivery files muxing reels or exporting 9:16 1:1 and 16:9 variants.
---

# Cinematic FFmpeg v1.0

**Tool skill** — post-polish technical assembly. Requires `ffmpeg` on PATH.

## When to Activate

- After **Assembly Editor** EDL is approved
- After **AI Polish Director** outputs polished clips
- Before platform upload or client delivery

## Scripts

Make executable once:
```bash
chmod +x .grok/skills/cinematic-ffmpeg/scripts/*.sh
```

### Concatenate polished sequence (rough cut / reel)

```bash
bash .grok/skills/cinematic-ffmpeg/scripts/concat_clips.sh \
  artifacts/polished/ artifacts/delivery/rough_cut.mp4
```

### Trim clip to EDL in/out

```bash
bash .grok/skills/cinematic-ffmpeg/scripts/trim_clip.sh \
  artifacts/polished/clip_002.mp4 artifacts/delivery/clip_002_trim.mp4 0.5 8.0
```

### Social crops

```bash
bash .grok/skills/cinematic-ffmpeg/scripts/social_crop.sh \
  artifacts/delivery/rough_cut.mp4 artifacts/delivery/vertical.mp4 9:16
bash .grok/skills/cinematic-ffmpeg/scripts/social_crop.sh \
  artifacts/delivery/rough_cut.mp4 artifacts/delivery/square.mp4 1:1
```

## Delivery Checklist

1. Assembly Editor EDL applied (trim before concat if needed)
2. All segments QA Go + polished
3. Concat → verify duration vs EDL target
4. Optional social crops per platform brief
5. Log paths in Project Bible `[DELIVERY_MANIFEST: ...]`

## Integration

- **Upstream:** Assembly Editor, AI Polish Director (`ai-polish-director`)
- **Downstream:** Localization Specialist (burn-in subs), client handoff
- **Never:** Concat unpolished or No-Go clips into delivery masters