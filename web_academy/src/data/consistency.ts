export type Algorithm = {
  id: string;
  name: string;
  short: string;
  stage: "pre" | "gen" | "extend" | "qa";
  weight: string;
  inputs: string[];
  outputs: string[];
  steps: string[];
  failsWhen: string[];
  studioAgents: string[];
  relatedTools: { label: string; to: string }[];
};

export const STAGES: { id: Algorithm["stage"]; label: string; blurb: string }[] =
  [
    {
      id: "pre",
      label: "Pre-lock",
      blurb: "Freeze identity and visual language before spend.",
    },
    {
      id: "gen",
      label: "Generation",
      blurb: "Packets that force the same character into every frame.",
    },
    {
      id: "extend",
      label: "Extend",
      blurb: "Carry pose, light, and props from clip N to N+1.",
    },
    {
      id: "qa",
      label: "QA gate",
      blurb: "Score continuity; block stitch on No-Go.",
    },
  ];

export const ALGORITHMS: Algorithm[] = [
  {
    id: "dna-inject",
    name: "Character DNA inject",
    short: "Prefix every prompt with a frozen face/wardrobe contract.",
    stage: "pre",
    weight: "Critical",
    inputs: ["refs", "face_lock", "wardrobe_lock", "age_band", "transform flags"],
    outputs: ["CHARACTER_DNA block", "inject_block string"],
    steps: [
      "Extract distinctive adult features and wardrobe into structured fields.",
      "Emit [CHARACTER_DNA id] … [/CHARACTER_DNA] inject.",
      "Prepend inject to every still and video packet for that character_id.",
      "If wardrobe must change, set transform_allowed and write Transform Track.",
    ],
    failsWhen: [
      "Inject omitted on later shots",
      "face_lock too vague (“pretty woman”)",
      "transform_allowed false but wardrobe freestyles",
    ],
    studioAgents: ["Identity Lock Specialist", "Imagine Prompt Master"],
    relatedTools: [
      { label: "DNA builder", to: "/dna" },
      { label: "Glossary · DNA", to: "/glossary" },
    ],
  },
  {
    id: "plate-lock",
    name: "Plate lock gate",
    short: "Refuse video spend until a still is explicitly locked.",
    stage: "pre",
    weight: "Critical",
    inputs: ["still candidates", "strict_plate flag", "DNA match check"],
    outputs: ["plate_status: locked", "hero plate URL/ref"],
    steps: [
      "Iterate cheap 1.0 stills with DNA inject.",
      "Promote one plate to locked (grok-imagine-image-2.0 quality medium).",
      "Handoff sets plate_status=locked and motion_vector.",
      "Video packets rejected while plate is draft.",
    ],
    failsWhen: [
      "Video started from first random still",
      "Plate does not match DNA face_lock",
      "Motion vector undefined",
    ],
    studioAgents: ["Imagine Agent Mode Handoff", "QA Guardian"],
    relatedTools: [
      { label: "Prompt lab", to: "/lab" },
      { label: "Plate → 6s scenario", to: "/scenarios" },
    ],
  },
  {
    id: "shared-negatives",
    name: "Shared negative + DoP card",
    short: "Same anti-artifacts and lighting grammar across the chain.",
    stage: "gen",
    weight: "High",
    inputs: ["DoP visual language", "global negatives", "lens set"],
    outputs: ["shared_negatives", "visual_language_card"],
    steps: [
      "Lock lighting language (key/fill/practicals) and lens set once.",
      "Reuse the same negatives: text, watermark, extra limbs, low-res…",
      "Prompt Master inherits card; does not reinvent grade each shot.",
    ],
    failsWhen: [
      "Each shot invents new lighting",
      "Negatives drift or are dropped on video",
    ],
    studioAgents: ["Director of Photography", "Imagine Prompt Master"],
    relatedTools: [
      { label: "Workflows", to: "/workflows" },
      { label: "Pipeline", to: "/pipeline" },
    ],
  },
  {
    id: "packet-validation",
    name: "Imagine packet validation",
    short: "Structural + policy check before API spend.",
    stage: "gen",
    weight: "High",
    inputs: ["imagine_generation packet", "DNA required?", "mode still|video"],
    outputs: ["validated | rejected", "gate_failures[]"],
    steps: [
      "Require DNA inject when Bible demands identity lock.",
      "Validate mode, duration, negatives, refs.",
      "Estimate quota; prefer draft stills before hero video.",
      "Only then route to images/video endpoints.",
    ],
    failsWhen: [
      "MISSING_DNA_INJECT",
      "PLATE_NOT_LOCKED",
      "Invalid duration / empty prompt",
    ],
    studioAgents: ["Imagine Agent Mode Handoff", "Workflow Quota Optimizer"],
    relatedTools: [
      { label: "API docs", to: "/docs" },
      { label: "Budget", to: "/budget" },
    ],
  },
  {
    id: "last-frame-recap",
    name: "LAST_FRAME_RECAP algorithm",
    short: "Encode the final frame of clip N as structured state for N+1.",
    stage: "extend",
    weight: "Critical",
    inputs: ["clip N last frame", "pose", "light", "props", "emotion"],
    outputs: ["LAST_FRAME_RECAP block", "motion_out vector"],
    steps: [
      "Describe only the final frame — not the whole scene story.",
      "Capture pose, framing, lighting, wardrobe, props, emotion.",
      "Write motion_out so Sequence Director knows momentum.",
      "Feed recap + DNA into extend packet.",
    ],
    failsWhen: [
      "Vague recap (“she stands there”)",
      "Props forgotten (candle, bag)",
      "motion_out missing → random re-entry",
    ],
    studioAgents: ["Sequence Director", "Multi-Clip Continuity Orchestrator"],
    relatedTools: [
      { label: "Recap builder", to: "/recap" },
      { label: "Mini extend scenario", to: "/scenarios" },
    ],
  },
  {
    id: "continuity-diff",
    name: "Continuity state diff",
    short: "Compare clip N+1 plan against continuity_state; flag drift fields.",
    stage: "extend",
    weight: "Critical",
    inputs: ["continuity_state", "proposed N+1 packet", "DNA"],
    outputs: ["matched | drift", "drift_fields[]", "constraints"],
    steps: [
      "Load wardrobe, props, lighting, emotion from prior clip.",
      "Diff against N+1 prompt/plan.",
      "If drift on locked fields → block or force repair.",
      "Allow only Transform Track documented changes.",
    ],
    failsWhen: [
      "Jacket color changes without transform",
      "Prop hand-side flips",
      "Time-of-day lighting flips mid-corridor",
    ],
    studioAgents: ["Multi-Clip Continuity Orchestrator"],
    relatedTools: [
      { label: "Recap builder", to: "/recap" },
      { label: "Glossary · Continuity", to: "/glossary" },
    ],
  },
  {
    id: "extend-from-frame",
    name: "Extend-from-Frame chain",
    short: "Grow long-form from short clips using last frame + recap.",
    stage: "extend",
    weight: "High",
    inputs: ["locked plate or last frame", "recap", "DNA", "duration"],
    outputs: ["clip N+1", "updated continuity_state"],
    steps: [
      "Condition generation on last frame / plate when API supports refs.",
      "Prompt motion relative to motion_out, not a full reset.",
      "Keep DNA inject + shared negatives.",
      "Update continuity_state after Go.",
    ],
    failsWhen: [
      "Full scene re-prompt without last-frame conditioning",
      "Duration jumps without budget check",
      "Stitch before QA",
    ],
    studioAgents: [
      "Sequence Director",
      "Imagine Agent Mode Handoff",
      "QA Guardian",
    ],
    relatedTools: [
      { label: "Workflow · Extend + QA", to: "/workflows" },
      { label: "Pricing (per-second)", to: "/pricing" },
    ],
  },
  {
    id: "chain-qa-score",
    name: "Chain QA weighted score",
    short: "Multi-check Go/No-Go before stitch or delivery.",
    stage: "qa",
    weight: "Critical",
    inputs: [
      "identity",
      "motion",
      "artifact",
      "continuity",
      "audio",
      "spend",
    ],
    outputs: ["decision Go|No-Go", "score", "fix_list"],
    steps: [
      "Score each check (identity often highest weight).",
      "Compare to threshold (e.g. 0.8).",
      "No-Go → repair plan only; do not rewrite Bible.",
      "Go → allow stitch / extend / delivery pack.",
    ],
    failsWhen: [
      "Below threshold but stitched anyway",
      "Retry storms without changing packet",
      "Ignoring identity drift",
    ],
    studioAgents: ["QA Guardian", "NSFW Chain QA (artistic paths)"],
    relatedTools: [
      { label: "API · Gates", to: "/docs" },
      { label: "Quiz", to: "/quiz" },
    ],
  },
  {
    id: "identity-drift-metric",
    name: "Identity drift metric",
    short: "Numeric face/wardrobe distance vs DNA and prior frame.",
    stage: "qa",
    weight: "High",
    inputs: ["DNA version", "frame_ref", "max_drift"],
    outputs: ["drift.face", "drift.wardrobe", "Go|No-Go"],
    steps: [
      "Compare generated frame to DNA inject descriptors / refs.",
      "Compare to last approved frame when extending.",
      "If drift > max_drift → No-Go with fix_list.",
    ],
    failsWhen: [
      "Age band shifts",
      "Hair length/color freestyle",
      "Costume silhouette changes",
    ],
    studioAgents: ["QA Guardian", "Identity Lock Specialist"],
    relatedTools: [
      { label: "DNA builder", to: "/dna" },
      { label: "Glossary · Identity gate", to: "/glossary" },
    ],
  },
];

export const PIPELINE_ORDER = [
  "dna-inject",
  "plate-lock",
  "shared-negatives",
  "packet-validation",
  "last-frame-recap",
  "continuity-diff",
  "extend-from-frame",
  "identity-drift-metric",
  "chain-qa-score",
] as const;
