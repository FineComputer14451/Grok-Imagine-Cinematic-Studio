import { createFileRoute, Link } from "@tanstack/react-router";
import { Aperture, RotateCcw } from "lucide-react";
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

export const Route = createFileRoute("/dop")({
  component: DopPage,
});

type Preset = {
  id: string;
  label: string;
  project: string;
  format: string;
  lenses: string;
  keyLight: string;
  fill: string;
  practicals: string;
  color: string;
  contrast: string;
  texture: string;
  cameraMove: string;
  avoid: string;
  notes: string;
};

const PRESETS: Preset[] = [
  {
    id: "neon",
    label: "Neon noir",
    project: "Neon Courier",
    format: "digital anamorphic 2.39 feel · 35mm / 50mm set",
    lenses: "35mm establish & medium · 50mm identity close · mild flare OK",
    keyLight: "hard teal rim from camera-right · wet ground bounce secondary",
    fill: "low amber fill camera-left · faces not fully crushed",
    practicals: "neon signs, shop tubes, puddle reflections as motivated sources",
    color: "teal / amber split · desaturated mid-tones · clean skin",
    contrast: "medium-high · preserve jacket edge detail in rain",
    texture: "fine grain · wet sheen · no plastic skin",
    cameraMove: "locked-off stills preferred · optional slow push on hero only",
    avoid: "daylight grade, soft beauty lighting, random color wheels per shot",
    notes: "Shared across all stills; Prompt Master must inherit this card",
  },
  {
    id: "hall",
    label: "Candle gothic",
    project: "Candle Hall",
    format: "spherical 1.85 · 24mm / 35mm",
    lenses: "24mm corridor · 35mm face · slight dutch allowed on wide only",
    keyLight: "warm candle as sole motivated key · falloff on walls",
    fill: "deep blue negative fill in corridor depth · no fill on far walls",
    practicals: "single brass candle · flame must read · no extra lamps",
    color: "warm key / cold blue shadow · muted wallpaper dyes",
    contrast: "high local contrast on face · soft falloff into blue",
    texture: "matte wool coat · soft freckles · peeling wallpaper grain",
    cameraMove: "static holds · creep only after plate lock",
    avoid: "bright even hallway lights, modern LED white, comedy grade",
    notes: "Candle height constant with prop lock in DNA",
  },
];

function buildCard(f: Preset & { cardId: string }) {
  return `[DOP_VISUAL_LANGUAGE ${f.cardId}]
project: ${f.project}
format: ${f.format}
lenses: ${f.lenses}
key_light: ${f.keyLight}
fill: ${f.fill}
practicals: ${f.practicals}
color: ${f.color}
contrast: ${f.contrast}
texture: ${f.texture}
camera_move: ${f.cameraMove}
avoid: ${f.avoid}
notes: ${f.notes}
rule: inherit on every Prompt Master packet; do not reinvent grade per shot
[/DOP_VISUAL_LANGUAGE]`;
}

function buildActivation(card: string, project: string) {
  return `ACTIVATE DOP
Then: ACTIVATE IMAGINE_PROMPT_MASTER

Task: lock visual language for "${project}", then write stills that obey the card.

${card}

Output: 3-bullet DoP summary + confirmation that Prompt Master will inherit card on all packets.`;
}

