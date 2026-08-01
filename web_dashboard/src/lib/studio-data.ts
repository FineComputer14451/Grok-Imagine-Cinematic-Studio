export type ShotStatus = "ready" | "rendering" | "queued" | "failed" | "draft";
export type AspectRatio = "16:9" | "9:16" | "1:1" | "2.39:1" | "4:3";
export type OutputMode = "image" | "video" | "storyboard";
export type ModelTier = "imagine" | "imagine-pro" | "cinematic";
export type DensityMode = "compact" | "ops" | "full";
export type GateStatus = "ready" | "hold" | "warn" | "na";

export interface Shot {
  id: string;
  title: string;
  prompt: string;
  projectId: string;
  status: ShotStatus;
  mode: OutputMode;
  aspect: AspectRatio;
  model: ModelTier;
  duration?: number;
  take: number;
  frame: string;
  createdAt: string;
  seed: number;
  camera: string;
  lens: string;
  grade: string;
}

export interface Project {
  id: string;
  name: string;
  description: string;
  shotCount: number;
  updatedAt: string;
  status: "active" | "archived" | "locked";
  color: string;
  hasBible: boolean;
}

export interface QueueItem {
  id: string;
  shotId: string;
  title: string;
  progress: number;
  etaSeconds: number;
  stage: string;
  priority: "normal" | "high" | "rush";
}

export interface UsagePoint {
  day: string;
  images: number;
  videos: number;
  credits: number;
}

export interface CharacterDNA {
  id: string;
  name: string;
  role: string;
  locked: boolean;
  driftScore: number;
  traits: string[];
  looks: string;
  projectId: string;
  updatedAt: string;
}

export interface Sequence {
  id: string;
  name: string;
  projectId: string;
  clips: number;
  durationSec: number;
  status: "draft" | "shooting" | "qa" | "color" | "polish" | "ready";
  chainQa: "pass" | "hold" | "pending";
  polishPass: boolean;
  deliverPass: boolean;
  identityLock: boolean;
}

export interface Specialist {
  id: string;
  name: string;
  activation: string;
  status: "idle" | "active" | "standby";
  focus: string;
}

export interface AttentionItem {
  id: string;
  severity: "critical" | "warn" | "info";
  message: string;
}

export interface ReadinessGate {
  id: string;
  label: string;
  status: GateStatus;
  detail: string;
}

export const STUDIO_VERSION = "3.8.9";
export const ACTIVATION = "Activate Grok Imagine Cinematic Studio v3.8.9";

export const PROJECTS: Project[] = [
  {
    id: "p-noir",
    name: "Neon Harbor",
    description: "Rain-slicked coastal noir, night exteriors",
    shotCount: 24,
    updatedAt: "2026-07-31T18:20:00Z",
    status: "active",
    color: "#3f3f46",
    hasBible: true,
  },
  {
    id: "p-desert",
    name: "Salt Flat Odyssey",
    description: "Wide desert vistas, golden hour plates",
    shotCount: 18,
    updatedAt: "2026-07-30T14:05:00Z",
    status: "active",
    color: "#52525b",
    hasBible: true,
  },
  {
    id: "p-orbital",
    name: "Orbital Echo",
    description: "Zero-g interiors, soft practicals",
    shotCount: 31,
    updatedAt: "2026-07-29T09:40:00Z",
    status: "locked",
    color: "#27272a",
    hasBible: true,
  },
  {
    id: "p-forest",
    name: "Moss Archive",
    description: "Ancient woodland, volumetric dawn light",
    shotCount: 12,
    updatedAt: "2026-07-28T21:15:00Z",
    status: "active",
    color: "#3f3f46",
    hasBible: false,
  },
];

