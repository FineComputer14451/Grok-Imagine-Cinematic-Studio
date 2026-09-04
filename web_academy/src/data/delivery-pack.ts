/** Delivery pack — Studio Academy (ship gate, masters, client package) */

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

export type QuizItem = {
  id: string;
  prompt: string;
  options: string[];
  answer: number;
  explain: string;
};

export const DELIVERY_PACK_VERSION = "4.5";
export const ACADEMY_MODULE_VERSION = "3.11.4";

export const DELIVERY_PACK_TAGLINE =
  "Final ship gate — blockers clear, picture lock, masters, variants, and client package without reopening the cut.";

export const PROTOCOLS: Protocol[] = [
  {
    id: "blockers-first",
    name: "BLOCKERS_FIRST",
    requirement:
      "Never export masters while pre-flight blockers are open (Bible, DNA, DoP, shots, budget).",
    why: "Shipping on unlocked identity or look freezes the wrong production.",
  },
  {
    id: "qa-go",
    name: "QA_GO_REQUIRED",
    requirement:
      "Chain QA Go (or explicit stills-only path) before stitch, polish, or client handoff.",
    why: "No-Go clips in a master become the brand memory.",
  },
  {
    id: "picture-lock",
    name: "PICTURE_LOCK_BEFORE_MASTERS",
    requirement:
      "Picture lock true before multi-ratio masters, heavy grade, or AI polish.",
    why: "Upscale and variants on a moving EDL burn quota and freeze wrong cuts.",
  },
  {
    id: "stills-valid",
    name: "STILLS_SHIP_VALID",
    requirement:
      "A complete stills montage with locked look is a valid full delivery — video is optional.",
    why: "Quota and gates often land stills first. Marketing can ship.",
  },
  {
    id: "one-package",
    name: "ONE_PACKAGE",
    requirement:
      "Client receives one package: pack export, masters, checklist report, rights/cost note.",
    why: "Folders of unlabeled drafts are not delivery.",
  },
  {
    id: "aspect-lock",
    name: "ASPECT_LOCK",
    requirement:
      "Export only planned aspects (2.39 / 16:9 / 9:16). Reframe; do not stretch.",
    why: "Squashed social cuts look unprofessional and break titles.",
  },
  {
    id: "negatives",
    name: "NEGATIVES_PRESENT",
    requirement:
      "Final generation packets still carry negatives and DNA inject where identity is frozen.",
    why: "Last-minute freestyle without DNA drifts the hero.",
  },
  {
    id: "cost-note",
    name: "COST_NOTE",
    requirement:
      "Attach session quota/cost note to the package for the next producer handoff.",
    why: "Economics must travel with the cut.",
  },
];

export const PACK_AGENTS: PackAgent[] = [
  {
    id: "director",
    name: "Studio Director",
    activation: "ACTIVATE STUDIO_DIRECTOR",
    role: "Final ship authority — blockers, package, client go.",
    skills: ["Ship Gate", "Package", "Client Go", "Stop on No-Go"],
  },
  {
    id: "assembly",
    name: "Assembly Editor",
    activation: "ACTIVATE ASSEMBLY_EDITOR",
    role: "Picture-locked EDL only from Go-set before masters.",
    skills: ["EDL", "Picture Lock", "Hard Cuts", "Button"],
  },
  {
    id: "polish",
    name: "AI Polish Director",
    activation: "ACTIVATE AI_POLISH_DIRECTOR",
    role: "Post-lock upscale/restore only after QA Go and picture lock.",
    skills: ["Upscale", "Face Restore", "Artifact Clean", "Masters"],
  },
  {
    id: "quota",
    name: "Workflow Quota Optimizer",
    activation: "ACTIVATE QUOTA_OPTIMIZER",
    role: "Cost note and remaining-quota honesty on the package.",
    skills: ["Cost Note", "Reserve", "Stills First"],
  },
];

export const LESSONS: Lesson[] = [
  {
    id: "why-delivery",
    step: "01",
    title: "Why delivery is a gate",
    minutes: "4 min",
    summary:
      "Delivery is the ship decision — not a folder dump of every render.",
    bullets: [
      "Blockers protect identity and look before spend becomes permanent.",
      "Stills-first packages are complete products.",
      "One package beats twenty unlabeled MP4s.",
    ],
    drill: "Name three items that must be true before client export.",
  },
  {
    id: "preflight",
    step: "02",
    title: "Pre-flight blockers",
    minutes: "6 min",
    summary:
      "Bible, DNA, DoP, shot list, budget — red means no hero spend.",
    bullets: [
      "Blockers are not optional etiquette; they are spend gates.",
      "Fix red items before generation, not after polish.",
      "Link each blocker to its Academy tool page.",
    ],
    drill: "Order the five pre-flight blockers by failure cost.",
  },
  {
    id: "qa-and-lock",
    step: "03",
    title: "QA Go and picture lock",
    minutes: "6 min",
    summary:
      "Chain QA Go → stitch → picture lock → then polish and masters.",
    bullets: [
      "No-Go means fix_list, not silent export.",
      "Picture lock freezes the cut for grade and upscale.",
      "Stills-only path skips video QA but not identity gates.",
    ],
    drill: "Write the gate order from plate lock to master export.",
  },
  {
    id: "package",
    step: "04",
    title: "The one package",
    minutes: "7 min",
    summary:
      "Project pack + masters + checklist report + cost/rights note.",
    bullets: [
      "Pack export holds Bible, DNA, DoP, shots, activation.",
      "Masters only for planned aspects.",
      "Checklist report proves what was verified.",
    ],
    drill: "List the four files/sections in a client package.",
  },
  {
    id: "variants",
    step: "05",
    title: "Aspects and variants",
    minutes: "5 min",
    summary:
      "Ship only planned ratios. Reframe from locked plates.",
    bullets: [
      "9:16 needs title-safe and face priority.",
      "Do not stretch 2.39 into vertical.",
      "Polish multi-ratio after lock only.",
    ],
    drill: "Note crop priority for a face button in 9:16 vs 2.39.",
  },
  {
    id: "ship",
    step: "06",
    title: "Ship order",
    minutes: "5 min",
    summary:
      "Checklist → fix red → pack → hero still → optional video → edit → sound → done.",
    bullets: [
      "Follow SHIP_ORDER; skip steps only with explicit stills-first intent.",
      "Stop on identity No-Go at any step.",
      "Graduate only after practice, not before ship discipline.",
    ],
    drill: "Mark which ship steps are optional on a stills-only teaser.",
  },
];

