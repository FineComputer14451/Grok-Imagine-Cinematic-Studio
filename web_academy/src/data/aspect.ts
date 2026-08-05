export type AspectRatio = {
  id: string;
  label: string;
  ratio: string;
  numeric: number;
  family: "cinema" | "broadcast" | "photo" | "social" | "square";
  names: string[];
  feel: string;
  body: string;
  compose: string;
  lighting: string;
  imagine: string;
  avoid: string;
  studioUse: string;
};

export type AspectTopic = {
  id: string;
  title: string;
  short: string;
  body: string;
  rule: string;
  studioTip: string;
};

export const ASPECT_RATIOS: AspectRatio[] = [
  {
    id: "239",
    label: "2.39:1",
    ratio: "2.39:1",
    numeric: 2.39,
    family: "cinema",
    names: ["Scope", "Anamorphic widescreen", "CinemaScope family"],
    feel: "Epic horizontal · landscape · modern theatrical",
    body: "Ultra-wide theatrical standard. Emphasizes environment, dual subjects, and lateral motion. Faces sit in a thin vertical band — headroom is precious.",
    compose: "Use thirds horizontally; stack depth; avoid excessive empty sky; pair well with leading lines along the horizon.",
    lighting: "Practicals and rims read as horizontal streaks; neon alleys love this frame.",
    imagine: "Say “anamorphic 2.39 widescreen, cinematic still” in format/lens lines.",
    avoid: "Tall vertical subjects without environment; heavy top/bottom letterbox waste in prompts.",
    studioUse: "Neon Courier DoP default feel · teaser plates · wide establishes",
  },
  {
    id: "235",
    label: "2.35:1",
    ratio: "2.35:1",
    numeric: 2.35,
    family: "cinema",
    names: ["Classic scope (approx)", "Older anamorphic target"],
    feel: "Slightly less wide than 2.39 · classic blockbuster",
    body: "Historically common scope; visually near 2.39. Treat interchangeably for learning; pick one and lock it in the DoP card.",
    compose: "Same as 2.39 — don’t mix 2.35 and 2.39 mid-project.",
    lighting: "Same wide practical language as 2.39.",
    imagine: "Prefer writing a single number (2.39) for consistency.",
    avoid: "Switching 2.35 ↔ 2.39 between stills in one sequence.",
    studioUse: "If Bible says “classic scope,” map to one locked ratio",
  },
  {
    id: "185",
    label: "1.85:1",
    ratio: "1.85:1",
    numeric: 1.85,
    family: "cinema",
    names: ["Flat", "Theatrical widescreen (US flat)"],
    feel: "Cinematic but less extreme · dialogue-friendly",
    body: "Standard “flat” theatrical widescreen. More vertical room for faces and standing figures than scope.",
    compose: "Balanced for MS/MCU; easier headroom than 2.39.",
    lighting: "Classic three-point and window light read cleanly.",
    imagine: "“1.85 widescreen theatrical flat” in format line.",
    avoid: "Composing as if you have scope width — edges will feel empty.",
    studioUse: "Candle Hall · character studies · dialogue stills",
  },
  {
    id: "178",
    label: "16:9",
    ratio: "16:9",
    numeric: 16 / 9,
    family: "broadcast",
    names: ["1.78:1", "HD/UHD television", "YouTube default"],
    feel: "Universal delivery · web video default",
    body: "Dominant for TV, streaming UI, and most web video. Safe all-rounder when delivery is online-first.",
    compose: "Center or thirds both work; protect lower-third graphics space if UI overlays exist.",
    lighting: "No special constraint — match DoP card.",
    imagine: "Default mental model if you omit ratio (many UIs crop toward 16:9).",
    avoid: "Assuming theatrical scope will survive uncropped on social.",
    studioUse: "Trailers for web · general Academy demos",
  },
  {
    id: "166",
    label: "1.66:1",
    ratio: "1.66:1",
    numeric: 1.66,
    family: "cinema",
    names: ["European widescreen", "Super 16 feel (approx)"],
    feel: "Slightly taller than 16:9 · indie / art-house",
    body: "Common in European theatrical history and some Super 16 presentations. A touch more height for portraiture than 1.85.",
    compose: "Good for standing figures and architecture height.",
    lighting: "Works with soft window and practical interiors.",
    imagine: "Specify explicitly — models won’t assume 1.66.",
    avoid: "Confusing with 16:9 in a multi-shot set.",
    studioUse: "Art-house Bibles · period corridors",
  },
  {
    id: "133",
    label: "4:3",
    ratio: "4:3",
    numeric: 4 / 3,
    family: "broadcast",
    names: ["1.33:1", "Academy ratio (approx family)", "Classic TV / early film"],
    feel: "Tall, archival, intimate, retro",
    body: "Near classical Academy aperture territory and old TV. Strong for faces and centered confront compositions; weak for epic lateral landscapes.",
    compose: "Embrace vertical body; careful with wide landscapes.",
    lighting: "Rembrandt / single-source portraits shine.",
    imagine: "“4:3 academy-style frame” + period grade.",
    avoid: "Scope-style dual-subject wides without cropping plan.",
    studioUse: "Found-footage adjacent SFW · flashback language",
  },
  {
    id: "141",
    label: "1.37:1 / Academy",
    ratio: "1.37:1",
    numeric: 1.37,
    family: "cinema",
    names: ["Academy ratio", "Classic Hollywood"],
    feel: "Golden-age studio · formal",
    body: "Classical Hollywood theatrical ratio. Similar teaching use to 4:3; slightly wider. Excellent for formal staging.",
    compose: "Centered or classical balanced frames.",
    lighting: "Studio three-point heritage.",
    imagine: "“Academy ratio 1.37” for period homage.",
    avoid: "Mixing with 2.39 in one sequence without a story cut.",
    studioUse: "Homage sequences · title cards",
  },
  {
    id: "32",
    label: "3:2",
    ratio: "3:2",
    numeric: 1.5,
    family: "photo",
    names: ["Full-frame still", "35mm photo"],
    feel: "Still photography native",
    body: "Native to many full-frame still cameras. Feels photographic rather than theatrical.",
    compose: "Natural for stills portfolios and print.",
    lighting: "Photo portrait language translates well.",
    imagine: "Useful when generating “photo still” not “film frame.”",
    avoid: "Calling it “cinema scope.”",
    studioUse: "Still-only campaigns · lookbooks",
  },
  {
    id: "11",
    label: "1:1",
    ratio: "1:1",
    numeric: 1,
    family: "square",
    names: ["Square", "Instagram classic"],
    feel: "Iconic · centered · graphic",
    body: "Equal sides force intentional centering or bold geometry. Great for icons and character stamps; poor for epic landscapes.",
    compose: "Center confront or strong geometric split.",
    lighting: "Symmetry in light sells the frame.",
    imagine: "“1:1 square crop, centered subject.”",
    avoid: "Wide alley establishes — they’ll feel cropped.",
    studioUse: "Avatar plates · social stamps · DNA face checks",
  },
  {
    id: "45",
    label: "4:5",
    ratio: "4:5",
    numeric: 0.8,
    family: "social",
    names: ["Portrait social", "Feed portrait"],
    feel: "Mobile feed · portrait emphasis",
    body: "Taller than square; common for social feed portraits. More face/body height than 1:1.",
    compose: "Protect headroom; vertical thirds.",
    lighting: "Beauty/key direction very visible on face.",
    imagine: "“4:5 portrait social frame.”",
    avoid: "Scope compositions forced into 4:5 without reframe.",
    studioUse: "Character posters · social stills from DNA",
  },
  {
    id: "916",
    label: "9:16",
    ratio: "9:16",
    numeric: 9 / 16,
    family: "social",
    names: ["Vertical video", "Stories / Reels / TikTok"],
    feel: "Phone-first · full-screen vertical",
    body: "Dominant short-form delivery. Subject often center-stacked; backgrounds become vertical tunnels. Theatrical wides must be redesigned, not letterboxed casually.",
    compose: "Stack FG/MG/BG vertically; center or upper-third faces; safe zones for UI.",
    lighting: "Top/bottom gradients common; practicals in vertical line.",
    imagine: "“9:16 vertical cinematic still, full body or MCU, mobile safe.”",
    avoid: "Generating 2.39 then hoping a center crop works for heroes.",
    studioUse: "Social cutdowns · vertical teasers",
  },
];

