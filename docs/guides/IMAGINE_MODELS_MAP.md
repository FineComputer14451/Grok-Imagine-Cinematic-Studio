# Imagine models map (incl. Agent Mode)

**Pin this.** Canonical product slugs + where Agent Mode fits.  
Studio is an independent community project — not affiliated with xAI.

Deeper references:
- Surfaces / API / pricing: [`references/agents/IMAGINE_SURFACES.md`](../../references/agents/IMAGINE_SURFACES.md)
- Studio handoff protocol: [`references/agents/IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md`](../../references/agents/IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md)
- Overrides skill: `.grok/skills/imagine-model-overrides`
- Official: https://docs.x.ai/docs/guides/image-generations · https://docs.x.ai/docs/models · https://grok.com/imagine

There is **no** `grok-imagine-video-2.0`. **2.0 is Image only.**

---

## Image models

| UI / role | Wire slug | Notes |
|-----------|-----------|-------|
| **Fast Mode** (draft) | `grok-imagine-image` | Volume / storyboard; up to **3** edit refs |
| **Quality Mode** (hero) | `grok-imagine-image-2.0` | Typography, faces, detail; API `quality` = `low` \| `medium` \| `auto`; up to **5** edit refs |
| Legacy Quality / Pro | `grok-imagine-image-quality` | **Retired 2026-11-02** — rewrite spend to **2.0** + `quality=low` |

Aliases (examples): `2.0` / `image-2.0` / `quality-mode` → Image 2.0; `1.0` / `fast` / `draft` → Image 1.0.

---

## Video models

| UI / role | Wire slug | Native audio | Edit / extend |
|-----------|-----------|--------------|---------------|
| Video **1.0** | `grok-imagine-video` | no | **yes** (required) |
| Video **1.5** | `grok-imagine-video-1.5` | yes (Sound Layer) | **no** |

---

## Presets (overrides skill)

| Preset | Image | Video | Use |
|--------|-------|-------|-----|
| `hero` | 2.0 `medium` | 1.5 | Finals |
| `balanced` | 2.0 `auto` | 1.0 | Default |
| `draft` | 1.0 | 1.0 | Quota save |
| `audio-final` | 2.0 `medium` | 1.5 | Locked plate → i2v + audio |
| `edit-extend` | keep plate | **1.0 only** | Edit / extend |

```text
ACTIVATE IMAGINE_MODEL_OVERRIDES hero
```

---

## Agent Mode — two meanings (do not conflate)

### 1) Consumer **Imagine Agent Mode** (grok.com/imagine, beta)

| | |
|--|--|
| **What** | Infinite-canvas **workflow agent** on the web Imagine product |
| **Not** | A separate public API model slug (no `grok-imagine-agent` in docs) |
| **Templates** | Create Worlds · Short Film · UGC Product Stories · Brand Identity |
| **Does** | Plan → batch stills → i2v → stitch short clips → edit/export on one canvas |
| **Models underneath** | Same Imagine stack: Quality/Fast stills + Video 1.0/1.5; planning uses chat-model quota |
| **Access** | Web / paid Grok (beta); treat as **orchestration UI**, then pin outputs with the tables above |

### DNA board + cross-ref with Agent Mode

Consumer Agent Mode **does not** run Studio scripts. Use sample DNA + the post-board check **around** the canvas:

1. Copy sample DNA (`character-dna-extractor/samples/onboarding-demo/`) or `dna_init` your cast.
2. Generate / batch on Imagine Agent Mode (or Quality stills).
3. Save hero plates into `characters/` · `props/` · `locations/` per `characters-props-locations-refs` naming.
4. Run `python .grok/skills/characters-props-locations-refs/scripts/cross_ref_check.py .` — DNA ids must match plates before Identity Lock.
5. Clear `"sample": true` on demo packets; then lock / i2v (Image **2.0** heroes; Video **1.5** vs **1.0** rules above).

**Studio Agent Mode handoff** (A–E) is the tighter fit: DNA + board live in the project, check runs locally, then handoff.

| Asset | Path |
|-------|------|
| Cross-ref check | `.grok/skills/characters-props-locations-refs/scripts/cross_ref_check.py` |
| Cross-ref docs | `.grok/skills/characters-props-locations-refs/references/CROSS_REF_CHECK.md` |
| Sample DNA | `.grok/skills/character-dna-extractor/samples/onboarding-demo/` |
| Demo board | `.grok/skills/characters-props-locations-refs/samples/onboarding-demo/` |


### 2) Studio **Agent Mode handoff** (this repo)

Routing from planning agents into execution surfaces:

| ID | `target_surface` | Generation runs via |
|----|------------------|---------------------|
| A | `grok_build_tools` | Build session tools (`image_gen`, i2v, …) |
| B | `grok_agent_acp` | `grok agent` / IDE ACP |
| C | `grok_com_imagine` | Manual paste on grok.com/imagine (Quality = Image 2.0) |
| D | `xai_api` | REST `imagine submit` / sequence |
| E | `xai_responses_tool` | Responses `image_generation` (Image 2.0 stills) |

```bash
python tools/cinematic_studio_cli.py imagine agent-handoff \
  --batch <slug> --shot <id> --surface xai_api --format markdown
```

---

## Quick routing

1. Hero still → Quality / `grok-imagine-image-2.0`  
2. Draft spam → Fast / `grok-imagine-image`  
3. Final + audio → Video **1.5**  
4. Edit / extend → Video **1.0** only  
5. Multi-step film / brand pack on web → **Consumer Agent Mode**, then save plates + run **cross-ref check** / DNA lock (2.0 / 1.0 / 1.5 rules)  
6. Studio pipeline → handoff packet → surfaces A–E (not a new Imagine slug)

Coding / Grok Build chat stays on **`grok-4.6`** — never select `grok-imagine-*` for code.
