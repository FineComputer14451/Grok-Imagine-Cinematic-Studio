export type MoveType = {
  id: string;
  name: string;
  short: string;
  body: string;
  energy: "static" | "slow" | "medium" | "fast";
  stillsNote: string;
  videoNote: string;
  packet: string;
  avoid: string;
  pairsWith: string;
};

export type MoveTopic = {
  id: string;
  title: string;
  short: string;
  body: string;
  rule: string;
  studioTip: string;
  level: "basics" | "craft" | "imagine";
};

export type MoveRecipe = {
  id: string;
  name: string;
  mood: string;
  moves: string;
  duration: string;
  plate: string;
  when: string;
  packet: string;
};

export const MOVE_TYPES: MoveType[] = [
  {
    id: "static",
    name: "Static / locked-off",
    short: "Tripod energy — no camera move.",
    body: "Camera position and angle fixed. Motion comes only from subject, weather, light flicker, or practicals. Cleanest for identity plates and stills-first workflows.",
    energy: "static",
    stillsNote: "Default for DNA locks and hero stills",
    videoNote: "Hold frame; micro subject motion only",
    packet: "locked-off camera, static frame, no pan or push",
    avoid: "Accidental handheld shake language",
    pairsWith: "50mm identity · plate lock before video",
  },
  {
    id: "pan",
    name: "Pan",
    short: "Rotate left/right on a fixed point.",
    body: "Reveals space laterally or follows a subject crossing frame. Speed sells intention: slow = observe, whip = transition/energy.",
    energy: "slow",
    stillsNote: "Describe as “pan implied composition” only if needed",
    videoNote: "slow pan left-to-right following subject",
    packet: "slow pan right, subject tracked center-left, horizon level",
    avoid: "Whip pan every shot",
    pairsWith: "Wide geography · 24–35mm",
  },
  {
    id: "tilt",
    name: "Tilt",
    short: "Rotate up/down on a fixed point.",
    body: "Reveals height — building, figure rising, candle lift. Often paired with low angle starts.",
    energy: "slow",
    stillsNote: "Prefer static low/high angle stills instead",
    videoNote: "slow tilt up from boots to face",
    packet: "slow tilt up, starting at hands/prop, ending on face",
    avoid: "Seasick continuous tilt loops",
    pairsWith: "Gothic corridors · power angles",
  },
  {
    id: "push",
    name: "Push-in / dolly in",
    short: "Camera moves closer to subject.",
    body: "Increases intimacy and pressure. Classic on hero faces and decision moments. Distinguish from zoom (perspective changes when you dolly).",
    energy: "slow",
    stillsNote: "Hero still = end frame of a push",
    videoNote: "slow push-in on face, 6s",
    packet: "slow push-in toward subject, locked horizon, ending medium close-up",
    avoid: "Crash zooms unless genre asks",
    pairsWith: "Neon hero A02 · plate→6s scenario",
  },
  {
    id: "pull",
    name: "Pull-out / dolly out",
    short: "Camera moves away — reveal or isolation.",
    body: "Reveals environment around a subject or leaves them small in frame. Emotional “you’re alone in this world.”",
    energy: "slow",
    stillsNote: "End frame often EWS/WS",
    videoNote: "slow pull-out revealing alley depth",
    packet: "slow pull-out, subject shrinks in frame, environment expands",
    avoid: "Pulling out so far identity is lost mid-clip",
    pairsWith: "Teaser openers reversed · geography",
  },
  {
    id: "track",
    name: "Track / truck",
    short: "Lateral move parallel to subject or set.",
    body: "Walks beside a character or slides along architecture. Maintains profile or three-quarter while world streams past.",
    energy: "medium",
    stillsNote: "Motion blur language optional in stills",
    videoNote: "lateral track keeping subject frame-left",
    packet: "lateral tracking shot, subject left third, background streaming right",
    avoid: "Track + dutch + whip all at once",
    pairsWith: "Courier walk · 35mm",
  },
  {
    id: "orbit",
    name: "Orbit / arc",
    short: "Camera circles subject.",
    body: "Heroic or tense 3D read of a character. Easy to overuse in generative video — keep arcs short and motivated.",
    energy: "medium",
    stillsNote: "Prefer two still angles over fake orbit still",
    videoNote: "slow 30° arc around subject, end on three-quarter",
    packet: "slow arc around subject, maintaining eye-level, 6s",
    avoid: "Full 360 every teaser",
    pairsWith: "Hero identity flex · after plate lock",
  },
  {
    id: "handheld",
    name: "Handheld",
    short: "Human micro-instability.",
    body: "Documentary urgency or anxiety. Needs restraint: “subtle handheld” ≠ earthquake. Identity locks are harder — prefer static for DNA plates.",
    energy: "medium",
    stillsNote: "Usually avoid for face locks",
    videoNote: "subtle handheld, controlled, no whip",
    packet: "subtle handheld camera, natural micro-movement, horizon mostly level",
    avoid: "Handheld on every shot in a polished noir",
    pairsWith: "Found-moment beats · chase fragments",
  },
  {
    id: "crane",
    name: "Crane / jib / boom",
    short: "Vertical or sweeping path through space.",
    body: "Rises over crowds or drops into a scene. Big “movie” grammar — save for act punctuation, not every clip.",
    energy: "medium",
    stillsNote: "Describe end height in still instead",
    videoNote: "crane up from street to neon signs",
    packet: "slow crane up, starting eye-level on subject, rising to wide alley",
    avoid: "Crane + orbit + whip stack",
    pairsWith: "Trailer button shots",
  },
  {
    id: "fpv",
    name: "FPV / rush",
    short: "Aggressive fly-through energy.",
    body: "High-speed immersive path. Expensive-feeling and easy to artifact. Use sparingly; never as identity plate language.",
    energy: "fast",
    stillsNote: "Not for DNA",
    videoNote: "only if Bible/genre demands; short duration",
    packet: "fast FPV rush down corridor, motion blur, brief 2–4s energy",
    avoid: "FPV for dialogue faces",
    pairsWith: "Action trailers · not Candle Hall",
  },
];

