import { createFileRoute, Link } from "@tanstack/react-router";
import { Film, RotateCcw } from "lucide-react";
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

export const Route = createFileRoute("/recap")({
  component: RecapPage,
});

type Preset = {
  id: string;
  label: string;
  clipId: string;
  characterId: string;
  pose: string;
  framing: string;
  lighting: string;
  wardrobe: string;
  props: string;
  emotion: string;
  environment: string;
  motionOut: string;
  image?: string;
};

const PRESETS: Preset[] = [
  {
    id: "noir",
    label: "Neon alley end",
    clipId: "clip_01",
    characterId: "lead_01",
    pose: "facing camera, weight on left foot, bag strap on left shoulder",
    framing: "medium shot, eye-level, subject centered-left",
    lighting: "teal rim from right, amber practical left, wet ground bounce",
    wardrobe: "black motorcycle jacket, charcoal turtleneck — unchanged",
    props: "messenger bag left shoulder, silver ring right hand",
    emotion: "quiet dread, jaw set, eyes locked on lens",
    environment: "rain-slick neon alley, steam from grate mid-ground",
    motionOut: "slow push-in continuing; rain direction down-left",
    image: "/examples/dna-noir.jpg",
  },
  {
    id: "gothic",
    label: "Hallway hold",
    clipId: "clip_01",
    characterId: "lead_02",
    pose: "three-quarter toward camera, candle in right hand at chest height",
    framing: "medium-wide, slight dutch, subject right of center",
    lighting: "warm candle key on face, deep blue fill in corridor depth",
    wardrobe: "charcoal wool coat, ivory blouse — unchanged",
    props: "brass candle holder, flame steady",
    emotion: "uneasy curiosity, breath held",
    environment: "Victorian hallway, peeling floral wallpaper both walls",
    motionOut: "creep forward along corridor axis; hold candle height",
    image: "/examples/dna-gothic.jpg",
  },
];

function buildRecap(f: {
  clipId: string;
  characterId: string;
  pose: string;
  framing: string;
  lighting: string;
  wardrobe: string;
  props: string;
  emotion: string;
  environment: string;
  motionOut: string;
}) {
  const clip = f.clipId.trim() || "clip_N";
  return `[LAST_FRAME_RECAP ${clip}]
character_id: ${f.characterId.trim() || "lead_01"}
pose: ${f.pose.trim() || "—"}
framing: ${f.framing.trim() || "—"}
lighting: ${f.lighting.trim() || "—"}
wardrobe: ${f.wardrobe.trim() || "—"}
props: ${f.props.trim() || "—"}
emotion: ${f.emotion.trim() || "—"}
environment: ${f.environment.trim() || "—"}
motion_out: ${f.motionOut.trim() || "—"}
continuity_note: wardrobe and face must match CHARACTER_DNA; treat mismatches as drift
[/LAST_FRAME_RECAP]`;
}

function buildContinuityState(f: {
  clipId: string;
  characterId: string;
  wardrobe: string;
  props: string;
  lighting: string;
  emotion: string;
}) {
  return `{
  "type": "continuity_state",
  "clip_id": "${f.clipId.trim() || "clip_N"}",
  "character_id": "${f.characterId.trim() || "lead_01"}",
  "last_frame_recap": "see LAST_FRAME_RECAP block",
  "wardrobe": "${(f.wardrobe || "unchanged").replace(/"/g, "'")}",
  "props": "${(f.props || "").replace(/"/g, "'")}",
  "lighting": "${(f.lighting || "").replace(/"/g, "'")}",
  "emotion": "${(f.emotion || "").replace(/"/g, "'")}"
}`;
}

function buildExtendPack(recap: string, continuity: string, characterId: string) {
  return `ACTIVATE SEQUENCE_DIRECTOR
ACTIVATE MULTI_CLIP_CONTINUITY
ACTIVATE IMAGINE_HANDOFF
ACTIVATE QA_GUARDIAN

Mode: Extend-from-Frame
Character: ${characterId || "lead"}
Input:
${recap}

${continuity}

Rule: Plan clip N+1 from recap + DNA inject. No stitch until chain QA is Go.
On No-Go: repair only — do not rewrite Production Bible.`;
}

