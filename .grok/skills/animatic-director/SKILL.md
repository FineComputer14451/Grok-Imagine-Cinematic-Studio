---
name: animatic-director
description: Low-cost animatic and previsualization workflow before Grok Imagine Video 1.5 spend. Plans storyboard beats still tiers and timing using draft image models and short motion tests to validate pacing under quota. Activate with ACTIVATE ANIMATIC DIRECTOR before long-form or hero batch sessions. Optimized for grok-4-auto grok-v9-4p5-multi grok-v9-4p5-chat-expert with dual Imagine Video 1.0 and 1.5 Native.
---

# Animatic Director v3.8.6 (Grok 4.6 / v9-4p5 · Pre-Vis / Cost Gate)

**Pipeline skill** — quota-saving previsualization before full video production. Validate **story rhythm, shot coverage, and identity anchors** at roughly **10–20%** of full production cost.

**Engine:** `tools/animatic_orchestrator.py` · CLI `animatic plan|list|show|promote`

## Model Layer (Grok 4.6 / v9-4p5)

| Task type | Preferred model | Reasoning |
|-----------|-----------------|-----------|
| Multi-agent orchestration / handoff synthesis | `grok-v9-4p5-multi` | high |
| Specialist deep craft / QA / identity-critical | `grok-v9-4p5-chat-expert` | high |
| Routine status / draft passes | `grok-4-auto` | medium |

**Stack default:** cinematic+Build API/chat **`grok-4.6`** (CLI ≥ 1.0.5 · fork `grok-build` or `grok-4.6`; `grok-4.5` aliases wrap 4.6). Opt-in 1M: `grok-4.3`.  
**Registry:** `tools/models.py` · `references/agents/MODEL_LAYER_v4.5.md` · `models verify`

```yaml
model_compatibility:
  - grok-v9-4p5-chat-expert
  - grok-v9-4p5-multi
  - grok-4-auto
preferred_model: grok-v9-4p5-multi
```

### Imagine Video dual-path (when this skill touches video)
- **1.5 Native** — preferred for hero / final motion with audio when budget allows
- **1.0** — cost default / draft / pre-viz; label outputs so downstream agents do not assume 1.5 capabilities

## When to Activate

- Before long-form sequences or multi-shot hero batches  
- When quota is tight and pacing/coverage is unproven  
- New production after Production Bible / Narrative Arc heatmap  
- User says: `ACTIVATE ANIMATIC DIRECTOR`, `PLAN ANIMATIC`, `PREVIS BOARD`, `PROMOTE ANIMATIC FRAME`

## When to Skip

| Situation | Skip animatic? |
|-----------|----------------|
| Single hero still → one short clip | Usually yes |
| Trailer / teaser under ~15s total | Optional |
| Bible + beat map already locked with existing plates | Optional light pass |
| User explicitly wants full video spend | Director override |

## Activation

```
ACTIVATE ANIMATIC DIRECTOR
```

Typical stack:

```
ACTIVATE ANIMATIC DIRECTOR
ACTIVATE ONLY Animatic Director, Narrative Arc Strategist, Reference Asset Curator, Workflow Quota Optimizer
```

Begin: **"Initiating Animatic Protocol v3.8.6 (Grok 4.6 / v9-4p5)…"**

## Goal

Prove the cut **before** hero `image-quality` plates and long `1.5` / multi-clip video:

1. Story rhythm holds at draft stills  
2. Coverage is sufficient (no missing story beats)  
3. Character anchors are lockable  
4. Risky shots are flagged (stunt / VFX / extend)  

## Tier Strategy (with Reference Curator)

| Phase | Asset tier | Image model | Video |
|-------|------------|-------------|--------|
| Storyboard stills | `draft` | `grok-imagine-image` | — |
| Layout / composition | `standard` | `grok-imagine-image` | — |
| Hero anchor lock | `hero` | `grok-imagine-image-quality` | — |
| Motion probe (optional) | `draft` | — | `grok-imagine-video` short (≈6s) |

