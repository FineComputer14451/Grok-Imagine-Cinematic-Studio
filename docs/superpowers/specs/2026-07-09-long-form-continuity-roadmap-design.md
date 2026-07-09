# Design: Long-Form Continuity Capability Roadmap (v3.7+)

**Date:** 2026-07-09  
**Topic:** Ranked backlog of additional tools, agents, and skills for long-form continuity  
**Status:** Design approved — ready for implementation planning  
**Approach:** Gap audit of the existing long-form stack (upgrade/tool-first; new Role Cards only for judgment gaps)

## Summary of Decisions

| Decision | Choice |
|----------|--------|
| Outcome | Capability **roadmap** (ranked backlog), not implementation |
| Priority driver | **Production pain** in real sessions |
| Pain center | **Long-form continuity** (extend/stitch, identity, QA, multi-clip flow) |
| Pain breadth | Full A–F cluster: identity drift, visual seams, narrative arc, chain QA overhead, audio continuity |
| Scope width | **Long-form track only** (not full studio roadmap) |
| Backlog shape | **Ranked list** with pain → outcome → rough effort |
| Methodology | **Gap audit** of current suite; prefer tools/upgrades over new agents |
| First build epic (suggested) | Items **#1–#3** (identity drift + seam report + chain QA assist v2) |

## Goal

Produce a **v3.7+ long-form continuity capability roadmap**: an ordered backlog of proposed **tools / skills / agents**, each with:

- **Pain** addressed (identity, seams, narrative, chain QA, audio)
- **Outcome** in real extend sessions
- **Rough effort** (S / M / L)
- **Type** (tool upgrade | new tool | skill | agent | Role Card upgrade)

Enough to pick **what to build next** — not implementation plans in this document.

## Scope

### In scope

- 60–180s+ extend/stitch pipelines (SFW primary; NSFW where the gap is shared)
- Baseline stack: Sequence Director, Cinematic Sequence Extender, Identity Lock, Character DNA, Continuity Guardian, Chain QA (+ assist), handoff packet validator, sequence runner/CLI, Sonic Architect / `audio_momentum_vector` fields
- Prefer **upgrades and tools** over new Role Cards when the gap is enforcement or measurement

### Non-goals

