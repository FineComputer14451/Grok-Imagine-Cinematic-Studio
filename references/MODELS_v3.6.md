# Model Registry v3.6 — Grok Build & xAI

Canonical model slugs for Grok Imagine Cinematic Studio. Implemented in `tools/models.py`.

**Last updated:** June 2026  
**Source:** [xAI Models & Pricing](https://docs.x.ai/developers/models), local `grok models`

---

## Grok Build CLI (Local Agent)

| Slug | Role | When to Use |
|------|------|-------------|
| `grok-composer-2.5-fast` | **Default** | Creative orchestration, multi-agent cinematic direction |
| `grok-build` | Fork secondary | Code generation, skill scripts, repo tooling |

Configured in `~/.grok/config.toml`:
```toml
[ui]
fork_secondary_model = "grok-build"
```

---

## xAI API Chat Models

| Slug | Context | Input / 1M | Output / 1M | When to Use |
|------|---------|------------|-------------|-------------|
| `grok-4.3` | 1M | $1.25 | $2.50 | Cinematic orchestration, Production Bibles, 1M context |
| `grok-build-0.1` | 256k | $1.00 | $2.00 | Coding, agentic workflows, CLI automation |

**Web UI default:** `grok-4.3` (cinematic prompts)  
**Build automation default:** `grok-build-0.1`

---

## Grok Imagine Video

| Slug | Cost | Native Audio | Modalities |
|------|------|--------------|------------|
| `grok-imagine-video-1.5` | **$0.080 / sec** | Yes (one-pass) | image → video |
| `grok-imagine-video` | $0.050 / sec | No | text, image, video → video |

**1.5 aliases (xAI API):** `grok-imagine-video-1.5-preview`, `grok-imagine-video-1.5-2026-05-30`  
**1.5 aliases (studio shorthand):** `imagine-video-1.5`, `video-1.5`, `1.5`, `1.5-preview`, `preview`  
**1.0 aliases:** `imagine-video`, `video-1.0`, `1.0`

**Regions:** `us-east-1`, `eu-west-1`, `us-west-2` (both models)

**VIDEO_PIPELINE_SPEC default:**
```
[VIDEO_PIPELINE_SPEC: model="grok-imagine-video-1.5", resolution="720p", ...]
```

---

## Grok Imagine Image

| Slug | Cost |
|------|------|
| `grok-imagine-image` | $0.02 / image |
| `grok-imagine-image-quality` | $0.05 / image |

---

## Python Helpers

`tools/models.py` exposes:
- `build_video_pipeline_spec(model)` — locked `VIDEO_PIPELINE_SPEC` string
- `model_stack_summary(chat_model, video_model)` — bible/CLI model stack dict
- `resolve_chat_model()` / `resolve_video_model()` — alias normalization

## CLI

```bash
python tools/cinematic_studio_cli.py models list
python tools/cinematic_studio_cli.py status
python tools/cinematic_studio_cli.py generate-prompt "Story" --chat-model grok-4.3 --video-model 1.5
python tools/cinematic_studio_cli.py create-bible "Title" --chat-model grok-4.3 --video-model 1.5
python tools/cinematic_studio_cli.py cost-simulate --duration 90 --video-model 1.5
python tools/cinematic_studio_cli.py quota estimate --duration 90 --video-model grok-imagine-video-1.5
```

---

## Model Selection Guide

| Task | Model |
|------|-------|
| Activate cinematic studio in Grok chat | `grok-4.3` |
| Run repo scripts / skill development | `grok-build` (CLI) or `grok-build-0.1` (API) |
| Generate 1.5 video with native audio | `grok-imagine-video-1.5` |
| Draft iteration (lower cost) | `grok-imagine-video` or Fast mode strategy |
| Hero keyframes | `grok-imagine-image-quality` |
| Reference stills | `grok-imagine-image` |