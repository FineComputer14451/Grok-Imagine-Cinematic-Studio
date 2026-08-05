import { GitBranch, LayoutGrid, ListTree, Search, X } from "lucide-react";
import { filters, type FilterId } from "@/lib/catalog";
import {
  useMarketplace,
  type CatalogView,
} from "@/store/marketplace";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const VIEWS: { id: CatalogView; label: string; icon: typeof LayoutGrid }[] = [
  { id: "packs", label: "Packs", icon: LayoutGrid },
  { id: "skills", label: "Skills", icon: ListTree },
  { id: "graph", label: "Graph", icon: GitBranch },
];

export function CatalogToolbar() {
  const search = useMarketplace((s) => s.search);
  const setSearch = useMarketplace((s) => s.setSearch);
  const filter = useMarketplace((s) => s.filter);
  const setFilter = useMarketplace((s) => s.setFilter);
  const view = useMarketplace((s) => s.view);
  const setView = useMarketplace((s) => s.setView);
  const clearAll = useMarketplace((s) => s.clearAll);
  const count = useMarketplace((s) => s.installedCount());

  return (
    <div className="space-y-4" id="catalog">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold tracking-tight text-[var(--color-fg)]">
            Catalog
          </h2>
          <p className="text-sm text-[var(--color-fg-muted)]">
            Full suite or modular packs · 64 exclusive skills · core required
            for satellites
          </p>
        </div>
        {count > 0 && (
          <Button variant="ghost" size="sm" onClick={clearAll}>
            Clear library
          </Button>
        )}
      </div>

      <div
        className="inline-flex rounded-[var(--radius-md)] border border-[var(--color-border)] bg-[var(--color-bg-elevated)] p-1"
        role="tablist"
        aria-label="Catalog view"
      >
        {VIEWS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            type="button"
            role="tab"
            aria-selected={view === id}
            onClick={() => setView(id)}
            className={cn(
              "inline-flex h-9 items-center gap-1.5 rounded-[var(--radius-sm)] px-3 text-sm font-medium transition-colors",
              view === id
                ? "bg-[var(--color-accent)] text-[var(--color-accent-fg)]"
                : "text-[var(--color-fg-muted)] hover:text-[var(--color-fg)]",
            )}
          >
            <Icon className="size-3.5" />
            {label}
          </button>
        ))}
      </div>

      {view === "packs" && (
        <>
          <div className="relative">
            <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-[var(--color-fg-subtle)]" />
            <Input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search packs, skills, tags…"
              className="h-11 pl-10 pr-10"
              aria-label="Search plugins"
            />
            {search && (
              <button
                type="button"
                onClick={() => setSearch("")}
                className="absolute right-3 top-1/2 -translate-y-1/2 rounded p-1 text-[var(--color-fg-subtle)] hover:text-[var(--color-fg)]"
                aria-label="Clear search"
              >
                <X className="size-4" />
              </button>
            )}
          </div>

          <div className="-mx-1 flex gap-1.5 overflow-x-auto px-1 pb-1">
            {filters.map((f) => (
              <button
                key={f.id}
                type="button"
                onClick={() => setFilter(f.id as FilterId)}
                className={cn(
                  "h-9 shrink-0 rounded-full border px-3.5 text-sm font-medium transition-colors",
                  filter === f.id
                    ? "border-[var(--color-accent)] bg-[var(--color-accent)] text-[var(--color-accent-fg)]"
                    : "border-[var(--color-border)] bg-[var(--color-bg-elevated)] text-[var(--color-fg-muted)] hover:border-[var(--color-border-strong)] hover:text-[var(--color-fg)]",
                )}
              >
                {f.label}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
