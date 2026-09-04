export type ApiEndpoint = {
  id: string;
  method: "GET" | "POST" | "DELETE";
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
  asOf: "September 2026",
  source: "x.ai/api · docs.x.ai",
  sourceUrl: "https://docs.x.ai",
  status:
    "Published developer API list prices — not “draft” rate cards. Confirm on docs.x.ai before you budget.",
  disclaimer:
    "These are published API list prices for metered developer keys (as listed on x.ai/api and docs.x.ai around September 2026). They are not temporary draft figures. SuperGrok / consumer app quotas are separate from API billing. Studio “snapshots” below are worked examples (~) using those list rates, not separate price tiers. Always re-check the official docs before production budgeting.",
  groups: [
    {
      id: "chat",
      title: "Chat / LLM",
      blurb: "Published list rates per million tokens.",
      rows: [
        {
          model: "grok-4.6",
          unit: "Input / 1M tokens",
          price: "$2.00",
          note: "List price",
        },
        {
          model: "grok-4.6",
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
        "Image 1.0 for cheap iteration; Image 2.0 for hero stills (`quality` low | medium | auto). The `grok-imagine-image-quality` slug retires 2026-11-02.",
      rows: [
        {
          model: "grok-imagine-image",
          unit: "Output / image (1K or 2K)",
          price: "$0.02",
          note: "Image 1.0 — cheaper iteration path",
        },
        {
          model: "grok-imagine-image",
          unit: "Media input / image",
          price: "$0.002",
          note: "When sending reference images",
        },
        {
          model: "grok-imagine-image-2.0",
          unit: "Output / image (1K, quality=low)",
          price: "$0.04",
          note: "List / auto generate. Retired quality slug rewrites here.",
        },
        {
          model: "grok-imagine-image-2.0",
          unit: "Output / image (1K, quality=medium)",
          price: "$0.06",
          note: "Hero / Quality Mode plates",
        },
        {
          model: "grok-imagine-image-2.0",
          unit: "Output / image (2K, quality=low)",
          price: "$0.06",
          note: "2K draft / auto generate",
        },
        {
          model: "grok-imagine-image-2.0",
          unit: "Output / image (2K, quality=medium)",
          price: "$0.08",
          note: "Hero 2K",
        },
        {
          model: "grok-imagine-image-2.0",
          unit: "Media input / image",
          price: "$0.01",
          note: "When sending reference images",
        },
      ],
    },
    {
      id: "video",
      title: "Imagine — video",
      blurb:
        "Published per-second list rates by resolution. Video is 1.0 / 1.5 only — there is no Imagine Video 2.0 (2.0 is Image only).",
      rows: [
        {
          model: "grok-imagine-video",
          unit: "Output / second (480p)",
          price: "$0.05",
          note: "Video 1.0 list",
        },
        {
          model: "grok-imagine-video",
          unit: "Output / second (720p)",
          price: "$0.07",
          note: "Video 1.0 list",
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
        {
          model: "grok-imagine-video-1.5",
          unit: "Output / second (480p)",
          price: "$0.08",
          note: "Video 1.5 native audio / physics — no Video 2.0",
        },
        {
          model: "grok-imagine-video-1.5",
          unit: "Output / second (720p)",
          price: "$0.14",
          note: "Video 1.5 native audio / physics — no Video 2.0",
        },
        {
          model: "grok-imagine-video-1.5",
          unit: "Output / second (1080p)",
          price: "$0.25",
          note: "Video 1.5 hero — no Video 2.0",
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
      label: "Hero still 1K (Image 2.0 medium)",
      estimate: "$0.06",
      detail: "1× grok-imagine-image-2.0 quality=medium @ 1K $0.06",
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
      detail: "Small grok-4.6 call with capped max_tokens — illustrative",
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
        model: "grok-4.6",
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
          "Default chat model: grok-4.6 unless the user asks otherwise.",
          "OpenAI SDKs work with base_url https://api.x.ai/v1.",
          "Prefer POST /v1/responses for new chat work; /v1/chat/completions remains compatible.",
        ],
      },
    ],
  },
  {
    id: "files",
    title: "Files",
    intro:
      "Private storage for Imagine inputs (and chat attachments). Upload once, then pass file_id instead of re-sending bytes. Max 50 MB. Official: docs.x.ai → Files API.",
    endpoints: [
      {
        id: "files-list",
        method: "GET",
        path: "/v1/files",
        title: "List files",
        summary:
          "Paginated list for the authenticated team. Pass pagination_token for the next page.",
        request: `GET https://api.x.ai/v1/files?limit=20
Authorization: Bearer $XAI_API_KEY

// Query: limit, order (asc|desc), sort_by (created_at|filename|size),
//        pagination_token, filter (AIP-160)`,
        response: `{
  "data": [
    {
      "id": "file_a128090d-f0c9-4873-bd84-e499777e7417",
      "object": "file",
      "bytes": 12345,
      "created_at": 1762345678,
      "expires_at": null,
      "filename": "plate.png",
      "purpose": "assistants"
    }
  ],
  "pagination_token": "file_a128090d-f0c9-4873-bd84-e499777e7417"
}`,
        notes: [
          "End of list: data.length < limit.",
          "purpose is accepted for OpenAI SDK compatibility; xAI does not enforce it.",
        ],
      },
      {
        id: "files-get",
        method: "GET",
        path: "/v1/files/{id}",
        title: "Get file metadata",
        summary:
          "Retrieve one file by id. 404 if missing, deleted, or past expires_at.",
        request: `GET https://api.x.ai/v1/files/{id}
Authorization: Bearer $XAI_API_KEY`,
        response: `{
  "id": "file_a128090d-f0c9-4873-bd84-e499777e7417",
  "object": "file",
  "bytes": 12345,
  "created_at": 1762345678,
  "expires_at": null,
  "filename": "plate.png"
}`,
      },
      {
        id: "files-upload",
        method: "POST",
        path: "/v1/files",
        title: "Upload file",
        summary:
          "Multipart upload. Returns id for Imagine image/video inputs. Files persist until delete or expires_after.",
        request: `POST https://api.x.ai/v1/files
Authorization: Bearer $XAI_API_KEY
Content-Type: multipart/form-data

# expires_after MUST appear before the file part (400 if reversed)
# expires_after: 3600–2592000 seconds (1 hour–30 days); omit = no expiry

curl -X POST https://api.x.ai/v1/files \\
  -H "Authorization: Bearer $XAI_API_KEY" \\
  -F expires_after=86400 \\
  -F purpose=assistants \\
  -F file="@locked-plate.png"`,
        response: `{
  "id": "file_a128090d-f0c9-4873-bd84-e499777e7417",
  "object": "file",
  "bytes": 12345,
  "created_at": 1762345678,
  "expires_at": 1762432078,
  "filename": "locked-plate.png"
}`,
        notes: [
          "Maximum 50 MB.",
          "Imagine accepts file_id anywhere a public URL or data URI is allowed (edits, i2v).",
          "Chunked upload exists (POST /v1/files:initialize + :uploadChunks) for large files — see docs.x.ai.",
        ],
      },
      {
        id: "files-delete",
        method: "DELETE",
        path: "/v1/files/{id}",
        title: "Delete file",
        summary:
          "Remove storage. The id no longer lists, downloads, or attaches.",
        request: `DELETE https://api.x.ai/v1/files/{id}
Authorization: Bearer $XAI_API_KEY`,
        response: `{
  "id": "file_a128090d-f0c9-4873-bd84-e499777e7417",
  "deleted": true
}`,
        notes: [
          "Use after a production wrap or when a plate is superseded.",
          "Do not log file bytes or API keys.",
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
          "OpenAI-compatible chat. grok-4.6 list: $2 input / $6 output per 1M tokens.",
        request: `POST https://api.x.ai/v1/chat/completions

{
  "model": "grok-4.6",
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
      "Image 1.0 for cheap iteration; Image 2.0 for hero stills (`quality` low | medium | auto). Dollar amounts are published list prices.",
    endpoints: [
      {
        id: "images-generations",
        method: "POST",
        path: "/v1/images/generations",
        title: "Generate image",
        summary:
          "1.0 list ~$0.02/img; 2.0 1K low $0.04 / medium $0.06. Do not send grok-imagine-image-quality.",
        request: `POST https://api.x.ai/v1/images/generations

{
  "model": "grok-imagine-image-2.0",
  "prompt": "Cinematic still, rain-slick neon alley, 35mm, teal amber practicals",
  "n": 1,
  "resolution": "1k",
  "quality": "medium",
  "response_format": "url"
}

// Cheaper iteration: "grok-imagine-image" (list ~$0.02)
// quality (2.0 only): "low" | "medium" | "auto"
// resolution: "1k" | "2k"
// n: ≤ 10
// response_format: "url" | "b64_json"`,
        response: `{
  "data": [
    { "url": "https://…" }
  ]
}`,
        notes: [
          "Image 2.0 costs more than Image 1.0 (`grok-imagine-image`).",
          "Cache URLs or persist via Files — do not regenerate per page view.",
          "Opt-in storage_options.filename persists the still as a Files file_id (CLI: --store-as).",
          "Gate public generation behind sign-in when possible.",
        ],
      },
      {
        id: "images-edits",
        method: "POST",
        path: "/v1/images/edits",
        title: "Edit image",
        summary:
          "JSON body (not OpenAI multipart). Source: public URL, data URI, or file_id. Image 2.0: up to 5 refs; Image 1.0: 3.",
        request: `POST https://api.x.ai/v1/images/edits
Content-Type: application/json

// Single source
{
  "model": "grok-imagine-image-2.0",
  "prompt": "Wardrobe lock: same coat, cooler practicals, identity preserved",
  "image": {
    "type": "image_url",
    "url": "https://…/locked-plate.png"
  },
  "quality": "medium"
}

// Or Files API: { "file_id": "file_…" }  (no type/url)
// Multi-ref (2.0, up to 5): "images": [ {…}, {…} ]
// Mix url / data URI / file_id in one images[] request
// OpenAI SDK images.edit() multipart is NOT supported`,
        response: `{
  "data": [
    { "url": "https://…" }
  ]
}`,
        notes: [
          "Ideal for plate polish before video spend.",
          "Keep identity locks in the edit prompt when Character DNA is required.",
          "Do not send grok-imagine-image-quality — pin grok-imagine-image-2.0.",
        ],
      },
    ],
  },
  {
    id: "imagine-video",
    title: "Imagine — video",
    intro:
      "Async video. POST returns request_id only — poll GET until done. Video 1.0 list ~$0.05–$0.07/s; Video 1.5 720p $0.14/s · 1080p $0.25/s. There is no Imagine Video 2.0 (2.0 is Image only).",
    endpoints: [
      {
        id: "video-start",
        method: "POST",
        path: "/v1/videos/generations",
        title: "Start video generation",
        summary:
          "Text-to-video, image-to-video (image url or file_id), or reference-to-video. Returns request_id for polling.",
        request: `POST https://api.x.ai/v1/videos/generations
Content-Type: application/json

{
  "model": "grok-imagine-video",
  "prompt": "Slow push-in on rain-slick neon alley, cinematic motion",
  "duration": 6,
  "resolution": "720p",
  "image": {
    "url": "https://…/locked-plate.png"
  }
}

// i2v from Files: "image": { "file_id": "file_…" }
// t2v: omit image
// r2v (1.5): reference_images[] and/or reference_audios[] — not with image (400)
// duration: 1–15 (default 8). Also accepts "seconds" for OpenAI compat.`,
        response: `{
  "request_id": "a3d1008e-4544-40d4-d075-11527e794e4a"
}`,
        notes: [
          "6s @ 720p Video 1.0 ≈ $0.42 at list rates — far more than a still.",
          "Prefer stills + locked plates before hero video spend.",
          "Studio also has POST /v1/videos/edits and /v1/videos/extensions (Video 1.0 only) — not required for this generate → poll loop.",
        ],
      },
      {
        id: "video-poll",
        method: "GET",
        path: "/v1/videos/{request_id}",
        title: "Poll video job",
        summary:
          "Deferred result. status is pending | done | failed | expired. URL is on video.url when done.",
        request: `GET https://api.x.ai/v1/videos/{request_id}
Authorization: Bearer $XAI_API_KEY`,
        response: `{
  "status": "done",
  "progress": 100,
  "model": "grok-imagine-video",
  "video": {
    "url": "https://vidgen.x.ai/…/clip.mp4",
    "duration": 6,
    "respect_moderation": true
  }
}

// pending: progress 0–99, video omitted
// failed: error.code + error.message
// expired: job no longer retrievable`,
        notes: [
          "Poll from the server with backoff (studio default ~5s). Never tight-loop from the browser with the API key.",
          "Retry failed jobs at most once.",
          "Terminal statuses: done | failed | expired.",
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
        request: `// 1) Chat: craft cinematic prompt (grok-4.6)
// 2) Images: POST /v1/images/generations with that prompt
// 3) Optional edit: POST /v1/images/edits for plate lock

{
  "pipeline": ["chat.completions", "images.generations"],
  "models": ["grok-4.6", "grok-imagine-image-2.0"]
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
  "plate": { "file_id": "file_…" },
  "video": {
    "model": "grok-imagine-video",
    "prompt": "Extend motion: slow push-in, rain continuity",
    "duration": 6
  }
}

// 1) POST /v1/files  → file_id
// 2) POST /v1/images/edits  (optional plate lock)
// 3) POST /v1/videos/generations  with image.file_id
// 4) GET  /v1/videos/{request_id}  until status=done`,
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
  { code: "done", meaning: "Async video ready — read video.url" },
  { code: "failed", meaning: "Async job failed — show error, optional single retry" },
  { code: "expired", meaning: "Deferred video job no longer retrievable" },
  { code: "404", meaning: "File or job missing (deleted, expired, or unknown id)" },
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
