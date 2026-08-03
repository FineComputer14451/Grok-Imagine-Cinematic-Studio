# Surface Bridges Index

Quick reference for Imagine Agent Mode Handoff execution surfaces.  
Studio Director and any agent preparing a generation handoff should consult this index first.

## Surfaces at a glance

| Code | Surface | Required skill / guidance | Bridge note | Primary use |
|------|---------|---------------------------|-------------|-------------|
| **A** | `grok_build_tools` | `grok-imagine-image-tools` | `GROK_IMAGINE_IMAGE_TOOLS_BRIDGE.md` | Local tools available (`image_gen`, `image_edit`, `image_to_video`) |
| **B** | `grok_agent_acp` | Inherits A (or D) | (clarification in handoff protocol) | ACP / IDE agent sessions |
| **C** | `grok_com_imagine` | Paste-friendly packet rules | `GROK_COM_IMAGINE_BRIDGE.md` | Manual paste into grok.com/imagine web UI |
| **D** | `xai_api` | `xai-grok-skill` | `XAI_API_SURFACE_BRIDGE.md` | Live jobs with injected `XAI_API_KEY` |

## Visual Decision Flowchart

```
START: Need to generate image or video
                │
                ▼
     ┌──────────────────────┐
     │ Local Imagine tools  │
     │ available in session?│
     └──────────┬───────────┘
                │
       ┌────────┴────────┐
       │ YES             │ NO
       ▼                 ▼
┌──────────────┐   ┌─────────────────────┐
│ Use Surface A│   │ Is this an ACP /    │
│ grok_build_  │   │ IDE agent session?  │
│ tools        │   └──────────┬──────────┘
│              │              │
│ Load:        │     ┌────────┴────────┐
│ grok-imagine-│     │ YES             │ NO
│ image-tools  │     ▼                 ▼
│ + Bridge A   │  ┌──────────┐   ┌──────────────────┐
└──────────────┘  │ Surface B│   │ XAI_API_KEY      │
                  │ Inherit A│   │ present?         │
                  │ (or D if │   └────────┬─────────┘
                  │  API)    │            │
                  └──────────┘   ┌────────┴────────┐
                                 │ YES             │ NO
                                 ▼                 ▼
                          ┌──────────────┐  ┌──────────────┐
                          │ Use Surface D│  │ Use Surface C│
                          │ xai_api      │  │ grok_com_    │
                          │              │  │ imagine      │
                          │ Load:        │  │              │
                          │ xai-grok-    │  │ Follow:      │
                          │ skill        │  │ Bridge C     │
                          │ + Bridge D   │  │ (paste packet│
                          └──────────────┘  │  format)     │
                                            └──────────────┘
```

### Decision rules (short form)

1. **Tools available in the current session** → prefer **A**
2. **ACP / IDE agent session** → **B** (still obey A or D rules)
3. **Key present + batch / remote job** → **D**
4. **No key + user wants web UI review** → **C**

## Bridge files (all under `references/`)

| Bridge note | Purpose |
|-------------|---------|
| `GROK_IMAGINE_IMAGE_TOOLS_BRIDGE.md` | Prompt craft, code-vs-image decision, reference-first, consistency |
| `GROK_COM_IMAGINE_BRIDGE.md` | Paste-friendly packet format for the web UI |
| `XAI_API_SURFACE_BRIDGE.md` | Real injected key, Responses API preferred, server-only, quota care |

## Ownership

Studio Director owns surface selection and must ensure the matching skill / bridge is loaded before any generation spend.
