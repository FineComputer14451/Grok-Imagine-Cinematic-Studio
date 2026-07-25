# Release Notes — Grok Imagine Cinematic Studio v3.8.7

**Date:** 2026-07-25  
**Stack:** Grok 4.5 cinematic + Build · Model Layer v4.5 (v9-4p5 / `grok-4-auto`) · optional Grok 4.3 1M · dual Imagine Video 1.0 / 1.5  
**Activation:** `Activate Grok Imagine Cinematic Studio v3.8.7`

## Highlights

| Area | Change |
|------|--------|
| **Suite** | **54 skills** (was 52); packs: core **20**, sequence-narrative **16** |
| **Role Cards** | **25 core agents** (was 23) — Grok Doctor + Multi-Clip Continuity Orchestrator |
| **Parallel Briefs** | Protocol v1.0 wired into Studio Director + 12 specialist Role Cards |
| **Install** | Method A ensures Grok Build CLI ≥ **0.2.93** (`grok update` / official installer) |
| **Doctor** | Prefer full git clone when present; health checks for catalog pin + quota recon |

## Added

- **Grok Doctor** skill / Role Card (`grok-doctor`) — multi-agent Studio Health Diagnostician
- **Multi-Clip Continuity Orchestrator** (`multi-clip-continuity-orchestrator`) — LAST_FRAME_RECAP / momentum / AMV chain commander
- **Parallel Brief Protocol v1.0** — concurrent specialist briefs under MAXIMUM AGENTIC MODE; Foley + NSFW densification patterns; coverage table on specialist cards
- **Method A Grok Build CLI ensure** — `CINEMATIC_SKIP_GROK_CLI` / `CINEMATIC_FORCE_GROK_CLI` / `CINEMATIC_MIN_GROK_CLI`

## Changed

- Marketplace catalog pin + plugin-index for 54-skill full suite
- AGENTS.md / guides / taxonomy aligned to 54 skills · 25 core Role Cards
- `grok-doctor` launcher prefers `~/Grok-Imagine-Cinematic-Studio` when it is a full git checkout

## Compatibility

- Grok Build CLI ≥ **0.2.93** (recommended current stable)
- Handoff `protocol_version` accepts **3.7.1–3.8.7**
- Registry default chat/build: **`grok-4.5`**; fork secondary: **`grok-build`**

## Upgrade

```bash
# Plugin (Method B)
grok plugin update grok-imagine-cinematic-studio
# or reinstall from clone
grok plugin install /path/to/Grok-Imagine-Cinematic-Studio --trust

# Meta installer (Method A)
bash scripts/cinematic_studio.sh update
bash scripts/cinematic_studio.sh verify --plugin   # or verify --all for Method A skills

# Health
CINEMATIC_REPO_ROOT=/path/to/clone grok-doctor --quick
```

Activation phrase after upgrade: **`Activate Grok Imagine Cinematic Studio v3.8.7`**

## Notes

- v3.8.6 remains the dual-model polish baseline; **3.8.7** packages suite expansion (doctor + multi-clip continuity), Parallel Brief wiring, and install/doctor hardening.
- Catalog pin workflow unchanged: commit content → `plugin catalog pin` → commit only `.grok-plugin/`.
