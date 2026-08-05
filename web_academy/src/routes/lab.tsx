import { createFileRoute, Link } from "@tanstack/react-router";
import { FlaskConical, Loader2, Sparkles, Wand2 } from "lucide-react";
import { useState } from "react";
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
import { enhanceCinematicPrompt } from "@/lib/prompt-lab";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/lab")({
  component: LabPage,
});

type Preset = {
  id: string;
  label: string;
  subject: string;
  environment: string;
  lighting: string;
  lens: string;
  mood: string;
};

const PRESETS: Preset[] = [
  {
    id: "noir",
    label: "Neon noir",
    subject: "A mysterious woman in a black coat",
    environment: "rain-slick neon alley at night",
    lighting: "cool teal and amber practicals, wet reflections",
    lens: "35mm anamorphic, shallow depth of field, lens flare",
    mood: "quiet dread",
  },
  {
    id: "day",
    label: "Golden hour",
    subject: "A courier on a rooftop with a messenger bag",
    environment: "dense city skyline at sunset",
    lighting: "warm golden hour side light, long shadows",
    lens: "50mm, slight haze, natural film grain",
    mood: "hopeful resolve",
  },
  {
    id: "horror",
    label: "Gothic hall",
    subject: "An adult woman holding a single candle",
    environment: "abandoned Victorian hallway, peeling wallpaper",
    lighting: "single warm candle key, deep blue fill in shadows",
    lens: "24mm wide, slight dutch angle",
    mood: "uneasy curiosity",
  },
];

function buildPrompt(fields: {
  subject: string;
  environment: string;
  lighting: string;
  lens: string;
  mood: string;
  extras: string;
}) {
  const parts = [
    fields.subject.trim() && `Subject: ${fields.subject.trim()}.`,
    fields.environment.trim() && `Environment: ${fields.environment.trim()}.`,
    fields.lighting.trim() && `Lighting: ${fields.lighting.trim()}.`,
    fields.lens.trim() && `Lens / camera: ${fields.lens.trim()}.`,
    fields.mood.trim() && `Mood: ${fields.mood.trim()}.`,
    fields.extras.trim() && fields.extras.trim(),
    "Cinematic still. No text, no watermark.",
    "Negatives: text, watermark, extra limbs, blurry face, low-res.",
  ].filter(Boolean);
  return parts.join("\n");
}