export const MOVE_TOPICS: MoveTopic[] = [
  {
    id: "motivated",
    title: "Motivated movement",
    short: "Move because story or subject asks.",
    body: "Camera should follow attention, power, or geography — not decorate. If the actor walks, track or pan can be motivated. If nothing changes, static is a choice, not a failure.",
    rule: "Write the why in shot notes: “push for pressure,” not only “push.”",
    studioTip: "Shot list notes field is the motivation line.",
    level: "basics",
  },
  {
    id: "stills-first",
    title: "Stills-first movement",
    short: "Lock plates static; add motion after.",
    body: "Studio Academy bias: generate identity and lighting on locked-off stills, then promote one plate to a single simple move (usually slow push-in).",
    rule: "No video move language until plate_status locked.",
    studioTip: "Plate → 6s scenario defaults to slow push-in.",
    level: "basics",
  },
  {
    id: "speed",
    title: "Speed & duration",
    short: "Slow reads intentional; fast burns budget.",
    body: "On short clips (6s), one slow move is plenty. Fast moves demand more temporal coherence and fail more often. Match speed to music later — don’t max energy in every beat.",
    rule: "One primary move per short clip.",
    studioTip: "Budget: fewer seconds + simpler move = cheaper QA.",
    level: "craft",
  },
  {
    id: "axis",
    title: "Axis & horizon",
    short: "Keep spatial grammar while moving.",
    body: "Pans/tracks should respect the 180° line and horizon unless dutch is intentional. Crossing axis mid-move confuses screen direction.",
    rule: "State horizon: level | slight dutch.",
    studioTip: "Recap framing should note height + side before extend moves.",
    level: "craft",
  },
  {
    id: "parallax",
    title: "Parallax & depth",
    short: "Move sells 3D when layers exist.",
    body: "Dolly and track shine when FG/MG/BG exist (rain, signs, door frames). Flat stages make moves feel like slides. Build depth in stills first.",
    rule: "Environment prompt needs layers if you plan a track/push.",
    studioTip: "Lighting practicals in depth help motion read.",
    level: "craft",
  },
  {
    id: "zoom-vs-dolly",
    title: "Zoom vs dolly",
    short: "Different perspective behavior.",
    body: "Dolly changes perspective (foreground shifts vs background). Zoom crops FOV with less perspective shift. Generative prompts should prefer “push-in / dolly” or “snap zoom” explicitly — don’t say only “zoom” if you mean physical pressure.",
    rule: "Prefer dolly/push language for cinematic pressure.",
    studioTip: "Packet: “slow push-in (dolly), not zoom.”",
    level: "craft",
  },
  {
    id: "prompt",
    title: "Movement in Imagine video",
    short: "One verb, one direction, one speed.",
    body: "Pattern: [speed] [move] [direction] [end framing]. Example: “slow push-in toward face, end MCU, locked horizon.” Stacking five moves causes mush.",
    rule: "Single motion sentence per 6s clip.",
    studioTip: "Handoff motion_vector field = this sentence.",
    level: "imagine",
  },
  {
    id: "extend",
    title: "Movement across extends",
    short: "motion_out in LAST_FRAME_RECAP.",
    body: "Clip N should declare how energy exits the frame so N+1 can continue or settle. Don’t restart a random orbit after a static hold without a beat change.",
    rule: "Recap motion_out must match planned N+1 move.",
    studioTip: "Recap builder → motion out field.",
    level: "imagine",
  },
];