function DopPage() {
  const [presetId, setPresetId] = useState(PRESETS[0].id);
  const [cardId, setCardId] = useState("vl_neon_01");
  const [project, setProject] = useState(PRESETS[0].project);
  const [format, setFormat] = useState(PRESETS[0].format);
  const [lenses, setLenses] = useState(PRESETS[0].lenses);
  const [keyLight, setKeyLight] = useState(PRESETS[0].keyLight);
  const [fill, setFill] = useState(PRESETS[0].fill);
  const [practicals, setPracticals] = useState(PRESETS[0].practicals);
  const [color, setColor] = useState(PRESETS[0].color);
  const [contrast, setContrast] = useState(PRESETS[0].contrast);
  const [texture, setTexture] = useState(PRESETS[0].texture);
  const [cameraMove, setCameraMove] = useState(PRESETS[0].cameraMove);
  const [avoid, setAvoid] = useState(PRESETS[0].avoid);
  const [notes, setNotes] = useState(PRESETS[0].notes);

  const form = useMemo(
    () => ({
      id: presetId,
      label: presetId,
      project,
      format,
      lenses,
      keyLight,
      fill,
      practicals,
      color,
      contrast,
      texture,
      cameraMove,
      avoid,
      notes,
      cardId,
    }),
    [
      presetId,
      project,
      format,
      lenses,
      keyLight,
      fill,
      practicals,
      color,
      contrast,
      texture,
      cameraMove,
      avoid,
      notes,
      cardId,
    ],
  );

  const card = useMemo(() => buildCard(form), [form]);
  const activation = useMemo(
    () => buildActivation(card, project),
    [card, project],
  );

  function applyPreset(id: string) {
    const p = PRESETS.find((x) => x.id === id);
    if (!p) return;
    setPresetId(p.id);
    setProject(p.project);
    setFormat(p.format);
    setLenses(p.lenses);
    setKeyLight(p.keyLight);
    setFill(p.fill);
    setPracticals(p.practicals);
    setColor(p.color);
    setContrast(p.contrast);
    setTexture(p.texture);
    setCameraMove(p.cameraMove);
    setAvoid(p.avoid);
    setNotes(p.notes);
    setCardId(id === "hall" ? "vl_hall_01" : "vl_neon_01");
  }

  const fieldClass =
    "mt-1.5 w-full rounded-lg border border-border bg-bg px-3 py-2.5 text-sm text-fg outline-none focus:border-border-strong focus:ring-2 focus:ring-teal/30";

  const fields: {
    label: string;
    value: string;
    set: (v: string) => void;
    rows?: number;
  }[] = [
    { label: "Card ID", value: cardId, set: setCardId },
    { label: "Project", value: project, set: setProject },
    { label: "Format", value: format, set: setFormat, rows: 2 },
    { label: "Lenses", value: lenses, set: setLenses, rows: 2 },
    { label: "Key light", value: keyLight, set: setKeyLight, rows: 2 },
    { label: "Fill", value: fill, set: setFill, rows: 2 },
    { label: "Practicals", value: practicals, set: setPracticals, rows: 2 },
    { label: "Color", value: color, set: setColor, rows: 2 },
    { label: "Contrast", value: contrast, set: setContrast },
    { label: "Texture", value: texture, set: setTexture },
    { label: "Camera move", value: cameraMove, set: setCameraMove, rows: 2 },
    { label: "Avoid", value: avoid, set: setAvoid, rows: 2 },
    { label: "Notes", value: notes, set: setNotes, rows: 2 },
  ];

  return (
    <div className="space-y-8">
      <div>
        <Badge variant="teal">DoP</Badge>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">
          Visual language card
        </h1>
        <p className="mt-2 max-w-2xl text-muted leading-relaxed">
          Lock lighting, lenses, color, and movement so every still and clip
          shares one photographic system — before Prompt Master writes packets.
        </p>
      </div>

      {/* Visual diagram of light triangle */}
      <div className="grid gap-3 sm:grid-cols-3">
        {[
          { t: "Key", d: "Primary motivated source", c: "border-amber/40 bg-amber/5" },
          { t: "Fill", d: "Controls shadow depth", c: "border-teal/40 bg-teal/5" },
          {
            t: "Practicals",
            d: "In-world lights in frame",
            c: "border-border bg-surface",
          },
        ].map((x) => (
          <div
            key={x.t}
            className={cn("rounded-xl border px-4 py-3", x.c)}
          >
            <p className="text-sm font-medium text-fg">{x.t}</p>
            <p className="mt-1 text-xs text-muted">{x.d}</p>
          </div>
        ))}
      </div>

      <div className="flex flex-wrap gap-1.5">
        {PRESETS.map((p) => (
          <button
            key={p.id}
            type="button"
            onClick={() => applyPreset(p.id)}
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
          onClick={() => applyPreset("neon")}
        >
          <RotateCcw className="h-3.5 w-3.5" />
          Reset
        </Button>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Aperture className="h-4 w-4 text-teal" />
              Language fields
            </CardTitle>
            <CardDescription>
              One card for the whole project — not per shot freestyle
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {fields.map(({ label, value, set, rows }) => (
              <label
                key={label}
                className="block text-xs font-medium text-subtle"
              >
                {label}
                {rows ? (
                  <textarea
                    value={value}
                    onChange={(e) => set(e.target.value)}
                    rows={rows}
                    className={cn(fieldClass, "resize-y")}
                  />
                ) : (
                  <input
                    value={value}
                    onChange={(e) => set(e.target.value)}
                    className={fieldClass}
                  />
                )}
              </label>
            ))}
          </CardContent>
        </Card>

        <div className="space-y-4 lg:sticky lg:top-20 lg:self-start">
          <Card className="border-teal/20">
            <CardHeader>
              <div className="flex items-start justify-between gap-2">
                <div>
                  <CardTitle className="text-base">DoP card export</CardTitle>
                  <CardDescription>
                    Inherit on every Prompt Master packet
                  </CardDescription>
                </div>
                <CopyButton text={card} label="Copy card" />
              </div>
            </CardHeader>
            <CardContent>
              <pre className="max-h-[320px] overflow-auto whitespace-pre-wrap rounded-lg border border-border bg-bg p-3.5 font-mono text-[11px] leading-relaxed text-muted">
                {card}
              </pre>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-start justify-between gap-2">
                <div>
                  <CardTitle className="text-base">Activation pack</CardTitle>
                  <CardDescription>DoP → Prompt Master</CardDescription>
                </div>
                <CopyButton text={activation} label="Copy pack" />
              </div>
            </CardHeader>
            <CardContent>
              <pre className="max-h-44 overflow-auto whitespace-pre-wrap rounded-lg border border-border bg-bg p-3.5 font-mono text-[11px] leading-relaxed text-muted">
                {activation}
              </pre>
              <div className="mt-3 flex flex-wrap gap-2 text-xs">
                <Link to="/bible" className="text-teal hover:underline">
                  Bible
                </Link>
                <Link to="/shots" className="text-teal hover:underline">
                  Shots
                </Link>
                <Link to="/dna" className="text-teal hover:underline">
                  DNA
                </Link>
                <Link to="/lab" className="text-teal hover:underline">
                  Prompt lab
                </Link>
                <Link to="/consistency" className="text-teal hover:underline">
                  Consistency
                </Link>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Where it fits</CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-muted space-y-1.5">
              <p>
                <span className="text-fg font-medium">After</span> Mini Bible
                charter · <span className="text-fg font-medium">before</span>{" "}
                bulk still generation.
              </p>
              <p>
                Shared negatives + this card ={" "}
                <Link to="/consistency" className="text-teal hover:underline">
                  generation-stage consistency
                </Link>
                .
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
