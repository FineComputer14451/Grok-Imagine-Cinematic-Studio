import { createFileRoute, Link } from "@tanstack/react-router";
import { Camera, Search } from "lucide-react";
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
  FOCAL_BANDS,
  LENS_LEVELS,
  LENS_RECIPES,
  LENS_TOPICS,
  type LensTopic,
} from "@/data/lenses";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/lenses")({
  component: LensesPage,
});

const CHEAT = `LENS CHEAT (Studio Academy)
Bands (FF-equivalent)
• 14–20 ultra wide — scale / distort
• 24–28 wide — place + person
• 35 story default
• 50 normal / identity
• 85 portrait compression
• 100–135 tele isolation

Rules
1. Name mm in DoP + hero packets
2. Identity CUs: 50–85 — don’t only crop wides
3. 3–4 focal lengths max per mini-project
4. Pair anamorphic wording with 2.39 (not 9:16)
5. DOF is story: shallow isolate · deep geography
6. Perspective ≠ digital zoom crop

Prompt pattern
[shot size] · [mm] · [DOF] · [aspect/format]
e.g. medium close-up, 50mm, shallow DOF, 2.39 anamorphic feel`;

function LensesPage() {
  const [q, setQ] = useState("");
  const [level, setLevel] = useState<LensTopic["level"] | "all">("all");
  const [bandId, setBandId] = useState(FOCAL_BANDS[2]?.id ?? "35");
  const [topicId, setTopicId] = useState(LENS_TOPICS[0]?.id ?? "");
  const [recipeId, setRecipeId] = useState(LENS_RECIPES[0]?.id ?? "");

  const filteredTopics = useMemo(() => {
    return LENS_TOPICS.filter((t) => {
      if (level !== "all" && t.level !== level) return false;
      if (!q.trim()) return true;
      const hay = `${t.title} ${t.short} ${t.body} ${t.rule}`.toLowerCase();
      return hay.includes(q.trim().toLowerCase());
    });
  }, [q, level]);

  const band = FOCAL_BANDS.find((b) => b.id === bandId) ?? FOCAL_BANDS[0];
  const topic =
    filteredTopics.find((t) => t.id === topicId) ?? filteredTopics[0] ?? null;
  const recipe =
    LENS_RECIPES.find((r) => r.id === recipeId) ?? LENS_RECIPES[0];

  return (
    <div className="space-y-8">
      <div>
        <Badge variant="teal">Cinematography</Badge>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">
          Lenses & focal length
        </h1>
        <p className="mt-2 max-w-2xl text-muted leading-relaxed">
          From 24mm geography to 85mm portraits — how mm, DOF, and anamorphic
          feel change the image, and how to write them into Studio packets.
        </p>
      </div>

      {/* FOV visual strip */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Focal length ladder</CardTitle>
          <CardDescription>
            Wider mm → more world · longer mm → more isolation
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap items-end justify-center gap-3">
            {FOCAL_BANDS.map((b, i) => {
              const selected = bandId === b.id;
              const w = 36 + i * 10;
              return (
                <button
                  key={b.id}
                  type="button"
                  onClick={() => setBandId(b.id)}
                  className="flex flex-col items-center gap-1.5"
                >
                  <div
                    className={cn(
                      "rounded-sm border-2 transition-colors",
                      selected
                        ? "border-teal bg-teal/15"
                        : "border-border bg-elevated hover:border-border-strong",
                    )}
                    style={{ width: w, height: 44 }}
                  />
                  <span className="font-mono text-[10px] text-muted">
                    {b.mm.split("–")[0].replace("mm", "")}
                  </span>
                </button>
              );
            })}
          </div>
          <p className="mt-3 text-center text-xs text-subtle">
            Bars get wider as focal length increases (tighter field of view)
          </p>
        </CardContent>
      </Card>

      {/* Band detail */}
      <div className="flex flex-wrap gap-1.5">
        {FOCAL_BANDS.map((b) => (
          <button
            key={b.id}
            type="button"
            onClick={() => setBandId(b.id)}
            className={cn(
              "h-9 rounded-md border px-3 text-xs font-medium",
              bandId === b.id
                ? "border-teal/40 bg-teal/10 text-teal"
                : "border-border bg-surface text-muted hover:text-fg",
            )}
          >
            {b.mm}
          </button>
        ))}
      </div>

      {band && (
        <Card className="border-teal/20">
          <CardHeader>
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant="teal">{band.mm}</Badge>
              <Badge variant="outline">{band.label}</Badge>
            </div>
            <CardTitle className="mt-2 flex items-center gap-2 text-xl">
              <Camera className="h-5 w-5 text-teal" />
              {band.label}
            </CardTitle>
            <CardDescription>{band.feel}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm leading-relaxed text-muted">{band.body}</p>
            <div className="grid gap-2 sm:grid-cols-2">
              {(
                [
                  ["Angle", band.angle],
                  ["Face", band.face],
                  ["Body / space", band.bodySpace],
                  ["Distortion", band.distortion],
                  ["Use", band.use],
                  ["Avoid", band.avoid],
                  ["Pairs with", band.pairsWith],
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
                  <p className="mt-1 font-mono text-xs text-fg">{band.packet}</p>
                </div>
                <CopyButton text={band.packet} label="Copy" />
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Topics */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <label className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-subtle" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search DOF, anamorphic, perspective…"
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
          {LENS_LEVELS.map((l) => (
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

      {/* Recipes */}
      <section className="space-y-4">
        <div>
          <h2 className="text-lg font-semibold tracking-tight">Lens recipes</h2>
          <p className="mt-1 text-sm text-muted">
            Ready sets for Academy presets — copy into DoP or Prompt lab.
          </p>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {LENS_RECIPES.map((r) => (
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
                  ["Focal plan", recipe.focal],
                  ["DOF feel", recipe.apertureFeel],
                  ["Format", recipe.format],
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
              <CardDescription>mm + DOF + format pattern</CardDescription>
            </div>
            <CopyButton text={CHEAT} label="Copy" />
          </div>
        </CardHeader>
        <CardContent>
          <pre className="whitespace-pre-wrap rounded-lg border border-border bg-bg p-3.5 font-mono text-[11px] leading-relaxed text-muted">
            {CHEAT}
          </pre>
          <div className="mt-4 flex flex-wrap gap-2 text-sm">
            <Link to="/aspect" className="text-teal hover:underline">
              Aspect ratios
            </Link>
            <Link to="/composition" className="text-teal hover:underline">
              Framing
            </Link>
            <Link to="/lighting" className="text-teal hover:underline">
              Lighting
            </Link>
            <Link to="/dop" className="text-teal hover:underline">
              DoP card
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