export const ASPECT_TOPICS: AspectTopic[] = [
  {
    id: "what",
    title: "What aspect ratio is",
    short: "Width ÷ height of the active picture.",
    body: "Aspect ratio is the shape of the frame, not resolution. 1920×1080 and 3840×2160 are both 16:9. Changing ratio changes composition rules, not just crop bars.",
    rule: "Lock ratio in the DoP / Bible before bulk stills.",
    studioTip: "DoP “format” line should name one ratio for the project.",
  },
  {
    id: "vs-res",
    title: "Ratio vs resolution",
    short: "Shape ≠ pixel count.",
    body: "1K/2K Imagine sizes describe detail budget; aspect describes shape. You can have a sharp 16:9 or a soft 2.39 — they solve different problems.",
    rule: "Pick ratio for story/delivery; pick resolution for quality spend.",
    studioTip: "Budget calculator cares about still/video cost; ratio is free but composition-critical.",
  },
  {
    id: "protect",
    title: "Protect & common top/bottom",
    short: "Shooting wider/taller than delivery.",
    body: "Some productions shoot with extra headroom so multiple deliveries (2.39, 16:9, 9:16) can be extracted. In pure generative work, it’s often cheaper to regenerate per delivery ratio than to fake a protect.",
    rule: "If multi-delivery matters, plan hero frames for the strictest crop.",
    studioTip: "Vertical 9:16 usually needs its own packet, not a side-crop of scope.",
  },
  {
    id: "letterbox",
    title: "Letterbox & pillarbox",
    short: "Black bars when ratios don’t match the screen.",
    body: "Letterbox = bars top/bottom (wide film on a taller screen). Pillarbox = bars left/right (tall/narrow on a wide screen). Bars are presentation — don’t invent random bars inside the generated image unless intentional UI.",
    rule: "Prefer true framed generation over baking fake bars into pixels.",
    studioTip: "Negatives: “letterbox bars, black bars in frame” if the model draws bars.",
  },
  {
    id: "continuity",
    title: "Ratio continuity",
    short: "Don’t change shape mid-sequence without a reason.",
    body: "Jumping 2.39 → 1:1 mid-teaser reads as a different show. Intentional ratio shifts can mark flashbacks or UI inserts — document them in the Bible.",
    rule: "One primary ratio per sequence; label exceptions.",
    studioTip: "Shot list / DoP inherit the same format string.",
  },
  {
    id: "imagine-write",
    title: "Writing ratio for Imagine",
    short: "Name the shape in the format/lens line.",
    body: "Include aspect in the Ultimate Template area for camera/format: “2.39 anamorphic still,” “9:16 vertical cinematic,” “1:1 centered portrait.” Pair with shot size so the model doesn’t guess.",
    rule: "Ratio + shot size + height in every hero packet.",
    studioTip: "Prompt lab lens/mood fields can carry the ratio phrase.",
  },
];

export const ASPECT_FAMILIES: {
  id: AspectRatio["family"];
  label: string;
}[] = [
  { id: "cinema", label: "Cinema" },
  { id: "broadcast", label: "Broadcast / web" },
  { id: "photo", label: "Photo" },
  { id: "social", label: "Social" },
  { id: "square", label: "Square" },
];
