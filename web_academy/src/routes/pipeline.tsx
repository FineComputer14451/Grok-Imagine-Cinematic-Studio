import { createFileRoute } from "@tanstack/react-router";
import { ArrowDown } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { PIPELINE } from "@/data/studio";

export const Route = createFileRoute("/pipeline")({
  component: PipelinePage,
});

function PipelinePage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">
          Production pipeline
        </h1>
        <p className="mt-2 max-w-2xl text-muted">
          How a full Tier 3 production moves from concept to delivery inside
          Cinematic Studio. Each stage has a gate — skip none if you want
          identity and continuity to hold.
        </p>
      </div>

      <div className="mx-auto max-w-2xl">
        <ol className="space-y-0">
          {PIPELINE.map((stage, i) => (
            <li key={stage.id} className="relative">
              <Card className="relative z-10">
                <CardHeader className="flex-row items-start gap-4 space-y-0">
                  <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-border bg-elevated font-mono text-sm font-semibold text-teal">
                    {String(i + 1).padStart(2, "0")}
                  </span>
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <CardTitle className="text-base">{stage.label}</CardTitle>
                      {i === 0 && <Badge variant="teal">Start here</Badge>}
                      {i === PIPELINE.length - 1 && (
                        <Badge variant="accent">Ship</Badge>
                      )}
                    </div>
                    <CardDescription className="mt-1">
                      {stage.detail}
                    </CardDescription>
                  </div>
                </CardHeader>
              </Card>
              {i < PIPELINE.length - 1 && (
                <div className="flex justify-center py-2" aria-hidden>
                  <ArrowDown className="h-4 w-4 text-subtle" />
                </div>
              )}
            </li>
          ))}
        </ol>
      </div>

      <Card className="bg-elevated/30">
        <CardHeader>
          <CardTitle className="text-base">Dual video stack</CardTitle>
          <CardDescription>
            Imagine Video 1.0 is the default. Use 1.5 when you need native
            synchronized audio, stronger physics, or intimacy-safe R-rated
            motion. Set this in VIDEO_PIPELINE_SPEC inside the Production Bible.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-lg border border-border bg-bg p-4">
              <p className="text-sm font-medium">Video 1.0</p>
              <p className="mt-1 text-sm text-muted">
                Reliable baseline clips, Extend-from-Frame chaining, broad
                prompt coverage.
              </p>
            </div>
            <div className="rounded-lg border border-teal/30 bg-teal/5 p-4">
              <p className="text-sm font-medium text-teal">Video 1.5</p>
              <p className="mt-1 text-sm text-muted">
                Native audio, improved physics, 1080p, image/voice references
                for identity lock.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
