# Imagine Agent Mode Handoff Protocol

**Version:** 3.7.1 / Enhanced 4.5 (Extend-Priority Default)  
**Status:** Official  
**Owner:** Studio Director (routing authority)  
**Studio:** Grok Imagine Cinematic Studio v3.8.6 / v4.5  
**Last updated:** August 2026  

**Model stack:** `grok-4-auto` · `grok-v9-4p5-multi` · `grok-v9-4p5-chat-expert` · Imagine Video 1.0 (default) / 1.5 Native  

**Canonical Model Layer:** `references/agents/MODEL_LAYER_v4.5.md`  
**Surface index:** `grok-imagine-cinematic-studio/references/SURFACE_BRIDGES_INDEX.md`  

**Pairs with:** `imagine-execution-bridge` · `imagine-prompt-master` · `image-to-video-specialist` · `handoff-packet-validator` · `workflow-quota-optimizer` · `studio-director` · `cinematic-sequence-extender` · `sequence-director` · `grok-imagine-image-tools` · `xai-grok-skill`

---

## 1. Purpose

This protocol defines the **single authoritative handoff** from Cinematic Studio planning (Production Bible, Character DNA, shot lists, prompts, QA gates) into **Imagine execution surfaces**.

Its goals are:

1. Preserve pipeline context when generation leaves the multi-agent planning loop.
2. Force the correct skill / bridge for every execution surface before any quota spend.
3. Prefer **extend-from-frame** chains for multi-clip work (continuity + cost).
4. Give every agent the same packet contract so Identity Lock, Continuity Guardian, and QA can track results.

**Imagine Agent Mode** (studio definition) means any runtime where Grok is the agent and Imagine tools or the Imagine UI perform image or video generation.

This protocol does **not** install the studio into the web Imagine UI. It standardizes the **handoff contract** between planning agents and execution.

---

## 2. Execution Surfaces

| Code | `target_surface` value | How generation runs | Studio posture |
|------|------------------------|---------------------|----------------|
| **A** | `grok_build_tools` | `image_gen` / `image_edit` / `image_to_video` / `reference_to_video` in TUI or agent session | **Preferred** when tools are available |
| **B** | `grok_agent_acp` | `grok agent stdio` / IDE ACP — same skills + shell + tools | Full studio skills; use this packet for gen steps |
| **C** | `grok_com_imagine` | Manual paste in grok.com/imagine web UI | Classic Execution Bridge packet (subset of this protocol) |
| **D** | `xai_api` | Live jobs via injected `XAI_API_KEY` | Prefer for batch / remote; packet still logs intent + QA |

### 2.1 Required skills and bridges by surface

Full index and visual decision flowchart:

→ `grok-imagine-cinematic-studio/references/SURFACE_BRIDGES_INDEX.md`

| Surface | Required skill / guidance | Bridge note |
|---------|---------------------------|-------------|
| **A** `grok_build_tools` | `grok-imagine-image-tools` | `GROK_IMAGINE_IMAGE_TOOLS_BRIDGE.md` |
| **B** `grok_agent_acp` | Inherits A (or D) | See §2.2 |
| **C** `grok_com_imagine` | Paste-friendly packet rules (still respect prompt craft) | `GROK_COM_IMAGINE_BRIDGE.md` |
| **D** `xai_api` | `xai-grok-skill` | `XAI_API_SURFACE_BRIDGE.md` |

Studio Director **must** ensure the matching skill and bridge are loaded and followed before any generation spend on that surface.

### 2.2 Surface B (`grok_agent_acp`) clarification

ACP / IDE agent sessions do **not** have a separate bridge file.

- When local Imagine tools (`image_gen`, `image_edit`, `image_to_video`, etc.) are available inside the ACP session → treat as **Surface A**: load `grok-imagine-image-tools` + `GROK_IMAGINE_IMAGE_TOOLS_BRIDGE.md`.
- When the session routes work to the live API → treat as **Surface D**: load `xai-grok-skill` + `XAI_API_SURFACE_BRIDGE.md`.

Never treat ACP as a free-form generation path that bypasses prompt craft, reference-first, or consistency requirements.

### 2.3 Surface decision rules (short form)

1. Local Imagine tools available in session → prefer **A**
2. ACP / IDE agent session → **B** (still obey A or D rules)
3. `XAI_API_KEY` present + batch / remote job → **D**
4. No key + user wants web UI review → **C**

