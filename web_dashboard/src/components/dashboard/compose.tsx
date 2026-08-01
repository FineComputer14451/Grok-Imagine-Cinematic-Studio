import {
  Aperture,
  Camera,
  Clapperboard,
  Film,
  ImageIcon,
  Sparkles,
  Wand2,
} from "lucide-react";
import { toast } from "sonner";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  CAMERA_PRESETS,
  GRADE_PRESETS,
  LENS_PRESETS,
  PROJECTS,
  type AspectRatio,
  type ModelTier,
  type OutputMode,
} from "@/lib/studio-data";
import { useStudioStore } from "@/lib/studio-store";
import { cn } from "@/lib/utils";
import { ShotFrame } from "./shot-frame";

const MODES: { id: OutputMode; label: string; icon: typeof ImageIcon }[] = [
  { id: "image", label: "Still", icon: ImageIcon },
  { id: "video", label: "Video", icon: Film },
  { id: "storyboard", label: "Board", icon: Clapperboard },
];

const ASPECTS: AspectRatio[] = ["16:9", "2.39:1", "9:16", "1:1", "4:3"];
const MODELS: { id: ModelTier; label: string; hint: string }[] = [
  { id: "imagine", label: "Imagine", hint: "Fast drafts" },
  { id: "imagine-pro", label: "Imagine Pro", hint: "Higher fidelity" },
  { id: "cinematic", label: "Cinematic", hint: "Film-grade plates" },
];

const PROMPT_CHIPS = [
  "volumetric god rays",
  "anamorphic lens flare",
  "shallow DOF",
  "practical neon",
  "35mm film grain",
  "golden hour",
];

