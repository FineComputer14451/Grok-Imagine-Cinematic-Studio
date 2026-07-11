# Design: Identity Strict CLI Gates (Opt-in Hard Fail)

**Date:** 2026-07-11  
**Topic:** Opt-in `--strict-identity` hard-fail on extend-path CLI commands  
**Status:** Design approved — ready for implementation planning  
**Target version:** 3.8.x patch (tools + CLI + protocol note)  
**Approach:** Shared pure gate helper + flags on `sequence handoff` and `sequence extend-prompt` only  
**Parent:** [Identity Continuity Agent Wiring](./2026-07-11-identity-continuity-agent-wiring-design.md) (protocol + warn-only validator)

## Summary of Decisions

| Decision | Choice |
|----------|--------|
| Default behavior | **Unchanged** — warn-only / no CLI hard-block |
| Hard mode | **Opt-in only** via `--strict-identity` |
| Surfaces | **Extend path only:** `sequence handoff`, `sequence extend-prompt` |
| Fail matrix | **Missing + risk** |
| Skipped with reason under strict | **Fail** (skip is not a pass when hard mode is requested) |
| Bible / sequence auto-strict | **Out of scope** |
| Validator default | **Unchanged** (warn-only); no required validator flag in this epic |
| Precedent | Mirrors `sequence temp gate --strict` exit-1 pattern |

## Problem

Identity Continuity Protocol v1.0 wires agents and attaches `drift_evidence`, and the handoff validator **warns** when evidence is missing. Automation and CI still need a way to **refuse** extend handoff/prompt generation when identity is incomplete or at risk — without turning hard-fail on for every interactive session.

## Goals

1. Opt-in hard-fail on `sequence handoff` and `sequence extend-prompt` via `--strict-identity`.
2. Fail when evidence is **missing/incomplete** or **risk** (score ≥ 2.5 / scorer not pass / `status=risk`).
3. Keep default (no flag) behavior identical to today.
4. Single pure, unit-tested evaluator shared by both commands.
5. Evaluate **before** writing success artifacts so failed strict runs do not leave “green” handoff files.
6. Document opt-in mode on the Identity Continuity Protocol.

## Non-goals

- Default hard-fail for any sequence command  
- Auto-enable from Production Bible, sequence JSON policy, or `identity_lock_status=locked`  
- Gating `sequence qa`, `qa-assist`, `run`, or `drift-score`  
- Required changes to `validate_handoff.py` exit codes (optional follow-up)  
- Vision / evidence-quality upgrades to the scorer  
- New agents or Role Cards  
- Changing default threshold (remains **2.5**)

---

## Architecture

```text
sequence handoff | sequence extend-prompt
        │
        ├─ load sequence + clip
        │
        └─ if --strict-identity:
                 evaluate_identity_strict_gate(clip, drift_evidence?)
                      │
                      ├─ pass → build + write/print → exit 0
                      └─ fail → print reasons + fixes → exit 1
                                 (no success file write)
           else:
                 build + write/print → exit 0  (today)
```

### Units

| Unit | Responsibility |
|------|----------------|
| `evaluate_identity_strict_gate` | Pure fail/pass decision from clip + optional evidence |
| `sequence handoff` | Optional flag; gate before write |
| `sequence extend-prompt` | Optional flag; gate before write/print |
| Protocol doc | Document CLI opt-in hard mode |

### Helper contract

```python
def evaluate_identity_strict_gate(
    *,
    clip: dict[str, Any],
    drift_evidence: dict | list | None = None,
    threshold: float = DEFAULT_DRIFT_THRESHOLD,  # 2.5
) -> dict[str, Any]:
    """
    Returns:
      {
        "pass": bool,
        "strict": True,
        "status": "pass" | "risk" | "incomplete" | "skipped" | "missing",
        "reasons": list[str],
        "fixes": list[str],
        "score": float | None,
        "threshold": float,
      }
    """
```

**Suggested location:** `tools/identity_drift.py` (alongside `report_to_drift_evidence`) unless the file grows too large — then `tools/identity_gate.py` importing from `identity_drift`.

### Evidence resolution order

1. If `drift_evidence` argument is provided → normalize via `normalize_drift_evidence` and evaluate each item.  
2. Else if `clip["identity_drift"]` is a dict with `drift_score` present → project with `report_to_drift_evidence` (slug from `clip.character_slug` or report or `"unknown"`).  
3. Else → `status=missing`, `pass=False`.

### Fail matrix (`--strict-identity`)

