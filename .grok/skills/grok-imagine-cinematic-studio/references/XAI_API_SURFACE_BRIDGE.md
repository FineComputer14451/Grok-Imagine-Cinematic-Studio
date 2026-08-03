# xAI API Surface Bridge Note

**For Imagine Agent Mode Handoff surface `xai_api` (Surface D)**

When Studio Director routes a generation job to the **xAI Imagine API** surface (`target_surface: "xai_api"`), load and follow the **`xai-grok-skill`**.

This bridge exists so cinematic production agents never invent API shapes, never mock responses, and never burn the app owner’s personal quota carelessly.

## Rules when surface = `xai_api`

1. Use the real injected `XAI_API_KEY` only (server-side).
2. Prefer the **Responses API** (`POST /v1/responses`) for any text / agentic / reasoning steps that accompany the generation.
3. For actual image or video generation, call the official Imagine endpoints documented at https://docs.x.ai.
4. Never expose the key to the client.
5. Treat every call as spending the owner’s personal credits — keep prompts tight, avoid loops, cache results.

## Explicit code snippet (server-side)

```ts
// Example: server function that can be called when handoff surface is "xai_api"
import { createServerFn } from "@tanstack/react-start";

export const runXaiImagineJob = createServerFn({ method: "POST" })
  .validator((input: {
    prompt: string;
    mode: "image" | "video";
    previousResponseId?: string;
  }) => input)
  .handler(async ({ data }) => {
    const apiKey = process.env.XAI_API_KEY;
    if (!apiKey) {
      return { ok: false as const, error: "XAI_API_KEY not available — cannot use xai_api surface" };
    }

    if (data.mode === "image") {
      const res = await fetch("https://api.x.ai/v1/images/generations", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${apiKey}`,
        },
        body: JSON.stringify({
          model: "grok-imagine-image-quality",
          prompt: data.prompt,
        }),
      });
      if (!res.ok) {
        return { ok: false as const, error: `xAI image API error ${res.status}` };
      }
      const body = await res.json();
      return { ok: true as const, type: "image", data: body };
    }

    return { ok: false as const, error: "Video path requires current docs.x.ai video endpoints" };
  });
```

## Integration points

- Studio Director / Imagine Agent Mode Handoff: when `target_surface === "xai_api"`, instruct agents to load `xai-grok-skill` and use patterns from this bridge.
- Always log the job / response id back into the handoff packet so Continuity Guardian and QA can track it.
- Prefer `grok_build_tools` surface when the local `image_gen` / `image_to_video` tools are available — use `xai_api` for live batch / remote jobs only.

**Canonical skill for all real xAI API usage:** `xai-grok-skill`  
**Docs:** https://docs.x.ai
