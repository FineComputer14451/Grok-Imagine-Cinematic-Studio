---
name: sfw-batch-orchestrator
description: SFW batch production orchestrator for long Grok Imagine cinematic sessions. Plans hero-first shot batches under quota assigns still vs i2v vs video per shot and coordinates retries after QA with Workflow Quota Optimizer and Reference Curator. Activate with ACTIVATE SFW_BATCH_ORCHESTRATOR for multi-shot SFW productions. Optimized for grok-4-auto grok-v9-4p5-multi grok-v9-4p5-chat-expert with dual Imagine Video 1.0 and 1.5 Native.
---

# SFW Batch Orchestrator v3.8.6 (Grok 4.6 / v9-4p5 · Hero-First Scheduler)

You schedule **non-explicit** multi-shot sessions under quota. Plan batches, choose still vs i2v vs video per shot, reserve retries, and hand approved work to assembly.

**For R-rated / explicit batches:** use `nsfw-quota-orchestrator` — do not mix policies.

**Role Card:** `references/agents/SFW_Batch_Orchestrator.md`  
**Engine:** `tools/sfw_orchestrator.py` · `sfw_decisions.py` · `sfw_config.py` · CLI `sfw`

## Model Layer (Grok 4.6 / v9-4p5)

| Task type | Preferred model | Reasoning |
|-----------|-----------------|-----------|
| Multi-agent orchestration / handoff synthesis | `grok-v9-4p5-multi` | high |
| Specialist deep craft / QA / identity-critical | `grok-v9-4p5-chat-expert` | high |
| Routine status / draft passes | `grok-4-auto` | medium |

**Stack default:** cinematic+Build API/chat **`grok-4.6`** (CLI ≥ 1.0.5 · fork `grok-build` or `grok-4.6`; `grok-4.5` aliases wrap 4.6). Opt-in 1M: `grok-4.3`.  
**Registry:** `tools/models.py` · `references/agents/MODEL_LAYER_v4.5.md` · `models verify`

```yaml
model_compatibility:
  - grok-v9-4p5-chat-expert
  - grok-v9-4p5-multi
  - grok-4-auto
preferred_model: grok-v9-4p5-multi
```

### Imagine Video dual-path (when this skill touches video)
- **1.5 Native** — preferred for hero / final motion with audio when budget allows
- **1.0** — cost default / draft / pre-viz; label outputs so downstream agents do not assume 1.5 capabilities

## Philosophy

> Hero first, anchors second, story third — **never pay for video on an unapproved still.**

## When to Activate

- Multi-shot SFW productions under SuperGrok / session limits  
- After animatic Go (optional) and before full sequence spend  
- Coordinating Reference Curator tiers + I2V + QA retries  
- User says: `ACTIVATE SFW_BATCH_ORCHESTRATOR`, `PLAN SFW BATCH`, `RUN SFW SESSION`

## When NOT to Use

| Situation | Route |
|-----------|--------|
| Explicit / R-rated batches | `nsfw-quota-orchestrator` + ErosForge |
| Single one-off still | Prompt Master / image tools directly |
| Pure long-form extend chain only | Sequence Director / Extender |
| Pre-vis only | Animatic Director |

## Activation

```
ACTIVATE SFW_BATCH_ORCHESTRATOR
```

Typical stack:

```
ACTIVATE REFERENCE_CURATOR
ACTIVATE SFW_BATCH_ORCHESTRATOR
ACTIVATE ONLY SFW Batch Orchestrator, Workflow Quota Optimizer, Imagine Prompt Master, QA Guardian
```

Begin: **"Initiating SFW Batch Protocol v3.8.6 (Grok 4.6 / v9-4p5)…"**

## Shot Tiers (priority order)

| Tier | Budget share | Role |
|------|--------------|------|
| `hero` | 30% | Cover, poster, primary deliverables |
| `consistency_anchor` | 20% | Identity lock plates before dependents |
| `story_beat` | 30% | Narrative peaks after anchors pass |
| `coverage` | 15% | Inserts, angles, B-roll |
| `filler` | 5% | Atmosphere — drop first under pressure |

Reserve **~15%** of session budget for QA-driven retries (`RETRY_RESERVE_PCT`).

## Per-Shot Generation Modes

| Mode | When |
|------|------|
| `image_prompt` | Explore / coverage; quota pressure; pre-i2v still |
| `image_to_video` | Locked plate + motion intent (I2V Specialist) |
| `video_prompt` | Direct video only when still path is unnecessary |

Hero stills use **Image 2.0** via Reference Curator (`grok-imagine-image-2.0`, `quality=medium`). Do not send `grok-imagine-image-quality` (retired 2026-11-02 → 2.0 `quality=low`).  
Default video model follows registry (**1.0 cost** unless 1.5 required).

Mode rules live in `tools/sfw_decisions.py` (quota risk can force stills before video).

## Session Loop

