import { createFileRoute, Link } from "@tanstack/react-router";
import { Move, Search } from "lucide-react";
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
  ENERGY_TONE,
  MOVE_LEVELS,
  MOVE_RECIPES,
  MOVE_TOPICS,
  MOVE_TYPES,
  type MoveTopic,
} from "@/data/movement";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/movement")({
  component: MovementPage,
});

const CHEAT = `CAMERA MOVEMENT CHEAT (Studio Academy)
Types: static · pan · tilt · push-in · pull-out · track · orbit · handheld · crane · FPV

Rules
1. Motivate the move (story/attention) — don’t decorate
2. Stills-first: lock plates static, then one simple video move
3. One primary move per 6s clip
4. Prefer “slow push-in (dolly)” over vague “zoom”
5. Horizon: level unless dutch is intentional
6. motion_out in LAST_FRAME_RECAP for extends

Prompt pattern
[speed] [move] [direction] [end framing] [horizon]
e.g. slow push-in toward face, end MCU, horizon level, 6s`;

function MovementPage() {
  const [q, setQ] = useState("");
  const [level, setLevel] = useState<MoveTopic["level"] | "all">("all");
  const [moveId, setMoveId] = useState(MOVE_TYPES[0]?.id ?? "static");
  const [topicId, setTopicId] = useState(MOVE_TOPICS[0]?.id ?? "");
  const [recipeId, setRecipeId] = useState(MOVE_RECIPES[0]?.id ?? "");

  const filteredTopics = useMemo(() => {
    return MOVE_TOPICS.filter((t) => {
      if (level !== "all" && t.level !== level) return false;
      if (!q.trim()) return true;
      const hay = `${t.title} ${t.short} ${t.body} ${t.rule}`.toLowerCase();
      return hay.includes(q.trim().toLowerCase());
    });
  }, [q, level]);

  const move = MOVE_TYPES.find((m) => m.id === moveId) ?? MOVE_TYPES[0];
  const topic =
    filteredTopics.find((t) => t.id === topicId) ?? filteredTopics[0] ?? null;
  const recipe =
    MOVE_RECIPES.find((r) => r.id === recipeId) ?? MOVE_RECIPES[0];

  return (
    <div className="space-y-8">
      <div>
        <Badge variant="teal">Cinematography</Badge>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">
          Camera movement
        </h1>
        <p className="mt-2 max-w-2xl text-muted leading-relaxed">
          Static holds to push-ins and tracks — when to move, how to write motion
          for short Imagine clips, and how extends inherit{" "}
          <span className="text-fg">motion_out</span>.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Energy scale</CardTitle>
          <CardDescription>
            Prefer left side until plates and identity are locked
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {(
              [
                ["static", "Static"],
                ["slow", "Slow"],
                ["medium", "Medium"],
                ["fast", "Fast"],
              ] as const
            ).map(([k, label]) => (
              <span
                key={k}
                className={cn(
                  "rounded-md border px-3 py-1.5 text-xs font-medium capitalize",
                  ENERGY_TONE[k],
                )}
              >
                {label}
              </span>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="flex flex-wrap gap-1.5">
        {MOVE_TYPES.map((m) => (
          <button
            key={m.id}
            type="button"
            onClick={() => setMoveId(m.id)}
            className={cn(
              "h-9 rounded-md border px-3 text-xs font-medium",
              moveId === m.id
                ? "border-teal/40 bg-teal/10 text-teal"
                : "border-border bg-surface text-muted hover:text-fg",
            )}
          >
            {m.name.split(" / ")[0]}
          </button>
        ))}
      </div>

      {move && (
        <Card className="border-teal/20">
          <CardHeader>
            <div className="flex flex-wrap items-center gap-2">
              <span
                className={cn(
                  "rounded border px-2 py-0.5 text-[10px] font-semibold uppercase",
                  ENERGY_TONE[move.energy],
                )}
              >
                {move.energy}
              </span>
              <Badge variant="outline">{move.name}</Badge>
            </div>
            <CardTitle className="mt-2 flex items-center gap-2 text-xl">
              <Move className="h-5 w-5 text-teal" />
              {move.name}
            </CardTitle>
            <CardDescription>{move.short}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm leading-relaxed text-muted">{move.body}</p>
            <div className="grid gap-2 sm:grid-cols-2">
              {(
                [
                  ["Stills", move.stillsNote],
                  ["Video", move.videoNote],
                  ["Pairs with", move.pairsWith],
                  ["Avoid", move.avoid],
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
            </div>
            <div className="rounded-lg border border-teal/30 bg-teal/5 px-3 py-3">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <p className="text-[11px] uppercase tracking-wide text-teal">
                    Packet crumb
                  </p>
                  <p className="mt-1 font-mono text-xs text-fg">{move.packet}</p>
                </div>
                <CopyButton text={move.packet} label="Copy" />
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <label className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-subtle" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search push-in, parallax, extends…"
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
          {MOVE_LEVELS.map((l) => (
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
        <ul className="max-h-[50dvh] space-y-1.5 overflow-y-auto pr-1">
          {filteredTopics.map((t) => {
            const selected = topic?.id === t.id;
            return (
              <li key={t.id}>
                <button
                  type="button"
                  onClick={() => setTopicId(t.id)}
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

        {topic && (
          <Card className="h-fit lg:sticky lg:top-20">
            <CardHeader>
              <Badge variant="teal" className="w-fit capitalize">
                {topic.level}
              </Badge>
              <CardTitle className="mt-2 text-xl">{topic.title}</CardTitle>
              <CardDescription>{topic.short}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 text-sm leading-relaxed text-muted">
              <p>{topic.body}</p>
              <div className="rounded-lg border border-border bg-bg px-3 py-2.5">
                <p className="text-[11px] uppercase tracking-wide text-subtle">
                  Rule
                </p>
                <p className="mt-1 text-fg">{topic.rule}</p>
              </div>
              <div className="rounded-lg border border-teal/30 bg-teal/5 px-3 py-2.5">
                <p className="text-[11px] uppercase tracking-wide text-teal">
                  Studio tip
                </p>
                <p className="mt-1">{topic.studioTip}</p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      <section className="space-y-4">
        <div>
          <h2 className="text-lg font-semibold tracking-tight">
            Motion recipes
          </h2>
          <p className="mt-1 text-sm text-muted">
            Short-clip patterns after plate lock — copy into handoff motion
            vectors.
          </p>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {MOVE_RECIPES.map((r) => (
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
                <CopyButton text={recipe.packet} label="Copy" />
              </div>
            </CardHeader>
            <CardContent className="grid gap-2 sm:grid-cols-2">
              {(
                [
                  ["Moves", recipe.moves],
                  ["Duration", recipe.duration],
                  ["Plate", recipe.plate],
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
                  <p className="mt-1 text-sm text-fg">{value}</p>
                </div>
              ))}
              <div className="rounded-lg border border-teal/30 bg-teal/5 px-3 py-2.5 sm:col-span-2">
                <p className="text-[11px] uppercase tracking-wide text-teal">
                  Packet
                </p>
                <p className="mt-1 font-mono text-xs leading-relaxed text-fg">
                  {recipe.packet}
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
              <CardDescription>One move · one speed · one end frame</CardDescription>
            </div>
            <CopyButton text={CHEAT} label="Copy" />
          </div>
        </CardHeader>
        <CardContent>
          <pre className="whitespace-pre-wrap rounded-lg border border-border bg-bg p-3.5 font-mono text-[11px] leading-relaxed text-muted">
            {CHEAT}
          </pre>
          <div className="mt-4 flex flex-wrap gap-2 text-sm">
            <Link to="/lenses" className="text-teal hover:underline">
              Lenses
            </Link>
            <Link to="/composition" className="text-teal hover:underline">
              Framing
            </Link>
            <Link to="/recap" className="text-teal hover:underline">
              Last-frame recap
            </Link>
            <Link to="/scenarios" className="text-teal hover:underline">
              Plate → 6s
            </Link>
            <Link to="/consistency" className="text-teal hover:underline">
              Consistency
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
