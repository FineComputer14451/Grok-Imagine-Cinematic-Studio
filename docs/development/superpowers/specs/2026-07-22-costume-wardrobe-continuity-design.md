# Design: Costume & Wardrobe Continuity Agent (P1)

**Date:** 2026-07-22  
**Topic:** New core agent for structured outfit DNA, wardrobe inject blocks, and clip-level wardrobe state  
**Status:** Design approved — ready for implementation planning  
**Target version:** 3.8.x / 3.9.x (new skill + Role Card; suite count 51 → 52)  
**Approach:** Nested `wardrobe_lock` on Character DNA + skill/Role Card + optional handoff fields (no new CLI)

## Summary of Decisions

| Decision | Choice |
|----------|--------|
| Roadmap position | **P1** of five-agent backlog (then Dialogue → Failure Recovery → Score → Platform Delivery) |
| Scope depth | **Core lock only** — outfit DNA, inject, state; no fashion-ideation mode |
| Multi-cast | **Primary character only**; secondary = short `secondary_notes` |
| State richness | **Structured core** — garments, materials, silhouette, accessories, layers, condition, optional delta |
| Product surface | **Skill + Role Card + handoff fields**; no new CLI in P1 |
| Data home | **Nested under Character DNA** (not parallel wardrobe files, not sequence-only) |
| Packet type | **No new required packet type** — optional `wardrobe` on identity / sequence handoffs |

## Problem

Character DNA today carries a flat `clothing_style` string. Production Designer owns set/props; Identity Lock owns face/body continuity. **Clothing drift** across stills → i2v → extend is common and has no dedicated owner:

- Signature coats, accessories, and layer order get paraphrased away in long chains.
- Condition changes (wet, damaged) are ad hoc prose in recaps, not structured state.
- Multi-cast scenes have no rule for who gets a full wardrobe lock vs a note.
- Continuity Guardian and Chain QA cannot check against a stable wardrobe contract.

## Goals

1. Add **Costume & Wardrobe Continuity** as a first-class agent (Role Card + skill).
2. Nest structured **`wardrobe_lock`** on Character DNA; keep `clothing_style` as a synced one-line summary.
3. Emit **wardrobe inject blocks** (compact, full, video) for Prompt Master / I2V / Extender.
4. Carry **clip-level `wardrobe_state`** (condition + delta) without rewriting the canonical look by default.
5. Attach optional **`wardrobe`** fields on identity-related handoffs when status is `locked`.
6. Wire short integration bullets into Identity Lock, Continuity Guardian, and AGENT_INDEX / AGENTS.md.
7. Update suite skill count marketing strings when the skill is catalogued (51 → 52).

## Non-goals

- Fashion design / lookbook-from-logline ideation mode
- Full multi-cast wardrobe arbitration (dual DNA)
- New CLI (`dna wardrobe …` or similar)
- Parallel `wardrobe.json` character files
- High-fidelity damage maps, zip/button state, per-layer continuity scores
- New required handoff packet type
- ErosForge intimacy choreography (may *consume* layer/condition only)
- Implementing P2–P5 agents in this epic

---

## Architecture & ownership

**Display name:** Costume & Wardrobe Continuity  
**Skill slug:** `costume-wardrobe-continuity`  
**Role Card:** `references/agents/Costume_Wardrobe_Continuity.md`  
**Activation:** `ACTIVATE COSTUME_WARDROBE` · `ACTIVATE WARDROBE_CONTINUITY` · `LOCK WARDROBE`

**Model Layer (v4.5):**

| Task type | Preferred model | Reasoning |
|-----------|-----------------|-----------|
| Lock / detailed outfit extraction / inject craft | `grok-v9-4p5-chat-expert` | high |
| Multi-shot wardrobe audit across a sequence | `grok-v9-4p5-multi` | high |
| Routine status / condition-only update | `grok-4-auto` | medium |

**Owns**

- `wardrobe_lock` block on Character DNA (canonical look)
- Wardrobe inject blocks
- Clip-level `wardrobe_state` updates after approved clips
- Short secondary wardrobe notes for multi-cast
- Handoff `wardrobe` fields for Identity Lock, Continuity, Prompt Master, Sequence Extender

**Does not own**

- Face/body Identity Lock or drift scoring
- Set / props (Production Designer)
- Creative costume invention mode
- Full multi-cast wardrobe DNA
- CLI commands
- NSFW undress direction (ErosForge)

### Pipeline placement