| Condition | Result |
|-----------|--------|
| No evidence | **fail** `missing` |
| `status=incomplete` | **fail** |
| `status=skipped` (with or without reason) | **fail** (strict rejects skip) |
| `status=risk` OR scorer `pass is False` OR score ≥ threshold | **fail** `risk` |
| Multi-cast array: any element fails | **fail** |
| All items `status=pass` and (score is None or score &lt; threshold) | **pass** |

### CLI

```bash
python tools/cinematic_studio_cli.py sequence handoff "Seq" --clip clip_001 --strict-identity
python tools/cinematic_studio_cli.py sequence extend-prompt "Seq" --clip clip_001 --beat "..." --strict-identity
```

- Flag name: **`--strict-identity`** (explicit; do not overload `temp gate --strict`).  
- On fail: Rich/console print of `reasons` + `fixes` (e.g. run `sequence drift-score`, complete ICP-02/03); `raise typer.Exit(1)`.  
- On pass with flag: optional dim line that strict gate passed.

### Fixes copy (minimum)

- `"Run: sequence drift-score \"{name}\" --clip {clip} --dna characters/{slug}/dna.json"`  
- `"Attach drift_evidence (ICP-02/03); see IDENTITY_CONTINUITY_PROTOCOL_v3.8.md"`  
- On risk: scorer `fixes` when available + reinforce DNA / re-lock

### Write policy

| Command | On strict fail |
|---------|----------------|
| `handoff` | Do **not** write the handoff JSON path |
| `extend-prompt` | Do **not** write `--output` file; do not print success panel as if ready |

---

## Testing

| Case | Expected |
|------|----------|
| No evidence | `pass=False`, `status=missing` |
| `identity_drift` pass, score &lt; 2.5 | `pass=True` |
| `identity_drift` fail / score ≥ 2.5 | `pass=False`, `status=risk` |
| `drift_evidence` status `pass` | `pass=True` |
| `status=skipped` with reason | `pass=False` |
| Multi-cast: one risk in array | `pass=False` |
| Regression: helper not called / soft path | Existing handoff tests still pass without flag |

CLI integration tests optional if the suite lacks Typer runners; pure helper is mandatory.

---

## Docs & rollout

1. Implement helper + tests.  
2. Wire both commands.  
3. Protocol subsection: **CLI opt-in hard mode**.  
4. CHANGELOG Unreleased bullet.  
5. No plugin catalog pin required unless packaging a release that only ships docs (skills unchanged if protocol-only + tools).

### Protocol doc addition (sketch)

```markdown
## CLI opt-in hard mode

Default: no CLI hard-block (agent protocol + warn-only validator).

With `--strict-identity` on `sequence handoff` or `sequence extend-prompt`:
exit 1 when drift evidence is missing/incomplete/skipped or status=risk
(score ≥ 2.5). Evaluate before writing artifacts.
```

---

## Risks

| Risk | Mitigation |
|------|------------|
| Users expect Bible auto-strict | Explicit non-goal; document flag-only |
| Skipped-with-reason surprises under strict | Document: strict never accepts skip |
| Dual evidence sources disagree | Prefer explicit `drift_evidence` arg; else clip report |
| False confidence if write-then-fail | Evaluate before write |

---

## Acceptance criteria

- [ ] `evaluate_identity_strict_gate` implemented and unit-tested  
- [ ] `sequence handoff --strict-identity` exits 1 on missing/risk; no success file  
- [ ] `sequence extend-prompt --strict-identity` exits 1 on missing/risk; no success output file  
- [ ] Without flag: behavior unchanged  
- [ ] Protocol + CHANGELOG updated  
- [ ] No new agents; no default hard-fail  

---

## Approaches considered

| Approach | Outcome |
|----------|---------|
| **1. Shared helper + flags on handoff/extend-prompt** | **Selected** |
| 2. Validator-only hard mode | Rejected — easy to skip; weak extend-prompt coverage |
| 3. Sequence JSON / Bible auto-strict | Rejected — user chose flag-only opt-in |

---

## Relationship to prior work

- Builds on ICP v1.0, `report_to_drift_evidence`, warn-only validator.  
- Does not replace agent protocol; hardens **optional automation** only.  
- Future: soft hybrid (Bible `strict_identity`), validator `--strict-identity`, QA/run gating.

---

## Next step

After user review of this written spec: invoke **writing-plans** for implementation.

---

*Grok Imagine Cinematic Studio — Identity Strict CLI Gates design — 2026-07-11*
