export type FocalBand = {
  id: string;
  mm: string;
  label: string;
  angle: string;
  feel: string;
  body: string;
  face: string;
  bodySpace: string;
  distortion: string;
  use: string;
  avoid: string;
  packet: string;
  pairsWith: string;
};

export type LensTopic = {
  id: string;
  title: string;
  short: string;
  body: string;
  rule: string;
  studioTip: string;
  level: "basics" | "craft" | "imagine";
};

export type LensRecipe = {
  id: string;
  name: string;
  mood: string;
  focal: string;
  apertureFeel: string;
  format: string;
  when: string;
  packet: string;
};

export const FOCAL_BANDS: FocalBand[] = [
  {
    id: "14-20",
    mm: "14–20mm",
    label: "Ultra wide",
    angle: "Very wide FOV",
    feel: "Scale, distortion, immersive space",
    body: "Pulls environment in aggressively. Verticals bend at edges. Great for architecture and extreme geography; harsh for intimate faces unless intentional.",
    face: "Distorts noses/foreheads if close — use carefully",
    bodySpace: "Full body + huge world",
    distortion: "High edge stretch",
    use: "EWS establishes, sci-fi corridors, comic unease",
    avoid: "Beauty close-ups · DNA face checks",
    packet: "ultra-wide 18mm, deep environment, slight edge stretch OK",
    pairsWith: "2.39 establishes · dutch gothic wides",
  },
  {
    id: "24-28",
    mm: "24–28mm",
    label: "Wide",
    angle: "Wide FOV",
    feel: "Place + person together",
    body: "Standard wide cinematic workhorse. Holds full body and readable location without extreme face warp at medium distance.",
    face: "OK at medium distance; close MCU still warps",
    bodySpace: "WS / full body natural",
    distortion: "Moderate",
    use: "Candle hall corridor · alley wides · group blocking",
    avoid: "Tight CU identity plates",
    packet: "24mm wide shot, environment readable, subject full body",
    pairsWith: "1.85 / 2.39 wides · neon alley A01",
  },
  {
    id: "35",
    mm: "35mm",
    label: "Wide-standard",
    angle: "Natural-wide",
    feel: "Story default · documentary-cinema hybrid",
    body: "Often the “walk and talk” lens. Feels human without tele compression. Excellent multi-purpose for stills-first Studio work.",
    face: "Good for MS/MCU if not too close",
    bodySpace: "MS with place context",
    distortion: "Low–moderate",
    use: "Hero mediums · courier medium · general coverage",
    avoid: "Ultra-flat beauty only looks (use 50–85)",
    packet: "35mm medium shot, natural perspective, subject on third",
    pairsWith: "Academy neon mediums · DoP default set",
  },
  {
    id: "50",
    mm: "50mm",
    label: "Normal / standard",
    angle: "Approx human FOV (full frame)",
    feel: "Neutral, honest, classic",
    body: "Closest common stand-in for “normal” perspective on full-frame. Safe for identity, dialogue, and centered confront plates.",
    face: "Excellent for MCU/CU identity",
    bodySpace: "MCU natural · MS slightly tight",
    distortion: "Low",
    use: "DNA face locks · character posters · CU heroes",
    avoid: "Tiny-subject extreme wides (wrong tool)",
    packet: "50mm medium close-up, natural perspective, shallow DOF optional",
    pairsWith: "Identity plates · center confront recipe",
  },
  {
    id: "85",
    mm: "85mm",
    label: "Short tele / portrait",
    angle: "Narrower FOV",
    feel: "Flattering compression · subject isolation",
    body: "Compresses background toward subject; classic portrait cinema. Backgrounds smear into color fields with shallow DOF.",
    face: "Very flattering · strong for beauty/identity",
    bodySpace: "CU / ECU · tight MCU",
    distortion: "Very low",
    use: "Emotion peaks · beauty stills · eye ECU",
    avoid: "Cramped interiors needing environment",
    packet: "85mm close-up, background compression, soft bokeh",
    pairsWith: "Hero CU · DNA check after 50mm",
  },
  {
    id: "100-135",
    mm: "100–135mm",
    label: "Tele",
    angle: "Tight FOV",
    feel: "Surveillance, voyeur, compressed streets",
    body: "Stacks planes; crowds and streets feel denser. Isolates faces from far away. Harder to “show the room.”",
    face: "Strong isolation · paparazzi/spy language",
    bodySpace: "CU from distance",
    distortion: "Minimal · heavy compression",
    use: "Long-lens street · compressed neon bokeh",
    avoid: "Wide geography storytelling",
    packet: "135mm telephoto compression, subject isolated, creamy bokeh",
    pairsWith: "Noir surveillance beats",
  },
];

