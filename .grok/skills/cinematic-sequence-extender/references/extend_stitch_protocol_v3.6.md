# Extend & Stitch Protocol v3.7.1 — Grok Imagine Video 1.0/1.5

Authoritative protocol for low-degradation long-form chaining (60–180s+).  
Orchestration: **Grok 4.5**. Skill: `cinematic-sequence-extender`.

**Video default:** `grok-imagine-video` (1.0 cost). Use **1.5** when native audio / rich AMV is required.

---

## Locked Variables

**Cost default (1.0):**

```
[VIDEO_PIPELINE_SPEC: model="grok-imagine-video", resolution="720p", clip_length="8-12s preferred", native_audio=false, reference_image_fidelity=high, extend_protocol="LAST_FRAME + MOTION_VECTOR + AUDIO_CUE", stitch_priority=high]
```

**Native audio (1.5):**

```
[VIDEO_PIPELINE_SPEC: model="grok-imagine-video-1.5", resolution="720p", clip_length="8-12s preferred", native_audio=true, reference_image_fidelity=high, extend_protocol="LAST_FRAME + MOTION_VECTOR + AUDIO_CUE", stitch_priority=high]
```

## Handoff Packet (Required Between Clips)

Every approved clip must output:

| Field | Purpose |
|-------|---------|
| `LAST_FRAME_RECAP` | Exact ending visual state (pose, props, lighting, camera) |
| `MOMENTUM_VECTOR` | Action, emotion, camera energy, physics, visual motifs |
| `AUDIO_MOMENTUM_VECTOR` | Dialogue state, lip-sync, SFX timing, music cues |
| `reference_image_id` | Propagated unless deliberate scene change |
| `continuity_state` | Props, wardrobe, environment, timeline position |

## Clip Length Rules (1.5)

| Beat type | Duration |
|-----------|----------|
| Default | 8–12s |
| High action / emotion | 6–8s |
| Sensual / atmospheric | 10–15s |
| Dialogue-heavy | 8–10s (lip-sync fidelity) |

## Extend Prompt Structure

```
[VIDEO_PIPELINE_SPEC: ...]
LAST_FRAME_RECAP: ...
MOMENTUM_VECTOR: ...
AUDIO_MOMENTUM_VECTOR: ...
Next beat: ...
Transition: invisible_edit | match_cut | dissolve
reference_image_id=...
Sound Layer: ...
Physics: weighty momentum, no morphing at stitch boundary
```

## Generation Order

1. Sequence Director plans blueprint + dependency graph
2. Generate clip 1 → run chain QA → capture LAST_FRAME_RECAP
3. Continuity Guardian validates state memory
4. Build extend prompt from handoff → generate clip 2
5. Repeat; never extend from unapproved or QA-failed clip

## Transition Types

- **invisible_edit** — default; audience should not feel the cut
- **match_cut** — shape/color/motion match across boundary
- **dissolve** — time passage or emotional shift
- **whip_pan** — kinetic energy carry (action only)
- **hard_cut** — deliberate scene change only

## CLI Workflow

```bash
python tools/cinematic_studio_cli.py sequence init "Neon Alley Chase" --duration 90
python tools/cinematic_studio_cli.py sequence add-clip "Neon Alley Chase" --prompt "..." --recap "..."
python tools/cinematic_studio_cli.py sequence handoff "Neon Alley Chase" --clip clip_001
python tools/cinematic_studio_cli.py sequence extend-prompt "Neon Alley Chase" --clip clip_001 --beat "She turns into the alley"
python tools/cinematic_studio_cli.py sequence qa "Neon Alley Chase" --clip clip_002 --scores '{"last_frame_continuity":8,...}'
python tools/cinematic_studio_cli.py sequence health "Neon Alley Chase"
```

## Failure Recovery

| Symptom | Fix |
|---------|-----|
| Morphing at stitch | Regenerate ending 2s of previous clip; tighten physics descriptors |
| Audio desync | Re-specify lip_sync_state in AUDIO_MOMENTUM_VECTOR |
| Character drift | Re-inject CHARACTER_DNA; increase primary_ref_weight |
| Lighting jump | Add lighting_state to both LAST_FRAME_RECAP and next prompt |
| Prop teleport | Update continuity_state; Continuity Guardian memory bank |