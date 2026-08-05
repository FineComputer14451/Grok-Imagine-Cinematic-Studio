import { createFileRoute, Link } from "@tanstack/react-router";
import { BookText, RotateCcw } from "lucide-react";
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

export const Route = createFileRoute("/bible")({
  component: BiblePage,
});

type Preset = {
  id: string;
  label: string;
  title: string;
  logline: string;
  genre: string;
  rating: string;
  duration: string;
  deliverables: string;
  tone: string;
  visual: string;
  characters: string;
  constraints: string;
  success: string;
};

const PRESETS: Preset[] = [
  {
    id: "neon",
    label: "Neon courier",
    title: "Neon Courier — Micro Teaser",
    logline:
      "A courier races a sealed package across a flooded neon city before the tide of blackouts closes every bridge.",
    genre: "Neon noir · thriller",
    rating: "PG-13 / SFW cinematic",
    duration: "30s teaser + 6 stills + optional 6s hero clip",
    deliverables:
      "1 mini-Bible, 1 DNA lock, 6 still plates, 1 locked hero plate, optional 6s 720p clip, teaser beat sheet",
    tone: "Wet chrome, quiet urgency, practical neon, no camp",
    visual:
      "Anamorphic 35mm language, teal rim + amber practicals, wet reflections, shallow DOF on close plates",
    characters:
      "lead_01 Mara Chen (adult_30s) — only locked lead for v1; no deepfakes of real people",
    constraints:
      "Plate lock before any video. DNA inject on every packet. Budget-first stills. No extend until chain QA Go.",
    success:
      "Face/wardrobe continuous across 6 stills; teaser beats readable; cost within stills-first budget",
  },
  {
    id: "hall",
    label: "Candle hall",
    title: "Candle Hall — Character Study",
    logline:
      "In a peeling Victorian corridor, a woman follows a single candle toward a door that should not exist.",
    genre: "Gothic atmospheric · character study",
    rating: "PG-13 / SFW cinematic",
    duration: "2 angles + optional 6s hold",
    deliverables:
      "DNA lock, 2 stills (wide + close), LAST_FRAME_RECAP if video, continuity_state",
    tone: "Uneasy quiet, candle intimacy, blue negative fill, no jump-scare spam",
    visual:
      "24mm corridor, slight dutch on wide, eye-level close; warm candle key, deep blue fill",
    characters:
      "lead_02 Elena Voss (adult_late_20s) — candle prop locked right hand",
    constraints:
      "Transform Track required for any wardrobe change. Prop hand-side constant. Identity gate on both plates.",
    success:
      "Same face/coat across angles; candle continuity; no wardrobe freestyle",
  },
];

function buildBible(f: Preset & { projectId: string }) {
  const id = f.projectId.trim() || "project_01";
  return `# PRODUCTION BIBLE LITE — ${f.title}
project_id: ${id}
version: 0.1 · Studio Academy educational
sfw: true · fictional adults only

## 1. Charter
logline: ${f.logline}
genre: ${f.genre}
rating: ${f.rating}
target_duration: ${f.duration}

## 2. Deliverables
${f.deliverables}

## 3. Tone & visual language
tone: ${f.tone}
visual: ${f.visual}

## 4. Characters
${f.characters}
rule: CHARACTER_DNA inject required on every still/video packet

## 5. Hard constraints
${f.constraints}

## 6. Success criteria
${f.success}

## 7. Pipeline gates
1. Identity Lock / DNA approved
2. Still plates generated (draft → hero)
3. plate_status = locked before video
4. LAST_FRAME_RECAP if extending
5. Chain QA Go before stitch / delivery

## 8. VIDEO_PIPELINE_SPEC (lite)
modes: stills_first
video: only after plate lock
preferred_clip: 6s @ 720p for tests
extend: require recap + continuity_state
qa_threshold: identity-weighted Go/No-Go

[/PRODUCTION_BIBLE_LITE]`;
}

function buildActivation(bible: string, title: string) {
  return `Activate Grok Imagine Cinematic Studio v3.9.1
ACTIVATE STUDIO_DIRECTOR
ACTIVATE MEGA_PRODUCTION_ARCHITECT
ACTIVATE DOP
ACTIVATE IDENTITY_LOCK
ACTIVATE QUOTA_OPTIMIZER

Task: open production from the Mini Bible below. Confirm gates before spend.

${bible}

Output: confirmed charter summary, DoP card (3 bullets), DNA next steps, stills-first shot list (max 6).
Project: ${title}`;
}

