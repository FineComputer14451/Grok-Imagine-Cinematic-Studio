import { Link, createFileRoute } from "@tanstack/react-router";
import {
  Aperture,
  ArrowRight,
  AudioLines,
  Award,
  BookMarked,
  BookOpen,
  BookText,
  Calculator,
  Camera,
  CheckCircle2,
  CircleHelp,
  Clapperboard,
  ClipboardCheck,
  Code2,
  Cpu,
  DollarSign,
  Film,
  Fingerprint,
  FlaskConical,
  Frame,
  GitBranch,
  GitMerge,
  Layers,
  Lightbulb,
  Link2,
  ListVideo,
  Move,
  Package,
  Palette,
  RectangleHorizontal,
  Scissors,
  Search,
  Sparkles,
  Users,
  Wand2,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { GRADE_LOOKS } from "@/data/color";
import { CUT_TYPES } from "@/data/editing";
import { QUIZ_QUESTIONS } from "@/data/quiz";
import { SOUND_LAYERS } from "@/data/sound";
import { AGENTS, STATS, STUDIO_VERSION, TIERS } from "@/data/studio";
import { DELIVERY_ALL_IDS } from "@/data/delivery";
import { useProgress } from "@/lib/progress";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/")({
  component: HomePage,
});

function HomePage() {
  const completedTiers = useProgress((s) => s.completedTiers);
  const quizBestScore = useProgress((s) => s.quizBestScore);
  const masteredCards = useProgress((s) => s.masteredCards);
  const graduatedAt = useProgress((s) => s.graduatedAt);
  const deliveryChecked = useProgress((s) => s.deliveryChecked);
  const progress = Math.round((completedTiers.length / TIERS.length) * 100);

  return (
    <div className="space-y-12">
      <section className="grid gap-8 lg:grid-cols-[1.2fr_0.8fr] lg:items-end">
        <div className="space-y-5">
          <Badge variant="teal">v{STUDIO_VERSION} · Educational companion</Badge>
          <h1 className="max-w-xl text-balance text-3xl font-semibold tracking-tight sm:text-4xl lg:text-[2.75rem] lg:leading-[1.1]">
            Learn the Cinematic Studio without drowning in agents.
          </h1>
          <p className="max-w-xl text-base text-muted leading-relaxed sm:text-lg">
            Walk the craft path, practice, then graduate — stills-first from
            Bible to sound.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link
              to="/graduate"
              className={cn(
                "inline-flex h-12 items-center justify-center gap-2 rounded-lg px-6 text-base font-semibold",
                "bg-teal text-bg transition-all hover:bg-teal/90 active:scale-[0.98]",
              )}
            >
              {graduatedAt ? "View certificate" : "Graduate"}
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              to="/craft"
              className={cn(
                "inline-flex h-12 items-center justify-center gap-2 rounded-lg px-6 text-base font-medium",
                "border border-border bg-elevated text-fg transition-all hover:border-border-strong active:scale-[0.98]",
              )}
            >
              Craft hub
            </Link>
            <Link
              to="/extend"
              className={cn(
                "inline-flex h-12 items-center justify-center gap-2 rounded-lg px-6 text-base font-medium",
                "border border-border bg-elevated text-fg transition-all hover:border-border-strong active:scale-[0.98]",
              )}
            >
              Extend Lab
              <Link2 className="h-4 w-4" />
            </Link>
            <Link
              to="/delivery"
              className={cn(
                "inline-flex h-12 items-center justify-center gap-2 rounded-lg px-6 text-base font-medium",
                "border border-border bg-elevated text-fg transition-all hover:border-border-strong active:scale-[0.98]",
              )}
            >
              Delivery
              <ClipboardCheck className="h-4 w-4" />
            </Link>
          </div>
        </div>

        <Card className="bg-elevated/40">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Clapperboard className="h-4 w-4 text-teal" />
              Your progress
            </CardTitle>
            <CardDescription>
              {completedTiers.length} of {TIERS.length} tiers
              {quizBestScore > 0 && (
                <> · quiz {quizBestScore}/{QUIZ_QUESTIONS.length}</>
              )}
              {masteredCards.length > 0 && (
                <> · cards {masteredCards.length}/{AGENTS.length}</>
              )}
              {graduatedAt && <> · graduated</>}
              {deliveryChecked.length > 0 && (
                <> · delivery {deliveryChecked.length}/{DELIVERY_ALL_IDS.length}</>
              )}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="h-2 overflow-hidden rounded-full bg-border">
              <div
                className="h-full rounded-full bg-teal transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className="font-mono text-2xl font-semibold tabular-nums text-fg">
              {progress}%
            </p>
            <ul className="space-y-2">
              {TIERS.map((t) => {
                const done = completedTiers.includes(t.id);
                return (
                  <li
                    key={t.id}
                    className="flex items-center gap-2 text-sm text-muted"
                  >
                    <CheckCircle2
                      className={
                        done ? "h-4 w-4 text-success" : "h-4 w-4 text-subtle"
                      }
                    />
                    <span className={done ? "text-fg" : undefined}>
                      Tier {t.id}: {t.title}
                    </span>
                  </li>
                );
              })}
            </ul>
          </CardContent>
        </Card>
      </section>

      <section className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
        {[
          ...STATS,
          { label: "Layers", value: String(SOUND_LAYERS.length) },
          { label: "Cuts", value: String(CUT_TYPES.length) },
          { label: "Looks", value: String(GRADE_LOOKS.length) },
          {
            label: "Graduate",
            value: graduatedAt ? "Yes" : "—",
          },
        ].map((s) => (
          <div
            key={s.label}
            className="rounded-xl border border-border bg-surface px-4 py-5"
          >
            <p className="font-mono text-2xl font-semibold tabular-nums tracking-tight">
              {s.value}
            </p>
            <p className="mt-1 text-xs uppercase tracking-wide text-muted">
              {s.label}
            </p>
          </div>
        ))}
      </section>

      <section className="space-y-4">
        <div className="flex items-end justify-between gap-4">
          <div>
            <h2 className="text-xl font-semibold tracking-tight">
              Three tiers. Zero overwhelm.
            </h2>
            <p className="mt-1 text-sm text-muted">
              Start simple. Scale only when you are ready.
            </p>
          </div>
          <Link
            to="/learn"
            className="hidden text-sm text-teal hover:underline sm:inline"
          >
            Open path
          </Link>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          {TIERS.map((t) => (
            <Card key={t.id} className="flex flex-col">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <Badge variant={t.id === 1 ? "teal" : "outline"}>
                    Tier {t.id}
                  </Badge>
                  <span className="text-xs text-subtle">{t.minutes}</span>
                </div>
                <CardTitle className="mt-2">{t.title}</CardTitle>
                <CardDescription>{t.subtitle}</CardDescription>
              </CardHeader>
              <CardContent className="mt-auto">
                <p className="text-sm leading-relaxed text-muted">{t.outcome}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {[
          {
            to: "/extend" as const,
            icon: Link2,
            title: "Extend Lab",
            body: "Multi-clip chains, plate gates, copy packet.",
          },
          {
            to: "/delivery" as const,
            icon: ClipboardCheck,
            title: "Delivery checklist",
            body: "Ship gate: pre-flight through export. Copy report.",
          },
          {
            to: "/graduate" as const,
            icon: Award,
            title: "Graduate",
            body: "Certificate after tiers, quiz 7+, cards 8+.",
          },
          {
            to: "/sound" as const,
            icon: AudioLines,
            title: "Sound design",
            body: "Layers, mix hierarchy, copy-ready briefs.",
          },
          {
            to: "/editing" as const,
            icon: Scissors,
            title: "Editing & pacing",
            body: "Cuts, teaser spine, stills montage.",
          },
          {
            to: "/search" as const,
            icon: Search,
            title: "Search Academy",
            body: "Find pages, glossary, agents, scenarios.",
          },
          {
            to: "/pack" as const,
            icon: Package,
            title: "Project pack",
            body: "Export Bible + DNA + DoP + shots.",
          },
          {
            to: "/craft" as const,
            icon: Wand2,
            title: "Craft hub",
            body: "Full path 01–08 + master cheat.",
          },
          {
            to: "/color" as const,
            icon: Palette,
            title: "Color & grading",
            body: "Looks, skin protection, grade lines.",
          },
          {
            to: "/movement" as const,
            icon: Move,
            title: "Camera movement",
            body: "Static to push-in for short clips.",
          },
          {
            to: "/lenses" as const,
            icon: Camera,
            title: "Lenses & focal length",
            body: "24–85mm bands, DOF, anamorphic.",
          },
          {
            to: "/aspect" as const,
            icon: RectangleHorizontal,
            title: "Aspect ratios",
            body: "2.39 scope to 9:16 vertical.",
          },
          {
            to: "/composition" as const,
            icon: Frame,
            title: "Composition & framing",
            body: "Shot sizes, thirds, recipes.",
          },
          {
            to: "/lighting" as const,
            icon: Lightbulb,
            title: "Lighting basics",
            body: "Key, fill, rim, setups.",
          },
          {
            to: "/dop" as const,
            icon: Aperture,
            title: "DoP visual card",
            body: "Lock the look in one card.",
          },
          {
            to: "/shots" as const,
            icon: ListVideo,
            title: "Shot list",
            body: "Numbered stills + export.",
          },
          {
            to: "/bible" as const,
            icon: BookText,
            title: "Mini Production Bible",
            body: "Charter and gates.",
          },
          {
            to: "/consistency" as const,
            icon: Cpu,
            title: "Video consistency",
            body: "DNA → plate → extend → QA.",
          },
          {
            to: "/recap" as const,
            icon: Film,
            title: "Last-frame recap",
            body: "Recap + continuity_state.",
          },
          {
            to: "/scenarios" as const,
            icon: Sparkles,
            title: "Scenarios",
            body: "End-to-end playbooks.",
          },
          {
            to: "/dna" as const,
            icon: Fingerprint,
            title: "Character DNA",
            body: "Inject blocks + plates.",
          },
          {
            to: "/lab" as const,
            icon: FlaskConical,
            title: "Prompt lab",
            body: "Ultimate Template stills.",
          },
          {
            to: "/glossary" as const,
            icon: BookMarked,
            title: "Glossary",
            body: "Studio terms plain.",
          },
          {
            to: "/learn" as const,
            icon: BookOpen,
            title: "Learn path",
            body: "Tiers and prompts.",
          },
          {
            to: "/budget" as const,
            icon: Calculator,
            title: "Budget calculator",
            body: "Stills + video rates.",
          },
          {
            to: "/pricing" as const,
            icon: DollarSign,
            title: "Grok pricing",
            body: "API list rates.",
          },
          {
            to: "/docs" as const,
            icon: Code2,
            title: "Integration API",
            body: "Chat, Imagine, voice.",
          },
          {
            to: "/workflows" as const,
            icon: GitMerge,
            title: "Workflows",
            body: "Agent chains.",
          },
          {
            to: "/agents" as const,
            icon: Users,
            title: "Agent roster",
            body: "25 specialists.",
          },
          {
            to: "/pipeline" as const,
            icon: GitBranch,
            title: "Pipeline map",
            body: "Bible → QA.",
          },
          {
            to: "/quiz" as const,
            icon: CircleHelp,
            title: "Quiz",
            body: "10 questions.",
          },
          {
            to: "/cards" as const,
            icon: Layers,
            title: "Flashcards",
            body: "Activation drills.",
          },
        ].map(({ to, icon: Icon, title, body }) => (
          <Link key={to} to={to} className="group">
            <Card className="h-full transition-colors group-hover:border-border-strong group-hover:bg-elevated/30">
              <CardHeader>
                <span className="mb-2 flex h-9 w-9 items-center justify-center rounded-lg border border-border bg-bg">
                  <Icon className="h-4 w-4 text-teal" />
                </span>
                <CardTitle className="text-base">{title}</CardTitle>
                <CardDescription>{body}</CardDescription>
              </CardHeader>
            </Card>
          </Link>
        ))}
      </section>
    </div>
  );
}
