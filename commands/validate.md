---
description: Run full Cinematic Studio validation — skills, agents, models, DNA, sequences, and project state health checks.
---

# Validate Studio

Run the canonical validation suite before delivery, extension final stitch, or plugin publish.

## Preflight

1. **Working directory** — Run from the Cinematic Studio repo root (contains `tools/cinematic_studio_cli.py`).
2. **Dependencies** — `pip install -r requirements.txt` if imports fail; `pip install -r requirements-dev.txt` before running tests.
3. **Scope** — If "$ARGUMENTS" contains `plugin`, also validate the Grok plugin manifest and index freshness.

## Plan

1. Run CLI `validate` (skills, agents, models, paths).
2. Verify model compatibility stack.
3. If plugin scope: run `scripts/verify_plugins.sh` (manifest, catalog, optional installed checkout).
4. Report any blockers vs warnings with fix instructions.

## Commands

### Core validation

```bash
python tools/cinematic_studio_cli.py validate
```

### Test suite

```bash
pip install -r requirements-dev.txt
pytest
```

### Model stack verify

```bash
python tools/cinematic_studio_cli.py models verify
python tools/cinematic_studio_cli.py models list
```

### Plugin validation (when "$ARGUMENTS" includes plugin)

```bash
bash scripts/verify_plugins.sh
```

Regenerate stale index:

```bash
python scripts/generate_plugin_index.py
```

Before release (atomic catalog pin — run once, commit everything together):

```bash
bash scripts/release_plugin_catalog.sh
git add .grok-plugin/marketplace.json .grok-plugin/plugin-index.json .grok-plugin/plugin.json
# commit feature changes + catalog files in the SAME commit
```

Pre-publish gate (run on the feature commit before catalog pin is committed):

```bash
bash scripts/verify_plugins.sh --release
```

After the catalog pin commit, the marketplace sha intentionally points at the feature commit — use `bash scripts/verify_plugins.sh` (without `--release`) on repo tip.

Do **not** split marketplace sha bumps into a follow-up chore commit that only fixes a stale pin from an earlier release. The pin commit should immediately follow the feature commit and point at it.

### Optional: generate PDF report

```bash
python tools/cinematic_studio_cli.py report --output artifacts/production_report.pdf
```

## Verification

- `validate` exits 0 with no blocking issues.
- `models verify` reports `compatible: true`.
- `pytest` exits 0 (when dev deps installed).
- Plugin check (if run): `verify_plugins.sh` exits 0 (manifest, `plugin.json`, `plugin-index.json`; installed checkout when present).

Re-run failed checks after fixes and confirm exit code 0.

## Summary

```
## Result
- **Action**: Studio validation
- **Status**: passed | warnings | failed
- **CLI validate**: <exit code>
- **Models**: compatible | issues found
- **Plugin**: valid | stale index | skipped
- **Issues**: <count>
```

## Next Steps

- Fix any reported path or skill issues, then re-run `/validate`.
- Run `/quota` before large generation sessions.
- Activate `quality-assurance-guardian` for 16-point weighted review before client delivery.