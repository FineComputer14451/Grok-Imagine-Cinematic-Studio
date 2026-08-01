import { FolderKanban, Lock, MoreHorizontal } from "lucide-react";
import { toast } from "sonner";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { PROJECTS } from "@/lib/studio-data";
import { useStudioStore } from "@/lib/studio-store";
import { formatRelative } from "@/lib/utils";

export function ProjectsView() {
  const shots = useStudioStore((s) => s.shots);
  const setView = useStudioStore((s) => s.setView);
  const updateDraft = useStudioStore((s) => s.updateDraft);

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm text-fg-muted">
            Organize reels, lock identity packs, and track shot counts.
          </p>
        </div>
        <Button
          size="sm"
          onClick={() => toast.message("New project (demo) — use Compose to add shots")}
        >
          New project
        </Button>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-2">
        {PROJECTS.map((project) => {
          const projectShots = shots.filter((s) => s.projectId === project.id);
          const ready = projectShots.filter((s) => s.status === "ready").length;
          return (
            <Card key={project.id} className="overflow-hidden">
              <div
                className="h-1.5 w-full"
                style={{ background: project.color }}
              />
              <CardHeader className="flex-row items-start justify-between space-y-0">
                <div className="flex items-start gap-3">
                  <div className="flex size-10 items-center justify-center rounded-lg border border-border bg-bg-subtle">
                    {project.status === "locked" ? (
                      <Lock className="size-4 text-fg-muted" />
                    ) : (
                      <FolderKanban className="size-4 text-fg-muted" />
                    )}
                  </div>
                  <div>
                    <CardTitle>{project.name}</CardTitle>
                    <CardDescription>{project.description}</CardDescription>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="icon-sm"
                  aria-label="Project menu"
                  onClick={() => toast.message("Project menu (demo)")}
                >
                  <MoreHorizontal className="size-4" />
                </Button>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex flex-wrap gap-2">
                  <Badge>
                    {project.shotCount} cataloged
                  </Badge>
                  <Badge variant={project.status === "locked" ? "draft" : "ready"}>
                    {project.status}
                  </Badge>
                  <Badge variant="default">{ready} ready in session</Badge>
                </div>

                <dl className="grid grid-cols-2 gap-2 text-xs">
                  <div className="rounded-md border border-border bg-bg-subtle/50 px-2.5 py-2">
                    <dt className="text-fg-subtle">Updated</dt>
                    <dd className="mt-0.5 font-medium text-fg">
                      {formatRelative(new Date(project.updatedAt))}
                    </dd>
                  </div>
                  <div className="rounded-md border border-border bg-bg-subtle/50 px-2.5 py-2">
                    <dt className="text-fg-subtle">In this session</dt>
                    <dd className="mt-0.5 font-medium tabular text-fg">
                      {projectShots.length} shots
                    </dd>
                  </div>
                </dl>

                <div className="flex flex-wrap gap-2">
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={() => {
                      updateDraft({ projectId: project.id });
                      setView("compose");
                    }}
                  >
                    Compose in project
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setView("gallery")}
                  >
                    Open gallery
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
