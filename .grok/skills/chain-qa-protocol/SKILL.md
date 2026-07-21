---
name: chain-qa-protocol
description: Extend and stitch chain QA protocol for Grok Imagine Video 1.5 sequences. Runs the weighted 10-point gate before approving clips for extension or final stitch. Activate with RUN CHAIN QA REVIEW alongside Sequence Director and Cinematic Sequence Extender. Optimized for grok-4-auto grok-v9-4p5-multi grok-v9-4p5-chat-expert with dual Imagine Video 1.0 and 1.5 Native.
---

# Chain QA Protocol v3.8.6 (Grok 4.5 / v9-4p5 · Extend/Stitch Gate)

**Pipeline skill** — boundary continuity gate for multi-clip sequences. Complements QA Guardian’s **per-clip 16-point** review; does **not** replace it.

**Checklist:** `.grok/skills/cinematic-sequence-extender/references/chain_qa_checklist.md`  
**Implementation:** `tools/sequence_chain.py` (`CHAIN_QA_CHECKS`, `run_chain_qa`)  
**Assist:** `tools/chain_qa_assist.py` · CLI `sequence qa` / `sequence qa-assist`  
**NSFW variant:** `nsfw-chain-qa-protocol` (8-point artifact-aware)

## Model Layer (Grok 4.5 / v9-4p5)

| Task type | Preferred model | Reasoning |
|-----------|-----------------|-----------|
| Multi-agent orchestration / handoff synthesis | `grok-v9-4p5-multi` | high |
| Specialist deep craft / QA / identity-critical | `grok-v9-4p5-chat-expert` | high |
| Routine status / draft passes | `grok-4-auto` | medium |

**Stack default:** cinematic+Build API/chat **`grok-4.5`** (CLI ≥ 0.2.93 · fork `grok-build`). Opt-in 1M: `grok-4.3`.  
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

- Before **every** extend-from-last-frame generation  
- Before **final stitch** of a multi-clip sequence  
- After Continuity Guardian flags boundary risk  
- After I2V / sequence run when clip is a chain link  
- User says: `RUN CHAIN QA REVIEW`, `CHAIN QA`, `SCORE STITCH BOUNDARY`

```
ACTIVATE ONLY Sequence Director, Cinematic Sequence Extender, Continuity Guardian, Quality Assurance Guardian
RUN CHAIN QA REVIEW
```

Begin: **"Initiating Chain QA Protocol v3.8.6 (Grok 4.5 / v9-4p5)…"**

## When NOT Alone

| Need | Also activate |
|------|----------------|
| Per-clip artistic/tech quality | Quality Assurance Guardian (16-point) |
| Intimate / explicit chains | `nsfw-chain-qa-protocol` |
| Identity mid-shot drift only | Identity Lock + drift-score |

## 10-Point Checks (score 1–10 each)

Weights from `CHAIN_QA_CHECKS` in `tools/sequence_chain.py`:

| Key | Focus | Weight |
|-----|-------|--------|
| `last_frame_continuity` | N+1 starts from N end state | 1.5 **critical** |
| `momentum_carryover` | Action, camera, emotion | 1.2 |
| `audio_momentum_sync` | Dialogue, SFX, music | 1.3 **critical** |
| `physics_realism` | Stitch boundary physics | 1.2 |
| `reference_propagation` | reference_image_id fidelity | 1.0 |
| `character_drift_boundary` | Identity at stitch | 1.3 **critical** |
| `lighting_color_match` | Light/color at boundary | 1.0 |
| `prop_environment_state` | Props, wardrobe, set | 1.0 |
| `transition_readiness` | Clean ending for extend | 1.2 **critical** |
| `stitch_artifact_risk` | Flicker, morph, halo | 1.3 |

### Pass rules

| Result | Criteria |
|--------|----------|
| **Go** | Weighted score **≥ 7.0** and **no critical** check **&lt; 7.0** |
| **Conditional Go** | Weighted **5.5–6.9** (or fixable non-critical gaps) — fix handoff before final stitch |
| **No-Go** | Weighted **&lt; 5.5** **or** any **critical** check **&lt; 7.0** — regenerate; **do not extend** |

Critical set: `last_frame_continuity`, `audio_momentum_sync`, `character_drift_boundary`, `transition_readiness`.

