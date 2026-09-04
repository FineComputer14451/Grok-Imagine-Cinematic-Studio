/** ErosForge module — Studio Academy (educational, opt-in artistic R-rated path) */

export type Protocol = {
  id: string;
  name: string;
  requirement: string;
  why: string;
};

export type PackAgent = {
  id: string;
  name: string;
  activation: string;
  role: string;
  requiresErosforge: boolean;
  skills: string[];
};

export type Lesson = {
  id: string;
  step: string;
  title: string;
  minutes: string;
  summary: string;
  bullets: string[];
  drill?: string;
};

export type StateField = {
  key: string;
  label: string;
  hint: string;
  required: boolean;
};

export type ChainQaCheck = {
  key: string;
  weight: number;
  critical: boolean;
  inspect: string;
  recovery: string;
};

export type QuizItem = {
  id: string;
  prompt: string;
  options: string[];
  answer: number;
  explain: string;
};

export const EROSFORGE_VERSION = "4.5";
export const ACADEMY_MODULE_VERSION = "3.11.4";

/** Fail-closed AUP reminder shown on ErosForge paths */
export const AUP_POLICY_URL = "https://x.ai/legal/acceptable-use-policy";
export const AUP_ATTEST_HINT =
  "Before intimate work: nsfw attest --i-am-18 --imaginary-adults --not-a-real-person --acknowledge-aup";

export const EROSFORGE_TAGLINE =
  "Opt-in artistic intimacy direction — consent frames, physics, identity lock, and chain QA for R-rated cinematic work.";

export const PROTOCOLS: Protocol[] = [
  {
    id: "strict-opt-in",
    name: "STRICT_OPT_IN",
    requirement:
      "Never generate intimate content without explicit user activation (ACTIVATE EROSFORGE).",
    why: "Keeps the studio SFW by default. ErosForge is a satellite pack — load only when the production needs it. v3.11+ also requires local 18+ AUP attestation (nsfw attest) before intimate gates open — https://x.ai/legal/acceptable-use-policy",
  },
  {
    id: "erosforge-state",
    name: "EROSFORGE_STATE",
    requirement:
      "Track post-scene physical and emotional state for continuity across extends.",
    why: "Intimate sequences drift fastest. State handoff is the continuity spine for clip N → N+1.",
  },
  {
    id: "physics",
    name: "PHYSICS_OF_INTIMACY",
    requirement:
      "Enforce realistic body mechanics, fabric tension, weight transfer, and contact physics.",
    why: "Uncanny motion and body morphing kill artistic credibility more than lighting mistakes.",
  },
  {
    id: "micro",
    name: "MICRO_EXPRESSION_TIMING",
    requirement: "Design authentic emotional micro-beats before peak intensity.",
    why: "Performance sells the scene. Without timing notes, faces freeze or over-act between clips.",
  },
  {
    id: "breath",
    name: "BREATH_AUDIO_SYNC",
    requirement:
      "Align breath, vocalization, and ambient audio with action — especially on Video 1.5 native.",
    why: "Audio is half the intimacy read. Mismatched breath breaks immersion immediately.",
  },
  {
    id: "identity",
    name: "IDENTITY_PRESERVATION",
    requirement:
      "Never break locked Character DNA — even under wardrobe change or heat.",
    why: "Face/body drift is the #1 failure mode on multi-clip intimate work.",
  },
  {
    id: "model-layer",
    name: "MODEL_LAYER_ROUTING",
    requirement:
      "Record preferred chat model (v9-4p5-chat-expert / multi / grok-4-auto) on every intimate plan.",
    why: "Downstream agents must know which reasoning tier produced the plan.",
  },
  {
    id: "dual",
    name: "1.0_1.5_DUAL_SUPPORT",
    requirement:
      "Declare Imagine Video 1.5 (hero) vs 1.0 (draft) on every plan and state snapshot.",
    why: "Downstream agents must not assume 1.5 capabilities on 1.0 drafts.",
  },
  {
    id: "artistic",
    name: "ARTISTIC_JUSTIFICATION",
    requirement:
      "Every intimate moment must serve character truth or story — not gratuitous detail.",
    why: "Artistic priority is what separates cinematic R-rated work from generic explicit spam.",
  },
  {
    id: "explicitness",
    name: "EXPLICITNESS_LEVEL_PROTECTION",
    requirement:
      "Never dilute Level 3–4 intensity without explicit user direction.",
    why: "Silent sanitizing breaks the brief and wastes quota on wrong-tone regenerations.",
  },
  {
    id: "handoff",
    name: "HANDOFF_PACKET",
    requirement:
      "EROSFORGE_STATE and scene plans must be structured, validated, and handoff-ready.",
    why: "Planning essays are not generation packets. Gates refuse incomplete handoffs.",
  },
];

