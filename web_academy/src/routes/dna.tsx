import { createFileRoute, Link } from "@tanstack/react-router";
import {
  ArrowDown,
  Fingerprint,
  Layers,
  RotateCcw,
  Shield,
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
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/dna")({
  component: DnaPage,
});

type Preset = {
  id: string;
  label: string;
  characterId: string;
  name: string;
  ageBand: string;
  face: string;
  wardrobe: string;
  props: string;
  rules: string;
  transform: boolean;
  image: string;
  scene: string;
};

const PRESETS: Preset[] = [
  {
    id: "noir",
    label: "Neon courier",
    characterId: "lead_01",
    name: "Mara Chen",
    ageBand: "adult_30s",
    face:
      "East Asian woman, sharp cheekbones, dark brown eyes, short asymmetrical black hair, small scar above left brow",
    wardrobe:
      "matte black motorcycle jacket, charcoal turtleneck, silver zipper pulls, slim dark jeans, worn black boots",
    props: "messenger bag left shoulder, small silver ring right hand",
    rules:
      "Same face and wardrobe every shot. No age change. No glasses unless listed.",
    transform: false,
    image: "/examples/dna-noir.jpg",
    scene:
      "rain-slick neon alley at night, teal and amber practicals, wet reflections, 35mm anamorphic",
  },
  {
    id: "gothic",
    label: "Candle hall",
    characterId: "lead_02",
    name: "Elena Voss",
    ageBand: "adult_late_20s",
    face:
      "Adult woman, pale olive skin, long dark brown hair in loose waves, green-grey eyes, soft freckles across nose",
    wardrobe:
      "charcoal wool coat over ivory blouse, high-waist black trousers, thin gold chain necklace",
    props: "single brass candle holder",
    rules:
      "Lock face and coat. Candle prop always in right hand unless Transform Track.",
    transform: false,
    image: "/examples/dna-gothic.jpg",
    scene:
      "abandoned Victorian hallway, peeling wallpaper, single warm candle key, deep blue fill, 24mm",
  },
];

const ANATOMY = [
  {
    key: "header",
    color: "bg-teal/20 border-teal/40 text-teal",
    label: "Header",
    sample: "[CHARACTER_DNA lead_01]",
    why: "Names the lock so multi-character projects stay separate.",
  },
  {
    key: "face",
    color: "bg-amber/15 border-amber/40 text-amber",
    label: "Face lock",
    sample: "face_lock: sharp cheekbones, short asymmetrical black hair…",
    why: "Stops face drift across stills and extends.",
  },
  {
    key: "wardrobe",
    color: "bg-success/15 border-success/40 text-success",
    label: "Wardrobe lock",
    sample: "wardrobe_lock: matte black motorcycle jacket…",
    why: "Keeps costume continuous shot to shot.",
  },
  {
    key: "rules",
    color: "bg-accent/15 border-accent/40 text-accent",
    label: "Rules + transform",
    sample: "transform_allowed: false",
    why: "Defines what counts as drift vs intentional change.",
  },
  {
    key: "footer",
    color: "bg-elevated border-border text-muted",
    label: "Close",
    sample: "[/CHARACTER_DNA]",
    why: "Ends the inject so the scene prompt can begin.",
  },
] as const;

function buildInject(f: {
  characterId: string;
  name: string;
  ageBand: string;
  face: string;
  wardrobe: string;
  props: string;
  rules: string;
  transform: boolean;
}) {
  const id = f.characterId.trim() || "lead_01";
  const lines = [
    `[CHARACTER_DNA ${id}]`,
    f.name.trim() && `name: ${f.name.trim()}`,
    f.ageBand.trim() && `age_band: ${f.ageBand.trim()}`,
    f.face.trim() && `face_lock: ${f.face.trim()}`,
    f.wardrobe.trim() && `wardrobe_lock: ${f.wardrobe.trim()}`,
    f.props.trim() && `props: ${f.props.trim()}`,
    f.rules.trim() && `rules: ${f.rules.trim()}`,
    `transform_allowed: ${f.transform ? "true" : "false"}`,
    f.transform
      ? "transform_track: document any intentional wardrobe/makeup change before generation"
      : "transform_track: none — treat wardrobe/face changes as drift",
    "inject: prepend this block to every still and video prompt for this character",
    `[/CHARACTER_DNA]`,
  ].filter(Boolean);
  return lines.join("\n");
}

function buildActivation(inject: string, characterId: string) {
  return `ACTIVATE IDENTITY_LOCK
Then: ACTIVATE IMAGINE_PROMPT_MASTER

Task: lock Character DNA for ${characterId || "lead"}, then craft stills with inject at top of every packet.

${inject}

Output: DNA inject confirmed + 1 Ultimate Template still prompt using inject.`;
}