function LabPage() {
  const [subject, setSubject] = useState<string>(PRESETS[0].subject);
  const [environment, setEnvironment] = useState<string>(PRESETS[0].environment);
  const [lighting, setLighting] = useState<string>(PRESETS[0].lighting);
  const [lens, setLens] = useState<string>(PRESETS[0].lens);
  const [mood, setMood] = useState<string>(PRESETS[0].mood);
  const [extras, setExtras] = useState("");
  const [output, setOutput] = useState(() =>
    buildPrompt({
      subject: PRESETS[0].subject,
      environment: PRESETS[0].environment,
      lighting: PRESETS[0].lighting,
      lens: PRESETS[0].lens,
      mood: PRESETS[0].mood,
      extras: "",
    }),
  );
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [enhanced, setEnhanced] = useState(false);
  const [liveUsed, setLiveUsed] = useState(0);

  function applyPreset(id: string) {
    const p = PRESETS.find((x) => x.id === id);
    if (!p) return;
    setSubject(p.subject);
    setEnvironment(p.environment);
    setLighting(p.lighting);
    setLens(p.lens);
    setMood(p.mood);
    setEnhanced(false);
    setError(null);
    setOutput(
      buildPrompt({
        subject: p.subject,
        environment: p.environment,
        lighting: p.lighting,
        lens: p.lens,
        mood: p.mood,
        extras,
      }),
    );
  }

  function assemble() {
    setOutput(
      buildPrompt({ subject, environment, lighting, lens, mood, extras }),
    );
    setEnhanced(false);
    setError(null);
  }

  async function enhance() {
    if (busy) return;
    if (liveUsed >= 5) {
      setError(
        "Live enhance limit reached for this session (5). Use Assemble only.",
      );
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const notes = [
        subject && `Subject: ${subject}`,
        environment && `Environment: ${environment}`,
        lighting && `Lighting: ${lighting}`,
        lens && `Lens: ${lens}`,
        mood && `Mood: ${mood}`,
        extras && `Extras: ${extras}`,
      ]
        .filter(Boolean)
        .join("\n");

      const result = await enhanceCinematicPrompt({ data: { notes } });
      if (!result.ok) {
        setError(result.error);
        return;
      }
      setOutput(result.text);
      setEnhanced(true);
      setLiveUsed((n) => n + 1);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Enhance failed");
    } finally {
      setBusy(false);
    }
  }

  const fieldClass =
    "mt-1.5 w-full rounded-lg border border-border bg-bg px-3 py-2.5 text-sm text-fg placeholder:text-subtle outline-none focus:border-border-strong focus:ring-2 focus:ring-teal/30";

  const fields: {
    label: string;
    value: string;
    set: (v: string) => void;
    ph: string;
  }[] = [
    { label: "Subject", value: subject, set: setSubject, ph: "Who is in frame?" },
    {
      label: "Environment",
      value: environment,
      set: setEnvironment,
      ph: "Where?",
    },
    {
      label: "Lighting",
      value: lighting,
      set: setLighting,
      ph: "Key, fill, practicals",
    },
    {
      label: "Lens / camera",
      value: lens,
      set: setLens,
      ph: "Focal length, DOF, stock",
    },
    { label: "Mood", value: mood, set: setMood, ph: "Emotional temperature" },
  ];

  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <div>
        <Badge variant="teal">Practice</Badge>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">
          Prompt lab
        </h1>
        <p className="mt-2 text-muted">
          Build a Tier 1 cinematic still with the Ultimate Template order.
          Assemble offline anytime; optionally enhance with live Grok (capped).
        </p>
      </div>

      <div className="flex flex-wrap gap-1.5">
        {PRESETS.map((p) => (
          <button
            key={p.id}
            type="button"
            onClick={() => applyPreset(p.id)}
            className="h-9 rounded-md border border-border bg-surface px-3 text-xs font-medium text-muted hover:border-border-strong hover:text-fg"
          >
            {p.label}
          </button>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <FlaskConical className="h-4 w-4 text-teal" />
              Fields
            </CardTitle>
            <CardDescription>
              Subject → environment → lighting → lens → mood
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {fields.map(({ label, value, set, ph }) => (
              <label
                key={label}
                className="block text-xs font-medium text-subtle"
              >
                {label}
                <input
                  value={value}
                  onChange={(e) => set(e.target.value)}
                  placeholder={ph}
                  className={fieldClass}
                />
              </label>
            ))}
            <label className="block text-xs font-medium text-subtle">
              Extras (optional)
              <textarea
                value={extras}
                onChange={(e) => setExtras(e.target.value)}
                placeholder="Wardrobe, props, DNA inject notes…"
                rows={3}
                className={cn(fieldClass, "resize-y min-h-[72px]")}
              />
            </label>

            <div className="flex flex-wrap gap-2 pt-2">
              <Button type="button" variant="teal" onClick={assemble}>
                <Wand2 className="h-4 w-4" />
                Assemble prompt
              </Button>
              <Button
                type="button"
                variant="secondary"
                disabled={busy || liveUsed >= 5}
                onClick={enhance}
              >
                {busy ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Sparkles className="h-4 w-4" />
                )}
                Enhance with Grok
              </Button>
            </div>
            <p className="text-[11px] text-subtle">
              Live enhance: {liveUsed}/5 this session · chat only · max_tokens
              capped · no auto-calls
            </p>
            {error && (
              <p className="rounded-lg border border-danger/30 bg-danger/10 px-3 py-2 text-sm text-danger">
                {error}
              </p>
            )}
          </CardContent>
        </Card>

        <Card className={cn(enhanced && "border-teal/30")}>
          <CardHeader>
            <div className="flex items-start justify-between gap-2">
              <div>
                <CardTitle className="text-base">Output</CardTitle>
                <CardDescription>
                  {enhanced
                    ? "Enhanced by Grok — review before paste into Imagine"
                    : "Assembled template — ready to copy"}
                </CardDescription>
              </div>
              <CopyButton text={output} label="Copy" />
            </div>
          </CardHeader>
          <CardContent>
            <pre className="min-h-[280px] whitespace-pre-wrap rounded-lg border border-border bg-bg p-4 font-mono text-[12px] leading-relaxed text-muted">
              {output}
            </pre>
            <p className="mt-3 text-xs text-subtle">
              Next: paste into Grok Imagine, or study handoffs on{" "}
              <Link to="/workflows" className="text-teal hover:underline">
                Workflows
              </Link>{" "}
              and{" "}
              <Link to="/docs" className="text-teal hover:underline">
                API docs
              </Link>
              .
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
