export type EditTopic = {
  id: string;
  title: string;
  short: string;
  body: string;
  rule: string;
  studioTip: string;
  level: "basics" | "craft" | "imagine";
};

export type CutType = {
  id: string;
  name: string;
  short: string;
  body: string;
  when: string;
  avoid: string;
  packet: string;
};

export type PaceRecipe = {
  id: string;
  name: string;
  mood: string;
  structure: string;
  durations: string;
  music: string;
  when: string;
  checklist: string[];
};

export const CUT_TYPES: CutType[] = [
  {
    id: "hard",
    name: "Hard cut",
    short: "Instant switch A→B.",
    body: "Default edit. Energy comes from shot choice and timing, not transitions. Most Studio teaser cuts should be hard cuts.",
    when: "Nearly always for short trailers",
    avoid: "Using fades as decoration between every shot",
    packet: "hard cut on action / on beat",
  },
  {
    id: "match",
    name: "Match cut",
    short: "Graphic or motion continuity across shots.",
    body: "Shape, direction, or action aligns at the cut (door slam → footstep). Feels smart when planned in shot list.",
    when: "Hero moments, title accents",
    avoid: "Forced matches that break geography",
    packet: "match cut: [element] continues across shot A and B",
  },
  {
    id: "jcut-lcut",
    name: "J-cut / L-cut",
    short: "Audio leads or lags picture.",
    body: "J-cut: hear next scene before see it. L-cut: picture changes, prior audio holds. Needs sound design; pure silent still sequences skip this.",
    when: "Dialogue-ish or VO trailers",
    avoid: "Claiming J/L cuts with no audio plan",
    packet: "J-cut: next scene SFX under outgoing picture",
  },
  {
    id: "smash",
    name: "Smash cut",
    short: "Abrupt contrast for shock or humor.",
    body: "Quiet hold → loud impact, or reverse. Use once per short piece max.",
    when: "Trailer button, comic beat",
    avoid: "Smash every cut",
    packet: "smash cut to silence / impact still",
  },
  {
    id: "dissolve",
    name: "Dissolve / fade",
    short: "Time pass or soft mood shift.",
    body: "Signals elapsed time or dream. Softens urgency — often wrong for noir chase teasers.",
    when: "Memory inserts, mono flashbacks",
    avoid: "Default between every plate",
    packet: "slow dissolve to memory insert",
  },
  {
    id: "cross",
    name: "Cross-cut / parallel",
    short: "Alternate two storylines.",
    body: "A/B/A/B builds tension. Needs clear geography labels so viewers track both lines.",
    when: "Longer trailers with two threads",
    avoid: "Cross-cutting with only one clear story",
    packet: "cross-cut: courier / pursuer every 2s",
  },
];

