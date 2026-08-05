import { useMemo, useState } from "react";
import { Search, X } from "lucide-react";
import { formatSkillName } from "@/lib/utils";
import {
  buildSkillIndex,
  filterSkills,
  type SkillEntry,
} from "@/lib/skill-index";
import type { Plugin } from "@/lib/catalog";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

const PACK_CHIPS: { id: string | "all"; label: string }[] = [
  { id: "all", label: "All packs" },
  { id: "core", label: "Core" },
  { id: "camera-image", label: "Camera" },
  { id: "sequence-narrative", label: "Sequence" },
  { id: "delivery-post", label: "Delivery" },
  { id: "nsfw", label: "NSFW" },
];

type Props = {
  plugins: Plugin[];
  onOpenPlugin: (pluginId: string) => void;
  seedQuery?: string;
};

export function SkillBrowser({ plugins, onOpenPlugin, seedQuery = "" }: Props) {
  const [query, setQuery] = useState(seedQuery);
  const [packFilter, setPackFilter] = useState<string | "all">("all");

  const index = useMemo(() => buildSkillIndex(plugins), [plugins]);
  const visible = useMemo(
    () => filterSkills(index, query, packFilter),
    [index, query, packFilter],
  );

  const byPack = useMemo(() => {
    const map = new Map<string, number>();
    for (const s of index) {
      const key = s.packId ?? "full";
      map.set(key, (map.get(key) ?? 0) + 1);
    }
    return map;
  }, [index]);

  return (
    <div className="space-y-4" id="skills">
      <div className="flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold tracking-tight text-[var(--color-fg)]">
            Skill browser
          </h2>
          <p className="text-sm text-[var(--color-fg-muted)]">
            {index.length} exclusive skills across modular packs · click a row
            to open its pack
          </p>
        </div>
        <p className="text-xs text-[var(--color-fg-subtle)]">
          Showing {visible.length}
          {visible.length !== index.length ? ` of ${index.length}` : ""}
        </p>
      </div>

      <div className="relative">
        <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-[var(--color-fg-subtle)]" />
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Filter skills by name or description…"
          className="h-11 pl-10 pr-10"
          aria-label="Filter skills"
        />
        {query && (
          <button
            type="button"
            onClick={() => setQuery("")}
            className="absolute right-3 top-1/2 -translate-y-1/2 rounded p-1 text-[var(--color-fg-subtle)] hover:text-[var(--color-fg)]"
            aria-label="Clear skill filter"
          >
            <X className="size-4" />
          </button>
        )}
      </div>

      <div className="-mx-1 flex gap-1.5 overflow-x-auto px-1 pb-1">
        {PACK_CHIPS.map((chip) => {
          const count =
            chip.id === "all"
              ? index.length
              : (byPack.get(chip.id) ?? 0);
          return (
            <button
              key={chip.id}
              type="button"
              onClick={() => setPackFilter(chip.id)}
              className={cn(
                "h-9 shrink-0 rounded-full border px-3.5 text-sm font-medium transition-colors",
                packFilter === chip.id
                  ? "border-[var(--color-accent)] bg-[var(--color-accent)] text-[var(--color-accent-fg)]"
                  : "border-[var(--color-border)] bg-[var(--color-bg-elevated)] text-[var(--color-fg-muted)] hover:border-[var(--color-border-strong)] hover:text-[var(--color-fg)]",
              )}
            >
              {chip.label}
              <span className="ml-1.5 opacity-70">{count}</span>
            </button>
          );
        })}
      </div>

      <ul className="divide-y divide-[var(--color-border)] overflow-hidden rounded-[var(--radius-xl)] border border-[var(--color-border)] bg-[var(--color-bg-elevated)]">
        {visible.map((skill) => (
          <SkillRow
            key={skill.name}
            skill={skill}
            onOpen={() => onOpenPlugin(skill.pluginId)}
          />
        ))}
        {visible.length === 0 && (
          <li className="px-5 py-12 text-center text-sm text-[var(--color-fg-subtle)]">
            No skills match this filter.
          </li>
        )}
      </ul>
    </div>
  );
}

function SkillRow({
  skill,
  onOpen,
}: {
  skill: SkillEntry;
  onOpen: () => void;
}) {
  return (
    <li>
      <button
        type="button"
        onClick={onOpen}
        className="flex w-full flex-col gap-1 px-4 py-3.5 text-left transition-colors hover:bg-[var(--color-bg-subtle)] sm:flex-row sm:items-start sm:justify-between sm:gap-4"
      >
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium text-[var(--color-fg)]">
            {formatSkillName(skill.name)}
          </p>
          <p className="mt-0.5 font-mono text-[11px] text-[var(--color-fg-subtle)]">
            {skill.name}
          </p>
          {skill.description && (
            <p className="mt-1.5 line-clamp-2 text-xs leading-relaxed text-[var(--color-fg-muted)]">
              {skill.description}
            </p>
          )}
        </div>
        <Badge variant="muted" className="mt-1 w-fit shrink-0 sm:mt-0">
          {skill.packLabel}
        </Badge>
      </button>
    </li>
  );
}
