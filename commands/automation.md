---
description: Operations and automation — batch sessions, NSFW execute parity, artifact pipeline, unified production reports.
---

# Operations & Automation (`/automation`)

Tier 5 tooling for hands-free batch sessions, artifact registration, and unified production visibility.

## Preflight

```bash
python tools/cinematic_studio_cli.py imagine verify
python tools/cinematic_studio_cli.py sfw plan "Session" --shot "hero:Cover" --budget 300
```

## Single shot execute

```bash
# SFW
python tools/cinematic_studio_cli.py sfw run hero-session shot_hero_001 --dry-run

# NSFW (opt-in, Heavy tier)
python tools/cinematic_studio_cli.py nsfw run intimate-session shot_hero_001 --dry-run
```

## Automated session (next N shots)

```bash
python tools/cinematic_studio_cli.py sfw session hero-session --count 3 --dry-run
python tools/cinematic_studio_cli.py nsfw session intimate-session --count 2 --dry-run
```

Use `--continue-on-fail` to keep running after a shot failure.

## Artifact pipeline

```bash
python tools/cinematic_studio_cli.py imagine artifact job_20260626_120000_123456
python tools/cinematic_studio_cli.py imagine artifacts --limit 20
```

Manifests are written under `artifacts/generations/` with job metadata.

## Unified production report

```bash
python tools/cinematic_studio_cli.py imagine report
python tools/cinematic_studio_cli.py imagine report --output artifacts/production_report.md
python tools/cinematic_studio_cli.py dashboard --compact
```

Dashboard now includes pending shot counts and artifact totals.

## Web UI

- **Imagine → Batch execute** — SFW generate + QA record
- **NSFW → Execute** — NSFW generate + session runner

## Verification

- `sfw session` / `nsfw session` return executed count and per-shot status
- `imagine artifact` writes `.manifest.json` beside artifact path
- `imagine report` merges quota, batches, jobs, and artifacts

## Summary

```
## Result
- **Action**: Automation session
- **Pipeline**: sfw | nsfw
- **Executed**: <n>
- **Artifacts**: <registered>
```