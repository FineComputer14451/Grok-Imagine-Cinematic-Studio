export type ApiEndpoint = {
  id: string;
  method: "GET" | "POST";
  path: string;
  title: string;
  summary: string;
  request?: string;
  response?: string;
  notes?: string[];
};

export type ApiSection = {
  id: string;
  title: string;
  intro: string;
  endpoints: ApiEndpoint[];
};

export type PriceRow = {
  model: string;
  unit: string;
  price: string;
  note?: string;
};

export type PriceGroup = {
  id: string;
  title: string;
  blurb: string;
  rows: PriceRow[];
};

/**
 * Public xAI developer API list prices (not subscription quotas).
 * “Draft still” in studio examples means the cheaper image *model path*
 * (grok-imagine-image), not that the dollar amounts are unofficial drafts.
 */
export const GROK_PRICING: {
  asOf: string;
  source: string;
  sourceUrl: string;
  status: string;
  disclaimer: string;
  groups: PriceGroup[];
  studioExamples: {
    label: string;
    estimate: string;
    detail: string;
    kind: "list" | "example";
  }[];
} = {
  asOf: "August 2026",
  source: "x.ai/api · docs.x.ai",
  sourceUrl: "https://docs.x.ai",
  status:
    "Published developer API list prices — not “draft” rate cards. Confirm on docs.x.ai before you budget.",
  disclaimer:
    "These are published API list prices for metered developer keys (as listed on x.ai/api and docs.x.ai around August 2026). They are not temporary draft figures. SuperGrok / consumer app quotas are separate from API billing. Studio “snapshots” below are worked examples (~) using those list rates, not separate price tiers. Always re-check the official docs before production budgeting.",
  groups: [
    {
      id: "chat",
      title: "Chat / LLM",
      blurb: "Published list rates per million tokens.",
      rows: [
        {
          model: "grok-4.5",
          unit: "Input / 1M tokens",
          price: "$2.00",
          note: "List price",
        },
        {
          model: "grok-4.5",
          unit: "Output / 1M tokens",
          price: "$6.00",
          note: "List price",
        },
      ],
    },
    {
      id: "image",
      title: "Imagine — images",
      blurb:
        "Two product tiers: standard (cheaper iteration) vs quality (hero stills). Prices are official list rates for each model.",
      rows: [
        {
          model: "grok-imagine-image",
          unit: "Output / image (1K or 2K)",
          price: "$0.02",
          note: "Standard model — cheaper iteration path",
        },
        {
          model: "grok-imagine-image",
          unit: "Media input / image",
          price: "$0.002",
          note: "When sending reference images",
        },
        {
          model: "grok-imagine-image-quality",
          unit: "Output / image (1K)",
          price: "$0.05",
          note: "Quality model — hero / final stills",
        },
        {
          model: "grok-imagine-image-quality",
          unit: "Output / image (2K)",
          price: "$0.07",
          note: "Quality model",
        },
        {
          model: "grok-imagine-image-quality",
          unit: "Media input / image",
          price: "$0.01",
          note: "When sending reference images",
        },
      ],
    },
    {
      id: "video",
      title: "Imagine — video",
      blurb: "Published per-second list rates by resolution.",
      rows: [
        {
          model: "grok-imagine-video",
          unit: "Output / second (480p)",
          price: "$0.05",
          note: "List price",
        },
        {
          model: "grok-imagine-video",
          unit: "Output / second (720p)",
          price: "$0.07",
          note: "List price",
        },
        {
          model: "grok-imagine-video",
          unit: "Media input / second",
          price: "$0.01",
          note: "When conditioning on media",
        },
        {
          model: "grok-imagine-video",
          unit: "Media input / image",
          price: "$0.002",
          note: "Image conditioning",
        },
      ],
    },
    {
      id: "voice",
      title: "Voice",
      blurb: "Published TTS / STT / speech-to-speech list rates.",
      rows: [
        {
          model: "Text to speech",
          unit: "Per 1M characters",
          price: "$15.00",
          note: "List price",
        },
        {
          model: "Speech to text (REST)",
          unit: "Per hour",
          price: "$0.10",
          note: "List price",
        },
        {
          model: "Speech to text (streaming)",
          unit: "Per hour",
          price: "$0.20",
          note: "List price",
        },
        {
          model: "Speech to speech",
          unit: "Per minute",
          price: "from $0.05",
          note: "Starting rate on public sheet",
        },
      ],
    },
  ],
  studioExamples: [
    {
      label: "Standard still (iteration)",
      estimate: "$0.02",
      detail: "1× grok-imagine-image @ list $0.02 — not an unofficial “draft rate”",
      kind: "example",
    },
    {
      label: "Quality still 2K (hero)",
      estimate: "$0.07",
      detail: "1× grok-imagine-image-quality @ list $0.07",
      kind: "example",
    },
    {
      label: "6s clip @ 720p",
      estimate: "~$0.42",
      detail: "6 × $0.07/s list — worked example",
      kind: "example",
    },
    {
      label: "15s hero @ 720p",
      estimate: "~$1.05",
      detail: "15 × $0.07/s list — worked example",
      kind: "example",
    },
    {
      label: "Prompt craft (chat)",
      estimate: "≪ $0.01",
      detail: "Small grok-4.5 call with capped max_tokens — illustrative",
      kind: "example",
    },
  ],
};

