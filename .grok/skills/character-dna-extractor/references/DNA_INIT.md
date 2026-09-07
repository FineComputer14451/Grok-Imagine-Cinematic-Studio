# DNA init

Scaffold a Character DNA profile before forensic extract or Identity Lock.

## Portable (this skill — no Studio required)

```bash
python scripts/dna_init.py "Character Name" \
  --core "Core identity traits" \
  --facial "Facial structure, eyes, skin tone" \
  --hair "Hair and grooming" \
  --clothing "Wardrobe" \
  --movement "Posture" \
  --emotion "Baseline emotion" \
  --motion "Video motion notes" \
  --anchor "Non-negotiable trait" \
  --anchor "Another anchor"
```

Writes `characters/{slug}/dna.json` + `DNA.md`.

Flags:
- `-o path/to/dna.json` — JSON only
- `--stdout` — print JSON, no files
- `--characters-dir DIR` — default `./characters`

## Studio CLI (same schema)

```bash
python tools/cinematic_studio_cli.py dna init "Character Name" \
  --core "..." --facial "..." --hair "..."
```

Then: `dna show` · `dna lock` · `dna inject` · `dna handoff`

Full command card: `dna_cli_init.md`

## After init

Hero plates: Quality Mode / `grok-imagine-image-2.0` via `ACTIVATE IMAGINE_MODEL_OVERRIDES hero`.
Chat extract: **Expert** / API `grok-4.6`.
