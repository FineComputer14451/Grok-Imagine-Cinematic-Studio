import { useState } from "react";
import {
  Check,
  Copy,
  Download,
  ExternalLink,
  Lock,
  Trash2,
} from "lucide-react";
import type { Plugin } from "@/lib/catalog";
import { primaryCliCommand } from "@/lib/catalog";
import { copyText } from "@/lib/copy";
import { dependencyLabel, useMarketplace } from "@/store/marketplace";
import { PluginIcon } from "@/components/plugin-icon";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ConsentDialog } from "@/components/consent-dialog";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

type Props = {
  plugin: Plugin;
  onOpen: (id: string) => void;
};

export function PluginCard({ plugin, onOpen }: Props) {
  const isInstalled = useMarketplace((s) => s.isInstalled(plugin.id));
  const install = useMarketplace((s) => s.install);
  const uninstall = useMarketplace((s) => s.uninstall);
  const nsfwConsent = useMarketplace((s) => s.nsfwConsent);
  const [consentOpen, setConsentOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const deps = dependencyLabel(plugin);

  const handleInstall = () => {
    if (plugin.consentRequired && !nsfwConsent) {
      setConsentOpen(true);
      return;
    }
    const res = install(plugin.id);
    if (res.ok) toast.success(res.message);
    else toast.error(res.message);
  };

  const handleUninstall = () => {
    const res = uninstall(plugin.id);
    if (res.ok) toast.success(res.message);
    else toast.error(res.message);
  };

  const handleCopy = async () => {
    const cmd = primaryCliCommand(plugin, isInstalled);
    const ok = await copyText(cmd);
    if (ok) {
      setCopied(true);
      toast.success(
        isInstalled ? "Update command copied" : "Install command copied",
      );
      setTimeout(() => setCopied(false), 1500);
    } else {
      toast.error("Could not copy — select the command in Details instead");
    }
  };

  return (
    <>
      <article
        className={cn(
          "group flex h-full flex-col rounded-[var(--radius-xl)] border border-[var(--color-border)] bg-[var(--color-bg-elevated)] p-5 transition-[border-color,transform,background-color] duration-200 hover:border-[var(--color-border-strong)]",
          isInstalled &&
            "ring-1 ring-[color-mix(in_oklab,var(--color-success)_40%,transparent)]",
        )}
      >
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3">
            <div className="flex size-11 shrink-0 items-center justify-center rounded-[var(--radius-md)] border border-[var(--color-border)] bg-[var(--color-bg-subtle)] text-[var(--color-fg)]">
              <PluginIcon name={plugin.icon} className="size-5" />
            </div>
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-1.5">
                <h3 className="text-base font-semibold tracking-tight text-[var(--color-fg)]">
                  {plugin.displayName}
                </h3>
                {plugin.recommended && (
                  <Badge variant="accent">Recommended</Badge>
                )}
                {plugin.consentRequired && (
                  <Badge variant="warn">
                    <Lock className="mr-1 size-3" />
                    Opt-in
                  </Badge>
                )}
                {isInstalled && <Badge variant="success">Installed</Badge>}
              </div>
              <p className="mt-0.5 font-mono text-xs text-[var(--color-fg-subtle)]">
                {plugin.name} · v{plugin.version}
              </p>
            </div>
          </div>
        </div>

        <p className="mt-4 line-clamp-3 flex-1 text-sm leading-relaxed text-[var(--color-fg-muted)]">
          {plugin.longDescription || plugin.description}
        </p>

        <div className="mt-4 flex flex-wrap gap-2 text-xs text-[var(--color-fg-subtle)]">
          <span className="rounded-full border border-[var(--color-border)] px-2.5 py-1">
            {plugin.skillCount} skills
          </span>
          <span className="rounded-full border border-[var(--color-border)] px-2.5 py-1">
            {plugin.commandCount} commands
          </span>
          {deps && (
            <span className="rounded-full border border-[var(--color-border)] px-2.5 py-1">
              Requires {deps}
            </span>
          )}
        </div>

        <div className="mt-5 flex flex-wrap gap-2">
          {isInstalled ? (
            <Button
              variant="danger"
              size="sm"
              onClick={handleUninstall}
              className="min-h-10"
            >
              <Trash2 className="size-3.5" />
              Remove
            </Button>
          ) : (
            <Button size="sm" onClick={handleInstall} className="min-h-10">
              <Download className="size-3.5" />
              Install
            </Button>
          )}
          <Button
            variant="secondary"
            size="sm"
            onClick={() => onOpen(plugin.id)}
            className="min-h-10"
          >
            Details
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleCopy}
            className="min-h-10"
            aria-label={
              isInstalled ? "Copy update command" : "Copy install command"
            }
          >
            {copied ? (
              <Check className="size-3.5" />
            ) : (
              <Copy className="size-3.5" />
            )}
          </Button>
          <Button variant="ghost" size="sm" asChild className="min-h-10">
            <a href={plugin.homepage} target="_blank" rel="noreferrer">
              <ExternalLink className="size-3.5" />
            </a>
          </Button>
        </div>
      </article>

      <ConsentDialog open={consentOpen} onOpenChange={setConsentOpen} />
    </>
  );
}
