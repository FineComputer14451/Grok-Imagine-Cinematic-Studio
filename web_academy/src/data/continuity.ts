/** Continuity module — Studio Academy (multi-clip memory, LAST_FRAME_RECAP, drift gates) */

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

export type ContinuityField = {
  key: string;
  label: string;
  hint: string;
  required: boolean;
};

export type DriftCheck = {
  id: string;
  label: string;
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

export const CONTINUITY_VERSION = "4.5";
export const ACADEMY_MODULE_VERSION = "3.11.4";

export const CONTINUITY_TAGLINE =
  "Multi-clip memory keeper — LAST_FRAME_RECAP, continuity_state, prop/environment/emotion drift gates before every extend.";

export const PROTOCOLS: Protocol[] = [
  {
    id: "recap-required",
    name: "LAST_FRAME_RECAP_REQUIRED",
    requirement:
      "Never extend or stitch N+1 without a validated LAST_FRAME_RECAP from the approved prior clip.",
    why: "Without recap, the model invents a new scene instead of continuing one.",
  },
  {
    id: "state-packet",
    name: "CONTINUITY_STATE_PACKET",
    requirement:
      "Carry continuity_state: wardrobe, props, environment, lighting direction, emotional residue, camera momentum.",
    why: "Untracked state is the #1 source of multi-clip drift.",
  },
  {
    id: "identity-first",
    name: "IDENTITY_BEFORE_CONTINUITY",
    requirement:
      "Identity Lock / DNA freeze must hold before continuity can be trusted across clips.",
    why: "Face drift invalidates prop and wardrobe continuity scores.",
  },
  {
    id: "prop-memory",
    name: "PROP_MEMORY",
    requirement:
      "Track hero props in/out of frame; do not invent or lose objects between cuts.",
    why: "Missing guns, phones, or bags break audience trust faster than soft focus.",
  },
  {
    id: "env-lock",
    name: "ENVIRONMENT_LOCK",
    requirement:
      "Lock set DNA: weather, time of day, practical sources, background geography.",
    why: "Day-to-night or dry-to-rain jumps without motivation read as errors.",
  },
  {
    id: "emotion-residue",
    name: "EMOTIONAL_RESIDUE",
    requirement:
      "Carry emotional temperature into the next beat; do not reset to neutral without a story reason.",
    why: "Flat affect after a peak scene kills sequence drama.",
  },
  {
    id: "momentum",
    name: "MOMENTUM_VECTOR",
    requirement:
      "Record camera and subject motion direction so extend continues the same energy.",
    why: "Whip-pan into static or left-to-right into reverse without intent feels broken.",
  },
  {
    id: "block-on-high",
    name: "BLOCK_ON_HIGH_DRIFT",
    requirement:
      "High continuity risk blocks extension until fix_list is resolved — do not silent re-roll.",
    why: "Hope is not a continuity strategy.",
  },
  {
    id: "timeline-label",
    name: "TIMELINE_LABEL",
    requirement:
      "Label every clip with timeline_id when branching or non-linear; never mix unlabeled branches.",
    why: "Branch confusion looks like random continuity failure.",
  },
  {
    id: "handoff",
    name: "CONTINUITY_HANDOFF",
    requirement:
      "Attach continuity report to Sequence Blueprint / Handoff Packet before Chain QA and Assembly.",
    why: "Downstream agents need state, not vibes.",
  },
];

export const PACK_AGENTS: PackAgent[] = [
  {
    id: "continuity",
    name: "Continuity Consistency Guardian",
    activation: "ACTIVATE CONTINUITY_GUARDIAN",
    role: "Owns cross-clip memory, drift severity, and LAST_FRAME_RECAP validation.",
    skills: ["Recap Validation", "Drift Report", "State Packet", "Block High Risk"],
  },
  {
    id: "identity",
    name: "Identity Lock Specialist",
    activation: "ACTIVATE IDENTITY_LOCK",
    role: "DNA freeze must hold before continuity scores are meaningful.",
    skills: ["DNA Freeze", "Face Drift", "Multi-character"],
  },
  {
    id: "sequence",
    name: "Sequence Director",
    activation: "ACTIVATE SEQUENCE_DIRECTOR",
    role: "Plans clip order and dependencies that continuity must protect.",
    skills: ["Clip Plan", "Dependencies", "Extend Order"],
  },
  {
    id: "extend",
    name: "Cinematic Sequence Extender",
    activation: "ACTIVATE SEQUENCE_EXTENDER",
    role: "Consumes LAST_FRAME_RECAP + momentum for N+1 generation.",
    skills: ["Extend from Frame", "Momentum", "Chain QA"],
  },
  {
    id: "qa",
    name: "Quality Assurance Guardian",
    activation: "ACTIVATE QA_GUARDIAN",
    role: "Final gate; continuity report feeds Go / No-Go.",
    skills: ["Weighted Gate", "Fix List", "Go No-Go"],
  },
];

export const LESSONS: Lesson[] = [
  {
    id: "why-continuity",
    step: "01",
    title: "Why continuity is a gate",
    minutes: "4 min",
    summary:
      "Multi-clip work fails from forgotten state, not missing style words.",
    bullets: [
      "Every extend is a bet that N matches N−1.",
      "Silent drift compounds across a chain.",
      "Activate Continuity Guardian on any project with 2+ clips.",
    ],
    drill: "Name one prop and one emotion that must survive three clips.",
  },
  {
    id: "last-frame",
    step: "02",
    title: "LAST_FRAME_RECAP",
    minutes: "7 min",
    summary:
      "Validate the approved end frame before any extension prompt is written.",
    bullets: [
      "Recap includes pose, gaze, practical light, and exit motion.",
      "Bad recap → model invents a new opening.",
      "Pair with plate_status=locked when possible.",
    ],
    drill: "Write a 4-line recap for a runner exiting a neon alley.",
  },
  {
    id: "state-packet",
    step: "03",
    title: "continuity_state packet",
    minutes: "7 min",
    summary:
      "Wardrobe, props, environment, light, emotion, momentum — one packet.",
    bullets: [
      "Update the packet after every approved clip.",
      "Missing fields are assumed wrong by the next model call.",
      "Intimate work adds EROSFORGE_STATE awareness.",
    ],
    drill: "Fill a mini state packet for a rainy rooftop confrontation.",
  },
  {
    id: "prop-env",
    step: "04",
    title: "Props and environment",
    minutes: "6 min",
    summary:
      "Hero props in/out of frame; weather and time of day stay motivated.",
    bullets: [
      "Track who holds what.",
      "Do not teleport geography between hard cuts.",
      "Production Designer owns set DNA; Continuity enforces it.",
    ],
    drill: "List three environment locks for a single-location chase.",
  },
  {
    id: "emotion-momentum",
    step: "05",
    title: "Emotion and momentum",
    minutes: "6 min",
    summary:
      "Emotional residue and camera/subject vectors continue unless story resets them.",
    bullets: [
      "Peak → residue → next beat; not peak → blank slate.",
      "Momentum vector feeds extend-from-frame.",
      "Hard stops need explicit story motivation.",
    ],
    drill: "Describe residual emotion after a failed interrogation beat.",
  },
  {
    id: "drift-severity",
    step: "06",
    title: "Drift severity and blocks",
    minutes: "6 min",
    summary:
      "Low = note; medium = fix before promote; high = block extend.",
    bullets: [
      "High identity or prop loss is a hard stop.",
      "Fix_list before silent re-roll.",
      "Chain QA and Continuity share the same stop culture.",
    ],
    drill: "Classify: jacket color change mid-chase — severity and fix.",
  },
  {
    id: "timelines",
    step: "07",
    title: "Branches and timelines",
    minutes: "5 min",
    summary:
      "Label timeline_id on every clip in non-linear or A/B structures.",
    bullets: [
      "Unlabeled branches pollute the wrong continuity_state.",
      "Guardian tracks multi-timeline memory.",
      "Assembly must not interleave unlabeled paths.",
    ],
    drill: "Sketch two labeled timelines for a flashback teaser.",
  },
  {
    id: "handoff",
    step: "08",
    title: "Continuity handoff",
    minutes: "5 min",
    summary:
      "Report attaches to Sequence Blueprint before Chain QA and stitch.",
    bullets: [
      "Include recap, state, drift notes, model path (1.0 vs 1.5).",
      "Block list must be empty for extend approval.",
      "Feeds QA Guardian and Assembly Editor.",
    ],
    drill: "List five fields on a CONTINUITY_HANDOFF packet.",
  },
];

export const DRIFT_CHECKS: DriftCheck[] = [
  {
    id: "identity",
    label: "Identity / face",
    critical: true,
    inspect: "DNA match across end frame and next plate",
    recovery: "Re-lock DNA · refuse extend",
  },
  {
    id: "wardrobe",
    label: "Wardrobe",
    critical: true,
    inspect: "Outfit, damage, wet/sweat state",
    recovery: "Restore wardrobe_lock inject",
  },
  {
    id: "props",
    label: "Hero props",
    critical: true,
    inspect: "In-hand / holstered / missing objects",
    recovery: "Re-establish prop in plate",
  },
  {
    id: "environment",
    label: "Environment",
    critical: false,
    inspect: "Weather, TOD, practicals, geography",
    recovery: "Correct set DNA in prompt",
  },
  {
    id: "emotion",
    label: "Emotional residue",
    critical: false,
    inspect: "Affect matches prior peak/resolution",
    recovery: "Write residue into recap",
  },
  {
    id: "momentum",
    label: "Momentum vector",
    critical: false,
    inspect: "Camera and subject exit direction",
    recovery: "Encode vector in extend prompt",
  },
];

export const CONTINUITY_FIELDS: ContinuityField[] = [
  {
    key: "project",
    label: "Project slug",
    hint: "neon-alley-chase",
    required: true,
  },
  {
    key: "clip_id",
    label: "Current clip id",
    hint: "clip_03",
    required: true,
  },
  {
    key: "timeline_id",
    label: "Timeline id",
    hint: "main",
    required: true,
  },
  {
    key: "last_frame_recap",
    label: "LAST_FRAME_RECAP",
    hint: "Runner mid-stride exit left · wet jacket · neon rim from right · breath visible",
    required: true,
  },
  {
    key: "wardrobe",
    label: "Wardrobe state",
    hint: "black runner jacket · torn left sleeve · rain-dark",
    required: true,
  },
  {
    key: "props",
    label: "Props in play",
    hint: "phone in right hand · no weapon",
    required: true,
  },
  {
    key: "environment",
    label: "Environment lock",
    hint: "neon alley · heavy rain · 02:00 · practical red sign",
    required: true,
  },
  {
    key: "emotion",
    label: "Emotional residue",
    hint: "panic cooling into focus · jaw set",
    required: true,
  },
  {
    key: "momentum",
    label: "Momentum vector",
    hint: "subject L→R · slight handheld push",
    required: true,
  },
  {
    key: "drift_notes",
    label: "Drift notes / blocks",
    hint: "none · ready to extend",
    required: true,
  },
];

export const PIPELINE_STEPS = [
  { id: "dna", label: "DNA freeze", detail: "Identity holds" },
  { id: "recap", label: "LAST_FRAME_RECAP", detail: "Validate end frame" },
  { id: "state", label: "continuity_state", detail: "Packet complete" },
  { id: "drift", label: "Drift check", detail: "Severity gate" },
  { id: "extend", label: "Extend / stitch", detail: "Only if clear" },
  { id: "update", label: "Update state", detail: "After approval" },
  { id: "report", label: "Handoff", detail: "Attach to blueprint" },
] as const;

export const ACTIVATION_TEMPLATES = [
  {
    id: "basic",
    title: "Basic continuity check",
    body: `ACTIVATE CONTINUITY_GUARDIAN

Project: {{project}}
Validate LAST_FRAME_RECAP before any extend.
Output: continuity_state packet · drift severity · block list.
Refuse extend on high identity or prop drift.`,
  },
  {
    id: "pre-extend",
    title: "Pre-extend gate",
    body: `ACTIVATE CONTINUITY_GUARDIAN
ACTIVATE SEQUENCE_EXTENDER
VALIDATE LAST_FRAME_RECAP

Project: {{project}}
Clip N approved. Prepare N+1.
Require: recap · wardrobe · props · environment · emotion · momentum.
High drift → fix_list, do not generate.`,
  },
  {
    id: "chain",
    title: "Full chain audit",
    body: `ACTIVATE CONTINUITY_GUARDIAN
ACTIVATE QA_GUARDIAN
RUN CHAIN QA REVIEW

Project: {{project}}
Audit clips 01–N for cumulative drift.
Report timeline labels, missing state fields, and blocked joins.
Attach CONTINUITY_HANDOFF to Sequence Blueprint.`,
  },
  {
    id: "branch",
    title: "Branch / non-linear",
    body: `ACTIVATE CONTINUITY_GUARDIAN

Project: {{project}}
Label timeline_id on every clip.
Do not mix main and flashback state packets.
Output separate continuity_state per timeline.`,
  },
  {
    id: "handoff",
    title: "Handoff packet",
    body: `ACTIVATE CONTINUITY_GUARDIAN

Project: {{project}}
Export CONTINUITY_HANDOFF:
recap · state · drift_notes · model_path · timeline_id · blocks
Pass to Sequence Director / Chain QA / Assembly.`,
  },
] as const;

export const CONTINUITY_QUIZ: QuizItem[] = [
  {
    id: "cq1",
    prompt: "When is LAST_FRAME_RECAP required?",
    options: [
      "Only on the final delivery master",
      "Before every extend or stitch to N+1",
      "Only for stills montages",
      "Never if style is locked",
    ],
    answer: 1,
    explain: "LAST_FRAME_RECAP_REQUIRED — no recap, no extend.",
  },
  {
    id: "cq2",
    prompt: "continuity_state should include:",
    options: [
      "Only the logline",
      "Wardrobe, props, environment, emotion, momentum",
      "Only Camera ISO",
      "Quota remaining % only",
    ],
    answer: 1,
    explain: "CONTINUITY_STATE_PACKET carries the live scene memory.",
  },
  {
    id: "cq3",
    prompt: "Identity drift mid-chain means:",
    options: [
      "Continue and fix in polish",
      "Stop — identity must hold before continuity is trusted",
      "Ignore if props match",
      "Only matters for trailers",
    ],
    answer: 1,
    explain: "IDENTITY_BEFORE_CONTINUITY — face drift voids the chain.",
  },
  {
    id: "cq4",
    prompt: "Hero prop vanishes between clips:",
    options: [
      "Low note only",
      "Critical drift — restore or block extend",
      "Always intentional",
      "Fixed by louder score",
    ],
    answer: 1,
    explain: "PROP_MEMORY treats hero object loss as critical.",
  },
  {
    id: "cq5",
    prompt: "Emotional residue means:",
    options: [
      "Reset to neutral every cut",
      "Carry affect from the prior beat unless story resets it",
      "Only applies to VO",
      "Ignore for action scenes",
    ],
    answer: 1,
    explain: "EMOTIONAL_RESIDUE keeps drama continuous.",
  },
  {
    id: "cq6",
    prompt: "High drift severity should:",
    options: [
      "Be ignored if the still is pretty",
      "Block extension until fix_list clears",
      "Only appear in footnotes",
      "Trigger automatic 1.5 spend",
    ],
    answer: 1,
    explain: "BLOCK_ON_HIGH_DRIFT — hard stop culture.",
  },
  {
    id: "cq7",
    prompt: "Branching narratives require:",
    options: [
      "One shared unlabeled state",
      "timeline_id labels and separate state packets",
      "No continuity tracking",
      "Only hard cuts",
    ],
    answer: 1,
    explain: "TIMELINE_LABEL prevents cross-branch pollution.",
  },
  {
    id: "cq8",
    prompt: "CONTINUITY_HANDOFF is passed to:",
    options: [
      "Only social media",
      "Sequence Blueprint / Chain QA / Assembly before extend approval",
      "Pricing page only",
      "Graduate certificate only",
    ],
    answer: 1,
    explain: "CONTINUITY_HANDOFF feeds the production chain, not marketing alone.",
  },
];

export function buildContinuityPacket(
  values: Record<string, string>,
  stamp: string,
): string {
  const project = values.project?.trim() || "untitled";
  return `CONTINUITY_HANDOFF
stamp: ${stamp}
project: ${project}
clip_id: ${values.clip_id?.trim() || "—"}
timeline_id: ${values.timeline_id?.trim() || "main"}
last_frame_recap: ${values.last_frame_recap?.trim() || "—"}
wardrobe: ${values.wardrobe?.trim() || "—"}
props: ${values.props?.trim() || "—"}
environment: ${values.environment?.trim() || "—"}
emotion_residue: ${values.emotion?.trim() || "—"}
momentum_vector: ${values.momentum?.trim() || "—"}
drift_notes: ${values.drift_notes?.trim() || "—"}

policy: LAST_FRAME_RECAP_REQUIRED · CONTINUITY_STATE_PACKET · BLOCK_ON_HIGH_DRIFT · IDENTITY_BEFORE_CONTINUITY
next: clear blocks → extend/stitch → update state after approval
`;
}

export function buildDirectorActivation(project: string): string {
  return `ACTIVATE CONTINUITY_GUARDIAN
ACTIVATE SEQUENCE_DIRECTOR

Project: ${project || "untitled"}
Validate LAST_FRAME_RECAP before every extend.
Maintain continuity_state (wardrobe · props · env · emotion · momentum).
Block high drift. Label timelines. Attach CONTINUITY_HANDOFF to blueprint.`;
}
