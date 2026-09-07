# Sample DNA packets

Ready-to-copy Character DNA (schema 1.0) for new-project onboarding.

| Packet | Slug | Use |
|--------|------|-----|
| Mara Chen | `mara-chen` | Lead / courier — full anchors + hero plate ids |
| Kai Reed | `kai-reed` | Supporting / mechanic — scar + wardrobe anchors |

## Copy into a project

```bash
cp -R samples/onboarding-demo/characters/mara-chen /path/to/project/characters/
# or scaffold empty then paste fields:
python scripts/dna_init.py "Your Character" --core "..." --anchor "..."
```

Then generate plates matching `reference_image_ids` and run:

```bash
python ../characters-props-locations-refs/scripts/cross_ref_check.py /path/to/project
```

These packets set `"sample": true` — clear that flag (or re-init) before Identity Lock.

## Agent Mode

Safe to pair with grok.com/imagine **Agent Mode**: generate plates there, keep DNA here, then cross-ref check. See `docs/guides/IMAGINE_MODELS_MAP.md`.
