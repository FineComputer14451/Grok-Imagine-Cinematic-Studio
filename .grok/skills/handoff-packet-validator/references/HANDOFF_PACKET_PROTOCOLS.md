# Handoff Packet Protocols

**Version:** 3.8.6 / Wave A P1 (v3.8.7+) · Aligns with Imagine Agent Mode 3.7.1 / 4.5-extend-priority  
**Status:** Official  
**Owner:** Studio Director (routing) · Handoff Packet Validator (schema gate)  
**Studio:** Grok Imagine Cinematic Studio v3.8.6 / v4.5  
**Last updated:** August 2026  

**Engine:** `.grok/skills/handoff-packet-validator/scripts/validate_handoff.py`  
**Surface checker:** `.grok/skills/handoff-packet-validator/scripts/validate_surface.py`  
**Field cheat sheet:** `references/packet_types.md`  
**Imagine Agent Mode protocol:** `studio-director/references/agents/IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md`  
**Surface index:** `grok-imagine-cinematic-studio/references/SURFACE_BRIDGES_INDEX.md`

---

## 1. Purpose

Handoff packets are the **structured contract** between Cinematic Studio agents. They carry identity, continuity, asset tier, intimacy state, and Imagine execution intent so that:

1. Downstream agents never guess missing context.
2. QA and Continuity Guardian can score against declared state.
3. Quota spend is blocked when required fields or surface bridges are missing.
4. Extend-from-frame chains stay continuous across clips.

This document is the **official protocol** for every supported `packet_type`. Producers must emit valid packets; consumers must refuse incomplete ones.

---

## 2. Activation

```
VALIDATE HANDOFF
RUN HANDOFF VALIDATOR
CHECK HANDOFF PACKET
```

Run validation **before**:

- Loading external DNA into Identity Lock  
- Any extend / stitch / i2v spend  
- Imagine Agent Mode execution on any surface  
- Chain QA that depends on momentum / last-frame fields  

---

## 3. Supported Packet Types (core)

| `packet_type` | Producer → Consumer | Role |
|---------------|---------------------|------|
| `identity_lock_handoff` | Character DNA Extractor → Identity Lock | Character DNA + inject block |
| `sequence_extend_handoff` | Sequence Extender / Sequence Director → next clip / Chain QA | Last-frame + momentum for extend |
| `asset_manifest_entry` | Reference Asset Curator → i2v / batch / Prompt Master | Tier, models, lock status |
| `intimacy_state_handoff` | ErosForge / NSFW Sequence Extender → next intimate clip | Physics + post-scene state (opt-in) |
| `imagine_agent_mode_handoff` | Studio Director → Surfaces A/B/C/D | Full execution handoff |

Unknown `packet_type` → **hard fail**.

---

## 4. Core packet protocols

### 4.1 `identity_lock_handoff`

| Rule | Fields |
|------|--------|
| Required | `packet_type`, `character_name`, `slug`, `dna_profile`, `prompt_injection`, `key_consistency_anchors` |
| Nonempty | `character_name`, `slug` |
| Typed | `key_consistency_anchors` ≥ 1 item |

### 4.2 `sequence_extend_handoff`

| Rule | Fields |
|------|--------|
| Required | `packet_type`, `source_clip_id`, `last_frame_recap`, `momentum_vector`, `audio_momentum_vector` |
| Nonempty | `source_clip_id`, `last_frame_recap` |
| Typed | `momentum_vector` with nonempty `action`, `camera`, `emotion`; `audio_momentum_vector` object |

### 4.3 `asset_manifest_entry`

| Rule | Fields |
|------|--------|
| Required | `packet_type`, `asset_id`, `tier`, `image_model`, `video_model`, `status` |
| Nonempty | `asset_id` |
| Enums | `tier` ∈ hero\|standard\|draft · `status` ∈ draft\|approved\|locked |

### 4.4 `intimacy_state_handoff` (opt-in NSFW)

| Rule | Fields |
|------|--------|
| Required | `packet_type`, `source_clip_id`, `intimacy_physics_state`, `post_scene_state`, `clothing_displacement_log`, `emotional_residue` |
| Nonempty | `source_clip_id`, `emotional_residue` |

### 4.5 `imagine_agent_mode_handoff`

Full surface + extend protocol:  
→ `studio-director/references/agents/IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md`

**Surface bridges (mandatory before spend):**

| `target_surface` | Required skill | Bridge note |
|------------------|----------------|-------------|
| `grok_build_tools` | `grok-imagine-image-tools` | `GROK_IMAGINE_IMAGE_TOOLS_BRIDGE.md` |
| `grok_agent_acp` | Inherits A or D | Protocol §2.2 |
| `grok_com_imagine` | Paste-friendly rules | `GROK_COM_IMAGINE_BRIDGE.md` |
| `xai_api` | `xai-grok-skill` | `XAI_API_SURFACE_BRIDGE.md` |

Recommended: `bridge_ack: true`

---

## 5. Validation CLI

```bash
python .grok/skills/handoff-packet-validator/scripts/validate_handoff.py path/to/handoff.json
python .grok/skills/handoff-packet-validator/scripts/validate_handoff.py path/to/handoff.json --strict-handoff
python .grok/skills/handoff-packet-validator/scripts/validate_handoff.py path/to/handoff.json --strict-wave-a
python .grok/skills/handoff-packet-validator/scripts/validate_surface.py path/to/packet.json
python .grok/skills/handoff-packet-validator/scripts/validate_surface.py path/to/packet.json --strict
```

| Exit | Meaning |
|------|---------|
| 0 | Valid |
| 1 | Validation / JSON errors |
| 2 | Usage / missing file |

---

## 6. Governance

1. Unknown `packet_type` → fail.  
2. Surface D uses real xAI API via `xai-grok-skill` — never mock AI or invent another provider.  
3. Prefer `extend_from_frame_chain` for multi-clip unless user override or hard cut.  
4. Studio Director owns surface selection and bridge load before spend.

---

## 7. Related documents

| Document | Role |
|----------|------|
| `packet_types.md` | Compact field cheat sheet |
| `IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md` | Full Imagine Agent Mode protocol |
| `SURFACE_BRIDGES_INDEX.md` | Surface decision flowchart |
| `xai-grok-skill` / `grok-imagine-image-tools` | Surface D / A skills |

---

*Official Handoff Packet Protocols — Grok Imagine Cinematic Studio · August 2026*
