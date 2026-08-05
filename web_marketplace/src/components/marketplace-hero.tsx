import { useState } from "react";
import {
  ArrowRight,
  Check,
  Copy,
  Layers,
  Loader2,
  RefreshCw,
  Terminal,
  Wand2,
} from "lucide-react";
import {
  FULL_SUITE_UPDATE_CMD,
  REPO_INSTALL_CMD,
  totalCommands,
  totalSkills,
} from "@/lib/catalog";
import { copyText } from "@/lib/copy";
import { useCatalogLive } from "@/store/catalog-live";
import { useMarketplace } from "@/store/marketplace";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";

export function MarketplaceHero() {
  const marketplace = useCatalogLive((s) => s.marketplace);
  const plugins = useCatalogLive((s) => s.plugins);
  const syncing = useCatalogLive((s) => s.syncing);
  const source = useCatalogLive((s) => s.source);
  const lastSyncedAt = useCatalogLive((s) => s.lastSyncedAt);
  const syncFromGitHub = useCatalogLive((s) => s.syncFromGitHub);

  const installFullSuite = useMarketplace((s) => s.installFullSuite);
  const isInstalled = useMarketplace((s) => s.isInstalled);
  const setView = useMarketplace((s) => s.setView);
  const fullInstalled = isInstalled("grok-imagine-cinematic-studio");
  const [copied, setCopied] = useState<"update" | "install" | null>(null);

  const handleInstallFull = () => {
    try {
      const res = installFullSuite();
      if (res.ok) toast.success(res.message);
      else toast.error(res.message);
    } catch {
      toast.error("Could not update library state");
    }
  };

  const handleSync = async () => {
    const res = await syncFromGitHub();
    if (res.ok) toast.success(res.message);
    else toast.error(res.message);
  };

  const handleCopy = async (cmd: string, key: "update" | "install") => {
    const ok = await copyText(cmd);
    if (ok) {
      setCopied(key);
      toast.success(
        key === "update" ? "Update command copied" : "Install command copied",
      );
      setTimeout(() => setCopied(null), 1500);
    } else {
      toast.message("Select and copy manually", {
        description: cmd,
        duration: 8000,
      });
    }
  };

  const pin = marketplace.pinSha || "";
  const skillCount =
    plugins.find((p) => p.isFullSuite)?.skillCount ?? totalSkills();
  const commandCount =
    plugins.find((p) => p.isFullSuite)?.commandCount ?? totalCommands();

  return (
    <section className="relative overflow-hidden rounded-[var(--radius-xl)] border border-[var(--color-border)] bg-[var(--color-bg-elevated)]">
      <div className="absolute inset-0">
        <img
          src="/banner.jpg"
          alt=""
          className="h-full w-full object-cover opacity-35"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[var(--color-bg-elevated)] via-[color-mix(in_oklab,var(--color-bg-elevated)_70%,transparent)] to-[color-mix(in_oklab,var(--color-bg)_40%,transparent)]" />
      </div>

      <div className="relative z-10 flex flex-col gap-6 p-6 sm:p-8 md:p-10">
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="accent">v{marketplace.version}</Badge>
          <Badge variant="muted">
            Grok Build {marketplace.requiresGrokBuild}
          </Badge>
          <Badge variant="muted">Independent community project</Badge>
          <Badge variant={source === "github" ? "success" : "muted"}>
            {source === "github" ? "Live from GitHub" : "Bundled catalog"}
          </Badge>
        </div>

        <div className="max-w-2xl space-y-3">
          <h1 className="font-display text-balance text-3xl font-semibold tracking-[-0.03em] text-[var(--color-fg)] sm:text-4xl md:text-[2.75rem] md:leading-[1.1]">
            {marketplace.title}
          </h1>
          <p className="max-w-xl text-pretty text-base text-[var(--color-fg-muted)] sm:text-lg">
            Browse the full suite and modular packs — Core, Camera & Image,
            Sequence & Narrative, Delivery & Post, and optional NSFW. Real
            installs use the Grok CLI; this site demos library state locally.
          </p>
        </div>

        <div className="flex flex-wrap gap-3 text-sm text-[var(--color-fg-muted)]">
          <span className="inline-flex items-center gap-1.5">
            <Wand2 className="size-4 text-[var(--color-fg-subtle)]" />
            {skillCount} skills
          </span>
          <span className="inline-flex items-center gap-1.5">
            <Terminal className="size-4 text-[var(--color-fg-subtle)]" />
            {commandCount} commands
          </span>
          <span className="inline-flex items-center gap-1.5">
            <Layers className="size-4 text-[var(--color-fg-subtle)]" />
            {plugins.length} marketplace plugins
          </span>
        </div>

        <div className="w-full max-w-xl space-y-2 rounded-[var(--radius-md)] border border-[var(--color-border)] bg-[color-mix(in_oklab,var(--color-bg)_80%,transparent)] p-3 backdrop-blur-sm">
          <p className="text-[11px] font-medium uppercase tracking-wide text-[var(--color-fg-subtle)]">
            Real CLI
          </p>
          <div className="flex items-center gap-2">
            <code className="min-w-0 flex-1 truncate font-mono text-xs text-[var(--color-fg)] sm:text-sm">
              {FULL_SUITE_UPDATE_CMD}
            </code>
            <Button
              variant="secondary"
              size="sm"
              className="shrink-0"
              onClick={() => handleCopy(FULL_SUITE_UPDATE_CMD, "update")}
            >
              {copied === "update" ? (
                <Check className="size-3.5" />
              ) : (
                <Copy className="size-3.5" />
              )}
              Update
            </Button>
          </div>
          <div className="flex items-center gap-2">
            <code className="min-w-0 flex-1 truncate font-mono text-[11px] text-[var(--color-fg-muted)] sm:text-xs">
              {REPO_INSTALL_CMD}
            </code>
            <Button
              variant="ghost"
              size="sm"
              className="shrink-0"
              onClick={() => handleCopy(REPO_INSTALL_CMD, "install")}
            >
              {copied === "install" ? (
                <Check className="size-3.5" />
              ) : (
                <Copy className="size-3.5" />
              )}
              Fresh
            </Button>
          </div>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:flex-wrap">
          <Button
            size="lg"
            onClick={handleInstallFull}
            disabled={fullInstalled}
            className="min-h-11"
          >
            {fullInstalled
              ? "Full suite marked installed"
              : "Mark full suite installed"}
            {!fullInstalled && <ArrowRight className="size-4" />}
          </Button>
          <Button
            variant="secondary"
            size="lg"
            onClick={handleSync}
            disabled={syncing}
            className="min-h-11"
          >
            {syncing ? (
              <Loader2 className="size-4 animate-spin" />
            ) : (
              <RefreshCw className="size-4" />
            )}
            {syncing ? "Syncing…" : "Sync from GitHub"}
          </Button>
          <Button
            variant="outline"
            size="lg"
            className="min-h-11"
            onClick={() => {
              setView("skills");
              document.getElementById("catalog")?.scrollIntoView({
                behavior: "smooth",
              });
            }}
          >
            Browse skills
          </Button>
          <Button variant="outline" size="lg" asChild className="min-h-11">
            <a href="#catalog">Browse packs</a>
          </Button>
        </div>

        <p className="text-xs text-[var(--color-fg-subtle)]">
          Not affiliated with or endorsed by xAI.
          {pin ? (
            <>
              {" "}
              Pin SHA{" "}
              <code className="font-mono text-[var(--color-fg-muted)]">
                {pin.slice(0, 12)}…
              </code>
            </>
          ) : null}
          {lastSyncedAt ? (
            <> · Synced {new Date(lastSyncedAt).toLocaleString()}</>
          ) : null}
        </p>
      </div>
    </section>
  );
}
