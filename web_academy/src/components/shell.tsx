import { Link, useRouterState } from "@tanstack/react-router";
import {
  Aperture,
  AudioLines,
  Award,
  BookMarked,
  BookOpen,
  BookText,
  Calculator,
  Camera,
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
  LayoutDashboard,
  Lightbulb,
  ListVideo,
  Menu,
  Move,
  Package,
  Palette,
  RectangleHorizontal,
  Scissors,
  Search,
  Sparkles,
  Users,
  Wand2,
  X,
} from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

const NAV = [
  { to: "/", label: "Home", icon: LayoutDashboard },
  { to: "/search", label: "Search", icon: Search },
  { to: "/learn", label: "Learn", icon: BookOpen },
  { to: "/craft", label: "Craft", icon: Wand2 },
  { to: "/pack", label: "Pack", icon: Package },
  { to: "/delivery", label: "Delivery", icon: ClipboardCheck },
  { to: "/graduate", label: "Graduate", icon: Award },
  { to: "/lighting", label: "Lighting", icon: Lightbulb },
  { to: "/composition", label: "Framing", icon: Frame },
  { to: "/aspect", label: "Aspect", icon: RectangleHorizontal },
  { to: "/lenses", label: "Lenses", icon: Camera },
  { to: "/movement", label: "Movement", icon: Move },
  { to: "/color", label: "Color", icon: Palette },
  { to: "/editing", label: "Editing", icon: Scissors },
  { to: "/sound", label: "Sound", icon: AudioLines },
  { to: "/bible", label: "Bible", icon: BookText },
  { to: "/dop", label: "DoP", icon: Aperture },
  { to: "/shots", label: "Shots", icon: ListVideo },
  { to: "/scenarios", label: "Scenarios", icon: Sparkles },
  { to: "/consistency", label: "Consistency", icon: Cpu },
  { to: "/glossary", label: "Glossary", icon: BookMarked },
  { to: "/dna", label: "DNA", icon: Fingerprint },
  { to: "/recap", label: "Recap", icon: Film },
  { to: "/lab", label: "Lab", icon: FlaskConical },
  { to: "/agents", label: "Agents", icon: Users },
  { to: "/workflows", label: "Workflows", icon: GitMerge },
  { to: "/docs", label: "API", icon: Code2 },
  { to: "/pricing", label: "Pricing", icon: DollarSign },
  { to: "/budget", label: "Budget", icon: Calculator },
  { to: "/pipeline", label: "Pipeline", icon: GitBranch },
  { to: "/quiz", label: "Quiz", icon: CircleHelp },
  { to: "/cards", label: "Cards", icon: Layers },
] as const;

export function Shell({ children }: { children: React.ReactNode }) {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const [open, setOpen] = useState(false);

  return (
    <div className="min-h-dvh bg-bg text-fg">
      <div
        aria-hidden
        className="pointer-events-none fixed inset-0 -z-10"
        style={{
          background:
            "radial-gradient(ellipse 80% 50% at 50% -20%, color-mix(in oklab, #2dd4bf 8%, transparent), transparent), radial-gradient(ellipse 60% 40% at 100% 0%, color-mix(in oklab, #e4e4e7 4%, transparent), transparent)",
        }}
      />

      <header className="sticky top-0 z-40 border-b border-border/80 bg-bg/85 backdrop-blur-md">
        <div className="mx-auto flex h-14 max-w-6xl items-center justify-between gap-3 px-4 sm:px-6">
          <Link to="/" className="flex min-w-0 items-center gap-2.5">
            <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-border bg-elevated">
              <Clapperboard className="h-4 w-4 text-teal" />
            </span>
            <span className="truncate">
              <span className="block text-sm font-semibold tracking-tight">
                Studio Academy
              </span>
              <span className="hidden text-[11px] text-subtle sm:block">
                Grok Imagine Cinematic Studio
              </span>
            </span>
          </Link>

          <div className="flex items-center gap-1">
            <Link
              to="/search"
              className={cn(
                "inline-flex h-9 w-9 items-center justify-center rounded-lg",
                pathname === "/search"
                  ? "bg-elevated text-fg"
                  : "text-muted hover:bg-elevated/60 hover:text-fg",
              )}
              aria-label="Search"
            >
              <Search className="h-4 w-4" />
            </Link>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="shrink-0"
              aria-label={open ? "Close menu" : "Open menu"}
              onClick={() => setOpen((v) => !v)}
            >
              {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
          </div>
        </div>

        {open && (
          <nav className="max-h-[70dvh] overflow-y-auto border-t border-border px-4 py-3">
            <div className="mx-auto grid max-w-6xl grid-cols-2 gap-1 sm:grid-cols-3 lg:grid-cols-4">
              {NAV.map(({ to, label, icon: Icon }) => {
                const active = pathname === to;
                return (
                  <Link
                    key={to}
                    to={to}
                    onClick={() => setOpen(false)}
                    className={cn(
                      "inline-flex h-11 items-center gap-2 rounded-lg px-3 text-sm",
                      active
                        ? "bg-elevated text-fg"
                        : "text-muted hover:bg-elevated/60",
                    )}
                  >
                    <Icon className="h-4 w-4 shrink-0" />
                    {label}
                  </Link>
                );
              })}
            </div>
          </nav>
        )}
      </header>

      <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 sm:py-10">
        {children}
      </main>

      <footer className="border-t border-border/80 py-8">
        <div className="mx-auto flex max-w-6xl flex-col gap-2 px-4 text-sm text-subtle sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <p>Studio Academy — educational companion for Cinematic Studio v3.9.1</p>
          <p className="font-mono text-xs">Independent of xAI · MIT-style learning tool</p>
        </div>
      </footer>
    </div>
  );
}
