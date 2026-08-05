import { createFileRoute, Link } from "@tanstack/react-router";
import {
  ArrowRight,
  Cpu,
  GitBranch,
  Search,
  ShieldCheck,
} from "lucide-react";
import { useMemo, useState } from "react";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  ALGORITHMS,
  PIPELINE_ORDER,
  STAGES,
  type Algorithm,
} from "@/data/consistency";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/consistency")({
  component: ConsistencyPage,
});

const STAGE_TONE: Record<Algorithm["stage"], string> = {
  pre: "border-teal/40 bg-teal/10 text-teal",
  gen: "border-amber/40 bg-amber/10 text-amber",
  extend: "border-success/40 bg-success/10 text-success",
  qa: "border-accent/40 bg-accent/10 text-accent",
};

function ConsistencyPage() {
  const [q, setQ] = useState("");
  const [stage, setStage] = useState<Algorithm["stage"] | "all">("all");
  const [openId, setOpenId] = useState<string>(PIPELINE_ORDER[0]);

  const ordered = useMemo(() => {
    const map = new Map(ALGORITHMS.map((a) => [a.id, a]));
    return PIPELINE_ORDER.map((id) => map.get(id)!).filter(Boolean);
  }, []);

  const filtered = useMemo(() => {
    return ordered.filter((a) => {
      if (stage !== "all" && a.stage !== stage) return false;
      if (!q.trim()) return true;
      const hay =
        `${a.name} ${a.short} ${a.steps.join(" ")} ${a.studioAgents.join(" ")}`.toLowerCase();
      return hay.includes(q.trim().toLowerCase());
    });
  }, [ordered, q, stage]);

  const active =
    filtered.find((a) => a.id === openId) ?? filtered[0] ?? null;

  return (
    <div className="space-y-8">
      <div>
        <Badge variant="teal">Algorithms</Badge>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">
          Video consistency algorithms
        </h1>
        <p className="mt-2 max-w-2xl text-muted leading-relaxed">
          How Studio Academy (and Cinematic Studio) keep faces, wardrobe, light,
          and motion stable across stills and multi-clip video — from DNA inject
          to chain QA.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <GitBranch className="h-4 w-4 text-teal" />
            Consistency pipeline
          </CardTitle>
          <CardDescription>
            Order of operations — skip a stage and drift compounds
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-2 lg:flex-row lg:flex-wrap lg:items-stretch">
            {STAGES.map((s, i) => (
              <div
                key={s.id}
                className="flex flex-1 items-stretch gap-2 min-w-[140px]"
              >
                <button
                  type="button"
                  onClick={() => {
                    setStage(s.id);
                    const first = ordered.find((a) => a.stage === s.id);
                    if (first) setOpenId(first.id);
                  }}
                  className={cn(
                    "flex-1 rounded-xl border px-3 py-3 text-left transition-colors",
                    stage === s.id
                      ? "border-teal/40 bg-teal/5"
                      : "border-border bg-surface hover:border-border-strong",
                  )}
                >
                  <p className="font-mono text-[11px] text-teal">
                    {String(i + 1).padStart(2, "0")}
                  </p>
                  <p className="mt-1 text-sm font-medium text-fg">{s.label}</p>
                  <p className="mt-1 text-xs text-muted leading-snug">
                    {s.blurb}
                  </p>
                </button>
                {i < STAGES.length - 1 && (
                  <div
                    className="hidden lg:flex items-center text-subtle"
                    aria-hidden
                  >
                    <ArrowRight className="h-4 w-4" />
                  </div>
                )}
              </div>
            ))}
          </div>
          <button
            type="button"
            onClick={() => setStage("all")}
            className="mt-3 text-xs text-teal hover:underline"
          >
            Show all stages
          </button>
        </CardContent>
      </Card>

      <Card className="border-teal/20 bg-teal/5">
        <CardContent className="flex gap-3 pt-5 text-sm text-muted">
          <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-teal" />
          <p>
            These are{" "}
            <strong className="text-fg">orchestration algorithms</strong>{" "}
            (contracts + gates), not proprietary model weights. They sit on top
            of Grok Imagine generation and decide{" "}
            <em>what</em> is allowed to generate next.
          </p>
        </CardContent>
      </Card>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <label className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-subtle" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search DNA, recap, QA, drift…"
            className="h-11 w-full rounded-lg border border-border bg-surface pl-10 pr-3 text-sm text-fg placeholder:text-subtle outline-none focus:border-border-strong focus:ring-2 focus:ring-teal/30"
          />
        </label>
      </div>

      <p className="text-sm text-subtle">
        {filtered.length} of {ALGORITHMS.length} algorithms
      </p>

      {filtered.length === 0 ? (
        <p className="py-12 text-center text-sm text-muted">
          No algorithms match that filter.
        </p>
      ) : (
        <div className="grid gap-6 lg:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
          <ul className="space-y-1.5 max-h-[70dvh] overflow-y-auto pr-1">
            {filtered.map((a, idx) => {
              const selected = active?.id === a.id;
              return (
                <li key={a.id}>
                  <button
                    type="button"
                    onClick={() => setOpenId(a.id)}
                    className={cn(
                      "w-full rounded-xl border px-3.5 py-3 text-left transition-colors",
                      selected
                        ? "border-teal/40 bg-teal/5"
                        : "border-border bg-surface hover:border-border-strong",
                    )}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0">
                        <p className="font-medium text-fg leading-snug">
                          <span className="mr-2 font-mono text-[11px] text-teal">
                            {String(idx + 1).padStart(2, "0")}
                          </span>
                          {a.name}
                        </p>
                        <p className="mt-1 line-clamp-2 text-sm text-muted">
                          {a.short}
                        </p>
                      </div>
                      <span
                        className={cn(
                          "shrink-0 rounded border px-1.5 py-0.5 text-[10px] font-semibold uppercase",
                          STAGE_TONE[a.stage],
                        )}
                      >
                        {a.stage}
                      </span>
                    </div>
                  </button>
                </li>
              );
            })}
          </ul>

          {active && <AlgoDetail algo={active} />}
        </div>
      )}
    </div>
  );
}

