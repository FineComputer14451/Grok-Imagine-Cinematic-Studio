import { createFileRoute, Link } from "@tanstack/react-router";
import { RectangleHorizontal, Search } from "lucide-react";
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
  ASPECT_FAMILIES,
  ASPECT_RATIOS,
  ASPECT_TOPICS,
  type AspectRatio,
} from "@/data/aspect";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/aspect")({
  component: AspectPage,
});

const CHEAT = `ASPECT RATIO CHEAT (Studio Academy)
Cinema: 2.39 scope · 1.85 flat · 1.37 Academy
Web/TV: 16:9 (1.78)
Photo: 3:2
Social: 1:1 · 4:5 · 9:16 vertical

Rules
1. Ratio = shape (width÷height), not resolution
2. Lock one primary ratio per sequence in DoP/Bible
3. Write ratio into format line of every hero packet
4. 9:16 needs its own composition — not a lazy center-crop of 2.39
5. Avoid baking letterbox bars into pixels
6. Multi-delivery: design for the strictest crop

Prompt crumbs
• “anamorphic 2.39 widescreen cinematic still”
• “1.85 theatrical flat, medium close-up”
• “9:16 vertical cinematic, mobile safe”
• “1:1 square centered portrait”`;

function AspectPage() {
  const [q, setQ] = useState("");
  const [family, setFamily] = useState<AspectRatio["family"] | "all">("all");
  const [openId, setOpenId] = useState(ASPECT_RATIOS[0]?.id ?? "239");
  const [topicId, setTopicId] = useState(ASPECT_TOPICS[0]?.id ?? "");

  const filtered = useMemo(() => {
    return ASPECT_RATIOS.filter((r) => {
      if (family !== "all" && r.family !== family) return false;
      if (!q.trim()) return true;
      const hay =
        `${r.label} ${r.ratio} ${r.names.join(" ")} ${r.feel} ${r.body} ${r.studioUse}`.toLowerCase();
      return hay.includes(q.trim().toLowerCase());
    });
  }, [q, family]);

  const active =
    filtered.find((r) => r.id === openId) ?? filtered[0] ?? null;
  const topic =
    ASPECT_TOPICS.find((t) => t.id === topicId) ?? ASPECT_TOPICS[0];

  const packetLine = active
    ? active.id === "239"
      ? "anamorphic 2.39:1 widescreen cinematic still"
      : active.id === "916"
        ? "9:16 vertical cinematic still, mobile safe headroom"
        : active.id === "11"
          ? "1:1 square frame, centered subject"
          : `${active.ratio} frame, cinematic still`
    : "";

  return (
    <div className="space-y-8">
      <div>
        <Badge variant="teal">Cinematography</Badge>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">
          Aspect ratios
        </h1>
        <p className="mt-2 max-w-2xl text-muted leading-relaxed">
          Frame shape changes composition, delivery, and how you write Imagine
          packets — from theatrical 2.39 to vertical 9:16.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Shape comparison</CardTitle>
          <CardDescription>
            Tap a shape to open its full guide
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap items-end justify-center gap-4 py-2">
            {["239", "185", "178", "11", "916"].map((id) => {
              const r = ASPECT_RATIOS.find((x) => x.id === id)!;
              const selected = active?.id === r.id;
              return (
                <button
                  key={r.id}
                  type="button"
                  onClick={() => {
                    setOpenId(r.id);
                    setFamily("all");
                  }}
                  className="flex flex-col items-center gap-2"
                >
                  <div
                    className={cn(
                      "rounded-sm border-2 bg-elevated/80 transition-colors",
                      selected
                        ? "border-teal bg-teal/10"
                        : "border-border hover:border-border-strong",
                    )}
                    style={{
                      width:
                        r.numeric >= 1
                          ? `${Math.min(140, 48 * r.numeric)}px`
                          : `${Math.max(28, 48 * r.numeric)}px`,
                      height:
                        r.numeric >= 1
                          ? "48px"
                          : `${Math.min(120, 48 / r.numeric)}px`,
                    }}
                  />
                  <span className="font-mono text-[10px] text-muted">
                    {r.label}
                  </span>
                </button>
              );
            })}
          </div>
        </CardContent>
      </Card>

      <section className="space-y-3">
        <h2 className="text-lg font-semibold tracking-tight">Concepts</h2>
        <div className="flex flex-wrap gap-1.5">
          {ASPECT_TOPICS.map((t) => (
            <button
              key={t.id}
              type="button"
              onClick={() => setTopicId(t.id)}
              className={cn(
                "h-9 rounded-md border px-3 text-xs font-medium",
                topicId === t.id
                  ? "border-teal/40 bg-teal/10 text-teal"
                  : "border-border bg-surface text-muted hover:text-fg",
              )}
            >
              {t.title}
            </button>
          ))}
        </div>
        {topic && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">{topic.title}</CardTitle>
              <CardDescription>{topic.short}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 text-sm leading-relaxed text-muted">
              <p>{topic.body}</p>
              <div className="grid gap-2 sm:grid-cols-2">
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
              </div>
            </CardContent>
          </Card>
        )}
      </section>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <label className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-subtle" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search 2.39, 9:16, Academy…"
            className="h-11 w-full rounded-lg border border-border bg-surface pl-10 pr-3 text-sm text-fg placeholder:text-subtle outline-none focus:border-border-strong focus:ring-2 focus:ring-teal/30"
          />
        </label>
        <div className="flex flex-wrap gap-1.5">
          <button
            type="button"
            onClick={() => setFamily("all")}
            className={cn(
              "h-9 rounded-md border px-3 text-xs font-medium",
              family === "all"
                ? "border-teal/40 bg-teal/10 text-teal"
                : "border-border bg-surface text-muted hover:text-fg",
            )}
          >
            All
          </button>
          {ASPECT_FAMILIES.map((f) => (
            <button
              key={f.id}
              type="button"
              onClick={() => setFamily(f.id)}
              className={cn(
                "h-9 rounded-md border px-3 text-xs font-medium",
                family === f.id
                  ? "border-teal/40 bg-teal/10 text-teal"
                  : "border-border bg-surface text-muted hover:text-fg",
              )}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      <p className="text-sm text-subtle">
        {filtered.length} of {ASPECT_RATIOS.length} ratios
      </p>

      {filtered.length === 0 ? (
        <p className="py-12 text-center text-sm text-muted">No ratios match.</p>
      ) : (
        <div className="grid gap-6 lg:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
          <ul className="max-h-[65dvh] space-y-1.5 overflow-y-auto pr-1">
            {filtered.map((r) => {
              const selected = active?.id === r.id;
              return (
                <li key={r.id}>
                  <button
                    type="button"
                    onClick={() => setOpenId(r.id)}
                    className={cn(
                      "w-full rounded-xl border px-3.5 py-3 text-left transition-colors",
                      selected
                        ? "border-teal/40 bg-teal/5"
                        : "border-border bg-surface hover:border-border-strong",
                    )}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <p className="font-medium text-fg">{r.label}</p>
                      <Badge variant="outline" className="capitalize">
                        {r.family}
                      </Badge>
                    </div>
                    <p className="mt-1 line-clamp-2 text-sm text-muted">
                      {r.feel}
                    </p>
                  </button>
                </li>
              );
            })}
          </ul>

          {active && (
            <Card className="h-fit border-teal/20 lg:sticky lg:top-20">
              <CardHeader>
                <div className="flex flex-wrap items-center gap-2">
                  <Badge variant="teal">{active.ratio}</Badge>
                  <Badge variant="outline" className="capitalize">
                    {active.family}
                  </Badge>
                </div>
                <CardTitle className="mt-2 flex items-center gap-2 text-xl">
                  <RectangleHorizontal className="h-5 w-5 text-teal" />
                  {active.label}
                </CardTitle>
                <CardDescription>{active.feel}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-center rounded-xl border border-border bg-bg p-6">
                  <div
                    className="w-full max-w-[280px] rounded-sm border-2 border-teal/50 bg-teal/5"
                    style={{ aspectRatio: `${active.numeric} / 1` }}
                  />
                </div>

                <p className="text-sm leading-relaxed text-muted">
                  {active.body}
                </p>

                <div className="flex flex-wrap gap-1.5">
                  {active.names.map((n) => (
                    <Badge key={n} variant="default">
                      {n}
                    </Badge>
                  ))}
                </div>

                <div className="grid gap-2 sm:grid-cols-2">
                  {(
                    [
                      ["Compose", active.compose],
                      ["Lighting", active.lighting],
                      ["Imagine", active.imagine],
                      ["Avoid", active.avoid],
                      ["Studio use", active.studioUse],
                    ] as const
                  ).map(([label, value]) => (
                    <div
                      key={label}
                      className="rounded-lg border border-border bg-bg px-3 py-2.5"
                    >
                      <p className="text-[11px] uppercase tracking-wide text-subtle">
                        {label}
                      </p>
                      <p className="mt-1 text-sm leading-snug text-fg">
                        {value}
                      </p>
                    </div>
                  ))}
                </div>

                <div className="rounded-lg border border-teal/30 bg-teal/5 px-3 py-3">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <p className="text-[11px] uppercase tracking-wide text-teal">
                        Packet crumb
                      </p>
                      <p className="mt-1 font-mono text-xs text-fg">
                        {packetLine}
                      </p>
                    </div>
                    <CopyButton text={packetLine} label="Copy" />
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      <Card className="border-teal/20">
        <CardHeader>
          <div className="flex items-start justify-between gap-2">
            <div>
              <CardTitle className="text-base">Cheat sheet</CardTitle>
              <CardDescription>
                Copy into notes or DoP format line
              </CardDescription>
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
              DoP card
            </Link>
            <Link to="/composition" className="text-teal hover:underline">
              Composition
            </Link>
            <Link to="/lighting" className="text-teal hover:underline">
              Lighting
            </Link>
            <Link to="/lab" className="text-teal hover:underline">
              Prompt lab
            </Link>
            <Link to="/bible" className="text-teal hover:underline">
              Mini Bible
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
