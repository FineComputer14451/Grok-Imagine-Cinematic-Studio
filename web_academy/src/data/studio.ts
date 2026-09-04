export type Agent = {
  id: string;
  name: string;
  role: string;
  activation: string;
  tier: 1 | 2 | 3;
  category: "leadership" | "creative" | "production" | "post" | "special";
  /** Studio skill surface badges — mapped to the 64-skill suite */
  skills: string[];
};

export type Tier = {
  id: 1 | 2 | 3;
  title: string;
  subtitle: string;
  minutes: string;
  outcome: string;
  steps: { title: string; detail: string }[];
  prompt: string;
  agents: string[];
};

export const TIERS: Tier[] = [
  {
    id: 1,
    title: "Single Agent",
    subtitle: "One prompt. One still. Instant results.",
    minutes: "2 min",
    outcome: "A cinematic still from a direct Imagine prompt",
    steps: [
      {
        title: "Open Grok Imagine",
        detail: "No studio activation required. You are using the raw model.",
      },
      {
        title: "Paste a cinematic prompt",
        detail:
          "Subject, environment, lighting, lens, mood — in that order.",
      },
      {
        title: "Generate and iterate",
        detail: "Change one variable at a time: light, camera, wardrobe.",
      },
    ],
    prompt: `Create a cinematic still of a mysterious woman standing in a rain-slick neon alley at night.
Film noir lighting, anamorphic lens flare, shallow depth of field, 35mm, wet pavement reflections, cool teal and amber practicals.
Mood: quiet dread. No text, no watermark.`,
    agents: ["Imagine Prompt Master"],
  },
  {
    id: 2,
    title: "Two-Agent Workflow",
    subtitle: "Director writes. Imagine executes.",
    minutes: "10 min",
    outcome: "Consistent shots with a director brief + generation handoff",
    steps: [
      {
        title: "Activate Studio Director",
        detail: "Director locks the creative brief and shot list.",
      },
      {
        title: "Activate Imagine Prompt Master",
        detail: "Prompt Master turns the brief into production-ready packets.",
      },
      {
        title: "Generate with gates",
        detail: "Review identity, framing, and lighting before the next shot.",
      },
    ],
    prompt: `ACTIVATE STUDIO_DIRECTOR
Then: ACTIVATE IMAGINE_PROMPT_MASTER

Project: Neon Alley Noir — 3-shot sequence
Goal: Establish character, environment, and tension without dialogue.
Output: Three Grok Imagine prompts + one Extend-from-Frame plan.
Constraints: Same wardrobe, same face identity, R-rated mood only (no explicit content).`,
    agents: ["Studio Director", "Imagine Prompt Master"],
  },
  {
    id: 3,
    title: "Full 25-Agent Pipeline",
    subtitle: "Production Bible → DNA → Sequence → Delivery",
    minutes: "45+ min",
    outcome: "Long-form cinematic sequence with identity lock and post polish",
    steps: [
      {
        title: "Activate full studio",
        detail: "Loads 25 agents, 64 skills, Grok 4.6 default (+ optional grok-4.3 1M). grok-4.5 remains an alias of 4.6.",
      },
      {
        title: "Build the Production Bible",
        detail:
          "Mega Production Architect locks world, tone, and VIDEO_PIPELINE_SPEC.",
      },
      {
        title: "Lock Character DNA",
        detail:
          "Identity Lock Specialist freezes face, wardrobe, and continuity rules.",
      },
      {
        title: "Shoot → Handoff → Polish",
        detail:
          "Sequence Director + Imagine Agent Mode → AI Polish + QA Guardian.",
      },
    ],
    prompt: `Activate Grok Imagine Cinematic Studio v3.11.4

Full production mode.
Genre: Erotic horror (fictional adults, R-rated, artistic — no hardcore).
Working title: The House That Remembers
Deliverables: Production Bible, Character DNA for lead, 6-clip sequence plan, Imagine Video 1.5 handoff packets, post pipeline.
Start with the guided Bible wizard.`,
    agents: [
      "Studio Director",
      "Mega Production Architect",
      "Identity Lock Specialist",
      "Imagine Prompt Master",
      "Director of Photography",
      "Sequence Director",
      "QA Guardian",
      "ErosForge",
    ],
  },
];

