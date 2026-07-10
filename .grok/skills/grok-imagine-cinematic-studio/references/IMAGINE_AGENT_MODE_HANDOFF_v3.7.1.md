# Imagine Agent Mode Handoff Protocol v3.7.1

**Status:** Official (Studio Director owns routing)  
**Studio:** Grok Imagine Cinematic Studio **v3.7.1**  
**Pairs with:** `imagine-execution-bridge`, `imagine-prompt-master`, `image-to-video-specialist`, `handoff-packet-validator`, `workflow-quota-optimizer`

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

**Rule:** Never send locked plates to video without I2V Specialist motion block when surface supports i2v.

---

## Mandatory Packet Fields

`packet_type`: **`imagine_agent_mode_handoff`**

| Field | Required | Description |
|-------|----------|-------------|
| `packet_type` | yes | Always `imagine_agent_mode_handoff` |
| `protocol_version` | yes | `3.7.1` |
| `studio_version` | yes | Current studio release (e.g. `3.7.1`) |
| `target_surface` | yes | `grok_build_tools` \| `grok_agent_acp` \| `grok_com_imagine` \| `xai_api` |
| `execution_mode` | yes | `image_prompt` \| `image_edit` \| `image_to_video` \| `video_prompt` \| `reference_to_video` |
| `subject_id` | yes | shot_id / clip_id / asset id |
| `video_pipeline_spec` | yes* | Full `VIDEO_PIPELINE_SPEC` string (*required for any video mode) |
| `prompt` | yes | Ultimate-template body from Imagine Prompt Master |
| `sound_layer` | yes* | Native audio Sound Layer (*required for video / i2v with audio) |
| `reference_hints` | yes | List; may be empty for pure t2i |
| `model_stack` | yes | Object: chat, build, imagine_image, imagine_video |
| `quota_note` | yes | One-line budget / Fast-mode note from Workflow Quota Optimizer |
| `return_path` | yes | How results re-enter studio (record command, QA, artifact path) |
| `handoff_steps` | yes | Ordered execution steps for the target surface |
| `last_frame_recap` | clip only | Required when extending / stitching |
| `momentum_vector` | clip only | Camera/action/emotion carry |
| `audio_momentum_vector` | clip only when audio | AMV for chain QA |
| `dna_inject` | when cast | Identity Lock inject block or slug |
| `qa_gate` | recommended | Min score / chain-QA status before spend |

Validate:

```bash
python .grok/skills/handoff-packet-validator/scripts/validate_handoff.py handoff.json
```

---

## Standard Markdown Handoff (agent-readable)

```markdown
## Handoff: Imagine Agent Mode v3.7.1

**From:** Studio Director (+ Imagine Prompt Master / I2V Specialist as needed)
**To:** Imagine execution surface: <target_surface>
**Subject:** <subject_id> · **Mode:** <execution_mode>

### Context Summary
- Project: <title>
- Beat / shot intent: <one sentence>
- Tier: hero | standard | draft

### Key Decisions / State
- VIDEO_PIPELINE_SPEC locked: <yes>
- DNA / Identity Lock: <locked | pending | n/a>
- Plate lock: <locked | draft | none>
- i2i routing note: <agent + reason if applicable>
- Quota: <remaining / estimated spend>

### Artifacts
- Prompt body (Ultimate Template)
- Reference plate id / path / URL
- DNA inject block (if any)
- Sequence handoff fields (if clip)

### Execution Request
1. Target surface steps (see handoff_steps)
2. Duration / aspect / native_audio
3. On success → return_path

### Quality / Continuity Notes
- QA gate before next clip / promote
- LAST_FRAME_RECAP + MOMENTUM_VECTOR if extend
```

---

## Surface-Specific Steps

### A — Grok Build tools (`target_surface: grok_build_tools`)

1. Load / confirm studio skills for this turn (Prompt Master, DNA if cast).
2. **Stills:** `image_gen` or `image_edit` with `prompt` + references; aspect from packet.
3. **Video:** Prefer still → `image_to_video` (or `reference_to_video` only when multi-ref required).
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
2. `sfw run` / `sequence run` / `imagine submit` with packet prompt + models.
3. Attach `job_id` to packet log; reconcile quota.

---

## Studio Director Obligations

1. **Own the surface decision** — pick A/B/C/D with one-line reason in Director's Notes.
2. **Block incomplete packets** — no video handoff without pipeline spec + sound layer (when audio) + plate policy.
3. **Activate specialists before handoff** — DNA → Identity Lock → Reference Curator → Prompt Master → I2V → then Imagine Agent Mode Handoff.
4. **Close the loop** — after generation, require QA Guardian (and Chain QA for extend) before next handoff.
5. **Log** `imagine_agent_mode_handoff` in Project Bible / directors_notes_log with subject_id + surface + outcome.

---

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

## Integration Checklist (v3.7.1)

- [ ] Studio Director selected `target_surface`
- [ ] Imagine Prompt Master (or I2V Specialist) approved `prompt`
- [ ] `VIDEO_PIPELINE_SPEC` matches Project Bible
- [ ] References / DNA inject attached when required
- [ ] Quota note present; video not over budget
- [ ] Packet validated (`handoff-packet-validator`)
- [ ] `return_path` named before spend
- [ ] Director's Notes record handoff + outcome

---

*Canonical protocol for Grok Imagine Cinematic Studio v3.7.1 — Studio Director + main studio skill.*