export const PACK_AGENTS: PackAgent[] = [
  {
    id: "erosforge",
    name: "ErosForge NSFW Director",
    activation: "ACTIVATE EROSFORGE",
    role: "Lead intimacy director — scene intent, physics, micro-expression, state, model path.",
    requiresErosforge: false,
    skills: ["Scene Intent", "Physics Plan", "EROSFORGE_STATE", "Consent Frame"],
  },
  {
    id: "nsfw-extender",
    name: "NSFW Sequence Extender",
    activation: "ACTIVATE NSFW_SEQUENCE_EXTENDER",
    role: "30–120s+ sensual extend chains with tension curves and artifact-aware QA.",
    requiresErosforge: true,
    skills: ["Tension Curve", "Extend-from-Frame", "Camera Pacing", "Chain Continuity"],
  },
  {
    id: "nsfw-quota",
    name: "NSFW Quota Orchestrator",
    activation: "ACTIVATE NSFW_QUOTA_ORCHESTRATOR",
    role: "Hero-first batch planning under SuperGrok limits; 1.0 draft vs 1.5 hero routing.",
    requiresErosforge: true,
    skills: ["Hero-first", "Batch Plan", "i2v Logic", "Quota Report"],
  },
  {
    id: "nsfw-chain-qa",
    name: "NSFW Chain QA Protocol",
    activation: "RUN NSFW CHAIN QA REVIEW",
    role: "Weighted 8-point artifact-aware gate before every intimate extend or stitch.",
    requiresErosforge: true,
    skills: ["Hand Integrity", "Physics Fidelity", "Skin Continuity", "Tension Carryover"],
  },
  {
    id: "story-weaver",
    name: "NSFW Story Weaver",
    activation: "ACTIVATE NSFW STORY WEAVER",
    role: "Pure-text high-density narrative support — DNA-locked, not visual generation.",
    requiresErosforge: false,
    skills: ["Tension Curve", "DNA Dialogue", "Sensory Prose", "Continuity"],
  },
];

