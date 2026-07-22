# Imagine Agent Mode Handoff — Extend-from-Frame Priority (Default)

**Protocol:** 4.5-extend-priority  
**Status:** New default for all multi-clip / long-form Agent Mode handoffs  
**Owner:** Studio Director + Team Leader  
**Purpose:** Maximize continuity and minimize quota cost by forcing native Extend-from-Frame chains instead of independent clip generation.

---

## When to Use This Template

- Any sequence longer than a single clip
- Hero reveals, trailers, emotional arcs, action beats that must feel continuous
- Quota-constrained sessions
- Whenever identity lock, lighting, or motion continuity is critical

**Do not use independent-clip mode** unless the story requires a hard cut, new location, or the user explicitly overrides.

---

## Quick Copy Block (Markdown Handoff)

```markdown
## Handoff: Imagine Agent Mode — Extend Priority (v4.5)

**From:** Studio Director (+ Sequence Director / I2V Specialist / Sonic Architect)
**To:** Imagine execution surface: grok_build_tools | grok_agent_acp | xai_api
**Subject:** <clip_id> · **Mode:** image_to_video
**Generation Strategy:** extend_from_frame_chain (NON-NEGOTIABLE unless user override)
**Preferred Chat Model:** grok-v9-4p5-multi

### Context Summary
- Project: <title>
- Source clip: <source_clip_id> (must be Chain-QA approved)
- Video version: 1.5 (preferred) or 1.0 fallback
- Tier: hero | standard

### Key Decisions / State
- generation_strategy: extend_from_frame_chain
- extend_protocol: LAST_FRAME + MOTION_VECTOR + AUDIO_CUE
- VIDEO_PIPELINE_SPEC locked with stitch_priority=high
- DNA / Identity Lock: locked
- Quota optimization: prefer_extend_over_new_clip = true

### Required Continuity Fields
- last_frame_recap: <detailed description of approved last frame>
- momentum_vector: { action, camera, emotion, physics_notes }
- audio_momentum_vector: { energy, tone, spatial, intensity }

### Quota Optimization
- prefer_extend_over_new_clip: true
- max_new_independent_clips: 0
- estimated_savings: ~35-55%
- buffer_remaining_pct: 15

### Execution Request
1. Confirm source last_frame is present and QA-approved
2. Inject LAST_FRAME_RECAP + momentum vectors into prompt
3. Run native extend / image_to_video using last_frame as primary reference
4. Extract new last_frame + refresh vectors
5. Run 10-point Chain QA before any further extension
6. Return via return_path to Sequence Director

### Quality / Continuity Notes
- Chain QA mandatory between every extension
- No silent independent clip generation
- Identity Lock must remain injected
- Version consistency (do not mix 1.0 and 1.5 in the same chain without Director approval)
```

---

## JSON Template Location

Canonical machine-readable template:

`skills/studio-director/references/templates/imagine_agent_mode_handoff_extend_priority.json`

Copy this file into any Production Bible under:

`production-bible/<project>/handoffs/templates/`

or reference it directly when issuing `imagine agent-handoff`.

---

## Studio Director Enforcement Rules (now default)

1. For any multi-clip work, **default** `generation_strategy` to `"extend_from_frame_chain"`.
2. Require a valid upstream `sequence_extend_handoff` (or equivalent last_frame + momentum data) before emitting this packet.
3. Block video spend if `last_frame_recap` or `momentum_vector` is missing/weak when strategy is extend.
4. Always include the `quota_optimization` and `chain_control` objects.
5. Prefer Imagine Video 1.5 when native audio / physics continuity is needed; fall back to 1.0 only with explicit cost justification.
6. After generation, the next packet must be built from the *new* last frame — never restart from a still unless intentionally breaking the chain.

---

## Integration Points

| Agent / Skill                    | Role in this path                          |
|----------------------------------|--------------------------------------------|
| Sequence Director                | Owns dependency graph & health             |
| Cinematic Sequence Extender      | Plans the extend steps                     |
| Image-to-Video Specialist        | Crafts motion-ready extend prompt          |
| Continuity Consistency Guardian  | Validates LAST_FRAME_RECAP & vectors       |
| Workflow Quota Optimizer         | Confirms savings & buffer                  |
| Sonic Architect                  | Supplies / updates AUDIO_MOMENTUM_VECTOR   |
| Handoff Packet Validator         | Must pass (extend fields present)          |
| Quality Assurance Guardian       | Final Chain QA gate                        |

---

*Adopted as default Agent Mode handoff policy — July 2026 · Team Leader / Studio Director*
