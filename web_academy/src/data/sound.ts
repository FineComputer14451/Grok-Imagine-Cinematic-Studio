export type SoundLayer = {
  id: string;
  name: string;
  short: string;
  body: string;
  examples: string[];
  when: string;
  avoid: string;
  brief: string;
};

export type SoundTopic = {
  id: string;
  title: string;
  short: string;
  body: string;
  rule: string;
  studioTip: string;
  level: "basics" | "craft" | "imagine";
};

export type SoundRecipe = {
  id: string;
  name: string;
  mood: string;
  bed: string;
  hits: string;
  silence: string;
  when: string;
  brief: string;
};

export const SOUND_LAYERS: SoundLayer[] = [
  {
    id: "music",
    name: "Music bed",
    short: "Emotional spine of the teaser.",
    body: "Sets tempo and tone. For 15–24s pieces, one bed with a clear rise into the button is enough. Loud music fights dialogue and SFX.",
    examples: ["low pulse drone", "sparse piano", "dark synth arpeggio", "perc tick"],
    when: "Almost every teaser",
    avoid: "Wall-to-wall busy tracks with no pockets",
    brief: "music: low pulse, minor, rise into final button, leave 0.5s air",
  },
  {
    id: "atmos",
    name: "Atmosphere / room tone",
    short: "World air that sells place.",
    body: "Rain, traffic bed, corridor hum, wind. Continuity of atmos across hard cuts keeps geography alive even in still montages.",
    examples: ["rain loop", "neon hum", "distant traffic", "HVAC hiss"],
    when: "Any location-driven piece",
    avoid: "Atmos louder than story hits",
    brief: "atmos: steady rain + distant city, -18dB under music",
  },
  {
    id: "foley",
    name: "Foley / footsteps",
    short: "Body and object contact sounds.",
    body: "Boots on wet asphalt, coat rustle, bag strap. Sync loosely to picture energy even on stills (implied motion).",
    examples: ["boot splash", "zipper", "leather creak", "candle set-down"],
    when: "Character-forward beats",
    avoid: "Foley every frame — pick hero contacts",
    brief: "foley: 2–3 boot steps on wet street under MS walk stills",
  },
  {
    id: "sfx",
    name: "Designed SFX / hits",
    short: "Punctuation for cuts and buttons.",
    body: "Whooshes cover hard cuts; impacts land on title or final still. One strong hit beats five weak ones.",
    examples: ["whoosh", "sub drop", "glass tick", "power-down"],
    when: "Cut accents and buttons",
    avoid: "Hit on every cut",
    brief: "sfx: soft whoosh on cut 2; sub hit on button still",
  },
  {
    id: "vo",
    name: "Voice / VO",
    short: "Optional narration or diegetic line.",
    body: "Most Academy micro-teasers stay silent + music. If VO: short, clear, leave picture breathing room.",
    examples: ["one-line logline VO", "radio dispatch", "whisper motif"],
    when: "Marketing clarity needed",
    avoid: "Wall-to-wall VO over every image",
    brief: "vo: none (music + atmos only) OR one 4-word line at 0:08",
  },
  {
    id: "silence",
    name: "Silence / air",
    short: "Negative space is a layer.",
    body: "Drops before a smash or button make the hit larger. Stills montages benefit from a held breath before the end card.",
    examples: ["0.4s pre-button mute", "music duck under CU"],
    when: "Before button or reveal",
    avoid: "Dead air with no intention",
    brief: "silence: 0.5s music dip before final still",
  },
];

