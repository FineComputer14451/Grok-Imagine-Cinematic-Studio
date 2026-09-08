# MODEL_LAYER_v4.5.md
**Grok Imagine Cinematic Studio — Canonical Model Layer**  
**Version:** 4.6 | **Schema:** tools/models.py 1.1+  
**Date:** 2026-07-21  
**Owner:** Studio Director + Skill Agent Architect + Team Leader

---

## Purpose

This document is the single source of truth for how Cinematic Studio skills and agents should select, prefer, and declare compatibility with Grok models **and** Grok Imagine Video versions. All Role Cards and skills must reference this layer.

**Registry stack (studio v3.11.0):** cinematic + Build default is **`grok-4.6`**. Identifiers `grok-4.5`, `4.5`, `cinematic`, `build`, and `coding` resolve to `grok-4.6`. Chat modes are Auto / Fast / Expert / Heavy / Build. API and Build default is **`grok-4.6`**. Grok Build CLI min **1.0.5**. Optional 1M remains `grok-4.3`.

It provides first-class support for:

| Identifier                    | Short Name     | Primary Role                                      |
|-------------------------------|----------------|---------------------------------------------------|
| `grok-4.6` (Chat **Expert**)     | Chat Expert    | Highest-quality single-agent reasoning & craft    |
| `grok-4.6` (Chat **Heavy**)           | Multi          | Multi-agent orchestration, synthesis & handoffs   |
| `grok-4-auto`                 | Auto           | Balanced / automatic routing / draft / quota      |

And for Imagine generation (see `IMAGINE_SURFACES.md`):

| Version                  | When to Prefer                                      | Key Capabilities                          |
|--------------------------|-----------------------------------------------------|-------------------------------------------|
| **Imagine Image 1.0**    | Draft / volume stills                               | $0.02 / image                             |
| **Imagine Image 2.0**    | Hero plates, Quality Mode, Agent `image_generation` | Instruction-following, first-class edit, 1K/2K `quality` param |
| **Imagine Image Quality**| **Retired 2026-11-02** — do not send on the wire    | Redirects to 2.0 `quality=low` (was $0.05) |
| **Imagine Video 1.0**    | Default / cost-efficient / **edit + extend**        | t2v / i2v / v2v; 480p/720p                |
| **Imagine Video 1.5**    | Native audio, physics, intimacy, r2v, 1080p         | Native audio, refs + preset voices; **not** edit/extend |

There is **no** Imagine Video 2.0. `2.0` aliases resolve to Image 2.0 only.

---

## Model Profiles (Chat Layer)

### 1. grok-4.6  (Default for most specialist work)

- **Best for**: Deep reasoning, high-fidelity prompt engineering, Character DNA extraction & injection, Identity Lock decisions, QA reviews, narrative architecture, detailed lighting / DoP design, Sonic design, NSFW authenticity.
- **Strengths**: Reasoning depth, prompt quality, long-context fidelity, character consistency, subtle emotional subtext.
- **Preferred agents**: Imagine Prompt Master, Character DNA Extractor, Identity Lock Specialist, Quality Assurance Guardian, Narrative Arc & Pacing Strategist, Director of Photography, Sonic Architect (complex layers), ErosForge NSFW Director.
- **Reasoning recommendation**: **high** for Bibles, locks, QA, DNA, hero prompts, and complex creative judgments.
- **Use:** Chat **Expert** or API `grok-4.6`. Do not invent a picker id.

### 2. grok-4.6  (Default for Team Leader / Full Studio Mode)

- **Best for**: Multi-agent coordination, Team Leader synthesis, parallel specialist briefings, Handoff Packet assembly & Cross-Agent Consistency Audit, Sequence Director orchestration, Mega Production Architect planning, Continuity across clips.
- **Strengths**: Multi-agent awareness, handoff integrity, parallel reasoning, final synthesis quality, long production memory.
- **Preferred agents**: Team Leader / Final Synthesizer, Studio Director (Full Studio or MAXIMUM_AGENTIC_MODE), Mega Production Architect, Sequence Director, Continuity & Consistency Guardian (cross-clip), Cinematic Sequence Extender (chain planning).
- **Reasoning recommendation**: **high** + agentic depth.
- **Use:** Chat **Heavy** or API `grok-4.6`. Do not invent a picker id.

### 3. grok-4-auto

- **Best for**: Routine specialist tasks, draft / pre-vis / animatic passes, quota-sensitive sessions, rapid iteration, standard tier asset work, simple status & logging.
- **Strengths**: Balanced speed vs quality, lower cost profile, good generalist, reliable for non-critical paths.
- **Preferred agents**: Animatic Director (draft boards), Reference Asset Curator (standard tier), Foley (routine), Localization (standard), Generation Tracker, any “draft”, “fast”, or “quota” mode.
- **Reasoning recommendation**: medium (escalate to chat-expert or multi when quality gates fail or hero work begins).
- **Aliases**: `4-auto`, `auto`, `grok-auto`

---

## Imagine Video Protocol (1.0 vs 1.5 Native)

Every video-related Role Card and handoff **must** declare a `VIDEO_PIPELINE_SPEC`.

### Default Recommendation
- **Start with Imagine Video 1.0** unless one of the following is true:
  - Native synchronized audio is required (dialogue, intimate sound, Foley-critical, music-synced)
  - High physics fidelity or complex camera moves are needed
  - Micro-expression timing or breath/audio sync is critical (especially NSFW / performance)
  - User or Production Bible explicitly requests 1.5

