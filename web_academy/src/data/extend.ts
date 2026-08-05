export type ExtendRule = {
  id: string;
  title: string;
  short: string;
  body: string;
  severity: "blocker" | "craft" | "tip";
};

export type ExtendClip = {
  id: string;
  code: string;
  title: string;
  /** Seconds — keep short clips for Studio */
  duration: 4 | 6 | 8 | 10;
  framing: string;
  action: string;
  /** Primary camera move (one per clip) */
  move: string;
  motionIn: string;
  motionOut: string;
  emotion: string;
  plateStatus: "draft" | "locked" | "n/a";
  notes: string;
};

export type ExtendChainPreset = {
  id: string;
  label: string;
  project: string;
  characterId: string;
  genre: string;
  blurb: string;
  totalBudgetHint: string;
  clips: Omit<ExtendClip, "id">[];
};

export const EXTEND_RULES: ExtendRule[] = [
  {
    id: "plate-first",
    title: "Plate lock before clip 01 video",
    short: "No hero i2v until plate_status = locked.",
    body: "Generate stills with DNA inject until one plate is approved. Only then spend video seconds on clip_01. Draft plates burn quota and break identity later.",
    severity: "blocker",
  },
  {
    id: "one-move",
    title: "One primary move per clip",
    short: "Push OR track OR pan — not three at once.",
    body: "Short clips cannot carry complex blocking. Pick a single motion_vector. Static stills with hard cuts remain valid if motion fails QA.",
    severity: "blocker",
  },
  {
    id: "recap-handoff",
    title: "Recap every boundary",
    short: "Write LAST_FRAME_RECAP + motion_out before planning N+1.",
    body: "Sequence Director and Multi-Clip Continuity read the recap, not your memory. Missing motion_out is the #1 extend drift cause.",
    severity: "blocker",
  },
  {
    id: "dna-every",
    title: "DNA on every packet",
    short: "Prepend CHARACTER_DNA inject on each clip prompt.",
    body: "Extend does not magically remember face locks. Treat each clip as a new handoff that still carries DNA + DoP lines.",
    severity: "blocker",
  },
  {
    id: "chain-qa",
    title: "Chain QA before stitch",
    short: "Identity No-Go stops the chain — repair only.",
    body: "Do not rewrite the Bible or freestyle wardrobe to “fix” a No-Go. Repair the failed clip or re-lock the plate.",
    severity: "blocker",
  },
  {
    id: "short-chain",
    title: "Keep chains short early",
    short: "2–4 clips for first teasers.",
    body: "Long chains multiply drift risk. Ship a 2-clip proof before a 6-clip odyssey. Prefer still montage if motion is not ready.",
    severity: "craft",
  },
  {
    id: "inherit-look",
    title: "Inherit DoP — no palette freestyle",
    short: "Same key side, grade, and lens set across the chain.",
    body: "Clip N+1 may change framing size but not the visual language card. Grade and practical colors stay continuous.",
    severity: "craft",
  },
  {
    id: "motion-match",
    title: "Match motion_out → motion_in",
    short: "Outgoing vector must seed the next clip.",
    body: "If clip_01 ends on a slow push continuing, clip_02 motion_in continues that push (or explicitly holds). Contradictory vectors read as teleport cuts.",
    severity: "craft",
  },
  {
    id: "budget-note",
    title: "Count seconds before generate",
    short: "Sum durations · prefer 6s hero clips.",
    body: "Video is priced per second. Draft with stills and one hero 6s; only then fill support clips. Attach a quota note to the chain packet.",
    severity: "tip",
  },
  {
    id: "silent-ok",
    title: "Picture first — sound later",
    short: "Silent chain is valid for early QA.",
    body: "Lock motion and identity before writing music/SFX briefs. Sound will not fix identity drift or weak coverage.",
    severity: "tip",
  },
];

