import { Menu, Search, Bell, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useStudioStore, type StudioView } from "@/lib/studio-store";
import { STUDIO_VERSION, type DensityMode } from "@/lib/studio-data";
import { cn } from "@/lib/utils";

const titles: Record<StudioView, { title: string; subtitle: string }> = {
  overview: {
    title: "Dashboard",
    subtitle: `${STUDIO_VERSION} · TUI parity · compact / ops / full`,
  },
  production: {
    title: "Production Bible",
    subtitle: "Logline → visual language → pipeline lock",
  },
  dna: {
    title: "DNA & Memory",
    subtitle: "Identity lock · drift · injection blocks",
  },
  sequences: {
    title: "Sequences",
    subtitle: "Chain QA · polish · delivery readiness",
  },
  compose: {
    title: "Imagine",
    subtitle: "Prompt · camera · grade · agent-mode handoff",
  },
  gallery: {
    title: "Gallery",
    subtitle: "Takes, plates, and storyboard frames",
  },
  queue: {
    title: "Render queue",
    subtitle: "Live jobs and priority order",
  },
  quota: {
    title: "Quota",
    subtitle: "Spend, cascade, soft caps",
  },
  tools: {
    title: "Tools",
    subtitle: "Health actions · model stack · activation",
  },
  projects: {
    title: "Projects",
    subtitle: "Reels and locked sequences",
  },
};

const DENSITY: { id: DensityMode; label: string }[] = [
  { id: "compact", label: "1 · Compact" },
  { id: "ops", label: "2 · Ops" },
  { id: "full", label: "3 · Full" },
];

export function Topbar() {
  const view = useStudioStore((s) => s.view);
  const setView = useStudioStore((s) => s.setView);
  const setSidebarOpen = useStudioStore((s) => s.setSidebarOpen);
  const search = useStudioStore((s) => s.search);
  const setSearch = useStudioStore((s) => s.setSearch);
  const density = useStudioStore((s) => s.density);
  const setDensity = useStudioStore((s) => s.setDensity);
  const meta = titles[view];

  return (
    <header className="sticky top-0 z-30 border-b border-border bg-bg/90 backdrop-blur-md">
      <div className="flex flex-col gap-3 px-4 py-3 sm:px-6">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex items-start gap-3">
            <Button
              variant="ghost"
              size="icon-sm"
              className="mt-0.5 md:hidden"
              onClick={() => setSidebarOpen(true)}
              aria-label="Open menu"
            >
              <Menu className="size-4" />
            </Button>
            <div>
              <h1 className="text-lg font-semibold tracking-tight text-fg sm:text-xl">
                {meta.title}
              </h1>
              <p className="text-sm text-fg-muted">{meta.subtitle}</p>
            </div>
          </div>

          <div className="flex flex-1 items-center gap-2 sm:max-w-md lg:max-w-sm lg:flex-none">
            <div className="relative flex-1">
              <Search className="pointer-events-none absolute left-3 top-1/2 size-3.5 -translate-y-1/2 text-fg-subtle" />
              <Input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search shots, DNA, sequences…"
                className="h-9 pl-9"
                aria-label="Search"
              />
            </div>
            <Button variant="ghost" size="icon-sm" aria-label="Notifications">
              <Bell className="size-4" />
            </Button>
            <Button
              size="sm"
              className="shrink-0"
              onClick={() => setView("compose")}
            >
              <Plus className="size-3.5" />
              <span className="hidden sm:inline">New shot</span>
            </Button>
          </div>
        </div>

        {view === "overview" && (
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs text-fg-subtle">View density</span>
            <div className="flex rounded-md border border-border bg-bg-elevated p-0.5">
              {DENSITY.map((d) => (
                <button
                  key={d.id}
                  type="button"
                  onClick={() => setDensity(d.id)}
                  className={cn(
                    "h-8 rounded-sm px-2.5 text-xs font-medium transition-colors",
                    density === d.id
                      ? "bg-primary text-primary-fg"
                      : "text-fg-muted hover:text-fg",
                  )}
                >
                  {d.label}
                </button>
              ))}
            </div>
            <span className="text-xs text-fg-subtle">
              Matches TUI keys 1 / 2 / 3
            </span>
          </div>
        )}
      </div>
    </header>
  );
}