```text
DNA Extractor → Costume & Wardrobe Continuity → Identity Lock
                        │ wardrobe_lock + inject
                        ▼
              Prompt Master / I2V / Extender
                        │ wardrobe_state (delta)
                        ▼
              Continuity Guardian + Chain QA
```

---

## Data model

### Character DNA — `wardrobe_lock`

Nested on the existing DNA profile. Flat `clothing_style` remains and is rewritten from the active look when wardrobe is locked or permanently updated.

```json
"wardrobe_lock": {
  "schema_version": "1.0",
  "status": "pending",
  "active_look_id": "look_default",
  "looks": [
    {
      "look_id": "look_default",
      "label": "Hero trench night",
      "silhouette": "long overcoat over slim layers",
      "garments": [
        {
          "id": "coat",
          "name": "worn brown trench",
          "category": "outerwear",
          "colors": ["brown"],
          "materials": ["cotton twill"],
          "details": "water stains, frayed cuffs",
          "layer_index": 2
        }
      ],
      "accessories": [
        {
          "id": "ring",
          "name": "silver wedding ring",
          "hand": "left",
          "details": "twists when stressed"
        }
      ],
      "layer_order_bottom_to_top": ["shirt", "coat"],
      "condition_default": "worn",
      "inject_anchors": [
        "trench coat water stains",
        "frayed cuffs",
        "silver wedding ring left hand"
      ]
    }
  ],
  "secondary_notes": "",
  "locked_at": null,
  "source": "manual"
}
```

**Status enum:** `pending` | `locked` | `drift_review`  
**Condition enum (core):** `clean` | `worn` | `damaged` | `wet`  
**Source enum:** `manual` | `extracted` | `refined`

**Multi-look rule (P1):** Schema allows multiple `looks`; exactly one `active_look_id` is in force. Switching looks is an explicit agent action with a recorded reason.

**Conflict rule:** When `wardrobe_lock.status == locked`, structured lock wins over a divergent free-text `clothing_style`; the agent rewrites the summary string to match.

### Inject blocks

| Mode | Use |
|------|-----|
| `wardrobe_compact` | 1–2 sentences; tight token budgets |
| `wardrobe_full` | Garments + layers + accessories + condition |
| `wardrobe_video` | Full + fabric motion cues for 1.0 / 1.5 (no inventing unrelated motion DNA) |

**Token prefix:** `[WARDROBE_LOCK:<SLUG>:<LOOK_ID>] …`

When status is `locked`, Identity Lock and Imagine Prompt Master must include wardrobe inject on primary-character shots.

### Clip / sequence — `wardrobe_state`

Per-clip (or continuity payload) metadata; not a second bible:

```json
"wardrobe_state": {
  "character_slug": "marcus",
  "look_id": "look_default",
  "condition": "wet",
  "delta": "coat darker from rain; cuffs still frayed",
  "layer_order_bottom_to_top": ["shirt", "coat"],
  "updated_from_clip": "02"
}
```

**Delta rule:** Clip delta does **not** rewrite DNA `wardrobe_lock` unless the user confirms a **permanent** re-lock (e.g. coat destroyed).

Extender / Continuity consume: **canonical `wardrobe_lock` + last clip `wardrobe_state`**.

### Handoff extension

Optional object on identity-related handoffs (consumers ignore if absent). No new required `packet_type` in P1.

```json
"wardrobe": {
  "status": "locked",
  "active_look_id": "look_default",
  "inject": {
    "compact": "...",
    "full": "..."
  },
  "condition": "worn",
  "secondary_notes": "background detective: grey suit, no hero coat"
}
```

Handoff packet validator: optional schema acceptance for `wardrobe` on `identity_lock_handoff` is a **follow-up** if easy; not a P1 blocker.

---

## Workflows & protocols

### Activation triggers

- Explicit activation commands above
- After Character DNA Extractor when clothing is visible or `clothing_style` is non-empty
- Before first hero still / i2v / extend when Identity Lock is about to lock
- After Continuity or Chain QA flags clothing seam / outfit drift
- Studio Director routing when a signature outfit is production-critical

### Core protocols