function barePrompt(scene: string, name: string) {
  return `Subject: ${name || "lead character"}.
Environment: ${scene}.
Mood: cinematic.
Cinematic still. No text, no watermark.
Negatives: text, watermark, extra limbs.`;
}

function stackedPrompt(inject: string, scene: string, name: string) {
  return `${inject}

--- scene prompt below DNA ---

${barePrompt(scene, name)}`;
}

function DnaPage() {
  const [characterId, setCharacterId] = useState<string>(PRESETS[0].characterId);
  const [name, setName] = useState<string>(PRESETS[0].name);
  const [ageBand, setAgeBand] = useState<string>(PRESETS[0].ageBand);
  const [face, setFace] = useState<string>(PRESETS[0].face);
  const [wardrobe, setWardrobe] = useState<string>(PRESETS[0].wardrobe);
  const [props, setProps] = useState<string>(PRESETS[0].props);
  const [rules, setRules] = useState<string>(PRESETS[0].rules);
  const [transform, setTransform] = useState(false);
  const [scene, setScene] = useState<string>(PRESETS[0].scene);
  const [image, setImage] = useState<string>(PRESETS[0].image);
  const [presetId, setPresetId] = useState(PRESETS[0].id);

  const inject = useMemo(
    () =>
      buildInject({
        characterId,
        name,
        ageBand,
        face,
        wardrobe,
        props,
        rules,
        transform,
      }),
    [characterId, name, ageBand, face, wardrobe, props, rules, transform],
  );

  const activation = useMemo(
    () => buildActivation(inject, characterId),
    [inject, characterId],
  );

  const bare = useMemo(() => barePrompt(scene, name), [scene, name]);
  const stacked = useMemo(
    () => stackedPrompt(inject, scene, name),
    [inject, scene, name],
  );

  function applyPreset(id: string) {
    const p = PRESETS.find((x) => x.id === id);
    if (!p) return;
    setPresetId(p.id);
    setCharacterId(p.characterId);
    setName(p.name);
    setAgeBand(p.ageBand);
    setFace(p.face);
    setWardrobe(p.wardrobe);
    setProps(p.props);
    setRules(p.rules);
    setTransform(p.transform);
    setScene(p.scene);
    setImage(p.image);
  }

  function reset() {
    applyPreset("noir");
  }

  const fieldClass =
    "mt-1.5 w-full rounded-lg border border-border bg-bg px-3 py-2.5 text-sm text-fg placeholder:text-subtle outline-none focus:border-border-strong focus:ring-2 focus:ring-teal/30";

  return (
    <div className="space-y-8">
      <div>
        <Badge variant="teal">Identity</Badge>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">
          Character DNA builder
        </h1>
        <p className="mt-2 max-w-2xl text-muted leading-relaxed">
          Freeze face, wardrobe, and rules into a paste-ready inject block.
          Visual examples show how the inject sits on top of every prompt.
        </p>
        <p className="mt-2 text-xs text-subtle">
          Fictional adults only · See{" "}
          <Link to="/glossary" className="text-teal hover:underline">
            Character DNA
          </Link>{" "}
          in the glossary
        </p>
      </div>

      <Card className="border-amber/30 bg-amber/5">
        <CardContent className="flex gap-3 pt-5 text-sm text-muted">
          <Shield className="mt-0.5 h-4 w-4 shrink-0 text-amber" />
          <p>
            DNA is an educational contract for Studio continuity — not a
            deepfake tool. Reference plates below are fictional examples only.
          </p>
        </CardContent>
      </Card>

      {/* Visual examples */}
      <section className="space-y-4">
        <div>
          <h2 className="text-lg font-semibold tracking-tight">
            Visual examples
          </h2>
          <p className="mt-1 text-sm text-muted">
            Reference plates for the two starter locks — same DNA must survive a
            new camera angle or location.
          </p>
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          {PRESETS.map((p) => (
            <button
              key={p.id}
              type="button"
              onClick={() => applyPreset(p.id)}
              className={cn(
                "group overflow-hidden rounded-xl border text-left transition-colors",
                presetId === p.id
                  ? "border-teal/50 ring-2 ring-teal/20"
                  : "border-border hover:border-border-strong",
              )}
            >
              <div className="relative aspect-[3/2] bg-elevated">
                <img
                  src={p.image}
                  alt={`Reference plate for ${p.name}`}
                  className="h-full w-full object-cover"
                  loading="lazy"
                />
                <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-bg/95 via-bg/50 to-transparent p-3 pt-10">
                  <p className="text-sm font-medium text-fg">{p.label}</p>
                  <p className="font-mono text-[11px] text-teal">
                    {p.characterId}
                  </p>
                </div>
              </div>
              <div className="space-y-2 border-t border-border bg-surface p-3">
                <p className="text-xs text-muted line-clamp-2">
                  <span className="text-amber">face_lock</span> ·{" "}
                  {p.face.slice(0, 72)}…
                </p>
                <p className="text-xs text-muted line-clamp-2">
                  <span className="text-success">wardrobe_lock</span> ·{" "}
                  {p.wardrobe.slice(0, 72)}…
                </p>
              </div>
            </button>
          ))}
        </div>
      </section>

      {/* Stack order + anatomy */}
      <section className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Layers className="h-4 w-4 text-teal" />
              Packet stack order
            </CardTitle>
            <CardDescription>
              Always DNA first — scene prompt never replaces the lock
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {[
              {
                step: "01",
                title: "CHARACTER_DNA inject",
                body: "Face, wardrobe, rules — frozen",
                tone: "border-teal/40 bg-teal/10",
              },
              {
                step: "02",
                title: "Ultimate Template scene",
                body: "Subject → environment → lighting → lens → mood",
                tone: "border-border bg-elevated/40",
              },
              {
                step: "03",
                title: "Negatives",
                body: "text, watermark, extra limbs, low-res…",
                tone: "border-border bg-bg",
              },
            ].map((layer, i) => (
              <div key={layer.step}>
                <div
                  className={cn(
                    "rounded-lg border px-3 py-3",
                    layer.tone,
                  )}
                >
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-[11px] text-teal">
                      {layer.step}
                    </span>
                    <div>
                      <p className="text-sm font-medium text-fg">
                        {layer.title}
                      </p>
                      <p className="text-xs text-muted">{layer.body}</p>
                    </div>
                  </div>
                </div>
                {i < 2 && (
                  <div className="flex justify-center py-1 text-subtle" aria-hidden>
                    <ArrowDown className="h-3.5 w-3.5" />
                  </div>
                )}
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Inject anatomy</CardTitle>
            <CardDescription>
              Color map of each section inside the block
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {ANATOMY.map((row) => (
              <div
                key={row.key}
                className={cn(
                  "rounded-lg border px-3 py-2.5",
                  row.color,
                )}
              >
                <p className="text-[11px] font-semibold uppercase tracking-wide">
                  {row.label}
                </p>
                <p className="mt-1 font-mono text-[11px] leading-relaxed opacity-90">
                  {row.sample}
                </p>
                <p className="mt-1 text-xs text-muted">{row.why}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      </section>

      {/* Before / after */}
      <section className="space-y-3">
        <div>
          <h2 className="text-lg font-semibold tracking-tight">
            Without DNA vs with DNA
          </h2>
          <p className="mt-1 text-sm text-muted">
            Same scene line — only the inject changes continuity risk.
          </p>
        </div>
        <div className="grid gap-4 lg:grid-cols-[1fr_auto_1fr] lg:items-stretch">
          <Card className="border-danger/20">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between gap-2">
                <Badge variant="outline">Without inject</Badge>
                <CopyButton text={bare} label="Copy" />
              </div>
              <CardTitle className="text-base text-danger">Risky</CardTitle>
              <CardDescription>
                Face and wardrobe free to drift each generation
              </CardDescription>
            </CardHeader>
            <CardContent>
              <pre className="max-h-48 overflow-auto whitespace-pre-wrap rounded-lg border border-border bg-bg p-3 font-mono text-[11px] leading-relaxed text-muted">
                {bare}
              </pre>
            </CardContent>
          </Card>

          <div className="hidden items-center justify-center lg:flex">
            <ArrowDown className="h-5 w-5 rotate-[-90deg] text-teal" />
          </div>

          <Card className="border-teal/30">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between gap-2">
                <Badge variant="teal">With inject</Badge>
                <CopyButton text={stacked} label="Copy" />
              </div>
              <CardTitle className="text-base text-teal">Locked</CardTitle>
              <CardDescription>
                DNA block first, then scene — multi-shot safe
              </CardDescription>
            </CardHeader>
            <CardContent>
              <pre className="max-h-48 overflow-auto whitespace-pre-wrap rounded-lg border border-border bg-bg p-3 font-mono text-[11px] leading-relaxed text-muted">
                {stacked}
              </pre>
            </CardContent>
          </Card>
        </div>

        {image && (
          <Card className="overflow-hidden">
            <div className="grid md:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
              <div className="relative aspect-[3/2] md:aspect-auto md:min-h-[220px]">
                <img
                  src={image}
                  alt={`Active DNA reference for ${name}`}
                  className="h-full w-full object-cover"
                />
              </div>
              <div className="p-5 space-y-3">
                <p className="text-xs font-medium uppercase tracking-wide text-subtle">
                  Active reference plate
                </p>
                <p className="text-lg font-semibold text-fg">{name}</p>
                <p className="font-mono text-xs text-teal">{characterId}</p>
                <ul className="space-y-2 text-sm text-muted">
                  <li>
                    <span className="text-amber">Face</span> stays constant even
                    if the alley or hallway changes.
                  </li>
                  <li>
                    <span className="text-success">Wardrobe</span> stays
                    constant unless Transform Track is true.
                  </li>
                  <li>
                    Paste the inject{" "}
                    <strong className="text-fg">above</strong> every new still
                    or video prompt for this lead.
                  </li>
                </ul>
              </div>
            </div>
          </Card>
        )}
      </section>

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
                : "border-border bg-surface text-muted hover:border-border-strong hover:text-fg",
            )}
          >
            {p.label}
          </button>
        ))}
        <Button type="button" variant="ghost" size="sm" onClick={reset}>
          <RotateCcw className="h-3.5 w-3.5" />
          Reset
        </Button>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Fingerprint className="h-4 w-4 text-teal" />
              DNA fields
            </CardTitle>
            <CardDescription>
              Minimal lock set — enough for multi-shot consistency
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="grid gap-3 sm:grid-cols-2">
              <label className="block text-xs font-medium text-subtle">
                Character ID
                <input
                  value={characterId}
                  onChange={(e) => setCharacterId(e.target.value)}
                  className={fieldClass}
                  placeholder="lead_01"
                />
              </label>
              <label className="block text-xs font-medium text-subtle">
                Display name
                <input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className={fieldClass}
                  placeholder="Optional"
                />
              </label>
            </div>
            <label className="block text-xs font-medium text-subtle">
              Age band
              <input
                value={ageBand}
                onChange={(e) => setAgeBand(e.target.value)}
                className={fieldClass}
                placeholder="adult_30s"
              />
            </label>
            <label className="block text-xs font-medium text-subtle">
              Face lock
              <textarea
                value={face}
                onChange={(e) => setFace(e.target.value)}
                rows={3}
                className={cn(fieldClass, "resize-y min-h-[80px]")}
                placeholder="Distinctive adult features only"
              />
            </label>
            <label className="block text-xs font-medium text-subtle">
              Wardrobe lock
              <textarea
                value={wardrobe}
                onChange={(e) => setWardrobe(e.target.value)}
                rows={3}
                className={cn(fieldClass, "resize-y min-h-[80px]")}
              />
            </label>
            <label className="block text-xs font-medium text-subtle">
              Props
              <input
                value={props}
                onChange={(e) => setProps(e.target.value)}
                className={fieldClass}
              />
            </label>
            <label className="block text-xs font-medium text-subtle">
              Rules
              <textarea
                value={rules}
                onChange={(e) => setRules(e.target.value)}
                rows={2}
                className={cn(fieldClass, "resize-y")}
              />
            </label>
            <label className="block text-xs font-medium text-subtle">
              Scene line (for examples)
              <textarea
                value={scene}
                onChange={(e) => setScene(e.target.value)}
                rows={2}
                className={cn(fieldClass, "resize-y")}
              />
            </label>
            <label className="flex items-center gap-2 text-sm text-muted cursor-pointer">
              <input
                type="checkbox"
                checked={transform}
                onChange={(e) => setTransform(e.target.checked)}
                className="h-4 w-4 accent-teal"
              />
              Transform allowed (requires Transform Track notes)
            </label>
          </CardContent>
        </Card>

        <div className="space-y-4 lg:sticky lg:top-20 lg:self-start">
          <Card className="border-teal/20">
            <CardHeader>
              <div className="flex items-start justify-between gap-2">
                <div>
                  <CardTitle className="text-base">Inject block</CardTitle>
                  <CardDescription>
                    Paste at the top of every prompt for this character
                  </CardDescription>
                </div>
                <CopyButton text={inject} label="Copy DNA" />
              </div>
            </CardHeader>
            <CardContent>
              <pre className="max-h-[280px] overflow-auto whitespace-pre-wrap rounded-lg border border-border bg-bg p-4 font-mono text-[11px] leading-relaxed text-muted">
                {inject}
              </pre>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-start justify-between gap-2">
                <div>
                  <CardTitle className="text-base">Activation pack</CardTitle>
                  <CardDescription>
                    Identity Lock → Prompt Master starter
                  </CardDescription>
                </div>
                <CopyButton text={activation} label="Copy pack" />
              </div>
            </CardHeader>
            <CardContent>
              <pre className="max-h-[220px] overflow-auto whitespace-pre-wrap rounded-lg border border-border bg-bg p-4 font-mono text-[11px] leading-relaxed text-muted">
                {activation}
              </pre>
              <p className="mt-3 text-xs text-subtle">
                Next: build a still in{" "}
                <Link to="/lab" className="text-teal hover:underline">
                  Prompt lab
                </Link>{" "}
                with this inject on top, or open the{" "}
                <Link to="/workflows" className="text-teal hover:underline">
                  DNA lock chain
                </Link>{" "}
                workflow.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
