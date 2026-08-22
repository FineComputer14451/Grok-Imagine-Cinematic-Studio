# Release Notes — v3.10.0

**Date:** 2026-08-22  
**Codename:** Official Imagine surface map

## Highlights

Grok Imagine Cinematic Studio **v3.10.0** maps xAI’s public Imagine products onto studio slugs and execution surfaces. **2.0 is Imagine Image only** — there is no Video 2.0.

| Family | Official slug | Studio role |
|--------|---------------|-------------|
| Image 1.0 | `grok-imagine-image` | Draft / volume stills (default) |
| Image Quality | `grok-imagine-image-quality` | Legacy hero stills |
| **Image 2.0** | `grok-imagine-image-2.0` | Hero plates, Quality Mode, Responses `image_generation` |
| Video 1.0 | `grok-imagine-video` | Cost default video; **edit + extend** |
| Video 1.5 | `grok-imagine-video-1.5` | Native audio, physics, 1080p, reference-to-video |

Canonical: [`references/agents/IMAGINE_SURFACES.md`](../../references/agents/IMAGINE_SURFACES.md)

## Agent Mode surfaces A–E

| ID | `target_surface` | How generation runs |
|----|------------------|---------------------|
| A | `grok_build_tools` | Session tools |
| B | `grok_agent_acp` | `grok agent` / IDE ACP |
| C | `grok_com_imagine` | Manual paste (Quality Mode = Image 2.0). Alias: `grok_mobile_imagine` |
| D | `xai_api` | REST via `imagine submit` / `sfw run` / `sequence run` |
| E | `xai_responses_tool` | Responses `image_generation` (Image 2.0). Aliases: `responses`, `image_generation_tool` |

## REST coverage

`cinematic-studio imagine submit` now supports `image` · `image_edit` · `video` · `video_edit` · `video_extend` · `reference_to_video`, plus `--resolution` `--quality` `--file-id` `--reference-image-url` `--voice-id`.

Video **edit / extend** are Video **1.0** only. Reference-to-video is Video **1.5** only.

## Control plane

API `GET /v1/meta/production-options` exposes `image_models`, `imagine_surfaces`, and `imagine_execution_modes`. Streamlit / React / NiceGUI image pickers and the dashboard Imagine routing snapshot follow the same catalog.

## Compatibility

- `VERSION` / `STUDIO_COMPATIBILITY_VERSION`: **3.10.0**
- Handoff `PROTOCOL_OK` includes **3.10.0** (prior 3.7.1–3.9.1 packets still accepted)
- Activation: **`Activate Grok Imagine Cinematic Studio v3.10.0`**
