# character-dna-extractor

Forensic Character DNA extraction + Identity Lock handoff for Grok Imagine.
Includes portable **`dna init`**.

## Activate

```
ACTIVATE CHARACTER_DNA_EXTRACTOR
```

## DNA init (portable)

```bash
cd ~/.grok/skills/character-dna-extractor   # or wherever you unzipped
python scripts/dna_init.py "Character Name" \
  --core "Core identity" \
  --facial "Face / eyes / skin" \
  --hair "Hair" \
  --anchor "Key lock trait"
```

Creates `characters/{slug}/dna.json` + `DNA.md` (Studio schema 1.0).

Studio equivalent: `python tools/cinematic_studio_cli.py dna init "Name" ...`

## Install

```bash
unzip character-dna-extractor-skill.zip -d ~/.grok/skills/
# or from combined pack:
unzip grok-imagine-skills-pack.zip -d ~/.grok/
```

## Scripts

| Script | Role |
|--------|------|
| `scripts/dna_init.py` | Scaffold DNA profile (portable init) |
| `scripts/dna_handoff.py` | Identity Lock handoff (needs Studio `tools/`) |
| `scripts/dna_inject.py` | Prompt inject blocks (needs Studio `tools/`) |

See `references/DNA_INIT.md` and `references/dna_cli_init.md`.

## Sample DNA packets

See `samples/README.md` — Mara Chen + Kai Reed schema 1.0 packets for onboarding.
