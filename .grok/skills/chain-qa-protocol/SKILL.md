---
name: chain-qa-protocol
description: Extend and stitch chain QA protocol for Grok Imagine Video 1.5 sequences. Runs the weighted 10-point gate before approving clips for extension or final stitch. Activate with RUN CHAIN QA REVIEW alongside Sequence Director and Cinematic Sequence Extender.
---

# Chain QA Protocol v3.6.5

**Pipeline skill** — complements QA Guardian's per-clip 16-point review.


## Model Layer (Grok 4.5 · studio v3.7.1)

| Layer | Slug | When |
|-------|------|------|
| Orchestration (default) | `grok-4.5` | Bibles, direction, agent loops |
| Long-context (opt-in) | `grok-4.3` | 1M memory banks (`--chat-model grok-4.3`) |
| Grok Build CLI | `grok-4.5` · `grok-build` | Skills / coding (≥ 0.2.93) |
| Imagine Video | `grok-imagine-video` / `1.5` | 1.0 cost · 1.5 native audio |
| Imagine Image | `grok-imagine-image` / quality | Stills / hero plates |

Prefer stable `prompt_cache_key` on multi-turn `grok-4.5` loops. Reasoning **high** for Bibles/QA/locks; opt into `grok-4.3` only for 1M. Imagine tools: `image_gen` / `image_edit` / `image_to_video` (not chat models). Full stack: `references/agents/MODEL_LAYER_v3.7.1.md` · `tools/models.py`.

**Checklist:** `.grok/skills/cinematic-sequence-extender/references/chain_qa_checklist.md`  
**Implementation:** `tools/sequence_chain.py` (`CHAIN_QA_CHECKS`)

## When to Activate

- Before **every** extend-from-last-frame generation
- Before **final stitch** of a multi-clip sequence
- After Continuity Guardian flags boundary risk

```
ACTIVATE ONLY Sequence Director, Cinematic Sequence Extender, Continuity Guardian, Quality Assurance Guardian
RUN CHAIN QA REVIEW
```

## 10-Point Checks (1–10 each)

| Key | Focus |
|-----|-------|
| `last_frame_continuity` | N+1 starts from N end state (**critical**) |
| `momentum_carryover` | Action, camera, emotion |
| `audio_momentum_sync` | Dialogue, SFX, music (**critical**) |
| `physics_realism` | Stitch boundary physics |
| `reference_propagation` | reference_image_id fidelity |
| `character_drift_boundary` | Identity at stitch (**critical**) |
| `lighting_color_match` | Light/color at boundary |
| `prop_environment_state` | Props, wardrobe, set |
| `transition_readiness` | Clean ending for extend (**critical**) |
| `stitch_artifact_risk` | Flicker, morphing, halos |

**Pass:** weighted score ≥ 7.0 and no critical check below 7.0.

## CLI

Scaffold (awaiting scores):
```bash
python tools/cinematic_studio_cli.py sequence qa "Neon Alley Chase" --clip clip_002
```

Score and gate:
```bash
python tools/cinematic_studio_cli.py sequence qa "Neon Alley Chase" --clip clip_002 \
  --scores '{"last_frame_continuity":8,"momentum_carryover":7,"audio_momentum_sync":9,"physics_realism":8,"reference_propagation":8,"character_drift_boundary":8,"lighting_color_match":7,"prop_environment_state":8,"transition_readiness":9,"stitch_artifact_risk":7}'
```

Sequence health:
```bash
python tools/cinematic_studio_cli.py sequence health "Neon Alley Chase"
```

Evidence inputs (drift / seam / AMV for QA Assist v2):
```bash
python tools/cinematic_studio_cli.py sequence drift-score --dna dna.json --images clip_001.png clip_002.png
python tools/cinematic_studio_cli.py sequence seam-report --prev last.png --next first.png
python tools/cinematic_studio_cli.py sequence amv-check --prev prev_amv.json --next next_amv.json
```

## Decisions

| Result | Next step |
|--------|-----------|
| **Go** | Approve extend / stitch |
| **Conditional Go** | Fix handoff fields, re-score |
| **No-Go** | Regenerate clip N; do not extend. Use `sequence regen plan|apply|run` (attempt budget + fix prompt from chain QA / drift / seam / memory bank) |

## Handoff Requirements Before QA

Clip must include: `last_frame_recap`, `momentum_vector`, `audio_momentum_vector`, `reference_image_id`, `continuity_state`.

Validate packets:
```bash
python .grok/skills/handoff-packet-validator/scripts/validate_handoff.py handoff.json
```