export const MOVE_RECIPES: MoveRecipe[] = [
  {
    id: "plate-push",
    name: "Locked plate → push",
    mood: "Pressure / hero",
    moves: "Static still → slow push-in video",
    duration: "6s",
    plate: "MCU or MS hero locked",
    when: "First video after identity gate",
    packet:
      "from locked plate: slow push-in toward subject, 6s, horizon level, end tighter MCU, no orbit",
  },
  {
    id: "alley-track",
    name: "Alley track",
    mood: "Courier motion",
    moves: "Lateral track with walk",
    duration: "6s",
    plate: "MS walking plate optional",
    when: "Neon sequence motion beat",
    packet:
      "lateral track left-to-right, subject left third, rain, neon streaming, 35mm feel, 6s",
  },
  {
    id: "hall-creep",
    name: "Hall creep",
    mood: "Unease",
    moves: "Slow push along corridor axis",
    duration: "6s",
    plate: "Wide corridor with candle",
    when: "Candle Hall after plate lock",
    packet:
      "slow creep forward down corridor, candle height constant, slight dutch hold, 24mm, 6s",
  },
  {
    id: "static-rain",
    name: "Static rain hold",
    mood: "Observational noir",
    moves: "Locked-off · world moves",
    duration: "6s",
    plate: "Any locked hero/support",
    when: "Cheapest coherent motion test",
    packet:
      "locked-off static camera, subject still, rain and neon flicker only, 6s",
  },
  {
    id: "reveal-pull",
    name: "Reveal pull-out",
    mood: "Scale / isolation",
    moves: "Slow pull-out to wide",
    duration: "6–10s if available",
    plate: "MCU start preferred",
    when: "Teaser button / final beat",
    packet:
      "slow pull-out from MCU to wide, subject becomes small, environment readable, horizon level",
  },
];

export const MOVE_LEVELS = [
  { id: "basics" as const, label: "Basics" },
  { id: "craft" as const, label: "Craft" },
  { id: "imagine" as const, label: "Imagine" },
];

export const ENERGY_TONE: Record<MoveType["energy"], string> = {
  static: "border-border bg-elevated text-muted",
  slow: "border-teal/40 bg-teal/10 text-teal",
  medium: "border-amber/40 bg-amber/10 text-amber",
  fast: "border-danger/40 bg-danger/10 text-danger",
};
