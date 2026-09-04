import { createFileRoute, Link } from "@tanstack/react-router";
import { Calculator, RotateCcw } from "lucide-react";
import { useMemo, useState } from "react";
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

export const Route = createFileRoute("/budget")({
  component: BudgetPage,
});

/** Published list rates — same source as Pricing page · Sep 2026 */
const RATES = {
  chatInPerM: 2,
  chatOutPerM: 6,
  still: {
    standard: 0.02,
    low1k: 0.04,
    low2k: 0.06,
    med1k: 0.06,
    med2k: 0.08,
  },
  video: {
    v10_480: 0.05,
    v10_720: 0.07,
    v15_480: 0.08,
    v15_720: 0.14,
    v15_1080: 0.25,
  },
} as const;

type StillTier = keyof typeof RATES.still;
type VideoKey = keyof typeof RATES.video;

const STILL_LABELS: { id: StillTier; label: string }[] = [
  { id: "standard", label: "1.0 · $0.02" },
  { id: "low1k", label: "2.0 low 1K · $0.04" },
  { id: "low2k", label: "2.0 low 2K · $0.06" },
  { id: "med1k", label: "2.0 med 1K · $0.06" },
  { id: "med2k", label: "2.0 med 2K · $0.08" },
];

const VIDEO_LABELS: Record<VideoKey, string> = {
  v10_480: "1.0 480p",
  v10_720: "1.0 720p",
  v15_480: "1.5 480p",
  v15_720: "1.5 720p",
  v15_1080: "1.5 1080p",
};

const VIDEO_BUTTONS: { id: VideoKey; label: string }[] = [
  { id: "v10_480", label: "1.0 480p $0.05/s" },
  { id: "v10_720", label: "1.0 720p $0.07/s" },
  { id: "v15_480", label: "1.5 480p $0.08/s" },
  { id: "v15_720", label: "1.5 720p $0.14/s" },
  { id: "v15_1080", label: "1.5 1080p $0.25/s" },
];

function money(n: number) {
  if (n < 0.01 && n > 0) return `≈$${n.toFixed(4)}`;
  return `$${n.toFixed(2)}`;
}