function BiblePage() {
  const [presetId, setPresetId] = useState(PRESETS[0].id);
  const [projectId, setProjectId] = useState("project_neon_01");
  const [title, setTitle] = useState(PRESETS[0].title);
  const [logline, setLogline] = useState(PRESETS[0].logline);
  const [genre, setGenre] = useState(PRESETS[0].genre);
  const [rating, setRating] = useState(PRESETS[0].rating);
  const [duration, setDuration] = useState(PRESETS[0].duration);
  const [deliverables, setDeliverables] = useState(PRESETS[0].deliverables);
  const [tone, setTone] = useState(PRESETS[0].tone);
  const [visual, setVisual] = useState(PRESETS[0].visual);
  const [characters, setCharacters] = useState(PRESETS[0].characters);
  const [constraints, setConstraints] = useState(PRESETS[0].constraints);
  const [success, setSuccess] = useState(PRESETS[0].success);

  const form = useMemo(
    () => ({
      id: presetId,
      label: presetId,
      title,
      logline,
      genre,
      rating,
      duration,
      deliverables,
      tone,
      visual,
      characters,
      constraints,
      success,
      projectId,
    }),
    [
      presetId,
      title,
      logline,
      genre,
      rating,
      duration,
      deliverables,
      tone,
      visual,
      characters,
      constraints,
      success,
      projectId,
    ],
  );

  const bible = useMemo(() => buildBible(form), [form]);
  const activation = useMemo(
    () => buildActivation(bible, title),
    [bible, title],
  );

  function applyPreset(id: string) {
    const p = PRESETS.find((x) => x.id === id);
    if (!p) return;
    setPresetId(p.id);
    setTitle(p.title);
    setLogline(p.logline);
    setGenre(p.genre);
    setRating(p.rating);
    setDuration(p.duration);
    setDeliverables(p.deliverables);
    setTone(p.tone);
    setVisual(p.visual);
    setCharacters(p.characters);
    setConstraints(p.constraints);
    setSuccess(p.success);
    setProjectId(id === "hall" ? "project_hall_01" : "project_neon_01");
  }

  const fieldClass =
    "mt-1.5 w-full rounded-lg border border-border bg-bg px-3 py-2.5 text-sm text-fg placeholder:text-subtle outline-none focus:border-border-strong focus:ring-2 focus:ring-teal/30";

  const fields: {
    label: string;
    value: string;
    set: (v: string) => void;
    rows?: number;
  }[] = [
    { label: "Project ID", value: projectId, set: setProjectId },
    { label: "Title", value: title, set: setTitle },
    { label: "Logline", value: logline, set: setLogline, rows: 3 },
    { label: "Genre", value: genre, set: setGenre },
    { label: "Rating / mode", value: rating, set: setRating },
    { label: "Target duration", value: duration, set: setDuration },
    { label: "Deliverables", value: deliverables, set: setDeliverables, rows: 3 },
    { label: "Tone", value: tone, set: setTone, rows: 2 },
    { label: "Visual language", value: visual, set: setVisual, rows: 3 },
    { label: "Characters", value: characters, set: setCharacters, rows: 2 },
    { label: "Hard constraints", value: constraints, set: setConstraints, rows: 3 },
    { label: "Success criteria", value: success, set: setSuccess, rows: 2 },
  ];

  return (
    <div className="space-y-8">
      <div>
        <Badge variant="teal">Bible</Badge>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">
          Mini Production Bible
        </h1>
        <p className="mt-2 max-w-2xl text-muted leading-relaxed">
          Charter your project before you spend — logline, deliverables, visual
          language, gates. Copy the lite Bible into Studio Director + Architect.
        </p>
      </div>

      <div className="grid gap-3 sm:grid-cols-3">
        {[
          {
            n: "01",
            t: "Charter",
            d: "Logline, rating, deliverables",
          },
          {
            n: "02",
            t: "Language",
            d: "Tone, DoP visual, characters",
          },
          {
            n: "03",
            t: "Gates",
            d: "DNA → plates → video → QA",
          },
        ].map((s) => (
          <div
            key={s.n}
            className="rounded-xl border border-border bg-surface px-4 py-3"
          >
            <p className="font-mono text-[11px] text-teal">{s.n}</p>
            <p className="mt-1 text-sm font-medium text-fg">{s.t}</p>
            <p className="mt-0.5 text-xs text-muted">{s.d}</p>
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
              <BookText className="h-4 w-4 text-teal" />
              Bible fields
            </CardTitle>
            <CardDescription>
              Keep it short — a lite Bible beats an unread novel
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
                  <CardTitle className="text-base">Bible lite</CardTitle>
                  <CardDescription>
                    Paste into Studio / Architect
                  </CardDescription>
                </div>
                <CopyButton text={bible} label="Copy Bible" />
              </div>
            </CardHeader>
            <CardContent>
              <pre className="max-h-[360px] overflow-auto whitespace-pre-wrap rounded-lg border border-border bg-bg p-3.5 font-mono text-[11px] leading-relaxed text-muted">
                {bible}
              </pre>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-start justify-between gap-2">
                <div>
                  <CardTitle className="text-base">Activation pack</CardTitle>
                  <CardDescription>
                    Director → Architect → DoP → Identity → Quota
                  </CardDescription>
                </div>
                <CopyButton text={activation} label="Copy pack" />
              </div>
            </CardHeader>
            <CardContent>
              <pre className="max-h-48 overflow-auto whitespace-pre-wrap rounded-lg border border-border bg-bg p-3.5 font-mono text-[11px] leading-relaxed text-muted">
                {activation}
              </pre>
              <div className="mt-3 flex flex-wrap gap-2 text-xs">
                <Link to="/dna" className="text-teal hover:underline">
                  DNA builder
                </Link>
                <span className="text-subtle">·</span>
                <Link to="/lab" className="text-teal hover:underline">
                  Prompt lab
                </Link>
                <span className="text-subtle">·</span>
                <Link to="/scenarios" className="text-teal hover:underline">
                  Trailer sketch
                </Link>
                <span className="text-subtle">·</span>
                <Link to="/budget" className="text-teal hover:underline">
                  Budget
                </Link>
                <span className="text-subtle">·</span>
                <Link to="/consistency" className="text-teal hover:underline">
                  Consistency
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