export const LESSONS: Lesson[] = [
  {
    id: "opt-in",
    step: "01",
    title: "Strict opt-in",
    minutes: "3 min",
    summary:
      "ErosForge never auto-loads. You activate it only when the production needs an R-rated artistic path.",
    bullets: [
      "Default studio surface stays SFW (Core · Camera · Sequence · Delivery).",
      "Say ACTIVATE EROSFORGE (or install the NSFW marketplace pack) before intimate work.",
      "Without activation, intimate extends and quota batches must refuse generation.",
    ],
    drill: "Write the activation line for a new project that needs one intimate beat only.",
  },
  {
    id: "consent",
    step: "02",
    title: "Consent frame & hard limits",
    minutes: "5 min",
    summary:
      "Lock tone, rating, and non-negotiable boundaries before any plate or motion spend.",
    bullets: [
      "Fictional adults only — never minors, never non-consent themes.",
      "Record hard_limits and soft_limits in EROSFORGE_STATE.",
      "Artistic priority: emotion, lighting, performance — not gratuitous detail.",
    ],
    drill: "List three hard limits that always block generation for this academy path.",
  },
  {
    id: "dna",
    step: "03",
    title: "Identity lock first",
    minutes: "6 min",
    summary:
      "Character DNA must be locked before intimate plates. ErosForge never overrides Identity Lock.",
    bullets: [
      "Extract → lock → inject DNA for every adult character on screen.",
      "Wardrobe / heat transforms need Transform Track entries.",
      "Multi-character scenes need Multi-Character Identity Arbiter.",
    ],
    drill: "Name the gate that must pass before the first intimate still.",
  },
  {
    id: "scene-plan",
    step: "04",
    title: "Scene plan structure",
    minutes: "8 min",
    summary:
      "Every ErosForge response follows a fixed output structure for handoff readiness.",
    bullets: [
      "1. Scene Intent & Emotional Arc",
      "2. Physics & Micro-Expression Plan",
      "3. Breath / Audio Sync Notes",
      "4. EROSFORGE_STATE Snapshot",
      "5. Model Path Note (1.5 vs 1.0)",
      "6. Recommended Next Actions",
    ],
    drill: "Order the six output blocks from memory.",
  },
  {
    id: "state",
    step: "05",
    title: "EROSFORGE_STATE continuity",
    minutes: "8 min",
    summary:
      "Post-scene state is the intimacy equivalent of LAST_FRAME_RECAP — required before extend.",
    bullets: [
      "Capture emotional temperature, physical pose, wardrobe state, prop contact.",
      "Pass intimacy_state_handoff into NSFW Sequence Extender.",
      "Reject extends when state is missing or contradicts DNA.",
    ],
    drill: "Fill the state builder for a fictional two-character reunion beat.",
  },
  {
    id: "extend-qa",
    step: "06",
    title: "Extend + Chain QA",
    minutes: "10 min",
    summary:
      "Long-form intimate work uses NSFW Sequence Extender + the 8-point Chain QA gate.",
    bullets: [
      "Requires concurrent ErosForge activation.",
      "One deliberate camera move per short clip; tension curve across the chain.",
      "Critical checks must score ≥ 7.",
      "Weighted score ≥ 7.0 overall before stitch.",
    ],
    drill: "Name the four critical Chain QA checks.",
  },
  {
    id: "quota",
    step: "07",
    title: "Quota-aware batches",
    minutes: "6 min",
    summary:
      "NSFW Quota Orchestrator protects hero plates and routes 1.0 drafts vs 1.5 heroes.",
    bullets: [
      "Hero-first prioritization — never burn quota on unready intimate heroes.",
      "Label every batch path 1.0 or 1.5.",
      "Smart retry only after DNA + state + plate gates pass.",
    ],
    drill: "When would you choose Video 1.0 over 1.5 for an intimate beat?",
  },
  {
    id: "parallel",
    step: "08",
    title: "Parallel Brief densification",
    minutes: "5 min",
    summary:
      "Under MAXIMUM AGENTIC MODE, Level 3–4 briefs carry Confirmed Explicitness Level, ErosForge status, DNA lock, and Non-Negotiable Explicitness Anchors.",
    bullets: [
      "Intensity is never diluted silently across parallel specialists.",
      "Foley only densifies intimate SFX when ErosForge=true.",
      "Converge into handoff without silent NSFW routing.",
    ],
    drill: "List five fields every Level 3–4 Parallel Brief must carry.",
  },
];

