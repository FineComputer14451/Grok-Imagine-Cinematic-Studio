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
- `quota_optimization` (strongly recommended) — prefer_extend_over_new_clip, estimated_savings_pct, max_new_independent_clips, buffer_remaining_pct
- `chain_control` (recommended) — source_clip_id, max_extensions, dependency_graph, require_chain_qa_before_extend, min_chain_qa_score

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

## Wave A specialist packets (P1 · v3.8.7+)

Source: `tools/wave_a_packets.py`. Builders live there; validator registers schemas automatically.

| packet_type | Required (summary) | Producer skill |
|-------------|-------------------|----------------|
| `plate_motion_readiness` | `subject_id`, `plate_status` (draft\|approved\|locked), `motion_vector` {action,camera,emotion}, `i2v_motion_block_ready` | `plate-motion-readiness-lead` |
| `contact_micro_physics_brief` | `subject_id`, `contact_brief`, `micro_physics_notes` (object) | `contact-micro-physics-specialist` |
| `hmu_lock_handoff` | `character_slug`, `active_look_id`, `hmu_lock` (object) | `hair-makeup-continuity` |
| `dialogue_adr_block` | `subject_id`, `dialogue_block` (object) | `dialogue-adr-director` |
| `score_temp_music_block` | `subject_id`, `music_cues` (list) | `score-temp-music-supervisor` |
| `title_mograph_brief` | `deliverable_id`, `title_cards` (≥1) | `title-motion-graphics-lead` |
| `distribution_crop_plan` | `subject_id`, `crop_plan` (≥1 rows) | `distribution-crop-strategist` |
| `parallel_brief_dispatch_log` | `session_id`, `briefs` (≥1 with `brief_id`) | `parallel-brief-dispatcher` |

**Optional fields on any packet** (shape-checked when present):  
`plate_status`, `motion_vector`, `hmu_lock`, `dialogue_block`, `music_cues`, `crop_plan`.

**CLI flags:**
- `--strict-handoff` — readiness blockers hard-fail (agent-mode)
- `--strict-wave-a` — still→video requires approved/locked plate + complete motion triple; incomplete Wave A fields hard-fail

**Attach helper:** `wave_a_packets.attach_wave_a_to_imagine(packet, plate_motion=…, …)` nests under `wave_a` and lifts plate/motion to top-level for readiness evaluators.

## Exit codes

| Code | Meaning |
|------|--------|
| 0 | Valid |
| 1 | Validation / JSON errors |
| 2 | Usage / missing file |
