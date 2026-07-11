# Design: Generation Handoff Readiness (Semantic Packet Quality)

**Date:** 2026-07-11  
**Topic:** Semantic readiness checks for `imagine_agent_mode_handoff` packets before Imagine spend  
**Status:** Design approved — ready for implementation planning  
**Target version:** 3.8.x patch (tools + CLI + light agent notes)  
**Approach:** Pure readiness helper + validator warnings + opt-in `--strict-handoff` on `imagine agent-handoff`  
**Cluster:** Generation routing (deepen existing agents/tools — no new Role Cards)

## Summary of Decisions

| Decision | Choice |
|----------|--------|
| Cluster | **Generation routing** |
| Primary pain | **Incomplete / weak handoff packets** (semantic quality) |
| Deepening | **Semantic readiness checks** |
| Default | **Warn-only** (packets still emit; schema errors still hard-fail) |
| Hard mode | **Opt-in** `--strict-handoff` on `imagine agent-handoff` |
| Specialist-order automation | Out of scope (optional agent notes only) |
| Schema field expansion | Out of scope (no new required JSON keys in v1) |

## Problem

Imagine Agent Mode Handoff already requires structural fields (`prompt`, `return_path`, `model_stack`, video `video_pipeline_spec` / `sound_layer`, …). Production failures often come from **present-but-weak** packets:

- Video mode without real motion / I2V language  
- Empty or useless `reference_hints` on still→video  
- Placeholder `return_path` / `quota_note`  
- Stale `studio_version` relative to current studio  

Agents can claim “handoff ready” without a machine-readable quality score.

## Goals

1. Pure `evaluate_imagine_handoff_readiness(packet)` with `pass`, `warnings`, `blockers`, `fixes`.  
2. Validator prints readiness **warnings** (exit 0 if schema OK).  
3. `imagine agent-handoff --strict-handoff` exits 1 when readiness fails (evaluate before write).  
4. Light Role Card / skill notes: Studio Director, Prompt Master, I2V Specialist.  
5. No new required schema fields; no new agents.

## Non-goals

- Hard-default refusal on all agent-handoff writes  
- Auto-detect that DNA/Lock/Curator ran (specialist order epic)  
- Closed-loop job return automation  
- NSFW-only forks  
- Face vision scoring  

---

## Architecture

```text
imagine agent-handoff / validate_handoff
        │
        ├─ existing schema validation (hard issues)
        │
        └─ evaluate_imagine_handoff_readiness(packet)
                 │
                 ├─ blockers (strict fail) + warnings (soft)
                 │
                 └─ if --strict-handoff and not pass → exit 1 before write
                    else write/print + show ⚠️ warnings
```

### Helper contract

```python
def evaluate_imagine_handoff_readiness(
    packet: dict[str, Any],
    *,
    studio_version: str | None = None,  # default: read VERSION
) -> dict[str, Any]:
    """
    Returns:
      {
        "pass": bool,           # True if no blockers
        "strict": True,
        "warnings": list[str],
        "blockers": list[str],  # cause pass=False
        "fixes": list[str],
        "checks": list[dict],   # optional detail
      }
    """
```

**Suggested location:** `tools/handoff_readiness.py` (imports constants from `handoff_schema.py`) — keeps schema module focused.

### Readiness rules (v1)

Apply only when `packet_type == imagine_agent_mode_handoff` (or call sites pass agent-mode packets).

| ID | Severity | Rule |
|----|----------|------|
| **GHR-01** | blocker | Schema already failed → readiness not run / pass false with “fix schema first” |
| **GHR-02** | blocker (video modes) | `reference_hints` empty list for `image_to_video` or `reference_to_video` |
| **GHR-03** | blocker (video modes) | Prompt lacks motion/I2V cues (case-insensitive match any of: `motion`, `camera`, `dolly`, `pan`, `tilt`, `track`, `ken burns`, `first frame`, `i2v`, `extend`, `momentum`, `lip-sync`, `physics`) — OR optional field `i2v_motion_block` / `motion_vector` present and non-empty if we accept structured extras without requiring them |
| **GHR-04** | blocker | `return_path` missing re-entry cue (match any of: `qa`, `record`, `chain`, `artifact`, `sfw`, `sequence`, `handoff`, `validate`, `polish`) |
| **GHR-05** | warning | `quota_note` is placeholder (`todo`, `tbd`, `n/a`, `none`, empty after strip already schema) |
| **GHR-06** | warning | `studio_version` ≠ current studio VERSION (when both parseable) |
| **GHR-07** | warning | `protocol_version` not in `{3.7.1, 3.8.0, 3.8.1, current}` allowlist (warn only) |
| **GHR-08** | warning | `handoff_steps` length &lt; 2 |

