# Release Notes — v3.8.1

**Date:** 2026-07-11  
**Theme:** Identity continuity deepen — protocol wiring, opt-in CLI gates, hybrid drift evidence

## Highlights

1. **Identity Continuity Protocol v1.0** — mandatory agent steps (ICP-01…07), `drift_evidence` handoff section, warn-only handoff validator.
2. **`--strict-identity`** — opt-in hard-fail on `sequence handoff` and `sequence extend-prompt` when evidence is missing or identity risk.
3. **Drift evidence quality** — multi-signal soft-PIL still compare, path resolve via flags/clip fields, modest facial DNA weighting; `sequence drift-score --ref-still` / `--clip-still`.

## Install / update

```bash
# Plugin (Method B)
grok plugin update grok-imagine-cinematic-studio
# or reinstall
grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio --trust

# Meta installer (Method A)
bash scripts/cinematic_studio.sh update
```

## Verify

```bash
python tools/cinematic_studio_cli.py models verify
bash scripts/verify_plugins.sh --release
python tools/cinematic_studio_cli.py validate
```

## Activation

`Activate Grok Imagine Cinematic Studio v3.8.1`

## Related design docs

- `docs/development/superpowers/specs/2026-07-11-identity-continuity-agent-wiring-design.md`
- `docs/development/superpowers/specs/2026-07-11-identity-strict-cli-gates-design.md`
- `docs/development/superpowers/specs/2026-07-11-identity-drift-evidence-quality-design.md`