function RecapPage() {
  const [clipId, setClipId] = useState(PRESETS[0].clipId);
  const [characterId, setCharacterId] = useState(PRESETS[0].characterId);
  const [pose, setPose] = useState(PRESETS[0].pose);
  const [framing, setFraming] = useState(PRESETS[0].framing);
  const [lighting, setLighting] = useState(PRESETS[0].lighting);
  const [wardrobe, setWardrobe] = useState(PRESETS[0].wardrobe);
  const [props, setProps] = useState(PRESETS[0].props);
  const [emotion, setEmotion] = useState(PRESETS[0].emotion);
  const [environment, setEnvironment] = useState(PRESETS[0].environment);
  const [motionOut, setMotionOut] = useState(PRESETS[0].motionOut);
  const [image, setImage] = useState(PRESETS[0].image);
  const [presetId, setPresetId] = useState(PRESETS[0].id);

  const recap = useMemo(
    () =>
      buildRecap({
        clipId,
        characterId,
        pose,
        framing,
        lighting,
        wardrobe,
        props,
        emotion,
        environment,
        motionOut,
      }),
    [
      clipId,
      characterId,
      pose,
      framing,
      lighting,
      wardrobe,
      props,
      emotion,
      environment,
      motionOut,
    ],
  );

  const continuity = useMemo(
    () =>
      buildContinuityState({
        clipId,
        characterId,
        wardrobe,
        props,
        lighting,
        emotion,
      }),
    [clipId, characterId, wardrobe, props, lighting, emotion],
  );

  const extendPack = useMemo(
    () => buildExtendPack(recap, continuity, characterId),
    [recap, continuity, characterId],
  );

  function applyPreset(id: string) {
    const p = PRESETS.find((x) => x.id === id);
    if (!p) return;
    setPresetId(p.id);
    setClipId(p.clipId);
    setCharacterId(p.characterId);
    setPose(p.pose);
    setFraming(p.framing);
    setLighting(p.lighting);
    setWardrobe(p.wardrobe);
    setProps(p.props);
    setEmotion(p.emotion);
    setEnvironment(p.environment);
    setMotionOut(p.motionOut);
    setImage(p.image);
  }

  const fieldClass =
    "mt-1.5 w-full rounded-lg border border-border bg-bg px-3 py-2.5 text-sm text-fg placeholder:text-subtle outline-none focus:border-border-strong focus:ring-2 focus:ring-teal/30";

  const fields: {
    label: string;
    value: string;
    set: (v: string) => void;
    rows?: number;
  }[] = [
    { label: "Clip ID", value: clipId, set: setClipId },
    { label: "Character ID", value: characterId, set: setCharacterId },
    { label: "Pose", value: pose, set: setPose, rows: 2 },
    { label: "Framing", value: framing, set: setFraming },
    { label: "Lighting", value: lighting, set: setLighting, rows: 2 },
    { label: "Wardrobe", value: wardrobe, set: setWardrobe, rows: 2 },
    { label: "Props", value: props, set: setProps },
    { label: "Emotion", value: emotion, set: setEmotion },
    { label: "Environment", value: environment, set: setEnvironment, rows: 2 },
    {
      label: "Motion out (into clip N+1)",
      value: motionOut,
      set: setMotionOut,
      rows: 2,
    },
  ];

  return (
    <div className="space-y-8">
      <div>
        <Badge variant="teal">Continuity</Badge>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">
          Last-frame recap builder
        </h1>
        <p className="mt-2 max-w-2xl text-muted leading-relaxed">
          Write a concrete{" "}
          <Link to="/glossary" className="text-teal hover:underline">
            LAST_FRAME_RECAP
          </Link>{" "}
          so extend chains know pose, light, props, and emotion — then copy a
          continuity packet and extend activation.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {PRESETS.map((p) => (
          <button
            key={p.id}
            type="button"
            onClick={() => applyPreset(p.id)}
            className={cn(
              "overflow-hidden rounded-xl border text-left transition-colors",
              presetId === p.id
                ? "border-teal/50 ring-2 ring-teal/20"
                : "border-border hover:border-border-strong",
            )}
          >
            {p.image && (
              <div className="aspect-[3/2] bg-elevated">
                <img
                  src={p.image}
                  alt=""
                  className="h-full w-full object-cover"
                  loading="lazy"
                />
              </div>
            )}
            <div className="border-t border-border bg-surface px-3 py-2.5">
              <p className="text-sm font-medium text-fg">{p.label}</p>
              <p className="font-mono text-[11px] text-teal">
                {p.clipId} · {p.characterId}
              </p>
            </div>
          </button>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Why recaps matter</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 sm:grid-cols-3 text-sm text-muted">
          <p>
            <span className="text-fg font-medium">Vague recaps</span> → wardrobe
            and prop drift on clip N+1.
          </p>
          <p>
            <span className="text-fg font-medium">Concrete pose + light</span> →
            Sequence Director can plan motion_out.
          </p>
          <p>
            <span className="text-fg font-medium">Pair with DNA</span> → face
            lock + last frame = multi-clip identity.
          </p>
        </CardContent>
      </Card>

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
          onClick={() => applyPreset("noir")}
        >
          <RotateCcw className="h-3.5 w-3.5" />
          Reset
        </Button>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Film className="h-4 w-4 text-teal" />
              Recap fields
            </CardTitle>
            <CardDescription>
              Be specific — “standing” is not enough
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {fields.map(({ label, value, set, rows }) => (
              <label
                key={label}
                className="block text-xs font-medium text-subtle"
              >
                {label}
                {rows ? (
                  <textarea
                    value={value}
                    onChange={(e) => set(e.target.value)}
                    rows={rows}
                    className={cn(fieldClass, "resize-y")}
                  />
                ) : (
                  <input
                    value={value}
                    onChange={(e) => set(e.target.value)}
                    className={fieldClass}
                  />
                )}
              </label>
            ))}
          </CardContent>
        </Card>

        <div className="space-y-4 lg:sticky lg:top-20 lg:self-start">
          {image && (
            <div className="overflow-hidden rounded-xl border border-border">
              <img
                src={image}
                alt="Frame reference for recap"
                className="aspect-[3/2] w-full object-cover"
              />
              <p className="border-t border-border bg-surface px-3 py-2 text-xs text-muted">
                Reference still for this recap preset — describe the{" "}
                <em>final frame</em>, not the whole scene.
              </p>
            </div>
          )}

          <Card className="border-teal/20">
            <CardHeader>
              <div className="flex items-start justify-between gap-2">
                <div>
                  <CardTitle className="text-base">LAST_FRAME_RECAP</CardTitle>
                  <CardDescription>Paste into extend workflows</CardDescription>
                </div>
                <CopyButton text={recap} label="Copy recap" />
              </div>
            </CardHeader>
            <CardContent>
              <pre className="max-h-52 overflow-auto whitespace-pre-wrap rounded-lg border border-border bg-bg p-3.5 font-mono text-[11px] leading-relaxed text-muted">
                {recap}
              </pre>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-start justify-between gap-2">
                <div>
                  <CardTitle className="text-base">continuity_state</CardTitle>
                  <CardDescription>JSON handoff packet</CardDescription>
                </div>
                <CopyButton text={continuity} label="Copy JSON" />
              </div>
            </CardHeader>
            <CardContent>
              <pre className="max-h-40 overflow-auto whitespace-pre-wrap rounded-lg border border-border bg-bg p-3.5 font-mono text-[11px] leading-relaxed text-muted">
                {continuity}
              </pre>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-start justify-between gap-2">
                <div>
                  <CardTitle className="text-base">Extend activation</CardTitle>
                  <CardDescription>
                    Sequence → Continuity → Handoff → QA
                  </CardDescription>
                </div>
                <CopyButton text={extendPack} label="Copy pack" />
              </div>
            </CardHeader>
            <CardContent>
              <pre className="max-h-48 overflow-auto whitespace-pre-wrap rounded-lg border border-border bg-bg p-3.5 font-mono text-[11px] leading-relaxed text-muted">
                {extendPack}
              </pre>
              <p className="mt-3 text-xs text-subtle">
                Pair with{" "}
                <Link to="/dna" className="text-teal hover:underline">
                  Character DNA
                </Link>
                , run the{" "}
                <Link to="/scenarios" className="text-teal hover:underline">
                  Mini extend chain
                </Link>{" "}
                scenario, or study{" "}
                <Link to="/workflows" className="text-teal hover:underline">
                  Extend chain + QA
                </Link>
                .
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
