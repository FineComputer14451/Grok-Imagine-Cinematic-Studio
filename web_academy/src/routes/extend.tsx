import { createFileRoute, Link } from "@tanstack/react-router";
import {
  AlertTriangle,
  Check,
  Circle,
  ExternalLink,
  GitBranch,
  Plus,
  RotateCcw,
  Trash2,
} from "lucide-react";
import { useMemo, useState } from "react";
import { CopyButton } from "@/components/copy-button";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  blockersOk,
  buildChainPacket,
  buildDirectorBrief,
  clipsFromPreset,
  emptyClip,
  EXTEND_PRESETS,
  EXTEND_RULES,
  totalSeconds,
  type ExtendClip,
} from "@/data/extend";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/extend")({
  component: ExtendPage,
});

const DURATIONS = [4, 6, 8, 10] as const;
const PLATES = ["draft", "locked", "n/a"] as const;

const fieldClass =
  "mt-1.5 w-full rounded-lg border border-border bg-bg px-3 py-2.5 text-sm text-fg placeholder:text-subtle outline-none focus:border-border-strong focus:ring-2 focus:ring-teal/30";

function ExtendPage() {
  const [presetId, setPresetId] = useState(EXTEND_PRESETS[0].id);
  const [project, setProject] = useState(EXTEND_PRESETS[0].project);
  const [characterId, setCharacterId] = useState(
    EXTEND_PRESETS[0].characterId,
  );
  const [clips, setClips] = useState<ExtendClip[]>(() =>
    clipsFromPreset(EXTEND_PRESETS[0]),
  );
  const [openId, setOpenId] = useState<string | null>(null);

  const secs = useMemo(() => totalSeconds(clips), [clips]);
  const gate = useMemo(() => blockersOk(clips), [clips]);
  const packet = useMemo(
    () => buildChainPacket({ project, characterId, clips }),
    [project, characterId, clips],
  );
  const brief = useMemo(
    () => buildDirectorBrief({ project, characterId, clips }),
    [project, characterId, clips],
  );

  function applyPreset(id: string) {
    const p = EXTEND_PRESETS.find((x) => x.id === id);
    if (!p) return;
    setPresetId(p.id);
    setProject(p.project);
    setCharacterId(p.characterId);
    const next = clipsFromPreset(p);
    setClips(next);
    setOpenId(next[0]?.id ?? null);
  }

  function updateClip(id: string, patch: Partial<ExtendClip>) {
    setClips((list) =>
      list.map((c) => (c.id === id ? { ...c, ...patch } : c)),
    );
  }

  function addClip() {
    setClips((list) => {
      const next = emptyClip(list.length);
      setOpenId(next.id);
      return [...list, next];
    });
  }

  function removeClip(id: string) {
    setClips((list) => {
      const next = list.filter((c) => c.id !== id);
      if (openId === id) setOpenId(next[0]?.id ?? null);
      return next;
    });
  }

  function resetChain() {
    applyPreset(presetId);
  }

  const active =
    clips.find((c) => c.id === openId) ?? clips[0] ?? null;

  return (
    <div className="space-y-8">
      <div>
        <Badge variant="teal">Sequence</Badge>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">
          Extend Lab
        </h1>
        <p className="mt-2 max-w-2xl text-muted leading-relaxed">
          Plan multi-clip{" "}
          <Link to="/glossary" className="text-teal hover:underline">
            Extend-from-Frame
          </Link>{" "}
          chains — plate gates, one move per clip, motion handoffs, then copy a
          director packet. Pairs with{" "}
          <Link to="/recap" className="text-teal hover:underline">
            last-frame recap
          </Link>{" "}
          and{" "}
          <Link to="/delivery" className="text-teal hover:underline">
            delivery
          </Link>
          .
        </p>
      </div>

      {/* Status bar */}
      <div className="rounded-xl border border-border bg-surface px-4 py-4">
        <div className="flex flex-wrap items-center justify-between gap-3 text-sm">
          <div className="flex flex-wrap items-center gap-2">
            <GitBranch className="h-4 w-4 text-teal" />
            <span className="text-muted">
              {clips.length} clip{clips.length === 1 ? "" : "s"} · ~{secs}s
            </span>
            {gate.ok ? (
              <Badge variant="teal" className="text-[11px]">
                Gates clear
              </Badge>
            ) : (
              <Badge variant="outline" className="text-[11px] text-amber">
                {gate.issues.length} gate issue
                {gate.issues.length === 1 ? "" : "s"}
              </Badge>
            )}
          </div>
          <div className="flex flex-wrap gap-2">
            <CopyButton text={brief} label="Copy brief" />
            <CopyButton text={packet} label="Copy chain packet" />
          </div>
        </div>
        {!gate.ok && (
          <ul className="mt-3 space-y-1.5 border-t border-border pt-3">
            {gate.issues.map((issue) => (
              <li
                key={issue}
                className="flex gap-2 text-sm text-amber"
              >
                <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                {issue}
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Presets */}
      <section className="space-y-3">
        <h2 className="text-sm font-medium text-fg">Chain presets</h2>
        <div className="grid gap-3 sm:grid-cols-3">
          {EXTEND_PRESETS.map((p) => (
            <button
              key={p.id}
              type="button"
              onClick={() => applyPreset(p.id)}
              className={cn(
                "rounded-xl border px-4 py-3.5 text-left transition-colors",
                presetId === p.id
                  ? "border-teal/50 bg-teal/5 ring-2 ring-teal/20"
                  : "border-border bg-surface hover:border-border-strong",
              )}
            >
              <p className="text-sm font-medium text-fg">{p.label}</p>
              <p className="mt-1 text-xs text-muted leading-relaxed">
                {p.blurb}
              </p>
              <p className="mt-2 font-mono text-[11px] text-teal">
                {p.clips.length} clips · {p.totalBudgetHint}
              </p>
            </button>
          ))}
        </div>
      </section>

      {/* Project meta */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Project</CardTitle>
          <CardDescription>
            Character id must match DNA inject blocks
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <label className="block text-sm">
            <span className="text-muted">Project title</span>
            <input
              value={project}
              onChange={(e) => setProject(e.target.value)}
              className={fieldClass}
            />
          </label>
          <label className="block text-sm">
            <span className="text-muted">Character ID</span>
            <input
              value={characterId}
              onChange={(e) => setCharacterId(e.target.value)}
              className={fieldClass}
            />
          </label>
        </CardContent>
      </Card>

      {/* Timeline */}
      <section className="space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h2 className="text-sm font-medium text-fg">Clip timeline</h2>
          <div className="flex flex-wrap gap-2">
            <Button type="button" variant="secondary" size="sm" onClick={addClip}>
              <Plus className="h-3.5 w-3.5" />
              Add clip
            </Button>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={resetChain}
            >
              <RotateCcw className="h-3.5 w-3.5" />
              Reset preset
            </Button>
          </div>
        </div>

        <div className="flex gap-2 overflow-x-auto pb-1">
          {clips.map((c, i) => {
            const selected = active?.id === c.id;
            return (
              <button
                key={c.id}
                type="button"
                onClick={() => setOpenId(c.id)}
                className={cn(
                  "min-w-[9.5rem] shrink-0 rounded-xl border px-3 py-3 text-left transition-colors",
                  selected
                    ? "border-teal/50 bg-teal/10"
                    : "border-border bg-surface hover:border-border-strong",
                )}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="font-mono text-[11px] text-teal">
                    {String(i + 1).padStart(2, "0")}
                  </span>
                  <span
                    className={cn(
                      "rounded px-1.5 py-0.5 text-[10px] uppercase tracking-wide",
                      c.plateStatus === "locked"
                        ? "bg-success/15 text-success"
                        : c.plateStatus === "draft"
                          ? "bg-amber/15 text-amber"
                          : "bg-elevated text-subtle",
                    )}
                  >
                    {c.plateStatus}
                  </span>
                </div>
                <p className="mt-1.5 truncate text-sm font-medium text-fg">
                  {c.title}
                </p>
                <p className="mt-0.5 font-mono text-[11px] text-muted">
                  {c.code} · {c.duration}s
                </p>
              </button>
            );
          })}
        </div>

        {active ? (
          <Card>
            <CardHeader className="flex-row items-start justify-between gap-3 space-y-0">
              <div>
                <CardTitle className="text-base">{active.title}</CardTitle>
                <CardDescription className="font-mono text-xs">
                  {active.code}
                </CardDescription>
              </div>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => removeClip(active.id)}
                disabled={clips.length <= 1}
                aria-label="Remove clip"
              >
                <Trash2 className="h-3.5 w-3.5" />
              </Button>
            </CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-2">
              <label className="block text-sm sm:col-span-1">
                <span className="text-muted">Title</span>
                <input
                  value={active.title}
                  onChange={(e) =>
                    updateClip(active.id, { title: e.target.value })
                  }
                  className={fieldClass}
                />
              </label>
              <label className="block text-sm">
                <span className="text-muted">Code</span>
                <input
                  value={active.code}
                  onChange={(e) =>
                    updateClip(active.id, { code: e.target.value })
                  }
                  className={fieldClass}
                />
              </label>
              <div className="text-sm">
                <span className="text-muted">Duration (s)</span>
                <div className="mt-1.5 flex flex-wrap gap-1.5">
                  {DURATIONS.map((d) => (
                    <button
                      key={d}
                      type="button"
                      onClick={() => updateClip(active.id, { duration: d })}
                      className={cn(
                        "inline-flex h-10 min-w-12 items-center justify-center rounded-lg border px-3 text-sm font-mono transition-colors",
                        active.duration === d
                          ? "border-teal/50 bg-teal/10 text-fg"
                          : "border-border bg-bg text-muted hover:border-border-strong",
                      )}
                    >
                      {d}
                    </button>
                  ))}
                </div>
              </div>
              <div className="text-sm">
                <span className="text-muted">Plate status</span>
                <div className="mt-1.5 flex flex-wrap gap-1.5">
                  {PLATES.map((p) => (
                    <button
                      key={p}
                      type="button"
                      onClick={() =>
                        updateClip(active.id, { plateStatus: p })
                      }
                      className={cn(
                        "inline-flex h-10 items-center justify-center rounded-lg border px-3 text-sm capitalize transition-colors",
                        active.plateStatus === p
                          ? "border-teal/50 bg-teal/10 text-fg"
                          : "border-border bg-bg text-muted hover:border-border-strong",
                      )}
                    >
                      {p}
                    </button>
                  ))}
                </div>
              </div>
              <label className="block text-sm sm:col-span-2">
                <span className="text-muted">Framing</span>
                <input
                  value={active.framing}
                  onChange={(e) =>
                    updateClip(active.id, { framing: e.target.value })
                  }
                  className={fieldClass}
                />
              </label>
              <label className="block text-sm sm:col-span-2">
                <span className="text-muted">Action</span>
                <textarea
                  value={active.action}
                  onChange={(e) =>
                    updateClip(active.id, { action: e.target.value })
                  }
                  rows={2}
                  className={fieldClass}
                />
              </label>
              <label className="block text-sm">
                <span className="text-muted">Primary move (one only)</span>
                <input
                  value={active.move}
                  onChange={(e) =>
                    updateClip(active.id, { move: e.target.value })
                  }
                  className={fieldClass}
                />
              </label>
              <label className="block text-sm">
                <span className="text-muted">Emotion</span>
                <input
                  value={active.emotion}
                  onChange={(e) =>
                    updateClip(active.id, { emotion: e.target.value })
                  }
                  className={fieldClass}
                />
              </label>
              <label className="block text-sm">
                <span className="text-muted">Motion in</span>
                <textarea
                  value={active.motionIn}
                  onChange={(e) =>
                    updateClip(active.id, { motionIn: e.target.value })
                  }
                  rows={2}
                  className={fieldClass}
                />
              </label>
              <label className="block text-sm">
                <span className="text-muted">Motion out → next recap</span>
                <textarea
                  value={active.motionOut}
                  onChange={(e) =>
                    updateClip(active.id, { motionOut: e.target.value })
                  }
                  rows={2}
                  className={fieldClass}
                />
              </label>
              <label className="block text-sm sm:col-span-2">
                <span className="text-muted">Notes</span>
                <input
                  value={active.notes}
                  onChange={(e) =>
                    updateClip(active.id, { notes: e.target.value })
                  }
                  className={fieldClass}
                />
              </label>
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardContent className="py-8 text-center text-sm text-muted">
              Add a clip to start the chain.
            </CardContent>
          </Card>
        )}
      </section>

      {/* Rules */}
      <section className="space-y-3">
        <h2 className="text-sm font-medium text-fg">Extend rules</h2>
        <div className="grid gap-2 sm:grid-cols-2">
          {EXTEND_RULES.map((r) => (
            <div
              key={r.id}
              className="rounded-xl border border-border bg-surface px-4 py-3"
            >
              <div className="flex items-start gap-2">
                {r.severity === "blocker" ? (
                  <Circle className="mt-0.5 h-3.5 w-3.5 shrink-0 text-amber" />
                ) : r.severity === "craft" ? (
                  <Check className="mt-0.5 h-3.5 w-3.5 shrink-0 text-teal" />
                ) : (
                  <Circle className="mt-0.5 h-3.5 w-3.5 shrink-0 text-subtle" />
                )}
                <div>
                  <p className="text-sm font-medium text-fg">{r.title}</p>
                  <p className="mt-0.5 text-xs text-muted">{r.short}</p>
                  <p className="mt-1.5 text-xs leading-relaxed text-subtle">
                    {r.body}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Packet preview */}
      <Card>
        <CardHeader className="flex-row items-start justify-between gap-3 space-y-0">
          <div>
            <CardTitle className="text-base">Chain packet</CardTitle>
            <CardDescription>
              Paste into Studio chat or save with your project pack
            </CardDescription>
          </div>
          <CopyButton text={packet} label="Copy packet" />
        </CardHeader>
        <CardContent>
          <pre className="max-h-80 overflow-auto rounded-lg border border-border bg-bg p-4 font-mono text-xs leading-relaxed text-muted whitespace-pre-wrap">
            {packet}
          </pre>
        </CardContent>
      </Card>

      {/* Related tools */}
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {[
          {
            to: "/recap" as const,
            label: "Last-frame recap",
            why: "Write motion_out handoffs",
          },
          {
            to: "/consistency" as const,
            label: "Consistency",
            why: "Plate · extend · chain QA",
          },
          {
            to: "/dna" as const,
            label: "Character DNA",
            why: "Inject every packet",
          },
          {
            to: "/delivery" as const,
            label: "Delivery",
            why: "Ship gate before stitch",
          },
        ].map((t) => (
          <Link
            key={t.to}
            to={t.to}
            className="group flex items-center justify-between gap-2 rounded-xl border border-border bg-surface px-4 py-3 transition-colors hover:border-border-strong"
          >
            <div>
              <p className="text-sm font-medium text-fg">{t.label}</p>
              <p className="text-xs text-muted">{t.why}</p>
            </div>
            <ExternalLink className="h-3.5 w-3.5 shrink-0 text-subtle group-hover:text-teal" />
          </Link>
        ))}
      </div>
    </div>
  );
}
