import { createFileRoute, Link } from "@tanstack/react-router";
import { Frame, Search } from "lucide-react";
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
  COMP_LEVELS,
  COMP_RECIPES,
  COMP_TOPICS,
  SHOT_SIZES,
  type CompTopic,
} from "@/data/composition";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/composition")({
  component: CompositionPage,
});

const CHEAT = `COMPOSITION CHEAT (Studio Academy)
1. Shot size — EWS → WS → MS → MCU → CU → ECU
2. Height — eye-level neutral · low = power · high = vulnerability
3. Thirds — eyes on upper third · looking room in gaze direction
4. Lead room — space where they look / move
5. Depth — FG / MG / BG layers
6. Lines — one dominant system; dutch sparingly
7. 180° — keep screen direction for multi-shot sets
8. Prompt — size + height + placement + lens
9. Continuity — recap framing on extends

Shot list framing field = size · height
DoP format line = aspect / lens set`;

function CompositionPage() {
  const [q, setQ] = useState("");
  const [level, setLevel] = useState<CompTopic["level"] | "all">("all");
  const [openId, setOpenId] = useState(COMP_TOPICS[0]?.id ?? "");
  const [recipeId, setRecipeId] = useState(COMP_RECIPES[0]?.id ?? "");

  const filtered = useMemo(() => {
    return COMP_TOPICS.filter((t) => {
      if (level !== "all" && t.level !== level) return false;
      if (!q.trim()) return true;
      const hay = `${t.title} ${t.short} ${t.body} ${t.rule}`.toLowerCase();
      return hay.includes(q.trim().toLowerCase());
    });
  }, [q, level]);

  const active =
    filtered.find((t) => t.id === openId) ?? filtered[0] ?? null;
  const recipe =
    COMP_RECIPES.find((r) => r.id === recipeId) ?? COMP_RECIPES[0];

  return (
    <div className="space-y-8">
      <div>
        <Badge variant="teal">Cinematography</Badge>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">
          Composition & framing
        </h1>
        <p className="mt-2 max-w-2xl text-muted leading-relaxed">
          Shot size, thirds, eyeline, depth, and how to write framing into shot
          lists and Imagine packets — the partner to lighting basics.
        </p>
      </div>

      {/* Visual thirds grid */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Thirds grid (mental model)</CardTitle>
          <CardDescription>
            Place eyes on upper intersections · leave looking room
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="relative mx-auto aspect-video max-w-lg overflow-hidden rounded-xl border border-border bg-elevated/50">
            {/* grid lines */}
            <div className="pointer-events-none absolute inset-0 grid grid-cols-3 grid-rows-3">
              {Array.from({ length: 9 }).map((_, i) => (
                <div key={i} className="border border-border/60" />
              ))}
            </div>
            <div className="absolute left-[16%] top-[28%] h-3 w-3 rounded-full bg-teal shadow-[0_0_12px_color-mix(in_oklab,#2dd4bf_60%,transparent)]" />
            <p className="absolute left-[22%] top-[26%] text-[10px] font-medium text-teal">
              eye / interest
            </p>
            <div className="absolute bottom-3 left-3 right-3 flex justify-between text-[10px] text-subtle">
              <span>looking room →</span>
              <span>avoid dead center by default</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Shot sizes ladder */}
      <section className="space-y-3">
        <h2 className="text-lg font-semibold tracking-tight">Shot size ladder</h2>
        <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {SHOT_SIZES.map((s) => (
            <div
              key={s.id}
              className="rounded-xl border border-border bg-surface px-3.5 py-3"
            >
              <div className="flex items-center justify-between gap-2">
                <p className="font-medium text-fg">{s.name}</p>
                <span className="font-mono text-[11px] text-teal">{s.code}</span>
              </div>
              <p className="mt-1 text-xs text-muted">{s.frames}</p>
              <p className="mt-2 text-xs text-subtle">
                <span className="text-fg">Use:</span> {s.use}
              </p>
              <p className="mt-1 text-xs text-subtle">
                <span className="text-fg">Light:</span> {s.lightingNote}
              </p>
            </div>
          ))}
        </div>
      </section>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <label className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-subtle" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search thirds, eyeline, coverage…"
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
          {COMP_LEVELS.map((l) => (
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
        <ul className="max-h-[60dvh] space-y-1.5 overflow-y-auto pr-1">
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
                <Frame className="h-5 w-5 text-teal" />
                {active.title}
              </CardTitle>
              <CardDescription>{active.short}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 text-sm leading-relaxed text-muted">
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

      <section className="space-y-4">
        <div>
          <h2 className="text-lg font-semibold tracking-tight">
            Framing recipes
          </h2>
          <p className="mt-1 text-sm text-muted">
            Copy the packet line into Prompt lab or a shot list notes field.
          </p>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {COMP_RECIPES.map((r) => (
            <button
              key={r.id}
              type="button"
              onClick={() => setRecipeId(r.id)}
              className={cn(
                "h-9 rounded-md border px-3 text-xs font-medium",
                recipeId === r.id
                  ? "border-teal/40 bg-teal/10 text-teal"
                  : "border-border bg-surface text-muted hover:text-fg",
              )}
            >
              {r.name}
            </button>
          ))}
        </div>
        {recipe && (
          <Card>
            <CardHeader>
              <div className="flex items-start justify-between gap-2">
                <div>
                  <CardTitle className="text-xl">{recipe.name}</CardTitle>
                  <CardDescription>{recipe.mood}</CardDescription>
                </div>
                <CopyButton text={recipe.packetLine} label="Copy line" />
              </div>
            </CardHeader>
            <CardContent className="grid gap-3 sm:grid-cols-2">
              {(
                [
                  ["Framing", recipe.framing],
                  ["Lens feel", recipe.lensFeel],
                  ["Subject", recipe.subject],
                  ["Background", recipe.background],
                  ["When", recipe.when],
                ] as const
              ).map(([label, value]) => (
                <div
                  key={label}
                  className="rounded-lg border border-border bg-bg px-3 py-2.5"
                >
                  <p className="text-[11px] uppercase tracking-wide text-subtle">
                    {label}
                  </p>
                  <p className="mt-1 text-sm leading-snug text-fg">{value}</p>
                </div>
              ))}
              <div className="rounded-lg border border-teal/30 bg-teal/5 px-3 py-2.5 sm:col-span-2">
                <p className="text-[11px] uppercase tracking-wide text-teal">
                  Packet line
                </p>
                <p className="mt-1 font-mono text-xs leading-relaxed text-fg">
                  {recipe.packetLine}
                </p>
              </div>
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
            <Link to="/lighting" className="text-teal hover:underline">
              Lighting basics
            </Link>
            <Link to="/dop" className="text-teal hover:underline">
              DoP card
            </Link>
            <Link to="/shots" className="text-teal hover:underline">
              Shot list
            </Link>
            <Link to="/lab" className="text-teal hover:underline">
              Prompt lab
            </Link>
            <Link to="/recap" className="text-teal hover:underline">
              Last-frame recap
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