export const API_OVERVIEW = {
  title: "xAI Integration API",
  version: "v1 · OpenAI-compatible",
  base: "https://api.x.ai/v1",
  auth: "Authorization: Bearer $XAI_API_KEY",
  description:
    "Server-side integration reference for Grok chat, Imagine (image & video), and Voice. Keys are server-only — never expose XAI_API_KEY to the browser. Official source of truth: docs.x.ai.",
};

export const API_SECTIONS: ApiSection[] = [
  {
    id: "auth",
    title: "Auth & setup",
    intro:
      "The platform injects XAI_API_KEY in preview and deploy. Read it only inside createServerFn / server code. Do not create a .env file or use VITE_ prefixes.",
    endpoints: [
      {
        id: "auth-header",
        method: "POST",
        path: "Authorization header",
        title: "Bearer authentication",
        summary: "Every request uses the same header. Missing key → degrade gracefully.",
        request: `const apiKey = process.env.XAI_API_KEY;
if (!apiKey) {
  return { ok: false, error: "AI is not available" };
}

fetch("https://api.x.ai/v1/chat/completions", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: \`Bearer \${apiKey}\`,
  },
  body: JSON.stringify({ /* … */ }),
});`,
        response: `// 401 — invalid or missing key
// 429 — rate limited / quota
// 5xx — retry at most once, then surface error`,
        notes: [
          "Key belongs to the app owner — every call spends their credits.",
          "Never call xAI from client components.",
          "If key is absent (rollout-gated), show “AI unavailable” UI instead of crashing.",
        ],
      },
      {
        id: "server-fn-pattern",
        method: "POST",
        path: "createServerFn",
        title: "TanStack server function pattern",
        summary: "Canonical shape for this stack (Studio Academy / Grok Build apps).",
        request: `import { createServerFn } from "@tanstack/react-start";

export const askGrok = createServerFn({ method: "POST" })
  .validator((input: { prompt: string }) => input)
  .handler(async ({ data }) => {
    const apiKey = process.env.XAI_API_KEY;
    if (!apiKey) return { ok: false as const, error: "AI is not available" };

    const res = await fetch("https://api.x.ai/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: \`Bearer \${apiKey}\`,
      },
      body: JSON.stringify({
        model: "grok-4.5",
        messages: [{ role: "user", content: data.prompt }],
      }),
    });
    if (!res.ok) {
      return { ok: false as const, error: \`xAI API error \${res.status}\` };
    }
    const body = (await res.json()) as {
      choices: { message: { content: string } }[];
    };
    return { ok: true as const, text: body.choices[0]?.message.content ?? "" };
  });`,
        notes: [
          "Default chat model: grok-4.5 unless the user asks otherwise.",
          "OpenAI SDKs work with base_url https://api.x.ai/v1.",
        ],
      },
    ],
  },
  {
    id: "chat",
    title: "Chat / LLM",
    intro:
      "Text generation for briefs, Production Bible drafts, prompt refinement, and agent-style orchestration in your app.",
    endpoints: [
      {
        id: "chat-completions",
        method: "POST",
        path: "/v1/chat/completions",
        title: "Chat completions",
        summary:
          "OpenAI-compatible chat. grok-4.5 list: $2 input / $6 output per 1M tokens.",
        request: `POST https://api.x.ai/v1/chat/completions

{
  "model": "grok-4.5",
  "messages": [
    { "role": "system", "content": "You are a cinematic production assistant." },
    { "role": "user", "content": "Write a 3-shot neon alley brief." }
  ],
  "max_tokens": 1024,
  "temperature": 0.7
}`,
        response: `{
  "id": "chatcmpl-…",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Shot 1 — wide establishing…"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": { "prompt_tokens": 42, "completion_tokens": 180 }
}`,
        notes: [
          "Cap max_tokens on visitor-facing features.",
          "User-initiated only — not on page load or every keystroke.",
          "Streaming, tools, and vision: see docs.x.ai.",
        ],
      },
    ],
  },
  {
    id: "imagine-image",
    title: "Imagine — images",
    intro:
      "Standard model for cheap iteration; quality model for hero stills. Dollar amounts are published list prices.",
    endpoints: [
      {
        id: "images-generations",
        method: "POST",
        path: "/v1/images/generations",
        title: "Generate image",
        summary:
          "Standard list ~$0.02/img; quality list $0.05 (1K) / $0.07 (2K).",
        request: `POST https://api.x.ai/v1/images/generations

{
  "model": "grok-imagine-image-quality",
  "prompt": "Cinematic still, rain-slick neon alley, 35mm, teal amber practicals",
  "n": 1,
  "resolution": "1k",
  "response_format": "url"
}

// Cheaper iteration: "grok-imagine-image" (list ~$0.02)
// resolution: "1k" | "2k"
// n: ≤ 10
// response_format: "url" | "b64_json"`,
        response: `{
  "data": [
    { "url": "https://…" }
  ]
}`,
        notes: [
          "Quality model costs more than the standard imagine-image model.",
          "Cache URLs or persist to storage — do not regenerate per page view.",
          "Gate public generation behind sign-in when possible.",
        ],
      },
      {
        id: "images-edits",
        method: "POST",
        path: "/v1/images/edits",
        title: "Edit image",
        summary: "Natural-language edits with up to 3 reference images.",
        request: `POST https://api.x.ai/v1/images/edits

// multipart or JSON per docs.x.ai Imagine API
// - prompt: edit instruction
// - image / images: up to 3 references
// Use for wardrobe fix, lighting match, identity-preserving refine`,
        response: `{
  "data": [
    { "url": "https://…" }
  ]
}`,
        notes: [
          "Ideal for plate polish before video spend.",
          "Keep identity locks in the edit prompt when Character DNA is required.",
        ],
      },
    ],
  },
  {
    id: "imagine-video",
    title: "Imagine — video",
    intro:
      "Async video. Published list from ~$0.05–$0.07 per second depending on resolution.",
    endpoints: [
      {
        id: "video-start",
        method: "POST",
        path: "/v1/videos (async start)",
        title: "Start video generation",
        summary: "Kick off grok-imagine-video; returns a request id to poll.",
        request: `// Model: grok-imagine-video
// Resolutions: 480p (list ~$0.05/s) | 720p (list ~$0.07/s) | 1080p (see docs)
// Duration: up to ~15 seconds
// Flow: POST start → poll status with returned id → download result

{
  "model": "grok-imagine-video",
  "prompt": "Slow push-in on rain-slick neon alley, cinematic motion",
  "duration": 6
}`,
        response: `{
  "request_id": "req_…",
  "status": "pending"
}`,
        notes: [
          "6s @ 720p ≈ $0.42 at list rates — far more than a still.",
          "Never poll in a tight loop from the client with the API key.",
          "Prefer stills + locked plates before hero video spend.",
        ],
      },
      {
        id: "video-poll",
        method: "GET",
        path: "/v1/videos/{request_id}",
        title: "Poll video job",
        summary: "Check status until complete; then fetch the clip URL.",
        request: `GET https://api.x.ai/v1/…/{request_id}
Authorization: Bearer $XAI_API_KEY`,
        response: `{
  "status": "completed" | "pending" | "failed",
  "url": "https://…/clip.mp4"
}`,
        notes: [
          "Exact paths and fields: docs.x.ai → Imagine Video.",
          "Retry failed jobs at most once.",
        ],
      },
    ],
  },
  {
    id: "voice",
    title: "Voice",
    intro:
      "Text-to-speech and related voice APIs. Return audio bytes from the server — never stream the key to the browser.",
    endpoints: [
      {
        id: "tts",
        method: "POST",
        path: "/v1/tts",
        title: "Text to speech",
        summary: "Turn narration into audio. List ~$15 per 1M characters.",
        request: `POST https://api.x.ai/v1/tts

{
  "text": "Night falls on the alley. She does not look back.",
  "voice_id": "eve"
}`,
        response: `// Binary audio body (e.g. audio/mpeg)
// Serve via your server function as base64 or a temporary URL`,
        notes: [
          "Default voice_id example: eve.",
          "List voices: GET /v1/tts/voices (custom voices supported).",
          "Transcription (STT) also available — see docs.x.ai Voice API.",
        ],
      },
      {
        id: "tts-voices",
        method: "GET",
        path: "/v1/tts/voices",
        title: "List voices",
        summary: "Enumerate available and custom TTS voices.",
        request: `GET https://api.x.ai/v1/tts/voices
Authorization: Bearer $XAI_API_KEY`,
        response: `{
  "voices": [
    { "voice_id": "eve", "name": "Eve" }
  ]
}`,
      },
    ],
  },
  {
    id: "studio-bridge",
    title: "Studio bridge",
    intro:
      "How Cinematic Studio chat activations map onto API calls when you productize a workflow in an app.",
    endpoints: [
      {
        id: "bridge-prompt-master",
        method: "POST",
        path: "chat → images",
        title: "Prompt Master → Imagine still",
        summary: "LLM writes the packet; images API renders the plate.",
        request: `// 1) Chat: craft cinematic prompt (grok-4.5)
// 2) Images: POST /v1/images/generations with that prompt
// 3) Optional edit: POST /v1/images/edits for plate lock

{
  "pipeline": ["chat.completions", "images.generations"],
  "models": ["grok-4.5", "grok-imagine-image-quality"]
}`,
        notes: [
          "Keep DNA inject text inside the image prompt string.",
          "Do not auto-chain video until plate is approved by the user.",
        ],
      },
      {
        id: "bridge-sequence",
        method: "POST",
        path: "images → video",
        title: "Locked plate → video",
        summary: "After still approval, start async video from prompt (and refs when supported).",
        request: `{
  "plate_url": "https://…/locked-still.png",
  "video": {
    "model": "grok-imagine-video",
    "prompt": "Extend motion: slow push-in, rain continuity",
    "duration": 6
  }
}`,
        notes: [
          "Quota: video seconds cost more than stills — hero-first order.",
          "User button press required for each expensive generation.",
        ],
      },
    ],
  },
];