export function ComposeView() {
  const draft = useStudioStore((s) => s.draft);
  const updateDraft = useStudioStore((s) => s.updateDraft);
  const submitDraft = useStudioStore((s) => s.submitDraft);

  const onGenerate = () => {
    if (!draft.prompt.trim()) {
      toast.error("Add a prompt before generating");
      return;
    }
    submitDraft();
    toast.success("Shot queued for render");
  };

  return (
    <div className="grid gap-4 xl:grid-cols-5">
      <div className="space-y-4 xl:col-span-3">
        <Card>
          <CardHeader>
            <CardTitle>Shot brief</CardTitle>
            <CardDescription>
              Describe the frame, camera move, and light. The studio locks identity and grade across takes.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="mb-1.5 block text-xs font-medium text-fg-muted">
                Prompt
              </label>
              <Textarea
                value={draft.prompt}
                onChange={(e) => updateDraft({ prompt: e.target.value })}
                placeholder="Cinematic wide shot of a rain-soaked harbor at night, neon reflections, anamorphic flares…"
                className="min-h-36"
              />
              <div className="mt-2 flex flex-wrap gap-1.5">
                {PROMPT_CHIPS.map((chip) => (
                  <button
                    key={chip}
                    type="button"
                    onClick={() =>
                      updateDraft({
                        prompt: draft.prompt
                          ? `${draft.prompt.trim()}, ${chip}`
                          : chip,
                      })
                    }
                    className="rounded-full border border-border bg-bg-subtle px-2.5 py-1 text-xs text-fg-muted transition-colors hover:border-border-strong hover:text-fg"
                  >
                    {chip}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="mb-1.5 block text-xs font-medium text-fg-muted">
                Negative / avoid
              </label>
              <Input
                value={draft.negative}
                onChange={(e) => updateDraft({ negative: e.target.value })}
              />
            </div>

            <div className="grid gap-3 sm:grid-cols-3">
              <div>
                <label className="mb-1.5 block text-xs font-medium text-fg-muted">
                  Output
                </label>
                <div className="flex gap-1 rounded-md border border-border bg-bg-elevated p-1">
                  {MODES.map((m) => {
                    const Icon = m.icon;
                    return (
                      <button
                        key={m.id}
                        type="button"
                        onClick={() => updateDraft({ mode: m.id })}
                        className={cn(
                          "flex h-8 flex-1 items-center justify-center gap-1.5 rounded-sm text-xs font-medium transition-colors",
                          draft.mode === m.id
                            ? "bg-primary text-primary-fg"
                            : "text-fg-muted hover:text-fg",
                        )}
                      >
                        <Icon className="size-3.5" />
                        <span className="hidden sm:inline">{m.label}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              <div>
                <label className="mb-1.5 block text-xs font-medium text-fg-muted">
                  Aspect
                </label>
                <div className="flex flex-wrap gap-1">
                  {ASPECTS.map((a) => (
                    <button
                      key={a}
                      type="button"
                      onClick={() => updateDraft({ aspect: a })}
                      className={cn(
                        "h-8 rounded-md border px-2 text-xs tabular transition-colors",
                        draft.aspect === a
                          ? "border-primary bg-primary text-primary-fg"
                          : "border-border bg-bg-elevated text-fg-muted hover:text-fg",
                      )}
                    >
                      {a}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="mb-1.5 block text-xs font-medium text-fg-muted">
                  Project
                </label>
                <select
                  value={draft.projectId}
                  onChange={(e) => updateDraft({ projectId: e.target.value })}
                  className="flex h-10 w-full rounded-md border border-border bg-bg-elevated px-3 text-sm text-fg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/40"
                >
                  {PROJECTS.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {draft.mode === "video" && (
              <div>
                <div className="mb-1.5 flex items-center justify-between text-xs">
                  <span className="font-medium text-fg-muted">Duration</span>
                  <span className="tabular text-fg">{draft.duration}s</span>
                </div>
                <input
                  type="range"
                  min={2}
                  max={12}
                  step={1}
                  value={draft.duration}
                  onChange={(e) =>
                    updateDraft({ duration: Number(e.target.value) })
                  }
                  className="w-full accent-primary"
                />
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Camera & grade</CardTitle>
            <CardDescription>
              Identity lock holds subject continuity; grade lock holds look across takes.
            </CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4 sm:grid-cols-3">
            <FieldSelect
              label="Camera body"
              icon={Camera}
              value={draft.camera}
              options={[...CAMERA_PRESETS]}
              onChange={(v) => updateDraft({ camera: v })}
            />
            <FieldSelect
              label="Lens"
              icon={Aperture}
              value={draft.lens}
              options={[...LENS_PRESETS]}
              onChange={(v) => updateDraft({ lens: v })}
            />
            <FieldSelect
              label="Color grade"
              icon={Wand2}
              value={draft.grade}
              options={[...GRADE_PRESETS]}
              onChange={(v) => updateDraft({ grade: v })}
            />
          </CardContent>
        </Card>
      </div>

      <div className="space-y-4 xl:col-span-2">
        <Card>
          <CardHeader>
            <CardTitle>Model tier</CardTitle>
            <CardDescription>Higher tiers cost more credits per take</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {MODELS.map((m) => (
              <button
                key={m.id}
                type="button"
                onClick={() => updateDraft({ model: m.id })}
                className={cn(
                  "flex w-full items-center justify-between rounded-lg border px-3 py-2.5 text-left transition-colors",
                  draft.model === m.id
                    ? "border-border-strong bg-bg-subtle"
                    : "border-border bg-bg-elevated hover:bg-bg-hover",
                )}
              >
                <div>
                  <p className="text-sm font-medium">{m.label}</p>
                  <p className="text-xs text-fg-muted">{m.hint}</p>
                </div>
                {draft.model === m.id && (
                  <Badge variant="solid" className="text-[10px]">
                    Active
                  </Badge>
                )}
              </button>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Preview slate</CardTitle>
            <CardDescription>
              Framing guide · {draft.aspect} · {draft.mode}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ShotFrame
              frame="shot-a"
              aspect={draft.aspect}
              status="draft"
              mode={draft.mode}
            />
            <div className="mt-3 space-y-1.5 text-xs text-fg-muted">
              <p className="flex items-center gap-1.5">
                <Camera className="size-3.5" />
                {draft.camera} · {draft.lens}
              </p>
              <p className="flex items-center gap-1.5">
                <Sparkles className="size-3.5" />
                {draft.grade} · {draft.model}
              </p>
            </div>
            <div className="mt-4 flex flex-col gap-2 sm:flex-row">
              <Button className="flex-1" onClick={onGenerate}>
                <Sparkles className="size-3.5" />
                Generate take
              </Button>
              <Button
                variant="secondary"
                onClick={() =>
                  updateDraft({
                    takes: draft.takes + 1,
                  })
                }
              >
                Takes: {draft.takes}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function FieldSelect({
  label,
  icon: Icon,
  value,
  options,
  onChange,
}: {
  label: string;
  icon: typeof Camera;
  value: string;
  options: string[];
  onChange: (v: string) => void;
}) {
  return (
    <div>
      <label className="mb-1.5 flex items-center gap-1.5 text-xs font-medium text-fg-muted">
        <Icon className="size-3.5" />
        {label}
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="flex h-10 w-full rounded-md border border-border bg-bg-elevated px-3 text-sm text-fg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/40"
      >
        {options.map((o) => (
          <option key={o} value={o}>
            {o}
          </option>
        ))}
      </select>
    </div>
  );
}
