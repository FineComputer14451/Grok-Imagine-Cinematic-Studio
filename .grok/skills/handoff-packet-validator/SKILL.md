---
name: handoff-packet-validator
description: Validates JSON handoff packets between Cinematic Studio agents including identity lock sequence extend asset manifest intimacy state and Imagine Agent Mode Handoff. Run before activating downstream agents or extend generation. Use when validating handoff.json packets or debugging chain QA failures. Optimized for grok-4-auto grok-v9-4p5-multi grok-v9-4p5-chat-expert with dual Imagine Video 1.0 and 1.5 Native.
---

# Handoff Packet Validator v3.8.6 (Grok 4.5 / v9-4p5 · Schema Gate)

**Tool skill** — data-driven schema checks for agent handoff JSON. Blocks broken packets before Identity Lock, extend/stitch, i2v, or Imagine spend.

**Engine:** `.grok/skills/handoff-packet-validator/scripts/validate_handoff.py`  
**Canonical Imagine Agent Mode schema:** `tools/handoff_schema.py`  
**Field cheat sheet:** `references/packet_types.md`

## Model Layer (Grok 4.5 / v9-4p5)

| Task type | Preferred model | Reasoning |
|-----------|-----------------|-----------|
| Multi-agent orchestration / handoff synthesis | `grok-v9-4p5-multi` | high |
| Specialist deep craft / QA / identity-critical | `grok-v9-4p5-chat-expert` | high |
| Routine status / draft passes | `grok-4-auto` | medium |

**Stack default:** cinematic+Build API/chat **`grok-4.5`** (CLI ≥ 0.2.93 · fork `grok-build`). Opt-in 1M: `grok-4.3`.  
**Registry:** `tools/models.py` · `references/agents/MODEL_LAYER_v4.5.md` · `models verify`

```yaml
model_compatibility:
  - grok-v9-4p5-chat-expert
  - grok-v9-4p5-multi
  - grok-4-auto
preferred_model: grok-v9-4p5-chat-expert
```

### Imagine Video dual-path (when this skill touches video)
- **1.5 Native** — preferred for hero / final motion with audio when budget allows
- **1.0** — cost default / draft / pre-viz; label outputs so downstream agents do not assume 1.5 capabilities

## When to Activate

- After `dna handoff` / DNA Extractor packets  
- After `sequence handoff` or Sequence Extender packets  
- Before `ACTIVATE IDENTITY_LOCK` load of external JSON  
- Before `ACTIVATE I2V_SPECIALIST` or extend/stitch generation  
- Before Imagine Agent Mode Handoff execution (any surface)  
- When chain QA fails on continuity / momentum fields that should have been in the packet  
- User says: `VALIDATE HANDOFF`, `RUN HANDOFF VALIDATOR`, `CHECK HANDOFF PACKET`

## When NOT Required

| Situation | Note |
|-----------|------|
| Pure in-session chat with no JSON packet | No file to validate |
| Already-locked DNA in project state without file export | Optional — re-validate if regenerating `handoff.json` |
| Editing prompts only | Use Imagine Prompt Master |

## Supported Packet Types

| `packet_type` | Producer → Consumer |
|---------------|---------------------|
| `identity_lock_handoff` | Character DNA Extractor → Identity Lock |
| `sequence_extend_handoff` | Sequence Extender / Sequence Director → next clip / Chain QA |
| `asset_manifest_entry` | Reference Asset Curator → i2v / batch / Prompt Master |
| `intimacy_state_handoff` | ErosForge / NSFW Sequence Extender → next intimate clip |
| `imagine_agent_mode_handoff` | Studio Director → Build tools / ACP / grok.com / xAI API |

Unknown `packet_type` → **fail**. See `references/packet_types.md` for required fields.

## CLI

```bash
# From repo root
python .grok/skills/handoff-packet-validator/scripts/validate_handoff.py path/to/handoff.json
python .grok/skills/handoff-packet-validator/scripts/validate_handoff.py characters/hero-slug/handoff.json
python .grok/skills/handoff-packet-validator/scripts/validate_handoff.py artifacts/handoffs/clip_001_extend.json
# Agent-mode readiness blockers as hard failures:
python .grok/skills/handoff-packet-validator/scripts/validate_handoff.py packet.json --strict-handoff
python .grok/skills/handoff-packet-validator/scripts/validate_handoff.py packet.json --strict-wave-a
```

| Exit | Meaning |
|------|---------|
| `0` | Valid (may include ⚠️ warnings) |
| `1` | Schema / JSON structure errors, or readiness blockers with `--strict-handoff` |
| `2` | Usage or file not found |

## Identity Continuity (`drift_evidence`)