export const AGENTS: Agent[] = [
  {
    id: "studio-director",
    name: "Studio Director",
    role: "Central commander. Orchestrates agents, presets, client review.",
    activation: "ACTIVATE STUDIO_DIRECTOR",
    tier: 2,
    category: "leadership",
    skills: ["Orchestration", "Presets", "Client Review", "Agent Routing"],
  },
  {
    id: "mega-architect",
    name: "Mega Production Architect",
    role: "Builds the locked Production Bible and dependency map.",
    activation: "ACTIVATE MEGA_PRODUCTION_ARCHITECT",
    tier: 3,
    category: "leadership",
    skills: ["Production Bible", "Dependency Map", "VIDEO_PIPELINE_SPEC", "World Lock"],
  },
  {
    id: "identity-lock",
    name: "Identity Lock Specialist",
    role: "Character DNA, face continuity, transformation tracking.",
    activation: "ACTIVATE IDENTITY_LOCK",
    tier: 3,
    category: "creative",
    skills: ["Character DNA", "Face Continuity", "Wardrobe Lock", "Transform Track"],
  },
  {
    id: "prompt-master",
    name: "Imagine Prompt Master",
    role: "Elite prompt engineer. Shot library and failure-based learning.",
    activation: "ACTIVATE IMAGINE_PROMPT_MASTER",
    tier: 1,
    category: "creative",
    skills: ["Prompt Craft", "Shot Library", "Failure Learning", "I2I Refiner"],
  },
  {
    id: "dop",
    name: "Director of Photography",
    role: "Lighting language, lenses, camera movement grammar.",
    activation: "ACTIVATE DOP",
    tier: 3,
    category: "creative",
    skills: ["Lighting", "Lens Grammar", "Camera Move", "Visual Language"],
  },
  {
    id: "sequence",
    name: "Sequence Director",
    role: "Clip chaining, Extend-from-Frame plans, long-form continuity.",
    activation: "ACTIVATE SEQUENCE_DIRECTOR",
    tier: 3,
    category: "production",
    skills: ["Extend-from-Frame", "Clip Chain", "Long-form", "Shot List"],
  },
  {
    id: "performance",
    name: "Performance & Emotion Director",
    role: "Performance beats, micro-expressions, emotional arcs.",
    activation: "ACTIVATE PERFORMANCE_EMOTION",
    tier: 3,
    category: "creative",
    skills: ["Performance Beats", "Micro-expression", "Emotional Arc", "Blocking"],
  },
  {
    id: "vfx",
    name: "VFX & SFX Supervisor",
    role: "Particles, creatures, digital integration, practical effects.",
    activation: "ACTIVATE VFX_SFX",
    tier: 3,
    category: "production",
    skills: ["Particles", "Creature FX", "Digital Integrate", "Practical FX"],
  },
  {
    id: "production-design",
    name: "Production Designer",
    role: "Environment DNA, prop memory, world-building.",
    activation: "ACTIVATE PRODUCTION_DESIGNER",
    tier: 3,
    category: "production",
    skills: ["Environment DNA", "Prop Memory", "World-building", "Set Continuity"],
  },
  {
    id: "stunt",
    name: "Stunt & Action Choreographer",
    role: "Fight grammar, vehicle stunts, physics-safe action.",
    activation: "ACTIVATE STUNT_ACTION",
    tier: 3,
    category: "production",
    skills: ["Fight Grammar", "Vehicle Stunts", "Physics QA", "Action Timing"],
  },
  {
    id: "sonic",
    name: "Sonic Architect",
    role: "Dialogue, SFX beds, music cues, native audio specs.",
    activation: "ACTIVATE SONIC_ARCHITECT",
    tier: 3,
    category: "post",
    skills: ["Native Audio", "Dialogue Spec", "Music Cues", "SFX Beds"],
  },
  {
    id: "foley",
    name: "Foley & Sound Design",
    role: "Hyper-real foley layers and diegetic detail.",
    activation: "ACTIVATE FOLEY",
    tier: 3,
    category: "post",
    skills: ["Foley Layers", "Diegetic Detail", "Texture Pass", "Room Tone"],
  },
  {
    id: "polish",
    name: "AI Polish Director",
    role: "Upscale, face restore, color grade, final sheen.",
    activation: "ACTIVATE AI_POLISH",
    tier: 3,
    category: "post",
    skills: ["Upscale", "Face Restore", "Color Grade", "Final Sheen"],
  },
  {
    id: "qa",
    name: "QA Guardian",
    role: "Readiness gates: plate, motion, identity, spend, delivery.",
    activation: "ACTIVATE QA_GUARDIAN",
    tier: 3,
    category: "leadership",
    skills: ["Plate Gate", "Motion Gate", "Identity Gate", "Spend Gate"],
  },
  {
    id: "quota",
    name: "Workflow Quota Optimizer",
    role: "Cost simulation, budget tracking, batch routing.",
    activation: "ACTIVATE QUOTA_OPTIMIZER",
    tier: 3,
    category: "special",
    skills: ["Cost Sim", "Budget Track", "Batch Route", "Quota Intel"],
  },
  {
    id: "trailer",
    name: "Trailer & Teaser Director",
    role: "High-impact marketing cuts and teaser structure.",
    activation: "ACTIVATE TRAILER_DIRECTOR",
    tier: 3,
    category: "post",
    skills: ["Trailer Cut", "Teaser Structure", "Hook Timing", "Marketing Pack"],
  },
  {
    id: "key-art",
    name: "Key Art & Poster Designer",
    role: "Posters, stills packages, brand frames.",
    activation: "ACTIVATE KEY_ART",
    tier: 3,
    category: "post",
    skills: ["Poster Design", "Stills Package", "Brand Frames", "Title Lock"],
  },
  {
    id: "localization",
    name: "Localization Specialist",
    role: "Cultural adaptation, SDH, multi-language packs.",
    activation: "ACTIVATE LOCALIZATION",
    tier: 3,
    category: "special",
    skills: ["Cultural Adapt", "SDH", "Multi-language", "Subtitle Pack"],
  },
  {
    id: "erosforge",
    name: "ErosForge (NSFW Director)",
    role: "R-rated artistic standards, consent framing, physics QA.",
    activation: "ACTIVATE EROSFORGE",
    tier: 3,
    category: "special",
    skills: ["R-rated Art", "Consent Frame", "Intimacy Physics", "NSFW Batch"],
  },
  {
    id: "continuity",
    name: "Multi-Clip Continuity Orchestrator",
    role: "Cross-clip wardrobe, prop, and lighting continuity.",
    activation: "ACTIVATE MULTI_CLIP_CONTINUITY",
    tier: 3,
    category: "production",
    skills: ["Cross-clip Continuity", "Wardrobe Match", "Prop Track", "Light Match"],
  },
  {
    id: "doctor",
    name: "Grok Doctor",
    role: "Diagnoses broken pipelines, skill conflicts, handoff errors.",
    activation: "ACTIVATE GROK_DOCTOR",
    tier: 3,
    category: "special",
    skills: ["Pipeline Diagnose", "Skill Conflict", "Handoff Debug", "Repair Plan"],
  },
  {
    id: "recreation",
    name: "AI Image Recreation",
    role: "Rebuild stills from refs while preserving identity DNA.",
    activation: "ACTIVATE AI_IMAGE_RECREATION",
    tier: 3,
    category: "creative",
    skills: ["Ref Rebuild", "Identity Preserve", "Still Recreate", "I2I Refiner"],
  },
  {
    id: "sound-bed",
    name: "Adaptive Audio Specialist",
    role: "Scene-reactive audio beds for Video 1.5 native sound.",
    activation: "ACTIVATE ADAPTIVE_AUDIO",
    tier: 3,
    category: "post",
    skills: ["Video 1.5 Audio", "Scene-reactive", "Adaptive Beds", "Sync Pass"],
  },
  {
    id: "handoff",
    name: "Imagine Agent Mode Handoff",
    role: "Validates generation packets before they hit Imagine.",
    activation: "ACTIVATE IMAGINE_HANDOFF",
    tier: 3,
    category: "production",
    skills: ["Packet Validate", "Surface Bridge", "Handoff Gate", "Imagine Route"],
  },
  {
    id: "set-deco",
    name: "Set Decorator",
    role: "Prop density, set dressing memory, practical sources.",
    activation: "ACTIVATE SET_DECORATOR",
    tier: 3,
    category: "production",
    skills: ["Prop Density", "Set Dressing", "Practical Lights", "Detail Pass"],
  },
];

