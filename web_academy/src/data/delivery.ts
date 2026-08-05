export type DeliveryItem = {
  id: string;
  label: string;
  /** Optional deep-link into Academy tools */
  href?: string;
  /** Blocker items must pass before generation spend */
  blocker?: boolean;
};

export type DeliverySection = {
  id: string;
  title: string;
  blurb: string;
  items: DeliveryItem[];
};

/** Final ship gate — stills-first SFW path. Mirrors docs/academy/DELIVERY_CHECKLIST.md */
export const DELIVERY_SECTIONS: DeliverySection[] = [
  {
    id: "preflight",
    title: "Pre-flight",
    blurb: "Blockers before hero stills or video spend.",
    items: [
      {
        id: "bible",
        label: "Production Bible lite locked (logline, format, constraints)",
        href: "/bible",
        blocker: true,
      },
      {
        id: "dna",
        label: "Character DNA inject ready · transform_allowed: false if identity is frozen",
        href: "/dna",
        blocker: true,
      },
      {
        id: "dop",
        label: "DoP visual language card locked (light · lenses · color · format)",
        href: "/dop",
        blocker: true,
      },
      {
        id: "shots",
        label: "Shot list ordered · hero / support / draft priorities set",
        href: "/shots",
        blocker: true,
      },
      {
        id: "budget",
        label: "Budget counted (stills first · optional video seconds)",
        href: "/budget",
        blocker: true,
      },
    ],
  },
  {
    id: "generation",
    title: "Generation gates",
    blurb: "Rules that keep identity and look stable shot-to-shot.",
    items: [
      {
        id: "dna-every",
        label: "DNA prepended on every still/video packet",
        href: "/lab",
      },
      {
        id: "dop-inherit",
        label: "DoP lines inherited (no freestyle palette drift)",
        href: "/dop",
      },
      {
        id: "identity-cu",
        label: "Identity CUs on 50–85mm language — not cropped ultra-wides",
        href: "/lenses",
      },
      {
        id: "plate-lock",
        label: "Plate status = locked before any i2v / 6s spend",
        href: "/consistency",
      },
      {
        id: "one-move",
        label: "One primary move per short clip (or static still montage)",
        href: "/movement",
      },
    ],
  },
  {
    id: "continuity",
    title: "Continuity & QA",
    blurb: "Stop on identity No-Go. Chain QA before stitch.",
    items: [
      {
        id: "recap",
        label: "LAST_FRAME_RECAP + motion_out written before any extend",
        href: "/recap",
      },
      {
        id: "chain-qa",
        label: "Chain QA Go before stitch (identity No-Go = stop)",
        href: "/consistency",
      },
      {
        id: "wardrobe",
        label: "Wardrobe / prop / light side consistent across the shot list",
        href: "/dna",
      },
      {
        id: "grade",
        label: "Grade continuous (same look · skin protected)",
        href: "/color",
      },
    ],
  },
  {
    id: "post",
    title: "Post",
    blurb: "Cut picture first. Score second.",
    items: [
      {
        id: "edit-spine",
        label: "Edit spine set: wide → MS → CU → button",
        href: "/editing",
      },
      {
        id: "hard-cuts",
        label: "Hard cuts default · smash/dissolve only if intentional",
        href: "/editing",
      },
      {
        id: "sound-brief",
        label: "Sound brief after picture spine (or silent-first accepted)",
        href: "/sound",
      },
      {
        id: "hero-sound",
        label: "One hero sound event at a time · no clipping on button hit",
        href: "/sound",
      },
    ],
  },
  {
    id: "export",
    title: "Export",
    blurb: "Package what the session produced.",
    items: [
      {
        id: "pack",
        label: "Project pack assembled (Bible · DNA · DoP · shots · motion · activation)",
        href: "/pack",
      },
      {
        id: "aspect",
        label: "Aspect locked for delivery (2.39 / 16:9 / 9:16 as planned)",
        href: "/aspect",
      },
      {
        id: "negatives",
        label: "Negatives still present on final packets",
        href: "/lab",
      },
      {
        id: "quota",
        label: "Quota / cost note attached for the session",
        href: "/budget",
      },
    ],
  },
];

export const DELIVERY_ALL_IDS = DELIVERY_SECTIONS.flatMap((s) =>
  s.items.map((i) => i.id),
);

export const DIRECTOR_ONELINER = `DELIVERY CHECKLIST — run before stitch or client handoff
Bible ✓ DNA ✓ DoP ✓ shot list ✓ plate lock ✓ QA Go ✓ edit spine ✓ sound or silent ✓ pack export ✓
Stop on any identity No-Go. Stills-first. One move per clip.`;

export const SHIP_ORDER = [
  "Run this checklist",
  "Fix any red items",
  "Export Project pack",
  "Build hero still in Prompt lab",
  "Optional: plate-locked 6s clip",
  "Edit (spine + hard cuts)",
  "Sound brief or silent-first",
  "Done",
] as const;

export function buildDeliveryReport(checked: string[]): string {
  const lines: string[] = [
    "STUDIO ACADEMY — DELIVERY CHECKLIST",
    `Checked ${checked.length}/${DELIVERY_ALL_IDS.length}`,
    "",
  ];
  for (const section of DELIVERY_SECTIONS) {
    lines.push(`## ${section.title}`);
    for (const item of section.items) {
      const mark = checked.includes(item.id) ? "[x]" : "[ ]";
      lines.push(`${mark} ${item.label}`);
    }
    lines.push("");
  }
  lines.push("## Director one-liner");
  lines.push(DIRECTOR_ONELINER);
  lines.push("");
  lines.push("Stills-first · SFW path · stop on identity No-Go");
  return lines.join("\n");
}
