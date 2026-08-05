import { createFileRoute, Link } from "@tanstack/react-router";
import {
  ArrowRight,
  BookOpen,
  CheckCircle2,
  CircleHelp,
  RotateCcw,
  XCircle,
} from "lucide-react";
import { useMemo, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { QUIZ_QUESTIONS, scoreBand } from "@/data/quiz";
import { useProgress } from "@/lib/progress";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/quiz")({
  component: QuizPage,
});

type Phase = "intro" | "question" | "feedback" | "results";

function tally(answers: (number | null)[]) {
  return QUIZ_QUESTIONS.reduce(
    (acc, q, i) => acc + (answers[i] === q.answer ? 1 : 0),
    0,
  );
}

function QuizPage() {
  const recordQuiz = useProgress((s) => s.recordQuiz);
  const quizBestScore = useProgress((s) => s.quizBestScore);
  const quizAttempts = useProgress((s) => s.quizAttempts);

  const [phase, setPhase] = useState<Phase>("intro");
  const [index, setIndex] = useState(0);
  const [selected, setSelected] = useState<number | null>(null);
  const [score, setScore] = useState(0);
  const [answers, setAnswers] = useState<(number | null)[]>(
    () => QUIZ_QUESTIONS.map(() => null),
  );

  const total = QUIZ_QUESTIONS.length;
  const q = QUIZ_QUESTIONS[index];
  const band = useMemo(() => scoreBand(score, total), [score, total]);

  function start() {
    setPhase("question");
    setIndex(0);
    setSelected(null);
    setScore(0);
    setAnswers(QUIZ_QUESTIONS.map(() => null));
  }

  function confirmAnswer() {
    if (selected === null || !q) return;
    const nextAnswers = [...answers];
    nextAnswers[index] = selected;
    setAnswers(nextAnswers);
    setScore(tally(nextAnswers));
    setPhase("feedback");
  }

  function next() {
    if (index + 1 >= total) {
      const final = tally(answers);
      setScore(final);
      recordQuiz(final);
      setPhase("results");
      return;
    }
    setIndex((i) => i + 1);
    setSelected(null);
    setPhase("question");
  }

  return (
    <div className="mx-auto max-w-2xl space-y-8">
      <div>
        <Badge variant="teal">Knowledge check</Badge>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">
          Studio Academy Quiz
        </h1>
        <p className="mt-2 text-muted">
          {total} questions across Tier 1–3. Scored, with explanations after each
          answer. Best score is saved on this device.
        </p>
      </div>

      {(phase === "question" || phase === "feedback") && (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs text-subtle">
            <span>
              Question {index + 1} of {total}
            </span>
            <span className="font-mono tabular-nums">
              {Math.round(
                ((index + (phase === "feedback" ? 1 : 0)) / total) * 100,
              )}
              %
            </span>
          </div>
          <div className="h-1.5 overflow-hidden rounded-full bg-border">
            <div
              className="h-full rounded-full bg-teal transition-all duration-300"
              style={{
                width: `${Math.round(((index + (phase === "feedback" ? 1 : 0)) / total) * 100)}%`,
              }}
            />
          </div>
        </div>
      )}

      {phase === "intro" && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <CircleHelp className="h-5 w-5 text-teal" />
              Ready when you are
            </CardTitle>
            <CardDescription>
              Multiple choice. One answer per question. You will see why after
              each pick.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-5">
            <ul className="grid gap-2 text-sm text-muted sm:grid-cols-3">
              <li className="rounded-lg border border-border bg-bg px-3 py-2">
                <span className="block font-medium text-fg">Tier 1</span>
                3 questions · foundations
              </li>
              <li className="rounded-lg border border-border bg-bg px-3 py-2">
                <span className="block font-medium text-fg">Tier 2</span>
                3 questions · two-agent
              </li>
              <li className="rounded-lg border border-border bg-bg px-3 py-2">
                <span className="block font-medium text-fg">Tier 3</span>
                4 questions · full pipeline
              </li>
            </ul>
            {(quizAttempts > 0 || quizBestScore > 0) && (
              <p className="text-sm text-muted">
                Best score:{" "}
                <span className="font-mono font-semibold text-fg">
                  {quizBestScore}/{total}
                </span>
                {quizAttempts > 0 && (
                  <span className="text-subtle">
                    {" "}
                    · {quizAttempts} attempt{quizAttempts === 1 ? "" : "s"}
                  </span>
                )}
              </p>
            )}
            <Button type="button" variant="teal" size="lg" onClick={start}>
              Start quiz
              <ArrowRight className="h-4 w-4" />
            </Button>
          </CardContent>
        </Card>
      )}

      {(phase === "question" || phase === "feedback") && q && (
        <Card>
          <CardHeader>
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant="outline">Tier {q.tier}</Badge>
              {phase === "feedback" &&
                (selected === q.answer ? (
                  <Badge
                    variant="teal"
                    className="border-success/30 bg-success/10 text-success"
                  >
                    Correct
                  </Badge>
                ) : (
                  <Badge className="border-danger/30 bg-danger/10 text-danger">
                    Incorrect
                  </Badge>
                ))}
            </div>
            <CardTitle className="mt-2 text-lg leading-snug sm:text-xl">
              {q.prompt}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div
              className="flex flex-col gap-2"
              role="radiogroup"
              aria-label="Answers"
            >
              {q.options.map((opt, i) => {
                const isSelected = selected === i;
                const isCorrect = i === q.answer;
                const showResult = phase === "feedback";
                return (
                  <button
                    key={opt}
                    type="button"
                    role="radio"
                    aria-checked={isSelected}
                    disabled={phase === "feedback"}
                    onClick={() => setSelected(i)}
                    className={cn(
                      "flex items-start gap-3 rounded-lg border px-3.5 py-3 text-left text-sm transition-colors",
                      !showResult &&
                        isSelected &&
                        "border-teal/50 bg-teal/10 text-fg",
                      !showResult &&
                        !isSelected &&
                        "border-border bg-bg text-muted hover:border-border-strong hover:text-fg",
                      showResult &&
                        isCorrect &&
                        "border-success/40 bg-success/10 text-fg",
                      showResult &&
                        isSelected &&
                        !isCorrect &&
                        "border-danger/40 bg-danger/10 text-fg",
                      showResult &&
                        !isCorrect &&
                        !isSelected &&
                        "border-border bg-bg text-subtle opacity-70",
                    )}
                  >
                    <span
                      className={cn(
                        "mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full border text-[11px] font-mono",
                        isSelected || (showResult && isCorrect)
                          ? "border-teal/50 text-teal"
                          : "border-border text-subtle",
                      )}
                    >
                      {String.fromCharCode(65 + i)}
                    </span>
                    <span className="flex-1 leading-relaxed">{opt}</span>
                    {showResult && isCorrect && (
                      <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-success" />
                    )}
                    {showResult && isSelected && !isCorrect && (
                      <XCircle className="mt-0.5 h-4 w-4 shrink-0 text-danger" />
                    )}
                  </button>
                );
              })}
            </div>

            {phase === "feedback" && (
              <div className="rounded-lg border border-border bg-elevated/40 px-3.5 py-3 text-sm text-muted leading-relaxed">
                <span className="font-medium text-fg">Why: </span>
                {q.explain}
              </div>
            )}

            <div className="flex flex-wrap gap-2 pt-1">
              {phase === "question" && (
                <Button
                  type="button"
                  variant="teal"
                  disabled={selected === null}
                  onClick={confirmAnswer}
                >
                  Check answer
                </Button>
              )}
              {phase === "feedback" && (
                <Button type="button" variant="teal" onClick={next}>
                  {index + 1 >= total ? "See results" : "Next question"}
                  <ArrowRight className="h-4 w-4" />
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {phase === "results" && (
        <Card className="border-teal/20">
          <CardHeader>
            <CardTitle className="text-xl">Your score</CardTitle>
            <CardDescription>
              Attempt finished. Best score updates if you beat it.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex flex-wrap items-end gap-4">
              <p className="font-mono text-5xl font-semibold tabular-nums tracking-tight">
                {score}
                <span className="text-2xl text-subtle">/{total}</span>
              </p>
              <div>
                <Badge
                  variant={
                    band.tone === "success"
                      ? "teal"
                      : band.tone === "amber"
                        ? "amber"
                        : "outline"
                  }
                  className={cn(
                    band.tone === "danger" &&
                      "border-danger/40 bg-danger/10 text-danger",
                    band.tone === "amber" &&
                      "border-amber/40 bg-amber/10 text-amber",
                  )}
                >
                  {band.label}
                </Badge>
                <p className="mt-2 max-w-sm text-sm text-muted">{band.detail}</p>
              </div>
            </div>

            <p className="text-sm text-subtle">
              Best on this device:{" "}
              <span className="font-mono text-fg">
                {Math.max(quizBestScore, score)}/{total}
              </span>
            </p>

            <div className="space-y-2">
              <p className="text-xs font-medium uppercase tracking-wide text-subtle">
                Review
              </p>
              <ul className="space-y-2">
                {QUIZ_QUESTIONS.map((item, i) => {
                  const picked = answers[i];
                  const ok = picked === item.answer;
                  return (
                    <li
                      key={item.id}
                      className="flex items-start gap-2 rounded-lg border border-border bg-bg px-3 py-2.5 text-sm"
                    >
                      {ok ? (
                        <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-success" />
                      ) : (
                        <XCircle className="mt-0.5 h-4 w-4 shrink-0 text-danger" />
                      )}
                      <div className="min-w-0">
                        <p className="text-fg leading-snug">{item.prompt}</p>
                        {!ok && (
                          <p className="mt-1 text-xs text-muted">
                            Answer: {item.options[item.answer]}
                          </p>
                        )}
                      </div>
                    </li>
                  );
                })}
              </ul>
            </div>

            <div className="flex flex-wrap gap-2">
              <Button type="button" variant="teal" onClick={start}>
                <RotateCcw className="h-4 w-4" />
                Retry quiz
              </Button>
              <Link
                to="/learn"
                className={cn(
                  "inline-flex h-10 items-center justify-center gap-2 rounded-md border border-border bg-elevated px-4 text-sm font-medium text-fg hover:border-border-strong",
                )}
              >
                <BookOpen className="h-4 w-4" />
                Open Learn path
              </Link>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