export const CHARACTERS: CharacterDNA[] = [
  {
    id: "dna-1",
    name: "Mira Vale",
    role: "Lead · Neon Harbor",
    locked: true,
    driftScore: 0.04,
    traits: ["ash-brown hair", "scar over left brow", "cool olive skin"],
    looks: "Early 30s, sharp jaw, understated trench silhouette, low-key night grade",
    projectId: "p-noir",
    updatedAt: "2026-07-31T12:00:00Z",
  },
  {
    id: "dna-2",
    name: "Kade Renn",
    role: "Support · Neon Harbor",
    locked: true,
    driftScore: 0.09,
    traits: ["silver temples", "weathered hands", "steel-blue eyes"],
    looks: "50s dockworker frame, worn leather, wet-street reflections",
    projectId: "p-noir",
    updatedAt: "2026-07-30T16:20:00Z",
  },
  {
    id: "dna-3",
    name: "Sol Arden",
    role: "Lead · Salt Flat Odyssey",
    locked: false,
    driftScore: 0.22,
    traits: ["sun-bleached hair", "dust freckles", "lean build"],
    looks: "Late 20s traveler, linen layers, golden-hour rim light",
    projectId: "p-desert",
    updatedAt: "2026-07-30T10:00:00Z",
  },
  {
    id: "dna-4",
    name: "Unit 7",
    role: "Lead · Orbital Echo",
    locked: true,
    driftScore: 0.02,
    traits: ["smooth composite skin", "iris LED ring", "neutral affect"],
    looks: "Androgynous android, cool steel palette, soft practical LEDs",
    projectId: "p-orbital",
    updatedAt: "2026-07-29T08:00:00Z",
  },
];

export const SEQUENCES: Sequence[] = [
  {
    id: "seq-1",
    name: "Harbor approach",
    projectId: "p-noir",
    clips: 6,
    durationSec: 42,
    status: "polish",
    chainQa: "pass",
    polishPass: true,
    deliverPass: false,
    identityLock: true,
  },
  {
    id: "seq-2",
    name: "Alley confrontation",
    projectId: "p-noir",
    clips: 4,
    durationSec: 28,
    status: "qa",
    chainQa: "hold",
    polishPass: false,
    deliverPass: false,
    identityLock: true,
  },
  {
    id: "seq-3",
    name: "Salt flats establish",
    projectId: "p-desert",
    clips: 3,
    durationSec: 18,
    status: "color",
    chainQa: "pass",
    polishPass: false,
    deliverPass: false,
    identityLock: false,
  },
  {
    id: "seq-4",
    name: "Corridor drift",
    projectId: "p-orbital",
    clips: 5,
    durationSec: 36,
    status: "shooting",
    chainQa: "pending",
    polishPass: false,
    deliverPass: false,
    identityLock: true,
  },
];

export const SPECIALISTS: Specialist[] = [
  {
    id: "studio-director",
    name: "Studio Director",
    activation: "ACTIVATE STUDIO_DIRECTOR",
    status: "active",
    focus: "Orchestration & handoffs",
  },
  {
    id: "identity-lock",
    name: "Identity Lock",
    activation: "ACTIVATE IDENTITY_LOCK",
    status: "active",
    focus: "DNA continuity",
  },
  {
    id: "prompt-master",
    name: "Imagine Prompt Master",
    activation: "ACTIVATE IMAGINE_PROMPT_MASTER",
    status: "standby",
    focus: "1.5 plate language",
  },
  {
    id: "dop",
    name: "Director of Photography",
    activation: "ACTIVATE DOP",
    status: "standby",
    focus: "Light & camera",
  },
  {
    id: "sequence",
    name: "Sequence Director",
    activation: "ACTIVATE SEQUENCE_DIRECTOR",
    status: "active",
    focus: "Long-form stitch",
  },
  {
    id: "qa",
    name: "QA Guardian",
    activation: "ACTIVATE QA_GUARDIAN",
    status: "active",
    focus: "16-point + chain QA",
  },
  {
    id: "quota",
    name: "Quota Optimizer",
    activation: "ACTIVATE WORKFLOW_OPTIMIZER",
    status: "standby",
    focus: "Spend & risk",
  },
  {
    id: "polish",
    name: "AI Polish Director",
    activation: "ACTIVATE AI_POLISH_DIRECTOR",
    status: "idle",
    focus: "Upscale & delivery",
  },
];

export const ATTENTION: AttentionItem[] = [
  {
    id: "a1",
    severity: "critical",
    message: "Sequence “Alley confrontation” chain QA holds — 1 no-go clip before handoff",
  },
  {
    id: "a2",
    severity: "warn",
    message: "Sol Arden DNA unlocked · drift 0.22 — lock before principal plates",
  },
  {
    id: "a3",
    severity: "warn",
    message: "Moss Archive has no Production Bible — create before sequence init",
  },
  {
    id: "a4",
    severity: "info",
    message: "Quota cascade burn 1.15× — soft cap 82% for the session",
  },
];

