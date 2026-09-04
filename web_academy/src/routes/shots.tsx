import { createFileRoute, Link } from "@tanstack/react-router";
import { ListVideo, Plus, RotateCcw, Trash2 } from "lucide-react";
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
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/shots")({
  component: ShotsPage,
});

type Shot = {
  id: string;
  code: string;
  title: string;
  framing: string;
  action: string;
  camera: string;
  notes: string;
  priority: "hero" | "support" | "draft";
};

type Preset = {
  id: string;
  label: string;
  project: string;
  characterId: string;
  shots: Omit<Shot, "id">[];
};

const PRESETS: Preset[] = [
  {
    id: "neon",
    label: "Neon alley 3-shot",
    project: "Neon Courier teaser",
    characterId: "lead_01",
    shots: [
      {
        code: "A01",
        title: "Wide establish",
        framing: "wide · eye-level",
        action: "Lead at alley mouth; rain; neon signs readable",
        camera: "35mm anamorphic · slow locked-off",
        notes: "DNA inject · standard still first",
        priority: "support",
      },
      {
        code: "A02",
        title: "Medium courier",
        framing: "medium · eye-level",
        action: "Bag left, messenger bag, wet jacket sheen",
        camera: "35mm · slight push option later",
        notes: "Hero plate candidate",
        priority: "hero",
      },
      {
        code: "A03",
        title: "Close identity",
        framing: "close · eye-level",
        action: "Face lock check — scar, hair, eyes",
        camera: "50mm · shallow DOF",
        notes: "Identity gate still",
        priority: "hero",
      },
    ],
  },
  {
    id: "hall",
    label: "Candle hall pair",
    project: "Candle Hall study",
    characterId: "lead_02",
    shots: [
      {
        code: "B01",
        title: "Corridor wide",
        framing: "medium-wide · slight dutch",
        action: "Candle right hand; peeling wallpaper both sides",
        camera: "24mm · hold",
        notes: "Prop hand-side locked",
        priority: "support",
      },
      {
        code: "B02",
        title: "Face + flame",
        framing: "medium close · eye-level",
        action: "Warm candle key on face; blue fill in depth",
        camera: "35mm · static",
        notes: "Hero plate for optional 6s hold",
        priority: "hero",
      },
    ],
  },
];

function uid() {
  return Math.random().toString(36).slice(2, 9);
}

function emptyShot(index: number): Shot {
  const n = String(index + 1).padStart(2, "0");
  return {
    id: uid(),
    code: `S${n}`,
    title: "New shot",
    framing: "medium · eye-level",
    action: "",
    camera: "35mm",
    notes: "DNA inject on packet",
    priority: "draft",
  };
}

function buildShotList(
  project: string,
  characterId: string,
  shots: Shot[],
) {
  const lines = [
    `# SHOT LIST — ${project}`,
    `character_id: ${characterId}`,
    `count: ${shots.length}`,
    `rule: CHARACTER_DNA inject on every packet · stills before video`,
    "",
  ];
  shots.forEach((s, i) => {
    lines.push(
      `## ${s.code} — ${s.title}`,
      `priority: ${s.priority}`,
      `framing: ${s.framing}`,
      `action: ${s.action || "—"}`,
      `camera: ${s.camera}`,
      `notes: ${s.notes || "—"}`,
      `order: ${i + 1}`,
      "",
    );
  });
  lines.push("[/SHOT_LIST]");
  return lines.join("\n");
}

function buildActivation(list: string, project: string) {
  return `ACTIVATE STUDIO_DIRECTOR
ACTIVATE IMAGINE_PROMPT_MASTER
ACTIVATE QUOTA_OPTIMIZER

Task: execute stills-first shot list for "${project}".
Order: draft support stills → hero plates → identity gate → optional video only on locked heroes.

${list}

Output: one Imagine packet per shot (DNA prepended), mark plate candidates.`;
}