- Full studio roadmap (marketing, Web UI redesign, new genres, general onboarding)
- Implementation code, scaffolding, or plugin catalog pin work in this design phase
- Ideal greenfield pipeline redesign
- Role Card personality rewrites without a capability gap
- A separate full vision-QA product as its own agent (may power tools #1–#3 later)

## Approaches Considered

### 1. Gap audit of existing long-form stack (selected)

Inventory current coverage, map each pain to covered / partial / missing, invent new units only where the gap is real. Rank by pain × frequency × quota saved ÷ effort.

### 2. Ideal long-form pipeline first (rejected)

Design target architecture then backfill everything missing. Higher risk of reinventing DNA / Continuity / Chain QA; weaker pick-order for v3.7.

### 3. Instrumentation-first only (partial influence)

Prefer CLI/metrics/validators before agents. Adopted as a **bias** inside Approach 1, not the sole method (narrative/emotion still needs agent-facing skills).

## Gap Audit

### Baseline units and limits

| Unit | What it does today | Limit for long-form |
|------|--------------------|---------------------|
| Character DNA + Identity Lock | DNA profiles, handoff packets, drift threshold **2.5** in text/JSON | Drift is **declarative**, not measured from frames; multi-char arbitration is thin |
| Sequence chain (`tools/sequence_chain.py`) | Scaffold, clips, handoffs, extend prompts, 10-pt chain QA schema | QA often **metadata-filled**, not vision/pixel-aware |
| Chain QA assist (`tools/chain_qa_assist.py`) | Heuristics from recap length, field fill ratios, duration | High scores possible without looking at the actual clip |
| Handoff packet validator | JSON shape validation | Does not score continuity quality |
| Continuity Guardian (skill / Role Card) | Protocol + agent judgment | Little dedicated CLI for `continuity_state` diffs across N clips |
| Cinematic Sequence Extender | Plans + scripts for extend/stitch | Strong planning; weak closed-loop re-gen after No-Go |
| Sequence Director | Clip breakdown, dependency orchestration | Weak **emotional temperature** enforcement over the whole arc |
| Sonic Architect / AMV fields | Native audio design + `audio_momentum_vector` keys | No checksum/diff of AMV across stitches; dialogue state easy to drop |
| NSFW chain QA / extender | Parallel 8-pt + sensual pacing | Same metadata-assist gap; shared tooling opportunity |

### Pain × coverage matrix

| Pain | Coverage | Gap type |
|------|----------|----------|
| **A. Identity / DNA drift** | Partial — DNA inject + threshold language | **Measurement + multi-char lock** missing |
| **B. Visual seam / physics** | Partial — chain QA checks exist | **Evidence** (last-frame compare, artifact flags) missing |
| **C. Emotional / narrative arc** | Partial — `emotional_temperature_curve` field, Narrative Arc agent | Not wired into extend gates or auto replan |
| **D. Chain QA overhead** | Partial — 10-pt + assist CLI | Assist is weak; no batch re-score; slow human loop |
| **E. Audio continuity** | Partial — AMV in handoffs | No AMV integrity tool; stitch audio not validated |
| **Cross-cutting** | Handoffs + `sequence.json` | No first-class **sequence memory bank** (running world/cast state) |

### Design rules from the audit

1. **Upgrade before invent** when a Role Card already owns the judgment.
2. **New tool** when the gap is measurement, diff, or closed-loop re-gen.
3. **New skill/agent** only when no owner exists or multi-agent coordination needs a dedicated commander.
4. **Shared SFW/NSFW** tooling where the failure mode is the same (drift, seam, AMV).

## Ranked Backlog

**Ranking formula (qualitative):**  
pain severity × frequency in long-form sessions × quota saved if fixed ÷ effort  

**Effort:** **S** (~1–2 focused PRs) · **M** (multi-file + tests + skill touch) · **L** (new agent surface + protocols + CLI + docs)

| Rank | Name | Type | Pain | Outcome | Effort |
|------|------|------|------|---------|--------|
| **1** | **Identity Drift Scorer** | New tool (+ thin skill wrapper) | A | Before each extend, score face/wardrobe/ref fidelity vs DNA + previous end-state; block or flag if above threshold (replace “trust the prose” with a number) | M |
| **2** | **Last-Frame Seam Report** | New tool | B, D | Extract/compare last frame of clip N vs first of N+1 (or recap+ref); emit seam risk + suggested fixes for chain QA | M |
| **3** | **Chain QA Assist v2** | Tool upgrade (`chain_qa_assist`) | D, B, A | Fold drift score + seam report into the 10-pt assist; fewer false high scores; `--apply` with evidence trail | M |
| **4** | **Sequence Memory Bank** | New tool + sequence schema fields | A, B, C, E | Running cast/prop/lighting/emotion/audio state across the whole sequence; handoffs read/write one bank, not ad-hoc clip fields only | M–L |
| **5** | **Extend Re-Gen Loop** | Tool upgrade (`sequence_runner` / extender scripts) | D, B | On No-Go: auto-build targeted fix prompt from QA fixes + memory bank; track attempt budget (quota-aware) | M |
| **6** | **Audio Momentum Integrity** | New tool | E | Diff/validate `AUDIO_MOMENTUM_VECTOR` across stitch; flag dropped dialogue state, SFX timing gaps, music cue breaks | S–M |
| **7** | **Emotional Temperature Gate** | Tool + skill touch (Narrative Arc / Sequence Director) | C | Enforce `emotional_temperature_curve` vs planned beats at extend time; warn when arc goes flat or spikes without plan | M |
| **8** | **Multi-Character Identity Arbiter** | New skill + Role Card (optional agent) | A | When 2+ locked characters share a frame/sequence: conflict rules, primary lock, dual-DNA inject order | L |
| **9** | **Continuity Diff CLI** | New tool (strengthens Continuity Guardian) | B, A | `continuity_state` / memory bank diff clip-to-clip; human-readable report for Guardian / QA | S |
| **10** | **Long-Form Health Dashboard** | Tool upgrade (CLI dashboard / report) | D (+ long-form ops) | Per-sequence: chain QA status, drift trend, seam risks, re-gen count, estimated remaining cost | S–M |
| **11** | **Stitch Artifact Lexicon** | Skill reference + optional agent notes | B | Shared vocabulary + negative-prompt packs for flicker/morph/halo; Prompt Master + Extender consume | S |
| **12** | **Arc Replan Co-pilot** | Skill (Sequence Director upgrade or thin skill) | C | After mid-sequence failure or drift lock, replan remaining clip beats without rewriting whole Bible | M |

### Suggested build order rationale (top 5)

1. **#1 → #2 → #3** form a **closed evidence loop** for the worst re-gen tax (identity + seams + QA).
2. **#4 → #5** make extends **stateful and recoverable**.
3. **#6 → #7** close audio + narrative without new crew.
4. **#8** only when multi-cast productions dominate.

### Explicit non-items (deferred / not long-form track)

- New marketing, trailer, or key-art agents
- Web UI redesign
- Full vision-model QA product as a standalone agent
- Greenfield “Timeline Director” replacing Sequence Director

## Type Conventions (for later implementation)

| Type | When |
|------|------|
| **Tool** (`tools/*.py` + CLI) | Measurement, diffs, reports, re-gen loop, memory bank I/O |
| **Skill** | Agent-facing workflow that orchestrates tools + handoffs |
| **Role Card / agent** | Soft creative judgment with no clear single tool owner (#8, parts of #12) |
| **Upgrade** | Prefer when Continuity Guardian / Chain QA / Extender already own the domain |

### NSFW policy

Reuse the same tools (#1–#6, #9–#10). Do **not** fork parallel scorers unless an 8-pt check has no SFW twin.

## How to Use This Roadmap

1. **Pick from the top** unless a session is blocked by a lower item (e.g. multi-cast → jump to #8).
2. Each build should be a **single capability** (one tool or one upgrade), with tests + CLI surface; skill/Role Card touch only if agents must call it.
3. After each ship: re-rank only if production pain shifts (living doc under Unreleased or a revised design).
4. Next process step after this design is approved in-repo: **writing-plans** for the first epic (**#1–#3 evidence loop**), not ad-hoc coding.

## Architecture Sketch (target, not implementation)

```
sequence.json
  ├── clips[] (existing)
  ├── emotional_temperature_curve (existing; gated by #7)
  └── memory_bank (#4)  ←── Continuity Diff (#9)
         ▲
         │ read/write on handoff
         │
extend path:
  DNA / Identity Lock ──► Drift Scorer (#1) ──┐
  last/first frames ──► Seam Report (#2) ────┼──► Chain QA Assist v2 (#3) ──► Go / No-Go
  AMV ──► Audio Integrity (#6) ──────────────┘         │
                                                       ▼ No-Go
                                              Extend Re-Gen Loop (#5)
                                              (+ Arc Replan #12 if mid-arc)
```

v1 of #1/#2 may use **metadata + frame extract / structural heuristics** (hashes, histogram, optional face landmarks if available). Optional vision-model scoring can land later without changing backlog rank.

## Schema / Compatibility Notes

- **Sequence Memory Bank (#4)** may require a small `sequence.json` schema bump (`schema_version` 1.0 → 1.1 or 2.0). That bump is **part of item #4**, not a separate roadmap entry.
- Existing handoff packet shapes remain valid; memory bank is additive and can mirror into `continuity_state` for backward compatibility during transition.
- Chain QA 10-point check IDs stay stable; Assist v2 only improves scoring inputs and evidence trails.

## Risks and Assumptions

| Risk / assumption | Mitigation |
|-------------------|------------|
| Drift/seam tools without full vision still help | Ship heuristics + frame compare first; wire vision later behind same CLI |
| Memory bank schema churn | Additive fields; dual-read in handoffs for one release |
| Suite bloat from new agents | Only #8 (and optionally #12 as skill) add agent surface; rest are tools |
| Quota cost of re-gen loop | Explicit attempt budget + Workflow Quota Optimizer hooks in #5 plan |

## Acceptance Criteria (this design document)

- [x] Scoped to long-form continuity only
- [x] Gap audit against current stack
- [x] Ranked 1–12 with pain → outcome → effort
- [x] Explicit non-items
- [x] Written to `docs/superpowers/specs/2026-07-09-long-form-continuity-roadmap-design.md`
- [ ] User review of the written spec
- [ ] Implementation plan via writing-plans (after user approves this file)

## Next Step

After user approves this written spec: invoke **writing-plans** for the first implementation epic — **Identity Drift Scorer + Last-Frame Seam Report + Chain QA Assist v2** (#1–#3).

---

*Grok Imagine Cinematic Studio — long-form continuity roadmap design — 2026-07-09*
