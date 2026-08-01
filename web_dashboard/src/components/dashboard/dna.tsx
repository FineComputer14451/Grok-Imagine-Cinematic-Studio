import { Lock, Unlock } from "lucide-react";
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
import { formatRelative } from "@/lib/utils";

export function DnaView() {
  const characters = useStudioStore((s) => s.characters);
  const lockCharacter = useStudioStore((s) => s.lockCharacter);
  const search = useStudioStore((s) => s.search);
  const apiSource = useStudioStore((s) => s.apiSource);

  const filtered = characters.filter((c) => {
    const q = search.trim().toLowerCase();
    if (!q) return true;
    return (
      c.name.toLowerCase().includes(q) ||
      c.role.toLowerCase().includes(q) ||
      c.looks.toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-4">
      <p className="text-xs text-fg-muted">
        DNA source: <strong className="text-fg">{apiSource}</strong> · lock
        calls <code className="text-fg-subtle">POST /api/v1/dna/lock</code>
      </p>
      <div className="grid gap-3 sm:grid-cols-3">
        <Card>
          <CardContent className="p-4">
            <p className="text-xs text-fg-muted">Profiles</p>
            <p className="mt-1 text-2xl font-semibold tabular">
              {characters.length}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-xs text-fg-muted">Locked</p>
            <p className="mt-1 text-2xl font-semibold tabular">
              {characters.filter((c) => c.locked).length}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-xs text-fg-muted">Mean drift</p>
            <p className="mt-1 text-2xl font-semibold tabular">
              {(
                characters.reduce((a, c) => a + c.driftScore, 0) /
                Math.max(1, characters.length)
              ).toFixed(2)}
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-3 lg:grid-cols-2">
        {filtered.map((c) => {
          const project = PROJECTS.find((p) => p.id === c.projectId);
          return (
            <Card key={c.id}>
              <CardHeader className="flex-row items-start justify-between space-y-0">
                <div>
                  <CardTitle className="text-base">{c.name}</CardTitle>
                  <CardDescription>
                    {c.role}
                    {project ? ` · ${project.name}` : ""}
                  </CardDescription>
                </div>
                <Badge variant={c.locked ? "ready" : "queued"}>
                  {c.locked ? "locked" : "unlocked"}
                </Badge>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm text-fg-muted">{c.looks}</p>
                <div className="flex flex-wrap gap-1.5">
                  {c.traits.map((t) => (
                    <Badge key={t}>{t}</Badge>
                  ))}
                </div>
                <div className="flex items-center justify-between text-xs text-fg-subtle">
                  <span>
                    Drift{" "}
                    <strong className="tabular text-fg">
                      {c.driftScore.toFixed(2)}
                    </strong>
                  </span>
                  <span>{formatRelative(new Date(c.updatedAt))}</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {!c.locked ? (
                    <Button
                      size="sm"
                      onClick={() => {
                        void lockCharacter(c.id).then(() =>
                          toast.success(`${c.name} identity locked`),
                        );
                      }}
                    >
                      <Lock className="size-3.5" />
                      Lock DNA
                    </Button>
                  ) : (
                    <Button size="sm" variant="secondary" disabled>
                      <Lock className="size-3.5" />
                      Locked
                    </Button>
                  )}
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() =>
                      toast.message("Injection block copied (demo)")
                    }
                  >
                    <Unlock className="size-3.5" />
                    Inject block
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
