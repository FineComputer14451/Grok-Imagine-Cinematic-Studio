export type GradeLook = {
  id: string;
  name: string;
  short: string;
  body: string;
  palette: string[];
  skin: string;
  contrast: string;
  saturation: string;
  when: string;
  avoid: string;
  packet: string;
  pairsWith: string;
};

export type ColorTopic = {
  id: string;
  title: string;
  short: string;
  body: string;
  rule: string;
  studioTip: string;
  level: "basics" | "craft" | "imagine";
};

export type ColorRecipe = {
  id: string;
  name: string;
  mood: string;
  look: string;
  lightingLink: string;
  when: string;
  packet: string;
};

export const GRADE_LOOKS: GradeLook[] = [
  {
    id: "teal-orange",
    name: "Teal & orange",
    short: "Blockbuster complementary split.",
    body: "Cool shadows/backgrounds vs warm skin and practicals. Readable faces against stylized worlds. Easy to overcook into plastic skin.",
    palette: ["#2A9D8F", "#E76F51", "#1A1A2E", "#F4A261"],
    skin: "Protect warmth; don’t cyan-wash faces",
    contrast: "Medium-high",
    saturation: "Controlled pop",
    when: "Action trailers, night city, neon-adjacent",
    avoid: "Orange skin + teal everything including eyes",
    packet:
      "teal and orange cinematic grade, warm skin protected, cool shadows, controlled saturation",
    pairsWith: "Neon noir lighting · 2.39",
  },
  {
    id: "neon-split",
    name: "Neon practical split",
    short: "Motivated gels from signs, not LUTs only.",
    body: "Color comes from practical neon — magenta tubes, teal signage, amber shop light. Grade supports sources rather than inventing a second palette.",
    palette: ["#00F5D4", "#F15BB5", "#FEE440", "#0A0A0F"],
    skin: "Lit by practical spill; keep natural undertone",
    contrast: "High local · wet speculars",
    saturation: "High on lights · restrained midtones",
    when: "Neon Courier, wet alley stills",
    avoid: "Random rainbow gels with no practicals in frame",
    packet:
      "neon-motivated grade, teal and amber practical spill, wet reflections, skin natural under gel spill",
    pairsWith: "Neon DoP card · rain plates",
  },
  {
    id: "cold-blue",
    name: "Cold blue / steel",
    short: "Detached, clinical, winter, sci-fi.",
    body: "Overall cool cast with limited warm anchors. Power and isolation. Risk: corpses and gray lips if overdone.",
    palette: ["#4CC9F0", "#4895EF", "#1B263B", "#E0E1DD"],
    skin: "Slight cool; keep lips/cheeks alive",
    contrast: "Medium · clean",
    saturation: "Low–medium",
    when: "Sci-fi, interrogation, rainy day",
    avoid: "Warm romantic dialogue in pure steel",
    packet:
      "cool steel blue grade, low saturation midtones, living skin undertone preserved",
    pairsWith: "Soft window daylight cool",
  },
  {
    id: "warm-candle",
    name: "Warm candle / tungsten",
    short: "Intimate heat vs cool falloff.",
    body: "Key is warm (candle/tungsten); shadows may go cool blue for depth. Classic gothic/interior drama.",
    palette: ["#F4A261", "#E9C46A", "#264653", "#1A1423"],
    skin: "Golden key; freckles readable",
    contrast: "High near key · soft falloff",
    saturation: "Warm pop · cool mute",
    when: "Candle Hall, period night interiors",
    avoid: "Daylight LED white washing the flame story",
    packet:
      "warm candle key grade, cool blue shadow falloff, tungsten intimacy, natural skin",
    pairsWith: "Candle gothic DoP · 1.85",
  },
  {
    id: "bleach",
    name: "Bleach / desat drama",
    short: "Lower chroma, harsh mid contrast.",
    body: "War / aftermath / moral gray. Colors drained; silver-black emphasis. Faces still need separation from bg.",
    palette: ["#8D99AE", "#2B2D42", "#EDF2F4", "#D90429"],
    skin: "Pale but not dead; slight blood tone",
    contrast: "Hard midtones",
    saturation: "Very low",
    when: "Gritty drama, aftermath beats",
    avoid: "Product beauty · candy neon",
    packet:
      "bleach bypass feel, desaturated, hard mid contrast, sparse accent color only",
    pairsWith: "Handheld fragments · tele compression",
  },
  {
    id: "pastel-soft",
    name: "Pastel soft",
    short: "Lifted blacks, gentle chroma.",
    body: "Dreamy, romantic, memory. Soft contrast; pastel accents. Can look cheap if clipped highlights go milky.",
    palette: ["#FFC8DD", "#BDE0FE", "#CDB4DB", "#FFF1E6"],
    skin: "Soft glow · careful highlight roll-off",
    contrast: "Low",
    saturation: "Soft pastels",
    when: "Memory inserts, soft drama",
    avoid: "Hard noir rain stories",
    packet:
      "soft pastel grade, lifted blacks, gentle contrast, dreamy highlight roll-off",
    pairsWith: "Window soft wrap lighting",
  },
  {
    id: "mono",
    name: "Monochrome / noir B&W",
    short: "Luminance storytelling only.",
    body: "Shape, smoke, rain, and face modeling carry the frame. Grade is about tonal separation, not hue.",
    palette: ["#000000", "#4A4A4A", "#9A9A9A", "#F0F0F0"],
    skin: "Mid-gray modeling · catchlights critical",
    contrast: "High classic noir or soft gray",
    saturation: "Zero",
    when: "Noir homage, graphic stills",
    avoid: "Expecting color practical storytelling",
    packet:
      "black and white noir grade, rich blacks, silver midtones, strong face modeling",
    pairsWith: "Hard key · rim separation",
  },
  {
    id: "natural",
    name: "Natural / clean",
    short: "Minimal stylization; true-to-eye.",
    body: "Slight contrast and white-balance polish without a “look LUT.” Best baseline for DNA checks and client-safe stills.",
    palette: ["#E8D5B7", "#7C9A92", "#2F3E46", "#CAD2C5"],
    skin: "Accurate undertone",
    contrast: "Gentle",
    saturation: "Natural",
    when: "Identity plates, product-adjacent, docs",
    avoid: "Calling it natural while blasting teal shadows",
    packet:
      "clean natural color grade, accurate skin, gentle contrast, no heavy LUT look",
    pairsWith: "50mm identity · daylight",
  },
];

