import { ArrowDown, GitBranch, Layers } from "lucide-react";
import type { Plugin } from "@/lib/catalog";
import { packSkillCounts } from "@/lib/skill-index";
import { Badge } from "@/components/ui/badge";
import { PluginIcon } from "@/components/plugin-icon";
import { cn } from "@/lib/utils";

type Props = {
  plugins: Plugin[];
  onOpenPlugin: (pluginId: string) => void;
};

export function DependencyGraph({ plugins, onOpenPlugin }: Props) {
  const rows = packSkillCounts(plugins);
  const full = rows.find((r) => r.isFullSuite);
  const satellites = rows.filter((r) => !r.isFullSuite);
  const totalExclusive = satellites.reduce((n, r) => n + r.skills, 0);

  return (
    <div className="space-y-5" id="graph">
      <div>
        <h2 className="text-lg font-semibold tracking-tight text-[var(--color-fg)]">
          Dependency graph
        </h2>
        <p className="text-sm text-[var(--color-fg-muted)]">
          Full suite is the recommended one-click path. Satellite packs require
          Core; exclusive membership totals {totalExclusive} skills.
        </p>
      </div>

      {/* Full suite */}
      {full && (
        <button
          type="button"
          onClick={() => onOpenPlugin(full.id)}
          className="w-full rounded-[var(--radius-xl)] border border-[var(--color-accent)] bg-[color-mix(in_oklab,var(--color-accent)_8%,var(--color-bg-elevated))] p-5 text-left transition-colors hover:bg-[color-mix(in_oklab,var(--color-accent)_14%,var(--color-bg-elevated))]"
        >
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div className="flex items-start gap-3">
              <div className="flex size-11 items-center justify-center rounded-[var(--radius-md)] border border-[var(--color-border)] bg-[var(--color-bg)]">
                <Layers className="size-5 text-[var(--color-fg)]" />
              </div>
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <h3 className="text-base font-semibold text-[var(--color-fg)]">
                    {full.label}
                  </h3>
                  {full.recommended && (
                    <Badge variant="accent">Recommended</Badge>
                  )}
                </div>
                <p className="mt-1 text-sm text-[var(--color-fg-muted)]">
                  One install · supersedes satellites via{" "}
                  <code className="font-mono text-xs">full_suite_wins</code>
                </p>
              </div>
            </div>
            <div className="flex gap-2 text-xs text-[var(--color-fg-subtle)]">
              <span className="rounded-full border border-[var(--color-border)] px-2.5 py-1">
                {full.skills} skills
              </span>
              <span className="rounded-full border border-[var(--color-border)] px-2.5 py-1">
                {full.commands} commands
              </span>
            </div>
          </div>
        </button>
      )}

      <div className="flex justify-center text-[var(--color-fg-subtle)]">
        <div className="flex flex-col items-center gap-1">
          <ArrowDown className="size-4" />
          <span className="text-[11px] uppercase tracking-wide">or modular</span>
          <ArrowDown className="size-4" />
        </div>
      </div>

      {/* Core */}
      {(() => {
        const core = satellites.find((s) =>
          plugins.find((p) => p.id === s.id)?.packId === "core",
        );
        if (!core) return null;
        const corePlugin = plugins.find((p) => p.id === core.id)!;
        return (
          <div className="space-y-3">
            <NodeCard
              plugin={corePlugin}
              skills={core.skills}
              commands={core.commands}
              onOpen={() => onOpenPlugin(core.id)}
              highlight
            />
            <div className="flex justify-center">
              <div className="flex items-center gap-2 text-[11px] uppercase tracking-wide text-[var(--color-fg-subtle)]">
                <GitBranch className="size-3.5" />
                requires core
              </div>
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              {satellites
                .filter((s) => s.id !== core.id)
                .map((s) => {
                  const plugin = plugins.find((p) => p.id === s.id)!;
                  return (
                    <NodeCard
                      key={s.id}
                      plugin={plugin}
                      skills={s.skills}
                      commands={s.commands}
                      onOpen={() => onOpenPlugin(s.id)}
                    />
                  );
                })}
            </div>
          </div>
        );
      })()}

      <div className="rounded-[var(--radius-xl)] border border-[var(--color-border)] bg-[var(--color-bg-elevated)] p-4 text-xs leading-relaxed text-[var(--color-fg-muted)]">
        <p className="font-medium text-[var(--color-fg)]">Declutter policy</p>
        <p className="mt-1.5">
          If Full Suite and satellite packs are both present, studio tooling
          applies{" "}
          <code className="font-mono text-[var(--color-fg)]">
            full_suite_wins
          </code>{" "}
          — overlapping satellite skill copies are dropped. Skills stay
          single-source in the repo; packs are manifest filters only.
        </p>
      </div>
    </div>
  );
}

function NodeCard({
  plugin,
  skills,
  commands,
  onOpen,
  highlight,
}: {
  plugin: Plugin;
  skills: number;
  commands: number;
  onOpen: () => void;
  highlight?: boolean;
}) {
  return (
    <button
      type="button"
      onClick={onOpen}
      className={cn(
        "w-full rounded-[var(--radius-lg)] border bg-[var(--color-bg-elevated)] p-4 text-left transition-colors hover:border-[var(--color-border-strong)]",
        highlight
          ? "border-[var(--color-border-strong)]"
          : "border-[var(--color-border)]",
      )}
    >
      <div className="flex items-start gap-3">
        <div className="flex size-10 shrink-0 items-center justify-center rounded-[var(--radius-sm)] border border-[var(--color-border)] bg-[var(--color-bg)]">
          <PluginIcon name={plugin.icon} className="size-4" />
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-sm font-semibold text-[var(--color-fg)]">
            {plugin.displayName}
          </p>
          <p className="mt-0.5 font-mono text-[11px] text-[var(--color-fg-subtle)]">
            {plugin.name}
          </p>
          <div className="mt-2 flex flex-wrap gap-1.5 text-[11px] text-[var(--color-fg-subtle)]">
            <span className="rounded-full border border-[var(--color-border)] px-2 py-0.5">
              {skills} skills
            </span>
            {commands > 0 && (
              <span className="rounded-full border border-[var(--color-border)] px-2 py-0.5">
                {commands} cmds
              </span>
            )}
            {plugin.requires.length > 0 && (
              <span className="rounded-full border border-[var(--color-border)] px-2 py-0.5">
                needs {plugin.requires.join(", ")}
              </span>
            )}
          </div>
        </div>
      </div>
    </button>
  );
}
