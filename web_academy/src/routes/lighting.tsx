import { createFileRoute, Link } from "@tanstack/react-router";
import { Lightbulb, Search } from "lucide-react";
import { useMemo, useState } from "react";
import { CopyButton } from "@/components/copy-button";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  LIGHTING_LEVELS,
  LIGHTING_SETUPS,
  LIGHTING_TOPICS,
  type LightingTopic,
} from "@/data/lighting";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/lighting")({
  component: LightingPage,
});

const CHEAT = `LIGHTING CHEAT (Studio Academy)
1. Key — main motivated source & direction
2. Fill — shadow depth (or negative fill)
3. Rim — separate subject from bg
4. Practicals — in-world lights that justify color
5. Ratio — lock mood (2:1 gentle · 4:1 drama · 8:1 noir)
6. Quality — hard vs soft (size relative to subject)
7. Color — warm/cool strategy once per sequence
8. Prompt — subject → env → lighting → lens → mood
9. Continuity — recap key side + practical state on extends

DoP card inherits all of the above.`;

function LightingPage() {
  const [q, setQ] = useState("");
  const [level, setLevel] = useState<LightingTopic["level"] | "all">("all");
  const [openId, setOpenId] = useState(LIGHTING_TOPICS[0]?.id ?? "");
  const [setupId, setSetupId] = useState(LIGHTING_SETUPS[0]?.id ?? "");

  const filtered = useMemo(() => {
    return LIGHTING_TOPICS.filter((t) => {
      if (level !== "all" && t.level !== level) return false;
      if (!q.trim()) return true;
      const hay = `${t.title} ${t.short} ${t.body} ${t.rule}`.toLowerCase();
      return hay.includes(q.trim().toLowerCase());
    });
  }, [q, level]);

  const active =
    filtered.find((t) => t.id === openId) ?? filtered[0] ?? null;
  const setup =
    LIGHTING_SETUPS.find((s) => s.id === setupId) ?? LIGHTING_SETUPS[0];

  return (
    <div className="space-y-8">
      <div>
        <Badge variant="teal">Cinematography</Badge>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">
          Lighting basics
        </h1>
        <p className="mt-2 max-w-2xl text-muted leading-relaxed">
          Key, fill, rim, practicals, ratio, and color — then how to write them
          into Imagine packets and DoP cards without drifting shot to shot.
        </p>
      </div>

      {/* Simple visual: 3-point diagram */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Three-point map</CardTitle>
          <CardDescription>
            Mental model before stylized neon / candle looks
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="relative mx-auto max-w-md aspect-square rounded-2xl border border-border bg-elevated/40 p-6">
            <div className="absolute left-1/2 top-[18%] -translate-x-1/2 text-center">
              <div className="mx-auto h-10 w-10 rounded-full border-2 border-amber/50 bg-amber/20" />
              <p className="mt-1 text-xs font-medium text-amber">Key</p>
              <p className="text-[10px] text-subtle">main shape</p>
            </div>
            <div className="absolute left-[12%] top-[42%] text-center">
              <div className="mx-auto h-8 w-8 rounded-full border-2 border-teal/40 bg-teal/15" />
              <p className="mt-1 text-xs font-medium text-teal">Fill</p>
              <p className="text-[10px] text-subtle">shadows</p>
            </div>
            <div className="absolute right-[12%] top-[38%] text-center">
              <div className="mx-auto h-8 w-8 rounded-full border-2 border-fg/30 bg-fg/10" />
              <p className="mt-1 text-xs font-medium text-fg">Rim</p>
              <p className="text-[10px] text-subtle">edge</p>
            </div>
            <div className="absolute left-1/2 top-[58%] -translate-x-1/2 text-center">
              <div className="mx-auto flex h-16 w-12 items-end justify-center rounded-t-full border border-border bg-surface">
                <span className="mb-2 text-[10px] text-muted">Subject</span>
              </div>
            </div>
            <div className="absolute bottom-4 left-1/2 -translate-x-1/2 text-center">
              <p className="text-[10px] text-subtle">
                Practicals live in the set (lamps, neon, candle)
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <label className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-subtle" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search key, ratio, practicals…"
            className="h-11 w-full rounded-lg border border-border bg-surface pl-10 pr-3 text-sm text-fg placeholder:text-subtle outline-none focus:border-border-strong focus:ring-2 focus:ring-teal/30"
          />
        </label>
        <div className="flex flex-wrap gap-1.5">
          <button
            type="button"
            onClick={() => setLevel("all")}
            className={cn(
              "h-9 rounded-md border px-3 text-xs font-medium",
              level === "all"
                ? "border-teal/40 bg-teal/10 text-teal"
                : "border-border bg-surface text-muted hover:text-fg",
            )}
          >
            All
          </button>
          {LIGHTING_LEVELS.map((l) => (
            <button
              key={l.id}
              type="button"
              onClick={() => setLevel(l.id)}
              className={cn(
                "h-9 rounded-md border px-3 text-xs font-medium",
                level === l.id
                  ? "border-teal/40 bg-teal/10 text-teal"
                  : "border-border bg-surface text-muted hover:text-fg",
              )}
            >
              {l.label}
            </button>
          ))}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
        <ul className="space-y-1.5 max-h-[60dvh] overflow-y-auto pr-1">
          {filtered.map((t) => {
            const selected = active?.id === t.id;
            return (
              <li key={t.id}>
                <button
                  type="button"
                  onClick={() => setOpenId(t.id)}
                  className={cn(
                    "w-full rounded-xl border px-3.5 py-3 text-left transition-colors",
                    selected
                      ? "border-teal/40 bg-teal/5"
                      : "border-border bg-surface hover:border-border-strong",
                  )}
                >
                  <div className="flex items-start justify-between gap-2">
                    <p className="font-medium text-fg">{t.title}</p>
                    <Badge variant="outline" className="shrink-0 capitalize">
                      {t.level}
                    </Badge>
                  </div>
                  <p className="mt-1 line-clamp-2 text-sm text-muted">
                    {t.short}
                  </p>
                </button>
              </li>
            );
          })}
        </ul>

        {active && (
          <Card className="h-fit border-teal/20 lg:sticky lg:top-20">
            <CardHeader>
              <Badge variant="teal" className="w-fit capitalize">
                {active.level}
              </Badge>
              <CardTitle className="mt-2 flex items-center gap-2 text-xl">
                <Lightbulb className="h-5 w-5 text-teal" />
                {active.title}
              </CardTitle>
              <CardDescription>{active.short}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 text-sm text-muted leading-relaxed">
              <p>{active.body}</p>
              <div className="rounded-lg border border-border bg-bg px-3 py-3">
                <p className="text-[11px] uppercase tracking-wide text-subtle">
                  Rule
                </p>
                <p className="mt-1 text-fg">{active.rule}</p>
              </div>
              <div className="rounded-lg border border-teal/30 bg-teal/5 px-3 py-3">
                <p className="text-[11px] uppercase tracking-wide text-teal">
                  Studio tip
                </p>
                <p className="mt-1">{active.studioTip}</p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Setups */}
      <section className="space-y-4">
        <div>
          <h2 className="text-lg font-semibold tracking-tight">
            Common setups
          </h2>
          <p className="mt-1 text-sm text-muted">
            Recipes you can copy into a DoP card or Prompt lab lighting field.
          </p>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {LIGHTING_SETUPS.map((s) => (
            <button
              key={s.id}
              type="button"
              onClick={() => setSetupId(s.id)}
              className={cn(
                "h-9 rounded-md border px-3 text-xs font-medium",
                setupId === s.id
                  ? "border-teal/40 bg-teal/10 text-teal"
                  : "border-border bg-surface text-muted hover:text-fg",
              )}
            >
              {s.name}
            </button>
          ))}
        </div>
        {setup && (
          <Card>
            <CardHeader>
              <CardTitle className="text-xl">{setup.name}</CardTitle>
              <CardDescription>{setup.mood}</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-3 sm:grid-cols-2">
              {(
                [
                  ["Key", setup.key],
                  ["Fill", setup.fill],
                  ["Rim", setup.rim ?? "—"],
                  ["Practicals", setup.practicals ?? "—"],
                  ["Ratio", setup.ratio],
                  ["Color", setup.color],
                  ["Use when", setup.useWhen],
                  ["DoP hint", setup.dopHint],
                ] as const
              ).map(([label, value]) => (
                <div
                  key={label}
                  className="rounded-lg border border-border bg-bg px-3 py-2.5"
                >
                  <p className="text-[11px] uppercase tracking-wide text-subtle">
                    {label}
                  </p>
                  <p className="mt-1 text-sm text-fg leading-snug">{value}</p>
                </div>
              ))}
            </CardContent>
          </Card>
        )}
      </section>

      <Card className="border-teal/20">
        <CardHeader>
          <div className="flex items-start justify-between gap-2">
            <div>
              <CardTitle className="text-base">Cheat sheet</CardTitle>
              <CardDescription>Copy into notes or chat</CardDescription>
            </div>
            <CopyButton text={CHEAT} label="Copy" />
          </div>
        </CardHeader>
        <CardContent>
          <pre className="whitespace-pre-wrap rounded-lg border border-border bg-bg p-3.5 font-mono text-[11px] leading-relaxed text-muted">
            {CHEAT}
          </pre>
          <div className="mt-4 flex flex-wrap gap-2 text-sm">
            <Link to="/dop" className="text-teal hover:underline">
              Open DoP card
            </Link>
            <Link to="/lab" className="text-teal hover:underline">
              Prompt lab
            </Link>
            <Link to="/consistency" className="text-teal hover:underline">
              Consistency algorithms
            </Link>
            <Link to="/recap" className="text-teal hover:underline">
              Last-frame recap
            </Link>
            <Link to="/glossary" className="text-teal hover:underline">
              Glossary
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