export const EXTEND_PRESETS: ExtendChainPreset[] = [
  {
    id: "neon-3",
    label: "Neon alley 3-clip",
    project: "Neon Courier teaser",
    characterId: "lead_01",
    genre: "Noir / thriller",
    blurb: "Wide establish → medium push → identity CU hold. Stills-first path.",
    totalBudgetHint: "3 stills + optional 3×6s video",
    clips: [
      {
        code: "clip_01",
        title: "Alley establish",
        duration: 6,
        framing: "wide · eye-level · subject left of center",
        action: "Courier at alley mouth; rain; neon readable; slow hold then tiny push",
        move: "static → micro push-in",
        motionIn: "from locked wide plate",
        motionOut: "slow push continuing toward subject; rain down-left",
        emotion: "watchful, quiet dread",
        plateStatus: "locked",
        notes: "DNA inject · DoP teal/amber · plate locked before i2v",
      },
      {
        code: "clip_02",
        title: "Medium courier",
        duration: 6,
        framing: "medium · eye-level",
        action: "Bag left; messenger bag; wet jacket sheen; walks deeper two steps",
        move: "slow track forward",
        motionIn: "continues push from clip_01; bag strap left shoulder",
        motionOut: "track settles to MS; eyes toward lens axis",
        emotion: "jaw set, focused",
        plateStatus: "locked",
        notes: "Inherit wardrobe + bag · one move only",
      },
      {
        code: "clip_03",
        title: "Identity button",
        duration: 6,
        framing: "close · 50–85mm language · eye-level",
        action: "Face hold; rain flecks; practical amber rim; hard cut ready",
        move: "static hold",
        motionIn: "from MS settle; face fills frame",
        motionOut: "hold for button / title safe",
        emotion: "quiet dread, eyes locked",
        plateStatus: "locked",
        notes: "Identity CU not cropped ultra-wide · chain QA before stitch",
      },
    ],
  },
  {
    id: "candle-2",
    label: "Candle hall pair",
    project: "Candle Hall study",
    characterId: "lead_02",
    genre: "Gothic / slow horror",
    blurb: "Corridor creep → face + flame hold. Two-clip proof of extend.",
    totalBudgetHint: "2 stills + optional 2×6s",
    clips: [
      {
        code: "clip_01",
        title: "Corridor creep",
        duration: 8,
        framing: "medium-wide · slight dutch",
        action: "Candle right hand; walk corridor axis; peeling wallpaper both sides",
        move: "slow creep / dolly in",
        motionIn: "from locked corridor plate",
        motionOut: "creep continues; candle height steady at chest",
        emotion: "uneasy curiosity",
        plateStatus: "locked",
        notes: "Prop hand-side locked · warm key / blue fill",
      },
      {
        code: "clip_02",
        title: "Face + flame",
        duration: 6,
        framing: "medium close · eye-level",
        action: "Warm candle key on face; blue fill in depth; breath held",
        move: "static hold",
        motionIn: "from creep settle; flame in frame lower-right",
        motionOut: "hold; optional smash to black",
        emotion: "breath held, eyes wider",
        plateStatus: "locked",
        notes: "Do not freestyle wardrobe · recap before any third clip",
      },
    ],
  },
  {
    id: "still-hybrid",
    label: "Still montage + one hero 6s",
    project: "Hybrid teaser",
    characterId: "lead_01",
    genre: "Marketing / trailer",
    blurb: "Three locked stills as hard cuts, one optional hero motion clip.",
    totalBudgetHint: "3 stills + 1×6s hero",
    clips: [
      {
        code: "still_01",
        title: "Wide plate",
        duration: 4,
        framing: "wide · 2.39",
        action: "Establish geography — hard cut only (no motion required)",
        move: "static still",
        motionIn: "n/a — still montage",
        motionOut: "hard cut to still_02",
        emotion: "tone set",
        plateStatus: "locked",
        notes: "Export as still; no video spend",
      },
      {
        code: "still_02",
        title: "Medium plate",
        duration: 4,
        framing: "medium",
        action: "Character readable; wardrobe lock check",
        move: "static still",
        motionIn: "hard cut",
        motionOut: "hard cut to hero",
        emotion: "tension rise",
        plateStatus: "locked",
        notes: "Still montage valid early delivery",
      },
      {
        code: "clip_hero",
        title: "Hero 6s motion",
        duration: 6,
        framing: "medium close · 50mm",
        action: "Slow push on locked identity plate",
        move: "slow push-in",
        motionIn: "from locked hero plate",
        motionOut: "push settles; button safe",
        emotion: "peak dread",
        plateStatus: "locked",
        notes: "Only video spend in this chain · chain QA then stitch",
      },
    ],
  },
];

export function uid() {
  return Math.random().toString(36).slice(2, 9);
}

