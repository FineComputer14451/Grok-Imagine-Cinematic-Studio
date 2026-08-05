import { createFileRoute, Link } from "@tanstack/react-router";
import { Palette, Search } from "lucide-react";
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
  COLOR_LEVELS,
  COLOR_RECIPES,
  COLOR_TOPICS,
  GRADE_LOOKS,
  type ColorTopic,
} from "@/data/color";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/color")({
  component: ColorPage,
});

const CHEAT = `COLOR & GRADE CHEAT (Studio Academy)
Looks: teal-orange · neon split · cold steel · warm candle · bleach · pastel · mono · natural

Rules
1. White balance follows practicals / DoP card
2. Protect skin when stylizing environments
3. One hue-contrast strategy per sequence
4. Chroma hierarchy: hero color > support > mute field
5. Grade continuity across stills + extends
6. Prompt: [look] + [skin line] + [contrast] + [sat]

Pattern
neon-motivated teal/amber grade, warm skin protected, medium-high contrast, controlled saturation`;

function ColorPage() {
  const [q, setQ] = useState("");
  const [level, setLevel] = useState<ColorTopic["level"] | "all">("all");
  const [lookId, setLookId] = useState(GRADE_LOOKS[1]?.id ?? "neon-split");
  const [topicId, setTopicId] = useState(COLOR_TOPICS[0]?.id ?? "");
  const [recipeId, setRecipeId] = useState(COLOR_RECIPES[0]?.id ?? "");

  const filteredTopics = useMemo(() => {
    return COLOR_TOPICS.filter((t) => {
      if (level !== "all" && t.level !== level) return false;
      if (!q.trim()) return true;
      const hay = `${t.title} ${t.short} ${t.body} ${t.rule}`.toLowerCase();
      return hay.includes(q.trim().toLowerCase());
    });
  }, [q, level]);

  const look = GRADE_LOOKS.find((l) => l.id === lookId) ?? GRADE_LOOKS[0];
  const topic =
    filteredTopics.find((t) => t.id === topicId) ?? filteredTopics[0] ?? null;
  const recipe =
    COLOR_RECIPES.find((r) => r.id === recipeId) ?? COLOR_RECIPES[0];

  return (
    <div className="space-y-8">
      <div>
        <Badge variant="teal">Cinematography</Badge>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">
          Color & grading
        </h1>
        <p className="mt-2 max-w-2xl text-muted leading-relaxed">
          Looks, skin protection, contrast, and how to write grade lines into
          Imagine packets — the finish pass after lighting and lenses.
        </p>
      </div>

      <div className="flex flex-wrap gap-1.5">
        {GRADE_LOOKS.map((l) => (
          <button
            key={l.id}
            type="button"
            onClick={() => setLookId(l.id)}
            className={cn(
              "h-9 rounded-md border px-3 text-xs font-medium",
              lookId === l.id
                ? "border-teal/40 bg-teal/10 text-teal"
                : "border-border bg-surface text-muted hover:text-fg",
            )}
          >
            {l.name}
          </button>
        ))}
      </div>

      {look && (
        <Card className="border-teal/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-xl">
              <Palette className="h-5 w-5 text-teal" />
              {look.name}
            </CardTitle>
            <CardDescription>{look.short}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-2">
              {look.palette.map((hex) => (
                <div key={hex} className="flex items-center gap-2">
                  <span
                    className="h-9 w-9 rounded-lg border border-border shadow-inner"
                    style={{ backgroundColor: hex }}
                    title={hex}
                  />
                  <span className="font-mono text-[10px] text-subtle">
                    {hex}
                  </span>
                </div>
              ))}
            </div>
            <p className="text-sm leading-relaxed text-muted">{look.body}</p>
            <div className="grid gap-2 sm:grid-cols-2">
              {(
                [
                  ["Skin", look.skin],
                  ["Contrast", look.contrast],
                  ["Saturation", look.saturation],
                  ["When", look.when],
                  ["Avoid", look.avoid],
                  ["Pairs with", look.pairsWith],
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
                  <p className="mt-1 font-mono text-xs text-fg">{look.packet}</p>
                </div>
                <CopyButton text={look.packet} label="Copy" />
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
            placeholder="Search skin, saturation, continuity…"
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
          {COLOR_LEVELS.map((l) => (
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
            Project grade recipes
          </h2>
          <p className="mt-1 text-sm text-muted">
            Tied to Academy presets — drop into DoP color line or Prompt lab.
          </p>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {COLOR_RECIPES.map((r) => (
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
                  ["Look", recipe.look],
                  ["Lighting link", recipe.lightingLink],
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
              <CardDescription>Look + skin + contrast pattern</CardDescription>
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
              Lighting
            </Link>
            <Link to="/dop" className="text-teal hover:underline">
              DoP card
            </Link>
            <Link to="/lenses" className="text-teal hover:underline">
              Lenses
            </Link>
            <Link to="/movement" className="text-teal hover:underline">
              Movement
            </Link>
            <Link to="/lab" className="text-teal hover:underline">
              Prompt lab
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
