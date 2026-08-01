import { Check, Circle } from "lucide-react";
import { toast } from "sonner";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { BIBLE_STAGES, PROJECTS } from "@/lib/studio-data";
import { cn } from "@/lib/utils";
import { useState } from "react";

export function ProductionView() {
  const [title, setTitle] = useState("Neon Harbor");
  const [logline, setLogline] = useState(
    "A burned detective tracks a ghost freighter through rain-soaked docks while identity itself starts to slip.",
  );
  const [tone, setTone] = useState("Low-key neo-noir · restrained teal grade · wet practicals");
  const [pipeline, setPipeline] = useState<"1.0" | "1.5">("1.5");

  const done = BIBLE_STAGES.filter((s) => s.done).length;

  return (
    <div className="grid gap-4 lg:grid-cols-5">
      <div className="space-y-4 lg:col-span-3">
        <Card>
          <CardHeader>
            <CardTitle>Guided Production Bible</CardTitle>
            <CardDescription>
              Multi-stage wizard · CLI twin: cinematic-studio create-bible --wizard
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="mb-1.5 block text-xs font-medium text-fg-muted">
                Project title
              </label>
              <Input value={title} onChange={(e) => setTitle(e.target.value)} />
            </div>
            <div>
              <label className="mb-1.5 block text-xs font-medium text-fg-muted">
                Logline
              </label>
              <Textarea
                value={logline}
                onChange={(e) => setLogline(e.target.value)}
                className="min-h-24"
              />
            </div>
            <div>
              <label className="mb-1.5 block text-xs font-medium text-fg-muted">
                World & tone
              </label>
              <Input value={tone} onChange={(e) => setTone(e.target.value)} />
            </div>
            <div>
              <label className="mb-1.5 block text-xs font-medium text-fg-muted">
                Video pipeline
              </label>
              <div className="flex gap-2">
                {(["1.0", "1.5"] as const).map((p) => (
                  <button
                    key={p}
                    type="button"
                    onClick={() => setPipeline(p)}
                    className={cn(
                      "h-9 rounded-md border px-3 text-sm",
                      pipeline === p
                        ? "border-primary bg-primary text-primary-fg"
                        : "border-border bg-bg-elevated text-fg-muted",
                    )}
                  >
                    Imagine Video {p}
                    {p === "1.5" ? " + audio" : ""}
                  </button>
                ))}
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button
                onClick={() =>
                  toast.success("Bible stages saved (demo) — ready for DNA lock")
                }
              >
                Save bible draft
              </Button>
              <Button
                variant="secondary"
                onClick={() => toast.message("Bible lock requires schedule + budget stages")}
              >
                Lock bible
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="space-y-4 lg:col-span-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Stage progress</CardTitle>
            <CardDescription>
              {done}/{BIBLE_STAGES.length} complete
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {BIBLE_STAGES.map((s) => (
              <div
                key={s.id}
                className="flex items-center gap-2 rounded-md border border-border px-2.5 py-2 text-sm"
              >
                {s.done ? (
                  <Check className="size-3.5 text-success" />
                ) : (
                  <Circle className="size-3.5 text-fg-subtle" />
                )}
                <span className={s.done ? "text-fg" : "text-fg-muted"}>
                  {s.label}
                </span>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Projects with bible</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {PROJECTS.map((p) => (
              <div
                key={p.id}
                className="flex items-center justify-between rounded-md border border-border px-2.5 py-2 text-sm"
              >
                <span>{p.name}</span>
                <Badge variant={p.hasBible ? "ready" : "draft"}>
                  {p.hasBible ? "loaded" : "missing"}
                </Badge>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
