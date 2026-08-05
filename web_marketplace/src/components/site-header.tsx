import { Github, PackageOpen, RefreshCw } from "lucide-react";
import { Link } from "@tanstack/react-router";
import { useCatalogLive } from "@/store/catalog-live";
import { useMarketplace } from "@/store/marketplace";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { SignedIn, SignedOut, UserButton } from "@/lib/auth/gates";
import { useCurrentUserState } from "@/lib/auth/use-current-user";
import { toast } from "sonner";

export function SiteHeader() {
  const marketplace = useCatalogLive((s) => s.marketplace);
  const syncing = useCatalogLive((s) => s.syncing);
  const syncFromGitHub = useCatalogLive((s) => s.syncFromGitHub);
  const installed = useMarketplace((s) => s.installed);
  const setFilter = useMarketplace((s) => s.setFilter);
  const installedCount = Object.keys(installed).length;
  const { isPending } = useCurrentUserState();

  const handleSync = async () => {
    const res = await syncFromGitHub();
    if (res.ok) toast.success(res.message);
    else toast.error(res.message);
  };

  return (
    <header className="sticky top-0 z-40 border-b border-[var(--color-border)] bg-[color-mix(in_oklab,var(--color-bg)_88%,transparent)] backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between gap-3 px-4 sm:px-6">
        <div className="flex min-w-0 items-center gap-2.5">
          <div className="flex size-8 shrink-0 items-center justify-center rounded-[var(--radius-sm)] border border-[var(--color-border)] bg-[var(--color-bg-elevated)]">
            <PackageOpen className="size-4 text-[var(--color-fg)]" />
          </div>
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold tracking-tight text-[var(--color-fg)]">
              Plugin Marketplace
            </p>
            <p className="hidden truncate text-xs text-[var(--color-fg-subtle)] sm:block">
              {marketplace.title} · v{marketplace.version}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setFilter("installed")}
            className="hidden rounded-full sm:inline-flex"
            aria-label="View installed plugins"
          >
            <Badge variant={installedCount > 0 ? "success" : "muted"}>
              {installedCount} installed
            </Badge>
          </button>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleSync}
            disabled={syncing}
            className="hidden sm:inline-flex"
            aria-label="Sync catalog from GitHub"
          >
            <RefreshCw className={syncing ? "size-3.5 animate-spin" : "size-3.5"} />
            <span className="hidden md:inline">Sync</span>
          </Button>
          <Button variant="outline" size="sm" asChild>
            <a
              href={marketplace.homepage}
              target="_blank"
              rel="noreferrer"
              className="gap-1.5"
            >
              <Github className="size-3.5" />
              <span className="hidden sm:inline">Source</span>
            </a>
          </Button>
          {isPending ? (
            <div className="size-8 animate-pulse rounded-full bg-[var(--color-bg-muted)]" />
          ) : (
            <>
              <SignedOut>
                <Button variant="secondary" size="sm" asChild>
                  <Link to="/login">Sign in</Link>
                </Button>
              </SignedOut>
              <SignedIn>
                <UserButton />
              </SignedIn>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
