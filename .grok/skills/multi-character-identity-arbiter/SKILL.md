---
name: multi-character-identity-arbiter
description: Arbitrate primary and secondary Character DNA locks for multi-cast Grok Imagine scenes. Builds dual inject blocks and conflict reports. Activate when two or more characters share a frame or sequence.
---

# Multi-Character Identity Arbiter v3.7.1

**Role Card:** `references/agents/Multi_Character_Identity_Arbiter.md`  
**Tool:** `tools/multi_character_arbiter.py`

## Model Layer (Grok 4.5 · studio v3.7.1)

| Layer | Slug | When |
|-------|------|------|
| Orchestration (default) | `grok-4.5` | Bibles, direction, agent loops |
| Long-context (opt-in) | `grok-4.3` | 1M memory banks (`--chat-model grok-4.3`) |
| Grok Build CLI | `grok-4.5` · `grok-build` | Skills / coding (≥ 0.2.93) |
| Imagine Video | `grok-imagine-video` / `1.5` | 1.0 cost · 1.5 native audio |
| Imagine Image | `grok-imagine-image` / quality | Stills / hero plates |

Prefer stable `prompt_cache_key` on multi-turn `grok-4.5` loops. Reasoning **high** for Bibles/QA/locks; opt into `grok-4.3` only for 1M. Imagine tools: `image_gen` / `image_edit` / `image_to_video` (not chat models). Full stack: `references/agents/MODEL_LAYER_v3.7.1.md` · `tools/models.py`.

## Activation

```
ACTIVATE MULTI_CHARACTER_ARBITER
```

**When:** two or more locked characters share a frame, shot, or sequence extend. Pair with Identity Lock Specialist and Sequence Director.

## CLI

Arbitrate cast (elect primary, weights, conflicts; save on sequence):

```bash
python tools/cinematic_studio_cli.py sequence cast arbitrate "Sequence Name" \
  --characters hero,partner --primary hero
```

Print multi-character inject block (saved plan or fresh):

```bash
python tools/cinematic_studio_cli.py sequence cast inject "Sequence Name"
python tools/cinematic_studio_cli.py sequence cast inject "Sequence Name" \
  --characters hero,partner --primary hero -o artifacts/cast_inject.txt
```

Optional: `--weights hero=0.75,partner=0.25` · `--no-save` on arbitrate.

## Plan keys (`cast_arbitration`)

| Key | Meaning |
|-----|---------|
| `mode` | `"multi_character"` |
| `primary_slug` / `primary_name` | Elected primary lock |
| `cast[]` | `slug`, `name`, `role`, `ref_weight`, `locked`, inject fields |
| `conflicts[]` | `code`, `severity`, `message` |
| `inject_block` | Full multi-DNA prompt injection |
| `rules_applied` | Rule tags applied |
| `pass` | `False` if any error-severity conflict |

Default weights: primary `0.75` (N=2) / `0.70` (N=3) / `0.65` (N≥4); secondaries split remainder.

## Anti-merge rules

- Exactly **one** primary; secondaries never override primary face DNA
- Inject order: primary cinematic block first, then secondary compact blocks
- Always include anti-merge language: distinct faces, hair, wardrobe; no face morph
- Conflicts: `shared_ref_id` (warn), `not_locked` (warn), `no_primary` / `missing_dna` / `empty_cast` (error)

## Handoff

1. Arbitrate → review conflicts → fix unlocks / shared refs with Identity Lock
2. Pass `inject_block` unchanged to Imagine Prompt Master / Sequence Extender
3. Identity Lock owns per-character drift; this skill owns **cast-level** primary + dual inject

```
DNA lock(s) → MULTI_CHARACTER_ARBITER → Identity Lock enforce → Prompt Master / Extend
```
