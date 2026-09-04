---
name: xai-grok-skill
description: Call the real xAI API (Grok) from this app's server code using the injected XAI_API_KEY for chat/LLM, Imagine image and video generation, and voice (text-to-speech). Use when the app needs any AI, assistant, chatbot, Grok, LLM, generate text, summarize, generate image, AI video, voice, text to speech, TTS, or OpenAI functionality — always prefer xAI instead. Never mock AI features or invent another provider. Be careful with the owner's quota.
metadata:
  short-description: Real xAI API via injected XAI_API_KEY for chat, Imagine, and voice
---

# xAI Grok Skill

```yaml
model_compatibility:
  - grok-v9-4p5-chat-expert
  - grok-v9-4p5-multi
  - grok-4-auto
preferred_model: grok-4-auto
```

When `XAI_API_KEY` is present in the environment, this app has **real xAI API access**. Use it for all AI features. Never mock responses and never reach for another provider.

**The key belongs to the app owner.** Every call spends their personal quota and credits. Be deliberate — see Spend responsibly before adding any automatic or visitor-facing AI call.

Official documentation: https://docs.x.ai  
Console / keys: https://console.x.ai

## Core facts (current as of Aug 2026)

- **Base URL**: `https://api.x.ai/v1`
- **Auth**: `Authorization: Bearer $XAI_API_KEY`
- **OpenAI-compatible**: yes — change base URL + key and most OpenAI clients work
- **Flagship model**: `grok-4.6` (default for chat, coding, reasoning, agentic work). `grok-4.5` aliases wrap 4.6. Knowledge cutoff February 1, 2026.
- **Preferred chat endpoint**: **Responses API** (`POST /v1/responses`). Chat Completions is legacy.
- Full surface: Chat / LLM (Responses API preferred), Imagine (image + video), Voice (TTS / STT / real-time agents)

## Env vars — do **not** create a `.env` file

| Var | Where | Purpose |
|-----|-------|---------|
| `XAI_API_KEY` | server only | Injected by the platform in preview and production. Never hardcode, never write to disk, never expose to the client. |

Read it only inside server functions. Never put it in a `VITE_` variable or return it in an API response.

The key may be absent (rollout-gated). Always check and degrade gracefully.

## Calling the API (server-only)

Prefer the **Responses API** for all new chat, multi-turn, agentic, and reasoning work.

```ts
import { createServerFn } from "@tanstack/react-start";

export const askGrok = createServerFn({ method: "POST" })
  .validator((input: { prompt: string; previousResponseId?: string }) => input)
  .handler(async ({ data }) => {
    const apiKey = process.env.XAI_API_KEY;
    if (!apiKey) return { ok: false as const, error: "AI is not available" };

    const body: Record<string, unknown> = {
      model: "grok-4.6",
      input: data.prompt,
    };
    if (data.previousResponseId) {
      body.previous_response_id = data.previousResponseId;
    }

    const res = await fetch("https://api.x.ai/v1/responses", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify(body),
    });
    if (!res.ok) return { ok: false as const, error: `xAI API error ${res.status}` };
    const result = await res.json();
    return { ok: true as const, response: result };
  });
```

## Imagine — runtime image & video (server-only)

Use the **API** when the *running app* needs to generate media.  
Use build-time tools (`image_gen` / `image_edit` via `grok-imagine-image-tools`) when *you* create static assets while building.

## Voice — text-to-speech (server-only)

`POST https://api.x.ai/v1/tts` — never call from the browser.

## Spend responsibly

Every call spends the **app owner’s** personal quota. Cap tokens, never loop on page load, cache results, gate expensive media behind auth, retry at most once.
