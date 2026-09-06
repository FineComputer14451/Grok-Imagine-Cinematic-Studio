# Imagine model catalog (overrides)

Source of truth: FineComputer14451/Grok-Imagine-Cinematic-Studio `tools/models.py` + docs.x.ai Models (Sep 2026).

## Image slugs

| Canonical | Default role | Deprecated | Redirect |
|-----------|--------------|------------|----------|
| `grok-imagine-image` | Draft / Fast Mode | no | — |
| `grok-imagine-image-2.0` | Hero / Quality Mode | no | — |
| `grok-imagine-image-quality` | Legacy Quality | yes (retire 2026-11-02) | → `grok-imagine-image-2.0` + `quality=low` |

### Image 2.0 quality param

Allowed: `low` | `medium` | `auto`  
Omit on Image 1.0.

### Image aliases

```
2.0, image-2.0, imagine-image-2.0, grok-imagine-image-2, image-2, hero, quality-mode
  → grok-imagine-image-2.0

1.0, image, imagine-image, image-1.0, fast, fast-mode, draft
  → grok-imagine-image

quality, pro, image-quality, imagine-image-quality, grok-imagine-image-pro,
grok-imagine-image-quality-latest, grok-imagine-image-quality-20260403
  → grok-imagine-image-quality (then redirect to 2.0 + quality=low)
```

## Video slugs

| Canonical | Default role | Native audio | Edit/extend |
|-----------|--------------|--------------|-------------|
| `grok-imagine-video` | Cost default / draft | no | **yes** |
| `grok-imagine-video-1.5` | Final / audio | yes | **no** |

### Video aliases

```
1.0, video, imagine-video, video-1.0, edit-extend
  → grok-imagine-video

1.5, video-1.5, imagine-video-1.5, native-audio, 1.5-preview,
grok-imagine-video-1.5-preview, grok-imagine-video-1.5-2026-05-30
  → grok-imagine-video-1.5
```

## Studio role defaults (do not invent)

```
imagine_image default = grok-imagine-image
imagine_image hero    = grok-imagine-image-2.0
imagine_video default = grok-imagine-video
imagine_video audio   = grok-imagine-video-1.5
edit/extend video     = grok-imagine-video
```

## grok.com/imagine UI mapping

| UI control | Wire slug |
|------------|-----------|
| Quality Mode | `grok-imagine-image-2.0` |
| Fast Mode | `grok-imagine-image` |
| Video without native-audio emphasis | `grok-imagine-video` |
| Video with native audio / Sound Layer | `grok-imagine-video-1.5` |

There is **no** public "pick arbitrary slug" control on the consumer UI — overrides are expressed as **Quality/Fast + 1.0/1.5**, and as `model_stack` / `VIDEO_PIPELINE_SPEC` in Studio packets.