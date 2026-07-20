# Release Notes — v3.8.5

**Date:** 2026-07-20  
**Theme:** Full v4.5 Dual-Model Wave (Grok 4.5 / v9-4p5 + Imagine Video 1.0 & 1.5)

## Highlights

16 core skills upgraded to a uniform **Grok 4.5 / v9-4p5 Model Layer** with explicit dual **Imagine Video 1.0 + 1.5 Native** support.

### Identity & Continuity
- `character-dna-extractor`
- `identity-lock-specialist`
- `multi-character-identity-arbiter`
- `continuity-consistency-guardian`

### Sequencing & Direction
- `sequence-director`
- `studio-director`
- `cinematic-sequence-extender`
- `extend-frame-to-video`

### Prompting & Assets
- `imagine-prompt-master`
- `reference-asset-curator`

### Quality & Quota
- `quality-assurance-guardian`
- `workflow-quota-optimizer`
- `quota-dashboard`

### NSFW Pipeline
- `erosforge-nsfw-director`
- `nsfw-sequence-extender`
- `nsfw-quota-orchestrator`

## What Changed in Every Upgraded Skill

- Full Model Layer table for `grok-4-auto` / `grok-v9-4p5-multi` / `grok-v9-4p5-chat-expert`
- `model_compatibility` YAML block
- Explicit dual-path documentation (1.5 primary / 1.0 fallback)
- New or upgraded v4.5 Role Cards under `references/agents/`
- Updated Core Protocols (`MODEL_LAYER_ROUTING`, `1.0_1.5_DUAL_SUPPORT`, EROSFORGE awareness where relevant)
- Handoff Packet readiness
- Residual Grok 4.3 language removed

## Install / Update

```bash
# Recommended
grok plugin update grok-imagine-cinematic-studio

# Or via installer script
bash scripts/cinematic_studio.sh update
```

### From release assets

```bash
# Skills install zip
unzip grok-imagine-cinematic-studio-skills-install-v3.8.5.zip -d /tmp/cinematic-v385
cp -a /tmp/cinematic-v385/.grok/skills/* ~/.grok/skills/

# Meta-installer bootstrap
unzip grok-imagine-cinematic-studio-meta-installer-v3.8.5.zip -d /tmp/meta-v385
cd /tmp/meta-v385 && ./bootstrap.sh
```

## Verify

```bash
python tools/cinematic_studio_cli.py version   # should report 3.8.5
python tools/cinematic_studio_cli.py validate
bash scripts/cinematic_studio.sh verify
```

## Activation

```
Activate Grok Imagine Cinematic Studio v3.8.5
```

or

```
ACTIVATE CINEMATIC STUDIO META INSTALLER
```

## Notes

- This is a pure skill / documentation / Model Layer alignment release.
- No breaking changes to existing CLI commands, Production Bible schema, or Handoff Packet structure.
- All upgraded skills remain backward-compatible with previous workflows while adding explicit dual-model routing.

---

*Grok Imagine Cinematic Studio v3.8.5 — Dual-Model Ready*