export const EDIT_TOPICS: EditTopic[] = [
  {
    id: "why",
    title: "Editing is selection",
    short: "What you leave out matters most.",
    body: "Editing is not software — it’s choosing order, duration, and emphasis. For Studio Academy, that means which stills become heroes, which 6s clips survive QA, and how they sequence into a teaser.",
    rule: "Kill good shots that don’t serve the logline.",
    studioTip: "Shot list priority (hero/support/draft) is pre-editing.",
    level: "basics",
  },
  {
    id: "order",
    title: "Shot order & story spine",
    short: "Establish → complicate → button.",
    body: "Classic short teaser spine: geography wide, character medium, identity close or emotional peak, optional motion, button image. Don’t start on ECU unless mystery is the point.",
    rule: "Audience must know place or person within first 2 shots.",
    studioTip: "Project pack shot order is a first assemble.",
    level: "basics",
  },
  {
    id: "duration",
    title: "Duration & rhythm",
    short: "How long a shot lives on screen.",
    body: "Wides can hold longer; CUs burn faster. Music tempo and speech dictate pace. For silent still montages, 1.5–3s per still is a common teaser range.",
    rule: "Vary length — uniform 2s every shot feels robotic.",
    studioTip: "6s Imagine clips often = one beat each in a 24s teaser.",
    level: "basics",
  },
  {
    id: "continuity-edit",
    title: "Continuity vs montage",
    short: "Seamless space vs idea collision.",
    body: "Continuity editing hides cuts (screen direction, match action). Montage collides images for meaning. Trailers mix both: continuity inside a beat, montage across acts.",
    rule: "Don’t break 180° mid-conversation beat unless intentional.",
    studioTip: "Framing module 180° + Movement axis notes apply here.",
    level: "craft",
  },
  {
    id: "eyeline-cut",
    title: "Eyeline & motivation",
    short: "Cut where attention goes.",
    body: "If a character looks off-screen, the next shot often answers that look. Motivated cuts feel invisible; unmotivated jumps feel like errors.",
    rule: "Ask: why this image now?",
    studioTip: "Recap motion_out can motivate the next clip’s open.",
    level: "craft",
  },
  {
    id: "audio",
    title: "Picture locked to sound",
    short: "Cut on beats, hits, breaths.",
    body: "Even placeholder ticks help. Whooshes cover hard cuts; music drops land on button stills. Academy SFW trailers: plan a simple bed before final stitch.",
    rule: "One accent hit per major cut, not every frame.",
    studioTip: "Budget chat time for music brief if using agents.",
    level: "craft",
  },
  {
    id: "stills-montage",
    title: "Stills-first montage",
    short: "No video yet — still cut as teaser.",
    body: "Valid delivery: 4–8 locked stills on a 15–30s timeline with pans/zooms (Ken Burns) or hard cuts. Cheaper, often cleaner than forced motion.",
    rule: "Prefer still montage over failed video loops.",
    studioTip: "Quota Optimizer loves stills-first teasers.",
    level: "imagine",
  },
  {
    id: "qa-edit",
    title: "QA before stitch",
    short: "Don’t assemble No-Go clips.",
    body: "Chain QA and identity gates happen before editorial polish. Fix list first. Stitching drift multiplies cost.",
    rule: "No stitch on identity No-Go.",
    studioTip: "Consistency algorithms · QA stage.",
    level: "imagine",
  },
];

export const PACE_RECIPES: PaceRecipe[] = [
  {
    id: "15s-still",
    name: "15s still teaser",
    mood: "Minimal · portfolio",
    structure: "Wide → medium → CU → button",
    durations: "3s · 4s · 4s · 4s (still holds)",
    music: "Low pulse or silence + one riser",
    when: "Tier 1–2 demos, DNA proof",
    checklist: [
      "4 hero/support stills only",
      "Same DoP grade",
      "Hard cuts or soft push on stills",
      "End on strongest face or motif",
    ],
  },
  {
    id: "24s-hybrid",
    name: "24s hybrid",
    mood: "Neon trailer sketch",
    structure: "Still establish → 6s push → still CU → 6s track → button still",
    durations: "3s still · 6s clip · 3s still · 6s clip · 6s button",
    music: "Beat every ~2s; hit on button",
    when: "After plate→6s scenario",
    checklist: [
      "Both clips QA Go",
      "DNA continuous",
      "One move type per clip",
      "Budget counted for 2×6s video",
    ],
  },
  {
    id: "candle-slow",
    name: "Slow gothic hold",
    mood: "Unease",
    structure: "Wide corridor · face flame · optional creep · black",
    durations: "5s · 6s · 6s · 2s out",
    music: "Sparse drones · no busy percussion",
    when: "Candle Hall study",
    checklist: [
      "Candle prop side locked",
      "No smash cuts",
      "Grade warm/cool consistent",
      "Allow longer holds",
    ],
  },
  {
    id: "montage-idea",
    name: "Idea montage",
    mood: "Meaning over geography",
    structure: "5–7 stills colliding motif",
    durations: "1.5–2.5s each",
    music: "Rhythmic cuts on beat",
    when: "Title sequence experiments",
    checklist: [
      "Motif repeats (neon, rain, eyes)",
      "Aspect locked",
      "Avoid random stock energy",
      "Bible logline still true",
    ],
  },
];

export const EDIT_LEVELS = [
  { id: "basics" as const, label: "Basics" },
  { id: "craft" as const, label: "Craft" },
  { id: "imagine" as const, label: "Imagine" },
];
