# Imagine Agent Mode Handoff Protocol v3.7.1 / Enhanced v4.5

**Status:** Official (Studio Director owns routing)  
**Studio:** Grok Imagine Cinematic Studio **v3.8.3 / v4.5**  
**Model stack:** grok-4-auto · grok-v9-4p5-multi · grok-v9-4p5-chat-expert · Imagine Video 1.0 default / 1.5 Native  
**Canonical Model Layer:** `references/agents/MODEL_LAYER_v4.5.md` (v4.5.1)  
**Pairs with:** `imagine-execution-bridge`, `imagine-prompt-master`, `image-to-video-specialist`, `handoff-packet-validator`, `workflow-quota-optimizer`, `studio-director`

---

## Purpose

Define a single, authoritative handoff from **Cinematic Studio planning** (Production Bible, DNA, shot lists, prompts, QA gates) into **Imagine execution surfaces** — so generation never loses pipeline context when leaving the multi-agent planning loop.

**Imagine Agent Mode** (studio definition) means any runtime where Grok is the agent and Imagine tools or the Imagine UI perform image/video generation:

| Surface | How generation runs | Studio posture |
|---------|---------------------|----------------|
| **A. Grok Build tools** | `image_gen` / `image_edit` / `image_to_video` / `reference_to_video` in TUI or agent session | Preferred when tools are available |
| **B. Grok agent mode (ACP)** | `grok agent stdio` / IDE ACP — same skills + shell + tools | Full studio skills load; use this packet for gen steps |
| **C. grok.com/imagine** | Manual paste in web UI | Use classic Execution Bridge packet (subset of this protocol) |
| **D. xAI Imagine API** | `imagine submit` / `sfw run` / `sequence run` with `XAI_API_KEY` | Prefer live jobs; packet still logs intent + QA |

This protocol does **not** install the studio into the web Imagine UI. It standardizes the **handoff contract** between planning agents and execution.

---

## Model Layer (Grok 4.5 / v9-4p5) — Enhanced

| Task type                                      | Preferred model               | Reasoning |
|------------------------------------------------|-------------------------------|-----------|
| Full Studio handoff orchestration / multi-agent synthesis | `grok-v9-4p5-multi`     | high      |
| Prompt / DNA / I2V packet assembly & surface decision | `grok-v9-4p5-chat-expert` | high   |
| Quick status / simple packet refresh             | `grok-4-auto`                 | medium    |

**Registry:** `tools/models.py` (schema 1.1+) · `references/agents/MODEL_LAYER_v4.5.md` (v4.5.1) · `models verify`

```yaml
model_compatibility:
  - grok-v9-4p5-chat-expert
  - grok-v9-4p5-multi
  - grok-4-auto
preferred_model: grok-v9-4p5-multi   # for Studio Director orchestration of handoffs
```

Prefer stable `prompt_cache_key` (project slug). Reasoning **high** for surface selection, incomplete-packet blocks, and multi-specialist synthesis.

---

## Imagine Video Protocol (1.0 / 1.5 Native)

- **Default:** Imagine Video **1.0** for cost and reliability.
- **Escalate to 1.5** when native synchronized audio, physics fidelity, micro-expression timing, or intimate authenticity is required.
- Every video-mode handoff **must** contain a complete `VIDEO_PIPELINE_SPEC`.
- On 1.5: also require `sound_layer` + prepare / carry `AUDIO_MOMENTUM_VECTOR` (AMV).
- Version consistency is mandatory — do not mix 1.0 and 1.5 inside one continuous chain without explicit Continuity Guardian + Studio Director approval.

**1.0 Spec example (default):**
```
[VIDEO_PIPELINE_SPEC: model="grok-imagine-video", version="1.0", resolution="720p", clip_length="8-12s preferred", native_audio=false, reference_image_fidelity=high, extend_protocol="LAST_FRAME + MOTION_VECTOR", stitch_priority=high, audio_momentum=false]
```

