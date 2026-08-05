export type QuizQuestion = {
  id: string;
  tier: 1 | 2 | 3;
  prompt: string;
  options: string[];
  /** Index into options */
  answer: number;
  explain: string;
};

export const QUIZ_QUESTIONS: QuizQuestion[] = [
  {
    id: "q1",
    tier: 1,
    prompt: "What is the minimum viable path to a cinematic still?",
    options: [
      "Full 25-agent studio activation",
      "One strong Imagine prompt",
      "Production Bible + Character DNA",
      "Trailer Director only",
    ],
    answer: 1,
    explain:
      "Tier 1 is single-agent: a direct Grok Imagine prompt (Prompt Master / raw model) is enough for a still.",
  },
  {
    id: "q2",
    tier: 1,
    prompt: "Best order for a cinematic still prompt?",
    options: [
      "Mood → lens → subject → lighting → environment",
      "Subject → environment → lighting → lens → mood",
      "Lens → mood → environment → subject → lighting",
      "Lighting → mood → lens → subject → environment",
    ],
    answer: 1,
    explain:
      "Lead with what is in frame (subject + place), then light and optics, finish with emotional mood.",
  },
  {
    id: "q3",
    tier: 1,
    prompt: "Do you need full studio activation for a single still?",
    options: [
      "Yes — always load all 25 agents",
      "Yes — at least Studio Director",
      "No — raw Imagine is enough",
      "Only if using Video 1.5",
    ],
    answer: 2,
    explain:
      "Full activation is optional. A single still works without the multi-agent pipeline.",
  },
  {
    id: "q4",
    tier: 2,
    prompt: "Which pair is the core Tier 2 handoff?",
    options: [
      "QA Guardian + AI Polish Director",
      "Studio Director + Imagine Prompt Master",
      "ErosForge + Foley Specialist",
      "Stunt Choreographer + VFX Supervisor",
    ],
    answer: 1,
    explain:
      "Director locks the brief and shot list; Prompt Master turns it into production-ready Imagine packets.",
  },
  {
    id: "q5",
    tier: 2,
    prompt: "What does Studio Director lock before Prompt Master writes packets?",
    options: [
      "Final color grade only",
      "Creative brief and shot list",
      "Native audio beds only",
      "Delivery package zip",
    ],
    answer: 1,
    explain:
      "Tier 2 starts with a locked creative brief + shot list so prompts stay consistent across shots.",
  },
  {
    id: "q6",
    tier: 2,
    prompt: "Which is a valid gate before the next shot?",
    options: [
      "Identity / framing / lighting",
      "Only the Git commit hash",
      "Client social handle",
      "Random seed only",
    ],
    answer: 0,
    explain:
      "Check face continuity, framing, and lighting match before spending another generation.",
  },
  {
    id: "q7",
    tier: 3,
    prompt: "What does Mega Production Architect lock first?",
    options: [
      "Trailer cut only",
      "Production Bible (+ VIDEO_PIPELINE_SPEC)",
      "Foley layers only",
      "Quota dashboard screenshot",
    ],
    answer: 1,
    explain:
      "The Production Bible (world, tone, deliverables, VIDEO_PIPELINE_SPEC) is the Tier 3 foundation.",
  },
  {
    id: "q8",
    tier: 3,
    prompt: "What does Identity Lock Specialist freeze?",
    options: [
      "Only the music temp track",
      "Face, wardrobe, and continuity rules (Character DNA)",
      "Only the export resolution",
      "Only the project title card",
    ],
    answer: 1,
    explain:
      "Character DNA locks face, wardrobe, and continuity so multi-clip sequences do not drift.",
  },
  {
    id: "q9",
    tier: 3,
    prompt: "Correct pipeline order?",
    options: [
      "Shoot → Bible → DNA → Handoff → QA → Post → Delivery",
      "Bible → DNA → Pre-Prod → Shoot → Handoff → QA → Post → Delivery",
      "DNA → Delivery → Bible → Shoot → QA",
      "Handoff → Bible → DNA → Shoot → Delivery",
    ],
    answer: 1,
    explain:
      "Bible → DNA → Pre-Prod → Shoot → Handoff → QA → Post → Delivery is the Studio Academy map.",
  },
  {
    id: "q10",
    tier: 3,
    prompt: "When should you prefer Video 1.5 over 1.0?",
    options: [
      "Always for still images only",
      "Native audio, stronger physics, image/voice refs, intimacy-safe motion",
      "Only when offline",
      "Never — 1.0 is always better",
    ],
    answer: 1,
    explain:
      "1.5 is for synchronized audio, improved physics, reference conditioning, and longer chainable motion.",
  },
];

export function scoreBand(score: number, total: number) {
  const pct = total === 0 ? 0 : score / total;
  if (pct >= 0.8)
    return {
      label: "Solid",
      tone: "success" as const,
      detail: "You know the tiers well. Ready for full pipeline work.",
    };
  if (pct >= 0.5)
    return {
      label: "Review Learn path",
      tone: "amber" as const,
      detail: "Revisit Tier 2–3 and the pipeline map, then retry.",
    };
  return {
    label: "Stay on Tier 1–2",
    tone: "danger" as const,
    detail: "Master single prompts and Director + Prompt Master before scaling.",
  };
}
