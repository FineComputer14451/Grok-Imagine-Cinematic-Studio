export type CompTopic = {
  id: string;
  title: string;
  short: string;
  body: string;
  rule: string;
  studioTip: string;
  level: "basics" | "craft" | "imagine";
};

export type ShotSize = {
  id: string;
  code: string;
  name: string;
  frames: string;
  use: string;
  lightingNote: string;
};

export type CompRecipe = {
  id: string;
  name: string;
  mood: string;
  framing: string;
  lensFeel: string;
  subject: string;
  background: string;
  when: string;
  packetLine: string;
};

export const COMP_TOPICS: CompTopic[] = [
  {
    id: "shot-size",
    title: "Shot size",
    short: "How much of the subject is in frame.",
    body: "Extreme wide (geography), wide (body + place), medium (waist-up), medium close (chest-up), close-up (face), extreme close (eyes/detail). Size sets intimacy and information.",
    rule: "Change size for meaning — not randomly between matching coverage.",
    studioTip: "Shot list “framing” field should name size + height (e.g. medium · eye-level).",
    level: "basics",
  },
  {
    id: "thirds",
    title: "Rule of thirds & balance",
    short: "Place interest on thirds, then break it on purpose.",
    body: "Divide the frame into a 3×3 grid. Eyes often sit on the upper third. Centered frames feel formal or confrontational; off-center feels dynamic. Balance empty space (looking room) with motion direction.",
    rule: "If the subject looks right, leave space on the right — unless you want trapped tension.",
    studioTip: "Neon alley hero: subject left-third, neon depth right.",
    level: "basics",
  },
  {
    id: "eyeline",
    title: "Eyeline & camera height",
    short: "Camera height vs eye height changes power.",
    body: "Eye-level = neutral. Low angle = power / scale. High angle = vulnerability or map view. Match eyeline across reverse shots so characters appear to look at each other.",
    rule: "Keep height language consistent inside a scene unless story shifts power.",
    studioTip: "Recap “framing” should include height so extends don’t jump to bird’s-eye.",
    level: "basics",
  },
  {
    id: "lead-room",
    title: "Lead room & nose room",
    short: "Space in the direction of look or motion.",
    body: "Characters need air in the direction they face or walk. Too little room feels cramped; too much can unbalance. For chases, lead room sells velocity.",
    rule: "Match lead room when cutting matching angles of the same action.",
    studioTip: "Courier walking left→right: compose with open frame on the right.",
    level: "basics",
  },
  {
    id: "depth",
    title: "Depth layers",
    short: "Foreground, midground, background.",
    body: "Stack layers so the plate isn’t a flat cutout. Fog, rain, door frames, neon depth, corridor walls create z-axis. Shallow DOF isolates; deep focus sells space.",
    rule: "Name at least one fg or bg element in environment prompts.",
    studioTip: "Candle hall: peeling wallpaper FG + corridor depth BG.",
    level: "craft",
  },
  {
    id: "lines",
    title: "Leading lines & geometry",
    short: "Lines pull the eye to the subject.",
    body: "Corridors, roads, rails, neon strips, architectural edges. Dutch angle tilts the horizon for unease — use sparingly and match within a beat.",
    rule: "One dominant line system per shot; don’t crosswire competing diagonals.",
    studioTip: "DoP card can allow “slight dutch on wides only.”",
    level: "craft",
  },
  {
    id: "aspect",
    title: "Aspect ratio & headroom",
    short: "Frame shape changes composition math.",
    body: "2.39 widescreen loves horizontal layers; 1.85 / 16:9 is flexible; vertical is social-first. Headroom: too much empty sky weakens; cutting the skull feels amateur unless intentional.",
    rule: "Lock format in DoP card; compose for that ratio.",
    studioTip: "Academy neon preset targets anamorphic 2.39 feel.",
    level: "craft",
  },
  {
    id: "coverage",
    title: "Coverage & the 180° line",
    short: "Where the camera sits relative to action axis.",
    body: "The 180° rule keeps screen direction consistent. Crossing the line flips left/right relationships. For multi-shot still sets of one scene, pick a side of the line and stay.",
    rule: "Mark axis on the shot list for dialogue or two-subject beats.",
    studioTip: "Even single-hero alleys: keep walk direction consistent across A01–A03.",
    level: "craft",
  },
  {
    id: "prompt-frame",
    title: "Framing in Imagine prompts",
    short: "Write size, height, and subject placement.",
    body: "Include: shot size, camera height, subject placement (center / left third), and lens feel. Pair with lighting lines from the DoP card. Negatives: “awkward crop, cut-off skull, flat stagey composition.”",
    rule: "Framing line belongs in Ultimate Template after subject/environment.",
    studioTip: "Prompt lab: put size in subject or a dedicated camera feel in lens field.",
    level: "imagine",
  },
  {
    id: "match-cut",
    title: "Match frames across stills & extends",
    short: "Composition continuity is part of identity.",
    body: "When locking plates for video, composition is a continuity field: height, side, lead room. LAST_FRAME_RECAP should note framing so N+1 doesn’t re-center a left-third hero.",
    rule: "Hero plate framing becomes the extend truth.",
    studioTip: "Consistency algorithms: recap framing + DNA face lock together.",
    level: "imagine",
  },
];