---

## 3. Model Layer (Grok 4.6 / v9-4p5)

| Task type | Preferred model | Reasoning |
|-----------|-----------------|-----------|
| Full Studio handoff orchestration / multi-agent synthesis | `grok-v9-4p5-multi` | high |
| Prompt / DNA / I2V packet assembly & surface decision | `grok-v9-4p5-chat-expert` | high |
| Quick status / simple packet refresh | `grok-4-auto` | medium |

```yaml
model_compatibility:
  - grok-v9-4p5-chat-expert
  - grok-v9-4p5-multi
  - grok-4-auto
preferred_model: grok-v9-4p5-multi   # Studio Director orchestration of handoffs
```

Prefer a stable `prompt_cache_key` (project slug). Use **high** reasoning for surface selection, incomplete-packet blocks, and multi-specialist synthesis.

---

## 4. Imagine Video Protocol (1.0 / 1.5 Native)

| Policy | Rule |
|--------|------|
| Default | Imagine Video **1.0** for cost and reliability |
| Escalate to 1.5 | When native synchronized audio, physics fidelity, micro-expression timing, or intimate authenticity is required |
| Required on every video handoff | Complete `VIDEO_PIPELINE_SPEC` |
| Required on 1.5 | `sound_layer` + prepare / carry `AUDIO_MOMENTUM_VECTOR` (AMV) |
| Version consistency | Do **not** mix 1.0 and 1.5 inside one continuous chain without Continuity Guardian + Studio Director approval |

**1.0 example:**

```
[VIDEO_PIPELINE_SPEC: model="grok-imagine-video", version="1.0", resolution="720p", clip_length="8-12s preferred", native_audio=false, reference_image_fidelity=high, extend_protocol="LAST_FRAME + MOTION_VECTOR", stitch_priority=high, audio_momentum=false]
```

**1.5 Native example:**

```
[VIDEO_PIPELINE_SPEC: model="grok-imagine-video-1.5", version="1.5", resolution="720p", clip_length="8-12s preferred", native_audio=true, reference_image_fidelity=high, extend_protocol="LAST_FRAME + MOTION_VECTOR + AUDIO_CUE", stitch_priority=high, audio_momentum=true]
```

---

## 5. Activation

Studio Director activation phrases:

```
ACTIVATE IMAGINE_AGENT_MODE_HANDOFF
HANDOFF TO IMAGINE AGENT MODE
ROUTE TO IMAGINE EXECUTION
```

Related aliases (existing skills remain valid):

| Phrase | Effect |
|--------|--------|
| `ACTIVATE IMAGINE_BRIDGE` | Surface **C** only (copy-paste path) |
| `ACTIVATE IMAGINE_PROMPT_MASTER` | Craft prompt body before handoff |
| `ACTIVATE I2V_SPECIALIST` | Required before video spend on locked plates |

---

## 6. Decision Matrix (Studio Director owns)

| Condition | Target surface | Action |
|-----------|----------------|--------|
| Session has Imagine tools (`image_gen`, `image_to_video`, …) | **A** | Emit agent-mode packet → execute tools in-session |
| Session is ACP / `grok agent` without UI slash commands | **B** | Same as A; load plugin skills; shell for CLI |
| No API key + user wants manual UI review | **C** | Emit bridge packet → paste into grok.com/imagine |
| `XAI_API_KEY` set + batch / sequence job | **D** | Live API job; log job id on packet |
| Hero plate not QA ≥ 7 | Still only | Block video; handoff `mode=image_prompt` or i2i refine |
| Explicit / NSFW | A/B/D + ErosForge | Route ErosForge first; never silent NSFW handoff |
| Native audio / physics / intimacy required | Prefer 1.5 + A/B/D | Enforce `VIDEO_PIPELINE_SPEC` version `"1.5"` |

**Hard rule:** Never send locked plates to video without an I2V Specialist motion block when the surface supports i2v.

---

## 7. Extend-from-Frame Priority (Default for multi-clip)

**July / August 2026 Team Leader policy:**

Default generation strategy for all multi-clip / long-form work is **`extend_from_frame_chain`**.

| Resource | Path |
|----------|------|
| Canonical JSON template | `studio-director/references/templates/imagine_agent_mode_handoff_extend_priority.json` |
| Policy doc | `studio-director/references/templates/IMAGINE_AGENT_MODE_EXTEND_PRIORITY.md` |

