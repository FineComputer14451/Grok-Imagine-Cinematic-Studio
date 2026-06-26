---
description: Open the Grok Imagine Cinematic Studio CLI dashboard — studio health, quota, sequences, DNA, and production assets.
---

# Studio Dashboard

Show a unified overview of the local Cinematic Studio workspace: project state, model compatibility, quota, sequences, character DNA, and NSFW batches.

## Preflight

```bash
python tools/cinematic_studio_cli.py dashboard --help
```

## Plan

1. Run the dashboard command (default Rich layout).
2. If "$ARGUMENTS" contains `--json`, `--compact`, or `--watch`, pass those flags through.
3. Highlight any model compatibility issues or elevated quota risk.
4. Suggest the next concrete CLI action based on empty sections (no DNA → `/dna`, no sequences → `sequence init`).

## Commands

### Full dashboard

```bash
python tools/cinematic_studio_cli.py dashboard
```

### Compact summary

```bash
python tools/cinematic_studio_cli.py dashboard --compact
```

### JSON export

```bash
python tools/cinematic_studio_cli.py dashboard --json
```

### Live refresh (terminal)

```bash
python tools/cinematic_studio_cli.py dashboard --watch --interval 5
```

## Verification

- Header shows studio version and project title.
- Quota tier and session spend are displayed.
- Sequences and DNA tables appear when assets exist.
- Quick commands footer lists follow-up CLI paths.

## Summary

```
## Result
- **Action**: Studio dashboard rendered
- **Status**: success
- **CLI**: cinematic-studio dashboard
```

## Next Steps

- Run `/quota` for a detailed cost estimate before generation.
- Run `/cinematic` to start a production session.
- Run `validate` if model compatibility shows issues.