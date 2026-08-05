import { createFileRoute } from "@tanstack/react-router";
import {
  ArrowRight,
  GitMerge,
  Search,
  Workflow as WorkflowIcon,
} from "lucide-react";
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
import { WORKFLOWS, WORKFLOW_TAGS, type Workflow } from "@/data/workflows";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/workflows")({
  component: WorkflowsPage,
});

const TIERS: { id: 0 | 1 | 2 | 3; label: string }[] = [
  { id: 0, label: "All tiers" },
  { id: 1, label: "Tier 1" },
  { id: 2, label: "Tier 2" },
  { id: 3, label: "Tier 3" },
];

function WorkflowsPage() {
  const [q, setQ] = useState("");
  const [tier, setTier] = useState<0 | 1 | 2 | 3>(0);
  const [tag, setTag] = useState<string | null>(null);
  const [openId, setOpenId] = useState<string | null>(WORKFLOWS[0]?.id ?? null);

  const filtered = useMemo(() => {
    return WORKFLOWS.filter((w) => {
      if (tier !== 0 && w.tier !== tier) return false;
      if (tag && !w.tags.includes(tag)) return false;
      if (!q.trim()) return true;
      const hay =
        `${w.title} ${w.summary} ${w.when} ${w.agents.join(" ")} ${w.tags.join(" ")}`.toLowerCase();
      return hay.includes(q.trim().toLowerCase());
    });
  }, [q, tier, tag]);

  const active =
    filtered.find((w) => w.id === openId) ?? filtered[0] ?? null;

  return (
    <div className="space-y-8">
      <div>
        <Badge variant="teal">Discover</Badge>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">
          Agent integration workflows
        </h1>
        <p className="mt-2 max-w-2xl text-muted">
          Ready-made multi-agent chains. See who talks to whom, what each hands
          off, and copy a paste-ready activation block.
        </p>
      </div>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <label className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-subtle" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search workflows, agents, tags…"
            className="h-11 w-full rounded-lg border border-border bg-surface pl-10 pr-3 text-sm text-fg placeholder:text-subtle outline-none focus:border-border-strong focus:ring-2 focus:ring-teal/30"
          />
        </label>
        <div className="flex flex-wrap gap-1.5">
          {TIERS.map((t) => (
            <button
              key={t.id}
              type="button"
              onClick={() => setTier(t.id)}
              className={cn(
                "h-9 rounded-md border px-3 text-xs font-medium transition-colors",
                tier === t.id
                  ? "border-teal/40 bg-teal/10 text-teal"
                  : "border-border bg-surface text-muted hover:text-fg",
              )}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      <div className="flex flex-wrap gap-1.5">
        <button
          type="button"
          onClick={() => setTag(null)}
          className={cn(
            "h-7 rounded-md border px-2.5 text-[11px] font-medium",
            !tag
              ? "border-teal/40 bg-teal/10 text-teal"
              : "border-border bg-elevated/50 text-muted hover:text-fg",
          )}
        >
          All tags
        </button>
        {WORKFLOW_TAGS.map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setTag(tag === t ? null : t)}
            className={cn(
              "h-7 rounded-md border px-2.5 text-[11px] font-medium",
              tag === t
                ? "border-teal/40 bg-teal/10 text-teal"
                : "border-border bg-elevated/50 text-muted hover:text-fg",
            )}
          >
            {t}
          </button>
        ))}
      </div>

      <p className="text-sm text-subtle">
        Showing {filtered.length} of {WORKFLOWS.length} workflows
      </p>

      {filtered.length === 0 ? (
        <p className="py-12 text-center text-sm text-muted">
          No workflows match that filter.
        </p>
      ) : (
        <div className="grid gap-6 lg:grid-cols-[minmax(0,0.95fr)_minmax(0,1.05fr)]">
          <div className="space-y-2">
            {filtered.map((w) => {
              const selected = active?.id === w.id;
              return (
                <button
                  key={w.id}
                  type="button"
                  onClick={() => setOpenId(w.id)}
                  className={cn(
                    "w-full rounded-xl border px-4 py-3.5 text-left transition-colors",
                    selected
                      ? "border-teal/40 bg-teal/5"
                      : "border-border bg-surface hover:border-border-strong",
                  )}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <p className="font-medium text-fg leading-snug">
                        {w.title}
                      </p>
                      <p className="mt-1 line-clamp-2 text-sm text-muted">
                        {w.summary}
                      </p>
                    </div>
                    <Badge variant="outline" className="shrink-0">
                      T{w.tier}
                    </Badge>
                  </div>
                  <div className="mt-2 flex flex-wrap items-center gap-2 text-[11px] text-subtle">
                    <span className="font-mono">{w.minutes}</span>
                    <span>·</span>
                    <span>{w.agents.length} agents</span>
                  </div>
                </button>
              );
            })}
          </div>

          {active && <WorkflowDetail workflow={active} />}
        </div>
      )}
    </div>
  );
}

function WorkflowDetail({ workflow }: { workflow: Workflow }) {
  return (
    <Card className="h-fit lg:sticky lg:top-20">
      <CardHeader>
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="teal">Tier {workflow.tier}</Badge>
          <Badge variant="outline">{workflow.minutes}</Badge>
        </div>
        <CardTitle className="mt-2 text-xl leading-snug">
          {workflow.title}
        </CardTitle>
        <CardDescription>{workflow.summary}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-subtle">
            When to use
          </p>
          <p className="mt-1.5 text-sm text-muted leading-relaxed">
            {workflow.when}
          </p>
        </div>

        <div>
          <p className="mb-3 flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-subtle">
            <GitMerge className="h-3.5 w-3.5 text-teal" />
            Integration chain
          </p>
          <ol className="space-y-0">
            {workflow.steps.map((step, i) => (
              <li key={`${step.agent}-${i}`} className="relative">
                <div className="rounded-lg border border-border bg-bg p-3.5">
                  <div className="flex items-start gap-3">
                    <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md border border-border bg-elevated font-mono text-[11px] text-teal">
                      {String(i + 1).padStart(2, "0")}
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-fg">
                        {step.agent}
                      </p>
                      <p className="mt-1 text-sm text-muted leading-relaxed">
                        {step.action}
                      </p>
                      <p className="mt-2 flex items-start gap-1.5 text-xs text-teal">
                        <ArrowRight className="mt-0.5 h-3 w-3 shrink-0" />
                        <span>{step.handsOff}</span>
                      </p>
                    </div>
                  </div>
                </div>
                {i < workflow.steps.length - 1 && (
                  <div
                    className="flex justify-center py-1.5 text-subtle"
                    aria-hidden
                  >
                    ↓
                  </div>
                )}
              </li>
            ))}
          </ol>
        </div>

        <div>
          <div className="mb-2 flex items-center justify-between gap-2">
            <p className="flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-subtle">
              <WorkflowIcon className="h-3.5 w-3.5 text-teal" />
              Activation block
            </p>
            <CopyButton text={workflow.activation} label="Copy workflow" />
          </div>
          <pre className="overflow-x-auto rounded-lg border border-border bg-bg p-3.5 font-mono text-[11px] leading-relaxed text-muted whitespace-pre-wrap">
            {workflow.activation}
          </pre>
        </div>

        <div className="flex flex-wrap gap-1.5">
          {workflow.tags.map((t) => (
            <Badge key={t} variant="default">
              {t}
            </Badge>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
