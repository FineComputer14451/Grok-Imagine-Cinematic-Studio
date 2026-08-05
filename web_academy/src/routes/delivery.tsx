import { createFileRoute, Link } from "@tanstack/react-router";
import {
  Check,
  Circle,
  ClipboardCheck,
  ExternalLink,
  RotateCcw,
  Ship,
} from "lucide-react";
import { useMemo } from "react";
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
import {
  buildDeliveryReport,
  DELIVERY_ALL_IDS,
  DELIVERY_SECTIONS,
  DIRECTOR_ONELINER,
  SHIP_ORDER,
} from "@/data/delivery";
import { useProgress } from "@/lib/progress";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/delivery")({
  component: DeliveryPage,
});

function DeliveryPage() {
  const deliveryChecked = useProgress((s) => s.deliveryChecked);
  const toggleDelivery = useProgress((s) => s.toggleDelivery);
  const setDeliverySection = useProgress((s) => s.setDeliverySection);
  const clearDelivery = useProgress((s) => s.clearDelivery);

  const checkedSet = useMemo(
    () => new Set(deliveryChecked),
    [deliveryChecked],
  );

  const total = DELIVERY_ALL_IDS.length;
  const done = DELIVERY_ALL_IDS.filter((id) => checkedSet.has(id)).length;
  const pct = total === 0 ? 0 : Math.round((done / total) * 100);
  const allGreen = done === total;

  const blockers = DELIVERY_SECTIONS.find((s) => s.id === "preflight")!.items;
  const blockersDone = blockers.every((i) => checkedSet.has(i.id));

  const report = useMemo(
    () => buildDeliveryReport(deliveryChecked),
    [deliveryChecked],
  );

  return (
    <div className="space-y-8">
      <div>
        <Badge variant="teal">Ship gate</Badge>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">
          Delivery checklist
        </h1>
        <p className="mt-2 max-w-2xl text-muted leading-relaxed">
          Final gate before stitch, client handoff, or “done.” Stills-first ·
          SFW path · stop on any identity No-Go. Checks stay in this browser.
        </p>
      </div>

      <div className="rounded-xl border border-border bg-surface px-4 py-4">
        <div className="flex flex-wrap items-center justify-between gap-3 text-sm">
          <div className="flex items-center gap-2">
            <ClipboardCheck className="h-4 w-4 text-teal" />
            <span className="text-muted">
              {done}/{total} complete
            </span>
            {!blockersDone && (
              <Badge variant="outline" className="text-[11px]">
                Pre-flight open
              </Badge>
            )}
            {allGreen && (
              <Badge variant="teal" className="text-[11px]">
                Ready to ship
              </Badge>
            )}
          </div>
          <span className="font-mono text-teal">{pct}%</span>
        </div>
        <div className="mt-2 h-2 overflow-hidden rounded-full bg-border">
          <div
            className={cn(
              "h-full rounded-full transition-all duration-500",
              allGreen ? "bg-success" : "bg-teal",
            )}
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        <CopyButton text={report} label="Copy full report" />
        <CopyButton text={DIRECTOR_ONELINER} label="Copy director one-liner" />
        <Button
          type="button"
          variant="ghost"
          size="sm"
          className="gap-1.5 text-muted"
          onClick={() => clearDelivery()}
          disabled={done === 0}
        >
          <RotateCcw className="h-3.5 w-3.5" />
          Reset
        </Button>
      </div>

      <div className="space-y-6">
        {DELIVERY_SECTIONS.map((section) => {
          const sectionIds = section.items.map((i) => i.id);
          const sectionDone = sectionIds.filter((id) =>
            checkedSet.has(id),
          ).length;
          const sectionAll = sectionDone === sectionIds.length;
          return (
            <Card key={section.id}>
              <CardHeader className="pb-3">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <CardTitle className="text-base">{section.title}</CardTitle>
                      {section.id === "preflight" && (
                        <Badge variant="outline" className="text-[10px]">
                          Blockers
                        </Badge>
                      )}
                    </div>
                    <CardDescription className="mt-1">
                      {section.blurb}
                    </CardDescription>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs text-subtle">
                      {sectionDone}/{sectionIds.length}
                    </span>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="h-8 text-xs"
                      onClick={() =>
                        setDeliverySection(sectionIds, !sectionAll)
                      }
                    >
                      {sectionAll ? "Clear" : "All"}
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-1.5 pt-0">
                {section.items.map((item) => {
                  const on = checkedSet.has(item.id);
                  return (
                    <div
                      key={item.id}
                      className={cn(
                        "flex items-start gap-3 rounded-xl border px-3 py-3 transition-colors sm:px-4",
                        on
                          ? "border-teal/30 bg-teal/5"
                          : "border-border bg-bg hover:border-border-strong",
                      )}
                    >
                      <button
                        type="button"
                        onClick={() => toggleDelivery(item.id)}
                        className="mt-0.5 shrink-0 rounded-md p-0.5 text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal/40"
                        aria-pressed={on}
                        aria-label={
                          on
                            ? `Uncheck: ${item.label}`
                            : `Check: ${item.label}`
                        }
                      >
                        {on ? (
                          <Check className="h-5 w-5 text-success" />
                        ) : (
                          <Circle className="h-5 w-5 text-subtle" />
                        )}
                      </button>
                      <div className="min-w-0 flex-1">
                        <p
                          className={cn(
                            "text-sm leading-relaxed",
                            on ? "text-fg" : "text-muted",
                          )}
                        >
                          {item.label}
                        </p>
                        {item.href && (
                          <Link
                            to={item.href}
                            className="mt-1.5 inline-flex items-center gap-1 text-xs text-teal hover:underline"
                          >
                            Open tool
                            <ExternalLink className="h-3 w-3" />
                          </Link>
                        )}
                      </div>
                    </div>
                  );
                })}
              </CardContent>
            </Card>
          );
        })}
      </div>

      <Card className="border-teal/20 bg-teal/5">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Ship className="h-4 w-4 text-teal" />
            Director one-liner
          </CardTitle>
          <CardDescription>
            Paste into Studio Director / notes before final stitch
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <pre className="overflow-x-auto whitespace-pre-wrap rounded-lg border border-border bg-bg p-4 font-mono text-xs leading-relaxed text-muted">
            {DIRECTOR_ONELINER}
          </pre>
          <CopyButton text={DIRECTOR_ONELINER} label="Copy one-liner" />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Ship order</CardTitle>
          <CardDescription>
            Recommended sequence once pre-flight is green
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ol className="space-y-2">
            {SHIP_ORDER.map((step, i) => (
              <li
                key={step}
                className="flex items-start gap-3 text-sm text-muted"
              >
                <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-md border border-border bg-elevated font-mono text-[11px] text-subtle">
                  {i + 1}
                </span>
                <span className="pt-0.5">{step}</span>
              </li>
            ))}
          </ol>
          <div className="mt-5 flex flex-wrap gap-2">
            <Link
              to="/pack"
              className="inline-flex h-8 items-center rounded-md border border-border bg-elevated px-3 text-xs font-medium text-fg hover:border-border-strong"
            >
              Project pack
            </Link>
            <Link
              to="/lab"
              className="inline-flex h-8 items-center rounded-md border border-border bg-elevated px-3 text-xs font-medium text-fg hover:border-border-strong"
            >
              Prompt lab
            </Link>
            <Link
              to="/craft"
              className="inline-flex h-8 items-center rounded-md border border-border bg-elevated px-3 text-xs font-medium text-fg hover:border-border-strong"
            >
              Craft hub
            </Link>
          </div>
        </CardContent>
      </Card>

      <p className="text-xs leading-relaxed text-subtle">
        Rule of thumb: generate with craft 01–06 · cut with 07 · score with 08 ·
        ship only when this checklist is green. Companion markdown lives in the
        repo under docs/academy/DELIVERY_CHECKLIST.md.
      </p>
    </div>
  );
}
