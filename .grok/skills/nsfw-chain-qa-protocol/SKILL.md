---
name: nsfw-chain-qa-protocol
description: NSFW extend and stitch chain QA protocol for intimate Grok Imagine Video 1.5 sequences. Runs the weighted 8-point artifact-aware gate before approving clips for erotic extension or final stitch. Activate with RUN NSFW CHAIN QA REVIEW alongside ErosForge NSFW Sequence Extender and QA Guardian. Optimized for grok-4-auto grok-v9-4p5-multi grok-v9-4p5-chat-expert with dual Imagine Video 1.0 and 1.5 Native.
---

# NSFW Chain QA Protocol v3.8.6 (Grok 4.6 / v9-4p5 · Intimate Chain Gate)

**Pipeline skill** — weighted 8-point artifact-aware gate for explicit/intimate extend and stitch. Complements QA Guardian’s per-clip 16-point review; does **not** replace it.

**Checklist:** `.grok/skills/nsfw-chain-qa-protocol/references/nsfw_chain_qa_checklist.md`  
**Implementation:** `tools/nsfw_sequence_extender.py` (`NSFW_CHAIN_QA_CHECKS`)  
**Script:** `.grok/skills/nsfw-chain-qa-protocol/scripts/nsfw_chain_qa.py`

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
preferred_model: grok-v9-4p5-chat-expert
```

### Imagine Video dual-path (when this skill touches video)
- **1.5 Native** — preferred for hero / final motion with audio when budget allows
- **1.0** — cost default / draft / pre-viz; label outputs so downstream agents do not assume 1.5 capabilities

## When to Activate

- Before **every** NSFW extend-from-last-frame generation  
- Before **final stitch** of multi-clip intimate sequence  
- After ErosForge flags artifact risk or continuity drift at stitch boundary  
- User says: `RUN NSFW CHAIN QA REVIEW`, `NSFW CHAIN QA`

Requires explicit opt-in:

```
ACTIVATE EROSFORGE
RUN NSFW CHAIN QA REVIEW
```

Begin: **"Running NSFW Chain QA Protocol v3.8.6 (Grok 4.6 / v9-4p5)…"**

## Philosophy

> Critical checks veto averages. Hands and explicit zones fail closed. No extend on No-Go.

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

**Pass:** weighted score ≥ **7.0** and **no critical check below 7.0**.

## Handoff Requirements Before QA

Clip must include ErosForge state:

- `intimacy_physics_state`  
- `post_scene_state`  
- `clothing_displacement_log`  
- `emotional_residue`  

```bash
python .grok/skills/handoff-packet-validator/scripts/validate_handoff.py intimacy_handoff.json
```

Reject incomplete intimacy handoffs before scoring.

## CLI Workflow

Scaffold (awaiting scores):

```bash
python tools/cinematic_studio_cli.py nsfw extend qa "Intimate Sequence" --clip clip_002
```

Score and gate:

```bash
python tools/cinematic_studio_cli.py nsfw extend qa "Intimate Sequence" --clip clip_002 \
  --scores '{"hand_finger_integrity":8,"skin_texture_consistency":7,"fabric_cloth_physics":8,"explicit_area_artifact_risk":8,"body_proportion_stability":8,"intimate_physics_fidelity":7,"erotic_tension_carryover":8,"lighting_skin_modeling":7}'
```

Skill script:

```bash
python .grok/skills/nsfw-chain-qa-protocol/scripts/nsfw_chain_qa.py "Intimate Sequence" --clip clip_002
```

## Decisions

| Result | Next step |
|--------|-----------|
| **Go** | Approve extend / stitch |
| **Conditional Go** | Apply artifact fixes from scaffold, re-score |
| **No-Go** | Regenerate clip N; **do not** extend; optional Arc Replan |

## Workflow Loop

```
Clip N generated
  → Validate intimacy handoff
  → NSFW Chain QA (8-point)
  → Go → extend to N+1 / stitch
  → No-Go → regen (or ARC_REPLAN if remaining arc broken)
  → QA Guardian 16-point for client delivery
```

## Output Format

```text
NSFW CHAIN QA · v3.7.1
Sequence: … | Clip: …
Weighted: X.X / 10 | Critical floor: min(critical)
Decision: Go | Conditional Go | No-Go
Fails: …
Fixes ranked: …
Next: extend | regen | Arc Replan | stitch blocked
```

## Integration

| Partner | Role |
|---------|------|
| ErosForge | Intimacy state source |
| NSFW Sequence Extender | Extend plans gated by this QA |
| Identity Lock | Body/face consistency |
| Continuity Guardian | Prop/env + clothing displacement |
| QA Guardian | Final 16-point delivery gate |
| Arc Replan | Residual arc after No-Go |

## Reasoning (Grok 4.6)

| Task | Reasoning |
|------|-----------|
| Scaffold only | medium–high |
| Score + gate decision | **high** |
| Critical veto vs average | **high** |

---

*NSFW Chain QA Protocol v3.8.6 — Grok 4.6 / v9-4p5 · fail closed on criticals · no extend on No-Go*
