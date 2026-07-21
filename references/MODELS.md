# Models registry (canonical alias)

Full model selection guide for **Grok 4.5** (cinematic + Build default), optional **v9-4p5** routing surfaces, optional **Grok 4.3** 1M, and Imagine Video/Image:

→ **Primary agent embed:** [`agents/MODEL_LAYER_v4.5.md`](agents/MODEL_LAYER_v4.5.md)  
→ **Prior stack table:** [`agents/MODEL_LAYER_v3.7.1.md`](agents/MODEL_LAYER_v3.7.1.md)  
→ **Long-form guide:** [`MODELS_v3.6.md`](MODELS_v3.6.md) (filename historical; content tracks studio **v3.8.5**)

Code registry (single source of truth): `tools/models.py` · `STUDIO_COMPATIBILITY_VERSION = 3.8.5`.

```bash
python tools/cinematic_studio_cli.py models list
python tools/cinematic_studio_cli.py models verify
python tools/cinematic_studio_cli.py stack
```

| Layer | Default slug | Notes |
|-------|--------------|-------|
| Orchestration / cinematic chat | `grok-4.5` | Production Bibles, multi-agent |
| Opt-in multi / expert | `grok-v9-4p5-multi` · `grok-v9-4p5-chat-expert` | Skill Model Layer routing |
| Fast routing | `grok-4-auto` | Routine specialist hops |
| Long-context | `grok-4.3` | 1M memory banks only |
| Grok Build CLI | `grok-4.5` · fork `grok-build` | ≥ 0.2.93 binary |
| Imagine Video | `grok-imagine-video` (1.0 cost) / `1.5` native audio | Dual path |
| Imagine Image | `grok-imagine-image` · quality tier | Stills / hero plates |
