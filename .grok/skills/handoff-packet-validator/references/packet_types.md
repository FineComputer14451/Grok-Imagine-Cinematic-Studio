# Handoff Packet Types — Field Cheat Sheet (v3.7.1 + Extend-Priority)

Source of implementation: `scripts/validate_handoff.py` + `tools/handoff_schema.py` (Imagine Agent Mode).  
**July 2026:** `imagine_agent_mode_handoff` now defaults to Extend-from-Frame priority for multi-clip work.

## identity_lock_handoff

| Rule | Fields |
|------|--------|
| required | `packet_type`, `character_name`, `slug`, `dna_profile`, `prompt_injection`, `key_consistency_anchors` |
| nonempty | `character_name`, `slug` |
| typed | `key_consistency_anchors` ≥ 1 item |

Producer: `dna handoff` / Character DNA Extractor.

## sequence_extend_handoff

| Rule | Fields |
|------|--------|
| required | `packet_type`, `source_clip_id`, `last_frame_recap`, `momentum_vector`, `audio_momentum_vector` |
| nonempty | `source_clip_id`, `last_frame_recap` |
| typed | `momentum_vector` object with nonempty `action`, `camera`, `emotion`; `audio_momentum_vector` object |

Producer: sequence extend / handoff CLI.

## asset_manifest_entry

| Rule | Fields |
|------|--------|
| required | `packet_type`, `asset_id`, `tier`, `image_model`, `video_model`, `status` |
| nonempty | `asset_id` |
| enums | `tier` ∈ hero\|standard\|draft · `status` ∈ draft\|approved\|locked |

Producer: Reference Asset Curator.

## intimacy_state_handoff

| Rule | Fields |
|------|--------|
| required | `packet_type`, `source_clip_id`, `intimacy_physics_state`, `post_scene_state`, `clothing_displacement_log`, `emotional_residue` |
| nonempty | `source_clip_id`, `emotional_residue` |
| typed | physics/post_scene = object; clothing log = list |

Producer: ErosForge / NSFW Sequence Extender. Opt-in only.

## imagine_agent_mode_handoff

Canonical schema: `tools/handoff_schema.py` → `imagine_agent_mode_packet_schema()`.  
**July 2026 Extend-Priority Default** (Team Leader): multi-clip work defaults to `generation_strategy: "extend_from_frame_chain"`.

**Always required (nonempty where noted):**  
`packet_type`, `protocol_version`, `studio_version`, `target_surface`, `execution_mode`, `subject_id`, `prompt`, `reference_hints` (list), `model_stack` (object with any of chat/build/imagine_image/imagine_video), `quota_note`, `return_path`, `handoff_steps` (≥1).

**New / strengthened fields (multi-clip / extend path):**
- `generation_strategy` (required for multi-clip) — default `"extend_from_frame_chain"`; allowed: `extend_from_frame_chain` | `independent_clip` | `hybrid`
- `extend_protocol` (required for video extend) — `"LAST_FRAME + MOTION_VECTOR"` or `"LAST_FRAME + MOTION_VECTOR + AUDIO_CUE"`
- `last_frame_recap`, `momentum_vector` (required on extend)
- `audio_momentum_vector` (required on 1.5 / native-audio chains)
- `quota_optimization` (strongly recommended)
- `chain_control` (recommended)

**Enums:**

| Field | Values |
|-------|--------|
| `target_surface` | `grok_build_tools`, `grok_agent_acp`, `grok_com_imagine`, `xai_api` |
| `execution_mode` | `image_prompt`, `image_edit`, `image_to_video`, `video_prompt`, `reference_to_video` |
| `generation_strategy` | `extend_from_frame_chain`, `independent_clip`, `hybrid` |

**When `execution_mode` is video** (`image_to_video` \| `video_prompt` \| `reference_to_video`):  
also require nonempty `video_pipeline_spec` and `sound_layer`.  
When `generation_strategy` is `extend_from_frame_chain`, also require `last_frame_recap` + `momentum_vector`.

**Canonical templates:**  
`studio-director/references/templates/imagine_agent_mode_handoff_extend_priority.json`  
`studio-director/references/templates/IMAGINE_AGENT_MODE_EXTEND_PRIORITY.md`

Doc: `references/agents/IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md`

## Surface bridge validation (Imagine Agent Mode)

For `packet_type: imagine_agent_mode_handoff`, the field `target_surface` is required and must be one of:

`grok_build_tools` | `grok_agent_acp` | `grok_com_imagine` | `xai_api`

| target_surface | Required skill / guidance | Bridge note |
|----------------|---------------------------|-------------|
| `grok_build_tools` | `grok-imagine-image-tools` | `GROK_IMAGINE_IMAGE_TOOLS_BRIDGE.md` |
| `grok_agent_acp` | Inherits A (or D) | See handoff protocol Surface B clarification |
| `grok_com_imagine` | Paste-friendly packet rules | `GROK_COM_IMAGINE_BRIDGE.md` |
| `xai_api` | `xai-grok-skill` | `XAI_API_SURFACE_BRIDGE.md` |

**Standalone checker:**

```bash
python .grok/skills/handoff-packet-validator/scripts/validate_surface.py path/to/packet.json
python .grok/skills/handoff-packet-validator/scripts/validate_surface.py path/to/packet.json --strict
```

Acknowledgement options (any one is enough for a soft pass):
- `bridge_ack: true` or `surface_validated: true` on the packet
- Mention of the required skill or bridge filename in `quota_note`, `notes`, `handoff_steps`, or `return_path`

Index: `grok-imagine-cinematic-studio/references/SURFACE_BRIDGES_INDEX.md`

## Exit codes

| Code | Meaning |
|------|--------|
| 0 | Valid |
| 1 | Validation / JSON errors |
| 2 | Usage / missing file |
