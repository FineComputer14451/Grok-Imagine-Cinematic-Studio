export type LightingTopic = {
  id: string;
  title: string;
  short: string;
  body: string;
  rule: string;
  studioTip: string;
  level: "basics" | "craft" | "imagine";
};

export type LightingSetup = {
  id: string;
  name: string;
  mood: string;
  key: string;
  fill: string;
  rim?: string;
  practicals?: string;
  ratio: string;
  color: string;
  useWhen: string;
  dopHint: string;
};

export const LIGHTING_TOPICS: LightingTopic[] = [
  {
    id: "key",
    title: "Key light",
    short: "The main light that shapes the face and subject.",
    body: "Key is your primary motivated source — the sun, a window, a neon sign, a candle. Its direction sets cheekbone shadow, nose shadow, and where the eye catchlight sits. Soft key wraps; hard key carves.",
    rule: "Name one key direction per sequence and keep it unless time-of-day changes on purpose.",
    studioTip: "Put key direction in the DoP card (e.g. “teal rim camera-right”).",
    level: "basics",
  },
  {
    id: "fill",
    title: "Fill light",
    short: "Controls how deep the shadows go.",
    body: "Fill lifts shadows without creating a second nose shadow. Low fill = dramatic / noir. High fill = beauty / commercial. Negative fill (black flags, dark walls) deepens shadows by removing bounce.",
    rule: "Change fill ratio before inventing a second key.",
    studioTip: "“Deep blue negative fill” is a fill choice, not a second story light.",
    level: "basics",
  },
  {
    id: "rim",
    title: "Rim / edge / backlight",
    short: "Separates subject from background.",
    body: "A rim from behind or three-quarter back draws a bright edge on hair, jacket, or shoulders so the subject doesn’t melt into the plate. In rain/neon looks, rim is often a colored practical bounce.",
    rule: "Rim solves silhouettes; don’t use it as the only light on the face unless intentional.",
    studioTip: "Neon noir presets use teal rim + amber fill — classic split.",
    level: "basics",
  },
  {
    id: "practicals",
    title: "Practicals",
    short: "Lights that exist in the world of the shot.",
    body: "Lamps, neon signs, candles, phone screens, car headlights. Practicals justify the key/fill color and sell realism. If the candle is the story, it should read as the key — not a decoration under a softbox.",
    rule: "Motivate grade from practicals you can see (or strongly imply).",
    studioTip: "DNA prop locks (candle hand-side) pair with practical height in the DoP card.",
    level: "basics",
  },
  {
    id: "ratio",
    title: "Lighting ratio",
    short: "Key vs fill intensity relationship.",
    body: "Rough guide: ~2:1 gentle, ~4:1 dramatic portrait, ~8:1+ hard noir. Ratio is more important than absolute brightness for mood continuity across shots.",
    rule: "Lock a ratio band in the visual language card for multi-shot work.",
    studioTip: "Chain QA often fails when shot A is beauty-flat and shot B is crushed noir.",
    level: "craft",
  },
  {
    id: "quality",
    title: "Hard vs soft quality",
    short: "Size of source relative to subject.",
    body: "Large relative source (softbox, overcast, bounce) = soft shadows. Small distant source (bare bulb, hard sun, distant neon) = hard shadows. Quality is independent of color.",
    rule: "Don’t switch hard↔soft mid-sequence without a story reason.",
    studioTip: "Imagine prompts: say “hard neon edge” or “soft window wrap” — not just “cinematic lighting.”",
    level: "craft",
  },
  {
    id: "color-temp",
    title: "Color temperature & contrast",
    short: "Warm/cool relationships sell time and emotion.",
    body: "Warm key / cool fill is a classic night interior. Cool rim / warm practicals is neon night exterior. Mixed temps feel intentional when each source is motivated.",
    rule: "Pick a warm/cool strategy once; don’t randomize per still.",
    studioTip: "DoP card “color” line is your temp contract for Prompt Master.",
    level: "craft",
  },
  {
    id: "direction",
    title: "Direction & face modeling",
    short: "Where light hits the face changes character read.",
    body: "Front light flattens. 45° Rembrandt leaves a triangle on the cheek. Side light is dramatic. Top light can look interrogative. Underlight feels unnatural/horror. Match direction to emotion in the Bible.",
    rule: "Keep eye-line and key side consistent when cutting multi-angle coverage.",
    studioTip: "Recap builder should note key side so extends don’t flip the face.",
    level: "craft",
  },
  {
    id: "exposure",
    title: "Exposure & silhouette",
    short: "What you protect: face, practicals, or atmosphere.",
    body: "Expose for faces in dialogue; protect practical highlights in neon (clipping neon is OK if face holds). Silhouette means intentional underexposure of the subject against a brighter bg.",
    rule: "Write what must not clip: face detail vs neon bloom.",
    studioTip: "Negatives: “crushed face, blown skin, muddy midtones” when needed.",
    level: "craft",
  },
  {
    id: "prompt",
    title: "Lighting in Imagine prompts",
    short: "Be specific; vague “cinematic lighting” drifts.",
    body: "Order works: subject → environment → lighting (key/fill/practicals) → lens → mood. Name direction, quality, color, and practicals. Then negatives for bad light (flat, overexposed, random gel mess).",
    rule: "Inherit the DoP card; don’t reinvent lighting every packet.",
    studioTip: "Prompt lab lighting field + DoP card export = generation consistency.",
    level: "imagine",
  },
  {
    id: "continuity",
    title: "Lighting continuity across clips",
    short: "Same world light when extending clip N → N+1.",
    body: "LAST_FRAME_RECAP should capture key direction, practical state (candle flame, neon on), and color. Continuity diff flags time-of-day flips and prop light changes.",
    rule: "If light story changes, document it (golden hour → night) — don’t accidental flip.",
    studioTip: "See Consistency algorithms · shared negatives + DoP card.",
    level: "imagine",
  },
];

