import { createFileRoute } from "@tanstack/react-router";
import { Search, X } from "lucide-react";
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
import { AGENTS, type Agent } from "@/data/studio";
import { useProgress } from "@/lib/progress";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/agents")({
  component: AgentsPage,
});

const CATEGORIES: { id: Agent["category"] | "all"; label: string }[] = [
  { id: "all", label: "All" },
  { id: "leadership", label: "Leadership" },
  { id: "creative", label: "Creative" },
  { id: "production", label: "Production" },
  { id: "post", label: "Post" },
  { id: "special", label: "Special" },
];

function skillVariant(index: number): "teal" | "default" | "outline" | "accent" {
  const variants = ["teal", "default", "outline", "accent"] as const;
  return variants[index % variants.length];
}

function AgentsPage() {
  const [q, setQ] = useState("");
  const [cat, setCat] = useState<(typeof CATEGORIES)[number]["id"]>("all");
  const [skillFilter, setSkillFilter] = useState<string | null>(null);
  const { completedAgents, completeAgent } = useProgress();

  const popularSkills = useMemo(() => {
    const counts = new Map<string, number>();
    for (const a of AGENTS) {
      for (const s of a.skills) counts.set(s, (counts.get(s) ?? 0) + 1);
    }
    return [...counts.entries()]
      .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
      .slice(0, 12)
      .map(([name]) => name);
  }, []);

  const filtered = useMemo(() => {
    return AGENTS.filter((a) => {
      if (cat !== "all" && a.category !== cat) return false;
      if (skillFilter && !a.skills.includes(skillFilter)) return false;
      if (!q.trim()) return true;
      const hay =
        `${a.name} ${a.role} ${a.activation} ${a.skills.join(" ")}`.toLowerCase();
      return hay.includes(q.trim().toLowerCase());
    });
  }, [q, cat, skillFilter]);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">
          Agent roster
        </h1>
        <p className="mt-2 max-w-2xl text-muted">
          {AGENTS.length} specialists with skill badges. Filter by category or
          skill, search by name, copy activation commands.
        </p>
      </div>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <label className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-subtle" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search agents or skills…"
            className="h-11 w-full rounded-lg border border-border bg-surface pl-10 pr-3 text-sm text-fg placeholder:text-subtle outline-none focus:border-border-strong focus:ring-2 focus:ring-teal/30"
          />
        </label>
        <div className="flex flex-wrap gap-1.5">
          {CATEGORIES.map((c) => (
            <button
              key={c.id}
              type="button"
              onClick={() => setCat(c.id)}
              className={cn(
                "h-9 rounded-md border px-3 text-xs font-medium transition-colors",
                cat === c.id
                  ? "border-teal/40 bg-teal/10 text-teal"
                  : "border-border bg-surface text-muted hover:text-fg",
              )}
            >
              {c.label}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-2">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-medium uppercase tracking-wide text-subtle">
            Skills
          </span>
          {skillFilter && (
            <button
              type="button"
              onClick={() => setSkillFilter(null)}
              className="inline-flex h-6 items-center gap-1 rounded-md border border-border px-2 text-[11px] text-muted hover:text-fg"
            >
              <X className="h-3 w-3" />
              Clear skill
            </button>
          )}
        </div>
        <div className="flex flex-wrap gap-1.5">
          {popularSkills.map((skill) => {
            const active = skillFilter === skill;
            return (
              <button
                key={skill}
                type="button"
                onClick={() => setSkillFilter(active ? null : skill)}
                className={cn(
                  "inline-flex h-7 items-center rounded-md border px-2.5 text-[11px] font-medium transition-colors",
                  active
                    ? "border-teal/40 bg-teal/10 text-teal"
                    : "border-border bg-elevated/50 text-muted hover:border-border-strong hover:text-fg",
                )}
              >
                {skill}
              </button>
            );
          })}
        </div>
      </div>

      <p className="text-sm text-subtle">
        Showing {filtered.length}
        {skillFilter ? ` with “${skillFilter}”` : ""} ·{" "}
        {completedAgents.length} marked tried
      </p>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {filtered.map((agent) => {
          const tried = completedAgents.includes(agent.id);
          return (
            <Card
              key={agent.id}
              className={cn(tried && "border-success/30 bg-success/5")}
            >
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between gap-2">
                  <CardTitle className="text-base leading-snug">
                    {agent.name}
                  </CardTitle>
                  <Badge variant="outline">T{agent.tier}+</Badge>
                </div>
                <CardDescription className="line-clamp-3">
                  {agent.role}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex flex-wrap gap-1.5">
                  {agent.skills.map((skill, i) => (
                    <button
                      key={skill}
                      type="button"
                      title={`Filter by ${skill}`}
                      onClick={() =>
                        setSkillFilter(skillFilter === skill ? null : skill)
                      }
                      className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal/40 rounded-md"
                    >
                      <Badge
                        variant={
                          skillFilter === skill ? "teal" : skillVariant(i)
                        }
                        className={cn(
                          "cursor-pointer transition-opacity hover:opacity-90",
                          skillFilter &&
                            skillFilter !== skill &&
                            "opacity-50",
                        )}
                      >
                        {skill}
                      </Badge>
                    </button>
                  ))}
                </div>
                <code className="block rounded-md border border-border bg-bg px-2.5 py-2 font-mono text-[11px] text-muted break-all">
                  {agent.activation}
                </code>
                <div className="flex flex-wrap gap-2">
                  <CopyButton text={agent.activation} label="Copy command" />
                  <button
                    type="button"
                    onClick={() => completeAgent(agent.id)}
                    className={cn(
                      "inline-flex h-8 items-center rounded-md border px-3 text-xs font-medium transition-colors",
                      tried
                        ? "border-success/40 text-success"
                        : "border-border text-muted hover:text-fg",
                    )}
                  >
                    {tried ? "Tried" : "Mark tried"}
                  </button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {filtered.length === 0 && (
        <p className="py-12 text-center text-sm text-muted">
          No agents match that filter.
        </p>
      )}
    </div>
  );
}
