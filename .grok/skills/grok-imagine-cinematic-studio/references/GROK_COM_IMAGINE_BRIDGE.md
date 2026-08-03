# grok.com/imagine Surface Bridge Note (Surface C)

**For Imagine Agent Mode Handoff surface `grok_com_imagine`**

This is the **manual paste** path. The agent prepares a clean, human-readable packet that the user (or Studio Director) copies into the grok.com/imagine web UI. No live API key is used and no local `image_gen` / `image_to_video` tools are invoked.

## When to use this surface

- No `XAI_API_KEY` is available or the user explicitly wants to review/paste in the web UI.
- Quick visual checks, client review, or situations where the Build tools / ACP session are not available.
- Activation command: `ACTIVATE IMAGINE_BRIDGE`

## Rules for Surface C packets

1. **Subset only** — Emit a classic Execution Bridge packet (lighter than the full agent-mode handoff). Do not include server-only fields, API credentials, or internal CLI commands.
2. **Prompt quality still applies** — Load and follow `grok-imagine-image-tools` for prompt craft, reference-first rules, and consistency guidance even though the actual generation happens in the browser.
3. **Identity & continuity** — Always include the current Character DNA / Identity Lock inject block (or a clear reference to it) and any required last-frame / momentum notes so the user can paste them alongside the prompt.
4. **Keep it paste-friendly**:
   - Plain text or simple markdown
   - One clear prompt block
   - Optional short "Reference notes" or "DNA inject" section
   - No JSON that the web UI cannot consume directly
5. **Return path** — Tell the user exactly how to bring the generated image/video back into the studio (file path, upload instruction, or "drop into Sequence Director").

## Recommended paste packet structure

```text
=== GROK.COM/IMAGINE PASTE PACKET ===
Project / Shot: <slug or shot_id>
Mode: image | image_to_video | etc.
Aspect / Resolution note: <if relevant>

PROMPT:
<clean, Ultimate-template-style prompt ready to paste>

REFERENCE / DNA NOTES (paste or attach if the UI supports):
- Character DNA / Identity Lock: <short inject or "see Project Bible">
- Last frame / continuity: <if extend>
- Any required reference image description or URL the user should upload

RETURN PATH:
After generation, save the result and [upload to artifacts/ / tell Sequence Director / etc.]
=== END PACKET ===
```

## What to omit on Surface C

- Full `VIDEO_PIPELINE_SPEC` machine strings (summarize in plain language instead)
- Internal handoff_steps that only make sense for tools or API
- Any mention of `XAI_API_KEY` or server functions
- Long JSON payloads that cannot be pasted usefully

## Relationship to other surfaces

| Surface | Skill / Bridge |
|---------|----------------|
| A `grok_build_tools` | `grok-imagine-image-tools` + `GROK_IMAGINE_IMAGE_TOOLS_BRIDGE.md` |
| C `grok_com_imagine` | This note + still respect prompt rules from `grok-imagine-image-tools` |
| D `xai_api` | `xai-grok-skill` + `XAI_API_SURFACE_BRIDGE.md` |

Surface C is the lowest-automation path. Prefer A or D when the tools or key are available; use C when the user needs to work directly in the web UI.
