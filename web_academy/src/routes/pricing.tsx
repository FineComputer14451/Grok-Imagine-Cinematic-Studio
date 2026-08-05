import { createFileRoute, Link } from "@tanstack/react-router";
import { BadgeCheck, Calculator, DollarSign, ExternalLink } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { GROK_PRICING } from "@/data/api-docs";

export const Route = createFileRoute("/pricing")({
  component: PricingPage,
});

function PricingPage() {
  return (
    <div className="space-y-8">
      <div>
        <Badge variant="teal">Billing</Badge>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">
          Grok API pricing
        </h1>
        <p className="mt-2 max-w-2xl text-muted leading-relaxed">
          Developer API list prices for chat, Imagine, and Voice. Use these when
          budgeting Studio workflows and app integrations.
        </p>
        <div className="mt-3 flex flex-wrap items-center gap-3 text-xs text-subtle">
          <span className="rounded-md border border-border bg-surface px-2 py-1 font-mono">
            As of {GROK_PRICING.asOf}
          </span>
          <a
            href={GROK_PRICING.sourceUrl}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1 text-teal hover:underline"
          >
            {GROK_PRICING.source}
            <ExternalLink className="h-3 w-3" />
          </a>
          <Link
            to="/budget"
            className="inline-flex items-center gap-1 text-teal hover:underline"
          >
            <Calculator className="h-3 w-3" />
            Budget calculator
          </Link>
        </div>
      </div>

      <Card className="border-teal/30 bg-teal/5">
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-base">
            <BadgeCheck className="h-4 w-4 text-teal" />
            Are these draft rates?
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-muted leading-relaxed">
          <p>
            <strong className="text-fg">No.</strong> Table amounts are{" "}
            <strong className="text-fg">published developer API list prices</strong>{" "}
            from xAI’s public docs — not temporary or unofficial “draft” rate
            cards.
          </p>
          <p>
            “Standard still” means the cheaper image model (
            <span className="font-mono text-fg">grok-imagine-image</span>) for
            iteration, vs quality hero stills —{" "}
            <strong className="text-fg">not</strong> that the dollars were
            provisional.
          </p>
          <p>{GROK_PRICING.status}</p>
        </CardContent>
      </Card>

      <Card className="border-border bg-elevated/30">
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Scope & disclaimer</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted leading-relaxed">
          {GROK_PRICING.disclaimer}
        </CardContent>
      </Card>

      <section className="space-y-4">
        <div>
          <h2 className="text-lg font-semibold tracking-tight">
            Studio cost snapshots
          </h2>
          <p className="mt-1 text-sm text-muted">
            Worked examples (~) from list rates — not separate draft tiers. For
            interactive estimates, open the{" "}
            <Link to="/budget" className="text-teal hover:underline">
              budget calculator
            </Link>
            .
          </p>
        </div>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {GROK_PRICING.studioExamples.map((ex) => (
            <Card key={ex.label}>
              <CardHeader className="pb-2">
                <CardDescription>{ex.label}</CardDescription>
                <CardTitle className="font-mono text-2xl text-teal">
                  {ex.estimate}
                </CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-muted">{ex.detail}</CardContent>
            </Card>
          ))}
        </div>
      </section>

      {GROK_PRICING.groups.map((group) => (
        <Card key={group.id}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <DollarSign className="h-4 w-4 text-teal" />
              {group.title}
            </CardTitle>
            <CardDescription>{group.blurb}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto rounded-lg border border-border">
              <table className="w-full min-w-[420px] text-left text-sm">
                <thead className="border-b border-border bg-elevated/50 text-xs uppercase tracking-wide text-subtle">
                  <tr>
                    <th className="px-3 py-2 font-medium">Model / product</th>
                    <th className="px-3 py-2 font-medium">Unit</th>
                    <th className="px-3 py-2 font-medium">List price</th>
                    <th className="px-3 py-2 font-medium">Notes</th>
                  </tr>
                </thead>
                <tbody>
                  {group.rows.map((row) => (
                    <tr
                      key={`${row.model}-${row.unit}`}
                      className="border-b border-border/80 last:border-0"
                    >
                      <td className="px-3 py-2.5 font-mono text-xs text-fg">
                        {row.model}
                      </td>
                      <td className="px-3 py-2.5 text-muted">{row.unit}</td>
                      <td className="px-3 py-2.5 font-mono text-teal">
                        {row.price}
                      </td>
                      <td className="px-3 py-2.5 text-subtle">
                        {row.note ?? "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      ))}

      <Card className="bg-elevated/20">
        <CardHeader>
          <CardTitle className="text-base">Budget tips for Studio work</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-muted">
          <p>
            Iterate on{" "}
            <span className="font-mono text-fg">grok-imagine-image</span> (list
            ~$0.02) before hero{" "}
            <span className="font-mono text-fg">image-quality</span> or video.
          </p>
          <p>
            A 6s 720p clip (~$0.42 at list) costs more than twenty standard
            stills — lock plates and DNA first.
          </p>
          <div className="flex flex-wrap gap-3 pt-2">
            <Link to="/budget" className="text-teal hover:underline">
              Open budget calculator
            </Link>
            <Link to="/docs" className="text-teal hover:underline">
              Integration API docs
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