export const SHOT_SIZES: ShotSize[] = [
  {
    id: "ews",
    code: "EWS",
    name: "Extreme wide",
    frames: "Tiny figure in large world",
    use: "Establish geography, isolation",
    lightingNote: "Practicals and sky often dominate exposure",
  },
  {
    id: "ws",
    code: "WS",
    name: "Wide",
    frames: "Full body + environment",
    use: "Blocking, wardrobe, place",
    lightingNote: "Show motivated sources in frame",
  },
  {
    id: "ms",
    code: "MS",
    name: "Medium",
    frames: "Waist or thighs up",
    use: "Default dialogue / action read",
    lightingNote: "Key direction must read on torso + face",
  },
  {
    id: "mcu",
    code: "MCU",
    name: "Medium close-up",
    frames: "Chest up",
    use: "Emotion + face identity",
    lightingNote: "Catchlights and fill ratio critical",
  },
  {
    id: "cu",
    code: "CU",
    name: "Close-up",
    frames: "Face fills frame",
    use: "Identity lock check, emotion peak",
    lightingNote: "Soft/hard quality very visible",
  },
  {
    id: "ecu",
    code: "ECU",
    name: "Extreme close-up",
    frames: "Eyes, hands, prop detail",
    use: "Motif, tension, prop lock",
    lightingNote: "Tiny sources; texture grain matters",
  },
];

export const COMP_RECIPES: CompRecipe[] = [
  {
    id: "hero-third",
    name: "Hero on the third",
    mood: "Confident, cinematic default",
    framing: "MCU or MS · eye-level · subject on left or right third",
    lensFeel: "35–50mm equivalent",
    subject: "Eyes on upper third · looking room",
    background: "Depth layers, not busy patterns through the face",
    when: "Character plates, posters, DNA checks",
    packetLine:
      "Medium close-up, eye-level, subject on left third, looking room right, 50mm shallow DOF",
  },
  {
    id: "center-confront",
    name: "Center confront",
    mood: "Direct, iconic, tense",
    framing: "CU or MCU · eye-level · dead center",
    lensFeel: "50mm · minimal distortion",
    subject: "Symmetry · face full toward camera",
    background: "Simple or radial (corridor, tunnel)",
    when: "Title moments, identity hero, standoffs",
    packetLine:
      "Centered close-up, eye-level, symmetrical, subject facing camera, clean background falloff",
  },
  {
    id: "wide-geo",
    name: "Wide geography",
    mood: "Scale, world-building",
    framing: "WS/EWS · slight high or eye-level",
    lensFeel: "24–35mm · deep or mid DOF",
    subject: "Small in frame · clear silhouette",
    background: "Readable architecture / weather",
    when: "Openers, teaser first beats",
    packetLine:
      "Wide shot, full body small in frame, deep neon alley, rain, environment readable",
  },
  {
    id: "dutch-unease",
    name: "Dutch unease",
    mood: "Off-balance, gothic",
    framing: "MS/WS · slight dutch · subject off-center",
    lensFeel: "24mm corridor squeeze",
    subject: "Diagonal body line",
    background: "Tilting walls / wallpaper",
    when: "Horror-adjacent SFW, candle hall wides",
    packetLine:
      "Medium-wide, slight dutch angle, subject right of center, corridor leading lines",
  },
  {
    id: "otS",
    name: "Over-the-shoulder feel",
    mood: "Relational, dialogue",
    framing: "MS · eye-level · fg shoulder soft",
    lensFeel: "35mm",
    subject: "Face of listener/speaker midground",
    background: "Room depth",
    when: "Two-character beats (still storytelling)",
    packetLine:
      "Over-shoulder composition, soft foreground shoulder, medium shot on face, eye-level",
  },
];

export const COMP_LEVELS = [
  { id: "basics" as const, label: "Basics" },
  { id: "craft" as const, label: "Craft" },
  { id: "imagine" as const, label: "Imagine" },
];