export const STATE_FIELDS: StateField[] = [
  { key: "project", label: "Project / sequence slug", hint: "e.g. house-that-remembers / intimacy-01", required: true },
  { key: "rating", label: "Rating target", hint: "R-rated artistic · fictional adults only", required: true },
  { key: "consent_frame", label: "Consent frame", hint: "Mutual, enthusiastic, in-character boundaries", required: true },
  { key: "emotional_arc", label: "Emotional arc (this beat)", hint: "Start → turn → end temperature", required: true },
  { key: "physics_notes", label: "Physics notes", hint: "Weight, contact, fabric, one motion beat", required: true },
  { key: "micro_expression", label: "Micro-expression plan", hint: "Eyes, mouth, breath timing", required: true },
  { key: "breath_audio", label: "Breath / audio sync", hint: "Native 1.5 bed + diegetic breath", required: false },
  { key: "wardrobe_state", label: "Post-scene wardrobe state", hint: "What is on/off/displaced for extend continuity", required: true },
  { key: "pose_recap", label: "Pose / last-frame recap", hint: "Who faces camera, contact points, eyeline", required: true },
  { key: "emotional_residue", label: "Emotional residue", hint: "What the character still carries after the beat", required: false },
  { key: "hard_limits", label: "Hard limits", hint: "Always: no minors, no non-consent, no real persons", required: true },
  { key: "model_path", label: "Model path", hint: "video_1_5 | video_1_0 | still", required: true },
  { key: "chat_model", label: "Chat model (routing)", hint: "grok-v9-4p5-chat-expert | multi | grok-4-auto", required: false },
  { key: "dna_ids", label: "Locked DNA ids", hint: "Comma-separated character DNA keys", required: true },
];

export const CHAIN_QA: ChainQaCheck[] = [
  { key: "hand_finger_integrity", weight: 1.4, critical: true, inspect: "Finger count, pose, no merging", recovery: "Hands out of frame or single-hand pose" },
  { key: "explicit_area_artifact_risk", weight: 1.5, critical: true, inspect: "No morphing, duplication, uncanny detail", recovery: "Pull back framing, one body focus" },
  { key: "body_proportion_stability", weight: 1.3, critical: true, inspect: "Limb/torso ratios at stitch boundary", recovery: "Re-lock plate; shorten motion beat" },
  { key: "intimate_physics_fidelity", weight: 1.4, critical: true, inspect: "Weight transfer, skin compression, momentum", recovery: "Shorten clip to 6–8s, one motion beat" },
  { key: "skin_texture_consistency", weight: 1.3, critical: false, inspect: "Pores, tone, marks match across stitch", recovery: "Tighten DNA inject, match color grade" },
  { key: "fabric_cloth_physics", weight: 1.2, critical: false, inspect: "Drape, tension, pull direction", recovery: "One fabric tension point in prompt" },
  { key: "erotic_tension_carryover", weight: 1.1, critical: false, inspect: "Sensual curve — no mood drop at cut", recovery: "Re-plan tension midpoints; re-score emotion" },
  { key: "lighting_skin_modeling", weight: 1.0, critical: false, inspect: "Rim/practical flatters skin at boundary", recovery: "Match key direction from last-frame recap" },
];

export const MODEL_ROUTING = [
  { task: "Complex multi-character emotional arcs / full state synthesis", model: "grok-v9-4p5-multi", reasoning: "high" },
  { task: "Single-scene craft, micro-expression, physics, breath/audio", model: "grok-v9-4p5-chat-expert", reasoning: "high" },
  { task: "Quick status / simple state checks", model: "grok-4-auto", reasoning: "medium" },
] as const;

export const STUDIO_STATE_FIELDS = [
  "intimacy_physics_state",
  "post_scene_state",
  "clothing_displacement_log",
  "emotional_residue",
  "audio_sync_notes",
] as const;

