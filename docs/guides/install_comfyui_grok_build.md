# Install & Set Up ComfyUI with Grok Build

**Audience:** operators who want Grok Build (the coding agent) to install and configure [ComfyUI](https://github.com/comfyanonymous/ComfyUI) for local image/video generation.

**ComfyUI** is the node-graph engine for local diffusion workflows.  
**Grok Build** clones or reuses a tree, creates a venv, installs the correct PyTorch wheel, adds Manager, smoke-tests the server, and writes a short runbook.

This guide is a **paste-ready agent prompt** plus a manual fallback. It is independent of Grok Imagine API spend; local Comfy is a parallel path, not an Imagine model slug.

| Item | Recommendation |
|------|----------------|
| Grok Build | ≥ **0.2.93** (`grok --version`) |
| Install root | `~/ComfyUI` (change if needed) |
| Python | **3.12** or **3.13** preferred |
| Disk | ≥ **15 GB** free for core + one small checkpoint; **50 GB+** for SDXL/Flux |
| Network | Git + pip |
| GPU | NVIDIA CUDA / AMD ROCm / Intel XPU / Apple MPS; else `--cpu` (slow) |

---

## Prerequisites

| Need | Notes |
|------|--------|
| Grok Build auth | Browser sign-in or `XAI_API_KEY` |
| Git | Clone/update ComfyUI |
| Free disk | Stop large downloads if free space is low |
| GPU drivers | Match PyTorch index to your stack |

Pre-check (you or the agent):

```bash
grok --version
python3 --version
git --version
df -h ~
free -h
nvidia-smi 2>/dev/null || echo "No NVIDIA GPU"
```

---

## Quick start (Grok Build)

```bash
cd ~   # or your preferred parent directory
grok
```

Paste the **Ready-to-paste Grok Build prompt** in the next section.

Headless:

```bash
cd ~ && grok -p "$(cat path/to/install_comfyui_prompt.md)"
```

---

## Ready-to-paste Grok Build prompt

Copy everything inside the fenced block below into a Grok Build session.

```text
You are installing and configuring ComfyUI for local AI image/video generation.

## Goal
1. Detect hardware (NVIDIA / AMD / Intel / Apple / CPU-only) and install the correct PyTorch wheel.
2. Ensure ComfyUI is present at ~/ComfyUI (reuse if already cloned; otherwise git clone).
3. Create an isolated venv at ~/ComfyUI/.venv and install all dependencies.
4. Optionally install ComfyUI-Manager (recommended).
5. Verify model folder layout; do not delete existing checkpoints.
6. Smoke-test: start the server, hit the HTTP UI/API, then stop (or leave running if I ask).
7. Write SETUP_COMFYUI.md with start commands, flags, model paths, and troubleshooting.
8. Optionally write a shell launcher: ~/ComfyUI/start_comfyui.sh

## Paths & reuse policy
- Install root: ~/ComfyUI
- If ~/ComfyUI already exists and has main.py: UPDATE with git pull (only if clean or ask first); DO NOT re-clone wipe.
- Preserve models/checkpoints/* (e.g. existing v1-5, svd_xt, or custom models).
- Never commit multi-GB weights or .venv to git.

## Steps (execute in order)

### A. System probe
Report: OS, CPU, RAM, free disk, GPU name + VRAM (or “none”), Python version candidates.
Prefer python3.12 if available; else python3.13; avoid free-threaded builds for custom nodes.

### B. Clone or update
If missing:
  git clone https://github.com/comfyanonymous/ComfyUI.git ~/ComfyUI
If present:
  cd ~/ComfyUI && git status && git pull --ff-only (if fails, report and continue with current tree)

### C. Virtualenv
cd ~/ComfyUI
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -U pip wheel setuptools

### D. PyTorch (CRITICAL — match hardware)
Detect then install ONE path. Verify the current CUDA/ROCm index on https://pytorch.org and the ComfyUI README before pinning; indexes change over time.

1) NVIDIA (nvidia-smi works):
   # Example stable pattern (confirm latest cu* index in ComfyUI README):
   pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu130
   If “Torch not compiled with CUDA enabled”: uninstall torch* and reinstall.

2) AMD ROCm (Linux):
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm7.2
   (Adjust ROCm version to upstream README if newer.)

3) Intel XPU:
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/xpu

4) Apple Silicon:
   Install per Apple Metal / PyTorch guidance, then requirements.

5) CPU-only (no GPU):
   pip install torch torchvision torchaudio
   Document that generation will be very slow; use --cpu and small SD1.5 tests only.

Verify:
  python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
  # Also print mps / xpu if relevant

### E. ComfyUI dependencies
pip install -r requirements.txt
# Optional manager deps:
pip install -r manager_requirements.txt

### F. Directory hygiene
Ensure these exist (mkdir -p as needed):
  models/checkpoints
  models/loras
  models/vae
  models/controlnet
  models/embeddings
  models/upscale_models
  models/clip
  models/clip_vision
  models/diffusion_models
  input
  output
  custom_nodes
  user

Do NOT download large foundation models unless I explicitly ask. Optionally download only a tiny smoke-test checkpoint if none exist and free disk > 5GB (existing small SD1.5 fp16 is enough).

### G. ComfyUI-Manager (recommended)
If custom_nodes has no Manager:
  git clone https://github.com/Comfy-Org/ComfyUI-Manager.git custom_nodes/ComfyUI-Manager
  # Or follow current Manager v4 docs if install method changed
Document launch flag: python main.py --enable-manager

### H. Launcher script
Create start_comfyui.sh:

#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
source .venv/bin/activate
# GPU default; fall back to --cpu if no CUDA
ARGS=(--listen 127.0.0.1 --port 8188 --preview-method auto)
if ! python -c "import torch; raise SystemExit(0 if torch.cuda.is_available() else 1)" 2>/dev/null; then
  # On Apple MPS leave without --cpu; on pure CPU add --cpu
  if [[ "$(uname -s)" == "Darwin" ]]; then
    :
  else
    ARGS+=(--cpu)
  fi
fi
exec python main.py "${ARGS[@]}" --enable-manager "$@"

chmod +x start_comfyui.sh

### I. Smoke test
1. Start server in background with timeout or short run.
2. curl -sS -o /dev/null -w "%{http_code}" http://127.0.0.1:8188/  (expect 200)
3. Confirm process can import nodes without traceback.
4. Stop the server after success (do not leave hung processes).
5. On failure: capture last 80 lines of log, diagnose, fix once, retest.

### J. Deliverables
1. SETUP_COMFYUI.md covering:
   - Hardware detected + torch wheel used
   - How to start/stop
   - Model folder map (checkpoints, loras, vae, …)
   - How to install custom nodes via Manager
   - Recommended first workflow (default graph + existing SD1.5 if present)
   - VRAM/CPU tips (--lowvram, --normalvram, --cpu)
   - Update procedure (git pull + pip install -r requirements.txt)
2. Final summary: paths, versions (python, torch, comfy git SHA), smoke-test result, remaining manual steps.

## Constraints
- Prefer reversible changes; ask before deleting large files or force-resetting git.
- Bind to 127.0.0.1 by default (do not --listen 0.0.0.0 without asking).
- Do not install unrelated system packages with sudo unless absolutely required and approved.
- If disk < 5GB free, stop before large downloads and report.
- Adult checkpoints (e.g. Lustify) are out of scope unless separately requested.
```

### Optional host-context paragraph

Append when finishing an incomplete install on a known host (edit to match your machine):

```text
Host context:
- ComfyUI source already at ~/ComfyUI
- No .venv yet (or incomplete)
- Report GPU status accurately; plan for CPU if none found
- Preserve existing models/checkpoints/*
Prefer finishing the venv + deps + Manager + smoke test over re-cloning.
```

---

## What “done” looks like

```text
~/ComfyUI/
├── .venv/                          # Python + torch + deps
├── main.py
├── start_comfyui.sh                # launcher
├── SETUP_COMFYUI.md                # runbook written by the agent
├── custom_nodes/
│   └── ComfyUI-Manager/            # optional but recommended
├── models/
│   ├── checkpoints/                # put .safetensors here
│   ├── loras/
│   ├── vae/
│   └── …
├── input/
└── output/
```

**Smoke criteria**

- Venv activates; `python -c "import torch"` succeeds
- `python main.py` starts without traceback
- `http://127.0.0.1:8188` returns the UI (HTTP 200)
- Existing checkpoints still appear after UI refresh

---

## Manual fallback (no agent)

### Linux / macOS

```bash
# 1) Clone (skip if tree exists)
git clone https://github.com/comfyanonymous/ComfyUI.git ~/ComfyUI
cd ~/ComfyUI

# 2) Venv
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip wheel setuptools

# 3) PyTorch — pick ONE (verify indexes on pytorch.org / ComfyUI README)
# NVIDIA example:
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu130
# CPU:
# pip install torch torchvision torchaudio

# 4) Comfy deps
pip install -r requirements.txt
pip install -r manager_requirements.txt   # if using Manager

# 5) Manager (optional)
git clone https://github.com/Comfy-Org/ComfyUI-Manager.git custom_nodes/ComfyUI-Manager

# 6) Run
python main.py --listen 127.0.0.1 --port 8188 --enable-manager
# CPU-only:
# python main.py --listen 127.0.0.1 --port 8188 --cpu --enable-manager
```

Open: **http://127.0.0.1:8188**

### Windows alternatives

| Method | When |
|--------|------|
| [Desktop app](https://www.comfy.org/download) | Easiest GUI install (Windows/macOS) |
| [Windows portable](https://github.com/comfyanonymous/ComfyUI/releases) | NVIDIA / AMD / Intel 7z packages; drop models into `ComfyUI\models\…` |
| [comfy-cli](https://docs.comfy.org/comfy-cli/getting-started) | `pip install comfy-cli && comfy install` |

Grok Build can still automate portable extract and path setup if you point it at a download location.

---

## Model folder map

| Asset | Folder |
|-------|--------|
| Checkpoints (SD1.5, SDXL, etc.) | `models/checkpoints/` |
| LoRAs | `models/loras/` |
| VAE | `models/vae/` |
| ControlNet | `models/controlnet/` |
| Embeddings | `models/embeddings/` |
| Upscalers | `models/upscale_models/` |
| CLIP / dual encoders | `models/clip/`, `models/clip_vision/` |
| Diffusion models (split) | `models/diffusion_models/` |
| Outputs | `output/` |
| Inputs / reference images | `input/` |

Share models with another UI via `extra_model_paths.yaml` (copy from `extra_model_paths.yaml.example` and edit paths).

---

## Useful launch flags

| Flag | Purpose |
|------|---------|
| `--listen 127.0.0.1` | Local only (recommended default) |
| `--port 8188` | Web UI port |
| `--cpu` | Force CPU |
| `--lowvram` / `--normalvram` / `--highvram` | VRAM strategies |
| `--enable-manager` | ComfyUI-Manager |
| `--preview-method auto` | Latent previews |
| `--disable-api-nodes` | Offline-only; no paid API nodes |

---

## Day-2 operations

**Update ComfyUI**

```bash
cd ~/ComfyUI
source .venv/bin/activate
git pull --ff-only
pip install -r requirements.txt
```

**Update PyTorch** only when drivers or the upstream README change; re-run a CUDA/MPS/XPU check afterward.

**First generation test**

1. Load the default workflow in the UI.
2. Select an existing small checkpoint (e.g. SD1.5 fp16) if present.
3. Queue a 512×512 prompt.
4. Confirm a file appears under `output/`.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `Torch not compiled with CUDA enabled` | Reinstall torch from the correct CUDA index; confirm `nvidia-smi` and driver |
| UI won’t load | Port in use → try `--port 8189`; check process/firewall |
| OOM / process killed | `--lowvram`; lower resolution; free RAM; avoid SDXL on low-RAM hosts |
| Custom node import errors on 3.13 | Try a Python 3.12 venv; update the custom node |
| Manager missing | Clone Manager + `--enable-manager` + `manager_requirements.txt` |
| Black images | Wrong VAE / broken checkpoint; validate with stock SD1.5 first |
| Very slow generation | No GPU → expected with `--cpu`; use smaller models or a GPU machine |

---

## Relationship to Grok Imagine Cinematic Studio

| Path | Tooling |
|------|---------|
| Local open models / Comfy graphs | ComfyUI (this guide) |
| Studio orchestration, Production Bibles, agent suite | `grok-4.5` + Cinematic Studio skills |
| Imagine API video/image | `grok-imagine-video` / `grok-imagine-image` (not Comfy) |
| Optional long-context | `grok-4.3` (1M opt-in) |

Do **not** register Comfy checkpoints as Grok Build chat model slugs. Keep local weights under `ComfyUI/models/`.

Optional follow-ons (separate agent prompts):

1. Install a specific SDXL/NSFW checkpoint (e.g. Lustify) into `models/checkpoints/`.
2. Add custom nodes (Impact Pack, ControlNet aux, video helpers) **after** the core smoke test passes.
3. Point Studio workflows at exported Comfy stills under `artifacts/` for handoff into cinematic pipelines.

---

## Related docs

- Upstream: [ComfyUI README](https://github.com/comfyanonymous/ComfyUI) · [comfy.org](https://www.comfy.org/) · [comfy-cli](https://docs.comfy.org/comfy-cli/getting-started)
- This repo: [installation_guide.md](./installation_guide.md) · [Quick_Start_Guide.md](./Quick_Start_Guide.md)
- Models registry (Grok stack, not Comfy): `references/MODELS.md`

---

*Draft for SuperGrokPro / Cinematic Studio operators — July 2026*
