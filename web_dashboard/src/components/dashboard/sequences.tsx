import { toast } from "sonner";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { PROJECTS } from "@/lib/studio-data";
import { useStudioStore } from "@/lib/studio-store";

export function SequencesView() {
  const sequences = useStudioStore((s) => s.sequences);

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-fg-muted">
          Long-form chains with QA, polish, and delivery gates.
        </p>
        <Button
          size="sm"
          onClick={() => toast.message("Sequence init (demo) — use CLI for full pipeline")}
        >
          New sequence
        </Button>
      </div>

      <div className="grid gap-3">
        {sequences.map((seq) => {
          const project = PROJECTS.find((p) => p.id === seq.projectId);
          return (
            <Card key={seq.id}>
              <CardHeader className="flex-row flex-wrap items-start justify-between gap-2 space-y-0">
                <div>
                  <CardTitle className="text-base">{seq.name}</CardTitle>
                  <CardDescription>
                    {project?.name ?? "Project"} · {seq.clips} clips ·{" "}
                    {seq.durationSec}s
                  </CardDescription>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  <Badge>{seq.status}</Badge>
                  <Badge
                    variant={
                      seq.chainQa === "pass"
                        ? "ready"
                        : seq.chainQa === "hold"
                          ? "failed"
                          : "queued"
                    }
                  >
                    chain {seq.chainQa}
                  </Badge>
                  <Badge variant={seq.identityLock ? "ready" : "draft"}>
                    {seq.identityLock ? "ID lock" : "ID open"}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="mb-3 grid grid-cols-2 gap-2 text-xs sm:grid-cols-4">
                  <Meta
                    label="Polish"
                    value={seq.polishPass ? "pass" : "hold"}
                    ok={seq.polishPass}
                  />
                  <Meta
                    label="Deliver"
                    value={seq.deliverPass ? "pass" : "hold"}
                    ok={seq.deliverPass}
                  />
                  <Meta label="Clips" value={String(seq.clips)} ok />
                  <Meta label="Duration" value={`${seq.durationSec}s`} ok />
                </div>
                <div className="flex flex-wrap gap-2">
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={() => toast.message(`Chain QA dry-run: ${seq.name}`)}
                  >
                    Run chain QA
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() =>
                      toast.message(`Handoff packet draft: ${seq.name}`)
                    }
                  >
                    Build handoff
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() =>
                      toast.message(`Polish dry-run: ${seq.name}`)
                    }
                  >
                    Polish dry-run
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

function Meta({
  label,
  value,
  ok,
}: {
  label: string;
  value: string;
  ok?: boolean;
}) {
  return (
    <div className="rounded-md border border-border bg-bg-subtle/50 px-2.5 py-2">
      <p className="text-fg-subtle">{label}</p>
      <p className={ok ? "font-medium text-fg" : "font-medium text-warning"}>
        {value}
      </p>
    </div>
  );
}