export const ACTIVATION_TEMPLATES = [
  {
    id: "basic",
    title: "Basic activation",
    body: `ACTIVATE EROSFORGE\n\nMode: R-rated artistic (fictional adults only).\nProject: {{project}}\nPriority: emotion, lighting, identity lock — not gratuitous detail.\nHard limits: no minors, no non-consent, no real persons.\nOutput: Scene Intent → Physics & Micro-Expression → Breath/Audio → EROSFORGE_STATE → Model Path → Next Actions.`,
  },
  {
    id: "with-dna",
    title: "With Identity Lock",
    body: `ACTIVATE STUDIO_DIRECTOR\nACTIVATE EROSFORGE\nACTIVATE IDENTITY_LOCK\nACTIVATE PERFORMANCE_EMOTION\nACTIVATE QA_GUARDIAN\n\nMode: R-rated artistic (fictional adults only).\nRequire DNA lock before any intimate plate.\nDeclare model path: video_1_5 (hero) or video_1_0 (draft).\nRefuse generation until plate + identity gates pass.`,
  },
  {
    id: "extend-chain",
    title: "Intimate extend chain",
    body: `ACTIVATE EROSFORGE\nACTIVATE NSFW_SEQUENCE_EXTENDER\nACTIVATE IDENTITY_LOCK\nRUN NSFW CHAIN QA REVIEW\n\nSequence: {{project}}\nUse LAST_FRAME_RECAP + EROSFORGE_STATE for every clip N → N+1.\nOne camera move per short clip. Tension curve across the chain.\nCritical Chain QA checks must score ≥ 7 before extend or stitch.`,
  },
  {
    id: "quota-batch",
    title: "Quota-aware batch",
    body: `ACTIVATE EROSFORGE\nACTIVATE NSFW_QUOTA_ORCHESTRATOR\nACTIVATE QUOTA_OPTIMIZER\n\nHero-first intimate batch under remaining quota.\nDraft path: Imagine Video 1.0\nHero path: Imagine Video 1.5 Native (only after plate + DNA + state ready)\nOutput: cost table, ordered shot list, retry policy.`,
  },
  {
    id: "parallel-brief",
    title: "Parallel Brief (Level 3–4)",
    body: `ACTIVATE EROSFORGE\nMAXIMUM AGENTIC MODE — Parallel Brief Protocol v1.0\n\nProject: {{project}}\nConfirmed Explicitness Level: 3\nErosForge status: active\nDNA lock status: required before plate\nContinuity Flags: wardrobe_displacement · emotional_residue · contact_points\nNon-Negotiable Explicitness Anchors: (fill before dispatch)\n\nSpecialists: DoP · Prompt Master · Continuity · Foley (intimate SFX only if ErosForge=true)\nIntensity: never dilute without explicit user direction.\nConverge into handoff — no silent NSFW routing.`,
  },
] as const;

export const EROSFORGE_QUIZ: QuizItem[] = [
  {
    id: "eq1",
    prompt: "When may ErosForge generate intimate content?",
    options: [
      "Whenever the Production Bible mentions romance",
      "Only after explicit ACTIVATE EROSFORGE (strict opt-in)",
      "Automatically when NSFW pack is installed",
      "After any Tier 3 activation",
    ],
    answer: 1,
    explain: "STRICT_OPT_IN: never generate intimate content without explicit user activation.",
  },
  {
    id: "eq2",
    prompt: "What must be locked before intimate plates?",
    options: ["Final trailer cut", "Character DNA (Identity Lock)", "Only the music cue", "Delivery package zip"],
    answer: 1,
    explain: "IDENTITY_PRESERVATION requires locked DNA before multi-shot intimate work.",
  },
  {
    id: "eq3",
    prompt: "What is EROSFORGE_STATE primarily for?",
    options: [
      "Billing reports",
      "Post-scene physical/emotional continuity for extends",
      "Color LUT selection",
      "Git commit messages",
    ],
    answer: 1,
    explain: "State handoff tracks post-scene continuity so clip N+1 does not drift.",
  },
  {
    id: "eq4",
    prompt: "NSFW Sequence Extender requires which prerequisite?",
    options: ["Trailer Director only", "Prior or concurrent ACTIVATE EROSFORGE", "Localization Specialist", "Key Art only"],
    answer: 1,
    explain: "EROSFORGE_PREREQUISITE — extender never operates without ErosForge.",
  },
  {
    id: "eq5",
    prompt: "Chain QA pass rule for critical checks?",
    options: [
      "Average of all scores ≥ 5",
      "Critical checks ≥ 7 and weighted score ≥ 7.0",
      "Any single check ≥ 9",
      "Director gut feel only",
    ],
    answer: 1,
    explain: "Weighted score ≥ 7.0 and all critical checks ≥ 7.0 before extend/stitch.",
  },
  {
    id: "eq6",
    prompt: "Preferred model path for hero intimate video?",
    options: [
      "Imagine Video 1.0 only",
      "Imagine Video 1.5 Native (1.0 for drafts)",
      "Stills only — never video",
      "Always 1.0 for heroes",
    ],
    answer: 1,
    explain: "1.5 Native is primary for high-fidelity intimate sequences; 1.0 for cost drafts.",
  },
  {
    id: "eq7",
    prompt: "What does ARTISTIC_JUSTIFICATION require?",
    options: [
      "Max resolution at all times",
      "Every intimate moment serves character truth or story",
      "Always use anamorphic lenses",
      "Skip DNA for stills",
    ],
    answer: 1,
    explain: "Intimate beats must earn their place — emotion and story first, never gratuitous spam.",
  },
  {
    id: "eq8",
    prompt: "Under Parallel Brief Protocol, Level 3–4 intensity may be diluted when?",
    options: [
      "Whenever Foley prefers quieter SFX",
      "Only with explicit user direction",
      "Automatically on SuperGrok Free",
      "When DoP switches to 50mm",
    ],
    answer: 1,
    explain: "EXPLICITNESS_LEVEL_PROTECTION — intensity is never diluted silently across specialists.",
  },
];

