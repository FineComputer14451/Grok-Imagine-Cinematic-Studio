---
description: Run full Cinematic Studio validation — skills, agents, models, DNA, sequences, and project state health checks.
---

# Validate Studio

Run the canonical validation suite before delivery, extension final stitch, or plugin publish.

## Preflight

1. **Working directory** — Run from the Cinematic Studio repo root (contains `tools/cinematic_studio_cli.py`).
2. **Dependencies** — `pip install -r requirements.txt` if imports fail.
3. **Scope** — If "$ARGUMENTS" contains `plugin`, also validate the Grok plugin manifest and index freshness.

## Plan

1. Run CLI `validate` (skills, agents, models, paths).
2. Verify model compatibility stack.
3. If plugin scope: run `grok plugin validate` and check `plugin-index.json` is current.
4. Report any blockers vs warnings with fix instructions.

## Commands

### Core validation

```bash
python tools/cinematic_studio_cli.py validate
```

### Model stack verify

```bash
python tools/cinematic_studio_cli.py models verify
python tools/cinematic_studio_cli.py models list
```

### Plugin validation (when "$ARGUMENTS" includes plugin)

```bash
grok plugin validate
python scripts/generate_plugin_index.py --check
bash scripts/cinematic_studio.sh verify --plugin
```

Regenerate stale index:

```bash
python scripts/generate_plugin_index.py
```

Before release (pin marketplace catalog to current commit):

```bash
python scripts/generate_plugin_index.py --sync-sha
# commit marketplace.json + plugin-index.json in the same commit
```

### Optional: generate PDF report

```bash
python tools/cinematic_studio_cli.py report --output artifacts/production_report.pdf
```

## Verification

- `validate` exits 0 with no blocking issues.
- `models verify` reports `compatible: true`.
- Plugin check (if run): manifest valid, `plugin-index.json` up to date.

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