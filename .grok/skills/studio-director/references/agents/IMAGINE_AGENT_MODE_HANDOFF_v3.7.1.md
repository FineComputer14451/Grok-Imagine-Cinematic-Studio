# Imagine Agent Mode Handoff Protocol v3.7.1 / Enhanced v4.5 + Extend-Priority Default

**Status:** Official (Studio Director owns routing)  
**Studio:** Grok Imagine Cinematic Studio **v3.8.6 / v4.5**  
**Model stack:** grok-4-auto · grok-v9-4p5-multi · grok-v9-4p5-chat-expert · Imagine Video 1.0 default / 1.5 Native  
**Canonical Model Layer:** `references/agents/MODEL_LAYER_v4.5.md` (v4.5.1)  
**Pairs with:** `imagine-execution-bridge`, `imagine-prompt-master`, `image-to-video-specialist`, `handoff-packet-validator`, `workflow-quota-optimizer`, `studio-director`, `cinematic-sequence-extender`, `sequence-director`

**July 2026 Update (Team Leader):**  
Default generation strategy for all multi-clip / long-form work is now **`extend_from_frame_chain`**.  
Canonical template: `references/templates/imagine_agent_mode_handoff_extend_priority.json`  
Policy doc: `references/templates/IMAGINE_AGENT_MODE_EXTEND_PRIORITY.md`  
Independent clips are allowed only with explicit user override or hard narrative cut.

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
| `protocol_version` | yes | `3.7.1` or `4.5-extend-priority` (preferred for multi-clip) |
| `studio_version` | yes | Current studio release (e.g. `3.8.6` / `4.5`) |
| `target_surface` | yes | `grok_build_tools` \| `grok_agent_acp` \| `grok_com_imagine` \| `xai_api` |
| `execution_mode` | yes | `image_prompt` \| `image_edit` \| `image_to_video` \| `video_prompt` \| `reference_to_video` |
| `subject_id` | yes | shot_id / clip_id / asset id |
| `generation_strategy` | yes (multi-clip) | **Default:** `extend_from_frame_chain`. Allowed: `extend_from_frame_chain` \| `independent_clip` \| `hybrid` |
| `extend_protocol` | yes (video extend) | Must be `LAST_FRAME + MOTION_VECTOR` or `LAST_FRAME + MOTION_VECTOR + AUDIO_CUE` |
| `video_pipeline_spec` | yes* | Full `VIDEO_PIPELINE_SPEC` string (*required for any video mode). Must include `stitch_priority=high` and matching extend_protocol |
| `prompt` | yes | Ultimate-template body from Imagine Prompt Master |
| `sound_layer` | yes* | Native audio Sound Layer (*required for video / i2v with audio, especially 1.5) |
| `reference_hints` | yes | List; for extend must contain the approved last_frame path |
| `model_stack` | yes | Object: chat, build, imagine_image, imagine_video (must declare 1.0 or 1.5) |
| `quota_note` | yes | One-line budget / Fast-mode note from Workflow Quota Optimizer |
| `return_path` | yes | How results re-enter studio (record command, QA, artifact path) |
| `handoff_steps` | yes | Ordered execution steps for the target surface |
| `last_frame_recap` | yes (extend) | Detailed visual + emotional state of the approved last frame |
| `momentum_vector` | yes (extend) | Object: action, camera, emotion, physics_notes |
| `audio_momentum_vector` | yes (1.5 / native audio) | Object: energy, tone, spatial, intensity |
| `quota_optimization` | recommended (strongly for multi-clip) | Object controlling prefer_extend, savings estimate, max new clips, buffer |
| `chain_control` | recommended (multi-clip) | source_clip_id, max_extensions, dependency_graph, require_chain_qa, min score |
| `dna_inject` | when cast | Identity Lock inject block or slug |
| `qa_gate` | recommended | Min score / chain-QA status before spend |
| `preferred_chat_model` | recommended | `grok-v9-4p5-multi` / `grok-v9-4p5-chat-expert` / `grok-4-auto` |

Validate:

```bash
python .grok/skills/handoff-packet-validator/scripts/validate_handoff.py handoff.json
python .grok/skills/handoff-packet-validator/scripts/validate_handoff.py handoff.json --strict-handoff
```

---

*Enhanced for Grok 4.5 / v9-4p5 + Extend-from-Frame Priority default — July 2026 · Team Leader / Studio Director*