### VIDEO_PIPELINE_SPEC Templates

**1.0 (Default – cost & reliability optimized)**
```
[VIDEO_PIPELINE_SPEC: model="grok-imagine-video", version="1.0", resolution="720p", clip_length="8-12s preferred", native_audio=false, reference_image_fidelity=high, extend_protocol="LAST_FRAME + MOTION_VECTOR", stitch_priority=high, audio_momentum=false]
```

**1.5 Native (when audio / physics / intimacy required)**
```
[VIDEO_PIPELINE_SPEC: model="grok-imagine-video-1.5", version="1.5", resolution="720p", clip_length="8-12s preferred", native_audio=true, reference_image_fidelity=high, extend_protocol="LAST_FRAME + MOTION_VECTOR + AUDIO_CUE", stitch_priority=high, audio_momentum=true]
```

### Model Routing for Video Work

| Task                                      | Preferred Chat Model          | Video Version | Notes |
|-------------------------------------------|-------------------------------|---------------|-------|
| Hero prompt craft / DNA inject            | grok-4.6       | 1.0 or 1.5    | High reasoning |
| Sequence planning / multi-clip orchestration | grok-4.6          | 1.0 default   | Use multi for chain |
| Native audio design + AMV                 | grok-4.6       | **1.5**       | Sonic Architect owns |
| Draft / animatic / quota-tight            | grok-4-auto                   | 1.0           | Fast path |
| Extend / stitch chain QA                  | grok-4.6             | Match previous| Continuity Guardian |
| Intimate / ErosForge sequences            | grok-4.6       | **1.5 preferred** | Physics + audio authenticity |

### Critical Rules
1. Never claim native audio capabilities on 1.0.
2. Always carry `AUDIO_MOMENTUM_VECTOR` (AMV) when using 1.5 extends.
3. I2V Specialist and Prompt Master must embed the chosen VIDEO_PIPELINE_SPEC.
4. Sequence Extender and Continuity Guardian must validate version consistency across a chain.
5. Quota Optimizer must surface cost delta (1.5 is higher) before major 1.5 spends.

---

## Usage Rules for Skills & Role Cards

Every skill SKILL.md and every Role Card that performs non-trivial reasoning **must** contain a short **Model Layer** section:

```markdown
## Model Layer (Grok 4.6)

| Task type                    | Preferred model              | Reasoning |
|-----------------------------|------------------------------|-----------|
| Standard specialist work    | grok-4.6      | high      |
| Multi-agent / handoff work  | grok-4.6            | high      |
| Draft / quota-sensitive     | grok-4-auto                  | medium    |

**Registry:** `tools/models.py` · `references/agents/MODEL_LAYER_v4.5.md` · `models verify`
```

Plus, when the agent touches video:

```markdown
## Imagine Video Protocol
- Default: 1.0 unless native audio / physics / intimacy requires 1.5
- Always emit VIDEO_PIPELINE_SPEC
- Carry AUDIO_MOMENTUM_VECTOR on 1.5 extends
```

### Declaration (Recommended in frontmatter or body)

```yaml
model_compatibility:
  - grok-4.6
preferred_model: grok-4.6   # or multi / auto
imagine_video_support:
  - "1.0"
  - "1.5"
```

---

## Routing Helpers (from tools/models.py)

```python
from tools.models import (
    resolve_chat_model,
    recommended_model_for_role,
    DEFAULT_XAI_CHAT_MODEL,          # → grok-4.6 (registry / Bible / Build stack lock)
    DEFAULT_XAI_CHAT_EXPERT_MODEL,   # → grok-4.6 (specialist craft)
    DEFAULT_XAI_MULTI_MODEL,         # → grok-4.6
    DEFAULT_XAI_AUTO_MODEL,          # → grok-4-auto
)
```

- `resolve_chat_model("multi")` → `grok-4.6` (Chat **Heavy**)
- `resolve_chat_model("chat-expert")` → `grok-4.6` (Chat **Expert**)
- `resolve_chat_model` empty or `grok-4.6` → `grok-4.6`. Chat Expert is a grok.com mode, not an API id.
- `recommended_model_for_role("Team Leader")` → `grok-4.6` (Chat **Heavy**)
- `recommended_model_for_role("Imagine Prompt Master")` → `grok-4.6` (Chat **Expert**)

### Grok Build picker install (when native product IDs are unavailable)

Public `api.x.ai` may return **Model not found** for `grok-4.6` / `grok-4-auto`. Install session-auth specialist pickers that wrap `grok-4.6` with role-tuned sampling:

```bash
grok models
/model grok-4.6
```


---

## Migration & Validation Notes

- All Role Cards in `references/agents/` have been enhanced (or are being enhanced) to this standard as of 2026-07-21.
- Previous hard-coded “Grok 4.5” language should now use the explicit 4.6 identifiers for **specialist routing**; stack lock / Bibles remain **`grok-4.6`** (`grok-4.5` aliases wrap 4.6).
- Team Leader / Full Studio Mode orchestration **defaults to grok-4.6**.
- Run after changes:

```bash
python tools/models.py
python tools/cinematic_studio_cli.py models verify
bash .grok/skills/cinematic-skill-creator/scripts/validate_skill.sh <skill> --v45
```

---

**End of MODEL_LAYER_v4.5.md (v4.5.1)**  
*Grok Imagine Cinematic Studio — Fully optimized for grok-4-auto · grok-4.6 · grok-4.6 + Imagine Video 1.0 / 1.5 Native*
