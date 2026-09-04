import { createFileRoute, Link } from "@tanstack/react-router";
import { Check, Package, RotateCcw } from "lucide-react";
import { useMemo, useState } from "react";
import { CopyButton } from "@/components/copy-button";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/pack")({
  component: PackPage,
});

type PackPreset = {
  id: string;
  label: string;
  projectId: string;
  title: string;
  logline: string;
  characterId: string;
  characterName: string;
  face: string;
  wardrobe: string;
  props: string;
  format: string;
  lenses: string;
  lighting: string;
  color: string;
  shots: { code: string; title: string; framing: string; camera: string }[];
  motion: string;
  budgetNote: string;
};

const PRESETS: PackPreset[] = [
  {
    id: "neon",
    label: "Neon Courier",
    projectId: "project_neon_01",
    title: "Neon Courier — Micro Teaser",
    logline:
      "A courier races a sealed package across a flooded neon city before blackouts close every bridge.",
    characterId: "lead_01",
    characterName: "Mara Chen",
    face:
      "East Asian woman, sharp cheekbones, dark brown eyes, short asymmetrical black hair, small scar above left brow, adult_30s",
    wardrobe:
      "matte black motorcycle jacket, charcoal turtleneck, slim dark jeans, worn black boots",
    props: "messenger bag left shoulder, silver ring right hand",
    format: "digital anamorphic 2.39 feel",
    lenses: "35mm coverage · 50mm identity CU · FF-equivalent",
    lighting:
      "teal rim camera-right, amber practical left, wet ground bounce, medium-high ratio",
    color:
      "neon-motivated teal/amber grade, warm skin protected, wet speculars, medium-high contrast",
    shots: [
      {
        code: "A01",
        title: "Wide establish",
        framing: "wide · eye-level",
        camera: "35mm · locked-off",
      },
      {
        code: "A02",
        title: "Medium courier",
        framing: "medium · eye-level · left third",
        camera: "35mm · hero plate",
      },
      {
        code: "A03",
        title: "Close identity",
        framing: "close · eye-level",
        camera: "50mm shallow DOF",
      },
    ],
    motion:
      "After plate lock only: slow push-in on A02 hero, 6s, horizon level",
    budgetNote: "3 standard stills first · optional 1 quality hero · optional 6s 720p",
  },
  {
    id: "hall",
    label: "Candle Hall",
    projectId: "project_hall_01",
    title: "Candle Hall — Character Study",
    logline:
      "In a peeling Victorian corridor, a woman follows a single candle toward a door that should not exist.",
    characterId: "lead_02",
    characterName: "Elena Voss",
    face:
      "Adult woman late 20s, pale olive skin, long dark brown wavy hair, green-grey eyes, soft freckles",
    wardrobe:
      "charcoal wool coat over ivory blouse, high-waist black trousers, thin gold chain",
    props: "brass candle holder right hand",
    format: "spherical 1.85",
    lenses: "24mm corridor · 35mm face",
    lighting:
      "warm candle key sole motivated source, deep blue negative fill, high local contrast",
    color:
      "warm candle grade, cool blue corridor depth, natural freckled skin, soft highlight on flame",
    shots: [
      {
        code: "B01",
        title: "Corridor wide",
        framing: "medium-wide · slight dutch",
        camera: "24mm · static",
      },
      {
        code: "B02",
        title: "Face + flame",
        framing: "medium close · eye-level",
        camera: "35mm · hero plate",
      },
    ],
    motion:
      "After plate lock: slow creep forward down corridor, candle height constant, 6s",
    budgetNote: "2 standard stills · optional quality on B02 · optional 6s hold",
  },
];