**1.5 Native Spec example:**
```
[VIDEO_PIPELINE_SPEC: model="grok-imagine-video-1.5", version="1.5", resolution="720p", clip_length="8-12s preferred", native_audio=true, reference_image_fidelity=high, extend_protocol="LAST_FRAME + MOTION_VECTOR + AUDIO_CUE", stitch_priority=high, audio_momentum=true]
```

---

## Activation (Studio Director)

```
ACTIVATE IMAGINE_AGENT_MODE_HANDOFF
HANDOFF TO IMAGINE AGENT MODE
ROUTE TO IMAGINE EXECUTION
```

Aliases (existing skills remain valid):

- `ACTIVATE IMAGINE_BRIDGE` — surface **C** only (copy-paste)
- `ACTIVATE IMAGINE_PROMPT_MASTER` — craft prompt body before handoff
- `ACTIVATE I2V_SPECIALIST` — required before video spend on locked plates

---

## Decision Matrix (Studio Director owns)

| Condition | Target surface | Action |
|-----------|----------------|--------|
| Session has Imagine tools (`image_gen`, `image_to_video`, …) | **A** | Emit agent-mode packet → execute tools in-session |
| Session is ACP / `grok agent` without UI slash commands | **B** | Same as A; load plugin skills; shell for CLI |
| No API key + user wants manual UI review | **C** | Emit bridge packet → paste grok.com/imagine |
| `XAI_API_KEY` set + batch/sequence job | **D** | `sfw run` / `sequence run` / `imagine submit`; log job id on packet |
| Hero plate not QA ≥7 | **Still only** | Block video; handoff `mode=image_prompt` or i2i refine |
| Explicit/NSFW | **A/B/D + ErosForge** | Route ErosForge first; never silent NSFW handoff |
| Native audio / physics / intimacy required | Prefer 1.5 + surface A/B/D | Enforce VIDEO_PIPELINE_SPEC version="1.5" |

**Rule:** Never send locked plates to video without I2V Specialist motion block when surface supports i2v.

---

## Mandatory Packet Fields

`packet_type`: **`imagine_agent_mode_handoff`**

| Field | Required | Description |
|-------|----------|-------------|
| `packet_type` | yes | Always `imagine_agent_mode_handoff` |
| `protocol_version` | yes | `3.7.1` (or `4.5` after full migration) |
| `studio_version` | yes | Current studio release (e.g. `3.8.3` / `4.5`) |
| `target_surface` | yes | `grok_build_tools` \| `grok_agent_acp` \| `grok_com_imagine` \| `xai_api` |
| `execution_mode` | yes | `image_prompt` \| `image_edit` \| `image_to_video` \| `video_prompt` \| `reference_to_video` |
| `subject_id` | yes | shot_id / clip_id / asset id |
| `video_pipeline_spec` | yes* | Full `VIDEO_PIPELINE_SPEC` string (*required for any video mode) |
| `prompt` | yes | Ultimate-template body from Imagine Prompt Master |
| `sound_layer` | yes* | Native audio Sound Layer (*required for video / i2v with audio, especially 1.5) |
| `reference_hints` | yes | List; may be empty for pure t2i |
| `model_stack` | yes | Object: chat, build, imagine_image, imagine_video (must declare 1.0 or 1.5) |
| `quota_note` | yes | One-line budget / Fast-mode note from Workflow Quota Optimizer |
| `return_path` | yes | How results re-enter studio (record command, QA, artifact path) |
| `handoff_steps` | yes | Ordered execution steps for the target surface |
| `last_frame_recap` | clip only | Required when extending / stitching |
| `momentum_vector` | clip only | Camera/action/emotion carry |
| `audio_momentum_vector` | clip only when audio / 1.5 | AMV for chain QA |
| `dna_inject` | when cast | Identity Lock inject block or slug |
| `qa_gate` | recommended | Min score / chain-QA status before spend |
| `preferred_chat_model` | recommended | `grok-v9-4p5-multi` / `grok-v9-4p5-chat-expert` / `grok-4-auto` |