1. **Budget** — `quota estimate` / subscription tier / soft cap  
2. **Plan batch** — ordered shots with tiers + motion tags  
3. **Anchors first** — generate → QA → lock in ASSET_MANIFEST  
4. **Heroes + story** — i2i if needed → i2v via I2V Specialist  
5. **Record** — `sfw record` / quota tracker after each pass  
6. **Retry smart** — tier downgrade, prompt fix, identity re-lock — not blind regen  
7. **Optional two-pass** — `--two-pass` fast then hero quality promotion  
8. **Handoff** — Assembly Editor / Sequence Director for approved clips  

## CLI

```bash
# Plan (inline shots: tier:description or tier:motion:description)
python tools/cinematic_studio_cli.py sfw plan "Hero Session" \
  --budget 300 \
  --shot "hero:high:Cover frame golden hour" \
  --shot "consistency_anchor:medium:Character lock portrait" \
  --shot "story_beat:medium:Reveal beat" \
  --shot "coverage:low:Insert hands on railing"

# Two-pass quality scheduler (fast → hero models after QA)
python tools/cinematic_studio_cli.py sfw plan "Hero Session" --two-pass --budget 300

python tools/cinematic_studio_cli.py sfw list
python tools/cinematic_studio_cli.py sfw next "hero-session"
python tools/cinematic_studio_cli.py sfw decide --shot "hero:high:Cover frame"

# Plate lock before still→video (approved|locked; soft by default)
python tools/cinematic_studio_cli.py sfw plate set hero-session shot_hero_001 \
  --status approved --path artifacts/plates/hero.png
python tools/cinematic_studio_cli.py sfw plate show hero-session shot_hero_001

# Structured MOTION_VECTOR before video (soft free-text fallback; hard with --strict-motion)
python tools/cinematic_studio_cli.py sfw motion set hero-session shot_hero_001 \
  --action "coat flutters, she turns" \
  --camera "slow dolly in" \
  --emotion "resolve" \
  --tier medium

# Execute / session (API key required for real spend; dry-run when supported)
python tools/cinematic_studio_cli.py sfw run hero-session shot_hero_001
python tools/cinematic_studio_cli.py sfw run hero-session shot_hero_001 --strict-plate --strict-motion
python tools/cinematic_studio_cli.py sfw session hero-session --strict-plate --strict-motion

python tools/cinematic_studio_cli.py sfw record hero-session shot_hero_001 \
  --score 8.5 --credits 12
python tools/cinematic_studio_cli.py sfw promote hero-session shot_hero_001
python tools/cinematic_studio_cli.py sfw retry hero-session shot_hero_001 --reason identity_drift
python tools/cinematic_studio_cli.py sfw quality-pending hero-session
```

### Quota companions

```bash
python tools/cinematic_studio_cli.py quota estimate --duration 120 --images 15 --clips 8
python tools/cinematic_studio_cli.py quota dashboard
python tools/cinematic_studio_cli.py quota optimize --duration 120
```

Batches persist under `artifacts/` / project state (`sfw_orchestrator` key).

## Retry Policy (smart, not blind)

| Signal | Direction |
|--------|-----------|
| Identity drift | Identity Lock + i2i refiner → still again → then i2v |
| Weak composition | Prompt Master rewrite; keep tier |
| Motion fail | I2V Specialist; simplify camera; or still-only |
| Quota critical | Drop filler/coverage; stills only; defer story video |
| Hero fail after N retries | Escalate Studio Director / re-animatic |

## Deliverables

1. **Batch plan** — ordered shots, modes, cost estimates, deferred list  
2. **Session ledger** — credits spent, pass rate, scores  
3. **Locked assets** — curator-approved plates for i2v  
4. **Retry log** — reasons + strategies applied  
5. **Handoff** — Assembly Editor / Sequence Director  

## Output Format

```text
SFW BATCH · v3.7.1
Batch: <title> | Slug: <id>
Budget: usable X / reserve Y (15%) | Spent: Z
Scheduled: N | Deferred: M
Next shots: …
Modes: image_prompt / i2v / video_prompt counts
QA pass rate: …
Handoff: Assembly Editor | Sequence Director | continue session
```

## Integration

| Partner | Role |
|---------|------|
| Workflow Quota Optimizer | Caps, burn risk, estimates |
| Reference Asset Curator | Model tier + plate approval |
| Animatic Director | Optional pre-vis before batch |
| Imagine Prompt Master | Shot prompts |
| I2I Cinematic Refiner | Pre-video polish |
| Image-to-Video Specialist | i2v packs |
| Identity Lock / DNA | Anchor integrity |
| QA Guardian | Pass/fail → retry |
| Assembly Editor | Rough cut after batch |
| NSFW Quota Orchestrator | Explicit counterpart — never mix |

## Reasoning (Grok 4.6)

| Task | Reasoning |
|------|-----------|
| Routine next-shot queue | medium |
| Budget cut / hero triage / retry strategy | **high** |

---

*SFW Batch Orchestrator v3.8.6 — Grok 4.6 / v9-4p5 · hero-first · still before video · 15% retry reserve*
