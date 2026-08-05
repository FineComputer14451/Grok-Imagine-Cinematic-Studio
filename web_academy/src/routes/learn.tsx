import { createFileRoute } from "@tanstack/react-router";
import {
  CheckCircle2,
  ChevronRight,
  Circle,
  Clock,
  RotateCcw,
} from "lucide-react";
import { useState } from "react";
import { CopyButton } from "@/components/copy-button";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { TIERS } from "@/data/studio";
import { useProgress } from "@/lib/progress";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/learn")({
  component: LearnPage,
});

function LearnPage() {
  const { completedTiers, completeTier, reset } = useProgress();
  const [active, setActive] = useState(1);
  const tier = TIERS.find((t) => t.id === active) ?? TIERS[0];
  const done = completedTiers.includes(tier.id);

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">
            Learn path
          </h1>
          <p className="mt-2 max-w-2xl text-muted">
            Three progressive tiers. Copy the prompt into Grok, run the
            exercise, then mark the tier complete.
          </p>
        </div>
        <Button type="button" variant="ghost" size="sm" onClick={() => reset()}>
          <RotateCcw className="h-3.5 w-3.5" />
          Reset progress
        </Button>
      </div>

      <div className="flex flex-col gap-2 sm:flex-row">
        {TIERS.map((t) => {
          const isActive = t.id === active;
          const isDone = completedTiers.includes(t.id);
          return (
            <button
              key={t.id}
              type="button"
              onClick={() => setActive(t.id)}
              className={cn(
                "flex flex-1 items-center gap-3 rounded-xl border px-4 py-3 text-left transition-colors",
                isActive
                  ? "border-teal/40 bg-teal/5"
                  : "border-border bg-surface hover:border-border-strong",
              )}
            >
              {isDone ? (
                <CheckCircle2 className="h-5 w-5 shrink-0 text-success" />
              ) : (
                <Circle
                  className={cn(
                    "h-5 w-5 shrink-0",
                    isActive ? "text-teal" : "text-subtle",
                  )}
                />
              )}
              <div className="min-w-0">
                <p className="text-sm font-medium">
                  Tier {t.id}: {t.title}
                </p>
                <p className="truncate text-xs text-subtle">{t.minutes}</p>
              </div>
              <ChevronRight
                className={cn(
                  "ml-auto h-4 w-4 shrink-0",
                  isActive ? "text-teal" : "text-subtle",
                )}
              />
            </button>
          );
        })}
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_0.95fr]">
        <Card>
          <CardHeader>
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant="teal">Tier {tier.id}</Badge>
              <Badge variant="outline" className="gap-1">
                <Clock className="h-3 w-3" />
                {tier.minutes}
              </Badge>
              {done && <Badge variant="accent">Completed</Badge>}
            </div>
            <CardTitle className="mt-2 text-xl">{tier.title}</CardTitle>
            <CardDescription className="text-base">
              {tier.subtitle}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-subtle">
                Outcome
              </p>
              <p className="mt-1 text-sm text-muted leading-relaxed">
                {tier.outcome}
              </p>
            </div>

            <ol className="space-y-4">
              {tier.steps.map((step, i) => (
                <li key={step.title} className="flex gap-3">
                  <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-border bg-elevated font-mono text-xs text-muted">
                    {i + 1}
                  </span>
                  <div>
                    <p className="text-sm font-medium">{step.title}</p>
                    <p className="mt-0.5 text-sm text-muted leading-relaxed">
                      {step.detail}
                    </p>
                  </div>
                </li>
              ))}
            </ol>

            <div>
              <p className="mb-2 text-xs font-medium uppercase tracking-wide text-subtle">
                Agents involved
              </p>
              <div className="flex flex-wrap gap-1.5">
                {tier.agents.map((a) => (
                  <Badge key={a} variant="outline">
                    {a}
                  </Badge>
                ))}
              </div>
            </div>

            {!done ? (
              <Button
                type="button"
                variant="teal"
                className="w-full sm:w-auto"
                onClick={() => {
                  completeTier(tier.id);
                  if (tier.id < 3) setActive((tier.id + 1) as 1 | 2 | 3);
                }}
              >
                Mark tier complete
              </Button>
            ) : (
              <p className="text-sm text-success">
                Tier complete.{" "}
                {tier.id < 3
                  ? "Move to the next tier when ready."
                  : "You finished the full path."}
              </p>
            )}
          </CardContent>
        </Card>

        <Card className="bg-elevated/30">
          <CardHeader className="flex-row items-start justify-between gap-3 space-y-0">
            <div>
              <CardTitle className="text-base">Copy into Grok</CardTitle>
              <CardDescription className="mt-1">
                Paste this activation block in a fresh chat, then generate.
              </CardDescription>
            </div>
            <CopyButton text={tier.prompt} />
          </CardHeader>
          <CardContent>
            <pre className="max-h-[28rem] overflow-auto rounded-lg border border-border bg-bg p-4 font-mono text-xs leading-relaxed text-muted whitespace-pre-wrap">
              {tier.prompt}
            </pre>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
