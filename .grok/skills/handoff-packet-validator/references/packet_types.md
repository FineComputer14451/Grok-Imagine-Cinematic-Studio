# Handoff Packet Types — Field Cheat Sheet (v3.7.1)

Source of implementation: `scripts/validate_handoff.py` + `tools/handoff_schema.py` (Imagine Agent Mode).

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

**Always required (nonempty where noted):**  
`packet_type`, `protocol_version`, `studio_version`, `target_surface`, `execution_mode`, `subject_id`, `prompt`, `reference_hints` (list), `model_stack` (object with any of chat/build/imagine_image/imagine_video), `quota_note`, `return_path`, `handoff_steps` (≥1).

**Enums:**

| Field | Values |
|-------|--------|
| `target_surface` | `grok_build_tools`, `grok_agent_acp`, `grok_com_imagine`, `xai_api` |
| `execution_mode` | `image_prompt`, `image_edit`, `image_to_video`, `video_prompt`, `reference_to_video` |

**When `execution_mode` is video** (`image_to_video` \| `video_prompt` \| `reference_to_video`):  
also require nonempty `video_pipeline_spec` and `sound_layer`.

Doc: `references/agents/IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md`

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Valid |
| 1 | Validation / JSON errors |
| 2 | Usage / missing file |