Independent clips are allowed **only** with explicit user override or a hard narrative cut.

When `generation_strategy` is `extend_from_frame_chain`:

- `last_frame_recap` — required
- `momentum_vector` — required
- `audio_momentum_vector` — required for 1.5 / native-audio chains
- `extend_protocol` — must be `LAST_FRAME + MOTION_VECTOR` or `LAST_FRAME + MOTION_VECTOR + AUDIO_CUE`
- `reference_hints` must include the approved last-frame path

---

## 8. Mandatory Packet Fields

`packet_type` must be **`imagine_agent_mode_handoff`**.

| Field | Required | Description |
|-------|----------|-------------|
| `packet_type` | yes | Always `imagine_agent_mode_handoff` |
| `protocol_version` | yes | `3.7.1` or `4.5-extend-priority` (preferred for multi-clip) |
| `studio_version` | yes | Current studio release (e.g. `3.8.6` / `4.5`) |
| `target_surface` | yes | `grok_build_tools` \| `grok_agent_acp` \| `grok_com_imagine` \| `xai_api` |
| `execution_mode` | yes | `image_prompt` \| `image_edit` \| `image_to_video` \| `video_prompt` \| `reference_to_video` |
| `subject_id` | yes | shot_id / clip_id / asset id |
| `generation_strategy` | yes (multi-clip) | **Default:** `extend_from_frame_chain`. Allowed: `extend_from_frame_chain` \| `independent_clip` \| `hybrid` |
| `extend_protocol` | yes (video extend) | `LAST_FRAME + MOTION_VECTOR` or `LAST_FRAME + MOTION_VECTOR + AUDIO_CUE` |
| `video_pipeline_spec` | yes* | Full `VIDEO_PIPELINE_SPEC` string (*required for any video mode) |
| `prompt` | yes | Ultimate-template body from Imagine Prompt Master |
| `sound_layer` | yes* | Native audio Sound Layer (*required for video / i2v with audio, especially 1.5) |
| `reference_hints` | yes | List; for extend must contain the approved last_frame path |
| `model_stack` | yes | Object: chat, build, imagine_image, imagine_video (must declare 1.0 or 1.5) |
| `quota_note` | yes | One-line budget / Fast-mode note from Workflow Quota Optimizer |
| `return_path` | yes | How results re-enter the studio (record command, QA, artifact path) |
| `handoff_steps` | yes | Ordered execution steps for the target surface |
| `last_frame_recap` | yes (extend) | Detailed visual + emotional state of the approved last frame |
| `momentum_vector` | yes (extend) | Object: `action`, `camera`, `emotion`, `physics_notes` |
| `audio_momentum_vector` | yes (1.5 / native audio) | Object: `energy`, `tone`, `spatial`, `intensity` |
| `quota_optimization` | recommended (multi-clip) | prefer_extend, savings estimate, max new clips, buffer |
| `chain_control` | recommended (multi-clip) | source_clip_id, max_extensions, dependency_graph, require_chain_qa, min score |
| `dna_inject` | when cast | Identity Lock inject block or slug |
| `qa_gate` | recommended | Min score / chain-QA status before spend |
| `preferred_chat_model` | recommended | `grok-v9-4p5-multi` / `grok-v9-4p5-chat-expert` / `grok-4-auto` |
| `bridge_ack` | recommended | `true` when the required surface skill/bridge has been acknowledged |

---

## 9. Validation

### 9.1 Schema + readiness

```bash
python .grok/skills/handoff-packet-validator/scripts/validate_handoff.py path/to/handoff.json
python .grok/skills/handoff-packet-validator/scripts/validate_handoff.py path/to/handoff.json --strict-handoff
python .grok/skills/handoff-packet-validator/scripts/validate_handoff.py path/to/handoff.json --strict-wave-a
```

### 9.2 Surface bridge validation

```bash
python .grok/skills/handoff-packet-validator/scripts/validate_surface.py path/to/handoff.json
python .grok/skills/handoff-packet-validator/scripts/validate_surface.py path/to/handoff.json --strict
```

Surface validation checks:

1. `target_surface` is one of the four known values.
2. The packet acknowledges the required supporting skill / bridge for that surface.

Acknowledgement options (any one is enough for a soft pass):

