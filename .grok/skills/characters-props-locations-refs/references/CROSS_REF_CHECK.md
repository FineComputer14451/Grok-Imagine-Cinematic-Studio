# Post-board cross-ref consistency check

Run **after** the board pass (locations → characters → props → board), **before** sequence stills / video / Identity Lock.

## Why

Catches slug mismatches, missing hero plates, empty DNA anchors, and manifest drift while onboarding is cheap.

## Command

From the project root (folders `characters/` · `props/` · `locations/`):

```bash
python .grok/skills/characters-props-locations-refs/scripts/cross_ref_check.py .
# or against the demo pack:
python scripts/cross_ref_check.py samples/onboarding-demo
```

Flags:

- `--json` — machine report
- `--strict` — warnings become failures

Exit `0` = pass (warnings ok). Exit `1` = failures.

## What it checks

| Check | Fail | Warn |
|-------|------|------|
| `characters/*/dna.json` present | ✓ | |
| DNA `slug` matches folder name | ✓ | |
| `core_identity` / `facial_dna` / name filled | ✓ | |
| ≥1 `key_consistency_anchors` | ✓ | <3 anchors |
| Each `reference_image_ids` plate exists on board | ✓ | |
| `board/manifest.json` heroes/establish present | ✓ | missing manifest |
| Prop / location hero|establish plates | | ✓ |
| `sample: true` still set | | ✓ |

## Activation

```text
ACTIVATE CHARACTERS_PROPS_LOCATIONS_REFS board
ACTIVATE CHARACTERS_PROPS_LOCATIONS_REFS check
```

After generate pipeline step **Board**, always run this check before motion.

## Sample pack

`samples/onboarding-demo/` — Mara Chen + Kai Reed DNA, prop/location stubs, `board/manifest.json`.

```bash
python scripts/cross_ref_check.py samples/onboarding-demo
```

## Next

1. Fix failures (regen plates or fix DNA ids).
2. `ACTIVATE IDENTITY_LOCK` / Studio `dna lock`.
3. Sequence stills → video only if asked.
