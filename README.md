## 🏗️ System Architecture (v3.7.1)

**Visual Architecture Diagrams**

![System Architecture](assets/system_architecture_v3.3.png)

![Orchestration Flow](assets/orchestration_flow_v3.3.png)

```
Studio Director v3.7.1 + Mega Production Architect v3.6.5  (Role Cards; studio v3.7.1 · Grok 4.5)
├── .grok-plugin/                 # Marketplace + plugin manifests (48 skills) — managed via `cinematic-studio plugin catalog`
├── references/agents/            # Role Cards + AGENT_INDEX + MODEL_LAYER_v3.7.1 + Handoff protocol
├── tools/                        # character_dna, sequence_chain, quota_optimizer, nsfw_*, models.py, bible_stages, imagine_bridge
├── tools/cinematic_studio_cli.py   # CLI: create-bible --wizard, dna, sequence, quota, nsfw, models, imagine, plugin catalog
├── references/MODELS_v3.6.md   # Grok Build + xAI model registry (Grok 4.5 default)
├── web_ui/app.py                 # Streamlit + Guided Bible Creator + model pickers
├── examples/                     # Production Bible templates
├── MASTER_PROMPT.md         # Main activation prompt (v3.7.1 · Grok 4.5)
├── scripts/                      # thin shims (release/verify); real catalog work via `cinematic-studio plugin catalog`
└── .grok/skills/                 # 48 custom Grok skills (primary runtime)
```

**Key v3.7.1 Components:**
- `references/agents/` — Role Cards (labels remain v3.6.5 in CLI registry; Studio Director **v3.7.1**)
- `references/agents/MODEL_LAYER_v3.7.1.md` — Grok 4.5 operating rules for every agent/skill
- `MASTER_PROMPT.md` — Activation with Grok 4.5 stack + Imagine Agent Mode Handoff
- `tools/cli/bible_stages.py` — Guided Production Bible wizard (CLI `--wizard` + Web UI)
- `references/agents/AGENT_INDEX.md` — Quick reference + activation presets
- `.grok-plugin/` — Marketplace support for `grok plugin install` + release-pin hygiene

---

## 🎨 Visual Identity & Branding

<p align="center">
  <img src="assets/banner.jpg" alt="Grok Imagine Cinematic Studio Banner" width="100%">
</p>

<p align="center">
  <img src="assets/logo.jpg" alt="Studio Logo" width="280">
</p>

**New Epic Cinematic Banner (v3.8 Premium Upgrade)**

A brand new Hollywood-grade epic banner was generated specifically for this release. It features a massive cinematic camera lens with holographic AI elements, gold/teal accents, and premium film production aesthetics. 

**Recommended:** Replace `assets/banner.jpg` with the new version for a significantly more premium GitHub presence.

### Web UI Experience

The studio includes a beautiful Streamlit dashboard for guided Production Bible creation, model selection, live cost estimation, and sequence management.

### Cinematic Output Style

The system produces emotionally powerful, production-ready visuals with locked character identity, physics-aware motion (especially in Imagine Video 1.5), and native synchronized audio.

---