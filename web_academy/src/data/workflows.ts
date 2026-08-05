export type WorkflowStep = {
  agent: string;
  action: string;
  handsOff: string;
};

export type Workflow = {
  id: string;
  title: string;
  summary: string;
  tier: 1 | 2 | 3;
  minutes: string;
  tags: string[];
  agents: string[];
  steps: WorkflowStep[];
  activation: string;
  when: string;
};

export const WORKFLOWS: Workflow[] = [
  {
    id: "single-still",
    title: "Single-still sprint",
    summary: "One specialist, one plate. No multi-agent load.",
    tier: 1,
    minutes: "2–5 min",
    tags: ["still", "prompt", "fast"],
    agents: ["Imagine Prompt Master"],
    steps: [
      {
        agent: "Imagine Prompt Master",
        action: "Craft Ultimate Template prompt + negatives",
        handsOff: "Ready still prompt → Grok Imagine",
      },
    ],
    activation: `ACTIVATE IMAGINE_PROMPT_MASTER

Deliver: one cinematic still prompt (subject → environment → lighting → lens → mood).
Negatives: text, watermark, extra limbs.
Output format: paste-ready Imagine packet only.`,
    when: "Learning, mood boards, or testing a look before spending on agents.",
  },
  {
    id: "director-prompt",
    title: "Director → Prompt Master",
    summary: "Brief locks first; prompts stay consistent across a short shot list.",
    tier: 2,
    minutes: "10–15 min",
    tags: ["brief", "shots", "handoff"],
    agents: ["Studio Director", "Imagine Prompt Master"],
    steps: [
      {
        agent: "Studio Director",
        action: "Lock creative brief, tone, and 3-shot list",
        handsOff: "Shot list + constraints JSON",
      },
      {
        agent: "Imagine Prompt Master",
        action: "Convert each shot into Imagine packets",
        handsOff: "Per-shot prompts → generation",
      },
    ],
    activation: `ACTIVATE STUDIO_DIRECTOR
Then: ACTIVATE IMAGINE_PROMPT_MASTER

Project: short 3-shot sequence
Director locks: brief, wardrobe, lighting language, shot list.
Prompt Master outputs: 3 paste-ready Imagine prompts + shared negatives.
Gate before next shot: identity, framing, lighting.`,
    when: "You need more than one related still or a micro-sequence without full Bible.",
  },
  {
    id: "dna-lock-chain",
    title: "Character DNA lock chain",
    summary: "Extract identity once, freeze it, then generate without face drift.",
    tier: 3,
    minutes: "15–25 min",
    tags: ["identity", "DNA", "continuity"],
    agents: [
      "Identity Lock Specialist",
      "Imagine Prompt Master",
      "Imagine Agent Mode Handoff",
    ],
    steps: [
      {
        agent: "Identity Lock Specialist",
        action: "Build Character DNA from refs (face, wardrobe, rules)",
        handsOff: "DNA inject block",
      },
      {
        agent: "Imagine Prompt Master",
        action: "Write prompts with DNA inject at top of every packet",
        handsOff: "DNA-bound prompts",
      },
      {
        agent: "Imagine Agent Mode Handoff",
        action: "Validate packets before Imagine spend",
        handsOff: "Go/No-Go generation packets",
      },
    ],
    activation: `ACTIVATE IDENTITY_LOCK
Then: ACTIVATE IMAGINE_PROMPT_MASTER
Then: ACTIVATE IMAGINE_HANDOFF

Task: lock lead Character DNA, produce 4 consistent stills.
Rules: same face, wardrobe, age; no wardrobe change without Transform Track.
Handoff must pass identity gate before any video spend.`,
    when: "Recurring characters, multi-shot campaigns, or any sequence longer than one clip.",
  },
  {
    id: "bible-to-shoot",
    title: "Bible → Pre-pro → Shoot",
    summary: "Full production foundation: world lock, visual language, then principal photography.",
    tier: 3,
    minutes: "45+ min",
    tags: ["bible", "DoP", "sequence"],
    agents: [
      "Studio Director",
      "Mega Production Architect",
      "Director of Photography",
      "Sequence Director",
      "Imagine Agent Mode Handoff",
    ],
    steps: [
      {
        agent: "Studio Director",
        action: "Open project, set goals and deliverables",
        handsOff: "Project charter",
      },
      {
        agent: "Mega Production Architect",
        action: "Build Production Bible + VIDEO_PIPELINE_SPEC",
        handsOff: "Locked Bible",
      },
      {
        agent: "Director of Photography",
        action: "Define lighting, lenses, camera grammar",
        handsOff: "Visual language card",
      },
      {
        agent: "Sequence Director",
        action: "Break story into clips + extend plan",
        handsOff: "Clip graph + LAST_FRAME plan",
      },
      {
        agent: "Imagine Agent Mode Handoff",
        action: "Validate generation packets for Video 1.0/1.5",
        handsOff: "Approved shoot packets",
      },
    ],
    activation: `Activate Grok Imagine Cinematic Studio v3.9.1
ACTIVATE STUDIO_DIRECTOR
ACTIVATE MEGA_PRODUCTION_ARCHITECT
ACTIVATE DOP
ACTIVATE SEQUENCE_DIRECTOR
ACTIVATE IMAGINE_HANDOFF

Start guided Production Bible wizard.
After Bible lock: DoP language → sequence plan → handoff gates → generate.`,
    when: "Long-form, trailer work, or any project that needs continuity across many clips.",
  },
  {
    id: "extend-chain-qa",
    title: "Extend chain + QA gate",
    summary: "Grow a clip with Extend-from-Frame, then pass weighted chain QA before stitch.",
    tier: 3,
    minutes: "20–40 min",
    tags: ["extend", "QA", "long-form"],
    agents: [
      "Sequence Director",
      "Multi-Clip Continuity Orchestrator",
      "QA Guardian",
      "Imagine Agent Mode Handoff",
    ],
    steps: [
      {
        agent: "Sequence Director",
        action: "Plan clip N+1 from LAST_FRAME_RECAP",
        handsOff: "Extend brief + momentum vector",
      },
      {
        agent: "Multi-Clip Continuity Orchestrator",
        action: "Check wardrobe, props, light match vs prior clip",
        handsOff: "Continuity state",
      },
      {
        agent: "Imagine Agent Mode Handoff",
        action: "Route validated extend packet to Imagine",
        handsOff: "Generated extension clip",
      },
      {
        agent: "QA Guardian",
        action: "Run chain QA (identity, motion, artifact, spend)",
        handsOff: "Go / No-Go + fix list",
      },
    ],
    activation: `ACTIVATE SEQUENCE_DIRECTOR
ACTIVATE MULTI_CLIP_CONTINUITY
ACTIVATE IMAGINE_HANDOFF
ACTIVATE QA_GUARDIAN

Mode: Extend-from-Frame chain
Input: approved clip N last frame + continuity_state
Rule: No stitch until chain QA is Go.
On No-Go: repair plan only — do not rewrite Production Bible.`,
    when: "Building 60–180s+ sequences from short Imagine clips.",
  },
  {
    id: "post-delivery",
    title: "Post polish → delivery pack",
    summary: "Grade, restore, package key art and trailer after QA-approved cuts.",
    tier: 3,
    minutes: "25–45 min",
    tags: ["post", "polish", "delivery"],
    agents: [
      "QA Guardian",
      "AI Polish Director",
      "Key Art & Poster Designer",
      "Trailer & Teaser Director",
      "Sonic Architect",
    ],
    steps: [
      {
        agent: "QA Guardian",
        action: "Confirm picture lock / Go on final cut",
        handsOff: "Approved masters list",
      },
      {
        agent: "AI Polish Director",
        action: "Upscale, face restore, final sheen",
        handsOff: "Polished masters",
      },
      {
        agent: "Sonic Architect",
        action: "Dialogue, SFX beds, music cues (esp. Video 1.5)",
        handsOff: "Audio-locked cut",
      },
      {
        agent: "Key Art & Poster Designer",
        action: "Still package + poster frames",
        handsOff: "Key art set",
      },
      {
        agent: "Trailer & Teaser Director",
        action: "Hook-first 15–60s cut",
        handsOff: "Trailer / teaser deliverables",
      },
    ],
    activation: `ACTIVATE QA_GUARDIAN
ACTIVATE AI_POLISH
ACTIVATE SONIC_ARCHITECT
ACTIVATE KEY_ART
ACTIVATE TRAILER_DIRECTOR

Only run after sequence QA Go.
Deliver: polished master, key art pack, 30s teaser with native audio notes.`,
    when: "Client presentation, social cutdowns, or festival-ready package.",
  },
  {
    id: "quota-aware-batch",
    title: "Quota-aware batch plan",
    summary: "Simulate cost, prioritize hero shots, batch draft vs hero routes.",
    tier: 3,
    minutes: "10–20 min",
    tags: ["quota", "batch", "cost"],
    agents: [
      "Workflow Quota Optimizer",
      "Studio Director",
      "Imagine Prompt Master",
    ],
    steps: [
      {
        agent: "Workflow Quota Optimizer",
        action: "Estimate per-shot cost (1.0 vs 1.5) + session budget",
        handsOff: "Budget plan + hero priority list",
      },
      {
        agent: "Studio Director",
        action: "Approve which shots are hero vs draft",
        handsOff: "Approved shot tiers",
      },
      {
        agent: "Imagine Prompt Master",
        action: "Write tiered prompts (draft plate vs hero)",
        handsOff: "Batched packets",
      },
    ],
    activation: `ACTIVATE QUOTA_OPTIMIZER
ACTIVATE STUDIO_DIRECTOR
ACTIVATE IMAGINE_PROMPT_MASTER

Session goal: N stills + M clips under remaining quota.
Output: cost table, hero-first order, Fast-mode recommendations.
Do not generate hero video until plate readiness is locked.`,
    when: "Heavy sessions, weekly SuperGrok limits, or multi-project days.",
  },
  {
    id: "r-rated-artistic",
    title: "R-rated artistic path",
    summary: "Consent-framed intimacy direction with physics QA — fictional adults only.",
    tier: 3,
    minutes: "30–60 min",
    tags: ["R-rated", "ErosForge", "artistic"],
    agents: [
      "Studio Director",
      "ErosForge (NSFW Director)",
      "Identity Lock Specialist",
      "Performance & Emotion Director",
      "QA Guardian",
    ],
    steps: [
      {
        agent: "Studio Director",
        action: "Confirm R-rated artistic scope and boundaries",
        handsOff: "Tone + limits card",
      },
      {
        agent: "ErosForge (NSFW Director)",
        action: "Design intimacy beats, consent framing, physics notes",
        handsOff: "Intimacy state + shot plan",
      },
      {
        agent: "Identity Lock Specialist",
        action: "Freeze adult Character DNA across beats",
        handsOff: "DNA inject",
      },
      {
        agent: "Performance & Emotion Director",
        action: "Micro-expression and breath timing",
        handsOff: "Performance beats",
      },
      {
        agent: "QA Guardian",
        action: "Artifact-aware + identity gates before extend",
        handsOff: "Go / No-Go",
      },
    ],
    activation: `ACTIVATE STUDIO_DIRECTOR
ACTIVATE EROSFORGE
ACTIVATE IDENTITY_LOCK
ACTIVATE PERFORMANCE_EMOTION
ACTIVATE QA_GUARDIAN

Mode: R-rated artistic (fictional adults only).
No hardcore; prioritize emotion, lighting, and physics of intimacy.
Require ErosForge + identity lock before any intimate extend chain.`,
    when: "Mature cinematic scenes that must stay artistic, consistent, and policy-safe.",
  },
];

export const WORKFLOW_TAGS = Array.from(
  new Set(WORKFLOWS.flatMap((w) => w.tags)),
).sort();