export const COLOR_TOPICS: ColorTopic[] = [
  {
    id: "wb",
    title: "White balance & color temperature",
    short: "What “white” means in the scene.",
    body: "Warm (tungsten/candle) vs cool (daylight/overcast/neon cyan). Mixed temps are fine when motivated. Unmotivated green/magenta casts read as mistakes.",
    rule: "Match WB story to practicals in the DoP card.",
    studioTip: "Candle = warm key; don’t “correct” it to daylight unless story shifts.",
    level: "basics",
  },
  {
    id: "contrast",
    title: "Contrast & roll-off",
    short: "How hard black/white meet midtones.",
    body: "High contrast = drama and shape; low contrast = soft/dream. Highlight roll-off (how whites soften) separates expensive cinema from crunchy clips.",
    rule: "Lock contrast band per sequence.",
    studioTip: "Packet: “medium-high contrast, soft highlight roll-off.”",
    level: "basics",
  },
  {
    id: "skin",
    title: "Skin protection",
    short: "Faces are the grade’s truth test.",
    body: "Audiences forgive wild backgrounds before they forgive corpse skin or orange leather faces. Separate subject grade from environment grade in prompts when stylizing hard.",
    rule: "Always write a skin line when using strong LUTs/looks.",
    studioTip: "“warm skin protected, environment teal.”",
    level: "basics",
  },
  {
    id: "hue",
    title: "Hue contrast & complements",
    short: "Opposites vibrate; analogs calm.",
    body: "Teal/orange is a complement pair. Analogous (blue-cyan-teal) feels unified. Pick a strategy; don’t run all hues at max.",
    rule: "One dominant contrast pair per look.",
    studioTip: "DoP color line = your hue strategy.",
    level: "craft",
  },
  {
    id: "sat",
    title: "Saturation & chroma hierarchy",
    short: "Not everything can be loud.",
    body: "Push chroma on story colors (neon sign, blood accent, wardrobe hero) and restrain the rest. Uniform max sat is amateur.",
    rule: "Hierarchy: hero color > support > mute field.",
    studioTip: "Negatives: “oversaturated skin, neon blowout, plastic grade.”",
    level: "craft",
  },
  {
    id: "consistency",
    title: "Grade continuity",
    short: "Same world across stills and clips.",
    body: "Shot A bleach and shot B candy teal break the show. Extends inherit grade language from the locked plate and DoP card.",
    rule: "DoP color + shared negatives on every packet.",
    studioTip: "Consistency algorithms: shared DoP card stage.",
    level: "craft",
  },
  {
    id: "prompt",
    title: "Grade in Imagine prompts",
    short: "Look name + skin + contrast + what not to do.",
    body: "Pattern: [look] grade, [skin line], [contrast], [sat]. Place after lighting/lens. Avoid empty “cinematic color.”",
    rule: "Name the look; protect skin; set contrast.",
    studioTip: "Prompt lab mood field can carry grade; better as explicit color line.",
    level: "imagine",
  },
  {
    id: "refs",
    title: "References vs copy",
    short: "Mood boards, not deepfake stills of living films.",
    body: "Describe grade traits (teal shadows, warm practicals) rather than “exactly like [copyrighted film title] frame.” Educational looks stay trait-based.",
    rule: "Trait language over titled pastiche demands.",
    studioTip: "Academy presets already encode trait packs.",
    level: "imagine",
  },
];

