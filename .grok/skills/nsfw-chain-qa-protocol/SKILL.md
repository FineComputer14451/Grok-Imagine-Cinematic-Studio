---
name: nsfw-chain-qa-protocol
description: NSFW extend and stitch chain QA protocol for intimate Grok Imagine Video 1.5 sequences. Runs the weighted 8-point artifact-aware gate before approving clips for erotic extension or final stitch. Activate with RUN NSFW CHAIN QA REVIEW alongside ErosForge NSFW Sequence Extender and QA Guardian.
---

# NSFW Chain QA Protocol v3.6.5

**Pipeline skill** — complements QA Guardian's per-clip review for explicit/intimate sequences.


## Model Layer (Grok 4.5 · studio v3.6.7)

| Layer | Slug | When |
|-------|------|------|
| Orchestration (default) | `grok-4.5` | Bibles, direction, agent loops |
| Long-context (opt-in) | `grok-4.3` | 1M memory banks (`--chat-model grok-4.3`) |
| Grok Build CLI | `grok-4.5` · `grok-build` | Skills / coding (≥ 0.2.93) |
| Imagine Video | `grok-imagine-video` / `1.5` | 1.0 cost · 1.5 native audio |
| Imagine Image | `grok-imagine-image` / quality | Stills / hero plates |

Prefer stable `prompt_cache_key` on multi-turn `grok-4.5` loops. Full stack: `references/agents/MODEL_LAYER_v3.6.7.md` · `tools/models.py`.

**Checklist:** `.grok/skills/nsfw-chain-qa-protocol/references/nsfw_chain_qa_checklist.md`  
**Implementation:** `tools/nsfw_sequence_extender.py` (`NSFW_CHAIN_QA_CHECKS`)

## When to Activate

- Before **every** NSFW extend-from-last-frame generation
- Before **final stitch** of a multi-clip intimate sequence
- After ErosForge flags artifact risk or continuity drift at stitch boundary

Requires explicit opt-in:

```
ACTIVATE EROSFORGE
RUN NSFW CHAIN QA REVIEW
```

## 8-Point Checks (1–10 each)

| Key | Focus | Critical |
|-----|-------|----------|
| `hand_finger_integrity` | Hands/fingers — no extra digits, natural pose | ✓ |
| `skin_texture_consistency` | Skin detail — pores, tone, marks at stitch | |
| `fabric_cloth_physics` | Fabric drape, tension, displacement | |
| `explicit_area_artifact_risk` | No morphing, duplication in explicit zones | ✓ |
| `body_proportion_stability` | Proportions stable at stitch boundary | ✓ |
| `intimate_physics_fidelity` | Weight transfer, skin deformation, momentum | ✓ |
| `erotic_tension_carryover` | Sensual tension curve across boundary | |
| `lighting_skin_modeling` | Motivated light flatters skin at stitch | |

**Pass:** weighted score ≥ 7.0 and no critical check below 7.0.

## CLI

Scaffold (awaiting scores):
```bash
python tools/cinematic_studio_cli.py nsfw extend qa "Intimate Sequence" --clip clip_002
```

Score and gate:
```bash
python tools/cinematic_studio_cli.py nsfw extend qa "Intimate Sequence" --clip clip_002 \
  --scores '{"hand_finger_integrity":8,"skin_texture_consistency":7,"fabric_cloth_physics":8,"explicit_area_artifact_risk":8,"body_proportion_stability":8,"intimate_physics_fidelity":7,"erotic_tension_carryover":8,"lighting_skin_modeling":7}'
```

Skill script (sequence file):
```bash
python .grok/skills/nsfw-chain-qa-protocol/scripts/nsfw_chain_qa.py "Intimate Sequence" --clip clip_002
```

## Decisions

| Result | Next step |
|--------|-----------|
| **Go** | Approve extend / stitch |
| **Conditional Go** | Apply artifact fixes from QA scaffold, re-score |
| **No-Go** | Regenerate clip N; do not extend |

## Handoff Requirements Before QA

Clip must include ErosForge state: `intimacy_physics_state`, `post_scene_state`, `clothing_displacement_log`, `emotional_residue`.

Validate intimacy handoff:
```bash
python .grok/skills/handoff-packet-validator/scripts/validate_handoff.py intimacy_handoff.json
```