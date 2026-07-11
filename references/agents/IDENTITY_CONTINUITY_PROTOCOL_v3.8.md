# Identity Continuity Protocol v1.0 (studio v3.8)

**Cited as:** `[IDENTITY_CONTINUITY_PROTOCOL: v1.0]`  
**Path:** `references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md`  
**Enforcement:** Agent protocol only — CLI does **not** hard-block extend when evidence is missing.  
**Tooling:** `python tools/cinematic_studio_cli.py sequence drift-score`  
**Threshold:** drift score must stay **below 2.5** for `status=pass` (Identity Lock convention).

## Purpose

Make identity drift handling mandatory for long-form extend/stitch: score → record `drift_evidence` → consume in Extender / Continuity / QA — without new agents.

## Step IDs

| ID | When | Owner | Action |
|----|------|-------|--------|
| **ICP-01** | Character onboard / re-lock | DNA Extractor → Identity Lock | DNA complete; hero refs locked; inject blocks available |
| **ICP-02** | Before extend (N→N+1) or re-gen | Identity Lock (Extender verifies) | Run `sequence drift-score` vs DNA + prior end-state |
| **ICP-03** | Same moment as ICP-02 | Identity Lock | Fill `drift_evidence` on Lock + extend handoffs |
| **ICP-04** | Extend prompt build | Sequence Extender | Attach DNA inject; do not claim extend-ready if evidence missing or `skipped` without Director note |
| **ICP-05** | After clip / before next extend | Continuity Guardian | Mirror status/score into `continuity_state`; flag worsening trend |
| **ICP-06** | Chain QA / full QA | QA Guardian / Chain QA | Map identity criteria to evidence; missing → identity risk finding |
| **ICP-07** | No-Go on identity | Identity Lock + Extender | Fix → re-score → new evidence; increment `attempt` |

## Status language

| Condition | status | Agent behavior |
|-----------|--------|----------------|
| score &lt; 2.5 | `pass` | Proceed |
| score ≥ 2.5 | `risk` | Call out; recommend fix; user may continue (no CLI block) |
| Not scored | `incomplete` | Flag; run ICP-02 |
| User skip | `skipped` | Requires `skipped_reason` |

## Clip vs handoff fields

| Location | Field | Role |
|----------|-------|------|
| `sequence.json` clip | `identity_drift` | Raw scorer report from CLI |
| Handoff packet | `drift_evidence` | Agent contract (object or array) |
| Mapper | `identity_drift.report_to_drift_evidence` | Projection helper |

## `drift_evidence` shape

See design spec and `tools/identity_drift.py` (`report_to_drift_evidence`).  
Multi-cast: array of evidence objects (one per character).

## Validator

`handoff-packet-validator`: warns if missing/incomplete on extend-type packets; errors only on invalid schema (e.g. bad `status`). Exit 0 with warnings.

## Related agents

Identity Lock · Character DNA Extractor · Cinematic Sequence Extender · Continuity Guardian · QA Guardian · Sequence Director (routing) · Chain QA Protocol

---

*Identity Continuity Protocol v1.0 — Grok Imagine Cinematic Studio v3.8 · deepen existing agents*
