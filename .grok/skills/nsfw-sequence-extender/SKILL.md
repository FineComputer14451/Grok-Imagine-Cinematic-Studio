---
name: nsfw-sequence-extender
description: NSFW sensual sequence extension from reference frame or short clip to 30-120+ seconds. Plans erotic tension curves, Grok Imagine prompt chains, extend-from-frame instructions, camera pacing, and artifact-aware chain QA. Integrates Cinematic Sequence Extender, ErosForge, and NSFW Quota Orchestrator. Activate with ACTIVATE NSFW_SEQUENCE_EXTENDER or when extending intimate 1.5 sequences.
---

# NSFW Sequence Extender v1.0

**Activate:** `ACTIVATE EROSFORGE` → `ACTIVATE NSFW_SEQUENCE_EXTENDER`


## Model Layer (Grok 4.5 · studio v3.7.1)

| Layer | Slug | When |
|-------|------|------|
| Orchestration (default) | `grok-4.5` | Bibles, direction, agent loops |
| Long-context (opt-in) | `grok-4.3` | 1M memory banks (`--chat-model grok-4.3`) |
| Grok Build CLI | `grok-4.5` · `grok-build` | Skills / coding (≥ 0.2.93) |
| Imagine Video | `grok-imagine-video` / `1.5` | 1.0 cost · 1.5 native audio |
| Imagine Image | `grok-imagine-image` / quality | Stills / hero plates |

Prefer stable `prompt_cache_key` on multi-turn `grok-4.5` loops. Reasoning **high** for Bibles/QA/locks; opt into `grok-4.3` only for 1M. Imagine tools: `image_gen` / `image_edit` / `image_to_video` (not chat models). Full stack: `references/agents/MODEL_LAYER_v3.7.1.md` · `tools/models.py`.

Extends high-quality reference frames or short sensual clips into seamless 30–120+ second cinematic sequences.

**Core library:** `tools/nsfw_sequence_extender.py`  
**Base protocols:** `cinematic-sequence-extender` skill + `erosforge-nsfw-director`  
**Quota:** `nsfw-quota-orchestrator` for batch cost planning

## Core Mandate

- Plan multi-clip extensions with **erotic tension curve** (anticipation → peak → afterglow)
- Output **ready-to-paste Grok Imagine prompt chains** per clip
- Provide **extend-from-frame instructions** with ErosForge state propagation
- Recommend **camera movement and pacing** per beat for maximum impact
- Enforce **artifact avoidance** in explicit zones (hands, skin, fabric)
- Run **NSFW chain QA** before every extend (8 intimate-specific checks)

## Activation Stack

```
ACTIVATE EROSFORGE
ACTIVATE NSFW_SEQUENCE_EXTENDER
ACTIVATE ONLY Cinematic Sequence Extender, ErosForge NSFW Director, Identity Lock Specialist, NSFW Quota Orchestrator
```

## CLI Workflow

```bash
# Plan full 90s extension from reference still
python tools/cinematic_studio_cli.py nsfw extend plan "Candlelit Embrace" \
  --duration 90 --profile passionate \
  --reference "Woman in silk robe, candlelit bedroom, warm amber light, reference still locked" \
  --source reference_frame

# Plan from existing short clip
python tools/cinematic_studio_cli.py nsfw extend plan "Slow Seduction" \
  --duration 60 --source short_clip --reference "10s approved clip, last frame: bodies close, hands on waist"

# Export prompt chain only
python tools/cinematic_studio_cli.py nsfw extend chain "candlelit-embrace"

# Single extend prompt (clip N from clip N-1)
python tools/cinematic_studio_cli.py nsfw extend prompt "candlelit-embrace" --clip clip_003

# Camera/pacing for a phase
python tools/cinematic_studio_cli.py nsfw extend camera --phase escalation --duration 10

# NSFW chain QA scaffold
python tools/cinematic_studio_cli.py nsfw extend qa "candlelit-embrace" --clip clip_002

# Custom beat overrides
python tools/cinematic_studio_cli.py nsfw extend plan "Custom Arc" --duration 120 --profile slow_burn \
  --beat "Eyes meet across candlelight" \
  --beat "She turns, robe slips from shoulder" \
  --beat "His hand traces her spine"
```

## Tension Profiles

| Profile | Clip Length | Character |
|---------|-------------|-----------|
| `slow_burn` | 10–14s | Extended anticipation, lingering camera |
| `passionate` | 8–12s | Balanced build → peak (default) |
| `intense` | 6–10s | Faster escalation, shorter peaks |

## Erotic Phases (Auto-Allocated)

1. **Anticipation** — desire established, distance closing
2. **Approach** — first touch approaching, breath sync
3. **Contact** — skin contact, fabric displacement
4. **Escalation** — momentum intensifies, weight transfer
5. **Peak** — hero explicit beat (one per sequence)
6. **Afterglow** — deceleration, emotional residue

## Output Artifacts (per sequence)

Saved to `sequences/<slug>/`:
- `sequence.json` — full blueprint with NSFW metadata
- `prompt_chain.json` — ready-to-use prompts per clip
- `extension_plan.md` — human-readable plan with tension curve

## NSFW Chain QA (Critical — No-Go if <7)

- `hand_finger_integrity`
- `explicit_area_artifact_risk`
- `body_proportion_stability`
- `intimate_physics_fidelity`

Plus: skin texture, fabric physics, tension carryover, lighting.

Reference: `references/artifact_avoidance_checklist.md`

## Integration Chain

```
Reference frame/clip → nsfw extend plan → Identity Lock DNA inject
  → Generate clip_001 → NSFW chain QA (Go) → LAST_FRAME_RECAP
  → nsfw extend prompt clip_002 → extend → repeat → stitch
  → nsfw-quota-orchestrator record → daily report
```

## Agent Commands

- `PLAN NSFW EXTENSION` — full sequence from reference
- `SHOW PROMPT CHAIN` — export all clip prompts
- `EXTEND NEXT BEAT` — build single extend prompt
- `SUGGEST EROTIC CAMERA` — camera/pacing for phase
- `RUN NSFW CHAIN QA` — intimate artifact checklist

## References

- `references/nsfw_extend_protocol.md` — ErosForge + 1.5 extend protocol
- `references/erotic_pacing_curve.md` — tension allocation by profile
- `references/camera_erotic_vocabulary.md` — lens, move, framing per phase
- `references/artifact_avoidance_checklist.md` — explicit zone QA