## Identity Continuity (ICP-06)

When scoring `character_drift_boundary` / identity criteria, require handoff `drift_evidence` (or clip `identity_drift`).  
If missing → finding: run ICP-02/03 (`sequence drift-score`).  
Protocol: `references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md` · `[IDENTITY_CONTINUITY_PROTOCOL: v1.0]`

## Prerequisites (handoff)

Clip / packet should include:

- `last_frame_recap`  
- `momentum_vector` (action, camera, emotion)  
- `audio_momentum_vector`  
- `reference_image_id` (when used)  
- `continuity_state`  

```bash
python .grok/skills/handoff-packet-validator/scripts/validate_handoff.py handoff.json
```

## CLI

### Scaffold (awaiting scores)

```bash
python tools/cinematic_studio_cli.py sequence qa "Neon Alley Chase" --clip clip_002
```

### Score and gate

```bash
python tools/cinematic_studio_cli.py sequence qa "Neon Alley Chase" --clip clip_002 \
  --scores '{"last_frame_continuity":8,"momentum_carryover":7,"audio_momentum_sync":9,"physics_realism":8,"reference_propagation":8,"character_drift_boundary":8,"lighting_color_match":7,"prop_environment_state":8,"transition_readiness":9,"stitch_artifact_risk":7}'
```

### QA Assist (heuristic pre-fill → optional apply)

```bash
python tools/cinematic_studio_cli.py sequence qa-assist "Neon Alley Chase" --clip clip_002
python tools/cinematic_studio_cli.py sequence qa-assist "Neon Alley Chase" --clip clip_002 --apply
python tools/cinematic_studio_cli.py sequence qa-assist "Intimate" --clip clip_002 --nsfw --apply
```

### Evidence (Assist v2 / regen inputs)

```bash
python tools/cinematic_studio_cli.py sequence drift-score --dna dna.json --images clip_001.png clip_002.png
python tools/cinematic_studio_cli.py sequence seam-report --prev last.png --next first.png
python tools/cinematic_studio_cli.py sequence amv-check --prev prev_amv.json --next next_amv.json
python tools/cinematic_studio_cli.py sequence health "Neon Alley Chase"
```

### After No-Go

```bash
python tools/cinematic_studio_cli.py sequence regen plan "Neon Alley Chase" --clip clip_002
python tools/cinematic_studio_cli.py sequence regen apply "Neon Alley Chase" --clip clip_002
# run spends attempt via sequence runner when ready
```

Optional: `sequence replan` (Arc Replan Co-pilot) if mid-sequence arc breaks.

## Decision Matrix

| Result | Next step |
|--------|-----------|
| **Go** | Approve extend / stitch; update sequence `chain_qa_status` |
| **Conditional Go** | Fix LAST_FRAME_RECAP / momentum / audio fields; re-score before final stitch |
| **No-Go** | Regenerate clip N; block extend; regen plan from chain QA + drift/seam/memory |

## Output Format

```text
CHAIN QA · v3.7.1
Sequence: <name> | Clip: <id>
Weighted: X.X / threshold 7.0
Critical failures: <none|keys>
Decision: go | conditional_go | no_go
Checks:
  last_frame_continuity: …
  …
Evidence: drift=… seam=… amv=…
Next: extend | fix handoff | regen plan | Assembly Editor (if final Go)
```

## Integration

| Partner | Role |
|---------|------|
| Sequence Director / Extender | When to gate; consume decision |
| Continuity Guardian | Boundary risk flags |
| Quality Assurance Guardian | Full 16-point per clip |
| Identity Lock | Character drift boundary |
| I2V Specialist | Motion/audio seeds under review |
| Handoff Packet Validator | Packet completeness |
| Arc Replan Co-pilot | Mid-sequence replan after No-Go |
| NSFW Chain QA | Intimate sequences only |

## Reasoning (Grok 4.5)

| Task | Reasoning |
|------|-----------|
| Scaffold / assist pre-fill review | medium–high |
| Final go/no-go on hero chain | **high** |
| Regen strategy after No-Go | **high** |

---

*Chain QA Protocol v3.8.6 — Grok 4.5 / v9-4p5 · weighted 10-point stitch gate · critical floor 7.0*