function BudgetPage() {
  const [stillCount, setStillCount] = useState(8);
  const [stillTier, setStillTier] = useState<StillTier>("standard");
  const [videoSeconds, setVideoSeconds] = useState(12);
  const [videoKey, setVideoKey] = useState<VideoKey>("v10_720");
  const [chatInK, setChatInK] = useState(20);
  const [chatOutK, setChatOutK] = useState(8);
  const [bufferPct, setBufferPct] = useState(15);

  const breakdown = useMemo(() => {
    const stillUnit = RATES.still[stillTier];
    const stills = stillCount * stillUnit;

    const videoUnit = RATES.video[videoKey];
    const video = videoSeconds * videoUnit;

    const chatIn = (chatInK / 1000) * RATES.chatInPerM;
    const chatOut = (chatOutK / 1000) * RATES.chatOutPerM;
    const chat = chatIn + chatOut;

    const subtotal = stills + video + chat;
    const buffer = subtotal * (bufferPct / 100);
    const total = subtotal + buffer;

    return {
      stillUnit,
      stills,
      videoUnit,
      video,
      chat,
      chatIn,
      chatOut,
      subtotal,
      buffer,
      total,
      lines: [
        {
          id: "stills",
          label: `${stillCount} stills × ${money(stillUnit)}`,
          amount: stills,
          share: subtotal > 0 ? stills / subtotal : 0,
        },
        {
          id: "video",
          label: `${videoSeconds}s ${VIDEO_LABELS[videoKey]} × ${money(videoUnit)}/s`,
          amount: video,
          share: subtotal > 0 ? video / subtotal : 0,
        },
        {
          id: "chat",
          label: `Chat ${chatInK}k in + ${chatOutK}k out`,
          amount: chat,
          share: subtotal > 0 ? chat / subtotal : 0,
        },
      ],
    };
  }, [
    stillCount,
    stillTier,
    videoSeconds,
    videoKey,
    chatInK,
    chatOutK,
    bufferPct,
  ]);

  function reset() {
    setStillCount(8);
    setStillTier("standard");
    setVideoSeconds(12);
    setVideoKey("v10_720");
    setChatInK(20);
    setChatOutK(8);
    setBufferPct(15);
  }

  return (
    <div className="space-y-8">
      <div>
        <Badge variant="teal">Planner</Badge>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">
          Budget calculator
        </h1>
        <p className="mt-2 max-w-2xl text-muted leading-relaxed">
          Estimate API spend for a Studio session from published list rates.
          Adjust stills, video seconds, and chat tokens — not a quote, a planning
          tool.
        </p>
        <p className="mt-2 text-xs text-subtle">
          List prices as of Sep 2026 · same source as{" "}
          <Link to="/pricing" className="text-teal hover:underline">
            Pricing
          </Link>
          . SuperGrok app quotas are separate.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1.05fr)_minmax(0,0.95fr)]">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Calculator className="h-4 w-4 text-teal" />
              Session inputs
            </CardTitle>
            <CardDescription>
              Typical Tier 2–3 micro-production defaults loaded.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <Field
              label="Stills"
              value={stillCount}
              onChange={setStillCount}
              min={0}
              max={100}
              step={1}
              suffix={`${stillCount} images`}
            />
            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-subtle">
                Still model
              </p>
              <div className="mt-2 flex flex-wrap gap-1.5">
                {STILL_LABELS.map((opt) => (
                  <button
                    key={opt.id}
                    type="button"
                    onClick={() => setStillTier(opt.id)}
                    className={cn(
                      "h-9 rounded-md border px-3 text-xs font-medium transition-colors",
                      stillTier === opt.id
                        ? "border-teal/40 bg-teal/10 text-teal"
                        : "border-border bg-surface text-muted hover:text-fg",
                    )}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
              <p className="mt-2 text-[11px] text-subtle leading-relaxed">
                1.0 is unchanged Nov 2. Hero plates: 2.0 medium. The retiring
                image-quality slug redirects to 2.0-low.
              </p>
            </div>

            <Field
              label="Video duration"
              value={videoSeconds}
              onChange={setVideoSeconds}
              min={0}
              max={120}
              step={1}
              suffix={`${videoSeconds} seconds`}
            />
            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-subtle">
                Video model · resolution
              </p>
              <div className="mt-2 flex flex-wrap gap-1.5">
                {VIDEO_BUTTONS.map((opt) => (
                  <button
                    key={opt.id}
                    type="button"
                    onClick={() => setVideoKey(opt.id)}
                    className={cn(
                      "h-9 rounded-md border px-3 text-xs font-medium transition-colors",
                      videoKey === opt.id
                        ? "border-teal/40 bg-teal/10 text-teal"
                        : "border-border bg-surface text-muted hover:text-fg",
                    )}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            <Field
              label="Chat input tokens (thousands)"
              value={chatInK}
              onChange={setChatInK}
              min={0}
              max={500}
              step={1}
              suffix={`${chatInK}k tokens · $2/1M`}
            />
            <Field
              label="Chat output tokens (thousands)"
              value={chatOutK}
              onChange={setChatOutK}
              min={0}
              max={500}
              step={1}
              suffix={`${chatOutK}k tokens · $6/1M`}
            />
            <Field
              label="Contingency buffer"
              value={bufferPct}
              onChange={setBufferPct}
              min={0}
              max={50}
              step={1}
              suffix={`${bufferPct}% for retries / QA regen`}
            />

            <Button type="button" variant="secondary" onClick={reset}>
              <RotateCcw className="h-4 w-4" />
              Reset defaults
            </Button>
          </CardContent>
        </Card>

        <div className="space-y-4 lg:sticky lg:top-20 lg:self-start">
          <Card className="border-teal/30 bg-teal/5">
            <CardHeader>
              <CardDescription>Estimated session total (list)</CardDescription>
              <CardTitle className="font-mono text-4xl tracking-tight text-teal">
                {money(breakdown.total)}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <Row label="Subtotal" value={money(breakdown.subtotal)} />
              <Row
                label={`Buffer (${bufferPct}%)`}
                value={money(breakdown.buffer)}
              />
              <div className="border-t border-border pt-3">
                <Row label="Total" value={money(breakdown.total)} strong />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Breakdown</CardTitle>
              <CardDescription>Share of subtotal before buffer</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {breakdown.lines.map((line) => (
                <div key={line.id}>
                  <div className="mb-1.5 flex items-center justify-between gap-2 text-sm">
                    <span className="text-muted">{line.label}</span>
                    <span className="font-mono tabular-nums text-fg">
                      {money(line.amount)}
                    </span>
                  </div>
                  <div className="h-1.5 overflow-hidden rounded-full bg-border">
                    <div
                      className="h-full rounded-full bg-teal transition-all"
                      style={{ width: `${Math.round(line.share * 100)}%` }}
                    />
                  </div>
                </div>
              ))}
              <p className="text-xs text-subtle pt-1">
                Video often dominates once you leave stills. Lock plates before
                1.5 / 1080p chains. 6s @ 1.5 720p is ~$0.84 list.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Quick scenarios</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-2">
              <button
                type="button"
                className="h-9 rounded-md border border-border bg-surface px-3 text-xs text-muted hover:text-fg"
                onClick={() => {
                  setStillCount(4);
                  setStillTier("standard");
                  setVideoSeconds(0);
                  setChatInK(5);
                  setChatOutK(2);
                  setBufferPct(10);
                }}
              >
                Tier 1 stills only
              </button>
              <button
                type="button"
                className="h-9 rounded-md border border-border bg-surface px-3 text-xs text-muted hover:text-fg"
                onClick={() => {
                  setStillCount(6);
                  setStillTier("standard");
                  setVideoSeconds(18);
                  setVideoKey("v10_720");
                  setChatInK(30);
                  setChatOutK(12);
                  setBufferPct(20);
                }}
              >
                Tier 2 short film
              </button>
              <button
                type="button"
                className="h-9 rounded-md border border-border bg-surface px-3 text-xs text-muted hover:text-fg"
                onClick={() => {
                  setStillCount(12);
                  setStillTier("med1k");
                  setVideoSeconds(45);
                  setVideoKey("v15_720");
                  setChatInK(80);
                  setChatOutK(40);
                  setBufferPct(25);
                }}
              >
                Tier 3 trailer pass
              </button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
  min,
  max,
  step,
  suffix,
}: {
  label: string;
  value: number;
  onChange: (n: number) => void;
  min: number;
  max: number;
  step: number;
  suffix: string;
}) {
  return (
    <label className="block">
      <div className="flex items-center justify-between gap-2">
        <span className="text-xs font-medium uppercase tracking-wide text-subtle">
          {label}
        </span>
        <span className="font-mono text-xs text-teal">{suffix}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="mt-2 w-full accent-teal"
      />
      <input
        type="number"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value) || 0)}
        className="mt-2 h-10 w-full rounded-lg border border-border bg-bg px-3 font-mono text-sm text-fg outline-none focus:border-border-strong focus:ring-2 focus:ring-teal/30"
      />
    </label>
  );
}

function Row({
  label,
  value,
  strong,
}: {
  label: string;
  value: string;
  strong?: boolean;
}) {
  return (
    <div className="flex items-center justify-between gap-3">
      <span className={strong ? "text-fg font-medium" : "text-muted"}>
        {label}
      </span>
      <span
        className={cn(
          "font-mono tabular-nums",
          strong ? "text-fg font-semibold" : "text-fg",
        )}
      >
        {value}
      </span>
    </div>
  );
}