export const LENS_TOPICS: LensTopic[] = [
  {
    id: "focal",
    title: "Focal length",
    short: "How “zoomed” the perspective feels.",
    body: "Measured in millimeters (full-frame equivalent in most prompt talk). Lower mm = wider angle of view; higher mm = tighter, more compressed. It changes perspective relationship, not just crop.",
    rule: "Name a focal band in DoP + every hero packet.",
    studioTip: "Shot list “camera” field: “35mm · locked-off.”",
    level: "basics",
  },
  {
    id: "ff-vs",
    title: "Full-frame equivalent",
    short: "Speak one sensor language in prompts.",
    body: "“35mm on full frame” is the common cinema/photo shorthand. If you mix formats without saying so, collaborators (and models) assume different angles of view.",
    rule: "Write FOV as full-frame equivalent unless Bible says otherwise.",
    studioTip: "DoP format line can say “FF-equivalent lens set: 24 / 35 / 50.”",
    level: "basics",
  },
  {
    id: "perspective",
    title: "Perspective vs zoom crop",
    short: "Walking closer ≠ same as longer lens.",
    body: "Cropping a wide plate to a face is not the same as an 85mm close-up. Perspective (size relationships nose-to-ears, bg scale) only matches if you change focal length or camera distance deliberately.",
    rule: "For identity CUs, generate on 50–85 language — don’t only crop wides.",
    studioTip: "DNA lock plates prefer 50mm MCU over 24mm punch-in.",
    level: "craft",
  },
  {
    id: "dof",
    title: "Depth of field",
    short: "What stays sharp in depth.",
    body: "Shallow DOF isolates faces (fast aperture feel, longer lens, closer subject). Deep focus keeps alley and subject sharp (wide angle, more light, farther subject). DOF is a storytelling choice, not a quality slider.",
    rule: "Lock DOF intent per sequence in DoP texture/camera_move notes.",
    studioTip: "Packet: “shallow DOF, soft neon bokeh” or “deep focus, rain readable.”",
    level: "craft",
  },
  {
    id: "anamorphic",
    title: "Spherical vs anamorphic feel",
    short: "Oval bokeh, flares, widescreen DNA.",
    body: "Anamorphic language implies widescreen stretch history, horizontal flares, oval highlights. Spherical is cleaner/modern default. Pair anamorphic wording with 2.39 for coherent scope packages.",
    rule: "Don’t write “anamorphic” on 9:16 vertical unless intentional pastiche.",
    studioTip: "Neon preset: “digital anamorphic 2.39 feel.”",
    level: "craft",
  },
  {
    id: "set",
    title: "Lens sets",
    short: "A small family for one show.",
    body: "Productions pick a set (e.g. 24/35/50/85) so coverage matches. Studio Academy DoP cards should list the allowed set so Prompt Master doesn’t freestyle 14mm then 200mm randomly.",
    rule: "3–4 focal lengths max per mini-project.",
    studioTip: "Neon: 35 + 50. Candle: 24 + 35.",
    level: "craft",
  },
  {
    id: "prompt",
    title: "Lenses in Imagine prompts",
    short: "mm + DOF + format together.",
    body: "Put focal length in the camera/lens line of the Ultimate Template: “35mm anamorphic feel, shallow DOF, 2.39.” Combine with shot size from Framing and lighting from DoP.",
    rule: "mm + shot size + aspect in every hero still.",
    studioTip: "Prompt lab lens field is the right home for this line.",
    level: "imagine",
  },
  {
    id: "consistency",
    title: "Lens continuity",
    short: "Random mm reads as different shows.",
    body: "Jumping 18mm → 135mm without coverage logic breaks spatial continuity. Extends should inherit focal intent from the locked plate when possible.",
    rule: "Recap can note lens feel if it matters for N+1.",
    studioTip: "Consistency stage “shared DoP card” includes lens set.",
    level: "imagine",
  },
];

export const LENS_RECIPES: LensRecipe[] = [
  {
    id: "neon-set",
    name: "Neon courier set",
    mood: "Wet scope thriller",
    focal: "35mm coverage · 50mm identity",
    apertureFeel: "Medium-shallow on MCU; deeper on wides",
    format: "2.39 anamorphic feel",
    when: "Alley stills A01–A03",
    packet:
      "35mm medium, anamorphic 2.39 feel, teal rim, wet reflections; identity CU on 50mm shallow DOF",
  },
  {
    id: "candle-set",
    name: "Candle hall set",
    mood: "Uneasy corridor study",
    focal: "24mm wide · 35mm face",
    apertureFeel: "Deep enough to read wallpaper; soft falloff on face",
    format: "1.85 spherical",
    when: "Gothic pair B01–B02",
    packet:
      "24mm medium-wide corridor, slight dutch OK; 35mm medium close-up warm candle key",
  },
  {
    id: "portrait-hero",
    name: "Portrait hero",
    mood: "Poster / DNA stamp",
    focal: "50–85mm",
    apertureFeel: "Shallow · background melt",
    format: "1:1 or 4:5 social · or 1.85 theatrical",
    when: "Face lock verification",
    packet:
      "85mm close-up, eye-level, shallow DOF, background soft color field, natural perspective",
  },
  {
    id: "geo-wide",
    name: "Geography wide",
    mood: "World first",
    focal: "24mm (18mm if extreme)",
    apertureFeel: "Deeper focus",
    format: "2.39 or 16:9",
    when: "Teaser openers",
    packet:
      "24mm extreme-wide, subject small in frame, deep focus, environment sharp",
  },
  {
    id: "vertical-phone",
    name: "Vertical phone",
    mood: "Social full-screen",
    focal: "28–35mm equivalent",
    apertureFeel: "Moderate DOF · keep subject readable",
    format: "9:16",
    when: "Stories / reels cutdowns",
    packet:
      "35mm equivalent, 9:16 vertical, subject upper-third safe, moderate DOF",
  },
];

export const LENS_LEVELS = [
  { id: "basics" as const, label: "Basics" },
  { id: "craft" as const, label: "Craft" },
  { id: "imagine" as const, label: "Imagine" },
];
