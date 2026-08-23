# AI Polish Delivery Presets v3.7.1

Use with **AI Polish Director**. Orchestration: Grok 4.6. Execution: `ai-video-upscaler` / `sequence polish`.

Native Imagine masters are typically **720p**. Presets target delivery class without re-grading.

## Preset table

| Preset | `--scale` | Face restore | CRF | When |
|--------|-----------|--------------|-----|------|
| `1080p_web` | 2 | Heroes / CU only | 18–20 | Default client, web, review |
| `4k_festival` | 4 (or 2 if artifacts) | On for CU/MCU | 16–18 | Festival, master archive |
| `social_safe` | 2 | Off unless true CU | 20–22 | Before 9:16 / 1:1 crops |
| `hero_only` | 2 | On | 18 | Quota/compute limited |

## POLISH_SPEC line (Project Bible)

```text
[POLISH_SPEC: preset=1080p_web, scale=2, face_restore=auto_hero, method=gpu, crf=18, sequence="Act 1"]
```

## Method selection

| Environment | Method |
|-------------|--------|
| CUDA + realesrgan + models installed | GPU (`ai_video_upscale.py`) |
| No GPU / missing models | Pure-Python (`ai_video_upscale_pure.py`) or script auto-fallback |
| Sequence under studio CLI | `sequence polish` → upscaler script |
| Dry plan | `--dry-run` (copy/placeholder + manifest) |

## Face restore policy

- **On:** MCU/CU heroes, identity-critical, trailer faces  
- **Off:** wide, crowd, VFX-heavy, no readable faces  
- **Auto:** CLI enables face-restore when `clip.hero_shot` is true even if global flag is mixed — prefer explicit hero list

## Failure playbook

1. Halo / plastic skin → drop scale 4→2, disable face-restore, re-inspect  
2. Flicker → pure path or re-gen source; do not force festival scale  
3. Grade shift → Color Grading Supervisor (do not over-sharpen to “fix”)  
4. Identity drift → Identity Lock; new plate if needed  
5. Root motion fail → Sequence / Studio Director re-gen — **no polish**

## Post-polish delivery

```bash
python tools/cinematic_studio_cli.py sequence deliver "Act 1" --formats 16:9,9:16,1:1
```

Or `cinematic-ffmpeg` concat/crop scripts on `artifacts/polished/`.