Promotion path: **draft → standard → hero** (`animatic promote`).

## Workflow

1. **Beat map** — Narrative Arc heatmap → **8–15** storyboard frames (or project-specific count)  
2. **Plan board** — CLI `animatic plan` with duration hints + tiers  
3. **Still pass** — draft/standard `image_gen` / batch only; **no long video yet**  
4. **Timing board** — seconds per beat vs target sequence duration  
5. **Identity check** — promote 1–2 anchors per character to **hero** after DNA/Identity Lock  
6. **Optional motion probe** — 3–5s/6s clips only for complex camera or physics  
7. **Cost gate** — animatic ≤ **~20%** of full production estimate (override requires Studio Director)  
8. **Go/No-Go** → SFW Batch Orchestrator / Sequence Director / I2V Specialist  

## CLI

```bash
# Plan board (beat = description:seconds OR tier:description:seconds)
python tools/cinematic_studio_cli.py animatic plan "Act 1 Previs" \
  --duration 60 \
  --beat "draft:Wide establish golden hour:6" \
  --beat "draft:Hero at window:4" \
  --beat "standard:Reveal beat medium:5" \
  --beat "hero:Anchor portrait close-up:4"

# From JSON beat list
python tools/cinematic_studio_cli.py animatic plan "Act 1 Previs" \
  --file artifacts/animatics/beats.json --duration 90

python tools/cinematic_studio_cli.py animatic list
python tools/cinematic_studio_cli.py animatic show "act-1-previs"

# Promote frame after still QA
python tools/cinematic_studio_cli.py animatic promote "act-1-previs" \
  --frame frame_002 --tier hero --score 8.5
```

Artifacts: `artifacts/animatics/{slug}.json` (+ markdown via show/export).

### Cost helpers

```bash
python tools/cinematic_studio_cli.py quota estimate --duration 90 --images 12
python tools/cinematic_studio_cli.py cost-simulate --duration 90 --complexity medium
```

Board `cost_estimate` includes `animatic_credits`, `full_production_credits`, `animatic_pct_of_full`, `within_budget`.

## Deliverables

1. **Animatic board** — ordered frames with tier, duration hints, model routes  
2. **Locked anchors** — frame IDs / asset IDs approved for i2v  
3. **Risk list** — stunt, VFX, multi-cast, long extend  
4. **Budget report** — animatic % of full estimate  
5. **Go/No-Go** + handoff to Sequence Director or SFW Batch Orchestrator  

## Output Format

```text
ANIMATIC COMPLETE · v3.7.1
Board: <title> | Slug: <slug>
Frames: N | Target: Xs
Cost: <animatic_cr> cr (~P% of full <full_cr>)
Within budget: yes|no
Locked anchors: frame_…
Risks: …
Decision: GO → Sequence Director / SFW Batch | NO-GO → replan beats
Artifacts: artifacts/animatics/<slug>.json
```

## Integration

| Partner | Role |
|---------|------|
| Mega Production Architect / Production Bible | Project scope |
| Narrative Arc Strategist | Heatmap → beats |
| Workflow Quota Optimizer | Budget cap |
| Reference Asset Curator | Tier enforcement / ASSET_MANIFEST |
| Character DNA / Identity Lock | Hero anchor lock |
| SFW Batch Orchestrator | Post-animatic shot spend |
| Sequence Director / Extender | Full clip plan after Go |
| Image-to-Video Specialist | Motion from locked stills |
| Studio Director | Override budget / skip rules |

## Reasoning (Grok 4.6)

| Task | Reasoning |
|------|-----------|
| Simple 8-frame board | medium |
| Multi-act risk + budget go/no-go | **high** |
| Hero promote for identity | **high** |

---

*Animatic Director v3.8.6 — Grok 4.6 / v9-4p5 · draft stills → promote heroes → gate video spend*
