import { useMemo, useState } from "react";
import {
  Check,
  Copy,
  Download,
  ExternalLink,
  Trash2,
  X,
} from "lucide-react";
import type { Plugin } from "@/lib/catalog";
import { primaryCliCommand } from "@/lib/catalog";
import { copyText } from "@/lib/copy";
import { formatSkillName } from "@/lib/utils";
import { dependencyLabel, useMarketplace } from "@/store/marketplace";
import { PluginIcon } from "@/components/plugin-icon";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ConsentDialog } from "@/components/consent-dialog";
import { toast } from "sonner";

type Props = {
  plugin: Plugin;
  onClose: () => void;
};

export function PluginDetail({ plugin, onClose }: Props) {
  const isInstalled = useMarketplace((s) => s.isInstalled(plugin.id));
  const install = useMarketplace((s) => s.install);
  const uninstall = useMarketplace((s) => s.uninstall);
  const nsfwConsent = useMarketplace((s) => s.nsfwConsent);
  const [consentOpen, setConsentOpen] = useState(false);
  const [skillQuery, setSkillQuery] = useState("");
  const [copiedKey, setCopiedKey] = useState<string | null>(null);
  const deps = dependencyLabel(plugin);

  const skills = useMemo(() => {
    const q = skillQuery.trim().toLowerCase();
    if (!q) return plugin.skills;
    return plugin.skills.filter(
      (s) =>
        s.name.toLowerCase().includes(q) ||
        s.description.toLowerCase().includes(q),
    );
  }, [plugin.skills, skillQuery]);

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

  const handleCopy = async (cmd: string, key: string, label: string) => {
    const ok = await copyText(cmd);
    if (ok) {
      setCopiedKey(key);
      toast.success(`${label} copied`);
      setTimeout(() => setCopiedKey(null), 1500);
    } else {
      toast.message("Select the command below, then copy", {
        description: cmd,
        duration: 8000,
      });
    }
  };

  const updateCmd =
    plugin.updateCommand ||
    (plugin.isFullSuite
      ? "grok plugin update grok-imagine-cinematic-studio"
      : `grok plugin update ${plugin.name}`);

  return (
    <>
      <div
        className="fixed inset-0 z-50 bg-black/70"
        onClick={onClose}
        aria-hidden
      />
      <aside
        role="dialog"
        aria-modal="true"
        aria-labelledby="plugin-detail-title"
        className="fixed inset-y-0 right-0 z-50 flex w-full max-w-xl flex-col border-l border-[var(--color-border)] bg-[var(--color-bg)] shadow-[var(--shadow-soft)] sm:rounded-l-[var(--radius-xl)]"
      >
        <div className="flex items-start justify-between gap-3 border-b border-[var(--color-border)] p-5">
          <div className="flex items-start gap-3">
            <div className="flex size-12 shrink-0 items-center justify-center rounded-[var(--radius-md)] border border-[var(--color-border)] bg-[var(--color-bg-elevated)]">
              <PluginIcon name={plugin.icon} className="size-6" />
            </div>
            <div>
              <h2
                id="plugin-detail-title"
                className="text-xl font-semibold tracking-tight text-[var(--color-fg)]"
              >
                {plugin.displayName}
              </h2>
              <p className="mt-0.5 font-mono text-xs text-[var(--color-fg-subtle)]">
                {plugin.name} · v{plugin.version} · {plugin.license}
              </p>
              <div className="mt-2 flex flex-wrap gap-1.5">
                {plugin.recommended && (
                  <Badge variant="accent">Recommended</Badge>
                )}
                {isInstalled && <Badge variant="success">Installed</Badge>}
                {plugin.consentRequired && (
                  <Badge variant="warn">Consent required</Badge>
                )}
                {plugin.tags.map((t) => (
                  <Badge key={t} variant="muted">
                    {t}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            aria-label="Close"
          >
            <X className="size-4" />
          </Button>
        </div>

        <div className="flex-1 overflow-y-auto p-5">
          <p className="text-sm leading-relaxed text-[var(--color-fg-muted)]">
            {plugin.longDescription || plugin.description}
          </p>

          <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-3">
            <Stat label="Skills" value={String(plugin.skillCount)} />
            <Stat label="Commands" value={String(plugin.commandCount)} />
            <Stat label="Requires" value={deps ?? "None"} />
          </div>

          <div className="mt-5 space-y-3 rounded-[var(--radius-md)] border border-[var(--color-border)] bg-[var(--color-bg-elevated)] p-3">
            <p className="text-xs font-medium text-[var(--color-fg-subtle)]">
              Grok CLI (real install)
            </p>

            <CliRow
              label="Update existing"
              cmd={updateCmd}
              copied={copiedKey === "update"}
              onCopy={() => handleCopy(updateCmd, "update", "Update command")}
            />

            <CliRow
              label="Fresh install"
              cmd={plugin.installCommand}
              copied={copiedKey === "install"}
              onCopy={() =>
                handleCopy(plugin.installCommand, "install", "Install command")
              }
            />

            <p className="text-[11px] leading-relaxed text-[var(--color-fg-subtle)]">
              Run these in your local terminal with Grok Build installed. This
              marketplace UI only demos library state in the browser — it does
              not install skills into Grok automatically.
            </p>
          </div>

          <Separator className="my-6" />

          {plugin.commands.length > 0 && (
            <section className="mb-6">
              <h3 className="text-sm font-semibold text-[var(--color-fg)]">
                Slash commands
              </h3>
              <ul className="mt-3 flex flex-wrap gap-2">
                {plugin.commands.map((c) => (
                  <li key={c.name}>
                    <Badge variant="muted" className="font-mono">
                      /{c.name.replace(/^commands\//, "").replace(/\.md$/, "")}
                    </Badge>
                  </li>
                ))}
              </ul>
            </section>
          )}

          <section>
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h3 className="text-sm font-semibold text-[var(--color-fg)]">
                Skills ({skills.length})
              </h3>
              <input
                value={skillQuery}
                onChange={(e) => setSkillQuery(e.target.value)}
                placeholder="Filter skills…"
                className="h-9 w-full max-w-xs rounded-[var(--radius-sm)] border border-[var(--color-border)] bg-[var(--color-bg-elevated)] px-3 text-sm text-[var(--color-fg)] placeholder:text-[var(--color-fg-subtle)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-ring)] sm:w-48"
              />
            </div>
            <ul className="mt-3 space-y-2">
              {skills.map((s) => (
                <li
                  key={s.name}
                  className="rounded-[var(--radius-md)] border border-[var(--color-border)] bg-[var(--color-bg-elevated)] px-3 py-2.5"
                >
                  <p className="text-sm font-medium text-[var(--color-fg)]">
                    {formatSkillName(s.name)}
                  </p>
                  <p className="mt-0.5 font-mono text-[11px] text-[var(--color-fg-subtle)]">
                    {s.name}
                  </p>
                  {s.description && (
                    <p className="mt-1.5 text-xs leading-relaxed text-[var(--color-fg-muted)]">
                      {s.description}
                    </p>
                  )}
                </li>
              ))}
              {skills.length === 0 && (
                <li className="py-8 text-center text-sm text-[var(--color-fg-subtle)]">
                  No skills match your filter.
                </li>
              )}
            </ul>
          </section>
        </div>

        <div className="flex flex-wrap gap-2 border-t border-[var(--color-border)] p-5">
          {isInstalled ? (
            <Button
              variant="danger"
              onClick={handleUninstall}
              className="min-h-11"
            >
              <Trash2 className="size-4" />
              Remove
            </Button>
          ) : (
            <Button onClick={handleInstall} className="min-h-11">
              <Download className="size-4" />
              Install
              {plugin.requires.length > 0 ? " + deps" : ""}
            </Button>
          )}
          <Button
            variant="secondary"
            onClick={() =>
              handleCopy(
                primaryCliCommand(plugin, isInstalled),
                "primary",
                isInstalled ? "Update command" : "Install command",
              )
            }
            className="min-h-11"
          >
            {copiedKey === "primary" ? (
              <Check className="size-4" />
            ) : (
              <Copy className="size-4" />
            )}
            {isInstalled ? "Copy update CLI" : "Copy install CLI"}
          </Button>
          <Button variant="outline" asChild className="min-h-11">
            <a href={plugin.homepage} target="_blank" rel="noreferrer">
              <ExternalLink className="size-4" />
              GitHub
            </a>
          </Button>
        </div>
      </aside>

      <ConsentDialog open={consentOpen} onOpenChange={setConsentOpen} />
    </>
  );
}

function CliRow({
  label,
  cmd,
  copied,
  onCopy,
}: {
  label: string;
  cmd: string;
  copied: boolean;
  onCopy: () => void;
}) {
  return (
    <div>
      <p className="mb-1 text-[11px] font-medium text-[var(--color-fg-muted)]">
        {label}
      </p>
      <div className="flex items-center gap-2">
        <input
          readOnly
          value={cmd}
          onFocus={(e) => e.currentTarget.select()}
          onClick={(e) => e.currentTarget.select()}
          className="min-w-0 flex-1 overflow-x-auto rounded-[var(--radius-sm)] border border-[var(--color-border)] bg-[var(--color-bg)] px-3 py-2 font-mono text-xs text-[var(--color-fg)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-ring)]"
          aria-label={label}
        />
        <Button
          variant="secondary"
          size="icon"
          onClick={onCopy}
          aria-label={`Copy ${label}`}
        >
          {copied ? (
            <Check className="size-3.5" />
          ) : (
            <Copy className="size-3.5" />
          )}
        </Button>
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[var(--radius-md)] border border-[var(--color-border)] bg-[var(--color-bg-elevated)] px-3 py-2.5">
      <p className="text-[11px] uppercase tracking-wide text-[var(--color-fg-subtle)]">
        {label}
      </p>
      <p className="mt-1 text-sm font-medium text-[var(--color-fg)]">{value}</p>
    </div>
  );
}
