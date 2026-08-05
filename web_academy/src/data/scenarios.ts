export type Scenario = {
  id: string;
  title: string;
  tagline: string;
  tier: 1 | 2 | 3;
  minutes: string;
  genre: string;
  deliverable: string;
  budgetHint: string;
  agents: string[];
  dnaPreset?: "noir" | "gothic";
  steps: string[];
  activation: string;
  tips: string[];
};

export const SCENARIOS: Scenario[] = [
  {
    id: "first-still",
    title: "First cinematic still",
    tagline: "One agent. One plate. Learn the Ultimate Template.",
    tier: 1,
    minutes: "5–10 min",
    genre: "Any · stills",
    deliverable: "1 paste-ready Imagine still + negatives",
    budgetHint: "~$0.02–$0.07 (1 standard or quality still)",
    agents: ["Imagine Prompt Master"],
    steps: [
      "Open Prompt lab and pick a preset (or write your own fields).",
      "Assemble subject → environment → lighting → lens → mood.",
      "Copy into Grok Imagine; iterate on standard stills first.",
      "Optional: Enhance with Grok once (capped).",
    ],
    activation: `ACTIVATE IMAGINE_PROMPT_MASTER

Deliver: one cinematic still prompt (subject → environment → lighting → lens → mood).
Negatives: text, watermark, extra limbs.
Output format: paste-ready Imagine packet only.`,
    tips: [
      "Stay Tier 1 until plate quality is consistent.",
      "Use standard image model for cheap iteration.",
    ],
  },
  {
    id: "three-shot-alley",
    title: "Three-shot neon alley",
    tagline: "Director locks brief; Prompt Master writes three related stills.",
    tier: 2,
    minutes: "15–25 min",
    genre: "Neon noir · stills",
    deliverable: "3 continuity-aware still prompts + shared negatives",
    budgetHint: "~$0.06–$0.21 (3 stills) + tiny chat cost",
    agents: ["Studio Director", "Imagine Prompt Master"],
    dnaPreset: "noir",
    steps: [
      "Load Neon courier DNA (DNA page) and copy inject.",
      "Activate Director → lock tone, wardrobe, 3-shot list.",
      "Prompt Master: one packet per shot with DNA inject on top.",
      "Generate stills; only promote hero plates to quality model.",
    ],
    activation: `ACTIVATE STUDIO_DIRECTOR
Then: ACTIVATE IMAGINE_PROMPT_MASTER

Project: 3-shot neon alley sequence
Constraints: same wardrobe, adult fictional lead, shared lighting language.
Director locks: brief + shot list (wide / medium / close).
Prompt Master: 3 Imagine packets with CHARACTER_DNA inject prepended.
Gate: identity + framing before any video.`,
    tips: [
      "Same DNA on every shot — no wardrobe freestyle.",
      "Budget calculator: 3 standard stills + 15% buffer.",
    ],
  },
  {
    id: "dna-locked-pair",
    title: "DNA-locked pair",
    tagline: "Identity Lock first — two angles, one face.",
    tier: 3,
    minutes: "20–30 min",
    genre: "Character study · stills",
    deliverable: "Locked DNA + 2 matching plates (different camera)",
    budgetHint: "~$0.04–$0.14 stills · chat for DNA refine",
    agents: [
      "Identity Lock Specialist",
      "Imagine Prompt Master",
      "Imagine Agent Mode Handoff",
    ],
    dnaPreset: "gothic",
    steps: [
      "Build or load Candle hall DNA; copy inject + activation pack.",
      "Run Identity Lock → confirm face/wardrobe rules.",
      "Prompt Master: shot A wide, shot B close — same inject.",
      "Handoff validates packets before spend.",
    ],
    activation: `ACTIVATE IDENTITY_LOCK
Then: ACTIVATE IMAGINE_PROMPT_MASTER
Then: ACTIVATE IMAGINE_HANDOFF

Task: lock lead Character DNA, produce 2 consistent stills (wide + close).
Rules: same face, wardrobe, age; no wardrobe change without Transform Track.
Handoff must pass identity gate before any video spend.`,
    tips: [
      "If face drifts, strengthen face_lock — do not add random wardrobe.",
      "Transform Track only when change is intentional.",
    ],
  },
  {
    id: "plate-to-six",
    title: "Locked plate → 6s clip",
    tagline: "Approve a still, then spend on a short hero video.",
    tier: 3,
    minutes: "25–40 min",
    genre: "Micro-motion · video",
    deliverable: "1 locked plate + 6s 720p clip",
    budgetHint: "~$0.02–$0.07 still + ~$0.42 video (720p list)",
    agents: [
      "Imagine Prompt Master",
      "Imagine Agent Mode Handoff",
      "QA Guardian",
    ],
    dnaPreset: "noir",
    steps: [
      "Generate standard stills with DNA until plate is locked.",
      "Optional: quality still for hero plate only.",
      "Handoff: plate_status locked + motion vector (slow push-in).",
      "Generate 6s video; QA Go before any extend.",
    ],
    activation: `ACTIVATE IMAGINE_PROMPT_MASTER
ACTIVATE IMAGINE_HANDOFF
ACTIVATE QA_GUARDIAN

Mode: locked plate → short video
Plate: approved still only (strict_plate true)
Motion: slow push-in, rain continuity
Duration: 6s · prefer video path with physics if needed
Rule: No video until plate lock. QA before extend.`,
    tips: [
      "Video seconds dominate cost — see Budget calculator.",
      "Never skip plate lock to “save a step.”",
    ],
  },
  {
    id: "extend-chain-mini",
    title: "Mini extend chain",
    tagline: "Two clips: clip N then N+1 from LAST_FRAME_RECAP.",
    tier: 3,
    minutes: "40–60 min",
    genre: "Sequence · video",
    deliverable: "2× ~6s clips with continuity gate",
    budgetHint: "~$0.84+ video @ 720p (2×6s) + stills for repairs",
    agents: [
      "Sequence Director",
      "Multi-Clip Continuity Orchestrator",
      "Imagine Agent Mode Handoff",
      "QA Guardian",
    ],
    dnaPreset: "noir",
    steps: [
      "Start from approved clip N last frame + DNA inject.",
      "Write LAST_FRAME_RECAP (pose, light, props, emotion).",
      "Sequence Director plans N+1; Continuity checks wardrobe/props.",
      "Generate; Chain QA must be Go before stitch.",
    ],
    activation: `ACTIVATE SEQUENCE_DIRECTOR
ACTIVATE MULTI_CLIP_CONTINUITY
ACTIVATE IMAGINE_HANDOFF
ACTIVATE QA_GUARDIAN

Mode: Extend-from-Frame chain (2 clips)
Input: approved clip N last frame + continuity_state + CHARACTER_DNA
Rule: No stitch until chain QA is Go.
On No-Go: repair plan only — do not rewrite Production Bible.`,
    tips: [
      "Recap must be concrete — vague recaps cause drift.",
      "Budget buffer 20–25% for QA regens.",
    ],
  },
  {
    id: "trailer-sketch",
    title: "Trailer sketch day",
    tagline: "Bible lite → shot list → hero stills → short teaser plan.",
    tier: 3,
    minutes: "60–90 min",
    genre: "Trailer · mixed",
    deliverable: "Mini Bible, 6–12 stills plan, teaser beat sheet",
    budgetHint: "Stills-heavy first (~$0.20–$0.80); video later",
    agents: [
      "Studio Director",
      "Mega Production Architect",
      "Director of Photography",
      "Trailer & Teaser Director",
      "Workflow Quota Optimizer",
    ],
    steps: [
      "Director opens charter: logline, rating, deliverables.",
      "Architect: short Production Bible + VIDEO_PIPELINE_SPEC.",
      "DoP: one lighting/lens language card.",
      "Quota Optimizer: hero vs draft still order before any video.",
      "Trailer Director: 15–30s beat sheet using approved plates only.",
    ],
    activation: `Activate Grok Imagine Cinematic Studio v3.9.1
ACTIVATE STUDIO_DIRECTOR
ACTIVATE MEGA_PRODUCTION_ARCHITECT
ACTIVATE DOP
ACTIVATE QUOTA_OPTIMIZER
ACTIVATE TRAILER_DIRECTOR

Start guided mini-Bible for a 30s teaser.
Rule: stills and plate locks before hero video spend.
Output: Bible lite, DoP card, prioritized shot list, teaser beats.`,
    tips: [
      "Do not generate 15s hero video on day one.",
      "Use Budget calculator “Tier 3 trailer pass” scenario.",
    ],
  },
];
