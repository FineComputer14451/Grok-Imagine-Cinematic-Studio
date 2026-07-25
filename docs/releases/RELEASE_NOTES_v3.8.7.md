# Release Notes — Grok Imagine Cinematic Studio v3.8.7

**Date:** 2026-07-25  
**Stack:** Grok 4.5 cinematic + Build · Model Layer v4.5 (v9-4p5 / `grok-4-auto`) · optional Grok 4.3 1M · dual Imagine Video 1.0 / 1.5  
**Activation:** `Activate Grok Imagine Cinematic Studio v3.8.7`

## Highlights

| Area | Change |
|------|--------|
| **Suite** | **62 skills** (was 52 at 3.8.6 start); packs updated for Wave A |
| **Role Cards** | **25 core** + Wave A specialists · Grok Doctor + Multi-Clip Continuity |
| **Wave A** | 8 specialists P0→P2 (packets + CLI + `--strict-wave-a` spend gates) |
| **Parallel Briefs** | Protocol v1.0 on Director + specialists |
| **Grok Build binary** | Method A ensure + `cinematic-studio grok status\|ensure\|update\|install` |
| **Doctor** | Prefer full git clone; catalog pin + quota recon health |

## Added

- **Grok Doctor** (`grok-doctor`) — multi-agent Studio Health Diagnostician
- **Multi-Clip Continuity Orchestrator** — LAST_FRAME_RECAP / AMV chain commander
- **Parallel Brief Protocol v1.0** — concurrent specialist briefs under MAXIMUM AGENTIC MODE
- **Wave A specialists (8):** plate-motion readiness, contact micro-physics, hair/makeup continuity, dialogue/ADR, score/temp music, title/mograph, distribution crops, parallel-brief dispatcher
- **Wave A packets + CLI** — `tools/wave_a_packets.py`, `cinematic-studio wave-a …`, `--strict-wave-a` on sfw/nsfw/imagine
- **Grok Build CLI management** — `cinematic-studio grok status|ensure|update|install` (≥ **0.2.93**)
- **Method A Grok Build ensure** on install (`CINEMATIC_SKIP_GROK_CLI` / `FORCE` / `MIN`)

## Compatibility

- Grok Build CLI ≥ **0.2.93** (current stable often 0.2.112+)
- Handoff `protocol_version` accepts **3.7.1–3.8.7**
- Registry default chat/build: **`grok-4.5`**; fork secondary: **`grok-build`**

## Upgrade

```bash
# Plugin (Method B)
grok plugin update grok-imagine-cinematic-studio
# or reinstall from clone / release zip
grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio --trust

# Meta installer (Method A) — also ensures grok binary
bash scripts/cinematic_studio.sh update
bash scripts/cinematic_studio.sh verify --all   # or --plugin

# Grok Build binary only
cinematic-studio grok ensure

# Health
cinematic-studio doctor --quick
# or: grok-doctor --quick
```

Activation: **`Activate Grok Imagine Cinematic Studio v3.8.7`**

## Assets

- `grok-imagine-cinematic-studio-skills-install-v3.8.7.zip` — full **62** skills + tools/refs
- `grok-imagine-cinematic-studio-meta-installer-v3.8.7.zip` — bootstrap + installer scripts

## Notes

- v3.8.6 remains the dual-model polish baseline; **3.8.7** is suite expansion + Parallel Briefs + Wave A + Grok Build binary UX.
- Catalog pin workflow: commit content → `plugin catalog pin` → commit only `.grok-plugin/`.
