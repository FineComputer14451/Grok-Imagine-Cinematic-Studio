# NSFW Chain QA Checklist v3.6.5

Score each check **1–10**. Weighted gate implemented in `tools/nsfw_sequence_extender.py`.

---

## Critical Checks (No-Go if < 7)

| Key | Weight | Inspect |
|-----|--------|---------|
| `hand_finger_integrity` | 1.4 | Finger count, pose, no merging |
| `explicit_area_artifact_risk` | 1.5 | No morphing, duplication, uncanny detail |
| `body_proportion_stability` | 1.3 | Limb/torso ratios at stitch boundary |
| `intimate_physics_fidelity` | 1.4 | Weight transfer, skin compression, momentum |

## Standard Checks

| Key | Weight | Inspect |
|-----|--------|---------|
| `skin_texture_consistency` | 1.3 | Pores, tone, marks match across stitch |
| `fabric_cloth_physics` | 1.2 | Drape, tension, pull direction |
| `erotic_tension_carryover` | 1.1 | Sensual curve — no mood drop at cut |
| `lighting_skin_modeling` | 1.0 | Rim/practical flatters skin at boundary |

---

## Pass Criteria

- Weighted score ≥ **7.0**
- All **critical** checks ≥ **7.0**
- ErosForge `intimacy_state_handoff` validated before extend

---

## Recovery Actions

| Failure | Fix |
|---------|-----|
| `hand_finger_integrity` | Hands out of frame or single-hand pose |
| `explicit_area_artifact_risk` | Pull back framing, one body focus |
| `skin_texture_consistency` | Tighten DNA inject, match color grade |
| `fabric_cloth_physics` | One fabric tension point in prompt |
| `intimate_physics_fidelity` | Shorten clip to 6–8s, one motion beat |

---

## CLI

```bash
python tools/cinematic_studio_cli.py nsfw extend qa "sequence-slug" --clip clip_002
python .grok/skills/nsfw-chain-qa-protocol/scripts/nsfw_chain_qa.py "sequence-slug" --clip clip_002 \
  --scores '{"hand_finger_integrity":8,...}'
```