export const API_STATUS_CODES = [
  { code: "200", meaning: "Success — parse JSON or audio bytes as documented" },
  { code: "400", meaning: "Bad request — fix body/parameters" },
  { code: "401", meaning: "Unauthorized — missing or invalid API key" },
  { code: "429", meaning: "Rate limited or quota pressure — back off" },
  { code: "5xx", meaning: "Server error — retry at most once, then surface" },
  { code: "pending", meaning: "Async video job still running — keep polling" },
  { code: "completed", meaning: "Async video ready — fetch URL" },
  { code: "failed", meaning: "Async job failed — show error, optional single retry" },
];

export const API_ERRORS = [
  {
    error: "AI_NOT_AVAILABLE",
    fix: "XAI_API_KEY missing — show friendly empty state; do not crash.",
  },
  {
    error: "KEY_EXPOSED_TO_CLIENT",
    fix: "Move fetch into createServerFn; never use VITE_ for the secret.",
  },
  {
    error: "SPEND_ON_PAGE_LOAD",
    fix: "Remove automatic calls; require button/form submit; debounce.",
  },
  {
    error: "VIDEO_WITHOUT_PLATE_LOCK",
    fix: "Generate and approve stills first; then start video jobs.",
  },
  {
    error: "RETRY_STORM",
    fix: "On error surface message; retry at most once with backoff.",
  },
  {
    error: "UNAUTHED_PUBLIC_MEDIA",
    fix: "Gate image/video generation behind sign-in for public apps.",
  },
];

export const SPEND_RULES = [
  "Cap max_tokens; keep prompts small for visitor-facing chat.",
  "Image and especially video cost far more than chat per call.",
  "Never call in a loop, on every keystroke, or on page load.",
  "Cache or persist results instead of regenerating per visitor.",
  "Gate expensive media behind sign-in when the product allows.",
  "On API error: surface it; retry at most once.",
];