Validate:

```bash
python .grok/skills/handoff-packet-validator/scripts/validate_handoff.py handoff.json
python .grok/skills/handoff-packet-validator/scripts/validate_handoff.py handoff.json --strict-handoff
```

---

## Standard Markdown Handoff (agent-readable)

```markdown
## Handoff: Imagine Agent Mode v3.7.1 / Enhanced v4.5

**From:** Studio Director (+ Imagine Prompt Master / I2V Specialist as needed)
**To:** Imagine execution surface: <target_surface>
**Subject:** <subject_id> · **Mode:** <execution_mode>
**Preferred Chat Model:** <grok-v9-4p5-multi | grok-v9-4p5-chat-expert | grok-4-auto>

### Context Summary
- Project: <title>
- Beat / shot intent: <one sentence>
- Tier: hero | standard | draft
- Video version: 1.0 | 1.5

### Key Decisions / State
- VIDEO_PIPELINE_SPEC locked: <yes / version>
- DNA / Identity Lock: <locked | pending | n/a>
- Plate lock: <locked | draft | none>
- i2i routing note: <agent + reason if applicable>
- Quota: <remaining / estimated spend>
- Preferred model for this handoff: <model>

### Artifacts
- Prompt body (Ultimate Template)
- Reference plate id / path / URL
- DNA inject block (if any)
- Sequence handoff fields (if clip)
- AUDIO_MOMENTUM_VECTOR (if 1.5)

### Execution Request
1. Target surface steps (see handoff_steps)
2. Duration / aspect / native_audio
3. On success → return_path

### Quality / Continuity Notes
- QA gate before next clip / promote
- LAST_FRAME_RECAP + MOMENTUM_VECTOR if extend
- Version consistency check (1.0 / 1.5)
```

---

## Surface-Specific Steps

### A — Grok Build tools (`target_surface: grok_build_tools`)