export function emptyClip(index: number): ExtendClip {
  const n = String(index + 1).padStart(2, "0");
  return {
    id: uid(),
    code: `clip_${n}`,
    title: "New clip",
    duration: 6,
    framing: "medium · eye-level",
    action: "",
    move: "static hold",
    motionIn: "from previous recap",
    motionOut: "hold / continue one vector",
    emotion: "",
    plateStatus: "draft",
    notes: "DNA inject · one move",
  };
}

export function clipsFromPreset(preset: ExtendChainPreset): ExtendClip[] {
  return preset.clips.map((c) => ({ ...c, id: uid() }));
}

export function totalSeconds(clips: ExtendClip[]): number {
  return clips.reduce((sum, c) => sum + c.duration, 0);
}

export function blockersOk(clips: ExtendClip[]): {
  ok: boolean;
  issues: string[];
} {
  const issues: string[] = [];
  if (clips.length === 0) issues.push("Add at least one clip");
  const firstVideo = clips.find(
    (c) => !c.code.startsWith("still") && c.move !== "static still",
  );
  if (firstVideo && firstVideo.plateStatus === "draft") {
    issues.push(`${firstVideo.code}: plate still draft — lock before video spend`);
  }
  for (const c of clips) {
    if (!c.motionOut.trim()) {
      issues.push(`${c.code}: missing motion_out (recap handoff)`);
    }
    if (!c.move.trim()) {
      issues.push(`${c.code}: missing primary move`);
    }
  }
  // motion match soft check between consecutive
  for (let i = 1; i < clips.length; i++) {
    const prev = clips[i - 1];
    const cur = clips[i];
    if (
      prev.motionOut &&
      cur.motionIn &&
      prev.motionOut.length > 8 &&
      cur.motionIn === "from previous recap"
    ) {
      // soft tip only — not hard fail
    }
  }
  return { ok: issues.length === 0, issues };
}

export function buildChainPacket(input: {
  project: string;
  characterId: string;
  clips: ExtendClip[];
}): string {
  const { project, characterId, clips } = input;
  const secs = totalSeconds(clips);
  const lines = clips.map((c, i) => {
    return `--- ${c.code} (${c.duration}s) · ${c.title}
framing: ${c.framing}
action: ${c.action || "—"}
move: ${c.move}
motion_in: ${c.motionIn || "—"}
motion_out: ${c.motionOut || "—"}
emotion: ${c.emotion || "—"}
plate_status: ${c.plateStatus}
notes: ${c.notes || "—"}
handoff: write LAST_FRAME_RECAP for ${c.code} before planning clip ${i + 2 > clips.length ? "STITCH" : clips[i + 1]?.code ?? "N+1"}`;
  });

  return `EXTEND CHAIN PLAN — Studio Academy
Project: ${project || "Untitled"}
Character: ${characterId || "lead_01"}
Clips: ${clips.length} · Total motion budget: ~${secs}s (count API seconds separately for stills)

RULES
1. DNA inject on every packet
2. plate_status=locked before any i2v / hero 6s
3. One primary move per clip
4. LAST_FRAME_RECAP + motion_out at every boundary
5. Chain QA Go before stitch · identity No-Go = repair only
6. Inherit DoP — no freestyle palette

CLIPS
${lines.join("\n\n")}

ACTIVATION
ACTIVATE SEQUENCE_DIRECTOR
ACTIVATE MULTI_CLIP_CONTINUITY
ACTIVATE IMAGINE_HANDOFF
ACTIVATE QA_GUARDIAN
ACTIVATE IDENTITY_LOCK

Mode: Extend-from-Frame chain
Start: locked plate for first motion clip
On No-Go: repair clip only — do not rewrite Production Bible.

NEXT
1. Build recaps in /recap per boundary
2. Packets in /lab with DNA prepend
3. Run /delivery before client handoff
`;
}

export function buildDirectorBrief(input: {
  project: string;
  characterId: string;
  clips: ExtendClip[];
}): string {
  const spine = input.clips
    .map((c) => `${c.code}: ${c.title} (${c.duration}s, ${c.move})`)
    .join(" → ");
  return `DIRECTOR ONE-LINER — ${input.project || "Project"}
Character ${input.characterId || "lead"} · chain ${input.clips.length} clips · ~${totalSeconds(input.clips)}s
Spine: ${spine || "(empty)"}
Gate: plates locked · DNA every packet · chain QA before stitch.`;
}