export const COLOR_RECIPES: ColorRecipe[] = [
  {
    id: "neon",
    name: "Neon Courier grade",
    mood: "Wet night thriller",
    look: "Neon practical split + mild teal/amber",
    lightingLink: "Teal rim · amber fill",
    when: "All alley stills/clips",
    packet:
      "neon-motivated teal/amber grade, warm skin under spill, wet speculars, medium-high contrast, no plastic orange skin",
  },
  {
    id: "candle",
    name: "Candle Hall grade",
    mood: "Uneasy intimacy",
    look: "Warm tungsten key / cool blue falloff",
    lightingLink: "Candle key · blue negative fill",
    when: "Corridor pair + optional 6s",
    packet:
      "warm candle grade, cool blue corridor depth, natural freckled skin, high local contrast near flame",
  },
  {
    id: "identity",
    name: "Identity clean",
    mood: "Truthful face lock",
    look: "Natural / clean",
    lightingLink: "Whatever DoP says — grade stays honest",
    when: "DNA verification stills",
    packet:
      "clean natural grade, accurate skin undertone, gentle contrast, no heavy stylized LUT",
  },
  {
    id: "trailer-pop",
    name: "Trailer pop",
    mood: "Marketable energy",
    look: "Teal & orange restrained",
    lightingLink: "Hero rim + practical accents",
    when: "Final teaser stills only",
    packet:
      "restrained teal-orange cinematic grade, protected skin, punchy practicals, soft highlight roll-off",
  },
  {
    id: "mono-beat",
    name: "Mono insert",
    mood: "Memory / graphic beat",
    look: "Noir B&W",
    lightingLink: "Hard key + rim",
    when: "One intentional insert, labeled in Bible",
    packet:
      "black and white noir insert, rich blacks, silver face modeling, no color tint",
  },
];

export const COLOR_LEVELS = [
  { id: "basics" as const, label: "Basics" },
  { id: "craft" as const, label: "Craft" },
  { id: "imagine" as const, label: "Imagine" },
];