export const LIGHTING_SETUPS: LightingSetup[] = [
  {
    id: "three-point",
    name: "Classic three-point",
    mood: "Clear, readable, controlled",
    key: "45° front-side soft or hard",
    fill: "Opposite side, lower intensity",
    rim: "Back edge separation",
    ratio: "~2:1 to 4:1",
    color: "Usually matched temps",
    useWhen: "Interviews, clean character stills, baseline coverage",
    dopHint: "Default teaching setup before stylized looks",
  },
  {
    id: "neon-noir",
    name: "Neon noir split",
    mood: "Wet night, tension, urban",
    key: "Colored rim / edge (often teal)",
    fill: "Low warm or amber bounce",
    practicals: "Neon signs, tubes, puddle reflections",
    ratio: "~4:1 to 8:1",
    color: "Teal / amber split",
    useWhen: "Courier alley, night chase stills, noir teasers",
    dopHint: "Matches Academy Neon noir DoP preset",
  },
  {
    id: "candle-motivated",
    name: "Single practical motivated",
    mood: "Intimate, uneasy, period",
    key: "Candle / lamp as only true key",
    fill: "Negative fill / cool ambient only",
    practicals: "Visible flame or lamp in frame",
    ratio: "High local contrast",
    color: "Warm key / cool shadows",
    useWhen: "Gothic hall, horror-adjacent SFW, character study",
    dopHint: "Matches Candle gothic DoP preset",
  },
  {
    id: "window-soft",
    name: "Window soft wrap",
    mood: "Natural, emotional, daylight",
    key: "Large soft window camera-side",
    fill: "Bounce from room or low LED",
    practicals: "Window itself as source",
    ratio: "~2:1",
    color: "Daylight cool or late-day warm",
    useWhen: "Dialogue interiors, soft drama",
    dopHint: "Say “large soft window key, gentle fill” in packets",
  },
  {
    id: "silhouette",
    name: "Silhouette / against practicals",
    mood: "Mystery, scale, graphic",
    key: "None on face (or tiny rim)",
    fill: "Near zero",
    practicals: "Bright bg neon, doorway, sunset",
    ratio: "Extreme",
    color: "Bg carries color story",
    useWhen: "Establishing figures, title cards, teaser beats",
    dopHint: "Mark as intentional silhouette in shot notes",
  },
];

export const LIGHTING_LEVELS = [
  { id: "basics" as const, label: "Basics" },
  { id: "craft" as const, label: "Craft" },
  { id: "imagine" as const, label: "Imagine" },
];