For `sequence_extend_handoff` and `identity_lock_handoff`, missing or incomplete
`drift_evidence` produces **warnings** (exit 0). Invalid `status` enums are **errors**.
Protocol: `references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md`  
CLI: `sequence drift-score`

## Generation handoff readiness (`imagine_agent_mode_handoff`)

After schema OK, semantic readiness runs as **warnings** (exit 0): empty i2v
references, video without motion cues, weak `return_path`, placeholder quota,
missing/incomplete `specialist_checklist` (GHR-09/10), etc.

Hard-fail (exit 1 on readiness blockers):

```bash
python .grok/skills/handoff-packet-validator/scripts/validate_handoff.py packet.json \
  --strict-handoff
# or emit with hard gate:
python tools/cinematic_studio_cli.py imagine agent-handoff ... --strict-handoff
```

Helper: `tools/handoff_readiness.py` · Protocol: `IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md`

### Generate packets then validate

```bash
# Identity
python tools/cinematic_studio_cli.py dna handoff "Character Name" \
  --output characters/{slug}/handoff.json
python .grok/skills/handoff-packet-validator/scripts/validate_handoff.py \
  characters/{slug}/handoff.json

# Sequence extend
python tools/cinematic_studio_cli.py sequence handoff "Sequence Name" --clip clip_001
# validate the written path reported by CLI

# Imagine Agent Mode Handoff
python tools/cinematic_studio_cli.py imagine agent-handoff \
  --batch hero-session --shot shot_hero_001 \
  --surface grok_build_tools --format json \
  -o artifacts/handoffs/agent_mode.json
python .grok/skills/handoff-packet-validator/scripts/validate_handoff.py \
  artifacts/handoffs/agent_mode.json
```

## Validation Engine (data-driven)

`validate_packet()` loads schema from `PACKET_TYPES` and applies:

| Rule | Behavior |
|------|----------|
| `required` | Field must be present |
| `nonempty` | Non-empty string after strip |
| `enums` | Value ∈ allowed set |
| `typed` | list / dict / list_min / object_keys / object_any_of |
| `when` | Conditional (e.g. video modes need `video_pipeline_spec` + `sound_layer`) |

Imagine Agent Mode field lists live in **`tools/handoff_schema.py`** (single source of truth) so validator and bridge cannot drift.

## Gate Policy (Studio Director)

| Result | Action |
|--------|--------|
| Valid | Proceed to downstream agent |
| Invalid identity packet | Fix DNA / re-run `dna handoff` — do not lock |
| Invalid extend packet | Fix LAST_FRAME_RECAP / momentum — do not extend |
| Invalid asset entry | Curator re-tier — do not spend hero i2v |
| Invalid intimacy state | ErosForge re-state — do not NSFW-extend |
| Invalid agent-mode | Fix surface/mode/spec — **block Imagine spend** |
| Video mode missing sound layer | Fail — force Sound Layer block |

**Never** silent-pass NSFW or video handoffs with incomplete packets.

## Failure Playbook

1. Read printed `•` issues top to bottom  
2. Fix producer (DNA / sequence / curator / Studio Director) — do not hand-edit casually unless user owns the packet  
3. Re-run generator CLI if available  
4. Validate again until exit 0  
5. Only then activate consumer agent  

## Output Format

```text
HANDOFF VALIDATION · v3.7.1
File: <path>
packet_type: <type|unknown>
Result: PASS | FAIL
Issues:
  - <…>
Next: <activate consumer | fix producer | block spend>
```

## Integration

| Partner | Relationship |
|---------|----------------|
| Character DNA Extractor | Emits `identity_lock_handoff` |
| Identity Lock Specialist | Consumes only after PASS |
| Sequence Director / Extender | Emit/consume `sequence_extend_handoff` |
| Chain QA Protocol | Continuity fields should match packet |
| Reference Asset Curator | `asset_manifest_entry` |
| Image-to-Video Specialist | Prefer locked approved assets |
| ErosForge / NSFW Sequence Extender | `intimacy_state_handoff` |
| Studio Director | Owns `imagine_agent_mode_handoff` gates |
| Imagine Execution Bridge | Classic grok.com packets (related) |
| Quality Assurance Guardian | Invalid handoff = stop before client |

## Protocol Doc

Imagine Agent Mode (surfaces, modes, required fields):  
`references/agents/IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md`

## Reasoning (Grok 4.5)

| Task | Reasoning |
|------|-----------|
| Routine re-check | medium |
| Spend/identity-gating failure | **high** |

---

*Handoff Packet Validator v3.8.6 — Grok 4.5 / v9-4p5 schema gate · data-driven PACKET_TYPES · block broken handoffs before spend*
