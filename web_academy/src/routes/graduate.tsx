import { createFileRoute, Link } from "@tanstack/react-router";
import { Award, Check, Circle } from "lucide-react";
import { useMemo } from "react";
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
import { QUIZ_QUESTIONS } from "@/data/quiz";
import { AGENTS, TIERS } from "@/data/studio";
import { useProgress } from "@/lib/progress";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/graduate")({
  component: GraduatePage,
});

const QUIZ_PASS = 9;
const CARDS_PASS = 8;

function GraduatePage() {
  const completedTiers = useProgress((s) => s.completedTiers);
  const quizBestScore = useProgress((s) => s.quizBestScore);
  const masteredCards = useProgress((s) => s.masteredCards);
  const graduateName = useProgress((s) => s.graduateName);
  const graduatedAt = useProgress((s) => s.graduatedAt);
  const setGraduateName = useProgress((s) => s.setGraduateName);
  const claimGraduate = useProgress((s) => s.claimGraduate);

  const reqs = useMemo(() => {
    const tiersDone = TIERS.every((t) => completedTiers.includes(t.id));
    const quizDone = quizBestScore >= QUIZ_PASS;
    const cardsDone = masteredCards.length >= CARDS_PASS;
    return [
      {
        id: "tiers",
        label: `Complete all ${TIERS.length} learn tiers`,
        detail: `${completedTiers.length}/${TIERS.length} marked complete`,
        done: tiersDone,
        href: "/learn" as const,
      },
      {
        id: "quiz",
        label: `Score ${QUIZ_PASS}+ on the quiz`,
        detail: `Best ${quizBestScore}/${QUIZ_QUESTIONS.length}`,
        done: quizDone,
        href: "/quiz" as const,
      },
      {
        id: "cards",
        label: `Master ${CARDS_PASS}+ flashcards`,
        detail: `${masteredCards.length}/${AGENTS.length} mastered`,
        done: cardsDone,
        href: "/cards" as const,
      },
    ];
  }, [completedTiers, quizBestScore, masteredCards]);

  const eligible = reqs.every((r) => r.done);
  const progressPct = Math.round(
    (reqs.filter((r) => r.done).length / reqs.length) * 100,
  );

  const displayName =
    graduateName.trim() || "Studio Academy Learner";

  const certText = `CERTIFICATE OF COMPLETION
Studio Academy — Grok Imagine Cinematic Studio (educational companion)

This certifies that
${displayName}
has completed the Studio Academy learning path:
• Learn tiers (${TIERS.length}/${TIERS.length})
• Quiz best score ${Math.max(quizBestScore, QUIZ_PASS)}+ / ${QUIZ_QUESTIONS.length}
• Flashcards mastered ${Math.max(masteredCards.length, CARDS_PASS)}+

Craft path covered: lighting · framing · aspect · lenses · movement · color · editing · sound
Production tools: Bible · DNA · DoP · shots · pack · consistency

${graduatedAt ? `Claimed: ${new Date(graduatedAt).toLocaleString()}` : "Status: eligible / preview"}
Independent educational tool · not an official xAI credential
`;

  return (
    <div className="space-y-8">
      <div>
        <Badge variant="teal">Milestone</Badge>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">
          Graduate
        </h1>
        <p className="mt-2 max-w-2xl text-muted leading-relaxed">
          Finish the learn path, pass the quiz, and master activation cards —
          then claim a completion certificate you can copy.
        </p>
      </div>

      <div className="rounded-xl border border-border bg-surface px-4 py-4">
        <div className="flex items-center justify-between gap-3 text-sm">
          <span className="text-muted">Requirements</span>
          <span className="font-mono text-teal">{progressPct}%</span>
        </div>
        <div className="mt-2 h-2 overflow-hidden rounded-full bg-border">
          <div
            className="h-full rounded-full bg-teal transition-all duration-500"
            style={{ width: `${progressPct}%` }}
          />
        </div>
      </div>

      <ul className="space-y-2">
        {reqs.map((r) => (
          <li key={r.id}>
            <Link
              to={r.href}
              className={cn(
                "flex items-start gap-3 rounded-xl border px-4 py-3.5 transition-colors",
                r.done
                  ? "border-teal/30 bg-teal/5"
                  : "border-border bg-surface hover:border-border-strong",
              )}
            >
              {r.done ? (
                <Check className="mt-0.5 h-5 w-5 shrink-0 text-success" />
              ) : (
                <Circle className="mt-0.5 h-5 w-5 shrink-0 text-subtle" />
              )}
              <div className="min-w-0 flex-1">
                <p className="font-medium text-fg">{r.label}</p>
                <p className="mt-0.5 text-sm text-muted">{r.detail}</p>
              </div>
            </Link>
          </li>
        ))}
      </ul>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Your name on the certificate</CardTitle>
          <CardDescription>Stored locally in this browser only</CardDescription>
        </CardHeader>
        <CardContent>
          <input
            value={graduateName}
            onChange={(e) => setGraduateName(e.target.value)}
            placeholder="Name or handle"
            className="h-11 w-full max-w-md rounded-lg border border-border bg-bg px-3 text-sm text-fg placeholder:text-subtle outline-none focus:border-border-strong focus:ring-2 focus:ring-teal/30"
          />
        </CardContent>
      </Card>

      {/* Certificate visual */}
      <div
        className={cn(
          "relative overflow-hidden rounded-2xl border-2 px-6 py-10 sm:px-10",
          eligible
            ? "border-teal/50 bg-gradient-to-b from-teal/10 via-surface to-bg"
            : "border-border bg-surface opacity-90",
        )}
      >
        <div className="pointer-events-none absolute inset-0 opacity-30"
          style={{
            background:
              "radial-gradient(ellipse 70% 50% at 50% 0%, color-mix(in oklab, #2dd4bf 25%, transparent), transparent)",
          }}
        />
        <div className="relative mx-auto max-w-lg text-center">
          <Award
            className={cn(
              "mx-auto h-10 w-10",
              eligible ? "text-teal" : "text-subtle",
            )}
          />
          <p className="mt-4 font-mono text-[11px] uppercase tracking-[0.2em] text-subtle">
            Certificate of completion
          </p>
          <h2 className="mt-3 text-2xl font-semibold tracking-tight text-fg sm:text-3xl">
            Studio Academy
          </h2>
          <p className="mt-2 text-sm text-muted">
            Grok Imagine Cinematic Studio · educational companion
          </p>
          <div className="mx-auto my-6 h-px w-24 bg-border" />
          <p className="text-xs uppercase tracking-wide text-subtle">
            Awarded to
          </p>
          <p className="mt-2 text-xl font-medium text-fg sm:text-2xl">
            {displayName}
          </p>
          <p className="mx-auto mt-4 max-w-sm text-sm leading-relaxed text-muted">
            for completing the learn path, demonstrating Studio fundamentals on
            the quiz, and mastering activation flashcards.
          </p>
          <div className="mt-6 flex flex-wrap justify-center gap-2 text-[11px] text-subtle">
            <span>Craft 01–08</span>
            <span>·</span>
            <span>Stills-first</span>
            <span>·</span>
            <span>DNA · DoP · Pack</span>
          </div>
          {graduatedAt && (
            <p className="mt-4 font-mono text-xs text-teal">
              Claimed {new Date(graduatedAt).toLocaleDateString()}
            </p>
          )}
          {!eligible && (
            <p className="mt-6 text-xs text-muted">
              Preview only — finish requirements to claim
            </p>
          )}
        </div>
      </div>

      <div className="flex flex-wrap gap-3">
        <Button
          type="button"
          disabled={!eligible}
          onClick={() => claimGraduate()}
          className="gap-2"
        >
          <Award className="h-4 w-4" />
          {graduatedAt ? "Update claim timestamp" : "Claim certificate"}
        </Button>
        <CopyButton text={certText} label="Copy certificate text" />
      </div>

      {!eligible && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Suggested next steps</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-2 text-sm">
            {!reqs[0].done && (
              <Link to="/learn" className="text-teal hover:underline">
                Finish learn tiers
              </Link>
            )}
            {!reqs[1].done && (
              <Link to="/quiz" className="text-teal hover:underline">
                Take the quiz
              </Link>
            )}
            {!reqs[2].done && (
              <Link to="/cards" className="text-teal hover:underline">
                Master flashcards
              </Link>
            )}
            <Link to="/craft" className="text-teal hover:underline">
              Craft hub
            </Link>
            <Link to="/pack" className="text-teal hover:underline">
              Project pack
            </Link>
          </CardContent>
        </Card>
      )}

      <p className="text-xs text-subtle leading-relaxed">
        This is a fun learning milestone inside Studio Academy. It is not an
        official xAI, Grok, or school credential.
      </p>
    </div>
  );
}
