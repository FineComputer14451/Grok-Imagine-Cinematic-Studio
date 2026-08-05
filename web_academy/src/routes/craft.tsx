import { createFileRoute, Link } from "@tanstack/react-router";
import {
  ArrowRight,
  AudioLines,
  Camera,
  Frame,
  Lightbulb,
  Move,
  Palette,
  RectangleHorizontal,
  Scissors,
  Sparkles,
} from "lucide-react";
import { CopyButton } from "@/components/copy-button";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ASPECT_RATIOS } from "@/data/aspect";
import { GRADE_LOOKS } from "@/data/color";
import { COMP_TOPICS, SHOT_SIZES } from "@/data/composition";
import { CUT_TYPES, EDIT_TOPICS } from "@/data/editing";
import { FOCAL_BANDS } from "@/data/lenses";
import { LIGHTING_TOPICS, LIGHTING_SETUPS } from "@/data/lighting";
import { MOVE_TYPES } from "@/data/movement";
import { SOUND_LAYERS } from "@/data/sound";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/craft")({
  component: CraftPage,
});

const MODULES = [
  {
    to: "/lighting" as const,
    icon: Lightbulb,
    step: "01",
    title: "Lighting",
    body: "Key, fill, rim, practicals, ratio, setups.",
    count: `${LIGHTING_TOPICS.length} topics · ${LIGHTING_SETUPS.length} setups`,
  },
  {
    to: "/composition" as const,
    icon: Frame,
    step: "02",
    title: "Framing",
    body: "Shot sizes, thirds, eyeline, coverage recipes.",
    count: `${COMP_TOPICS.length} topics · ${SHOT_SIZES.length} sizes`,
  },
  {
    to: "/aspect" as const,
    icon: RectangleHorizontal,
    step: "03",
    title: "Aspect",
    body: "2.39 scope through 9:16 vertical delivery.",
    count: `${ASPECT_RATIOS.length} ratios`,
  },
  {
    to: "/lenses" as const,
    icon: Camera,
    step: "04",
    title: "Lenses",
    body: "Focal bands, DOF, anamorphic, lens sets.",
    count: `${FOCAL_BANDS.length} bands`,
  },
  {
    to: "/movement" as const,
    icon: Move,
    step: "05",
    title: "Movement",
    body: "Static to push-in — one move per short clip.",
    count: `${MOVE_TYPES.length} move types`,
  },
  {
    to: "/color" as const,
    icon: Palette,
    step: "06",
    title: "Color",
    body: "Looks, skin protection, grade packet lines.",
    count: `${GRADE_LOOKS.length} looks`,
  },
  {
    to: "/editing" as const,
    icon: Scissors,
    step: "07",
    title: "Editing",
    body: "Cuts, teaser spine, stills montage, stitch QA.",
    count: `${EDIT_TOPICS.length} topics · ${CUT_TYPES.length} cuts`,
  },
  {
    to: "/sound" as const,
    icon: AudioLines,
    step: "08",
    title: "Sound",
    body: "Layers, mix hierarchy, teaser sound briefs.",
    count: `${SOUND_LAYERS.length} layers`,
  },
] as const;

const MASTER = `CRAFT MASTER CHEAT — Studio Academy

PATH
Lighting → Framing → Aspect → Lenses → Movement → Color → Editing → Sound → DoP → Lab

STILL PACKET
DNA → subject → env → light → frame → lens/aspect → static → grade → negatives

TEASER
Wide → MS → CU → button · hard cuts · QA before stitch
Sound: picture first · one hero event · trait-based music brief · silent OK early

NEON DEFAULT
2.39 · 35/50 · teal/amber · slow push · 24s hybrid · rain + pulse + button sub

CANDLE DEFAULT
1.85 · 24/35 · warm/cool · corridor creep · slow holds · sparse drone`;

const TOOLS = [
  { to: "/dop" as const, label: "DoP visual card", why: "Freeze the look" },
  { to: "/lab" as const, label: "Prompt lab", why: "Assemble packets" },
  { to: "/shots" as const, label: "Shot list", why: "Order the stills" },
  { to: "/pack" as const, label: "Project pack", why: "Export the charter" },
  { to: "/delivery" as const, label: "Delivery checklist", why: "Ship gate" },
  { to: "/dna" as const, label: "Character DNA", why: "Lock the face" },
  { to: "/editing" as const, label: "Editing", why: "Cut the teaser" },
] as const;

