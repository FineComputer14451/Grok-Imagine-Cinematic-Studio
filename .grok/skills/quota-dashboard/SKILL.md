---
name: quota-dashboard
description: Mobile-optimized Quota Dashboard for Grok Imagine with full Weekly SuperGrok Heavy Limit support. Tracks session usage + weekly quota from app screenshots (%, reset date/time, Imagine/Chat/Build breakdown). Delivers beautiful at-a-glance visual reports + cinematic key-art style visual dashboard posters. Optimized for grok-4-auto, grok-4.6, grok-4.6 and both Grok Imagine Video 1.0 + 1.5. Complements workflow-quota-optimizer and nsfw-quota-orchestrator. Activate with SHOW QUOTA DASHBOARD, SHOW VISUAL DASHBOARD, or ACTIVATE QUOTA_DASHBOARD.
---

# Quota Dashboard v4.5 (Grok 4.6 + Grok Imagine Video 1.0 & 1.5)

**Role Card:** `references/agents/Quota_Dashboard.md` (v4.5) — Authoritative source for quota tracking, visual reporting, dual-model (1.0/1.5) awareness, and cinematic dashboard poster generation.

> Mobile-optimized Quota Dashboard for Grok Imagine with full Weekly SuperGrok Heavy Limit support.

## Model Layer (Grok 4.6)

| Task type                                      | Preferred model               | Reasoning |
|------------------------------------------------|-------------------------------|-----------|
| Complex multi-window quota synthesis and visual dashboard design | `grok-4.6` (Chat **Heavy**)         | high      |
| Single screenshot analysis, status report, key-art style poster | `grok-4.6` (Chat **Expert**)   | high      |
| Quick status / simple checks                   | `grok-4.6` | medium |

**Stack default:** cinematic+Build API/chat **`grok-4.6`** (CLI ≥ 1.0.5 · fork `grok-build` or `grok-4.6`; `grok-4.5` aliases wrap 4.6). Opt-in 1M: `grok-4.3`.  
**Registry:** `tools/models.py` (schema 1.1+) · `references/agents/MODEL_LAYER_v4.5.md` · `models verify`

**Legacy (still selectable):** `grok-4.5` (legacy alias that wraps `grok-4.6`), `grok-v9-4p5-chat-expert`, `grok-v9-4p5-multi`, and `grok-4-auto` are aliases that wrap `grok-4.6`. `grok-imagine-image` (Fast) stays selectable. Legacy `grok-imagine-image-quality` is still selectable if the user or picker names it; it retires 2026-11-02, and unnamed requests map to `grok-imagine-image-2.0` with `quality=low`. Video 1.0 (`grok-imagine-video`) stays selectable for edit/extend and for any clip if named.

**Named-id rule:** If the user or picker names a legacy id, use that id. Do not silently replace a named legacy choice.

```yaml
model_compatibility:
  - grok-4.6
  - grok-4.5  # legacy alias that wraps grok-4.6
  - grok-v9-4p5-chat-expert
  - grok-v9-4p5-multi
  - grok-4-auto
  - grok-4.3
preferred_model: grok-4.6
```


## When to Activate

- User provides app screenshots of quota status
- User says `SHOW QUOTA DASHBOARD`, `SHOW VISUAL DASHBOARD`, or `ACTIVATE QUOTA_DASHBOARD`
- Need for at-a-glance or cinematic visual quota reports

## Activation

`ACTIVATE QUOTA_DASHBOARD` / `SHOW QUOTA DASHBOARD` / `SHOW VISUAL DASHBOARD`

Load and follow the Role Card.

## Grok Imagine Video Compatibility

### Audio / final — Imagine Video 1.5 Native
- Track and report 1.5 usage distinctly when data is available

### Edit / extend — Imagine Video 1.0 (still selectable if named; not fallback-only. No Video 2.0.)
- Track and report 1.0 usage distinctly when data is available

Both paths share the same dashboard and visual reporting framework.

## Core Protocols (v4.5)

| Protocol                        | Requirement |
|--------------------------------|-------------|
| **SCREENSHOT_ANALYSIS**        | Extract % remaining, reset date/time, Imagine/Chat/Build breakdown |
| **WEEKLY_HEAVY_LIMIT**         | Full support for Weekly SuperGrok Heavy Limit tracking |
| **VISUAL_DASHBOARD**           | Deliver beautiful at-a-glance visual reports |
| **KEY_ART_POSTER**             | Optional cinematic key-art style visual dashboard posters |
| **MODEL_LAYER_ROUTING**        | Explicit model selection recorded in every report |
| **1.0_1.5_DUAL_SUPPORT**       | Distinguish 1.0 vs 1.5 usage when data allows |
| **HANDOFF_PACKET**             | Dashboard data must be attachable to plans |

## Integration Rules

- Complements Workflow Quota Optimizer and NSFW Quota Orchestrator
- Feeds Studio Director and Sequence Director with current quota reality

## Grok Build Compatibility

Fully compatible with Grok Build CLI, Termux/Android, and Kali NetHunter. All reports use structured formats.

**Load the Role Card** for complete dashboard philosophy, dual-model standards, and v4.5 Role Card updates.

---

*Enhanced for Grok 4.6 + dual Imagine Video 1.0 & 1.5 Native support — Cinematic Studio v4.5*
