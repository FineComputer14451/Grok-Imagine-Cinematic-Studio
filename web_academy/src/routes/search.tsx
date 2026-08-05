import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowRight, Search as SearchIcon } from "lucide-react";
import { useMemo, useState } from "react";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ALGORITHMS } from "@/data/consistency";
import { GLOSSARY } from "@/data/glossary";
import { SCENARIOS } from "@/data/scenarios";
import {
  SEARCH_GROUPS,
  SEARCH_INDEX,
  type SearchHit,
} from "@/data/search-index";
import { AGENTS } from "@/data/studio";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/search")({
  component: SearchPage,
});

function buildIndex(): SearchHit[] {
  const dynamic: SearchHit[] = [
    ...GLOSSARY.map((g) => ({
      id: `gloss-${g.id}`,
      title: g.term,
      blurb: g.short,
      href: "/glossary",
      group: "Glossary",
      tags: [
        "glossary",
        g.category,
        g.term.toLowerCase(),
        ...(g.related ?? []),
      ],
    })),
    ...SCENARIOS.map((s) => ({
      id: `scen-${s.id}`,
      title: s.title,
      blurb: s.tagline,
      href: "/scenarios",
      group: "Scenarios",
      tags: ["scenario", s.genre, `tier${s.tier}`, ...s.agents],
    })),
    ...ALGORITHMS.map((a) => ({
      id: `algo-${a.id}`,
      title: a.name,
      blurb: a.short,
      href: "/consistency",
      group: "Algorithms",
      tags: ["algorithm", a.stage, a.weight, ...a.studioAgents],
    })),
    ...AGENTS.map((a) => ({
      id: `agent-${a.id}`,
      title: a.name,
      blurb: a.role,
      href: "/agents",
      group: "Agents",
      tags: [
        "agent",
        a.activation,
        a.category,
        `tier${a.tier}`,
        ...a.skills.slice(0, 8),
      ],
    })),
  ];
  return [...SEARCH_INDEX, ...dynamic];
}

const EXTRA_GROUPS = ["Glossary", "Scenarios", "Algorithms", "Agents"] as const;

function SearchPage() {
  const [q, setQ] = useState("");
  const [group, setGroup] = useState<string>("all");
  const index = useMemo(() => buildIndex(), []);

  const groups = useMemo(() => {
    return ["all", ...SEARCH_GROUPS, ...EXTRA_GROUPS];
  }, []);

  const results = useMemo(() => {
    const query = q.trim().toLowerCase();
    return index
      .filter((h) => {
        if (group !== "all" && h.group !== group) return false;
        if (!query) return true;
        const hay =
          `${h.title} ${h.blurb} ${h.group} ${h.tags.join(" ")}`.toLowerCase();
        return query.split(/\s+/).every((tok) => hay.includes(tok));
      })
      .slice(0, 80);
  }, [index, q, group]);

  const byGroup = useMemo(() => {
    const map = new Map<string, SearchHit[]>();
    for (const h of results) {
      const list = map.get(h.group) ?? [];
      list.push(h);
      map.set(h.group, list);
    }
    return map;
  }, [results]);

  return (
    <div className="space-y-8">
      <div>
        <Badge variant="teal">Find</Badge>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">
          Search Academy
        </h1>
        <p className="mt-2 max-w-2xl text-muted leading-relaxed">
          Jump to pages, glossary terms, scenarios, algorithms, and agents —
          one search across Studio Academy.
        </p>
      </div>

      <label className="relative block">
        <SearchIcon className="pointer-events-none absolute left-3.5 top-1/2 h-5 w-5 -translate-y-1/2 text-subtle" />
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Try DNA, push-in, 2.39, plate lock, pricing…"
          autoFocus
          className="h-12 w-full rounded-xl border border-border bg-surface pl-12 pr-4 text-base text-fg placeholder:text-subtle outline-none focus:border-border-strong focus:ring-2 focus:ring-teal/30"
        />
      </label>

      <div className="flex flex-wrap gap-1.5">
        {groups.map((g) => (
          <button
            key={g}
            type="button"
            onClick={() => setGroup(g)}
            className={cn(
              "h-9 rounded-md border px-3 text-xs font-medium capitalize",
              group === g
                ? "border-teal/40 bg-teal/10 text-teal"
                : "border-border bg-surface text-muted hover:text-fg",
            )}
          >
            {g === "all" ? "All" : g}
          </button>
        ))}
      </div>

      <p className="text-sm text-subtle">
        {results.length} result{results.length === 1 ? "" : "s"}
        {q.trim() ? ` for “${q.trim()}”` : " · showing catalog"}
        {" · "}
        {index.length} indexed
      </p>

      {results.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-sm text-muted">
            No matches. Try “DNA”, “teal”, “Director”, or clear filters.
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-8">
          {[...byGroup.entries()].map(([g, hits]) => (
            <section key={g} className="space-y-3">
              <h2 className="text-sm font-medium uppercase tracking-wide text-subtle">
                {g}
                <span className="ml-2 font-mono text-teal">{hits.length}</span>
              </h2>
              <ul className="grid gap-2 sm:grid-cols-2">
                {hits.map((h) => (
                  <li key={h.id}>
                    <Link
                      to={h.href}
                      className="group flex h-full flex-col rounded-xl border border-border bg-surface px-4 py-3.5 transition-colors hover:border-border-strong hover:bg-elevated/30"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <p className="font-medium leading-snug text-fg">
                          {h.title}
                        </p>
                        <ArrowRight className="mt-0.5 h-4 w-4 shrink-0 text-subtle group-hover:text-teal" />
                      </div>
                      <p className="mt-1 line-clamp-2 text-sm text-muted">
                        {h.blurb}
                      </p>
                      <p className="mt-2 font-mono text-[10px] text-subtle">
                        {h.href}
                      </p>
                    </Link>
                  </li>
                ))}
              </ul>
            </section>
          ))}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Quick starts</CardTitle>
          <CardDescription>Common learner jumps</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          {[
            ["DNA inject", "dna"],
            ["Push-in", "push"],
            ["2.39", "2.39"],
            ["Plate lock", "plate"],
            ["Pricing", "pricing"],
            ["Director", "director"],
          ].map(([label, query]) => (
            <button
              key={query}
              type="button"
              onClick={() => {
                setQ(query);
                setGroup("all");
              }}
              className="h-9 rounded-md border border-border bg-elevated px-3 text-xs text-muted hover:text-fg"
            >
              {label}
            </button>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