function CraftPage() {
  return (
    <div className="space-y-8">
      <div>
        <Badge variant="teal">Craft hub</Badge>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">
          Cinematography path
        </h1>
        <p className="mt-2 max-w-2xl text-muted leading-relaxed">
          Eight craft modules — light through sound — then lock a DoP card and
          build packets.
        </p>
      </div>

      <Card className="border-teal/20 bg-teal/5">
        <CardContent className="flex flex-col gap-3 pt-5 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex gap-3">
            <Sparkles className="mt-0.5 h-5 w-5 shrink-0 text-teal" />
            <div>
              <p className="text-sm font-medium text-fg">
                Recommended flow for a new learner
              </p>
              <p className="mt-1 text-sm text-muted">
                Walk 01→08, copy the master cheat, open DoP, Prompt lab — edit +
                sound only after plates exist. Run delivery checklist before ship.
              </p>
            </div>
          </div>
          <Link
            to="/sound"
            className={cn(
              "inline-flex h-10 shrink-0 items-center justify-center gap-2 rounded-lg px-4 text-sm font-semibold",
              "bg-teal text-bg hover:bg-teal/90",
            )}
          >
            Open sound
            <ArrowRight className="h-4 w-4" />
          </Link>
        </CardContent>
      </Card>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {MODULES.map(({ to, icon: Icon, step, title, body, count }) => (
          <Link key={to} to={to} className="group">
            <Card className="h-full transition-colors group-hover:border-border-strong group-hover:bg-elevated/30">
              <CardHeader>
                <div className="flex items-center justify-between gap-2">
                  <span className="font-mono text-[11px] text-teal">{step}</span>
                  <span className="flex h-9 w-9 items-center justify-center rounded-lg border border-border bg-bg">
                    <Icon className="h-4 w-4 text-teal" />
                  </span>
                </div>
                <CardTitle className="mt-2 text-base">{title}</CardTitle>
                <CardDescription>{body}</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-subtle">{count}</p>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Packet → teaser → sound</CardTitle>
          <CardDescription>
            Generate with 01–06 · cut with 07 · score with 08 · ship with delivery
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ol className="space-y-2">
            {[
              ["DNA", "Face/wardrobe inject", "/dna"],
              ["Lighting", "Key · fill · practicals", "/lighting"],
              ["Framing + lens", "Size · mm · aspect", "/composition"],
              ["Color", "Look · skin · contrast", "/color"],
              ["Movement", "Static → one video move", "/movement"],
              ["Editing", "Order · duration · stitch", "/editing"],
              ["Sound", "Bed · hits · brief", "/sound"],
              ["Delivery", "Ship gate checklist", "/delivery"],
            ].map(([label, detail, href], i) => (
              <li key={label}>
                <Link
                  to={href}
                  className="flex items-center gap-3 rounded-lg border border-border bg-bg px-3 py-2.5 text-sm transition-colors hover:border-border-strong"
                >
                  <span className="font-mono text-[11px] text-teal">
                    {String(i + 1).padStart(2, "0")}
                  </span>
                  <span className="min-w-[6.5rem] font-medium text-fg">
                    {label}
                  </span>
                  <span className="text-muted">{detail}</span>
                  <ArrowRight className="ml-auto h-3.5 w-3.5 shrink-0 text-subtle" />
                </Link>
              </li>
            ))}
          </ol>
        </CardContent>
      </Card>

      <section className="space-y-3">
        <h2 className="text-lg font-semibold tracking-tight">
          Production tools
        </h2>
        <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {TOOLS.map((t) => (
            <Link
              key={t.to}
              to={t.to}
              className="flex items-center justify-between gap-2 rounded-xl border border-border bg-surface px-4 py-3 text-sm transition-colors hover:border-border-strong"
            >
              <span>
                <span className="font-medium text-fg">{t.label}</span>
                <span className="mt-0.5 block text-xs text-muted">{t.why}</span>
              </span>
              <ArrowRight className="h-4 w-4 shrink-0 text-teal" />
            </Link>
          ))}
        </div>
      </section>

      <Card className="border-teal/20">
        <CardHeader>
          <div className="flex items-start justify-between gap-2">
            <div>
              <CardTitle className="text-base">Master cheat sheet</CardTitle>
              <CardDescription>Craft 01–08 condensed</CardDescription>
            </div>
            <CopyButton text={MASTER} label="Copy all" />
          </div>
        </CardHeader>
        <CardContent>
          <pre className="max-h-[360px] overflow-auto whitespace-pre-wrap rounded-lg border border-border bg-bg p-3.5 font-mono text-[11px] leading-relaxed text-muted">
            {MASTER}
          </pre>
        </CardContent>
      </Card>
    </div>
  );
}
