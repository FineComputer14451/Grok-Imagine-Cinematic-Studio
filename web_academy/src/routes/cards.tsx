import { createFileRoute } from "@tanstack/react-router";
import {
  Check,
  ChevronLeft,
  ChevronRight,
  Layers,
  RotateCcw,
  Shuffle,
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
import { AGENTS, type Agent } from "@/data/studio";
import { useProgress } from "@/lib/progress";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/cards")({
  component: CardsPage,
});

const CATEGORIES: { id: Agent["category"] | "all"; label: string }[] = [
  { id: "all", label: "All" },
  { id: "leadership", label: "Leadership" },
  { id: "creative", label: "Creative" },
  { id: "production", label: "Production" },
  { id: "post", label: "Post" },
  { id: "special", label: "Special" },
];

function shuffleIds(ids: string[]) {
  const arr = [...ids];
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

function CardsPage() {
  const masteredCards = useProgress((s) => s.masteredCards);
  const markMastered = useProgress((s) => s.markMastered);
  const unmarkMastered = useProgress((s) => s.unmarkMastered);

  const [cat, setCat] = useState<(typeof CATEGORIES)[number]["id"]>("all");
  const [hideMastered, setHideMastered] = useState(false);
  const [order, setOrder] = useState<string[]>(() => AGENTS.map((a) => a.id));
  const [index, setIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);

  const pool = useMemo(() => {
    return order
      .map((id) => AGENTS.find((a) => a.id === id)!)
      .filter(Boolean)
      .filter((a) => (cat === "all" ? true : a.category === cat))
      .filter((a) => (hideMastered ? !masteredCards.includes(a.id) : true));
  }, [order, cat, hideMastered, masteredCards]);

  const safeIndex = pool.length === 0 ? 0 : Math.min(index, pool.length - 1);
  const agent = pool[safeIndex];
  const mastered = agent ? masteredCards.includes(agent.id) : false;
  const masteryPct = Math.round((masteredCards.length / AGENTS.length) * 100);

  function go(delta: number) {
    if (pool.length === 0) return;
    setFlipped(false);
    setIndex((i) => {
      const next = i + delta;
      if (next < 0) return pool.length - 1;
      if (next >= pool.length) return 0;
      return next;
    });
  }

  function reshuffle() {
    setOrder(shuffleIds(AGENTS.map((a) => a.id)));
    setIndex(0);
    setFlipped(false);
  }

  function resetDeck() {
    setOrder(AGENTS.map((a) => a.id));
    setIndex(0);
    setFlipped(false);
  }

  return (
    <div className="mx-auto max-w-2xl space-y-8">
      <div>
        <Badge variant="teal">Study mode</Badge>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">
          Activation flashcards
        </h1>
        <p className="mt-2 text-muted">
          Flip each card to reveal the activation command. Mark agents you know.
          {masteredCards.length > 0 && (
            <>
              {" "}
              <span className="font-mono text-fg">
                {masteredCards.length}/{AGENTS.length}
              </span>{" "}
              mastered.
            </>
          )}
        </p>
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs text-subtle">
          <span>Mastery</span>
          <span className="font-mono tabular-nums">{masteryPct}%</span>
        </div>
        <div className="h-1.5 overflow-hidden rounded-full bg-border">
          <div
            className="h-full rounded-full bg-teal transition-all duration-300"
            style={{ width: `${masteryPct}%` }}
          />
        </div>
      </div>

      <div className="flex flex-wrap gap-1.5">
        {CATEGORIES.map((c) => (
          <button
            key={c.id}
            type="button"
            onClick={() => {
              setCat(c.id);
              setIndex(0);
              setFlipped(false);
            }}
            className={cn(
              "h-9 rounded-md border px-3 text-xs font-medium transition-colors",
              cat === c.id
                ? "border-teal/40 bg-teal/10 text-teal"
                : "border-border bg-surface text-muted hover:text-fg",
            )}
          >
            {c.label}
          </button>
        ))}
      </div>

      <div className="flex flex-wrap gap-2">
        <Button type="button" variant="secondary" size="sm" onClick={reshuffle}>
          <Shuffle className="h-3.5 w-3.5" />
          Shuffle
        </Button>
        <Button type="button" variant="secondary" size="sm" onClick={resetDeck}>
          <RotateCcw className="h-3.5 w-3.5" />
          Reset order
        </Button>
        <Button
          type="button"
          variant={hideMastered ? "teal" : "secondary"}
          size="sm"
          onClick={() => {
            setHideMastered((v) => !v);
            setIndex(0);
            setFlipped(false);
          }}
        >
          {hideMastered ? "Showing unmastered" : "Hide mastered"}
        </Button>
      </div>

      {pool.length === 0 ? (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Deck empty</CardTitle>
            <CardDescription>
              All cards in this filter are mastered. Turn off “Hide mastered” or
              pick another category.
            </CardDescription>
          </CardHeader>
        </Card>
      ) : (
        <>
          <p className="text-sm text-subtle">
            Card {safeIndex + 1} of {pool.length}
            {cat !== "all" ? ` · ${cat}` : ""}
          </p>

          <button
            type="button"
            onClick={() => setFlipped((f) => !f)}
            className="group w-full text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal/40 rounded-xl"
            aria-label={flipped ? "Show agent name" : "Reveal activation command"}
          >
            <div
              className={cn(
                "relative min-h-[240px] rounded-xl border p-6 transition-colors sm:min-h-[280px] sm:p-8",
                flipped
                  ? "border-teal/40 bg-teal/5"
                  : "border-border bg-surface group-hover:border-border-strong",
                mastered && "ring-1 ring-success/30",
              )}
            >
              <div className="mb-4 flex items-center justify-between gap-2">
                <Badge variant="outline">T{agent.tier}+</Badge>
                <span className="text-[11px] uppercase tracking-wide text-subtle">
                  {flipped ? "Command" : "Agent"} · tap to flip
                </span>
              </div>

              {!flipped ? (
                <div className="space-y-3">
                  <h2 className="text-2xl font-semibold tracking-tight sm:text-3xl">
                    {agent.name}
                  </h2>
                  <p className="text-sm text-muted leading-relaxed sm:text-base">
                    {agent.role}
                  </p>
                  <div className="flex flex-wrap gap-1.5 pt-2">
                    {agent.skills.slice(0, 3).map((s) => (
                      <Badge key={s} variant="default">
                        {s}
                      </Badge>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="flex h-full flex-col justify-center gap-4">
                  <code className="block break-all font-mono text-lg font-semibold text-teal sm:text-xl">
                    {agent.activation}
                  </code>
                  <p className="text-sm text-muted">{agent.name}</p>
                </div>
              )}
            </div>
          </button>

          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex gap-2">
              <Button
                type="button"
                variant="secondary"
                size="icon"
                aria-label="Previous card"
                onClick={() => go(-1)}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button
                type="button"
                variant="secondary"
                size="icon"
                aria-label="Next card"
                onClick={() => go(1)}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>

            <div className="flex flex-wrap gap-2">
              {flipped && (
                <CopyButton text={agent.activation} label="Copy command" />
              )}
              <Button
                type="button"
                variant={mastered ? "teal" : "secondary"}
                size="sm"
                onClick={() =>
                  mastered ? unmarkMastered(agent.id) : markMastered(agent.id)
                }
              >
                <Check className="h-3.5 w-3.5" />
                {mastered ? "Mastered" : "Mark mastered"}
              </Button>
            </div>
          </div>

          <Card className="bg-elevated/30">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-sm">
                <Layers className="h-4 w-4 text-teal" />
                Study tip
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-muted leading-relaxed">
              Say the activation out loud before you flip. Mark mastered only
              when you can recall the command from the agent name alone.
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
