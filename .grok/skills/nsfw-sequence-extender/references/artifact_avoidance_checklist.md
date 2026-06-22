# Artifact Avoidance Checklist — NSFW Chain QA

Score each 1–10. **No-Go if critical check <7.**

---

## Critical Checks (No-Go)

| Key | What to Inspect |
|-----|-----------------|
| `hand_finger_integrity` | Correct finger count, natural pose, no merging |
| `explicit_area_artifact_risk` | No morphing, duplication, uncanny detail in explicit zones |
| `body_proportion_stability` | Limbs, torso ratios stable at stitch boundary |
| `intimate_physics_fidelity` | Weight transfer, skin compression, momentum realistic |

## Standard Checks

| Key | What to Inspect |
|-----|-----------------|
| `skin_texture_consistency` | Pores, tone, marks match across stitch |
| `fabric_cloth_physics` | Drape, tension, pull direction realistic |
| `erotic_tension_carryover` | Sensual curve maintained — no mood drop at cut |
| `lighting_skin_modeling` | Rim/practical flatters skin at boundary |

---

## Prompt Guard (Include Every Clip)

```
Artifact Guard:
- Hands: single natural pose, anatomically correct fingers
- Skin: consistent pore texture, no plastic sheen
- Fabric: one primary tension point per clip
- Bodies: stable proportions, no limb morphing
- Physics: weighty momentum, no stitch boundary morphing
```

---

## Recovery Actions

| Failure | Fix |
|---------|-----|
| Hand artifacts | Hands out of frame OR single-hand pose |
| Skin morphing | Tighten DNA inject, match color grade |
| Fabric glitch | One tension point in prompt, simplify motion |
| Explicit uncanny | Pull back framing, suggestive not graphic |
| Physics break | Shorten clip to 6–8s, one motion beat |

---

## CLI

```bash
python tools/cinematic_studio_cli.py nsfw extend qa "sequence-slug" --clip clip_002
python tools/cinematic_studio_cli.py nsfw extend qa "sequence-slug" --clip clip_002 \
  --scores '{"hand_finger_integrity":8,"skin_texture_consistency":7,...}'
```