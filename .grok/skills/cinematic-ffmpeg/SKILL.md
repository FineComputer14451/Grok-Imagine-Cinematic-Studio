---
name: cinematic-ffmpeg
description: Cinematic ffmpeg delivery toolkit for Grok Imagine Studio. Concatenates trims and social-crops polished clips after Assembly Editor and AI Polish Director. Activate when building delivery files muxing reels or exporting 9x16 1x1 and 16x9 variants. Uses Grok 4.5 orchestration.
---

# Cinematic FFmpeg v3.7.1 (Grok 4.5 · Delivery Toolkit)

**Tool skill** — post-polish technical assembly and platform export. Requires **`ffmpeg`** (and ideally **`ffprobe`**) on PATH. Orchestration is **Grok 4.5**; this skill does not spend Imagine API credits.

## Model Layer (Grok 4.5 · studio v3.7.1)

| Layer | Slug | When |
|-------|------|------|
| Orchestration (default) | `grok-4.5` | Concat, social crops, delivery packages |
| Long-context (opt-in) | `grok-4.3` | Rare — huge multi-reel manifests only |
| Grok Build CLI | `grok-4.5` · `grok-build` | Skills / coding (≥ 0.2.93) |
| Imagine Video | `grok-imagine-video` / `1.5` | 1.0 cost · 1.5 native audio |
| Imagine Image | `grok-imagine-image` / quality | Stills / hero plates |

Prefer stable `prompt_cache_key` on multi-turn `grok-4.5` loops. Reasoning **medium** for routine concat/crop; **high** if EDL timing, multi-format packages, or re-encode quality tradeoffs are non-trivial. Opt into `grok-4.3` only for 1M. Imagine tools are not used here. Registry: `tools/models.py` · `references/agents/MODEL_LAYER_v3.7.1.md` · `models verify`.

## When to Activate

- After **Assembly Editor** EDL is approved  
- After **AI Polish Director** writes polished masters  
- Building rough cuts, reels, or multi-aspect social packages  
- Before platform upload / client delivery  
- User says: `ACTIVATE CINEMATIC_FFMPEG`, `BUILD DELIVERY`, `EXPORT SOCIAL CROPS`, `CONCAT POLISHED REEL`

## When NOT to Use

| Situation | Instead |
|-----------|---------|
| Unpolished / No-Go clips | QA + AI Polish first |
| Re-generate story content | Studio / Sequence Director |
| Upscale / face restore | `ai-polish-director` / `ai-video-upscaler` |
| Subtitle burn-in design | Localization Specialist (then mux here if needed) |

## Pipeline Position

```
QA Go → Color Grade → AI Polish → Assembly EDL
  → Cinematic FFmpeg (this skill)
  → Studio Director sign-off / client handoff
```

## Prerequisites

```bash
command -v ffmpeg && ffmpeg -version | head -1
# optional: command -v ffprobe
chmod +x .grok/skills/cinematic-ffmpeg/scripts/*.sh
```

Install on Debian/Kali: `sudo apt-get install -y ffmpeg`

## Scripts

All paths relative to **repo root**. Prefer stream-copy (`-c copy`) when possible to avoid quality loss.

### 1. Concatenate polished clips (rough cut / reel)

Sorts `*.mp4` / `*.mov` in the input directory and concat-demuxes:

```bash
bash .grok/skills/cinematic-ffmpeg/scripts/concat_clips.sh \
  artifacts/polished/<slug>/ \
  artifacts/delivery/<slug>/rough_cut.mp4
```

### 2. Trim to EDL in/out

```bash
bash .grok/skills/cinematic-ffmpeg/scripts/trim_clip.sh \
  artifacts/polished/<slug>/clip_002_polished.mp4 \
  artifacts/delivery/<slug>/clip_002_trim.mp4 \
  0.5 8.0
# args: start_sec duration_sec
```

Tries stream-copy first; falls back to re-encode if needed.

### 3. Social crops

Aspect tokens use colons in **script args** (not skill frontmatter): `9:16` · `1:1` · `16:9`

```bash
bash .grok/skills/cinematic-ffmpeg/scripts/social_crop.sh \
  artifacts/delivery/<slug>/rough_cut.mp4 \
  artifacts/delivery/<slug>/vertical_9x16.mp4 \
  9:16

bash .grok/skills/cinematic-ffmpeg/scripts/social_crop.sh \
  artifacts/delivery/<slug>/rough_cut.mp4 \
  artifacts/delivery/<slug>/square_1x1.mp4 \
  1:1

bash .grok/skills/cinematic-ffmpeg/scripts/social_crop.sh \
  artifacts/delivery/<slug>/rough_cut.mp4 \
  artifacts/delivery/<slug>/landscape_16x9.mp4 \
  16:9
```

## Studio CLI (preferred for sequences)

```bash
# After polish — multi-format package
python tools/cinematic_studio_cli.py sequence deliver "Act 1" --formats 16:9,9:16,1:1
python tools/cinematic_studio_cli.py sequence deliver "Act 1" --dry-run
```

Uses polished clips under the sequence slug and the same ffmpeg scripts when available (`tools/sequence_delivery.py`).

## Delivery Presets (quick)

| Package | Steps |
|---------|--------|
| **Web reel 16×9** | concat polished → optional pad via `16:9` crop script |
| **Stories / Reels 9×16** | concat or hero select → `social_crop.sh … 9:16` |
| **Feed square 1×1** | concat or hero → `social_crop.sh … 1:1` |
| **Festival master** | polish at festival preset first → concat with `-c copy` only if same codec/res |

## Delivery Checklist

1. [ ] Assembly Editor EDL applied (trim before concat if cut points required)  
2. [ ] All segments **QA Go** + **polished** (`artifacts/polished/…`)  
3. [ ] Concat → verify duration vs EDL target (`ffprobe`)  
4. [ ] Optional social crops per platform brief  
5. [ ] Audio present and in sync on masters  
6. [ ] Log Project Bible:  
    ```text
    [DELIVERY_MANIFEST: slug=…, rough_cut=…, formats=16x9+9x16+1x1, ffmpeg=stream_copy|reencode]
    ```  
7. [ ] Hand off to Studio Director / Localization if burn-in needed  

## Output Report

```text
CINEMATIC FFMPEG DELIVERY · v3.7.1
Inputs: <n clips / path>
Ops: <concat|trim|crop|sequence deliver>
Outputs:
  - artifacts/delivery/…
Duration check: <ok|mismatch …>
Codec: <copy|reencode>
Next: Studio Director sign-off | Localization | upload
```

## Integration

| Partner | Role |
|---------|------|
| Assembly Editor | EDL / cut order |
| AI Polish Director | Polished sources only |
| Localization Specialist | Subs / SDH before or after mux |
| Studio Director | Final package approval |
| GitHub Repo Manager | Do not commit large masters unless intentional |

**Never** concat unpolished or No-Go clips into delivery masters.

## Quality Bar

- Prefer **stream copy** for concat when all sources share codec/resolution/framerate  
- Re-encode only when trim/crop filters require it  
- Spot-check first/last frames and audio after every mux  
- Save under `artifacts/delivery/` — not inside skill directories  

## Reasoning (Grok 4.5)

| Task | Reasoning |
|------|-----------|
| Routine concat/crop | medium |
| Multi-format package / re-encode risk | **high** |

---

*Cinematic FFmpeg v3.7.1 — Grok 4.5 delivery toolkit · post-polish concat trim crop · sequence deliver*
