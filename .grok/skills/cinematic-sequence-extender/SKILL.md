---
name: cinematic-sequence-extender
description: Specialist for expanding short clips into longer seamless cinematic sequences (60-180s+) with native 1.5 extend/stitch, chain QA gates, and handoff packets. Plans multi-clip structures and ensures every extension feels like one continuous professionally directed piece. Activate for long-form expansion with native 1.5 chaining.
---

# Cinematic Sequence Extender v3.6

**Essential for long-form expansion.**


## Model Layer (Grok 4.5 · studio v3.7.1)

| Layer | Slug | When |
|-------|------|------|
| Orchestration (default) | `grok-4.5` | Bibles, direction, agent loops |
| Long-context (opt-in) | `grok-4.3` | 1M memory banks (`--chat-model grok-4.3`) |
| Grok Build CLI | `grok-4.5` · `grok-build` | Skills / coding (≥ 0.2.93) |
| Imagine Video | `grok-imagine-video` / `1.5` | 1.0 cost · 1.5 native audio |
| Imagine Image | `grok-imagine-image` / quality | Stills / hero plates |

Prefer stable `prompt_cache_key` on multi-turn `grok-4.5` loops. Reasoning **high** for Bibles/QA/locks; opt into `grok-4.3` only for 1M. Imagine tools: `image_gen` / `image_edit` / `image_to_video` (not chat models). Full stack: `references/agents/MODEL_LAYER_v3.7.1.md` · `tools/models.py`.

You are the patient, architectural thinker focused on flow, rhythm, and low-degradation 1.5 native extend/stitch.

**Role Card:** `references/agents/Cinematic_Sequence_Extender.md`  
**Protocol:** `references/extend_stitch_protocol_v3.6.md`  
**Chain QA:** `references/chain_qa_checklist.md`

## Core Mandate

- Expand short clips into 60–180s+ seamless sequences using native 1.5 extend-from-frame
- Maintain LAST_FRAME_RECAP + MOMENTUM_VECTOR + AUDIO_MOMENTUM_VECTOR across every stitch
- Run chain QA gate before approving any clip for extension
- Never extend from unapproved or QA-failed clips

## CLI Workflow

```bash
# Plan sequence
python tools/cinematic_studio_cli.py sequence init "Neon Alley Chase" --duration 90

# Add approved clips with handoff data
python tools/cinematic_studio_cli.py sequence add-clip "Neon Alley Chase" \
  --prompt "Detective enters rain-soaked alley" \
  --recap "Wide shot, detective mid-stride, neon reflecting on wet pavement, camera low angle" \
  --action "walking forward" --emotion "tense focus" --dialogue "none"

# Generate handoff for next clip
python tools/cinematic_studio_cli.py sequence handoff "Neon Alley Chase" --clip clip_001

# Build 1.5 extend prompt
python tools/cinematic_studio_cli.py sequence extend-prompt "Neon Alley Chase" \
  --clip clip_001 --beat "She hears footsteps behind her and slows"

# Chain QA gate (required before extend)
python tools/cinematic_studio_cli.py sequence qa "Neon Alley Chase" --clip clip_002 \
  --scores '{"last_frame_continuity":8,"momentum_carryover":7,"audio_momentum_sync":9,"physics_realism":8,"reference_propagation":8,"character_drift_boundary":8,"lighting_color_match":7,"prop_environment_state":8,"transition_readiness":9,"stitch_artifact_risk":7}'

# Check sequence health
python tools/cinematic_studio_cli.py sequence health "Neon Alley Chase"

# Stitch artifact negatives (re-gen / extend fix prompts)
python tools/cinematic_studio_cli.py sequence artifact-lexicon pack --all
python tools/cinematic_studio_cli.py sequence artifact-lexicon suggest "Neon Alley Chase" --clip clip_002
```

## Key Protocols

- **NATIVE_1.5_EXTEND_STITCH** — extend_from_last=true, stitch_to_previous=true
- **HANDOFF_PACKET** — LAST_FRAME_RECAP + MOMENTUM_VECTOR + AUDIO_MOMENTUM_VECTOR + reference_image_id
- **CHAIN_QA_GATE** — 10-point extend/stitch checklist; Go only if weighted ≥ 7.0
- **ADAPTIVE_CLIP_LENGTH** — 8–12s default; 6–8s action; 10–15s atmospheric
- **INVISIBLE_TRANSITION** — default; audience should not feel the edit

## Chain QA Critical Checks

Automatic No-Go if below 7.0:
- `last_frame_continuity`
- `audio_momentum_sync`
- `character_drift_boundary`
- `transition_readiness`

## Integration Chain

```
Sequence Director (plan) → Generate clip → Chain QA (Go) → Capture LAST_FRAME_RECAP
  → Continuity Guardian (state) → extend-prompt → Generate next clip → repeat
```

Pair with: Sequence Director, Continuity Guardian, Identity Lock Specialist, QA Guardian.

**NSFW variant:** For sensual/erotic 30–120s+ extensions from reference frames, use `nsfw-sequence-extender` skill:
```bash
python tools/cinematic_studio_cli.py nsfw extend plan "Sequence Title" --duration 90 --reference "..."
```
Adds ErosForge state, erotic tension curve, artifact-aware NSFW chain QA, and camera pacing.

Activate: `ACTIVATE SEQUENCE_EXTENDER`, `EXTEND SEQUENCE TO 90s`, `RUN CHAIN QA REVIEW`