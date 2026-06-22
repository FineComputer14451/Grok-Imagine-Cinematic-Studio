# NSFW Extend Protocol — ErosForge + 1.5 Native

Extends `extend_stitch_protocol_v3.6.md` for sensual long-form sequences.

---

## Locked Variables

```
[VIDEO_PIPELINE_SPEC: model="grok-imagine-video-1.5", resolution="720p", native_audio=true,
 extend_protocol="LAST_FRAME + MOTION_VECTOR + AUDIO_CUE + EROSFORGE_STATE", stitch_priority=high]
```

## Handoff Packet (NSFW Extension)

Standard handoff fields **plus**:

| Field | Purpose |
|-------|---------|
| `intimacy_physics_state` | Weight transfer, skin compression, cloth tension |
| `post_scene_state` | Body position, emotional residue after beat |
| `clothing_displacement_log` | Fabric state — what moved, what remains |
| `erotic_tension_level` | 0.0–1.0 for pacing curve continuity |
| `color_grade` | Locked LUT mood across all clips |
| `atmosphere` | Practical light, haze, room tone |

## Source Types

| Type | Clip 001 Mode | Requirements |
|------|---------------|--------------|
| `reference_frame` | image_to_video | High-quality still, DNA locked, QA ≥8 |
| `short_clip` | extend_from_last_frame | Approved clip, LAST_FRAME_RECAP captured |

## Generation Order

1. `ACTIVATE EROSFORGE` + Identity Lock DNA inject
2. `nsfw extend plan` — beat sheet + prompt chain
3. Generate clip_001 → **NSFW chain QA** (8 checks) → Go
4. Capture LAST_FRAME_RECAP + EROSFORGE_STATE
5. `nsfw extend prompt` for clip_002 → extend → repeat
6. Never extend from `no_go` clip
7. Stitch → optional AI Polish Director for delivery

## Extend Prompt Layers

1. VIDEO_PIPELINE_SPEC
2. LAST_FRAME_RECAP + MOMENTUM_VECTOR + AUDIO_MOMENTUM_VECTOR
3. EROSFORGE_STATE block
4. Camera + timing beats
5. Artifact Guard block
6. Color grade + atmosphere continuity