**Severity policy:**  
- **blockers** → `pass=False` (strict exits 1)  
- **warnings** alone → `pass=True` with ⚠️ list  

Tune: image-only modes skip GHR-02/GHR-03.

### CLI

```bash
python tools/cinematic_studio_cli.py imagine agent-handoff ... --strict-handoff
```

- Default: build + write; print readiness warnings if any.  
- `--strict-handoff`: run readiness after successful schema build/validate; **do not write** on fail; print blockers + fixes; exit 1.

Optional later: `validate_handoff` always runs readiness for agent-mode packets (warn).

### Validator

After schema `issues` empty for `imagine_agent_mode_handoff`:

```
⚠️  handoff readiness: …
```

Exit 0 if only readiness warnings. Do **not** treat readiness blockers as schema errors unless `--strict` is added later to the validator CLI (optional; not required if agent-handoff has `--strict-handoff`).

**Minimal validator scope this epic:** always **warn** on readiness issues for agent-mode packets (including items that are blockers in strict mode). Strict hard-fail only on `imagine agent-handoff --strict-handoff`.

### Agent notes (light)

| Surface | Note |
|---------|------|
| Studio Director | Before generation spend, run readiness; use `--strict-handoff` in automation |
| Imagine Prompt Master | Ensure motion language for video modes; non-empty references for i2v |
| I2V Specialist | Own motion block content that satisfies GHR-03 |

Optional short protocol pointer in `IMAGINE_AGENT_MODE_HANDOFF` doc.

### Files

| Path | Action |
|------|--------|
| `tools/handoff_readiness.py` | **Create** helper + cue constants |
| `tests/test_handoff_readiness.py` | **Create** unit tests |
| `.grok/skills/handoff-packet-validator/scripts/validate_handoff.py` | Wire warn path |
| `tools/cli/imagine_commands.py` | `--strict-handoff` |
| `references/agents/IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md` | Readiness subsection |
| Role Cards / skills (Director, Prompt Master, I2V) | Short required notes |
| `CHANGELOG.md` | Unreleased |

---

## Testing

| Case | Expected |
|------|----------|
| Minimal valid image_prompt packet | pass=True, maybe version warn |
| i2v empty reference_hints | pass=False, GHR-02 |
| video prompt without motion cues | pass=False, GHR-03 |
| return_path “done” only | pass=False, GHR-04 |
| return_path “run chain QA then sfw record” | pass on GHR-04 |
| Schema-invalid packet | schema issues unchanged |
| CLI strict: fail before write | no output file |
| CLI soft: write + warnings | exit 0 |

---

## Acceptance criteria

- [ ] `evaluate_imagine_handoff_readiness` implemented + unit-tested  
- [ ] Validator warns on agent-mode readiness issues  
- [ ] `imagine agent-handoff --strict-handoff` hard-fails on blockers before write  
- [ ] Default path still emits packets when schema OK  
- [ ] Light agent/docs notes; CHANGELOG  
- [ ] No new agents; no new required schema fields  

---

## Approaches considered

| Approach | Outcome |
|----------|---------|
| **1. Readiness helper + warn + --strict-handoff** | **Selected** |
| 2. Protocol-only | Rejected for this epic’s semantic goal |
| 3. New required schema fields | Deferred |

---

## Relationship to prior work

- Complements identity continuity (extend path); this epic is **planner → generation spend**.  
- Reuses `handoff_schema` / validator patterns from Imagine Agent Mode Handoff v3.7.1.  
- Future: specialist-order gate; validator `--strict-handoff`; closed-loop return.

---

## Next step

User approves this design → write implementation plan (writing-plans) → implement.

---

*Grok Imagine Cinematic Studio — Generation Handoff Readiness design — 2026-07-11*