- `bridge_ack: true` or `surface_validated: true` on the packet
- Mention of the required skill or bridge filename in `quota_note`, `notes`, `handoff_steps`, or `return_path`

Field cheat sheet: `handoff-packet-validator/references/packet_types.md`  
Official packet protocols: `handoff-packet-validator/references/HANDOFF_PACKET_PROTOCOLS.md`

---

## 10. Minimal example packet (extend priority)

```json
{
  "packet_type": "imagine_agent_mode_handoff",
  "protocol_version": "4.5-extend-priority",
  "studio_version": "3.8.6 / 4.5",
  "target_surface": "grok_build_tools",
  "execution_mode": "image_to_video",
  "subject_id": "clip_003",
  "generation_strategy": "extend_from_frame_chain",
  "extend_protocol": "LAST_FRAME + MOTION_VECTOR + AUDIO_CUE",
  "bridge_ack": true,
  "prompt": "[Ultimate Template body — must reference last-frame visual/emotional state]",
  "reference_hints": [
    "artifacts/approved/clip_002_last_frame.png"
  ],
  "last_frame_recap": "Wide two-shot, soft key from left, subject looking toward frame right, rain continuing on glass.",
  "momentum_vector": {
    "action": "subject continues slow walk toward camera",
    "camera": "slow push-in, same 35mm feel",
    "emotion": "tension rising, restrained",
    "physics_notes": "rain streaks continuity on glass"
  },
  "audio_momentum_vector": {
    "energy": "low building",
    "tone": "tense ambient",
    "spatial": "rain L/R, dialogue center",
    "intensity": 0.55
  },
  "video_pipeline_spec": "[VIDEO_PIPELINE_SPEC: model=\\"grok-imagine-video-1.5\\", version=\\"1.5\\", resolution=\\"720p\\", clip_length=\\"8-12s\\", native_audio=true, reference_image_fidelity=high, extend_protocol=\\"LAST_FRAME + MOTION_VECTOR + AUDIO_CUE\\", stitch_priority=high, audio_momentum=true]",
  "sound_layer": "native rain bed + sparse score swell",
  "model_stack": {
    "chat": "grok-v9-4p5-multi",
    "imagine_video": "1.5"
  },
  "quota_note": "prefer extend; ~40% savings vs new independent clip; loaded grok-imagine-image-tools",
  "return_path": "artifacts/rendered/clip_003.mp4 → Chain QA → Continuity Guardian",
  "handoff_steps": [
    "Load grok-imagine-image-tools + GROK_IMAGINE_IMAGE_TOOLS_BRIDGE",
    "Confirm last_frame path exists",
    "Execute image_to_video with extend momentum",
    "Record job/result path into return_path"
  ]
}
```

---

## 11. Ownership and governance

| Responsibility | Owner |
|----------------|-------|
| Surface selection | Studio Director |
| Loading required skill / bridge | Studio Director (before spend) |
| Packet schema validity | Handoff Packet Validator |
| Surface bridge acknowledgement | Handoff Packet Validator (`validate_surface.py`) |
| Extend-priority default | Team Leader policy (this protocol) |
| Identity / continuity continuity | Identity Lock + Continuity Guardian |
| Final Go / No-Go on spend | Quality Assurance Guardian |

---

## 12. Related documents

| Document | Role |
|----------|------|
| `SURFACE_BRIDGES_INDEX.md` | Surface decision flowchart + bridge table |
| `GROK_IMAGINE_IMAGE_TOOLS_BRIDGE.md` | Surface A bridge |
| `GROK_COM_IMAGINE_BRIDGE.md` | Surface C bridge |
| `XAI_API_SURFACE_BRIDGE.md` | Surface D bridge |
| `IMAGINE_AGENT_MODE_EXTEND_PRIORITY.md` | Extend-priority policy |
| `imagine_agent_mode_handoff_extend_priority.json` | Canonical multi-clip template |
| `HANDOFF_PACKET_PROTOCOLS.md` | Full packet-type protocols |
| `packet_types.md` | Field cheat sheet + surface validation rules |
| `xai-grok-skill` | Real xAI API usage (Surface D) |
| `grok-imagine-image-tools` | Prompt craft + tool choice (Surface A / B) |

---

*Official Imagine Agent Mode Handoff Protocol — Grok Imagine Cinematic Studio · Grok 4.6 / v9-4p5 · Extend-from-Frame Priority default · August 2026*