| Protocol | Rule |
|----------|------|
| **WARDROBE_FROM_VISIBLE** | Prefer refs + approved stills; flag inventions as `inferred — confirm` |
| **ONE_ACTIVE_LOOK** | Exactly one `active_look_id` per character session |
| **PRIMARY_ONLY** | Full lock for primary; others → `secondary_notes` only |
| **STRUCTURED_CORE** | Garments, colors/materials, silhouette, accessories, layer order, condition, optional delta |
| **INJECT_READY** | Always emit compact + full when building a lock; add video mode when fabric/motion matters |
| **DELTA_NOT_REWRITE** | Clip state does not rewrite DNA without permanent re-lock confirmation |
| **HANDOFF_ATTACH** | Attach `wardrobe` when status is `locked` |
| **NO_FASHION_MODE** | No lookbook-from-logline track in P1 |
| **EROSFORGE_CONSUME** | Intimate work may read layer/condition; wardrobe agent does not author intimacy beats |

### Happy path

1. Draft `wardrobe_lock` from refs or existing `clothing_style` (`pending`).
2. Confirm → `locked`; refresh `clothing_style` summary; set `locked_at`.
3. Identity Lock loads DNA + wardrobe inject; Prompt Master includes `[WARDROBE_LOCK:…]`.
4. Generate stills / i2v / video with lock + last `wardrobe_state` if any.
5. After Go / Continuity pass, write clip `wardrobe_state` (condition + one-line delta).
6. Extend: canonical lock + last delta; do not drop accessories/layers silently.
7. Drift: `drift_review` → fix inject / re-gen guidance → re-lock only for permanent change.

### Agent graph

| Direction | Agents |
|-----------|--------|
| Upstream | Character DNA Extractor, Studio Director, user references |
| Peer | Identity Lock Specialist, Continuity Consistency Guardian, Imagine Prompt Master |
| Downstream consumers | Image-to-Video Specialist, Cinematic Sequence Extender, Chain QA |
| Opt-in consumer | ErosForge NSFW Director (layer/condition only) |

### Edge cases

| Case | Behavior |
|------|----------|
| No clothing visible | Omit block or leave `pending` with empty garments; do not invent |
| Mid-story look change | Explicit `active_look_id` switch + reason; new inject |
| Secondary steals frame | `secondary_notes` only |
| Permanent destruction | User confirm → update look or garments + re-lock |

---

## Implementation deliverables

1. **Role Card:** `references/agents/Costume_Wardrobe_Continuity.md` (Model Layer v4.5, protocols, outputs, handoffs)
2. **Skill:** `.grok/skills/costume-wardrobe-continuity/SKILL.md` (YAML frontmatter, activation, load Role Card)
3. **Index / agents docs:** `references/agents/AGENT_INDEX.md`, `AGENTS.md` slug table
4. **DNA contract:** Document `wardrobe_lock` on DNA template / Character DNA Extractor notes; optional example
5. **Integration bullets:** Identity Lock + Continuity Role Cards / skills (consume wardrobe; do not redefine)
6. **Handoff docs:** Optional `wardrobe` on identity handoff in relevant handoff reference
7. **Suite packaging:** Skill count 51 → 52 in README / plugin strings / meta-installer claims as needed; regenerate plugin catalog if the skill is shipped in the marketplace suite
8. **Python helpers:** Optional pure inject formatter under skill `scripts/` or extension of `tools/character_dna.py` — only if needed to prevent inject drift; **not required** for pure agent/docs ship

### Testing strategy

- Fixture DNA with valid `wardrobe_lock` (pending + locked)
- Inject builders (if code) produce non-empty compact/full when locked
- Handoff shape: `wardrobe` present when locked, absent when empty/pending
- Role Card self-check checklist (active look set, layers present, secondary not over-specified)
- No new CLI tests in P1

### Success criteria

- Primary outfit can be locked once and reused stills → i2v → extend without ad hoc re-description
- Handoffs can carry wardrobe status + inject + condition without a new packet type
- Secondary cast never receives a second full wardrobe bible
- `clothing_style` remains valid and synced when locked
- Operable in Grok Build via skill activation alone

---

## Roadmap context (out of scope for this epic)

| Phase | Agent |
|-------|--------|
| P1 (this design) | Costume & Wardrobe Continuity |
| P2 | Dialogue & Script Supervisor |
| P3 | Failure Recovery Coach |
| P4 | Music / Score Director |
| P5 | Platform Delivery Strategist |

---

## Open implementation choices (plan may pick)

1. Whether to extend `tools/character_dna.py` in P1 or keep wardrobe purely agent-documented until a later CLI epic  
2. Whether handoff-packet-validator gains optional `wardrobe` schema checks in the same PR or a follow-up  
3. Plugin pack membership (full suite only vs which satellite packs, if any)

These do not change the approved architecture.

---

*Grok Imagine Cinematic Studio — Costume & Wardrobe Continuity design · 2026-07-22*