export const READINESS: ReadinessGate[] = [
  {
    id: "overall",
    label: "Overall",
    status: "hold",
    detail: "HOLD · fix chain QA before video spend",
  },
  {
    id: "identity",
    label: "Identity",
    status: "ready",
    detail: "3/4 locked · mean drift 0.09",
  },
  {
    id: "chain",
    label: "Chain QA",
    status: "hold",
    detail: "1 sequence with no-go",
  },
  {
    id: "plate",
    label: "Plate / motion",
    status: "warn",
    detail: "4 plates ok · 2 motion briefs pending",
  },
  {
    id: "spend",
    label: "Spend gate",
    status: "ready",
    detail: "Budget remaining within soft cap",
  },
  {
    id: "delivery",
    label: "Delivery",
    status: "hold",
    detail: "0 sequences deliver-pass",
  },
];

export const SHOTS: Shot[] = [
  {
    id: "s-001",
    title: "Harbor approach — wide",
    prompt:
      "Cinematic wide shot of a rain-soaked harbor at night, neon reflections on wet asphalt, distant freighter lights, anamorphic lens flares, shallow atmospheric haze",
    projectId: "p-noir",
    status: "ready",
    mode: "image",
    aspect: "2.39:1",
    model: "cinematic",
    take: 3,
    frame: "shot-a",
    createdAt: "2026-07-31T17:40:00Z",
    seed: 482910,
    camera: "Arri Alexa 65",
    lens: "40mm anamorphic",
    grade: "Teal-ink night",
  },
  {
    id: "s-002",
    title: "Protagonist silhouette",
    prompt:
      "Medium silhouette of a figure under a streetlamp, trench coat, rain particles catching light, film grain, restrained contrast",
    projectId: "p-noir",
    status: "ready",
    mode: "image",
    aspect: "16:9",
    model: "imagine-pro",
    take: 5,
    frame: "shot-b",
    createdAt: "2026-07-31T16:10:00Z",
    seed: 119284,
    camera: "Sony Venice",
    lens: "50mm T1.4",
    grade: "Low-key noir",
  },
  {
    id: "s-003",
    title: "Salt flats — establishing",
    prompt:
      "Ultra-wide establishing shot of endless salt flats at golden hour, lone vehicle mid-frame, heat shimmer, dust atmosphere, IMAX scale",
    projectId: "p-desert",
    status: "ready",
    mode: "image",
    aspect: "2.39:1",
    model: "cinematic",
    take: 2,
    frame: "shot-c",
    createdAt: "2026-07-30T13:22:00Z",
    seed: 778201,
    camera: "IMAX 65mm",
    lens: "24mm",
    grade: "Warm desert bleach",
  },
  {
    id: "s-004",
    title: "Corridor drift",
    prompt:
      "Slow push through a zero-gravity corridor, soft practical LEDs, floating cable strands, cool steel surfaces, subtle camera float",
    projectId: "p-orbital",
    status: "rendering",
    mode: "video",
    aspect: "16:9",
    model: "cinematic",
    duration: 6,
    take: 1,
    frame: "shot-d",
    createdAt: "2026-07-31T18:05:00Z",
    seed: 330194,
    camera: "Virtual RED",
    lens: "35mm",
    grade: "Cool steel",
  },
  {
    id: "s-005",
    title: "Moss canopy — tracking",
    prompt:
      "Steadicam tracking through ancient moss-covered forest, volumetric god rays, wet ferns, soft depth of field falloff",
    projectId: "p-forest",
    status: "queued",
    mode: "video",
    aspect: "16:9",
    model: "imagine-pro",
    duration: 10,
    take: 1,
    frame: "shot-e",
    createdAt: "2026-07-31T18:12:00Z",
    seed: 901553,
    camera: "Alexa Mini LF",
    lens: "32mm",
    grade: "Moss emerald",
  },
  {
    id: "s-006",
    title: "Title card plate",
    prompt:
      "Minimal title plate, soft vignette, film leader texture, centered negative space for typography",
    projectId: "p-noir",
    status: "draft",
    mode: "image",
    aspect: "16:9",
    model: "imagine",
    take: 1,
    frame: "shot-f",
    createdAt: "2026-07-31T12:00:00Z",
    seed: 44102,
    camera: "Still",
    lens: "—",
    grade: "Neutral",
  },
  {
    id: "s-007",
    title: "Engine room detail",
    prompt:
      "Macro detail of spacecraft engine housing, brushed metal, condensation beads, soft rim light, shallow DOF",
    projectId: "p-orbital",
    status: "ready",
    mode: "image",
    aspect: "1:1",
    model: "imagine-pro",
    take: 4,
    frame: "shot-d",
    createdAt: "2026-07-29T11:30:00Z",
    seed: 662018,
    camera: "Macro plate",
    lens: "100mm macro",
    grade: "Cool steel",
  },
  {
    id: "s-008",
    title: "Dust storm insert",
    prompt:
      "Handheld insert of sandstorm approaching vehicle, grit on lens, warm amber sun bleed, anamorphic squeeze",
    projectId: "p-desert",
    status: "failed",
    mode: "video",
    aspect: "2.39:1",
    model: "cinematic",
    duration: 6,
    take: 2,
    frame: "shot-c",
    createdAt: "2026-07-30T15:00:00Z",
    seed: 228811,
    camera: "Handheld",
    lens: "28mm anamorphic",
    grade: "Amber grit",
  },
];