function buildPack(p: PackPreset, include: Record<SectionId, boolean>) {
  const parts: string[] = [];

  parts.push(`# PROJECT PACK — ${p.title}
project_id: ${p.projectId}
generated: Studio Academy educational export
sfw: true · fictional adults only
`);

  if (include.bible) {
    parts.push(`## PRODUCTION BIBLE LITE
logline: ${p.logline}
format: ${p.format}
constraints: plate lock before video · DNA inject every packet · stills-first
success: identity continuous · grade continuous · cost within stills-first budget
`);
  }

  if (include.dna) {
    parts.push(`## CHARACTER_DNA
[CHARACTER_DNA ${p.characterId}]
name: ${p.characterName}
face_lock: ${p.face}
wardrobe_lock: ${p.wardrobe}
props: ${p.props}
transform_allowed: false
inject: prepend to every still and video prompt
[/CHARACTER_DNA]
`);
  }

  if (include.dop) {
    parts.push(`## DOP_VISUAL_LANGUAGE
[DOP_VISUAL_LANGUAGE vl_${p.id}]
project: ${p.title}
format: ${p.format}
lenses: ${p.lenses}
lighting: ${p.lighting}
color: ${p.color}
rule: inherit on every Prompt Master packet
[/DOP_VISUAL_LANGUAGE]
`);
  }

  if (include.shots) {
    parts.push(`## SHOT LIST
character_id: ${p.characterId}
${p.shots
  .map(
    (s, i) =>
      `### ${s.code} — ${s.title}
order: ${i + 1}
framing: ${s.framing}
camera: ${s.camera}
notes: DNA inject + DoP inherit
`,
  )
  .join("\n")}
`);
  }

  if (include.grade) {
    parts.push(`## COLOR / GRADE
${p.color}
`);
  }

  if (include.motion) {
    parts.push(`## MOTION PLAN
${p.motion}
`);
  }

  if (include.budget) {
    parts.push(`## BUDGET HINT
${p.budgetNote}
See Budget calculator for list-rate totals.
`);
  }

  if (include.activation) {
    parts.push(`## ACTIVATION PACK
Activate Grok Imagine Cinematic Studio v3.11.4
ACTIVATE STUDIO_DIRECTOR
ACTIVATE DOP
ACTIVATE IDENTITY_LOCK
ACTIVATE IMAGINE_PROMPT_MASTER
ACTIVATE QUOTA_OPTIMIZER

Task: execute project pack ${p.projectId} stills-first.
Gates: DNA → stills → plate lock → optional video → QA.
`);
  }

  parts.push(`## NEXT IN ACADEMY
1. Refine fields in Bible / DNA / DoP / Shots tools if needed
2. Build one still in Prompt lab with DNA on top
3. Estimate spend in Budget
4. Optional: Recap builder before any extend

[/PROJECT_PACK]
`);

  return parts.join("\n");
}

const SECTIONS = [
  { id: "bible", label: "Bible lite" },
  { id: "dna", label: "Character DNA" },
  { id: "dop", label: "DoP card" },
  { id: "shots", label: "Shot list" },
  { id: "grade", label: "Color grade" },
  { id: "motion", label: "Motion plan" },
  { id: "budget", label: "Budget hint" },
  { id: "activation", label: "Activation" },
] as const;

type SectionId = (typeof SECTIONS)[number]["id"];

