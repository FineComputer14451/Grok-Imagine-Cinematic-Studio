# Documentation
## Grok Imagine Cinematic Studio v3.8.9

Project documentation index (community-maintained).

> [!NOTE]
> **Grok Imagine Cinematic Studio** is an **independent community project**. It is **not affiliated with, endorsed by, sponsored by, or officially connected to xAI**. Full notice: [DISCLAIMER.md](../DISCLAIMER.md).

---

## Start Here

| Document | Description |
|----------|-------------|
| **[Official Documentation](OFFICIAL_DOCUMENTATION.md)** | Canonical product manual — overview, install, workflow, agents, CLI, packs, Wave A, ops |
| **[Official Overview](OFFICIAL_OVERVIEW.md)** | Short product introduction and capabilities |
| **[Disclaimer](../DISCLAIMER.md)** | Independence notice — not affiliated with xAI |
| **[Quick Start Guide](guides/Quick_Start_Guide.md)** | Fast onboarding + operator loop |
| **[User Guide](guides/USER_GUIDE.md)** | End-to-end production workflow (v3.8.9) |
| **[Operator Control Plane](guides/OPERATOR_CONTROL_PLANE.md)** | Orient → Health → Produce → Gate → Deliver |
| **[Architecture](ARCHITECTURE.md)** | System design, layers, protocols |
| **[CLI Reference](CLI_REFERENCE.md)** | Full command reference + TUI keys |

---

## Additional Guides

| Guide | Description |
|-------|-------------|
| [Installation Guide](guides/installation_guide.md) | Method A (CLI install) / Method B (plugin) + packs |
| [Upgrade Guide](guides/UPGRADE_GUIDE.md) | Migrating between studio versions |
| [Streamlit Cloud Deploy](guides/streamlit_cloud_deploy.md) | Host Web UI on Streamlit Community Cloud |
| [ComfyUI + Grok Build](guides/install_comfyui_grok_build.md) | Optional local diffusion setup |
| [Lustify + Grok Build](guides/install_lustify_grok_build.md) | Optional local SDXL checkpoint setup |

## Templates

- [Production Bible Template](templates/Project_Bible_Template.md)
- [Kink / NSFW Cinematic Template Library](templates/Kink_Specific_Cinematic_Template_Library.md)

## Releases

- [Release Notes index](releases/) — current: **[v3.8.9](releases/RELEASE_NOTES_v3.8.9.md)**
- Root [CHANGELOG.md](../CHANGELOG.md)

## Agent & Protocol Sources of Truth

| Concern | Location |
|---------|----------|
| Role Cards & Agent Index | [`references/agents/AGENT_INDEX.md`](../references/agents/AGENT_INDEX.md) |
| Model Layer | [`references/agents/MODEL_LAYER_v4.5.md`](../references/agents/MODEL_LAYER_v4.5.md) |
| Imagine Agent Mode Handoff | [`references/agents/IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md`](../references/agents/IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md) |
| Identity Continuity Protocol | [`references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md`](../references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md) |
| Parallel Brief Protocol | [`references/agents/Parallel_Brief_Protocol.md`](../references/agents/Parallel_Brief_Protocol.md) |
| Skills taxonomy / packs | [`references/SKILLS_TAXONOMY.md`](../references/SKILLS_TAXONOMY.md) |
| Models registry | [`references/MODELS_v3.6.md`](../references/MODELS_v3.6.md) |
| Skills runtime | [`.grok/skills/`](../.grok/skills/) |
| Plugin marketplace | [`.grok-plugin/`](../.grok-plugin/) |
| Plugin pack definitions | [`config/plugin_packs.yaml`](../config/plugin_packs.yaml) |
| Master activation prompt | [`MASTER_PROMPT.md`](../MASTER_PROMPT.md) |
| Repository layout | [REPOSITORY_LAYOUT.md](REPOSITORY_LAYOUT.md) |

## Examples

Production Bible and genre examples live under [`examples/`](../examples/) (including [`examples/production_bibles/`](../examples/production_bibles/)).

## Community

- [CONTRIBUTING.md](../CONTRIBUTING.md)
- [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md)
- [CONTRIBUTORS.md](../CONTRIBUTORS.md)
- [LICENSE](../LICENSE) — MIT

---

**Version**: 3.8.9  
**Last updated**: August 2026  
**Requires**: Grok Build ≥ 0.2.93 · Python 3.12+ (CLI / Web UI)
