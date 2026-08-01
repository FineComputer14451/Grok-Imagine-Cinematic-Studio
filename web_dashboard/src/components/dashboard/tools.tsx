import { Copy, ExternalLink } from "lucide-react";
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
import {
  ACTIVATION,
  MODEL_STACK,
  SPECIALISTS,
  STUDIO_VERSION,
} from "@/lib/studio-data";
import { useStudioStore } from "@/lib/studio-store";

export function ToolsView() {
  const runHealthAction = useStudioStore((s) => s.runHealthAction);
  const healthLog = useStudioStore((s) => s.healthLog);

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Activation</CardTitle>
          <CardDescription>
            Paste in Grok chat to load the v{STUDIO_VERSION} department
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <code className="block rounded-lg border border-border bg-bg-subtle px-3 py-2.5 text-sm text-fg">
            {ACTIVATION}
          </code>
          <Button
            size="sm"
            variant="secondary"
            onClick={() => {
              void navigator.clipboard?.writeText(ACTIVATION);
              toast.success("Activation phrase copied");
            }}
          >
            <Copy className="size-3.5" />
            Copy activation
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Model stack</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
          {Object.entries(MODEL_STACK).map(([k, v]) => (
            <div
              key={k}
              className="rounded-md border border-border bg-bg-subtle/50 px-3 py-2"
            >
              <p className="text-xs capitalize text-fg-subtle">{k}</p>
              <p className="mt-0.5 text-sm font-medium">{v}</p>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Specialists</CardTitle>
          <CardDescription>Core SFW department (demo roster)</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-2 sm:grid-cols-2">
          {SPECIALISTS.map((s) => (
            <div
              key={s.id}
              className="rounded-lg border border-border px-3 py-2.5"
            >
              <div className="flex items-center justify-between gap-2">
                <p className="text-sm font-medium">{s.name}</p>
                <Badge
                  variant={
                    s.status === "active"
                      ? "ready"
                      : s.status === "standby"
                        ? "queued"
                        : "default"
                  }
                >
                  {s.status}
                </Badge>
              </div>
              <p className="mt-1 text-xs text-fg-muted">{s.focus}</p>
              <button
                type="button"
                className="mt-2 text-left font-mono text-[11px] text-fg-subtle hover:text-fg"
                onClick={() => {
                  void navigator.clipboard?.writeText(s.activation);
                  toast.success("Activation copied");
                }}
              >
                {s.activation}
              </button>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">CLI health</CardTitle>
          <CardDescription>
            Simulated safe commands · full CLI in the Python repo
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex flex-wrap gap-2">
            {["doctor", "validate", "quota-sync", "models"].map((a) => (
              <Button
                key={a}
                size="sm"
                variant="secondary"
                onClick={() => runHealthAction(a)}
              >
                {a}
              </Button>
            ))}
            <Button size="sm" variant="outline" asChild>
              <a
                href="https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio"
                target="_blank"
                rel="noreferrer"
              >
                <ExternalLink className="size-3.5" />
                Open repo
              </a>
            </Button>
          </div>
          {healthLog && (
            <pre className="overflow-x-auto rounded-lg border border-border bg-bg-subtle p-3 font-mono text-xs text-fg-muted whitespace-pre-wrap">
              {healthLog.out}
            </pre>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