export const PIPELINE_STEPS = [
  { id: "preflight", label: "Pre-flight", detail: "Blockers clear" },
  { id: "generate", label: "Generate", detail: "DNA · plates · QA" },
  { id: "lock", label: "Picture lock", detail: "Go-set EDL frozen" },
  { id: "polish", label: "Polish", detail: "Masters · variants" },
  { id: "package", label: "Package", detail: "Pack + report + cost" },
  { id: "ship", label: "Ship", detail: "Client go" },
] as const;

export const ACTIVATION_TEMPLATES = [
  {
    id: "checklist",
    title: "Run delivery checklist",
    body: `ACTIVATE STUDIO_DIRECTOR\n\nProject: {{project}}\nRun Delivery checklist end-to-end.\nReport: blockers open · QA status · picture lock · package contents.\nStop on any identity No-Go. Stills-first valid.`,
  },
  {
    id: "stills-ship",
    title: "Stills-only ship",
    body: `ACTIVATE STUDIO_DIRECTOR\nACTIVATE QUOTA_OPTIMIZER\n\nProject: {{project}}\nStills-only delivery path.\nConfirm: DNA · DoP · shot list · plate lock · edit spine · silent or bed.\nExport pack + checklist report. No video required.`,
  },
  {
    id: "full-masters",
    title: "Full masters path",
    body: `ACTIVATE STUDIO_DIRECTOR\nACTIVATE ASSEMBLY_EDITOR\nACTIVATE AI_POLISH_DIRECTOR\n\nProject: {{project}}\nQA Go + picture lock required.\nPolish after lock. Export planned aspects only.\nAttach cost note and rights. One client package.`,
  },
] as const;

export const DELIVERY_QUIZ: QuizItem[] = [
  {
    id: "dq1",
    prompt: "When may you export multi-ratio masters?",
    options: [
      "As soon as the first still looks good",
      "After picture lock and blockers clear",
      "Only on Fridays",
      "Before DNA freeze",
    ],
    answer: 1,
    explain: "PICTURE_LOCK_BEFORE_MASTERS — freeze the cut first.",
  },
  {
    id: "dq2",
    prompt: "Is a stills-only package a valid delivery?",
    options: [
      "No — video is always required",
      "Yes — when look and identity are locked",
      "Only for ErosForge",
      "Only if quota is empty",
    ],
    answer: 1,
    explain: "STILLS_SHIP_VALID — marketing can ship without video.",
  },
  {
    id: "dq3",
    prompt: "What belongs in the one client package?",
    options: [
      "Every draft render unlabeled",
      "Pack export, masters, checklist report, cost/rights note",
      "Only a Drive folder link with no notes",
      "DNA only",
    ],
    answer: 1,
    explain: "ONE_PACKAGE — one coherent handoff.",
  },
  {
    id: "dq4",
    prompt: "Open pre-flight blocker means:",
    options: [
      "Ship anyway and fix later",
      "No hero spend or master export until cleared",
      "Skip DNA forever",
      "Only affects sound",
    ],
    answer: 1,
    explain: "BLOCKERS_FIRST — red items stop the ship.",
  },
  {
    id: "dq5",
    prompt: "Platform variants should:",
    options: [
      "Stretch scope to 9:16",
      "Reframe from locked plates for planned aspects only",
      "Ignore title safe areas",
      "Run before picture lock",
    ],
    answer: 1,
    explain: "ASPECT_LOCK — reframe, do not squash.",
  },
  {
    id: "dq6",
    prompt: "Chain QA No-Go at delivery time means:",
    options: [
      "Polish harder until it passes",
      "Stop — fix_list before stitch or export",
      "Delete the checklist",
      "Ship with a disclaimer only",
    ],
    answer: 1,
    explain: "QA_GO_REQUIRED — No-Go is a hard stop.",
  },
];

export function buildDirectorActivation(project: string): string {
  return `ACTIVATE STUDIO_DIRECTOR\n\nProject: ${project || "untitled"}\nRun Delivery checklist. Clear blockers. Require QA Go and picture lock before masters.\nStills-first valid. One package: pack + masters + report + cost note.\nStop on identity No-Go.`;
}
