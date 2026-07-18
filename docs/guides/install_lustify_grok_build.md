# Install & Set Up Lustify with Grok Build

**Audience:** operators who want Grok Build to download and configure the **Lustify** SDXL checkpoint for local ComfyUI generation.

**Lustify** is a photoreal **SDXL** NSFW/SFW checkpoint (Civitai model **573152**, author coyotte). Mature downloads live on [civitai.red](https://civitai.red/models/573152/lustify-nsfw-checkpoint); community mirrors exist on Hugging Face (e.g. older v2).

| Item | Recommendation |
|------|----------------|
| Grok Build | ≥ **0.2.93** (`grok --version`) |
| ComfyUI | Installed and smoke-tested at `~/ComfyUI` — see [install_comfyui_grok_build.md](./install_comfyui_grok_build.md) |
| Checkpoint path | `~/ComfyUI/models/checkpoints/lustify_<version>.safetensors` |
| Disk | ~**6–14 GB** free for one SDXL `.safetensors` |
| GPU | Prefer **8 GB+** VRAM for SDXL; CPU is very slow |
| Tokens (optional) | `HF_TOKEN` and/or `CIVITAI_API_TOKEN` for automated download |

Local Lustify is **not** a Grok Build chat model slug and **not** a Grok Imagine API model. Keep weights under ComfyUI only.

---

## Prerequisites

| Need | Why |
|------|-----|
| Working ComfyUI | Venv, torch, UI reachable (typically `http://127.0.0.1:8188`) |
| Grok Build auth | Browser sign-in or `XAI_API_KEY` |
| Free disk | SDXL checkpoints are multi-GB |
| Optional API tokens | Mature Civitai / HF downloads may require auth |

Pre-check (you or the agent):

```bash
grok --version
ls ~/ComfyUI/models/checkpoints/
df -h ~
source ~/ComfyUI/.venv/bin/activate 2>/dev/null
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```

If ComfyUI is missing or broken, finish [install_comfyui_grok_build.md](./install_comfyui_grok_build.md) first.

---

## Quick start (Grok Build)

```bash
cd ~/ComfyUI && grok
```

Paste the **Ready-to-paste Grok Build prompt** below.

Headless:

```bash
cd ~/ComfyUI && grok -p "$(cat path/to/install_lustify_prompt.md)"
```

---

## Ready-to-paste Grok Build prompt

Copy everything inside the fenced block below into a Grok Build session.

```text
You are installing and configuring LUSTIFY (SDXL NSFW/SFW checkpoint) for local ComfyUI image generation.

## Goal
1. Confirm ComfyUI at ~/ComfyUI is runnable (venv + torch). If not, stop and point me at the ComfyUI install guide first.
2. Download the latest stable Lustify SDXL checkpoint (prefer full/fp16 safetensors).
3. Place it in ~/ComfyUI/models/checkpoints/ with a clear filename (lustify_<version>.safetensors).
4. Create a minimal text-to-image workflow JSON that loads Lustify with recommended sampler settings.
5. Write SETUP_LUSTIFY.md (start steps, settings, sample prompts, troubleshooting).
6. Do NOT generate illegal content. Adult content only for consenting-adult fictional use.

## Discover & choose version
- Primary: Civitai model 573152 “LUSTIFY!” — mature site: https://civitai.red/models/573152/lustify-nsfw-checkpoint
- Fallback: Hugging Face mirrors (search “lustify sdxl safetensors”); prefer well-known rehosts with hashes when available.
- Prefer latest production release the user can actually download.
- If multiple files: prefer fp16 for lower VRAM unless user has 16GB+ and wants full precision.
- Report: version name, file size, SHA256 if available, final path.

## Download rules
- Use huggingface-cli if HF_TOKEN is set and a HF repo is chosen:
    pip install -U "huggingface_hub[cli]"
    huggingface-cli download <repo_id> <file> --local-dir ~/ComfyUI/models/checkpoints
- Or wget/curl direct URL if Civitai/HF provides a direct link.
- If Civitai requires login/API: check CIVITAI_API_TOKEN or HF_TOKEN; if missing, stop and ask for a token or a local file path they already downloaded.
- Never commit multi-GB weights to git. Ensure path is gitignored if under a repo.
- Resume partial downloads when possible. Ask before re-downloading if a partial file exists.

## ComfyUI readiness
- Reuse ~/ComfyUI; do not wipe existing checkpoints (v1-5, svd_xt, or other models).
- Ensure models/checkpoints exists.
- Optional helpful custom nodes only if missing and network OK:
  - ComfyUI-Manager (if not installed)
  - Face/detailer style nodes for distant faces (Lustify docs note hands/faces at distance)
- Smoke: restart or refresh so the new checkpoint appears in Load Checkpoint.

## Recommended default generation settings (from model card)
- Sampler: DPM++ 2M SDE / DPM++ 3M SDE family (e.g. dpmpp_2m_sde)
- Scheduler: Karras or Exponential
- Steps: 30
- CFG: 4–7 (start at 5.5)
- Resolution: 1024×1024 or 832×1216 portrait (SDXL-native)
- Optional highres-style second pass: upscale ~1.4–1.5, denoise ~0.4
- Prompting: natural language + optional danbooru tags; avoid overloaded “schizo” negatives
- High-impact tags: camera brand tags, analog/glamour photo, cinematic/soft/neon lighting, film stock names

## Deliverables
1. Checkpoint: ~/ComfyUI/models/checkpoints/lustify_<version>.safetensors
2. Workflow: e.g. ~/ComfyUI/user/default/workflows/lustify_t2i_basic.json (or blueprints/ equivalent)
3. SETUP_LUSTIFY.md with:
   - how to start ComfyUI and load the workflow
   - sample SFW lock-test and adult-safe fictional prompts
   - VRAM tips and troubleshooting (OOM, black images, wrong base model selected)
4. Final summary: commands run, paths, any manual steps still needed (tokens, restart).

## Constraints
- Prefer reversible local changes; never delete other checkpoints.
- Bind workflows to local paths only.
- If download is blocked, leave the workflow ready and print a manual download checklist.
- Do not register Lustify as a Grok Build chat model slug.
```

### Optional host-context paragraph

Append when finishing setup on a known host (edit to match):

```text
Host context:
- ComfyUI at ~/ComfyUI (do not re-clone)
- Preserve existing models/checkpoints/*
- Prefer fp16 Lustify if VRAM is limited
- If HF_TOKEN or CIVITAI_API_TOKEN is unset, ask before assuming anonymous download works
```

---

## What “done” looks like

```text
~/ComfyUI/
├── models/checkpoints/
│   └── lustify_<version>.safetensors    # NEW
├── user/default/workflows/              # or blueprints/ — path may vary by Comfy version
│   └── lustify_t2i_basic.json           # NEW
└── SETUP_LUSTIFY.md                     # NEW (agent-written runbook)
```

**Smoke criteria**

- Checkpoint appears in Load Checkpoint after refresh/restart
- Workflow loads without missing-node errors
- One clean **1024×1024** (or portrait SDXL) still generates
- Output is **not** the wrong base model (e.g. accidental SD 1.5 selection)

```bash
cd ~/ComfyUI
./start_comfyui.sh
# or: source .venv/bin/activate && python main.py --listen 127.0.0.1 --port 8188
```

Open **http://127.0.0.1:8188** → load Lustify workflow → queue prompt → confirm file under `output/`.

---

## Manual fallback (no agent download)

1. Open [civitai.red/models/573152](https://civitai.red/models/573152/lustify-nsfw-checkpoint) (or your preferred HF mirror).
2. Download the **SDXL** `.safetensors` for the version you want.
3. Place it:

```bash
mkdir -p ~/ComfyUI/models/checkpoints
mv ~/Downloads/lustify*.safetensors ~/ComfyUI/models/checkpoints/
```

4. Restart ComfyUI → refresh checkpoints → select Lustify (not SD 1.5).
5. Start with: **30 steps · CFG 5.5 · DPM++ 2M SDE · Karras · 1024×1024**.

Tokens for later automation:

```bash
export HF_TOKEN="hf_..."           # Hugging Face
export CIVITAI_API_TOKEN="..."     # Civitai API
```

---

## Recommended generation settings

From the public model card / community usage (verify against the version you install):

| Setting | Suggested default |
|---------|-------------------|
| Sampler | DPM++ 2M SDE / DPM++ 3M SDE family |
| Scheduler | Karras or Exponential |
| Steps | **30** |
| CFG | **4–7** (start **5.5**) |
| Size | **1024×1024** or **832×1216** portrait |
| Highres-style pass | Upscale ~1.4–1.5, denoise ~0.4 |
| Prompt style | Natural language + optional danbooru tags; short negatives |

Tags that often have strong visual impact: camera brand strings, analog/glamour photography, cinematic/soft/neon lighting, film stock names.

---

## Recommended first prompts

**SFW photoreal lock test**

```text
photorealistic portrait of a woman, soft window light, 85mm, shallow depth of field,
shot on Canon EOS 5D, natural skin texture, cinematic color grade
```

**Negative (keep short)**

```text
blurry, deformed hands, extra fingers, watermark, text, lowres, oversaturated
```

Use adult prompts only for **fictional consenting adults**. Keep explicit assets out of shared repos if policy requires.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Checkpoint missing in UI | File must be under `models/checkpoints/`; restart ComfyUI |
| Looks like SD 1.5 / wrong aesthetic | Wrong checkpoint selected — pick Lustify explicitly |
| OOM / killed | Prefer fp16; lower res (e.g. 896×1152); launch with `--lowvram` |
| Bad faces/hands at distance | Second pass / face detailer; highres denoise ~0.4 |
| Download 401/403 | Set `HF_TOKEN` or Civitai token; mature content is on civitai.red |
| Comfy not ready | Complete [install_comfyui_grok_build.md](./install_comfyui_grok_build.md) first |
| Black images | Broken download / wrong VAE; re-download or try stock SD1.5 smoke test |

---

## Relationship to Grok Imagine Cinematic Studio

| Path | Tooling |
|------|---------|
| Local photoreal stills (Lustify) | ComfyUI + this guide |
| Studio orchestration / Production Bibles | `grok-4.5` + Cinematic Studio skills |
| Intimate sequence direction (opt-in) | `ACTIVATE EROSFORGE` — not automatic |
| Imagine API video/image | `grok-imagine-video` / `grok-imagine-image` |
| Optional long-context chat | `grok-4.3` (1M opt-in) |

Do **not** register Lustify under `tools/models.py` or Grok Build custom chat models. Export stills into `artifacts/` if you hand them into Studio pipelines.

Optional follow-ons (separate prompts):

1. Identity Lock / Character DNA from approved Lustify plates.
2. Face detailer / highres workflow refinement.
3. Batch export into `artifacts/` for Imagine Agent Mode Handoff or i2v.

---

## Related docs

- [install_comfyui_grok_build.md](./install_comfyui_grok_build.md) — install ComfyUI with Grok Build first
- [installation_guide.md](./installation_guide.md) — Studio CLI / plugin install
- Upstream: [Civitai Lustify (mature)](https://civitai.red/models/573152/lustify-nsfw-checkpoint) · ComfyUI model folders under `models/`
- Grok stack models (not Comfy): `references/MODELS.md`

---

*Draft for SuperGrokPro / Cinematic Studio operators — July 2026*
