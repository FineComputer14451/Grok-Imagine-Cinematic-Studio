---
name: xai-api-build
description: Wrapper for using the real xAI API inside Grok Build apps. Enforce server-only access via process.env.XAI_API_KEY, prefer grok-4.5 for chat, use Imagine endpoints for image and video generation, and apply strict spend controls. Activate when writing server functions that call Grok, Imagine, or Voice, or when the user mentions xAI API, XAI_API_KEY, or runtime AI features in Build mode.
metadata:
  type: wrapper
  version: "1.0"
  wraps: xai-api
---

# xAI API Build Wrapper

Enforce correct and cost-aware use of the real xAI API when building applications in Grok Build.

## Core Rules

- The key lives only in `process.env.XAI_API_KEY`. Never hardcode it, never put it in a `.env` file, never expose it to the client, and never prefix it with `VITE_`.
- Always check for the key existence and degrade gracefully when it is missing.
- Default chat model is `grok-4.5` unless the user specifies otherwise.
- Image and video generation are significantly more expensive than chat. Treat them as premium features.
- Prefer user-initiated calls (button clicks, form submits). Never call the API on page load, on every keystroke, or inside tight loops.
- Cap `max_tokens` on chat calls and keep prompts reasonably short for visitor-facing features.
- Cache or persist results when the same content would otherwise be regenerated.
- Gate expensive media generation behind authentication when the app design allows it.
- On API errors, surface the error cleanly. Retry at most once.

## Recommended Patterns

### Chat

```ts
const apiKey = process.env.XAI_API_KEY;
if (!apiKey) return { ok: false, error: "AI is not available" };

const res = await fetch("https://api.x.ai/v1/chat/completions", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${apiKey}`,
  },
  body: JSON.stringify({
    model: "grok-4.5",
    messages: [{ role: "user", content: prompt }],
  }),
});
```

### Image Generation

Use `POST /v1/images/generations` with model `grok-imagine-image-quality` (or the cheaper `grok-imagine-image`).

### Video Generation

Use the async video endpoints (`/v1/videos/generations` then poll). Prefer shorter durations and lower resolutions when budget is a concern.

## Spend Discipline

Every call consumes the app owner's personal quota and credits. Be deliberate. Prefer still images over video, 1k over 2k, and short clips over long ones when the use case allows it.

## References

See `references/original-xai-api.md` for the full original skill content.
