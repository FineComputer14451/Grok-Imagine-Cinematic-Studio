import { createFileRoute, Link } from "@tanstack/react-router";
import { BookMarked, Search } from "lucide-react";
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
  GLOSSARY,
  GLOSSARY_CATEGORIES,
  type GlossaryTerm,
} from "@/data/glossary";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/glossary")({
  component: GlossaryPage,
});

function GlossaryPage() {
  const [q, setQ] = useState("");
  const [cat, setCat] = useState<GlossaryTerm["category"] | "all">("all");
  const [openId, setOpenId] = useState(GLOSSARY[0]?.id ?? "");

  const filtered = useMemo(() => {
    return GLOSSARY.filter((t) => {
      if (cat !== "all" && t.category !== cat) return false;
      if (!q.trim()) return true;
      const hay = `${t.term} ${t.short} ${t.body}`.toLowerCase();
      return hay.includes(q.trim().toLowerCase());
    }).sort((a, b) => a.term.localeCompare(b.term));
  }, [q, cat]);

  const active =
    filtered.find((t) => t.id === openId) ?? filtered[0] ?? null;

  const relatedTerms = (active?.related ?? [])
    .map((id) => GLOSSARY.find((t) => t.id === id))
    .filter(Boolean) as GlossaryTerm[];

  return (
    <div className="space-y-8">
      <div>
        <Badge variant="teal">Reference</Badge>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">
          Studio glossary
        </h1>
        <p className="mt-2 max-w-2xl text-muted leading-relaxed">
          Plain-language definitions for pipeline, identity, Imagine, agents,
          API, and billing terms — so beginners can follow Workflows and the
          Learn path without drowning.
        </p>
      </div>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <label className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-subtle" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search DNA, plate, handoff, list price…"
            className="h-11 w-full rounded-lg border border-border bg-surface pl-10 pr-3 text-sm text-fg placeholder:text-subtle outline-none focus:border-border-strong focus:ring-2 focus:ring-teal/30"
          />
        </label>
      </div>

      <div className="flex flex-wrap gap-1.5">
        <button
          type="button"
          onClick={() => setCat("all")}
          className={cn(
            "h-8 rounded-md border px-3 text-xs font-medium",
            cat === "all"
              ? "border-teal/40 bg-teal/10 text-teal"
              : "border-border bg-surface text-muted hover:text-fg",
          )}
        >
          All
        </button>
        {GLOSSARY_CATEGORIES.map((c) => (
          <button
            key={c.id}
            type="button"
            onClick={() => setCat(c.id)}
            className={cn(
              "h-8 rounded-md border px-3 text-xs font-medium",
              cat === c.id
                ? "border-teal/40 bg-teal/10 text-teal"
                : "border-border bg-surface text-muted hover:text-fg",
            )}
          >
            {c.label}
          </button>
        ))}
      </div>

      <p className="text-sm text-subtle">
        {filtered.length} of {GLOSSARY.length} terms
      </p>

      {filtered.length === 0 ? (
        <p className="py-12 text-center text-sm text-muted">
          No terms match that filter.
        </p>
      ) : (
        <div className="grid gap-6 lg:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
          <ul className="space-y-1.5 max-h-[70dvh] overflow-y-auto pr-1">
            {filtered.map((t) => {
              const selected = active?.id === t.id;
              return (
                <li key={t.id}>
                  <button
                    type="button"
                    onClick={() => setOpenId(t.id)}
                    className={cn(
                      "w-full rounded-xl border px-3.5 py-3 text-left transition-colors",
                      selected
                        ? "border-teal/40 bg-teal/5"
                        : "border-border bg-surface hover:border-border-strong",
                    )}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <p className="font-medium text-fg leading-snug">
                        {t.term}
                      </p>
                      <Badge variant="outline" className="shrink-0 capitalize">
                        {t.category}
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

          {active && (
            <Card className="h-fit lg:sticky lg:top-20 border-teal/20">
              <CardHeader>
                <div className="flex flex-wrap items-center gap-2">
                  <Badge variant="teal" className="capitalize">
                    {active.category}
                  </Badge>
                  <BookMarked className="h-4 w-4 text-teal" />
                </div>
                <CardTitle className="mt-2 text-xl">{active.term}</CardTitle>
                <CardDescription>{active.short}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-5">
                <p className="text-sm text-muted leading-relaxed">
                  {active.body}
                </p>

                {relatedTerms.length > 0 && (
                  <div>
                    <p className="mb-2 text-xs font-medium uppercase tracking-wide text-subtle">
                      Related
                    </p>
                    <div className="flex flex-wrap gap-1.5">
                      {relatedTerms.map((r) => (
                        <button
                          key={r.id}
                          type="button"
                          onClick={() => {
                            setOpenId(r.id);
                            setCat("all");
                            setQ("");
                          }}
                          className="h-8 rounded-md border border-border bg-bg px-2.5 text-xs text-muted hover:border-teal/40 hover:text-teal"
                        >
                          {r.term}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                <div className="flex flex-wrap gap-3 text-sm border-t border-border pt-4">
                  <Link to="/learn" className="text-teal hover:underline">
                    Learn path
                  </Link>
                  <Link to="/workflows" className="text-teal hover:underline">
                    Workflows
                  </Link>
                  <Link to="/docs" className="text-teal hover:underline">
                    API docs
                  </Link>
                  <Link to="/pricing" className="text-teal hover:underline">
                    Pricing
                  </Link>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