1. Load / confirm studio skills for this turn (Prompt Master, DNA if cast).
2. **Stills:** `image_gen` or `image_edit` with `prompt` + references; aspect from packet.
3. **Video:** Prefer still → `image_to_video` (or `reference_to_video` only when multi-ref required). Respect declared 1.0 or 1.5.
4. Save outputs under `artifacts/`; never claim success without tool result.
5. Return via `return_path` (e.g. `sfw record`, sequence QA, Director's Notes).

### B — Grok agent mode ACP (`target_surface: grok_agent_acp`)

1. Ensure plugin enabled (`grok-imagine-cinematic-studio`) or `--plugin-dir` for process.
2. Same tool path as A; use shell for `cinematic_studio_cli.py` when batching.
3. Slash commands may be unavailable — use activation phrases + CLI, not TUI-only modals.
4. Permission mode: prefer explicit approve for video spend.

### C — grok.com/imagine (`target_surface: grok_com_imagine`)

1. Emit classic bridge block (`imagine bridge` / `bridge_to_clipboard`).
2. User pastes VIDEO_PIPELINE_SPEC + prompt + Sound Layer + references.
3. User downloads result → `return_path` (record QA + path).

### D — xAI API (`target_surface: xai_api`)

1. `imagine verify` preflight.
2. `sfw run` / `sequence run` / `imagine submit` with packet prompt + models (honor 1.0 vs 1.5).
3. Attach `job_id` to packet log; reconcile quota.

---

## Studio Director Obligations

1. **Own the surface decision** — pick A/B/C/D with one-line reason in Director's Notes.
2. **Block incomplete packets** — no video handoff without pipeline spec + sound layer (when audio) + plate policy.
3. **Activate specialists before handoff** — DNA → Identity Lock → Reference Curator → Prompt Master → I2V → then Imagine Agent Mode Handoff.
4. **Close the loop** — after generation, require QA Guardian (and Chain QA for extend) before next handoff.
5. **Log** `imagine_agent_mode_handoff` in Project Bible / directors_notes_log with subject_id + surface + model + outcome.
6. **Enforce model layer** — record preferred chat model and video version on every handoff.

---

## Handoff readiness (semantic quality)

Structural validation is not enough. Run semantic readiness before spend:

```bash
python .grok/skills/handoff-packet-validator/scripts/validate_handoff.py packet.json
python .grok/skills/handoff-packet-validator/scripts/validate_handoff.py packet.json --strict-handoff
python tools/cinematic_studio_cli.py imagine agent-handoff ... --strict-handoff
```

**Blockers (strict):** empty `reference_hints` on i2v/ref-to-video; video without motion/I2V cues; weak `return_path` (must mention qa/record/chain/artifact/sfw/sequence/…); incomplete `specialist_checklist` when present (GHR-10); missing or mismatched VIDEO_PIPELINE_SPEC version.  
**Warnings:** placeholder `quota_note`; `studio_version` mismatch; short `handoff_steps`; missing `specialist_checklist` (GHR-09); preferred_chat_model not declared.

### Specialist order checklist

Optional additive field `specialist_checklist` confirms Studio Director order before spend:

DNA Extractor → Identity Lock → Reference Curator → Prompt Master → I2V (video modes)

```bash
python tools/cinematic_studio_cli.py imagine agent-handoff \
  --batch … --shot … \
  --checklist dna,lock,curator,prompt,i2v \
  --strict-handoff
```

Helper: `evaluate_specialist_order` in `tools/specialist_order.py` (folded into `evaluate_imagine_handoff_readiness`).

## CLI

```bash
# Classic web bridge (surface C)
python tools/cinematic_studio_cli.py imagine bridge --batch <slug> --shot <id>
python tools/cinematic_studio_cli.py imagine bridge --sequence "Act 1" --clip clip_001 --format clipboard

# Official agent-mode handoff packet (surfaces A–D)
python tools/cinematic_studio_cli.py imagine agent-handoff \
  --batch <slug> --shot <id> \
  --surface grok_build_tools \
  --format json

python tools/cinematic_studio_cli.py imagine agent-handoff \
  --sequence "Act 1" --clip clip_001 \
  --surface grok_agent_acp \
  --format markdown -o artifacts/handoff_clip_001.md
```

---

## Relationship to Other Handoffs

| Packet | Role |
|--------|------|
| `identity_lock_handoff` | Cast consistency **before** Imagine Agent Mode |
| `asset_manifest_entry` | Plate tier / lock for still→video |
| `sequence_extend_handoff` | Clip-to-clip extend; embed fields into this packet when target is video extend |
| `imagine_agent_mode_handoff` | **This protocol** — planning → Imagine execution surface |
| Classic Execution Bridge | Markdown/clipboard subset for surface **C** only |

---

## Integration Checklist (Enhanced v4.5)

- [ ] Studio Director selected `target_surface` and preferred chat model
- [ ] Imagine Prompt Master (or I2V Specialist) approved `prompt`
- [ ] `VIDEO_PIPELINE_SPEC` matches Project Bible and declares 1.0 or 1.5
- [ ] References / DNA inject attached when required
- [ ] Quota note present; video not over budget; 1.5 cost delta acknowledged if used
- [ ] Packet validated (`handoff-packet-validator`)
- [ ] `return_path` named before spend
- [ ] Director's Notes record handoff + model + video version + outcome
- [ ] Specialist order checklist completed when using `--strict-handoff`

---

*Enhanced 2026-07-21 for grok-4-auto · grok-v9-4p5-multi · grok-v9-4p5-chat-expert + Imagine Video 1.0 / 1.5 Native*  
*Canonical protocol for Grok Imagine Cinematic Studio — Studio Director owns this handoff.*
