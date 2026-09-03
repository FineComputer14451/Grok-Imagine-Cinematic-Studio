# Batch Priority Tiers — NSFW Quota Orchestrator

Shot tiers ordered by production impact and quota efficiency on SuperGrok Heavy.

---

## Tier Order (Always Generate In This Sequence)

| Priority | Tier | Budget Share | Min QA | Purpose |
|----------|------|--------------|--------|---------|
| 1 | `hero` | 25% | 8.0 | Cover frames, primary deliverables, marketing stills |
| 2 | `consistency_anchor` | 15% | 8.0 | Identity lock references before any dependent video |
| 3 | `key_explicit` | 35% | 7.0 | Narrative-critical intimate beats |
| 4 | `support` | 15% | 7.0 | Transitions, establishing, emotional B-roll |
| 5 | `filler` | 10% | 7.0 | Atmosphere — skip when daily cap >50% used |

---

## Budget Allocation Rules

1. Reserve **15%** of batch budget for retries (never schedule 100%)
2. Schedule heroes + anchors before key_explicit when budget is tight
3. Defer filler entirely when `assess_budget_risk` returns `high` or `critical`
4. Default Heavy session budget: **40% of daily soft cap** (~1,000 credits)

---

## Per-Tier Generation Guidance

### Hero
- Use `grok-imagine-image-2.0` with `quality=medium` for stills (1K $0.05)
- Promote to `image_to_video` only after anchor QA ≥8
- One hero per session minimum before support shots

### Consistency Anchor
- Always `image_prompt` first — never video without locked still
- Inject Character DNA block from `dna inject`
- Store `reference_image_id` for all downstream shots

### Key Explicit
- Prefer `image_to_video` from locked anchor
- 8–12s clips, one primary motion beat
- Activate ErosForge physics + post_scene_state tracking

### Support / Filler
- `image_prompt` unless budget surplus confirmed
- Skip if session pass rate <60%

---

## Model Routing (Reference Curator)

Applied automatically by `apply_reference_curator_models()` in `tools/nsfw_orchestrator.py`:

| Shot Tier | Asset Tier | Image | Video |
|-----------|------------|-------|-------|
| `hero`, `key_intimate` (`key_explicit` alias), `consistency_anchor` | hero | `grok-imagine-image-2.0` (`quality=medium`) | `grok-imagine-video` |
| `support` | standard | `grok-imagine-image` | `grok-imagine-video` |
| `filler` | draft | `grok-imagine-image` | `grok-imagine-video` |