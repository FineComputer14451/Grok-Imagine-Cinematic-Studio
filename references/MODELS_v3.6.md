# Model Registry v3.6.7 — Grok Build & xAI (Dual Stack)

Canonical model slugs for Grok Imagine Cinematic Studio. Implemented in `tools/models.py`.

**Last updated:** July 2026  
**Studio target:** v3.6.7  
**Source:** [xAI Models & Pricing](https://docs.x.ai/developers/models), [Grok 4.5](https://docs.x.ai/developers/grok-4-5), local `grok models`

**Implementation note:** Defaults live only in `ROLE_DEFAULTS` / `STACK_CONTRACT` (not per-model flags). Aliases live on each model entry. `models verify` is data-driven (alias integrity + dual-stack contract) and soft-probes `grok --version` against recommended **0.2.93**.

---

## Dual-stack policy

| Layer | Default slug | Why |
|-------|--------------|-----|
| **Cinematic orchestration** (Production Bibles, long multi-agent memory) | `grok-4.3` | **1M** context, lower token cost |
| **Grok Build / coding / agentic** | `grok-4.5` | Live Build default; stronger coding/agent loops |
| **Grok Build CLI binary** | ≥ **0.2.93** | Install/update via `curl -fsSL https://x.ai/cli/install.sh \| bash` |

Do **not** treat `0.2.93` as an API model slug — it is the **CLI version**.

---

## Grok Build CLI (Local Agent)

| Slug | Role | When to Use |
|------|------|-------------|
| `grok-4.5` | **Default** | Coding, agentic tasks, knowledge work (powers Grok Build) |
| `grok-composer-2.5-fast` | Creative | Fast multi-agent cinematic direction |
| `grok-build` | Fork secondary | Code/skills tooling (`fork_secondary_model`) |
| `grok-4.3` | Cinematic | 1M-context orchestration inside Build sessions |

**Min recommended CLI:** `0.2.93`  
Note (0.2.93): **Esc no longer cancels a turn** — use **Ctrl+C**. Double-Esc rewind works while focused on scrollback.

Configured in `~/.grok/config.toml`:
```toml
[models]
default = "grok-4.5"

[ui]
fork_secondary_model = "grok-build"
```

---

## xAI API Chat Models

| Slug | Context | Input / 1M | Output / 1M | When to Use |
|------|---------|------------|-------------|-------------|
| `grok-4.3` | **1M** | $1.25 | $2.50 | **Cinematic default** — Production Bibles, 1M memory banks |
| `grok-4.5` | 500k | $2.00 ($0.50 cached) | $6.00 | **Build default** — coding, agentic, Grok Build |
| `grok-build-0.1` | 256k | $1.00 | $2.00 | **Legacy** coding API — prefer `grok-4.5` |

**Studio cinematic default:** `grok-4.3`  
**Studio build/coding default:** `grok-4.5`  

**4.5 aliases:** `4.5`, `grok-4.5-latest`, `grok-build-latest`, `coding`, `grok-build`, `build`  
**4.3 aliases:** `4.3`, `cinematic`, `grok-4`  

**Grok 4.5 reasoning:** low / medium / high (default **high**). Prefer a stable `prompt_cache_key` for multi-turn agent loops.

---

## Grok Imagine Video

| Slug | Cost | Native Audio | Modalities |
|------|------|--------------|------------|
| `grok-imagine-video` | **$0.050 / sec** | No | text, image, video → video |
| `grok-imagine-video-1.5` | $0.080 / sec | Yes (one-pass) | image → video |

**1.0 aliases (studio shorthand):** `imagine-video`, `video-1.0`, `1.0`  
**1.5 aliases (xAI API):** `grok-imagine-video-1.5-preview`, `grok-imagine-video-1.5-2026-05-30`  
**1.5 aliases (studio shorthand):** `imagine-video-1.5`, `video-1.5`, `1.5`, `1.5-preview`, `preview`

**Regions:** `us-east-1`, `eu-west-1`, `us-west-2` (both models)

**VIDEO_PIPELINE_SPEC default:**
```
[VIDEO_PIPELINE_SPEC: model="grok-imagine-video", resolution="720p", ...]
```

---

## Grok Imagine Image

| Slug | Cost | Modalities |
|------|------|------------|
| `grok-imagine-image` | $0.02 / image | text, image → image |
| `grok-imagine-image-quality` | $0.05 / image | text, image → image |

**Standard aliases (xAI API):** `grok-imagine-image-2026-03-02`  
**Standard aliases (studio shorthand):** `imagine-image`, `image`

**Quality aliases (xAI API):** `grok-imagine-image-quality-20260403`, `grok-imagine-image-quality-latest`, `grok-imagine-image-pro`  
**Quality aliases (studio shorthand):** `imagine-image-quality`, `image-quality`, `quality`, `pro`

**Regions:** `us-east-1`, `eu-west-1`, `us-west-2` (both models)

---

## Python Helpers

`tools/models.py` exposes:
- `ROLE_DEFAULTS` / `STACK_CONTRACT` — single source for dual-stack defaults
- `build_video_pipeline_spec(model)` — locked `VIDEO_PIPELINE_SPEC` string
- `model_stack_summary(chat_model, video_model)` — bible/CLI model stack dict
- `resolve_chat_model()` / `resolve_video_model()` / `resolve_image_model()` — alias normalization
- `known_chat_model()` — true only for registered ids/aliases (detects silent fallback)
- `imagine_video_pricing_table()` / `imagine_image_pricing_table()` — quota optimizer sync
- `RECOMMENDED_GROK_BUILD_CLI_VERSION` (`0.2.93`) — soft-probed by `models verify`

## CLI

```bash
python tools/cinematic_studio_cli.py models list
python tools/cinematic_studio_cli.py models verify
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
| Activate cinematic studio / long Production Bible | `grok-4.3` |
| Grok Build CLI sessions, skill development, coding | `grok-4.5` (CLI default) or `grok-build` |
| Headless agent / API automation | `grok-4.5` |
| Default video generation (cost-effective) | `grok-imagine-video` (1.0) |
| Native-audio video (1.5 features) | `grok-imagine-video-1.5` |
| Hero keyframes | `grok-imagine-image-quality` |
| Reference stills | `grok-imagine-image` |
