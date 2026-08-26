import { useEffect, useMemo } from "react";
import { useCatalogLive } from "@/store/catalog-live";
import { useMarketplace } from "@/store/marketplace";
import { SiteHeader } from "@/components/site-header";
import { MarketplaceHero } from "@/components/marketplace-hero";
import { CatalogToolbar } from "@/components/catalog-toolbar";
import { PluginCard } from "@/components/plugin-card";
import { LibraryPanel } from "@/components/library-panel";
import { PluginDetail } from "@/components/plugin-detail";
import { SkillBrowser } from "@/components/skill-browser";
import { DependencyGraph } from "@/components/dependency-graph";

export function MarketplacePage() {
  const plugins = useCatalogLive((s) => s.plugins);
  const marketplace = useCatalogLive((s) => s.marketplace);
  const getPlugin = useCatalogLive((s) => s.getPlugin);
  const syncFromGitHub = useCatalogLive((s) => s.syncFromGitHub);
  const search = useMarketplace((s) => s.search);
  const filter = useMarketplace((s) => s.filter);
  const view = useMarketplace((s) => s.view);
  const matchesFilter = useMarketplace((s) => s.matchesFilter);
  const installed = useMarketplace((s) => s.installed);
  const activePluginId = useMarketplace((s) => s.activePluginId);
  const setActivePluginId = useMarketplace((s) => s.setActivePluginId);

  useEffect(() => {
    void syncFromGitHub().catch(() => {
      /* keep bundled catalog */
    });
  }, [syncFromGitHub]);

  const list = Array.isArray(plugins) ? plugins : [];

  const visible = useMemo(() => {
    try {
      return list.filter((p) => p && matchesFilter(p));
    } catch {
      return list;
    }
  }, [list, matchesFilter, search, filter, installed]);

  const active = activePluginId ? getPlugin(activePluginId) : undefined;
  const skillTotal =
    list.find((p) => p.isFullSuite)?.skillCount ??
    list.reduce((n, p) => n + (p.packId ? p.skillCount || 0 : 0), 0);

  return (
    <div className="min-h-dvh bg-[var(--color-bg)] text-[var(--color-fg)]">
      <SiteHeader />
      <main className="mx-auto max-w-6xl px-4 pb-16 pt-6 sm:px-6">
        <MarketplaceHero />

        <div className="mt-10 grid gap-6 lg:grid-cols-[minmax(0,1fr)_280px]">
          <div className="min-w-0 space-y-4">
            <CatalogToolbar />

            {view === "packs" &&
              (visible.length === 0 ? (
                <div className="rounded-[var(--radius-xl)] border border-dashed border-[var(--color-border)] px-6 py-16 text-center text-sm text-[var(--color-fg-muted)]">
                  No plugins match your filters.
                </div>
              ) : (
                <div className="grid gap-4 sm:grid-cols-2">
                  {visible.map((plugin) => (
                    <PluginCard
                      key={plugin.id}
                      plugin={plugin}
                      onOpen={setActivePluginId}
                    />
                  ))}
                </div>
              ))}

            {view === "skills" && (
              <SkillBrowser
                plugins={list}
                onOpenPlugin={setActivePluginId}
                seedQuery={search}
              />
            )}

            {view === "graph" && (
              <DependencyGraph
                plugins={list}
                onOpenPlugin={setActivePluginId}
              />
            )}
          </div>

          <aside className="space-y-4 lg:sticky lg:top-20 lg:self-start">
            <LibraryPanel onOpen={setActivePluginId} />
            <div className="rounded-[var(--radius-xl)] border border-[var(--color-border)] bg-[var(--color-bg-elevated)] p-4 text-sm text-[var(--color-fg-muted)]">
              <p className="font-medium text-[var(--color-fg)]">How installs work</p>
              <ul className="mt-2 list-disc space-y-1.5 pl-4 text-xs leading-relaxed">
                <li>
                  <strong className="font-medium text-[var(--color-fg)]">
                    Real install
                  </strong>{" "}
                  uses the Grok CLI on your machine:
                  <code className="mt-1 block break-all rounded bg-[var(--color-bg)] px-2 py-1 font-mono text-[10px] text-[var(--color-fg)]">
                    grok plugin update grok-imagine-cinematic-studio
                  </code>
                </li>
                <li>
                  Fresh install:{" "}
                  <code className="break-all font-mono text-[10px] text-[var(--color-fg)]">
                    grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio --trust
                  </code>
                </li>
                <li>
                  Buttons here only save{" "}
                  <strong className="font-medium text-[var(--color-fg)]">
                    local demo state
                  </strong>{" "}
                  in this browser.
                </li>
                <li>NSFW requires explicit consent before marking installed.</li>
                <li>
                  Skill browser lists all 64 exclusive skills; Graph shows pack
                  requires + declutter.
                </li>
                <li>Catalog can sync live from the GitHub main branch.</li>
              </ul>
            </div>
          </aside>
        </div>

        <footer className="mt-14 border-t border-[var(--color-border)] pt-6 text-center text-xs text-[var(--color-fg-subtle)]">
          Grok Imagine Cinematic Studio marketplace · v{marketplace.version} ·{" "}
          {skillTotal} skills · MIT · Independent community project · Not
          affiliated with xAI
        </footer>
      </main>

      {active && (
        <PluginDetail
          plugin={active}
          onClose={() => setActivePluginId(null)}
        />
      )}
    </div>
  );
}