function ShotsPage() {
  const [presetId, setPresetId] = useState(PRESETS[0].id);
  const [project, setProject] = useState(PRESETS[0].project);
  const [characterId, setCharacterId] = useState(PRESETS[0].characterId);
  const [shots, setShots] = useState<Shot[]>(() =>
    PRESETS[0].shots.map((s) => ({ ...s, id: uid() })),
  );

  const list = useMemo(
    () => buildShotList(project, characterId, shots),
    [project, characterId, shots],
  );
  const activation = useMemo(
    () => buildActivation(list, project),
    [list, project],
  );

  const heroes = shots.filter((s) => s.priority === "hero").length;
  const drafts = shots.filter((s) => s.priority === "draft").length;

  function applyPreset(id: string) {
    const p = PRESETS.find((x) => x.id === id);
    if (!p) return;
    setPresetId(p.id);
    setProject(p.project);
    setCharacterId(p.characterId);
    setShots(p.shots.map((s) => ({ ...s, id: uid() })));
  }

  function updateShot(id: string, patch: Partial<Shot>) {
    setShots((prev) => prev.map((s) => (s.id === id ? { ...s, ...patch } : s)));
  }

  function removeShot(id: string) {
    setShots((prev) => prev.filter((s) => s.id !== id));
  }

  function addShot() {
    setShots((prev) => [...prev, emptyShot(prev.length)]);
  }

  function move(id: string, dir: -1 | 1) {
    setShots((prev) => {
      const i = prev.findIndex((s) => s.id === id);
      if (i < 0) return prev;
      const j = i + dir;
      if (j < 0 || j >= prev.length) return prev;
      const next = [...prev];
      [next[i], next[j]] = [next[j], next[i]];
      return next;
    });
  }

  const fieldClass =
    "mt-1 w-full rounded-md border border-border bg-bg px-2.5 py-2 text-sm text-fg outline-none focus:border-border-strong focus:ring-2 focus:ring-teal/30";

  return (
    <div className="space-y-8">
      <div>
        <Badge variant="teal">Planning</Badge>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">
          Shot list builder
        </h1>
        <p className="mt-2 max-w-2xl text-muted leading-relaxed">
          Turn a Bible into numbered stills — framing, action, camera, priority.
          Stills-first: mark heroes before any video spend.
        </p>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-xl border border-border bg-surface px-4 py-3">
          <p className="font-mono text-2xl text-teal">{shots.length}</p>
          <p className="text-xs text-muted uppercase tracking-wide">Shots</p>
        </div>
        <div className="rounded-xl border border-border bg-surface px-4 py-3">
          <p className="font-mono text-2xl text-teal">{heroes}</p>
          <p className="text-xs text-muted uppercase tracking-wide">Hero</p>
        </div>
        <div className="rounded-xl border border-border bg-surface px-4 py-3">
          <p className="font-mono text-2xl text-muted">{drafts}</p>
          <p className="text-xs text-muted uppercase tracking-wide">Draft</p>
        </div>
      </div>

      <div className="flex flex-wrap gap-1.5">
        {PRESETS.map((p) => (
          <button
            key={p.id}
            type="button"
            onClick={() => applyPreset(p.id)}
            className={cn(
              "h-9 rounded-md border px-3 text-xs font-medium",
              presetId === p.id
                ? "border-teal/40 bg-teal/10 text-teal"
                : "border-border bg-surface text-muted hover:text-fg",
            )}
          >
            {p.label}
          </button>
        ))}
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={() => applyPreset("neon")}
        >
          <RotateCcw className="h-3.5 w-3.5" />
          Reset
        </Button>
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        <label className="block text-xs font-medium text-subtle">
          Project
          <input
            value={project}
            onChange={(e) => setProject(e.target.value)}
            className={fieldClass}
          />
        </label>
        <label className="block text-xs font-medium text-subtle">
          Character ID
          <input
            value={characterId}
            onChange={(e) => setCharacterId(e.target.value)}
            className={fieldClass}
          />
        </label>
      </div>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1.05fr)_minmax(0,0.95fr)]">
        <div className="space-y-3">
          <div className="flex items-center justify-between gap-2">
            <h2 className="text-sm font-medium text-fg flex items-center gap-2">
              <ListVideo className="h-4 w-4 text-teal" />
              Shots
            </h2>
            <Button type="button" size="sm" variant="secondary" onClick={addShot}>
              <Plus className="h-3.5 w-3.5" />
              Add shot
            </Button>
          </div>

          {shots.length === 0 ? (
            <p className="rounded-xl border border-dashed border-border py-10 text-center text-sm text-muted">
              No shots — add one or load a preset.
            </p>
          ) : (
            shots.map((s, i) => (
              <Card key={s.id}>
                <CardHeader className="pb-2">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs text-teal">
                        {String(i + 1).padStart(2, "0")}
                      </span>
                      <Badge
                        variant={
                          s.priority === "hero"
                            ? "teal"
                            : s.priority === "support"
                              ? "outline"
                              : "default"
                        }
                      >
                        {s.priority}
                      </Badge>
                    </div>
                    <div className="flex gap-1">
                      <Button
                        type="button"
                        size="sm"
                        variant="ghost"
                        onClick={() => move(s.id, -1)}
                        aria-label="Move up"
                      >
                        ↑
                      </Button>
                      <Button
                        type="button"
                        size="sm"
                        variant="ghost"
                        onClick={() => move(s.id, 1)}
                        aria-label="Move down"
                      >
                        ↓
                      </Button>
                      <Button
                        type="button"
                        size="sm"
                        variant="ghost"
                        onClick={() => removeShot(s.id)}
                        aria-label="Remove shot"
                      >
                        <Trash2 className="h-3.5 w-3.5 text-danger" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="grid gap-2 sm:grid-cols-2">
                  <label className="text-xs text-subtle">
                    Code
                    <input
                      value={s.code}
                      onChange={(e) =>
                        updateShot(s.id, { code: e.target.value })
                      }
                      className={fieldClass}
                    />
                  </label>
                  <label className="text-xs text-subtle">
                    Priority
                    <select
                      value={s.priority}
                      onChange={(e) =>
                        updateShot(s.id, {
                          priority: e.target.value as Shot["priority"],
                        })
                      }
                      className={fieldClass}
                    >
                      <option value="hero">hero</option>
                      <option value="support">support</option>
                      <option value="draft">draft</option>
                    </select>
                  </label>
                  <label className="text-xs text-subtle sm:col-span-2">
                    Title
                    <input
                      value={s.title}
                      onChange={(e) =>
                        updateShot(s.id, { title: e.target.value })
                      }
                      className={fieldClass}
                    />
                  </label>
                  <label className="text-xs text-subtle">
                    Framing
                    <input
                      value={s.framing}
                      onChange={(e) =>
                        updateShot(s.id, { framing: e.target.value })
                      }
                      className={fieldClass}
                    />
                  </label>
                  <label className="text-xs text-subtle">
                    Camera
                    <input
                      value={s.camera}
                      onChange={(e) =>
                        updateShot(s.id, { camera: e.target.value })
                      }
                      className={fieldClass}
                    />
                  </label>
                  <label className="text-xs text-subtle sm:col-span-2">
                    Action
                    <textarea
                      value={s.action}
                      onChange={(e) =>
                        updateShot(s.id, { action: e.target.value })
                      }
                      rows={2}
                      className={cn(fieldClass, "resize-y")}
                    />
                  </label>
                  <label className="text-xs text-subtle sm:col-span-2">
                    Notes
                    <input
                      value={s.notes}
                      onChange={(e) =>
                        updateShot(s.id, { notes: e.target.value })
                      }
                      className={fieldClass}
                    />
                  </label>
                </CardContent>
              </Card>
            ))
          )}
        </div>

        <div className="space-y-4 lg:sticky lg:top-20 lg:self-start">
          <Card className="border-teal/20">
            <CardHeader>
              <div className="flex items-start justify-between gap-2">
                <div>
                  <CardTitle className="text-base">Shot list export</CardTitle>
                  <CardDescription>
                    Paste after Bible + DNA
                  </CardDescription>
                </div>
                <CopyButton text={list} label="Copy list" />
              </div>
            </CardHeader>
            <CardContent>
              <pre className="max-h-[280px] overflow-auto whitespace-pre-wrap rounded-lg border border-border bg-bg p-3.5 font-mono text-[11px] leading-relaxed text-muted">
                {list}
              </pre>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-start justify-between gap-2">
                <div>
                  <CardTitle className="text-base">Activation pack</CardTitle>
                  <CardDescription>
                    Director → Prompt Master → Quota
                  </CardDescription>
                </div>
                <CopyButton text={activation} label="Copy pack" />
              </div>
            </CardHeader>
            <CardContent>
              <pre className="max-h-48 overflow-auto whitespace-pre-wrap rounded-lg border border-border bg-bg p-3.5 font-mono text-[11px] leading-relaxed text-muted">
                {activation}
              </pre>
              <div className="mt-3 flex flex-wrap gap-2 text-xs">
                <Link to="/bible" className="text-teal hover:underline">
                  Bible
                </Link>
                <Link to="/dna" className="text-teal hover:underline">
                  DNA
                </Link>
                <Link to="/lab" className="text-teal hover:underline">
                  Prompt lab
                </Link>
                <Link to="/budget" className="text-teal hover:underline">
                  Budget
                </Link>
                <Link to="/scenarios" className="text-teal hover:underline">
                  Scenarios
                </Link>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Shoot order tip</CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-muted space-y-2">
              <p>
                Generate <strong className="text-fg">draft/support</strong>{" "}
                stills first on the standard image model.
              </p>
              <p>
                Promote only <strong className="text-fg">hero</strong> plates
                to Image 2.0 (`quality=medium`) or video after identity gate.
              </p>
              <p>
                Estimate cost in Budget: shots × still rate (+ video only for
                locked heroes).
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
