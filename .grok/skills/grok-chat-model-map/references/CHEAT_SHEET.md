# Grok Chat Mode Cheat Sheet
**For https://grok.com Chat — Auto / Fast / Expert / Heavy / Build**

Verified picker **2026-09-06**: Auto · Fast · Expert · Heavy · Build  
Skill: `ACTIVATE GROK_CHAT_MODEL_MAP`  
Plan PR: https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/pull/48  
Install: copy folder → `~/.grok/skills/grok-chat-model-map/`  
Models docs: https://docs.x.ai/developers/models · Grok 4.6: https://docs.x.ai/developers/grok-4-6

---

## 30-second pick

| You want… | Click in Chat picker |
|-----------|----------------------|
| Default / mixed | **Auto** |
| Speed | **Fast** |
| Hard reasoning / depth | **Expert** |
| Max multi-agent depth | **Heavy** |
| Coding agent | **Build** |
| Stills / video | Sidebar **Imagine** (not this picker) |

**Grok 4.6** = current Chat/Code generation (docs). It is **not** a separate fifth depth tile in the verified Chat picker.

---

## Mode → meaning

| Mode | Kind | Notes |
|------|------|-------|
| Auto | Router | Picks Fast-like or Expert-like path — **not** an API model string |
| Fast | Latency | Light / quick answers |
| Expert | Deep | Best Chat match for **4.6**-generation flagship reasoning |
| Heavy | Multi-agent | Separate Heavy path — not “Expert but slower” |
| Build | Surface hop | Opens **Grok Build** coding agent |

---

## Do not confuse

| Surface | What you pick |
|---------|----------------|
| grok.com **Chat** | Auto / Fast / Expert / Heavy (/ Build) |
| **api.x.ai** | `grok-4.6`, `grok-4.5`, … — never send `Auto` or `Expert` as `model` |
| **Grok Build** TUI | Host `/model` aliases; default coding ≈ `grok-4.6` |
| **Imagine** | Quality = **Image 2.0** (`grok-imagine-image-2.0`) · Fast = 1.0 · Video 1.0/1.5 → `imagine-model-overrides` |
| Cinematic Studio | `tools/models.py` registry (different map) |

---

## Tier note

On the verified 2026-09-06 grok.com session, all five modes were **visible with no lock badges**. Quotas can still differ by plan (Heavy often needs SuperGrok Heavy for full compute).
