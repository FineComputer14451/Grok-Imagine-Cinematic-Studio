import { Copy, Download, Eye } from "lucide-react";
import { toast } from "sonner";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PROJECTS, type Shot } from "@/lib/studio-data";
import { useStudioStore } from "@/lib/studio-store";
import { cn, formatRelative } from "@/lib/utils";
import { ShotFrame } from "./shot-frame";
import { StatusBadge } from "./status-badge";

const FILTERS: { id: "all" | Shot["status"] | Shot["mode"]; label: string }[] = [
  { id: "all", label: "All" },
  { id: "ready", label: "Ready" },
  { id: "rendering", label: "Rendering" },
  { id: "queued", label: "Queued" },
  { id: "image", label: "Stills" },
  { id: "video", label: "Video" },
  { id: "failed", label: "Failed" },
  { id: "draft", label: "Drafts" },
];

export function GalleryView() {
  const shots = useStudioStore((s) => s.shots);
  const search = useStudioStore((s) => s.search);
  const filter = useStudioStore((s) => s.galleryFilter);
  const setFilter = useStudioStore((s) => s.setGalleryFilter);
  const selectedShotId = useStudioStore((s) => s.selectedShotId);
  const setSelectedShotId = useStudioStore((s) => s.setSelectedShotId);

  const filtered = shots.filter((s) => {
    const q = search.trim().toLowerCase();
    const matchesSearch =
      !q ||
      s.title.toLowerCase().includes(q) ||
      s.prompt.toLowerCase().includes(q);
    if (!matchesSearch) return false;
    if (filter === "all") return true;
    if (filter === "image" || filter === "video" || filter === "storyboard") {
      return s.mode === filter;
    }
    return s.status === filter;
  });

  const selected =
    shots.find((s) => s.id === selectedShotId) ?? filtered[0] ?? null;

  return (
    <div className="grid gap-4 lg:grid-cols-5">
      <div className="space-y-4 lg:col-span-3">
        <div className="flex flex-wrap gap-1.5">
          {FILTERS.map((f) => (
            <button
              key={f.id}
              type="button"
              onClick={() => setFilter(f.id)}
              className={cn(
                "h-8 rounded-full border px-3 text-xs font-medium transition-colors",
                filter === f.id
                  ? "border-primary bg-primary text-primary-fg"
                  : "border-border bg-bg-elevated text-fg-muted hover:text-fg",
              )}
            >
              {f.label}
            </button>
          ))}
        </div>

        {filtered.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-16 text-center">
              <p className="text-sm font-medium text-fg">No shots match</p>
              <p className="mt-1 text-sm text-fg-muted">
                Try another filter or clear search.
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2">
            {filtered.map((shot) => {
              const active = selected?.id === shot.id;
              return (
                <button
                  key={shot.id}
                  type="button"
                  onClick={() => setSelectedShotId(shot.id)}
                  className={cn(
                    "rounded-xl border p-2 text-left transition-colors",
                    active
                      ? "border-border-strong bg-bg-subtle"
                      : "border-border bg-card hover:bg-bg-hover/40",
                  )}
                >
                  <ShotFrame
                    frame={shot.frame}
                    aspect={shot.aspect}
                    status={shot.status}
                    mode={shot.mode}
                  />
                  <div className="mt-2 flex items-start justify-between gap-2 px-0.5">
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium">{shot.title}</p>
                      <p className="text-xs text-fg-subtle">
                        {formatRelative(new Date(shot.createdAt))}
                      </p>
                    </div>
                    <StatusBadge status={shot.status} />
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </div>

      <div className="lg:col-span-2">
        {selected ? (
          <Card className="sticky top-20">
            <CardHeader>
              <div className="flex items-start justify-between gap-2">
                <div>
                  <CardTitle className="text-balance">{selected.title}</CardTitle>
                  <CardDescription>
                    {PROJECTS.find((p) => p.id === selected.projectId)?.name ??
                      "Project"}{" "}
                    · Take {selected.take}
                  </CardDescription>
                </div>
                <StatusBadge status={selected.status} />
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <ShotFrame
                frame={selected.frame}
                aspect={selected.aspect}
                status={selected.status}
                mode={selected.mode}
              />

              <p className="text-sm leading-relaxed text-fg-muted">
                {selected.prompt}
              </p>

              <dl className="grid grid-cols-2 gap-3 text-xs">
                <Meta label="Mode" value={selected.mode} />
                <Meta label="Aspect" value={selected.aspect} />
                <Meta label="Model" value={selected.model} />
                <Meta label="Seed" value={String(selected.seed)} />
                <Meta label="Camera" value={selected.camera} />
                <Meta label="Lens" value={selected.lens} />
                <Meta label="Grade" value={selected.grade} />
                {selected.duration != null && (
                  <Meta label="Duration" value={`${selected.duration}s`} />
                )}
              </dl>

              <div className="flex flex-wrap gap-2">
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => {
                    void navigator.clipboard?.writeText(selected.prompt);
                    toast.success("Prompt copied");
                  }}
                >
                  <Copy className="size-3.5" />
                  Copy prompt
                </Button>
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => toast.message("Export queued for download")}
                >
                  <Download className="size-3.5" />
                  Export
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => toast.message("Inspector opened (demo)")}
                >
                  <Eye className="size-3.5" />
                  Inspect
                </Button>
              </div>
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardContent className="py-16 text-center text-sm text-fg-muted">
              Select a shot to inspect metadata.
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

function Meta({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-border bg-bg-subtle/50 px-2.5 py-2">
      <dt className="text-fg-subtle">{label}</dt>
      <dd className="mt-0.5 font-medium text-fg">{value}</dd>
    </div>
  );
}
