---
name: imagine-model-overrides
description: >-
  Select and pin Grok Imagine image/video model overrides for grok.com/imagine
  and Studio handoffs. Use when choosing Quality vs Fast, Image 2.0 vs 1.0,
  Video 1.5 vs 1.0, legacy quality redirects, or when emitting model_stack /
  VIDEO_PIPELINE_SPEC for paste packets. Activate with ACTIVATE IMAGINE_MODEL_OVERRIDES
  or /imagine-model-overrides.
when-to-use: >-
  ACTIVATE IMAGINE_MODEL_OVERRIDES; override Imagine models; Quality Mode;
  Fast Mode; Image 2.0; Video 1.5; model_stack; pin imagine image/video model;
  grok.com/imagine model pick
argument-hint: "[preset|image-slug|video-slug]"
user-invocable: true
metadata:
  author: FineComputer14451
  short-description: Pin Imagine image/video models for grok.com/imagine
---

# Imagine Model Overrides

Canonical **select + pin** skill for Imagine models on [grok.com/imagine](https://grok.com/imagine) and Studio handoffs to surface `grok_com_imagine`.

Aligned with **Grok Imagine Cinematic Studio** `tools/models.py` (v3.11.4+) and xAI docs pricing table (Sep 2026).

Begin: **"Imagine model overrides locked…"** then emit the chosen preset.


## Model Layer (Grok 4.6 / v9-4p5)

| Task type | Preferred model | Reasoning |
|-----------|-----------------|-----------|
| Model pin / handoff synthesis | `grok-v9-4p5-chat-expert` | high |
| Multi-agent routing of presets | `grok-v9-4p5-multi` | high |
| Quick preset refresh | `grok-4-auto` | medium |

```yaml
model_compatibility:
  - grok-v9-4p5-chat-expert
  - grok-v9-4p5-multi
  - grok-4-auto
preferred_model: grok-v9-4p5-chat-expert
```

## Hard rules

1. **Never invent model slugs.** Only use the catalog below.
2. **There is no Video 2.0.** Video choices are `grok-imagine-video` (1.0) or `grok-imagine-video-1.5`.
3. **Hero stills** use Image **2.0** (`grok-imagine-image-2.0`) = grok.com/imagine **Quality Mode**.
4. **Draft / volume stills** use Image **1.0** (`grok-imagine-image`) = **Fast Mode**.
5. Legacy `grok-imagine-image-quality` **retires 2026-11-02** → rewrite to `grok-imagine-image-2.0` with `quality=low`.
6. **Edit / extend video** must stay on Video **1.0** (`grok-imagine-video`). Do not send 1.5 for edit/extend.
7. On surface **C** (`grok_com_imagine`), speak in UI terms (Quality / Fast / Video 1.5) and keep paste packets plain-text friendly.

## Catalog (canonical)

### Image

| Slug | UI / role | Notes |
|------|-----------|-------|
| `grok-imagine-image-2.0` | **Quality Mode** · hero | `quality`: `low` \| `medium` \| `auto` (default auto). Up to **5** edit refs. |
| `grok-imagine-image` | **Fast Mode** · default draft | Cheaper volume stills. Up to **3** edit refs. |
| `grok-imagine-image-quality` | Legacy Quality | **Deprecated.** Redirect → `grok-imagine-image-2.0` + `quality=low`. |

Aliases → 2.0: `2.0`, `image-2.0`, `imagine-image-2.0`, `hero`, `quality-mode`  
Aliases → 1.0: `1.0`, `image`, `fast`, `fast-mode`, `draft`  
Aliases → legacy (then redirect): `quality`, `pro`, `image-quality`

### Video

| Slug | UI / role | Notes |
|------|-----------|-------|
| `grok-imagine-video` | Video **1.0** · cost default | Silent. **Required** for edit + extend. Max 720p. |
| `grok-imagine-video-1.5` | Video **1.5 Native** | Native audio. Prefer for final motion / Sound Layer. 1080p on t2v/i2v. |

Aliases → 1.0: `1.0`, `video`, `edit-extend`  
Aliases → 1.5: `1.5`, `native-audio`, `video-1.5`

## Presets (select these)

| Preset id | Image | Video | When |
|-----------|-------|-------|------|
| `hero` | `grok-imagine-image-2.0` (`quality=medium`) | `grok-imagine-video-1.5` | Final plates + final motion with audio |
| `balanced` | `grok-imagine-image-2.0` (`quality=auto`) | `grok-imagine-video` | Hero stills, cost-aware video |
| `draft` | `grok-imagine-image` | `grok-imagine-video` | Volume / pre-viz / quota save |
| `audio-final` | `grok-imagine-image-2.0` (`quality=medium`) | `grok-imagine-video-1.5` | Locked plate → i2v with Sound Layer |
| `edit-extend` | (n/a or keep current plate) | `grok-imagine-video` | Video edit or extend only |

Default when user is vague: **`balanced`**.

## Activation

```text
ACTIVATE IMAGINE_MODEL_OVERRIDES
ACTIVATE IMAGINE_MODEL_OVERRIDES hero
ACTIVATE IMAGINE_MODEL_OVERRIDES draft
/imagine-model-overrides balanced
```

Also fire when the user asks to override / pin / select Imagine models for grok.com/imagine.

## What to emit

### A) Model stack block (always)

```yaml
model_stack:
  imagine_image: <slug>
  image_quality: <low|medium|auto|null>   # only for 2.0; null for 1.0
  imagine_video: <slug>
  ui_image_mode: Quality Mode | Fast Mode
  ui_video_note: Video 1.0 | Video 1.5 Native
  preset: <preset id>
```

### B) grok.com/imagine paste steps (surface C)

```text
=== IMAGINE MODEL OVERRIDE (grok.com/imagine) ===
Preset: <id>
Image UI: <Quality Mode | Fast Mode>  →  <slug>  [quality=<…>]
Video UI: <Video 1.0 | Video 1.5 Native>  →  <slug>

Steps:
1. Open https://grok.com/imagine
2. For stills: select <Quality Mode | Fast Mode> before generate
3. For video: prefer <1.0 | 1.5>; if native audio / Sound Layer needed → 1.5
4. Edit or extend a clip → stay on Video 1.0
5. After generate, save result and return to Studio / record path

Do not invent other model names in the UI.
=== END OVERRIDE ===
```

### C) VIDEO_PIPELINE_SPEC (when video)

**1.0**
```text
[VIDEO_PIPELINE_SPEC: model="grok-imagine-video", version="1.0", resolution="720p", clip_length="8-12s preferred", native_audio=false, reference_image_fidelity=high, extend_protocol="LAST_FRAME + MOTION_VECTOR", stitch_priority=high, audio_momentum=false]
```

**1.5**
```text
[VIDEO_PIPELINE_SPEC: model="grok-imagine-video-1.5", version="1.5", resolution="720p", clip_length="8-12s preferred", native_audio=true, reference_image_fidelity=high, extend_protocol="LAST_FRAME + MOTION_VECTOR + AUDIO_CUE", stitch_priority=high, audio_momentum=true]
```

## Decision cheat sheet

| User says… | Pin |
|------------|-----|
| Quality / hero / sharp text / typography | Image 2.0 + `quality=medium` |
| Fast / cheap / many drafts | Image 1.0 |
| Native audio / lip sync / Sound Layer | Video 1.5 |
| Edit clip / extend clip | Video 1.0 only |
| "Old quality model" / pro / image-quality | Rewrite → Image 2.0 + `quality=low` |
| Mixed chain 1.0 + 1.5 | Warn; need Continuity Guardian approval |

## Pairing

- Web paste packets → also `imagine-execution-bridge` / `ACTIVATE IMAGINE_BRIDGE`
- Full multi-surface handoff → `ACTIVATE IMAGINE_AGENT_MODE_HANDOFF`
- Registry source of truth → Studio `tools/models.py` (do not drift)

## References

- `references/model-catalog.md` — full alias + redirect table
- Official pricing / names: https://docs.x.ai/docs/models
- Surface C bridge: Studio `GROK_COM_IMAGINE_BRIDGE.md`