/** Unique skill labels across the roster (for filter chips) */
export const ALL_SKILLS = Array.from(
  new Set(AGENTS.flatMap((a) => a.skills)),
).sort((a, b) => a.localeCompare(b));

export const PIPELINE = [
  {
    id: "bible",
    label: "Production Bible",
    detail: "World, tone, deliverables, VIDEO_PIPELINE_SPEC",
  },
  {
    id: "dna",
    label: "Character DNA",
    detail: "Face, wardrobe, continuity rules locked",
  },
  {
    id: "pre",
    label: "Pre-Production",
    detail: "Mood boards, DoP language, shot list",
  },
  {
    id: "shoot",
    label: "Principal Photography",
    detail: "Clips with physics-aware motion + audio",
  },
  {
    id: "handoff",
    label: "Imagine Handoff",
    detail: "Validated packets → Video 1.0 / 1.5",
  },
  {
    id: "qa",
    label: "Readiness Gates",
    detail: "Identity, motion, spend, delivery checks",
  },
  {
    id: "post",
    label: "Post & Polish",
    detail: "Grade, upscale, face restore, package",
  },
  {
    id: "deliver",
    label: "Delivery",
    detail: "Final cut, key art, trailer, reports",
  },
];

export const STATS = [
  { label: "Agents", value: "25" },
  { label: "Skills", value: "62" },
  { label: "Video models", value: "1.0 + 1.5" },
  { label: "Learning tiers", value: "3" },
];
