import { createFileRoute, Link } from "@tanstack/react-router";
import { AudioLines, Search } from "lucide-react";
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
  SOUND_LAYERS,
  SOUND_LEVELS,
  SOUND_RECIPES,
  SOUND_TOPICS,
  type SoundTopic,
} from "@/data/sound";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/sound")({
  component: SoundPage,
});

const CHEAT = `SOUND DESIGN CHEAT (Studio Academy)

LAYERS (top → bottom attention)
VO/story hit → designed SFX → foley → music → atmos → silence

RULES
1. Picture spine first — sound won’t fix a weak cut
2. One hero sound event at a time
3. Cut points are candidate hit points
4. Trait-based music briefs (not titled clones)
5. Silent still montage is valid early
6. No clipping on button hits

BRIEF PATTERN
duration · music · atmos · foley · sfx hits (timecodes) · vo · do_not

NEON 24s QUICK
rain atmos + dark pulse · whoosh @3s @12s · sub @18s · 0.4s pre-button air`;

function SoundPage() {
  const [q, setQ] = useState("");
  const [level, setLevel] = useState<SoundTopic["level"] | "all">("all");
  const [layerId, setLayerId] = useState(SOUND_LAYERS[0]?.id ?? "music");
  const [topicId, setTopicId] = useState(SOUND_TOPICS[0]?.id ?? "");
  const [recipeId, setRecipeId] = useState(SOUND_RECIPES[0]?.id ?? "neon-24");

  const filteredTopics = useMemo(() => {
    return SOUND_TOPICS.filter((t) => {
      if (level !== "all" && t.level !== level) return false;
      if (!q.trim()) return true;
      const hay = `${t.title} ${t.short} ${t.body} ${t.rule}`.toLowerCase();
      return hay.includes(q.trim().toLowerCase());
    });
  }, [q, level]);

  const layer = SOUND_LAYERS.find((l) => l.id === layerId) ?? SOUND_LAYERS[0];
  const topic =
    filteredTopics.find((t) => t.id === topicId) ?? filteredTopics[0] ?? null;
  const recipe =
    SOUND_RECIPES.find((r) => r.id === recipeId) ?? SOUND_RECIPES[0];

  return (
    <div className="space-y-8">
      <div>
        <Badge variant="teal">Post</Badge>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">
          Sound design
        </h1>
        <p className="mt-2 max-w-2xl text-muted leading-relaxed">
          Layers, mix hierarchy, and copy-ready briefs for 15–24s teasers —
          including silent-first still montages.
        </p>
      </div>

      {/* Mix stack visual */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Mix stack</CardTitle>
          <CardDescription>
            Higher layers win when they collide — duck below
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-1.5">
          {SOUND_LAYERS.map((l, i) => (
            <button
              key={l.id}
              type="button"
              onClick={() => setLayerId(l.id)}
              className={cn(
                "flex w-full items-center gap-3 rounded-lg border px-3 py-2.5 text-left text-sm transition-colors",
                layerId === l.id
                  ? "border-teal/40 bg-teal/10"
                  : "border-border bg-surface hover:border-border-strong",
              )}
            >
              <span className="font-mono text-[11px] text-teal">
                {String(i + 1).padStart(2, "0")}
              </span>
              <span className="font-medium text-fg">{l.name}</span>
              <span className="ml-auto hidden text-xs text-muted sm:inline">
                {l.short}
              </span>
            </button>
          ))}
        </CardContent>
      </Card>

      {layer && (
        <Card className="border-teal/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-xl">
              <AudioLines className="h-5 w-5 text-teal" />
              {layer.name}
            </CardTitle>
            <CardDescription>{layer.short}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm leading-relaxed text-muted">{layer.body}</p>
            <div className="flex flex-wrap gap-1.5">
              {layer.examples.map((ex) => (
                <Badge key={ex} variant="outline">
                  {ex}
                </Badge>
              ))}
            </div>
            <div className="grid gap-2 sm:grid-cols-2">
              <div className="rounded-lg border border-border bg-bg px-3 py-2.5">
                <p className="text-[11px] uppercase tracking-wide text-subtle">
                  When
                </p>
                <p className="mt-1 text-sm text-fg">{layer.when}</p>
              </div>
              <div className="rounded-lg border border-border bg-bg px-3 py-2.5">
                <p className="text-[11px] uppercase tracking-wide text-subtle">
                  Avoid
                </p>
                <p className="mt-1 text-sm text-fg">{layer.avoid}</p>
              </div>
            </div>
            <div className="rounded-lg border border-teal/30 bg-teal/5 px-3 py-3">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <p className="text-[11px] uppercase tracking-wide text-teal">
                    Brief line
                  </p>
                  <p className="mt-1 font-mono text-xs text-fg">{layer.brief}</p>
                </div>
                <CopyButton text={layer.brief} label="Copy" />
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
            placeholder="Search mix, diegetic, silent…"
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
          {SOUND_LEVELS.map((l) => (
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
            Sound brief recipes
          </h2>
          <p className="mt-1 text-sm text-muted">
            Paste after your edit spine / project pack.
          </p>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {SOUND_RECIPES.map((r) => (
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
                <CopyButton text={recipe.brief} label="Copy brief" />
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid gap-2 sm:grid-cols-2">
                {(
                  [
                    ["Bed", recipe.bed],
                    ["Hits", recipe.hits],
                    ["Silence", recipe.silence],
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
              <pre className="max-h-56 overflow-auto whitespace-pre-wrap rounded-lg border border-teal/30 bg-teal/5 p-3.5 font-mono text-[11px] leading-relaxed text-fg">
                {recipe.brief}
              </pre>
            </CardContent>
          </Card>
        )}
      </section>

      <Card className="border-teal/20">
        <CardHeader>
          <div className="flex items-start justify-between gap-2">
            <div>
              <CardTitle className="text-base">Cheat sheet</CardTitle>
              <CardDescription>Layers · hierarchy · brief pattern</CardDescription>
            </div>
            <CopyButton text={CHEAT} label="Copy" />
          </div>
        </CardHeader>
        <CardContent>
          <pre className="whitespace-pre-wrap rounded-lg border border-border bg-bg p-3.5 font-mono text-[11px] leading-relaxed text-muted">
            {CHEAT}
          </pre>
          <div className="mt-4 flex flex-wrap gap-2 text-sm">
            <Link to="/editing" className="text-teal hover:underline">
              Editing
            </Link>
            <Link to="/pack" className="text-teal hover:underline">
              Project pack
            </Link>
            <Link to="/scenarios" className="text-teal hover:underline">
              Scenarios
            </Link>
            <Link to="/budget" className="text-teal hover:underline">
              Budget
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
