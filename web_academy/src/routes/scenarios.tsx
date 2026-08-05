import { createFileRoute, Link } from "@tanstack/react-router";
import {
  ArrowRight,
  Clapperboard,
  Fingerprint,
  ListOrdered,
  Search,
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
import { SCENARIOS, type Scenario } from "@/data/scenarios";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/scenarios")({
  component: ScenariosPage,
});

const TIERS: { id: 0 | 1 | 2 | 3; label: string }[] = [
  { id: 0, label: "All tiers" },
  { id: 1, label: "Tier 1" },
  { id: 2, label: "Tier 2" },
  { id: 3, label: "Tier 3" },
];

function ScenariosPage() {
  const [q, setQ] = useState("");
  const [tier, setTier] = useState<0 | 1 | 2 | 3>(0);
  const [openId, setOpenId] = useState(SCENARIOS[0]?.id ?? "");

  const filtered = useMemo(() => {
    return SCENARIOS.filter((s) => {
      if (tier !== 0 && s.tier !== tier) return false;
      if (!q.trim()) return true;
      const hay =
        `${s.title} ${s.tagline} ${s.genre} ${s.agents.join(" ")} ${s.deliverable}`.toLowerCase();
      return hay.includes(q.trim().toLowerCase());
    });
  }, [q, tier]);

  const active =
    filtered.find((s) => s.id === openId) ?? filtered[0] ?? null;

  return (
    <div className="space-y-8">
      <div>
        <Badge variant="teal">Playbooks</Badge>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">
          Scenario library
        </h1>
        <p className="mt-2 max-w-2xl text-muted leading-relaxed">
          End-to-end starters for learners — from first still to mini extend
          chain. Each scenario bundles steps, budget hints, and a copyable
          activation block.
        </p>
      </div>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <label className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-subtle" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search scenarios, genres, agents…"
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

      <p className="text-sm text-subtle">
        Showing {filtered.length} of {SCENARIOS.length} scenarios
      </p>

      {filtered.length === 0 ? (
        <p className="py-12 text-center text-sm text-muted">
          No scenarios match that filter.
        </p>
      ) : (
        <div className="grid gap-6 lg:grid-cols-[minmax(0,0.95fr)_minmax(0,1.05fr)]">
          <div className="space-y-2">
            {filtered.map((s) => {
              const selected = active?.id === s.id;
              return (
                <button
                  key={s.id}
                  type="button"
                  onClick={() => setOpenId(s.id)}
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
                        {s.title}
                      </p>
                      <p className="mt-1 line-clamp-2 text-sm text-muted">
                        {s.tagline}
                      </p>
                    </div>
                    <Badge variant="outline" className="shrink-0">
                      T{s.tier}
                    </Badge>
                  </div>
                  <div className="mt-2 flex flex-wrap gap-2 text-[11px] text-subtle">
                    <span className="font-mono">{s.minutes}</span>
                    <span>·</span>
                    <span>{s.genre}</span>
                  </div>
                </button>
              );
            })}
          </div>

          {active && <ScenarioDetail scenario={active} />}
        </div>
      )}
    </div>
  );
}

function ScenarioDetail({ scenario }: { scenario: Scenario }) {
  return (
    <Card className="h-fit lg:sticky lg:top-20">
      <CardHeader>
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="teal">Tier {scenario.tier}</Badge>
          <Badge variant="outline">{scenario.minutes}</Badge>
        </div>
        <CardTitle className="mt-2 text-xl leading-snug">
          {scenario.title}
        </CardTitle>
        <CardDescription>{scenario.tagline}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-5">
        <div className="grid gap-3 sm:grid-cols-2">
          <Meta label="Genre" value={scenario.genre} />
          <Meta label="Deliverable" value={scenario.deliverable} />
          <Meta label="Budget hint" value={scenario.budgetHint} />
          <Meta
            label="Agents"
            value={`${scenario.agents.length} specialists`}
          />
        </div>

        <div>
          <p className="mb-2 flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-subtle">
            <ListOrdered className="h-3.5 w-3.5 text-teal" />
            Steps
          </p>
          <ol className="space-y-2">
            {scenario.steps.map((step, i) => (
              <li
                key={step}
                className="flex gap-3 rounded-lg border border-border bg-bg px-3 py-2.5 text-sm text-muted"
              >
                <span className="font-mono text-[11px] text-teal shrink-0">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <span className="leading-relaxed">{step}</span>
              </li>
            ))}
          </ol>
        </div>

        <div>
          <p className="mb-2 text-xs font-medium uppercase tracking-wide text-subtle">
            Cast of agents
          </p>
          <div className="flex flex-wrap gap-1.5">
            {scenario.agents.map((a) => (
              <Badge key={a} variant="default">
                {a}
              </Badge>
            ))}
          </div>
        </div>

        <div>
          <div className="mb-2 flex items-center justify-between gap-2">
            <p className="flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-subtle">
              <Clapperboard className="h-3.5 w-3.5 text-teal" />
              Activation
            </p>
            <CopyButton text={scenario.activation} label="Copy" />
          </div>
          <pre className="max-h-56 overflow-auto whitespace-pre-wrap rounded-lg border border-border bg-bg p-3.5 font-mono text-[11px] leading-relaxed text-muted">
            {scenario.activation}
          </pre>
        </div>

        <ul className="space-y-1.5 text-sm text-muted">
          {scenario.tips.map((t) => (
            <li key={t} className="flex gap-2">
              <span className="text-teal">·</span>
              <span>{t}</span>
            </li>
          ))}
        </ul>

        <div className="flex flex-wrap gap-2 border-t border-border pt-4">
          {scenario.dnaPreset && (
            <Link
              to="/dna"
              className="inline-flex h-9 items-center gap-1.5 rounded-md border border-border bg-elevated px-3 text-xs text-muted hover:text-fg"
            >
              <Fingerprint className="h-3.5 w-3.5 text-teal" />
              Open DNA builder
            </Link>
          )}
          <Link
            to="/lab"
            className="inline-flex h-9 items-center gap-1.5 rounded-md border border-border bg-elevated px-3 text-xs text-muted hover:text-fg"
          >
            Prompt lab
            <ArrowRight className="h-3 w-3" />
          </Link>
          <Link
            to="/budget"
            className="inline-flex h-9 items-center gap-1.5 rounded-md border border-border bg-elevated px-3 text-xs text-muted hover:text-fg"
          >
            Budget calculator
          </Link>
          <Link
            to="/workflows"
            className="inline-flex h-9 items-center gap-1.5 rounded-md border border-border bg-elevated px-3 text-xs text-muted hover:text-fg"
          >
            Workflows
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}

function Meta({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-border bg-bg px-3 py-2.5">
      <p className="text-[11px] uppercase tracking-wide text-subtle">{label}</p>
      <p className="mt-1 text-sm text-fg leading-snug">{value}</p>
    </div>
  );
}
