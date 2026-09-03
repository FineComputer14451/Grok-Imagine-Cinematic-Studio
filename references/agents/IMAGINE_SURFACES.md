# Official Imagine surfaces (studio v3.11.2)

**Status:** Canonical mapping  
**Code:** `tools/models.py` (`imagine_surface_catalog()`) · `tools/handoff_schema.py`  
**Agent Mode protocol:** `IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md`

Grok Imagine Cinematic Studio is an independent community project. This file maps **xAI’s public Imagine products** to studio slugs and execution surfaces. It does not claim xAI endorsement.

There is **no** `grok-imagine-video-2.0`. **2.0 is Imagine Image only.**

---

## Imagine models

| Family | Official slug | Studio role | Pricing (docs.x.ai / x.ai/api) | Caps |
|--------|---------------|-------------|-------------------------------|------|
| Image 1.0 | `grok-imagine-image` | Draft / volume stills (**default**) | $0.02 / img | 1K / 2K |
| Image Quality | `grok-imagine-image-quality` | **Retired 2026-11-02** — aliases still resolve; spend rewrites to 2.0 `quality=low` | was $0.05 / img; billed as 2.0 low | 1K / 2K |
| **Image 2.0** | `grok-imagine-image-2.0` | **Hero plates, Quality Mode, Responses `image_generation` tool** | from $0.04 / img (1K low); `quality` = low \| medium \| auto | 1K / 2K; up to **5** edit refs; `21:9` / `5:2` |
| Video 1.0 | `grok-imagine-video` | Cost default video; **edit + extend** | from $0.05 / sec (480p); 720p $0.07 | 480p / 720p |
| Video 1.5 | `grok-imagine-video-1.5` | Native audio, physics, 1080p, reference-to-video | 480p $0.08 · 720p $0.14 · 1080p $0.25 / sec | t2v/i2v to 1080p / 15s; r2v cap 720p |

Aliases: `2.0` / `image-2.0` → Image 2.0. Video slug `2.0` is **not** a product (falls back to Video 1.0).  
`quality` / `pro` / `grok-imagine-image-pro` still resolve to the quality slug for display; the Imagine client never sends that slug on the wire after this studio pin. See [xAI migration](https://docs.x.ai/developers/migration/imagine-image-quality-nov-2).

### Routing

| Shot / asset | Image | Video |
|--------------|-------|-------|
| Draft / animatic / volume | `grok-imagine-image` | `grok-imagine-video` |
| Hero still / Identity Lock plate / Quality Mode | `grok-imagine-image-2.0` | — |
| i2v from locked plate | Image 2.0 plate | 1.0 default; 1.5 if native audio / physics / intimacy |
| Reference-to-video / preset voice | — | **1.5 only** |
| Video edit / extend | — | **1.0 only** (1.5 → `failed_precondition`) |

---

## REST endpoints (`https://api.x.ai/v1`)

| Mode | Method / path | Selects with |
|------|---------------|--------------|
| Image generate | `POST /images/generations` | `prompt` + `model` (`n`, `aspect_ratio`, `resolution`, `quality` on 2.0: low \| medium \| auto) |
| Image edit | `POST /images/edits` | `prompt` + `image` (url / data URI / `file_id`); up to **5** refs on 2.0 (3 on 1.0) |
| Text-to-video | `POST /videos/generations` | `prompt` only |
| Image-to-video | same | `prompt` + `image` |
| Reference-to-video | same | `prompt` + `reference_images` and/or `reference_audios` |
| Video edit | `POST /videos/edits` | `prompt` + `video`; input ≤ 8.7s |
| Video extend | `POST /videos/extensions` | `prompt` + `video` |
| Poll | `GET /videos/{request_id}` | `pending` / `done` / `failed` / `expired` |

`image` + `reference_images` in one request is a **400**.

CLI: `cinematic-studio imagine submit image|image_edit|video|video_edit|video_extend|reference_to_video`

---

## Agent Mode / operator surfaces

Studio `target_surface` values for `imagine_agent_mode_handoff`:

| ID | Surface | How generation runs |
|----|---------|---------------------|
| A | `grok_build_tools` | Session tools `image_gen` / `image_edit` / `image_to_video` / `reference_to_video` |
| B | `grok_agent_acp` | `grok agent` / IDE ACP — same tools + skills + CLI |
| C | `grok_com_imagine` | Manual paste; Quality Mode = Image 2.0. Alias: `grok_mobile_imagine` |
| D | `xai_api` | REST via `imagine submit` / `sfw run` / `sequence run` |
| E | `xai_responses_tool` | Server-side Responses `image_generation` tool (Image 2.0). Aliases: `responses`, `image_generation_tool` |

Console Playground uses the same REST models as D — no extra packet type.

```bash
python tools/cinematic_studio_cli.py imagine verify
python tools/cinematic_studio_cli.py imagine agent-handoff \
  --batch <slug> --shot <id> --surface xai_responses_tool --format markdown
```
