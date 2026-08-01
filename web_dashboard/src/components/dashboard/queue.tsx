import { ArrowUp, Ban, ListOrdered, RefreshCw } from "lucide-react";
import { toast } from "sonner";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { useStudioStore } from "@/lib/studio-store";
import { cn } from "@/lib/utils";

export function QueueView() {
  const queue = useStudioStore((s) => s.queue);
  const cancelQueueItem = useStudioStore((s) => s.cancelQueueItem);
  const promoteQueueItem = useStudioStore((s) => s.promoteQueueItem);
  const setView = useStudioStore((s) => s.setView);

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="flex-row items-start justify-between space-y-0">
          <div>
            <CardTitle>Render queue</CardTitle>
            <CardDescription>
              Priority order · rush jobs jump the line
            </CardDescription>
          </div>
          <Badge variant="default" className="tabular">
            {queue.length} active
          </Badge>
        </CardHeader>
        <CardContent className="space-y-3">
          {queue.length === 0 ? (
            <div className="flex flex-col items-center justify-center gap-3 py-14 text-center">
              <div className="flex size-12 items-center justify-center rounded-xl border border-border bg-bg-subtle">
                <ListOrdered className="size-5 text-fg-muted" />
              </div>
              <div>
                <p className="text-sm font-medium">Queue is empty</p>
                <p className="mt-1 text-sm text-fg-muted">
                  Compose a shot to add work to the render farm.
                </p>
              </div>
              <Button size="sm" onClick={() => setView("compose")}>
                Compose shot
              </Button>
            </div>
          ) : (
            queue.map((item, index) => (
              <div
                key={item.id}
                className="rounded-xl border border-border bg-bg-elevated p-4"
              >
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="tabular text-xs text-fg-subtle">
                        #{index + 1}
                      </span>
                      <h3 className="truncate text-sm font-semibold">
                        {item.title}
                      </h3>
                      <span
                        className={cn(
                          "rounded-full border px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide",
                          item.priority === "rush"
                            ? "border-danger/30 bg-danger/10 text-danger"
                            : item.priority === "high"
                              ? "border-warning/30 bg-warning/10 text-warning"
                              : "border-border bg-bg-subtle text-fg-muted",
                        )}
                      >
                        {item.priority}
                      </span>
                    </div>
                    <p className="mt-1 text-xs text-fg-muted">{item.stage}</p>
                  </div>
                  <div className="flex shrink-0 gap-1.5">
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => {
                        promoteQueueItem(item.id);
                        toast.success("Promoted to rush");
                      }}
                    >
                      <ArrowUp className="size-3.5" />
                      Rush
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        cancelQueueItem(item.id);
                        toast.message("Job cancelled");
                      }}
                    >
                      <Ban className="size-3.5" />
                      Cancel
                    </Button>
                  </div>
                </div>
                <div className="mt-3">
                  <div className="mb-1.5 flex justify-between text-xs">
                    <span className="tabular text-fg-muted">{item.progress}%</span>
                    <span className="tabular text-fg-subtle">
                      ETA {formatEta(item.etaSeconds)}
                    </span>
                  </div>
                  <Progress value={item.progress} />
                </div>
              </div>
            ))
          )}
        </CardContent>
      </Card>

      <Card>
        <CardContent className="flex flex-col gap-3 p-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            <div className="flex size-9 items-center justify-center rounded-md border border-border bg-bg-subtle">
              <RefreshCw className="size-4 text-fg-muted" />
            </div>
            <div>
              <p className="text-sm font-medium">Farm health</p>
              <p className="text-xs text-fg-muted">
                12 workers · region us-east · latency 38ms
              </p>
            </div>
          </div>
          <div className="flex gap-4 text-xs tabular text-fg-muted">
            <span>
              Throughput <strong className="text-fg">4.2</strong> /min
            </span>
            <span>
              Retry rate <strong className="text-fg">1.8%</strong>
            </span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function formatEta(seconds: number) {
  if (seconds < 60) return `${seconds}s`;
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}m ${s}s`;
}