function PackPage() {
  const [presetId, setPresetId] = useState(PRESETS[0].id);
  const [include, setInclude] = useState<Record<SectionId, boolean>>(() =>
    Object.fromEntries(SECTIONS.map((s) => [s.id, true])) as Record<
      SectionId,
      boolean
    >,
  );

  const preset = PRESETS.find((p) => p.id === presetId) ?? PRESETS[0];

  const pack = useMemo(
    () => buildPack(preset, include),
    [preset, include],
  );

  const enabledCount = SECTIONS.filter((s) => include[s.id]).length;

  function toggle(id: SectionId) {
    setInclude((prev) => ({ ...prev, [id]: !prev[id] }));
  }

  function all(on: boolean) {
    setInclude(
      Object.fromEntries(SECTIONS.map((s) => [s.id, on])) as Record<
        SectionId,
        boolean
      >,
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <Badge variant="teal">Export</Badge>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">
          Project pack
        </h1>
        <p className="mt-2 max-w-2xl text-muted leading-relaxed">
          One paste-ready bundle: Bible lite, DNA, DoP, shots, grade, motion,
          and activation — for learners who want the whole charter at once.
        </p>
      </div>

      <div className="flex flex-wrap gap-1.5">
        {PRESETS.map((p) => (
          <button
            key={p.id}
            type="button"
            onClick={() => setPresetId(p.id)}
            className={cn(
              "h-9 rounded-md border px-3 text-xs font-medium",
              presetId === p.id
                ? "border-teal/40 bg-teal/10 text-teal"
                : "border-border bg-surface text-muted hover:text-fg",
            )}
          >
            {p.label}
          </button>
        ))}
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={() => {
            setPresetId("neon");
            all(true);
          }}
        >
          <RotateCcw className="h-3.5 w-3.5" />
          Reset
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Include sections</CardTitle>
          <CardDescription>
            {enabledCount} of {SECTIONS.length} sections · toggle to slim the
            export
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="mb-3 flex gap-2">
            <Button type="button" size="sm" variant="secondary" onClick={() => all(true)}>
              All on
            </Button>
            <Button type="button" size="sm" variant="ghost" onClick={() => all(false)}>
              All off
            </Button>
          </div>
          <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
            {SECTIONS.map((s) => {
              const on = include[s.id];
              return (
                <button
                  key={s.id}
                  type="button"
                  onClick={() => toggle(s.id)}
                  className={cn(
                    "flex items-center gap-2 rounded-lg border px-3 py-2.5 text-left text-sm transition-colors",
                    on
                      ? "border-teal/40 bg-teal/5 text-fg"
                      : "border-border bg-surface text-muted",
                  )}
                >
                  <span
                    className={cn(
                      "flex h-5 w-5 items-center justify-center rounded border",
                      on
                        ? "border-teal bg-teal text-bg"
                        : "border-border bg-bg",
                    )}
                  >
                    {on && <Check className="h-3 w-3" />}
                  </span>
                  {s.label}
                </button>
              );
            })}
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-3 sm:grid-cols-3">
        <Meta label="Project" value={preset.projectId} />
        <Meta label="Lead" value={`${preset.characterName} · ${preset.characterId}`} />
        <Meta label="Shots" value={String(preset.shots.length)} />
      </div>

      <Card className="border-teal/20">
        <CardHeader>
          <div className="flex items-start justify-between gap-2">
            <div>
              <CardTitle className="flex items-center gap-2 text-base">
                <Package className="h-4 w-4 text-teal" />
                Pack export
              </CardTitle>
              <CardDescription>
                Copy into chat, notes, or Studio Director
              </CardDescription>
            </div>
            <CopyButton text={pack} label="Copy pack" />
          </div>
        </CardHeader>
        <CardContent>
          <pre className="max-h-[480px] overflow-auto whitespace-pre-wrap rounded-lg border border-border bg-bg p-3.5 font-mono text-[11px] leading-relaxed text-muted">
            {pack}
          </pre>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Open source tools</CardTitle>
          <CardDescription>
            Edit any section live, then re-export from those pages
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2 text-sm">
          {(
            [
              ["/bible", "Bible"],
              ["/dna", "DNA"],
              ["/dop", "DoP"],
              ["/shots", "Shots"],
              ["/color", "Color"],
              ["/movement", "Movement"],
              ["/budget", "Budget"],
              ["/lab", "Prompt lab"],
              ["/craft", "Craft hub"],
            ] as const
          ).map(([to, label]) => (
            <Link
              key={to}
              to={to}
              className="inline-flex h-9 items-center rounded-md border border-border bg-elevated px-3 text-xs text-muted hover:text-fg"
            >
              {label}
            </Link>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}

function Meta({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-border bg-surface px-4 py-3">
      <p className="text-[11px] uppercase tracking-wide text-subtle">{label}</p>
      <p className="mt-1 text-sm font-medium text-fg">{value}</p>
    </div>
  );
}
