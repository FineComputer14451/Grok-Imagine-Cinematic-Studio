---
name: nsfw-sequence-extender
description: NSFW sensual sequence extension from reference frame or short clip to 30-120+ seconds. Plans erotic tension curves, Grok Imagine prompt chains, extend-from-frame instructions, camera pacing, and artifact-aware chain QA. Integrates Cinematic Sequence Extender, ErosForge, and NSFW Quota Orchestrator. Activate with ACTIVATE NSFW_SEQUENCE_EXTENDER or when extending intimate 1.5 sequences. Uses Grok 4.5 orchestration.
---

# NSFW Sequence Extender v3.7.1 (Grok 4.5 · Sensual Extension)

**Explicit opt-in long-form intimate extension.** Extends reference frames or short sensual clips into seamless 30–120+ second sequences with erotic tension curves, prompt chains, extend-from-frame state, and artifact-aware chain QA.

**Requires:** `ACTIVATE EROSFORGE` first  
**Core library:** `tools/nsfw_sequence_extender.py`  
**Base protocols:** `cinematic-sequence-extender` · `erosforge-nsfw-director`  
**Quota:** `nsfw-quota-orchestrator` · **Gate:** `nsfw-chain-qa-protocol`

## Model Layer (Grok 4.5 · studio v3.7.1)

| Layer | Slug | When |
|-------|------|------|
| Orchestration (default) | `grok-4.5` | Extend plans, tension curves, stitch risk |
| Long-context (opt-in) | `grok-4.3` | 1M long intimate chain banks only |
| Grok Build CLI | `grok-4.5` · `grok-build` | Skills / coding (≥ 0.2.93) |
| Imagine Video | `grok-imagine-video` / `1.5` | Prefer **1.5** when breath/audio matter; else 1.0 cost |
| Imagine Image | `grok-imagine-image` / quality | Intimate keyframes / plates |

Prefer stable `prompt_cache_key` (project slug). Reasoning **high** for extend risk, intimacy state carryover, and stitch go/no-go. Full stack: `references/agents/MODEL_LAYER_v3.7.1.md` · `tools/models.py` · `models verify`.

## Activation Stack

```
ACTIVATE EROSFORGE
ACTIVATE NSFW_SEQUENCE_EXTENDER
ACTIVATE ONLY Cinematic Sequence Extender, ErosForge NSFW Director,
  Identity Lock Specialist, NSFW Quota Orchestrator
```

Begin: **"Initiating NSFW Sequence Extension Protocol v3.7.1 (Grok 4.5)…"**  
Adults only. Refuse minors.

## Core Mandate

1. Multi-clip plan with **erotic tension curve** (anticipation → peak → afterglow)  
2. Ready-to-paste **prompt chains** per clip  
3. **Extend-from-frame** instructions with ErosForge state propagation  
4. Camera movement + pacing per phase  
5. Artifact avoidance in explicit zones (hands, skin, fabric)  
6. **NSFW chain QA** before every extend (8 intimate checks)  
7. Lock `VIDEO_PIPELINE_SPEC` + DNA inject on every clip  

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
5. **Peak** — hero explicit beat (one primary peak per sequence)  
6. **Afterglow** — deceleration, emotional residue  

## CLI Workflow

```bash
# Plan full 90s from reference still
python tools/cinematic_studio_cli.py nsfw extend plan "Candlelit Embrace" \
  --duration 90 --profile passionate \
  --reference "Woman in silk robe, candlelit bedroom, warm amber light" \
  --source reference_frame

# From short clip
python tools/cinematic_studio_cli.py nsfw extend plan "Slow Seduction" \
  --duration 60 --source short_clip \
  --reference "10s approved clip, last frame: bodies close, hands on waist"

# Export prompt chain / single extend / camera
python tools/cinematic_studio_cli.py nsfw extend chain "candlelit-embrace"
python tools/cinematic_studio_cli.py nsfw extend prompt "candlelit-embrace" --clip clip_003
python tools/cinematic_studio_cli.py nsfw extend camera --phase escalation --duration 10

# NSFW chain QA
python tools/cinematic_studio_cli.py nsfw extend qa "candlelit-embrace" --clip clip_002

# Custom beats
python tools/cinematic_studio_cli.py nsfw extend plan "Custom Arc" --duration 120 --profile slow_burn \
  --beat "Eyes meet across candlelight" \
  --beat "She turns, robe slips from shoulder" \
  --beat "His hand traces her spine"
```

## State Propagation (Every Extend)

Carry on every handoff:

| Field | Source |
|-------|--------|
| `intimacy_physics_state` | ErosForge |
| `post_scene_state` | ErosForge |
| `clothing_displacement_log` | ErosForge / Continuity |
| `emotional_residue` | Performance + ErosForge |
| `LAST_FRAME_RECAP` | Sequence Extender |
| `MOMENTUM_VECTOR` | Sequence Extender |
| Character DNA inject | Identity Lock (verbatim) |

Validate:

```bash
python .grok/skills/handoff-packet-validator/scripts/validate_handoff.py intimacy_handoff.json
```

## Output Artifacts

Saved under `sequences/<slug>/`:

- `sequence.json` — blueprint + NSFW metadata  
- `prompt_chain.json` — prompts per clip  
- `extension_plan.md` — human plan + tension curve  

## Integration Chain

```
Reference frame/clip → nsfw extend plan → Identity Lock DNA inject
  → Generate clip_001 → NSFW chain QA (Go) → LAST_FRAME_RECAP
  → nsfw extend prompt clip_002 → extend → repeat → stitch
  → nsfw-quota-orchestrator record → daily report
  → QA Guardian → Assembly / Polish as needed
```

## Agent Commands

- `PLAN NSFW EXTENSION` — full sequence from reference  
- `SHOW PROMPT CHAIN` — export all clip prompts  
- `EXTEND NEXT BEAT` — single extend prompt  
- `SUGGEST EROTIC CAMERA` — camera/pacing for phase  
- `RUN NSFW CHAIN QA` — intimate artifact checklist  

## Hard Blocks

| Condition | Action |
|-----------|--------|
| No ErosForge activation | Block |
| NSFW Chain QA No-Go | Regen — no extend |
| Unlocked DNA on hero | Identity Lock first |
| Missing intimacy state | Reject handoff |

## References (skill)

- `references/nsfw_extend_protocol.md`  
- `references/erotic_pacing_curve.md`  
- `references/camera_erotic_vocabulary.md`  
- `references/artifact_avoidance_checklist.md`  

## Reasoning (Grok 4.5)

| Task | Reasoning |
|------|-----------|
| Single extend plan | high |
| 30–120s multi-clip intimate arc | **high** |
| 1.0 vs 1.5 for breath/audio | **high** |

---

*NSFW Sequence Extender v3.7.1 — Grok 4.5 · ErosForge required · chain QA every extend*
