# Model Registry v3.7.1 — Grok Build & xAI (Unified Chat Default)

Canonical model slugs for Grok Imagine Cinematic Studio. Implemented in `tools/models.py`.

**Last updated:** August 2026  
**Studio target:** v3.11.3  
**Source:** [xAI Models & Pricing](https://docs.x.ai/developers/models), [Grok 4.6](https://docs.x.ai/docs/models), local `grok models`

**Implementation note:** Defaults live only in `ROLE_DEFAULTS` / `STACK_CONTRACT` (not per-model flags). Aliases live on each model entry. `models verify` is data-driven (alias integrity + stack contract) and soft-probes `grok --version` against recommended **1.0.5**.

---

## Stack policy

| Layer | Default slug | Why |
|-------|--------------|-----|
| **Cinematic orchestration** (Production Bibles, multi-agent) | `grok-4.6` | Studio default (`grok-4.5` aliases wrap 4.6) |
| **Grok Build / coding / agentic** | `grok-4.6` | Live Build default |
| **Optional 1M-context Bibles** | `grok-4.3` | Opt-in via `--chat-model grok-4.3` (or `long-context`) |
| **Grok Build CLI binary** | ≥ **1.0.5** | Install/update via `curl -fsSL https://x.ai/cli/install.sh \| bash` |

Do **not** treat `1.0.5` as an API model slug — it is the **CLI version**.

---

## Grok Build CLI (Local Agent)

| Slug | Role | When to Use |
|------|------|-------------|
| `grok-4.6` | **Default** | Cinematic orchestration, coding, agentic tasks (powers Grok Build) |
| `grok-4.5` | Legacy picker | Alias of `grok-4.6` (not a second stack default) |
| `grok-composer-2.5-fast` | Creative | Fast multi-agent cinematic direction |
| `grok-build` | Fork secondary | Code/skills tooling (`fork_secondary_model`) |
| `grok-4.3` | Long context | Optional 1M-context sessions inside Build |

**Min recommended CLI:** `1.0.5`  
Note (1.0.5+): **Esc no longer cancels a turn** — use **Ctrl+C**. Double-Esc rewind works while focused on scrollback.

Configured in `~/.grok/config.toml`:
```toml
[models]
default = "grok-4.6"

[ui]
fork_secondary_model = "grok-build"
```

---

## Grok Build NSFW aliases (opt-in ErosForge)

Picker aliases for **orchestration** only (not Imagine generators). Registry: `GROK_BUILD_NSFW_MODELS` in `tools/models.py`. Config example: `config/grok-build-nsfw-models.example.toml`.

| Slug | Base model | Temp | Role |
|------|------------|------|------|
| `erosforge-director` | `grok-4.6` | 0.92 | Intimate direction |
| `nsfw-prompt-master` | `grok-4.6` | 0.78 | Erotic prompt craft |
| `nsfw-quota-planner` | `grok-4.6` | 0.35 | Batch / Heavy quota |
| `nsfw-sequence-extend` | `grok-4.6` | 0.72 | 30–120s sensual chains |
| `nsfw-chain-qa` | `grok-4.6` | 0.25 | 8-point intimate QA |
| `nsfw-identity-lock` | `grok-4.6` | 0.40 | Intimate DNA lock |
| `nsfw-long-context` | `grok-4.3` | 0.70 | 1M intimacy banks |
| `nsfw-creative-fast` | `grok-composer-2.5-fast` | 0.95 | Fast drafts |

**Install (user config only — models load from `~/.grok/config.toml`):**

```bash
bash scripts/install_nsfw_grok_models.sh
bash scripts/install_nsfw_grok_models.sh --force      # refresh blocks
bash scripts/install_nsfw_grok_models.sh --subagents  # explore/plan → NSFW planners
grok models
/model erosforge-director
```

Prefer **cli-chat-proxy** session auth (SuperGrok) over paid `api.x.ai` credits.  
Personas: `.grok/personas/{erosforge,nsfw-prompt,nsfw-qa}.toml`  
**Still/video generation** remains `grok-imagine-image*` / `grok-imagine-video*`.  
Activate production with **`ACTIVATE EROSFORGE`**.

---

## xAI API Chat Models

| Slug | Context | Input / 1M | Output / 1M | When to Use |
|------|---------|------------|-------------|-------------|
| `grok-4.6` | 500k | $2.00 ($0.50 cached) | $6.00 | **Studio default** — cinematic + coding + agentic |
| `grok-4.3` | **1M** | $1.25 | $2.50 | **Opt-in** — very long Production Bibles / memory banks |
| `grok-build-0.1` | 256k | $1.00 | $2.00 | **Legacy** coding API — prefer `grok-4.6` |

**Studio cinematic default:** `grok-4.6`  
**Studio build/coding default:** `grok-4.6`  
**Opt-in long context:** `grok-4.3`

**4.6 aliases:** `4.6`, `grok-4.6-latest`, `4.5`, `grok-4.5`, `grok-4.5-latest`, `grok-build-latest`, `coding`, `grok-build`, `build`, `cinematic`  
**4.3 aliases:** `4.3`, `long-context`, `grok-4`

**Grok 4.6 reasoning:** low / medium / high (default **high**). Prefer a stable `prompt_cache_key` for multi-turn agent loops.

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
| `grok-imagine-image-2.0` | from $0.04 / image (`quality` low \| medium \| auto) | text, image → image; up to 5 edit refs |
| `grok-imagine-image-quality` | **Retired 2026-11-02** — billed as 2.0 `quality=low` (was $0.05) | aliases still resolve; do not send on the wire |

**Standard aliases (xAI API):** `grok-imagine-image-2026-03-02`  
**Standard aliases (studio shorthand):** `imagine-image`, `image`

**2.0 aliases:** `image-2.0`, `2.0`, `imagine-image-2.0`

**Quality aliases (xAI API):** `grok-imagine-image-quality-20260403`, `grok-imagine-image-quality-latest`, `grok-imagine-image-pro`  
**Quality aliases (studio shorthand):** `imagine-image-quality`, `image-quality`, `quality`, `pro` — rewrite to 2.0 `quality=low`

**Regions:** `us-east-1`, `eu-west-1`, `us-west-2` (1.0); 2.0: `us-east-1`, `us-west-2`

---

## Python Helpers

`tools/models.py` exposes:
- `ROLE_DEFAULTS` / `STACK_CONTRACT` — single source for stack defaults
- `build_video_pipeline_spec(model)` — locked `VIDEO_PIPELINE_SPEC` string
- `model_stack_summary(chat_model, video_model)` — bible/CLI model stack dict
- `resolve_chat_model()` / `resolve_video_model()` / `resolve_image_model()` — alias normalization
- `known_chat_model()` — true only for registered ids/aliases (detects silent fallback)
- `imagine_video_pricing_table()` / `imagine_image_pricing_table()` — quota optimizer sync
- `RECOMMENDED_GROK_BUILD_CLI_VERSION` (`1.0.5`) — soft-probed by `models verify`

## CLI

```bash
python tools/cinematic_studio_cli.py models list
python tools/cinematic_studio_cli.py models verify
python tools/cinematic_studio_cli.py status
python tools/cinematic_studio_cli.py generate-prompt "Story" --chat-model grok-4.6 --video-model 1.5
python tools/cinematic_studio_cli.py create-bible "Title" --chat-model grok-4.6 --video-model 1.5
# Optional 1M-context Bible:
python tools/cinematic_studio_cli.py create-bible "Title" --chat-model grok-4.3 --video-model 1.5
python tools/cinematic_studio_cli.py cost-simulate --duration 90 --video-model 1.5
python tools/cinematic_studio_cli.py quota estimate --duration 90 --video-model grok-imagine-video-1.5
```

---

## Model Selection Guide

| Task | Model |
|------|-------|
| Activate cinematic studio / Production Bible (default) | `grok-4.6` |
| Very long Bible / 1M memory bank | `grok-4.3` (opt-in) |
| Grok Build CLI sessions, skill development, coding | `grok-4.6` (CLI default) or `grok-build` |
| Headless agent / API automation | `grok-4.6` |
| Default video generation (cost-effective) | `grok-imagine-video` (1.0) |
| Native-audio video (1.5 features) | `grok-imagine-video-1.5` |
| Hero keyframes | `grok-imagine-image-2.0` (`quality=medium`) |
| Reference stills | `grok-imagine-image` |
