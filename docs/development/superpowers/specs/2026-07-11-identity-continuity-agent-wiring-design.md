# Design: Identity Continuity Agent Wiring (Deepen Existing Agents)

**Date:** 2026-07-11  
**Topic:** Expand agent effectiveness for long-form identity drift via protocol wiring (not new crew)  
**Status:** Design approved — ready for implementation planning  
**Target version:** 3.8.x patch (docs/skills/schema; no new agents)  
**Approach:** Protocol hub + Role Card/skill patches + additive `drift_evidence` packet schema (warn-only validation)

## Summary of Decisions

| Decision | Choice |
|----------|--------|
| Expansion mode | **Deepen existing agents** (no new Role Cards / headcount) |
| First cluster | **Long-form continuity loop** |
| Primary pain | **Identity drift** across extend/stitch |
| Deepening type | **Agent wiring** — must call drift tools + handoffs every extend |
| Enforcement | **Protocol only** — no CLI hard-block / refuse on missing evidence |
| Finish line | Role Cards + skills + **canonical protocol** + **packet schema** |
| Implementation approach | **Protocol hub + coordinated agent patches + additive schema** |

## Problem

Long-form identity tooling already shipped on `main` (roadmap #1–#12), including:

- `tools/identity_drift.py` + `sequence drift-score` (stores report on clip as `identity_drift`)
- DNA handoffs, Identity Lock, Sequence Extender, Continuity Guardian, Chain QA
- Multi-character arbiter, memory bank, replan, health dashboard

The gap is **behavioral wiring**, not measurement invention:

- Agents can skip drift scoring and still claim extend-ready.
- There is no single **Identity Continuity Protocol** with stable step IDs.
- Handoffs do not have a **named required section** for drift evidence that QA/Continuity always read.
- DNA handoff prose still says “reject if > 2.5” while the studio’s tooling path is evidence + agent judgment (no CLI hard gate in this epic).

Production pain: identity slip across clips because protocol is optional and evidence is not a first-class handoff contract.

## Goals

1. One canonical **Identity Continuity Protocol** agents cite by path and version.
2. In-scope Role Cards + matching skills document **required** ICP steps they own.
3. Additive **`drift_evidence`** section on extend/identity handoffs (object or array for multi-cast).
4. `handoff-packet-validator` **schema-checks** and **warns** on missing/incomplete evidence for extend-type packets — does **not** block `sequence` extend execution.
5. Map existing clip field `identity_drift` → handoff `drift_evidence` without breaking sequence JSON.
6. Align agent language with threshold **2.5** (pass / risk / incomplete / skipped).

## Non-goals

- New agents or Role Cards
- CLI hard-block, `--force`, or Studio Director-only override flags (future epic)
- Vision-model / evidence-quality upgrades to the scorer
- Multi-cast arbiter redesign (reference multi-char; support `drift_evidence[]` only)
- NSFW-only forks (same protocol; reuse tools)
- Plugin pack membership changes unless a release pin is required for skill text
- Changing Imagine model stack or `VIDEO_PIPELINE_SPEC`

---

## Architecture

```text
Production Bible / DNA (locked)
        │
        ▼
┌───────────────────┐     sequence drift-score      ┌────────────────────┐
│ Identity Lock     │ ────────────────────────────► │ drift_evidence     │
│ (+ DNA Extractor) │   (agent runs / requests CLI) │ (handoff section)  │
└─────────┬─────────┘                               └──────────┬─────────┘
          │ required before extend                             │
          ▼                                                    │
┌───────────────────┐   LAST_FRAME + inject + evidence         │
│ Sequence Extender │ ◄────────────────────────────────────────┘
└─────────┬─────────┘
          │ continuity_state includes / mirrors drift_evidence
          ▼
┌───────────────────┐     Chain QA identity criteria
│ Continuity + QA   │ ◄── reads evidence; flags if missing (protocol)
└───────────────────┘
          │
          ▼  Go / No-Go (agent judgment; CLI not blocked)
```

### Units

| Unit | Responsibility | Depends on |
|------|----------------|------------|
| **Identity Continuity Protocol** | Checklist: when to score, thresholds, who fills fields, handoff order | `identity_drift` / `sequence drift-score` |
| **Character DNA Extractor** | DNA + inject ready; baseline refs for scoring | Protocol § DNA prerequisites |
| **Identity Lock Specialist** | Lock status; require drift vs DNA + prior end-state before approving extend | Protocol + drift CLI |
| **Cinematic Sequence Extender** | Do not claim extend-ready without filled `drift_evidence` (protocol language) | Handoff schema |
| **Continuity Guardian** | Mirror/check evidence in `continuity_state`; trend flags | Protocol + continuity fields |
| **QA / Chain QA** | Map identity criteria to evidence; missing → identity risk finding | Protocol + 10-pt mapping |
| **Handoff packet validator** | Shape validation; warn codes only | Schema |
| **Sequence Director** (light) | Long-form breakdown includes identity gate step before each extend | Protocol reference |

### Flow rules

1. **Pre-extend** (clip N→N+1 and re-gen): Identity Lock path produces or refreshes `drift_evidence`.
2. **Handoff:** Extender consumes DNA inject + `LAST_FRAME_RECAP` + `drift_evidence` together.
3. **Post-clip / chain QA:** Continuity + QA read the same section; no second identity log.
4. **Missing evidence:** Agents must flag and recommend `sequence drift-score`; they must not invent scores; CLI does not stop the user.

### Compatibility with existing tools

| Existing | Relationship to this design |
|----------|----------------------------|
| Clip field `identity_drift` (from `sequence drift-score`) | **Source report** on `sequence.json` clips |
| Handoff section `drift_evidence` | **Agent-facing contract** projected from scorer output (+ metadata) |
| DNA `identity_lock_handoff` | Gains `drift_evidence` when Lock completes ICP-02/03; instructions text soft-aligned to protocol |
| `sequence_extend_handoff` | Must carry `drift_evidence` (object or array) per protocol |
| Threshold 2.5 | Unchanged; scorer `pass` ↔ protocol `status=pass` when score &lt; 2.5 |

Implementation should provide a small pure helper (e.g. `identity_drift_report_to_drift_evidence(report, …)`) so agents and optional CLI export paths do not fork field names.

---

## Protocol steps & packet schema

### Canonical artifact

| Item | Spec |
|------|------|
| **Name** | Identity Continuity Protocol |
| **Path** | `references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md` |
| **Version** | `1.0` (bump when required fields change) |
| **Cited as** | `[IDENTITY_CONTINUITY_PROTOCOL: v1.0]` |

### Required steps (ICP)

| ID | When | Owner | Action |
|----|------|-------|--------|
| **ICP-01** | Character onboard / re-lock | DNA Extractor → Identity Lock | DNA complete; hero refs locked; inject blocks available |
| **ICP-02** | Before extend (N→N+1) or re-gen | Identity Lock (Extender verifies) | Run / request `sequence drift-score` vs DNA + prior end-state / last-frame context |
| **ICP-03** | Same moment as ICP-02 | Identity Lock | Fill **`drift_evidence`** on the extend (and Lock) handoff |
| **ICP-04** | Extend prompt build | Sequence Extender | Attach DNA inject + identity constraints; do not mark extend-ready if evidence missing or `status=skipped` without Director note |
| **ICP-05** | After clip / before next extend | Continuity Guardian | Mirror key fields into `continuity_state`; flag worsening trend |
| **ICP-06** | Chain QA / 16-pt as applicable | QA Guardian / Chain QA | Map identity criteria to `drift_evidence`; missing → identity risk + fix = run ICP-02/03 |
| **ICP-07** | No-Go on identity | Identity Lock + Extender | Refresh score after fix; new evidence supersedes prior; increment `attempt` |

### Threshold language (protocol, not hard gate)

| Condition | `status` | Agent behavior |
|-----------|----------|----------------|
| `score < 2.5` | `pass` | Proceed |
| `score >= 2.5` | `risk` | Call out; recommend fix / re-score; user may continue |
| Score / section missing | `incomplete` | Flag; recommend ICP-02/03 |
| User elects skip | `skipped` | Requires `skipped_reason`; Extender notes waiver |

### `drift_evidence` schema (additive)

```json
"drift_evidence": {
  "schema_version": "1.0",
  "protocol": "IDENTITY_CONTINUITY_PROTOCOL",
  "protocol_version": "1.0",
  "clip_id": "string",
  "character_slug": "string",
  "scored_at": "ISO-8601",
  "tool": "sequence drift-score",
  "score": 0.0,
  "threshold": 2.5,
  "status": "pass | risk | incomplete | skipped",
  "baseline": {
    "dna_slug": "string",
    "dna_version": 1,
    "reference_hint": "optional hero plate id or path"
  },
  "signals": {
    "summary": "short human/agent summary",
    "flags": ["optional", "tags"]
  },
  "attempt": 1,
  "notes": "optional",
  "skipped_reason": "only if status=skipped"
}
```

**Required for complete evidence:**  
`schema_version`, `protocol`, `protocol_version`, `clip_id`, `character_slug`, `scored_at`, `tool`, `score`, `threshold`, `status`, `baseline.dna_slug`, `attempt`.

**Multi-cast:** prefer `drift_evidence` as an **array** of objects when 2+ characters; single **object** allowed for one cast. Validator accepts object **or** array.

### Validator behavior

| Check | Result |
|-------|--------|
| Section present + required fields | OK |
| Extend-type packet missing section | **Warning** (not hard fail of entire packet by default) |
| `status=risk` | Warning + surface score |
| `status=skipped` without `skipped_reason` | Warning |
| Unknown `status` / bad types | Schema **error** for the section |
| Legacy packets without section | Still parseable; warn only for extend-related packet types |

**No change** to `sequence run` / extend execution exit codes in this epic.

Suggested extend-related `packet_type` values to treat as warn-if-missing (confirm during implementation against `validate_handoff.py` / builders):

- `sequence_extend_handoff`
- `identity_lock_handoff` (when used as pre-extend Lock packet after ICP-02)
- Any sequence chain handoff that marks `phase=extend` if such a flag exists

### Role Card / skill patch pattern

For each in-scope agent:

1. Keep **Model Layer (Grok 4.5)** block unchanged.
2. Add **Identity Continuity (required)** subsection: owned ICP step IDs + link to protocol path.
3. Output format: emit/consume `drift_evidence` when their step runs.
4. Soft language: “do not claim ready without evidence”; do not promise CLI refusal.
5. Soft-align any “reject if > 2.5” DNA/Lock lines to **risk + recommend correction** (agent may still refuse creatively; tooling does not hard-block).

**In-scope surfaces**

| Role Card | Skill |
|-----------|--------|
| `Identity_Lock_Specialist.md` | `identity-lock-specialist` |
| `Character_DNA_Extractor_v3.5.md` | `character-dna-extractor` |
| `Cinematic_Sequence_Extender.md` | `cinematic-sequence-extender` |
| `Continuity_Consistency_Guardian.md` | `continuity-consistency-guardian` |
| `Quality_Assurance_Guardian_v3.5.md` | `quality-assurance-guardian` (+ `chain-qa-protocol` skill touch) |
| `Sequence_Director.md` (light routing only) | `sequence-director` (light) |

Optional one-liner: `Studio_Director.md` / long-form preset in `AGENT_INDEX.md`.

---

## Error handling

| Situation | Agent behavior | Tooling |
|-----------|----------------|---------|
| Drift CLI not run | `status=incomplete`; instruct `sequence drift-score` | Validator warns |
| Score ≥ 2.5 | `status=risk`; recommend re-inject / hero plate / re-gen | No CLI block |
| User skips | `status=skipped` + required `skipped_reason` | Warn if reason missing |
| Stale evidence (wrong `clip_id`) | Continuity/QA flag; request ICP-02 refresh | Optional clip_id consistency warn |
| Multi-cast partial set | Incomplete set; Lock/Arbiter call out gaps | Warn per incomplete array element |
| Legacy handoff without section | Treat as incomplete for long-form claims | Warn on extend-type packets |

---

## Testing

| Layer | What to test |
|-------|----------------|
| Schema / validator | Object or array; required fields; warn on missing extend section; skipped without reason; invalid status |
| Mapping helper | `identity_drift` report → `drift_evidence` field completeness |
| Fixtures | Extend handoff with/without evidence; multi-char array |
| Docs consistency | ICP step IDs match Role Card ownership (checklist or lightweight verify) |
| Non-goals | No e2e Imagine generation; no hard-gate exit-code tests |

---

## Rollout

1. Protocol doc v1.0 + schema constants / mapping helper + validator warn paths.
2. Role Cards + skills (same PR or tight follow-up).
3. `AGENT_INDEX.md` long-form preset one-liner + optional Studio Director pointer.
4. CHANGELOG under Unreleased / next patch note (deepen agents; not “new agent suite”).
5. Plugin catalog pin only when shipping skill text in a release (existing pin hygiene).

### Suggested implementation order (for writing-plans)

1. Protocol markdown + schema types / required field list  
2. Mapping helper + unit tests  
3. Validator warn paths + fixtures  
4. Role Cards + skills (batch by agent)  
5. AGENT_INDEX / light Sequence Director  
6. DNA handoff instruction soft-align + optional builder field when score available  

---

## Risks

| Risk | Mitigation |
|------|------------|
| Protocol ignored in chat | Stable ICP-IDs; “required” language; Sequence Director / Studio Director pointers |
| Schema churn | `schema_version` 1.0; additive only |
| Dual Method A/B skill copies | Edit project `.grok/skills/`; users update plugin on release |
| Confusion with hard gates | Design + protocol state **warn-only** explicitly |
| Field dualism (`identity_drift` vs `drift_evidence`) | Document mapping; single helper; do not rename clip field in this epic |

---

## Acceptance criteria

- [ ] `references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md` v1.0 published
- [ ] All in-scope Role Cards + skills own their ICP steps and link the protocol
- [ ] `drift_evidence` documented; object **or** array accepted
- [ ] Validator warns on incomplete/missing evidence for extend-type packets
- [ ] Mapping from clip `identity_drift` documented (and helper tested if implemented)
- [ ] No new agents; no CLI hard-block on extend
- [ ] Tests cover validator warn/accept paths
- [ ] AGENT_INDEX long-form preset references identity continuity wiring

---

## Approaches considered

| Approach | Outcome |
|----------|---------|
| **1. Protocol hub + agent patches** | **Selected** — single source of truth, matches “upgrade before invent” |
| 2. Schema-first only, light agent notes | Rejected — weak wiring (user’s primary goal) |
| 3. Full closed-loop (score → gate → re-gen) | Rejected for this epic — user chose protocol-only enforcement |

---

## Relationship to prior work

- **Parent track:** [Long-form continuity roadmap](./2026-07-09-long-form-continuity-roadmap-design.md) (#1–#12 shipped).
- **This design:** Deepens **agent consumption** of #1 (and related identity surfaces) without reopening measurement or hard-gate epics.
- **Deferred follow-ups:** Hard/soft CLI gates; evidence-quality upgrades; multi-cast depth beyond array support.

---

## Next step

After user review of this written spec: invoke **writing-plans** for implementation (protocol → schema/validator → Role Cards/skills → index).

---

*Grok Imagine Cinematic Studio — Identity Continuity Agent Wiring design — 2026-07-11*
