# character-dna-extractor

Forensic Character DNA extraction + Identity Lock handoff for Grok Imagine.

## Activate

```
ACTIVATE CHARACTER_DNA_EXTRACTOR
```

## Install

```bash
unzip character-dna-extractor-skill.zip -d ~/.grok/skills/
# or from combined pack:
unzip grok-imagine-skills-pack.zip -d ~/.grok/
# lands under ~/.grok/skills/character-dna-extractor/
```

## DNA init (Studio CLI)

Scaffold a DNA profile with the Studio command (see `references/dna_cli_init.md`):

```bash
python tools/cinematic_studio_cli.py dna init "<character>" ...
```

Scripts in this skill: `scripts/dna_handoff.py`, `scripts/dna_inject.py`.