function AlgoDetail({ algo }: { algo: Algorithm }) {
  return (
    <Card className="h-fit border-teal/20 lg:sticky lg:top-20">
      <CardHeader>
        <div className="flex flex-wrap items-center gap-2">
          <span
            className={cn(
              "rounded border px-2 py-0.5 text-[10px] font-semibold uppercase",
              STAGE_TONE[algo.stage],
            )}
          >
            {algo.stage}
          </span>
          <Badge variant="outline">{algo.weight}</Badge>
        </div>
        <CardTitle className="mt-2 flex items-center gap-2 text-xl">
          <Cpu className="h-5 w-5 shrink-0 text-teal" />
          {algo.name}
        </CardTitle>
        <CardDescription>{algo.short}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-5">
        <div className="grid gap-3 sm:grid-cols-2">
          <div className="rounded-lg border border-border bg-bg p-3">
            <p className="text-[11px] uppercase tracking-wide text-subtle">
              Inputs
            </p>
            <ul className="mt-2 space-y-1 text-sm text-muted">
              {algo.inputs.map((x) => (
                <li key={x} className="font-mono text-[11px]">
                  {x}
                </li>
              ))}
            </ul>
          </div>
          <div className="rounded-lg border border-border bg-bg p-3">
            <p className="text-[11px] uppercase tracking-wide text-subtle">
              Outputs
            </p>
            <ul className="mt-2 space-y-1 text-sm text-muted">
              {algo.outputs.map((x) => (
                <li key={x} className="font-mono text-[11px]">
                  {x}
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div>
          <p className="mb-2 text-xs font-medium uppercase tracking-wide text-subtle">
            Steps
          </p>
          <ol className="space-y-2">
            {algo.steps.map((s, i) => (
              <li
                key={s}
                className="flex gap-3 rounded-lg border border-border bg-bg px-3 py-2.5 text-sm text-muted"
              >
                <span className="shrink-0 font-mono text-[11px] text-teal">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <span className="leading-relaxed">{s}</span>
              </li>
            ))}
          </ol>
        </div>

        <div>
          <p className="mb-2 text-xs font-medium uppercase tracking-wide text-subtle">
            Fails when
          </p>
          <ul className="space-y-1.5 text-sm text-muted">
            {algo.failsWhen.map((f) => (
              <li key={f} className="flex gap-2">
                <span className="text-danger">×</span>
                <span>{f}</span>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <p className="mb-2 text-xs font-medium uppercase tracking-wide text-subtle">
            Studio agents
          </p>
          <div className="flex flex-wrap gap-1.5">
            {algo.studioAgents.map((a) => (
              <Badge key={a} variant="default">
                {a}
              </Badge>
            ))}
          </div>
        </div>

        <div className="flex flex-wrap gap-2 border-t border-border pt-4">
          {algo.relatedTools.map((t) => (
            <Link
              key={t.to + t.label}
              to={t.to}
              className="inline-flex h-9 items-center gap-1.5 rounded-md border border-border bg-elevated px-3 text-xs text-muted hover:text-fg"
            >
              {t.label}
              <ArrowRight className="h-3 w-3" />
            </Link>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
