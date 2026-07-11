# Chain QA Checklist v3.7.1 — Extend/Stitch Gate (Grok 4.5)

Run **before** approving any clip for extension or final stitch. Complements the standard 16-point QA.

Skill: `chain-qa-protocol` · Code: `tools/sequence_chain.py` · Assist: `sequence qa-assist`

**Pass threshold:** weighted score ≥ 7.0  
**Critical checks** (any below 7.0 = automatic No-Go): `last_frame_continuity`, `audio_momentum_sync`, `character_drift_boundary`, `transition_readiness`

---

## 10-Point Chain QA (score each 1–10)

| # | Key | Check |
|---|-----|-------|
| 1 | `last_frame_continuity` | Clip N+1 starts from exact end state of clip N |
| 2 | `momentum_carryover` | Action, camera, emotion carry forward naturally |
| 3 | `audio_momentum_sync` | Dialogue, SFX, music cues continuous across boundary |
| 4 | `physics_realism` | Weight, momentum, cloth/hair physics believable at stitch |
| 5 | `reference_propagation` | reference_image_id fidelity maintained |
| 6 | `character_drift_boundary` | Face/body/clothing consistent at stitch point |
| 7 | `lighting_color_match` | Lighting direction & color temp match at boundary |
| 8 | `prop_environment_state` | Props, wardrobe, set dressing unchanged unless story-driven |
| 9 | `transition_readiness` | Previous clip ending is clean for extension |
| 10 | `stitch_artifact_risk` | No flicker, morphing, halos, or temporal instability |

## Decisions

| Weighted Score | Decision |
|----------------|----------|
| ≥ 7.0 + no critical failures | **Go** — safe to extend |
| 5.5–6.9 | **Conditional Go** — fix before final stitch |
| < 5.5 or critical failure | **No-Go** — regenerate |

## CLI

```bash
# Scaffold (awaiting scores)
python tools/cinematic_studio_cli.py sequence qa "Sequence Name" --clip clip_002

# Score and gate
python tools/cinematic_studio_cli.py sequence qa "Sequence Name" --clip clip_002 \
  --scores '{"last_frame_continuity":8,"momentum_carryover":7,"audio_momentum_sync":9,"physics_realism":8,"reference_propagation":8,"character_drift_boundary":8,"lighting_color_match":7,"prop_environment_state":8,"transition_readiness":9,"stitch_artifact_risk":7}'
```

## Agent Activation

```
ACTIVATE ONLY Sequence Director, Cinematic Sequence Extender, Continuity Guardian, Quality Assurance Guardian
RUN CHAIN QA REVIEW
```