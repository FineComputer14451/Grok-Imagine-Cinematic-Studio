# Release Notes — v3.11.0

**Date:** 2026-08-23  
**Codename:** Grok 4.6 stack lock

## Highlights

Grok Imagine Cinematic Studio **v3.11.0** makes **Grok 4.6** and **Grok Build CLI ≥ 1.0.5** first-class. `grok-4.5` remains an alias of 4.6, so older Bibles and handoff packets still normalize.

| Layer | Pin |
|-------|-----|
| Cinematic / Build / CLI agent | `grok-4.6` |
| Aliases | `grok-4.5`, `cinematic`, `build`, `coding` → 4.6 |
| Fork | `grok-build` or `grok-4.6` |
| Grok Build binary min | **1.0.5** |
| Specialists | v9-4p5 / `grok-4-auto` wrap 4.6 |
| 1M opt-in | `grok-4.3` |
| Imagine | Image 2.0 + Video 1.0 / 1.5 (no Video 2.0) |

Registry: `tools/models.py` · `references/agents/MODEL_LAYER_v4.5.md` · `cinematic-studio models verify`

## Doctor / host config

- `models.default = grok-4.6` **PASS** (aliases including `grok-4.5` also PASS)
- `fork_secondary_model` **PASS** for `grok-build` or `grok-4.6`
- CLI probe: installed **1.0.5 ≥ 1.0.5**

## Operator surfaces

CLI, TUI, Streamlit, NiceGUI, React, FastAPI, orchestrator skill, meta-installer, and activation phrase lock **v3.11.0** / Grok 4.6.

```text
Activate Grok Imagine Cinematic Studio v3.11.0
```

## Skills & Role Cards

Live SKILL.md stack defaults, Model Layer headings, H1 titles, YAML descriptions, and initiation phrases use **Grok 4.6**. Specialist v9-4p5 routing is unchanged. Archive `MODEL_LAYER_v3.7.1.md` is historical.

## Compatibility

- `VERSION` / `STUDIO_COMPATIBILITY_VERSION`: **3.11.0**
- Handoff `PROTOCOL_OK` includes **3.11.0** (prior 3.7.1–3.10.0 packets still accepted)
- Activation: **`Activate Grok Imagine Cinematic Studio v3.11.0`**
- Plugin marketplace catalog regenerated for 3.11.0 (64 skills + 11 commands)