export const QUEUE: QueueItem[] = [
  {
    id: "q-1",
    shotId: "s-004",
    title: "Corridor drift",
    progress: 68,
    etaSeconds: 42,
    stage: "Temporal upsample",
    priority: "high",
  },
  {
    id: "q-2",
    shotId: "s-005",
    title: "Moss canopy — tracking",
    progress: 12,
    etaSeconds: 180,
    stage: "Latent sample",
    priority: "normal",
  },
  {
    id: "q-3",
    shotId: "s-008",
    title: "Dust storm insert (retry)",
    progress: 0,
    etaSeconds: 240,
    stage: "Waiting",
    priority: "rush",
  },
];

export const USAGE: UsagePoint[] = [
  { day: "Mon", images: 42, videos: 6, credits: 118 },
  { day: "Tue", images: 58, videos: 9, credits: 164 },
  { day: "Wed", images: 37, videos: 4, credits: 96 },
  { day: "Thu", images: 71, videos: 12, credits: 205 },
  { day: "Fri", images: 64, videos: 11, credits: 188 },
  { day: "Sat", images: 29, videos: 3, credits: 74 },
  { day: "Sun", images: 51, videos: 8, credits: 142 },
];

export const SPEND_HISTORY = [
  { id: "sp1", label: "Corridor drift · video 1.5", credits: 48, at: "2026-07-31T18:05:00Z" },
  { id: "sp2", label: "Harbor wide · still pro", credits: 6, at: "2026-07-31T17:40:00Z" },
  { id: "sp3", label: "Silhouette · still pro", credits: 6, at: "2026-07-31T16:10:00Z" },
  { id: "sp4", label: "Salt flats · cinematic still", credits: 8, at: "2026-07-30T13:22:00Z" },
];

export const CAMERA_PRESETS = [
  "Arri Alexa 65",
  "Sony Venice",
  "IMAX 65mm",
  "RED V-Raptor",
  "Handheld 35mm",
  "Drone wide",
] as const;

export const LENS_PRESETS = [
  "24mm",
  "32mm",
  "40mm anamorphic",
  "50mm T1.4",
  "85mm",
  "100mm macro",
] as const;

export const GRADE_PRESETS = [
  "Teal-ink night",
  "Warm desert bleach",
  "Cool steel",
  "Low-key noir",
  "Neutral cinema",
  "Soft dawn",
] as const;

export const BIBLE_STAGES = [
  { id: "logline", label: "Logline", done: true },
  { id: "world", label: "World & tone", done: true },
  { id: "characters", label: "Characters", done: true },
  { id: "visual", label: "Visual language", done: true },
  { id: "pipeline", label: "Video pipeline 1.5", done: true },
  { id: "schedule", label: "Shoot schedule", done: false },
  { id: "budget", label: "Budget / quota", done: false },
  { id: "lock", label: "Bible lock", done: false },
] as const;

export const MODEL_STACK = {
  chat: "grok-4.5 cinematic",
  build: "grok-build ≥ 0.2.93",
  video: "imagine-video-1.5",
  image: "imagine-pro",
  reasoning: "high",
};

export const STATS = {
  creditsRemaining: 1840,
  creditsTotal: 2500,
  sessionSpent: 660,
  generationsToday: 51,
  queueDepth: 3,
  avgRenderSec: 38,
  successRate: 96.4,
  activeProjects: 3,
  readyShots: 5,
  coreAgents: 12,
  totalAgents: 23,
  roleCards: 23,
  skills: 52,
  riskLevel: "moderate" as const,
  tierLabel: "SuperGrok Pro · heavy",
  dailySoftCap: 900,
  cascade: "session-ledger",
  burnMultiplier: 1.15,
};