export function buildErosforgeStatePacket(
  values: Record<string, string>,
  generatedAt = "{{timestamp}}",
): string {
  const lines = [
    "EROSFORGE_STATE v4.5",
    "schema: intimacy_state_handoff",
    `generated_at: ${generatedAt}`,
    "",
  ];
  for (const f of STATE_FIELDS) {
    const v = (values[f.key] ?? "").trim() || "—";
    lines.push(`${f.key}: ${v}`);
  }
  lines.push("");
  lines.push("studio_state_aliases:");
  for (const alias of STUDIO_STATE_FIELDS) {
    lines.push(`  - ${alias}`);
  }
  lines.push("");
  lines.push("gates:");
  lines.push("  dna_locked: required");
  lines.push("  consent_frame: required");
  lines.push("  plate_ready: required before hero spend");
  lines.push("  chain_qa_min: 7.0");
  return lines.join("\n");
}

export function buildDirectorActivation(
  project: string,
  modelPath: string,
): string {
  return `ACTIVATE EROSFORGE\n\nProject: ${project || "untitled-sequence"}\nMode: R-rated artistic (fictional adults only)\nModel path: ${modelPath || "video_1_5"}\nHard limits: no minors · no non-consent · no real persons\n\nDeliver:\n1. Scene Intent & Emotional Arc\n2. Physics & Micro-Expression Plan\n3. Breath / Audio Sync Notes\n4. EROSFORGE_STATE Snapshot\n5. Model Path Note\n6. Recommended Next Actions\n\nRequire Identity Lock DNA inject before any Imagine spend.`;
}

export const PIPELINE_STEPS = [
  { id: "opt", label: "Opt-in", detail: "ACTIVATE EROSFORGE" },
  { id: "limits", label: "Limits", detail: "Consent + hard limits card" },
  { id: "dna", label: "DNA", detail: "Identity Lock freeze" },
  { id: "plan", label: "Scene plan", detail: "6-block ErosForge output" },
  { id: "state", label: "State", detail: "EROSFORGE_STATE snapshot" },
  { id: "plate", label: "Plate gate", detail: "Ready still before motion" },
  { id: "extend", label: "Extend", detail: "NSFW Sequence Extender" },
  { id: "qa", label: "Chain QA", detail: "8-point weighted gate" },
  { id: "deliver", label: "Deliver", detail: "Polish + ship checklist" },
] as const;
