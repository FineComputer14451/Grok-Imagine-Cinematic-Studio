import { createFileRoute, Link } from "@tanstack/react-router";
import { Scissors, Search } from "lucide-react";
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
  CUT_TYPES,
  EDIT_LEVELS,
  EDIT_TOPICS,
  PACE_RECIPES,
  type EditTopic,
} from "@/data/editing";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/editing")({
  component: EditingPage,
});

const CHEAT = `EDITING & PACING CHEAT (Studio Academy)

SPINE (short teaser)
Establish (wide) → character (MS) → identity/emotion (CU) → button

CUTS
hard (default) · match · J/L (needs audio) · smash (once) · dissolve (time/mood) · cross-cut

DURATION
wides longer · CUs shorter · still montage ~1.5–3s · vary rhythm

RULES
1. Selection > decoration — kill shots that miss the logline
2. Motivate cuts (eyeline, action, beat)
3. QA Go before stitch — no identity No-Go in the cut
4. Prefer stills-first montage over broken motion loops
5. One accent hit per major cut with music

24s HYBRID SKETCH
3s still · 6s push clip · 3s still · 6s track clip · 6s button still`;

function EditingPage() {
  const [q, setQ] = useState("");
  const [level, setLevel] = useState<EditTopic["level"] | "all">("all");
  const [cutId, setCutId] = useState(CUT_TYPES[0]?.id ?? "hard");
  const [topicId, setTopicId] = useState(EDIT_TOPICS[0]?.id ?? "");
  const [recipeId, setRecipeId] = useState(PACE_RECIPES[1]?.id ?? "24s-hybrid");

  const filteredTopics = useMemo(() => {
    return EDIT_TOPICS.filter((t) => {
      if (level !== "all" && t.level !== level) return false;
      if (!q.trim()) return true;
      const hay = `${t.title} ${t.short} ${t.body} ${t.rule}`.toLowerCase();
      return hay.includes(q.trim().toLowerCase());
    });
  }, [q, level]);

  const cut = CUT_TYPES.find((c) => c.id === cutId) ?? CUT_TYPES[0];
  const topic =
    filteredTopics.find((t) => t.id === topicId) ?? filteredTopics[0] ?? null;
  const recipe =
    PACE_RECIPES.find((r) => r.id === recipeId) ?? PACE_RECIPES[0];

  const timeline =
    recipe?.id === "24s-hybrid"
      ? [
          { t: "0–3s", label: "Still establish", c: "bg-elevated" },
          { t: "3–9s", label: "6s push clip", c: "bg-teal/20" },
          { t: "9–12s", label: "Still CU", c: "bg-elevated" },
          { t: "12–18s", label: "6s track", c: "bg-teal/20" },
          { t: "18–24s", label: "Button still", c: "bg-amber/20" },
        ]
      : recipe?.id === "15s-still"
        ? [
            { t: "0–3s", label: "Wide", c: "bg-elevated" },
            { t: "3–7s", label: "Medium", c: "bg-elevated" },
            { t: "7–11s", label: "CU", c: "bg-teal/20" },
            { t: "11–15s", label: "Button", c: "bg-amber/20" },
          ]
        : [
            { t: "Open", label: "Hold A", c: "bg-elevated" },
            { t: "Mid", label: "Hold B", c: "bg-teal/15" },
            { t: "Close", label: "Button", c: "bg-amber/15" },
          ];

  return (
    <div className="space-y-8">
      <div>
        <Badge variant="teal">Post</Badge>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">
          Editing & pacing
        </h1>
        <p className="mt-2 max-w-2xl text-muted leading-relaxed">
          How to order stills and short clips into a teaser — cuts, duration,
          montage vs continuity, and QA-before-stitch discipline.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Timeline sketch</CardTitle>
          <CardDescription>
            Visualize the selected pace recipe
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex h-14 overflow-hidden rounded-lg border border-border">
            {timeline.map((seg) => (
              <div
                key={seg.t + seg.label}
                className={cn(
                  "flex min-w-0 flex-1 flex-col items-center justify-center border-r border-border last:border-r-0 px-1",
                  seg.c,
                )}
              >
                <span className="truncate text-[10px] font-mono text-subtle">
                  {seg.t}
                </span>
                <span className="truncate text-[10px] font-medium text-fg">
                  {seg.label}
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="flex flex-wrap gap-1.5">
        {CUT_TYPES.map((c) => (
          <button
            key={c.id}
            type="button"
            onClick={() => setCutId(c.id)}
            className={cn(
              "h-9 rounded-md border px-3 text-xs font-medium",
              cutId === c.id
                ? "border-teal/40 bg-teal/10 text-teal"
                : "border-border bg-surface text-muted hover:text-fg",
            )}
          >
            {c.name}
          </button>
        ))}
      </div>

      {cut && (
        <Card className="border-teal/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-xl">
              <Scissors className="h-5 w-5 text-teal" />
              {cut.name}
            </CardTitle>
            <CardDescription>{cut.short}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm leading-relaxed text-muted">{cut.body}</p>
            <div className="grid gap-2 sm:grid-cols-2">
              <div className="rounded-lg border border-border bg-bg px-3 py-2.5">
                <p className="text-[11px] uppercase tracking-wide text-subtle">
                  When
                </p>
                <p className="mt-1 text-sm text-fg">{cut.when}</p>
              </div>
              <div className="rounded-lg border border-border bg-bg px-3 py-2.5">
                <p className="text-[11px] uppercase tracking-wide text-subtle">
                  Avoid
                </p>
                <p className="mt-1 text-sm text-fg">{cut.avoid}</p>
              </div>
            </div>
            <div className="rounded-lg border border-teal/30 bg-teal/5 px-3 py-3">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <p className="text-[11px] uppercase tracking-wide text-teal">
                    Note crumb
                  </p>
                  <p className="mt-1 font-mono text-xs text-fg">{cut.packet}</p>
                </div>
                <CopyButton text={cut.packet} label="Copy" />
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
            placeholder="Search montage, rhythm, stitch…"
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
          {EDIT_LEVELS.map((l) => (
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
          <h2 className="text-lg font-semibold tracking-tight">Pace recipes</h2>
          <p className="mt-1 text-sm text-muted">
            Ready timelines for Academy-length teasers.
          </p>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {PACE_RECIPES.map((r) => (
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
              <CardTitle className="text-xl">{recipe.name}</CardTitle>
              <CardDescription>{recipe.mood}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid gap-2 sm:grid-cols-2">
                {(
                  [
                    ["Structure", recipe.structure],
                    ["Durations", recipe.durations],
                    ["Music", recipe.music],
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
              </div>
              <ul className="space-y-1.5">
                {recipe.checklist.map((item) => (
                  <li
                    key={item}
                    className="flex gap-2 text-sm text-muted"
                  >
                    <span className="text-teal">·</span>
                    {item}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}
      </section>

      <Card className="border-teal/20">
        <CardHeader>
          <div className="flex items-start justify-between gap-2">
            <div>
              <CardTitle className="text-base">Cheat sheet</CardTitle>
              <CardDescription>Spine · cuts · hybrid 24s</CardDescription>
            </div>
            <CopyButton text={CHEAT} label="Copy" />
          </div>
        </CardHeader>
        <CardContent>
          <pre className="whitespace-pre-wrap rounded-lg border border-border bg-bg p-3.5 font-mono text-[11px] leading-relaxed text-muted">
            {CHEAT}
          </pre>
          <div className="mt-4 flex flex-wrap gap-2 text-sm">
            <Link to="/shots" className="text-teal hover:underline">
              Shot list
            </Link>
            <Link to="/movement" className="text-teal hover:underline">
              Movement
            </Link>
            <Link to="/consistency" className="text-teal hover:underline">
              Consistency QA
            </Link>
            <Link to="/scenarios" className="text-teal hover:underline">
              Scenarios
            </Link>
            <Link to="/pack" className="text-teal hover:underline">
              Project pack
            </Link>
            <Link to="/craft" className="text-teal hover:underline">
              Craft hub
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
