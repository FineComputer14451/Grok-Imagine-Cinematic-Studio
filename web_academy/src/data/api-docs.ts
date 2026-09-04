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

export const IMAGINE_MIGRATION = {
  asOf: "September 2, 2026",
  effective: "November 2, 2026",
  retiring: "grok-imagine-image-quality",
  redirect: 'grok-imagine-image-2.0 with quality: "low"',
  unaffected: "grok-imagine-image (1.0)",
  title: "Imagine image-quality slug retires November 2, 2026",
  body: "The grok-imagine-image-quality slug keeps resolving after November 2, but it is served as grok-imagine-image-2.0 with quality forced to low. Pin 2.0 and quality yourself if you care about look or cost. grok-imagine-image (1.0) is unchanged. grok-imagine-image-pro already follows quality, then follows this redirect.",
  rule: "Hero stills: grok-imagine-image-2.0 + quality medium. Cheap iterate: grok-imagine-image (1.0) or 2.0 low. Do not ride the retired slug.",
  consumerNote:
    "Consumer Quality Mode on grok.com is grok-imagine-image-2.0 — not the retiring API slug grok-imagine-image-quality.",
  sourceUrl:
    "https://docs.x.ai/developers/migration/imagine-image-quality-nov-2",
} as const;

/**
 * Public xAI developer API list prices (not subscription quotas).
 * “Draft still” in studio examples means the cheaper image *model path*
 * (grok-imagine-image 1.0), not that the dollar amounts are unofficial drafts.
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
  sourceUrl: "https://docs.x.ai/developers/pricing",
  status:
    "Published developer API list prices — not “draft” rate cards. Confirm on docs.x.ai before you budget. Image-quality slug retires November 2, 2026.",
  disclaimer:
    "These are published API list prices for metered developer keys (as listed on docs.x.ai around September 2026). They are not temporary draft figures. SuperGrok / consumer app quotas are separate from API billing. Studio “snapshots” below are worked examples (~) using those list rates, not separate price tiers. Always re-check the official docs before production budgeting.",
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
        "1.0 for cheap iteration. 2.0 with an explicit quality pin for plates. The old quality slug redirects to 2.0-low on November 2, 2026.",
      rows: [
        {
          model: "grok-imagine-image",
          unit: "Output / image (1K or 2K)",
          price: "$0.02",
          note: "1.0 — draft / explore. Unchanged Nov 2.",
        },
        {
          model: "grok-imagine-image",
          unit: "Media input / image",
          price: "$0.002",
          note: "When sending reference images",
        },
        {
          model: "grok-imagine-image-2.0",
          unit: "Output / 1K · quality low",
          price: "$0.04",
          note: "Cost-match old quality. Redirect target after Nov 2.",
        },
        {
          model: "grok-imagine-image-2.0",
          unit: "Output / 2K · quality low",
          price: "$0.06",
          note: "2.0 low",
        },
        {
          model: "grok-imagine-image-2.0",
          unit: "Output / 1K · quality medium",
          price: "$0.06",
          note: "Hero stills / Identity / Polish plates",
        },
        {
          model: "grok-imagine-image-2.0",
          unit: "Output / 2K · quality medium",
          price: "$0.08",
          note: "Highest still fidelity",
        },
        {
          model: "grok-imagine-image-2.0",
          unit: "Media input / image",
          price: "$0.01",
          note: "Up to 5 edit sources. Billed per input image.",
        },
        {
          model: "grok-imagine-image-quality",
          unit: "Output / image (1K / 2K)",
          price: "$0.05 / $0.07",
          note: "Retires Nov 2 → 2.0 quality low. Do not leave in templates.",
        },
      ],
    },
    {
      id: "video",
      title: "Imagine — video",
      blurb:
        "1.0 for cheap 480/720 draft motion. 1.5 for hero clips (1080p, audio in, extend, reference-to-video). Not in the Nov 2 image-quality retirement.",
      rows: [
        {
          model: "grok-imagine-video",
          unit: "Output / second (480p)",
          price: "$0.05",
          note: "1.0 draft motion",
        },
        {
          model: "grok-imagine-video",
          unit: "Output / second (720p)",
          price: "$0.07",
          note: "1.0 draft motion",
        },
        {
          model: "grok-imagine-video",
          unit: "Media input / second",
          price: "$0.01",
          note: "Video-to-video conditioning",
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
          note: "1.5 hero path",
        },
        {
          model: "grok-imagine-video-1.5",
          unit: "Output / second (720p)",
          price: "$0.14",
          note: "1.5 hero path",
        },
        {
          model: "grok-imagine-video-1.5",
          unit: "Output / second (1080p)",
          price: "$0.25",
          note: "Delivery masters",
        },
        {
          model: "grok-imagine-video-1.5",
          unit: "Media input / image",
          price: "$0.01",
          note: "Still → clip / reference-to-video",
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
      label: "1.0 still (iteration)",
      estimate: "$0.02",
      detail: "1× grok-imagine-image @ list $0.02 — draft path, not an unofficial rate",
      kind: "example",
    },
    {
      label: "2.0 low 1K (cost-match)",
      estimate: "$0.04",
      detail: "1× grok-imagine-image-2.0 quality low @ 1K — Nov 2 redirect look",
      kind: "example",
    },
    {
      label: "2.0 medium 2K (hero)",
      estimate: "$0.08",
      detail: "1× grok-imagine-image-2.0 quality medium @ 2K — Identity / Polish plate",
      kind: "example",
    },
    {
      label: "6s clip @ 1.0 720p",
      estimate: "~$0.42",
      detail: "6 × $0.07/s list — draft motion proof",
      kind: "example",
    },
    {
      label: "6s clip @ 1.5 720p",
      estimate: "~$0.84",
      detail: "6 × $0.14/s list — hero motion after plate lock",
      kind: "example",
    },
    {
      label: "6s clip @ 1.5 1080p",
      estimate: "~$1.50",
      detail: "6 × $0.25/s list — delivery master",
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
    "Server-side integration reference for Grok chat, Imagine (image & video), and Voice. Keys are server-only — never expose XAI_API_KEY to the browser. Official source of truth: docs.x.ai. Pin grok-imagine-image-2.0 + quality; do not leave grok-imagine-image-quality in templates after November 2, 2026.",
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
          "Share without deleting: POST /v1/files/{id}/public-url · revoke: POST /v1/files/{id}/public-url/revoke (CLI: files share|unshare).",
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
      "1.0 for cheap iteration. 2.0 with quality low | medium | auto for plates. quality auto currently serves low on generation and medium on edits. Bill at the quality served. After November 2, grok-imagine-image-quality is 2.0-low.",
    endpoints: [
      {
        id: "images-generations",
        method: "POST",
        path: "/v1/images/generations",
        title: "Generate image",
        summary:
          "Pin grok-imagine-image-2.0 + quality. 1.0 stays $0.02 for drafts.",
        request: `POST https://api.x.ai/v1/images/generations

{
  "model": "grok-imagine-image-2.0",
  "prompt": "Cinematic still, rain-slick neon alley, 35mm, teal amber practicals",
  "n": 1,
  "quality": "medium",
  "aspect_ratio": "21:9",
  "resolution": "2k",
  "response_format": "url"
}

// Draft iterate: "grok-imagine-image" (list $0.02) — no quality param
// quality: "low" | "medium" | "auto"  (2.0 only)
// auto: generation → low, edits → medium
// aspect_ratio includes 21:9 and 5:2 on 2.0
// resolution: "1k" | "2k"
// n: ≤ 10
// response_format: "url" | "b64_json"`,
        response: `{
  "data": [
    { "url": "https://…" }
  ],
  "model": "grok-imagine-image-2.0"
}`,
        notes: [
          "Log the model field on the response — after Nov 2 the retired slug reports 2.0.",
          "quality exists only on grok-imagine-image-2.0. Omit → auto.",
          "Cache URLs or persist to storage — do not regenerate per page view.",
          "Gate public generation behind sign-in when possible.",
          "Do not leave grok-imagine-image-quality in activation templates.",
        ],
      },
      {
        id: "images-edits",
        method: "POST",
        path: "/v1/images/edits",
        title: "Edit image",
        summary:
          "Natural-language edits with up to 5 reference images on grok-imagine-image-2.0.",
        request: `POST https://api.x.ai/v1/images/edits

{
  "model": "grok-imagine-image-2.0",
  "prompt": "Keep identity lock. Match wardrobe and 35mm rain practicals.",
  "quality": "medium",
  "image_urls": ["https://…/plate.png", "https://…/wardrobe-ref.png"]
}

// Up to 5 source images on 2.0
// auto quality currently serves medium for edits`,
        response: `{
  "data": [
    { "url": "https://…" }
  ],
  "model": "grok-imagine-image-2.0"
}`,
        notes: [
          "Ideal for plate polish before video spend.",
          "Keep identity locks in the edit prompt when Character DNA is required.",
          "2.0 adds 21:9 / 5:2 cinematic ratios — prefer native 21:9 over a 16:9 crop.",
        ],
      },
    ],
  },
  {
    id: "imagine-video",
    title: "Imagine — video",
    intro:
      "Async video. 1.0 for cheap 480/720 proofs. 1.5 for hero motion (1080p, audio in, extend, reference-to-video). Not affected by the November 2 image-quality retirement.",
    endpoints: [
      {
        id: "video-start",
        method: "POST",
        path: "/v1/videos (async start)",
        title: "Start video generation",
        summary:
          "Kick off grok-imagine-video-1.5 (hero) or grok-imagine-video (draft); poll the request id.",
        request: `// Hero: grok-imagine-video-1.5  480p $0.08/s · 720p $0.14/s · 1080p $0.25/s
// Draft: grok-imagine-video     480p $0.05/s · 720p $0.07/s
// Duration: up to ~15 seconds on 1.5
// Flow: POST start → poll status with returned id → download result

{
  "model": "grok-imagine-video-1.5",
  "prompt": "Slow push-in on rain-slick neon alley, cinematic motion",
  "duration": 6,
  "resolution": "720p"
}`,
        response: `{
  "request_id": "req_…",
  "status": "pending"
}`,
        notes: [
          "6s @ 1.5 720p ≈ $0.84 at list — twice 1.0 720p. Lock plates first.",
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
  "models": ["grok-4.5", "grok-imagine-image-2.0"],
  "image_quality": "medium"
}`,
        notes: [
          "Keep DNA inject text inside the image prompt string.",
          "Do not auto-chain video until plate is approved by the user.",
          "Pin quality on 2.0. Consumer Quality Mode ≠ the retiring image-quality slug.",
        ],
      },
      {
        id: "bridge-sequence",
        method: "POST",
        path: "images → video",
        title: "Locked plate → video",
        summary:
          "After still approval, start async video from prompt (and refs when supported).",
        request: `{
  "plate_url": "https://…/locked-still.png",
  "video": {
    "model": "grok-imagine-video-1.5",
    "prompt": "Extend motion: slow push-in, rain continuity",
    "duration": 6,
    "resolution": "720p"
  }
}`,
        notes: [
          "Quota: 1.5 seconds cost more than 1.0 — hero-first, gates before video.",
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
    error: "RETIRED_IMAGE_QUALITY_SLUG",
    fix: "Replace grok-imagine-image-quality with grok-imagine-image-2.0 and pin quality (low | medium). After Nov 2 the old slug is 2.0-low.",
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
  "Iterate on grok-imagine-image (1.0). Hero plates on grok-imagine-image-2.0 quality medium.",
  "Pin quality on 2.0. Do not ride grok-imagine-image-quality after November 2.",
  "Never call in a loop, on every keystroke, or on page load.",
  "Cache or persist results instead of regenerating per visitor.",
  "Gate expensive media behind sign-in when the product allows.",
  "On API error: surface it; retry at most once.",
];
