import {
  Clapperboard,
  Dna,
  Film,
  FolderKanban,
  Gauge,
  Images,
  LayoutDashboard,
  ListOrdered,
  PenLine,
  ScrollText,
  Settings2,
  Wallet,
  X,
  Sparkles,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useStudioStore, type StudioView } from "@/lib/studio-store";
import { Button } from "@/components/ui/button";
import { STATS, STUDIO_VERSION } from "@/lib/studio-data";

const NAV: { id: StudioView; label: string; icon: typeof LayoutDashboard }[] = [
  { id: "overview", label: "Dashboard", icon: LayoutDashboard },
  { id: "production", label: "Production", icon: ScrollText },
  { id: "dna", label: "DNA & Memory", icon: Dna },
  { id: "sequences", label: "Sequences", icon: Film },
  { id: "compose", label: "Imagine", icon: PenLine },
  { id: "gallery", label: "Gallery", icon: Images },
  { id: "queue", label: "Render queue", icon: ListOrdered },
  { id: "quota", label: "Quota", icon: Wallet },
  { id: "projects", label: "Projects", icon: FolderKanban },
  { id: "tools", label: "Tools", icon: Settings2 },
];

export function Sidebar() {
  const view = useStudioStore((s) => s.view);
  const setView = useStudioStore((s) => s.setView);
  const sidebarOpen = useStudioStore((s) => s.sidebarOpen);
  const setSidebarOpen = useStudioStore((s) => s.setSidebarOpen);
  const queueLen = useStudioStore((s) => s.queue.length);

  const creditPct = Math.round(
    (STATS.creditsRemaining / STATS.creditsTotal) * 100,
  );

  const nav = (
    <>
      <div className="flex items-center gap-2.5 px-4 py-5">
        <div className="flex size-9 items-center justify-center rounded-lg border border-border bg-bg-subtle">
          <Clapperboard className="size-4 text-fg" />
        </div>
        <div className="min-w-0">
          <div className="truncate text-sm font-semibold tracking-tight">
            Imagine Studio
          </div>
          <div className="truncate text-xs text-fg-subtle">
            Cinematic · v{STUDIO_VERSION}
          </div>
        </div>
      </div>

      <div className="mx-3 mb-3 rounded-md border border-border bg-bg-subtle/60 px-2.5 py-2">
        <div className="flex items-center gap-1.5 text-[11px] text-fg-muted">
          <Gauge className="size-3" />
          Ops severity
        </div>
        <p className="mt-0.5 text-xs font-medium text-warning">
          WARN · 3 attention items
        </p>
      </div>

      <nav className="flex flex-1 flex-col gap-0.5 overflow-y-auto px-2 pb-2">
        {NAV.map((item) => {
          const Icon = item.icon;
          const active = view === item.id;
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => {
                setView(item.id);
                setSidebarOpen(false);
              }}
              className={cn(
                "flex h-10 items-center gap-3 rounded-md px-3 text-sm font-medium transition-colors duration-150",
                active
                  ? "bg-bg-subtle text-fg"
                  : "text-fg-muted hover:bg-bg-hover hover:text-fg",
              )}
            >
              <Icon className="size-4 shrink-0" />
              <span className="flex-1 text-left">{item.label}</span>
              {item.id === "queue" && queueLen > 0 && (
                <span className="tabular rounded-full border border-border bg-bg-elevated px-1.5 py-0.5 text-[11px] text-fg-muted">
                  {queueLen}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      <div className="mt-auto border-t border-border p-4">
        <div className="mb-2 flex items-center justify-between text-xs">
          <span className="text-fg-muted">Credits</span>
          <span className="tabular text-fg">
            {STATS.creditsRemaining.toLocaleString()}
            <span className="text-fg-subtle">
              {" "}
              / {STATS.creditsTotal.toLocaleString()}
            </span>
          </span>
        </div>
        <div className="h-1.5 overflow-hidden rounded-full bg-bg-subtle">
          <div
            className="h-full rounded-full bg-primary transition-all duration-300"
            style={{ width: `${creditPct}%` }}
          />
        </div>
        <div className="mt-3 flex items-center gap-2 rounded-md border border-border bg-bg-elevated px-2.5 py-2">
          <Sparkles className="size-3.5 text-fg-muted" />
          <div className="min-w-0">
            <div className="text-xs font-medium text-fg">
              {STATS.coreAgents}-agent department
            </div>
            <div className="truncate text-[11px] text-fg-subtle">
              SuperGrok Pro · Grok 4.5
            </div>
          </div>
        </div>
      </div>
    </>
  );

  return (
    <>
      <aside className="hidden w-60 shrink-0 flex-col border-r border-border bg-bg-elevated md:flex">
        {nav}
      </aside>

      {sidebarOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          <button
            type="button"
            aria-label="Close menu"
            className="absolute inset-0 bg-bg/70"
            onClick={() => setSidebarOpen(false)}
          />
          <aside className="absolute inset-y-0 left-0 flex w-[min(16.5rem,88vw)] flex-col border-r border-border bg-bg-elevated shadow-xl">
            <div className="absolute right-2 top-3">
              <Button
                variant="ghost"
                size="icon-sm"
                onClick={() => setSidebarOpen(false)}
                aria-label="Close"
              >
                <X className="size-4" />
              </Button>
            </div>
            {nav}
          </aside>
        </div>
      )}
    </>
  );
}
