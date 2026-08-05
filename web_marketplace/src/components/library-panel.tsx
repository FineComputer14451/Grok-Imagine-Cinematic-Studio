import { Package } from "lucide-react";
import { useCatalogLive } from "@/store/catalog-live";
import { useMarketplace } from "@/store/marketplace";
import { Badge } from "@/components/ui/badge";
import { PluginIcon } from "@/components/plugin-icon";

export function LibraryPanel({ onOpen }: { onOpen: (id: string) => void }) {
  const plugins = useCatalogLive((s) => s.plugins);
  const installed = useMarketplace((s) => s.installed);
  const ids = Object.keys(installed);
  const items = plugins.filter((p) => ids.includes(p.id));

  if (items.length === 0) {
    return (
      <div className="rounded-[var(--radius-xl)] border border-dashed border-[var(--color-border)] bg-[var(--color-bg-elevated)] px-6 py-10 text-center">
        <Package className="mx-auto size-8 text-[var(--color-fg-subtle)]" />
        <p className="mt-3 text-sm font-medium text-[var(--color-fg)]">
          No plugins installed yet
        </p>
        <p className="mt-1 text-sm text-[var(--color-fg-muted)]">
          Install the full suite or pick modular packs from the catalog.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-[var(--radius-xl)] border border-[var(--color-border)] bg-[var(--color-bg-elevated)] p-4">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-[var(--color-fg)]">
          Your library
        </h3>
        <Badge variant="success">{items.length} active</Badge>
      </div>
      <ul className="divide-y divide-[var(--color-border)]">
        {items.map((p) => (
          <li key={p.id}>
            <button
              type="button"
              onClick={() => onOpen(p.id)}
              className="flex w-full items-center gap-3 py-3 text-left transition-colors hover:bg-[var(--color-bg-subtle)]"
            >
              <div className="flex size-9 items-center justify-center rounded-[var(--radius-sm)] border border-[var(--color-border)] bg-[var(--color-bg)]">
                <PluginIcon name={p.icon} className="size-4" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-[var(--color-fg)]">
                  {p.displayName}
                </p>
                <p className="truncate font-mono text-[11px] text-[var(--color-fg-subtle)]">
                  v{installed[p.id]?.version} ·{" "}
                  {new Date(installed[p.id]?.installedAt).toLocaleDateString()}
                </p>
              </div>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
