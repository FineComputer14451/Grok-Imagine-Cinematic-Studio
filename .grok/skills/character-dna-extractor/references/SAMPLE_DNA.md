# Sample DNA packets

See `samples/onboarding-demo/characters/` for filled schema 1.0 packets:

- `mara-chen` — lead
- `kai-reed` — supporting

Copy a folder into your project `characters/`, swap plate ids after you generate Quality / Image 2.0 heroes, then run the post-board cross-ref check (`characters-props-locations-refs/scripts/cross_ref_check.py`).

## With Imagine Agent Mode

1. Copy a sample folder into your project `characters/`.
2. Use consumer Agent Mode (or Quality / Image 2.0) to generate heroes matching `reference_image_ids`.
3. Drop plates into the board folders; run `characters-props-locations-refs/scripts/cross_ref_check.py`.
4. Clear `"sample": true` before Identity Lock.

See `docs/guides/IMAGINE_MODELS_MAP.md` (DNA board + cross-ref with Agent Mode).