export const SOUND_TOPICS: SoundTopic[] = [
  {
    id: "picture-lock",
    title: "Picture before polish sound",
    short: "Don’t score a moving target.",
    body: "Lock shot order and durations first (Editing module). Temp ticks are fine during assemble; final bed after picture is stable.",
    rule: "Picture-ish lock before final music pass.",
    studioTip: "Use Editing pace recipes as the sound grid.",
    level: "basics",
  },
  {
    id: "hierarchy",
    title: "Mix hierarchy",
    short: "What must be heard first.",
    body: "Typical teaser stack: story hit/VO > designed hit > foley > music > atmos. Duck lower layers when a higher one speaks.",
    rule: "One hero sound event at a time.",
    studioTip: "If rain + music + whoosh + VO fight, kill two.",
    level: "basics",
  },
  {
    id: "sync",
    title: "Sync & implied motion",
    short: "Stills still need rhythm.",
    body: "On still montages, cut and sound define motion. Place foley and hits on cut points. For 6s clips, land music accents on move peaks (end of push).",
    rule: "Cut point = candidate hit point.",
    studioTip: "24s hybrid: hit at clip boundaries.",
    level: "craft",
  },
  {
    id: "diegetic",
    title: "Diegetic vs score",
    short: "In-world vs outside narrator music.",
    body: "Neon hum can be diegetic; trailer synth is usually score. Blending both is fine if levels tell the truth (hum sits in world, score sits under).",
    rule: "Label layers diegetic | score in the brief.",
    studioTip: "Candle flame crackle = diegetic intimacy cue.",
    level: "craft",
  },
  {
    id: "loudness",
    title: "Loudness & platforms",
    short: "Don’t clip; leave headroom.",
    body: "Web teasers often aim for competitive but clean levels. Protect peaks on hits. Better slightly quieter than distorted.",
    rule: "No clipping on button hit.",
    studioTip: "Normalize bed first; add hits after.",
    level: "craft",
  },
  {
    id: "rights",
    title: "Rights & originality",
    short: "Don’t paste copyrighted tracks as if free.",
    body: "Educational briefs should request original/temp beds or clearly licensed stock. Describe mood traits (tempo, instruments) instead of “exactly like [famous track].”",
    rule: "Trait-based music briefs, not titled clones.",
    studioTip: "Same philosophy as color “looks not film titles.”",
    level: "imagine",
  },
  {
    id: "agent",
    title: "Sound in the Studio stack",
    short: "Where agents help.",
    body: "After picture intent is clear, a music/SFX brief can go to production agents. Keep briefs short: duration, mood, layer list, hit map, do-nots.",
    rule: "Sound brief after shot list + edit spine.",
    studioTip: "Attach pack project_id so tone matches Bible.",
    level: "imagine",
  },
  {
    id: "silent",
    title: "Silent-first delivery",
    short: "Valid and often smarter early.",
    body: "Shipping a still montage with no audio is acceptable for learning and client stills. Add sound only when the picture spine works mute.",
    rule: "If it fails silent, sound won’t save it.",
    studioTip: "Quota-friendly: picture only until plates lock.",
    level: "imagine",
  },
];

export const SOUND_RECIPES: SoundRecipe[] = [
  {
    id: "neon-24",
    name: "Neon 24s hybrid",
    mood: "Wet night pressure",
    bed: "Dark pulse + high neon tick",
    hits: "Whoosh at 3s and 12s; sub at 18s button",
    silence: "0.4s dip before button",
    when: "After Neon pack + 24s edit recipe",
    brief: `SOUND BRIEF — Neon Courier 24s
duration: 24s
music: dark minor pulse, restrained, rise from 0:15
atmos: rain + city bed, continuous
foley: wet boots under walking stills (2–3 steps)
sfx: soft whoosh @0:03, @0:12; sub hit @0:18 button
vo: none
silence: 0.4s pre-button duck
do_not: busy full orchestra, copyrighted melodies, constant hits`,
  },
  {
    id: "candle-slow",
    name: "Candle slow study",
    mood: "Unease · intimate",
    bed: "Sparse drone, almost static",
    hits: "Single low knock at button optional",
    silence: "Longer air; no whoosh spam",
    when: "Candle Hall slow holds",
    brief: `SOUND BRIEF — Candle Hall
duration: ~18–24s
music: sparse low drone, no percussion
atmos: quiet corridor air, faint wood creak
foley: soft fabric; one candle set if visible
sfx: optional single distant knock at end
vo: none
do_not: jump-scare stingers, rain, neon city`,
  },
  {
    id: "still-15",
    name: "15s still montage",
    mood: "Portfolio clean",
    bed: "Optional soft bed or mute",
    hits: "One riser into last still",
    silence: "Mute OK entire piece",
    when: "Tier 1 DNA proof",
    brief: `SOUND BRIEF — 15s stills
duration: 15s
music: optional soft bed OR silence
atmos: optional light room tone
sfx: single riser into final still (optional)
vo: none
note: silent delivery acceptable`,
  },
  {
    id: "vo-logline",
    name: "VO logline sting",
    mood: "Marketing clear",
    bed: "Low bed ducked under VO",
    hits: "Hit after VO ends on button",
    silence: "Clear VO pocket mid-piece",
    when: "Need message in <25s",
    brief: `SOUND BRIEF — VO sting
duration: 20–24s
vo: one short logline line (~8–12 words) mid-timeline
music: low bed, duck -6dB under VO
sfx: button hit after VO
do_not: VO over every shot`,
  },
];

export const SOUND_LEVELS = [
  { id: "basics" as const, label: "Basics" },
  { id: "craft" as const, label: "Craft" },
  { id: "imagine" as const, label: "Imagine" },
];
