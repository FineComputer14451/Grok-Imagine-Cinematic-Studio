import { createFileRoute, Link } from "@tanstack/react-router";
import {
  ArrowRight,
  Check,
  CheckCircle2,
  Circle,
  Film,
  GitBranch,
  Link2,
  Shield,
  ShieldCheck,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
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
import {
  ACADEMY_MODULE_VERSION,
  ACTIVATION_TEMPLATES,
  buildContinuityPacket,
  buildDirectorActivation,
  CONTINUITY_FIELDS,
  CONTINUITY_QUIZ,
  CONTINUITY_TAGLINE,
  CONTINUITY_VERSION,
  DRIFT_CHECKS,
  LESSONS,
  PACK_AGENTS,
  PIPELINE_STEPS,
  PROTOCOLS,
} from "@/data/continuity";
import { useProgress } from "@/lib/progress";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/continuity")({
  component: ContinuityPage,
});

const fieldClass =
  "mt-1.5 w-full min-w-0 rounded-lg border border-border bg-bg px-3 py-2.5 text-sm text-fg placeholder:text-subtle outline-none focus:border-border-strong focus:ring-2 focus:ring-teal/30";

function ContinuityPage() {
  const completedLessons = useProgress((s) => s.continuityLessons);
  const completeLesson = useProgress((s) => s.completeContinuityLesson);
  const quizBest = useProgress((s) => s.continuityQuizBest);
  const recordQuiz = useProgress((s) => s.recordContinuityQuiz);

  const [openLesson, setOpenLesson] = useState(LESSONS[0].id);
  const [values, setValues] = useState<Record<string, string>>(() =>
    Object.fromEntries(
      CONTINUITY_FIELDS.map((f) => [
        f.key,
        f.key === "project"
          ? "neon-alley-chase"
          : f.key === "clip_id"
            ? "clip_03"
            : f.key === "timeline_id"
              ? "main"
              : f.key === "last_frame_recap"
                ? "Runner mid-stride exit left · wet jacket · neon rim from right"
                : f.key === "wardrobe"
                  ? "black runner jacket · torn left sleeve · rain-dark"
                  : f.key === "props"
                    ? "phone in right hand · no weapon"
                    : f.key === "environment"
                      ? "neon alley · heavy rain · 02:00 · practical red sign"
                      : f.key === "emotion"
                        ? "panic cooling into focus · jaw set"
                        : f.key === "momentum"
                          ? "subject L→R · slight handheld push"
                          : f.key === "drift_notes"
                            ? "none · ready to extend"
                            : "",
      ]),
    ),
  );
  const [stamp, setStamp] = useState("{{timestamp}}");
  const [hydrated, setHydrated] = useState(false);
  const [project, setProject] = useState("neon-alley-chase");
  const [templateId, setTemplateId] = useState<
    (typeof ACTIVATION_TEMPLATES)[number]["id"]
  >(ACTIVATION_TEMPLATES[0].id);
  const [cleared, setCleared] = useState<string[]>(["environment", "emotion", "momentum"]);
  const [quizIdx, setQuizIdx] = useState(0);
  const [picked, setPicked] = useState<number | null>(null);
  const [quizScore, setQuizScore] = useState(0);
  const [quizDone, setQuizDone] = useState(false);
  const [ackRecap, setAckRecap] = useState(false);

  useEffect(() => {
    setHydrated(true);
    setStamp(new Date().toISOString());
  }, []);

  const packet = useMemo(
    () =>
      buildContinuityPacket(
        { ...values, project: project || values.project },
        stamp,
      ),
    [values, project, stamp],
  );
  const activation = useMemo(
    () => buildDirectorActivation(project),
    [project],
  );
  const templateBody = useMemo(() => {
    const t = ACTIVATION_TEMPLATES.find((x) => x.id === templateId)!;
    return t.body.replaceAll("{{project}}", project || "untitled-sequence");
  }, [templateId, project]);

  const lessonProgress = Math.round(
    (completedLessons.length / LESSONS.length) * 100,
  );
  const activeLesson = LESSONS.find((l) => l.id === openLesson) ?? LESSONS[0];
  const lessonsDone = hydrated ? completedLessons : [];
  const quizBestSafe = hydrated ? quizBest : 0;
  const lessonProgressSafe = hydrated ? lessonProgress : 0;
  const criticalOpen = DRIFT_CHECKS.filter(
    (d) => d.critical && !cleared.includes(d.id),
  );

  function toggleCheck(id: string) {
    setCleared((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
    );
  }

  function answerQuiz(option: number) {
    if (picked !== null || quizDone) return;
    setPicked(option);
    const q = CONTINUITY_QUIZ[quizIdx];
    const nextScore = quizScore + (option === q.answer ? 1 : 0);
    setQuizScore(nextScore);
    window.setTimeout(() => {
      if (quizIdx >= CONTINUITY_QUIZ.length - 1) {
        setQuizDone(true);
        recordQuiz(nextScore);
      } else {
        setQuizIdx((i) => i + 1);
        setPicked(null);
      }
    }, 650);
  }

  function resetQuiz() {
    setQuizIdx(0);
    setPicked(null);
    setQuizScore(0);
    setQuizDone(false);
  }

  return (
    <div className="min-w-0 space-y-10">
      <section className="space-y-5">
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="teal">Core pack · Sequence memory</Badge>
          <Badge variant="outline">Role Card v{CONTINUITY_VERSION}</Badge>
          <Badge variant="outline">Academy v{ACADEMY_MODULE_VERSION}</Badge>
        </div>
        <div className="grid gap-8 lg:grid-cols-[1.15fr_0.85fr] lg:items-end">
          <div className="min-w-0 space-y-4">
            <h1 className="max-w-2xl text-balance text-3xl font-semibold tracking-tight sm:text-4xl">
              Continuity
            </h1>
            <p className="max-w-2xl text-muted leading-relaxed sm:text-lg">
              {CONTINUITY_TAGLINE}
            </p>
            <p className="max-w-2xl text-sm text-subtle leading-relaxed">
              Educational module for Grok Imagine Cinematic Studio. Teaches
              LAST_FRAME_RECAP, continuity_state packets, drift severity, and
              handoff before every extend — pairs with Sequence, Extend, and
              Chain QA.
            </p>
            <div className="flex flex-wrap gap-3">
              <a
                href="#lessons"
                className={cn(
                  "inline-flex h-12 items-center justify-center gap-2 rounded-lg px-6 text-base font-semibold",
                  "bg-teal text-bg transition-all hover:bg-teal/90 active:scale-[0.98]",
                )}
              >
                Start lessons
                <ArrowRight className="h-4 w-4" />
              </a>
              <Link
                to="/consistency"
                className={cn(
                  "inline-flex h-12 items-center justify-center gap-2 rounded-lg px-6 text-base font-medium",
                  "border border-border bg-elevated text-fg transition-all hover:border-border-strong",
                )}
              >
                Consistency craft
              </Link>
              <Link
                to="/extend"
                className={cn(
                  "inline-flex h-12 items-center justify-center gap-2 rounded-lg px-6 text-base font-medium",
                  "border border-border bg-elevated text-fg transition-all hover:border-border-strong",
                )}
              >
                <Link2 className="h-4 w-4" />
                Extend
              </Link>
              <Link
                to="/delivery-pack"
                className={cn(
                  "inline-flex h-12 items-center justify-center gap-2 rounded-lg px-6 text-base font-medium",
                  "border border-border bg-elevated text-fg transition-all hover:border-border-strong",
                )}
              >
                Delivery pack
              </Link>
            </div>
          </div>

          <Card className="min-w-0 bg-elevated/40">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <ShieldCheck className="h-4 w-4 text-teal" />
                Module progress
              </CardTitle>
              <CardDescription>
                {lessonsDone.length} of {LESSONS.length} lessons
                {quizBestSafe > 0 && (
                  <>
                    {" "}
                    · quiz best {quizBestSafe}/{CONTINUITY_QUIZ.length}
                  </>
                )}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="h-2 overflow-hidden rounded-full bg-border">
                <div
                  className="h-full rounded-full bg-teal transition-all duration-500"
                  style={{ width: `${lessonProgressSafe}%` }}
                />
              </div>
              <p className="font-mono text-2xl font-semibold tabular-nums">
                {lessonProgressSafe}%
              </p>
              <label className="flex cursor-pointer items-start gap-3 rounded-lg border border-border bg-bg/60 p-3 text-sm">
                <input
                  type="checkbox"
                  className="mt-1 h-4 w-4 shrink-0 accent-teal"
                  checked={ackRecap}
                  onChange={(e) => setAckRecap(e.target.checked)}
                />
                <span className="min-w-0 text-muted leading-relaxed">
                  I will require{" "}
                  <strong className="text-fg">LAST_FRAME_RECAP</strong> and
                  block high drift before every extend.
                </span>
              </label>
            </CardContent>
          </Card>
        </div>
      </section>

      <Card className="min-w-0">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <GitBranch className="h-4 w-4 text-teal" />
            Continuity pipeline
          </CardTitle>
          <CardDescription>
            DNA → recap → state → drift gate → extend → update → handoff
          </CardDescription>
        </CardHeader>
        <CardContent className="overflow-x-auto">
          <div className="flex min-w-0 flex-col gap-2 sm:flex-row sm:flex-wrap">
            {PIPELINE_STEPS.map((s, i) => (
              <div
                key={s.id}
                className="flex min-w-0 flex-1 items-stretch gap-2 sm:min-w-[100px]"
              >
                <div className="min-w-0 flex-1 rounded-xl border border-border bg-surface px-3 py-3">
                  <p className="font-mono text-[11px] text-subtle">
                    {String(i + 1).padStart(2, "0")}
                  </p>
                  <p className="mt-1 text-sm font-medium">{s.label}</p>
                  <p className="mt-0.5 text-xs text-muted">{s.detail}</p>
                </div>
                {i < PIPELINE_STEPS.length - 1 && (
                  <span className="hidden items-center text-subtle lg:flex">
                    →
                  </span>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <section className="min-w-0 space-y-4">
        <div>
          <h2 className="text-xl font-semibold tracking-tight">
            Non-negotiable protocols
          </h2>
          <p className="mt-1 text-sm text-muted">
            Role Card v{CONTINUITY_VERSION} — load on multi-clip work
          </p>
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          {PROTOCOLS.map((p) => (
            <Card key={p.id} className="min-w-0">
              <CardHeader className="pb-2">
                <CardTitle className="font-mono text-sm text-teal">
                  {p.name}
                </CardTitle>
                <CardDescription className="text-sm text-fg/90">
                  {p.requirement}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-muted leading-relaxed">{p.why}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      <section id="lessons" className="min-w-0 space-y-4 scroll-mt-20">
        <div>
          <h2 className="text-xl font-semibold tracking-tight">Lessons</h2>
          <p className="mt-1 text-sm text-muted">
            {LESSONS.length} steps · mark complete as you practice
          </p>
        </div>
        <div className="grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
          <div className="min-w-0 space-y-2">
            {LESSONS.map((l) => {
              const done = lessonsDone.includes(l.id);
              const active = openLesson === l.id;
              return (
                <button
                  key={l.id}
                  type="button"
                  onClick={() => setOpenLesson(l.id)}
                  className={cn(
                    "flex w-full min-w-0 items-start gap-3 rounded-xl border px-3 py-3 text-left transition-colors",
                    active
                      ? "border-teal/40 bg-teal/10"
                      : "border-border bg-surface hover:border-border-strong",
                  )}
                >
                  {done ? (
                    <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-success" />
                  ) : (
                    <Circle className="mt-0.5 h-4 w-4 shrink-0 text-subtle" />
                  )}
                  <span className="min-w-0">
                    <span className="flex items-center gap-2">
                      <span className="font-mono text-[11px] text-subtle">
                        {l.step}
                      </span>
                      <span className="text-sm font-medium">{l.title}</span>
                    </span>
                    <span className="mt-0.5 block text-xs text-muted">
                      {l.minutes}
                    </span>
                  </span>
                </button>
              );
            })}
          </div>

          <Card className="min-w-0">
            <CardHeader>
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="font-mono text-[11px] text-subtle">
                    Lesson {activeLesson.step}
                  </p>
                  <CardTitle className="mt-1 text-lg">
                    {activeLesson.title}
                  </CardTitle>
                  <CardDescription className="mt-2">
                    {activeLesson.summary}
                  </CardDescription>
                </div>
                <Badge variant="outline">{activeLesson.minutes}</Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <ul className="space-y-2">
                {activeLesson.bullets.map((b) => (
                  <li
                    key={b}
                    className="flex gap-2 text-sm text-muted leading-relaxed"
                  >
                    <Check className="mt-0.5 h-3.5 w-3.5 shrink-0 text-teal" />
                    <span>{b}</span>
                  </li>
                ))}
              </ul>
              {activeLesson.drill && (
                <div className="rounded-lg border border-border bg-bg p-3">
                  <p className="text-xs font-medium uppercase tracking-wide text-subtle">
                    Drill
                  </p>
                  <p className="mt-1 text-sm text-fg leading-relaxed">
                    {activeLesson.drill}
                  </p>
                </div>
              )}
              <Button
                type="button"
                variant={
                  lessonsDone.includes(activeLesson.id) ? "outline" : "default"
                }
                disabled={!ackRecap}
                onClick={() => completeLesson(activeLesson.id)}
                className="w-full sm:w-auto"
              >
                {lessonsDone.includes(activeLesson.id)
                  ? "Completed"
                  : ackRecap
                    ? "Mark complete"
                    : "Ack recap rule above first"}
              </Button>
            </CardContent>
          </Card>
        </div>
      </section>

      <section className="min-w-0 space-y-4">
        <div>
          <h2 className="text-xl font-semibold tracking-tight">Pack agents</h2>
          <p className="mt-1 text-sm text-muted">
            Memory crew — guardian, identity, sequence, extend, QA
          </p>
        </div>
        <div className="grid gap-3 md:grid-cols-2">
          {PACK_AGENTS.map((a) => (
            <Card key={a.id} className="min-w-0">
              <CardHeader>
                <CardTitle className="text-base">{a.name}</CardTitle>
                <CardDescription>{a.role}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <code className="block break-all rounded-lg border border-border bg-bg px-3 py-2 font-mono text-xs text-teal">
                  {a.activation}
                </code>
                <div className="flex flex-wrap gap-1.5">
                  {a.skills.map((s) => (
                    <Badge key={s} variant="outline">
                      {s}
                    </Badge>
                  ))}
                </div>
                <CopyButton text={a.activation} label="Copy activation" />
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      <section className="min-w-0 space-y-4">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h2 className="text-xl font-semibold tracking-tight">
              Drift check lab
            </h2>
            <p className="mt-1 text-sm text-muted">
              Toggle clear · critical open blocks extend
            </p>
          </div>
          <Badge variant={criticalOpen.length ? "amber" : "teal"}>
            {criticalOpen.length
              ? `${criticalOpen.length} critical open`
              : "Criticals clear"}
          </Badge>
        </div>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {DRIFT_CHECKS.map((d) => {
            const on = cleared.includes(d.id);
            return (
              <button
                key={d.id}
                type="button"
                onClick={() => toggleCheck(d.id)}
                className={cn(
                  "rounded-xl border p-4 text-left transition-colors",
                  on
                    ? "border-teal/40 bg-teal/10"
                    : d.critical
                      ? "border-amber/40 bg-amber/5"
                      : "border-border bg-surface hover:border-border-strong",
                )}
              >
                <div className="flex items-center justify-between gap-2">
                  <p className="font-medium">{d.label}</p>
                  <Badge variant={d.critical ? "amber" : "outline"}>
                    {d.critical ? "critical" : "note"}
                  </Badge>
                </div>
                <p className="mt-1 text-sm text-muted">{d.inspect}</p>
                <p className="mt-2 font-mono text-[11px] text-teal">
                  {d.recovery}
                </p>
              </button>
            );
          })}
        </div>
      </section>

      <section className="min-w-0 space-y-4">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h2 className="text-xl font-semibold tracking-tight">
              Continuity handoff builder
            </h2>
            <p className="mt-1 text-sm text-muted">
              State packet → copy CONTINUITY_HANDOFF
            </p>
          </div>
          <Badge variant="outline">schema · continuity_handoff</Badge>
        </div>
        <div className="grid gap-4 lg:grid-cols-2">
          <Card className="min-w-0">
            <CardContent className="grid gap-3 p-4">
              {CONTINUITY_FIELDS.map((f) => {
                const isArea =
                  f.key === "last_frame_recap" ||
                  f.key === "wardrobe" ||
                  f.key === "props" ||
                  f.key === "environment" ||
                  f.key === "emotion" ||
                  f.key === "momentum" ||
                  f.key === "drift_notes";
                return (
                  <label key={f.key} className="min-w-0 block text-sm">
                    <span className="text-muted">
                      {f.label}
                      {f.required && <span className="text-teal"> *</span>}
                    </span>
                    {isArea ? (
                      <textarea
                        className={cn(fieldClass, "min-h-[64px] resize-y")}
                        placeholder={f.hint}
                        value={values[f.key] ?? ""}
                        onChange={(e) =>
                          setValues((v) => ({
                            ...v,
                            [f.key]: e.target.value,
                          }))
                        }
                      />
                    ) : (
                      <input
                        className={fieldClass}
                        placeholder={f.hint}
                        value={
                          f.key === "project"
                            ? project
                            : (values[f.key] ?? "")
                        }
                        onChange={(e) => {
                          if (f.key === "project") setProject(e.target.value);
                          setValues((v) => ({
                            ...v,
                            [f.key]: e.target.value,
                          }));
                        }}
                      />
                    )}
                  </label>
                );
              })}
            </CardContent>
          </Card>
          <Card className="min-w-0">
            <CardHeader className="flex flex-row items-start justify-between gap-2">
              <div>
                <CardTitle className="text-base">Continuity packet</CardTitle>
                <CardDescription>Attach to Sequence Blueprint</CardDescription>
              </div>
              <CopyButton text={packet} label="Copy packet" />
            </CardHeader>
            <CardContent>
              <pre className="max-h-[480px] overflow-auto whitespace-pre-wrap break-words rounded-lg border border-border bg-bg p-3.5 font-mono text-[11px] leading-relaxed text-muted">
                {packet}
              </pre>
            </CardContent>
          </Card>
        </div>
      </section>

      <section className="min-w-0 space-y-4">
        <div>
          <h2 className="text-xl font-semibold tracking-tight">
            Activation lab
          </h2>
          <p className="mt-1 text-sm text-muted">
            Copy-ready templates for pre-extend, chain audit, branches
          </p>
        </div>
        <Card className="min-w-0">
          <CardContent className="space-y-4 p-4">
            <label className="block text-sm">
              <span className="text-muted">Project slug</span>
              <input
                className={fieldClass}
                value={project}
                onChange={(e) => setProject(e.target.value)}
              />
            </label>
            <div className="flex flex-wrap gap-2">
              {ACTIVATION_TEMPLATES.map((t) => (
                <button
                  key={t.id}
                  type="button"
                  onClick={() => setTemplateId(t.id)}
                  className={cn(
                    "rounded-lg border px-3 py-2 text-sm transition-colors",
                    templateId === t.id
                      ? "border-teal/50 bg-teal/10 text-fg"
                      : "border-border text-muted hover:border-border-strong",
                  )}
                >
                  {t.title}
                </button>
              ))}
            </div>
            <div className="flex flex-wrap gap-2">
              <CopyButton text={templateBody} label="Copy template" />
              <CopyButton text={activation} label="Copy director block" />
            </div>
            <pre className="max-h-72 overflow-auto whitespace-pre-wrap break-words rounded-lg border border-border bg-bg p-3.5 font-mono text-[11px] leading-relaxed text-muted">
              {templateBody}
            </pre>
          </CardContent>
        </Card>
      </section>

      <section className="min-w-0 space-y-4">
        <div>
          <h2 className="text-xl font-semibold tracking-tight">Module quiz</h2>
          <p className="mt-1 text-sm text-muted">
            {CONTINUITY_QUIZ.length} checks · best score saved in progress
          </p>
        </div>
        <Card className="min-w-0">
          <CardContent className="space-y-4 p-5">
            {quizDone ? (
              <div className="space-y-3 text-center">
                <Shield className="mx-auto h-8 w-8 text-teal" />
                <p className="text-lg font-semibold">
                  Score {quizScore}/{CONTINUITY_QUIZ.length}
                </p>
                <p className="text-sm text-muted">
                  Best this device: {Math.max(quizBestSafe, quizScore)}/
                  {CONTINUITY_QUIZ.length}
                </p>
                <Button type="button" onClick={resetQuiz}>
                  Retry quiz
                </Button>
              </div>
            ) : (
              <>
                <div className="flex items-center justify-between gap-2 text-xs text-subtle">
                  <span>
                    Question {quizIdx + 1} / {CONTINUITY_QUIZ.length}
                  </span>
                  <span>Score {quizScore}</span>
                </div>
                <p className="text-base font-medium leading-relaxed">
                  {CONTINUITY_QUIZ[quizIdx].prompt}
                </p>
                <div className="grid gap-2">
                  {CONTINUITY_QUIZ[quizIdx].options.map((opt, i) => {
                    const isPicked = picked === i;
                    const isAnswer = i === CONTINUITY_QUIZ[quizIdx].answer;
                    return (
                      <button
                        key={opt}
                        type="button"
                        disabled={picked !== null}
                        onClick={() => answerQuiz(i)}
                        className={cn(
                          "rounded-xl border px-4 py-3 text-left text-sm transition-colors",
                          picked === null &&
                            "border-border hover:border-border-strong",
                          isPicked &&
                            isAnswer &&
                            "border-success/50 bg-success/10",
                          isPicked &&
                            !isAnswer &&
                            "border-amber/40 bg-amber/10",
                          picked !== null &&
                            !isPicked &&
                            isAnswer &&
                            "border-success/40 bg-success/5",
                          picked !== null &&
                            !isPicked &&
                            !isAnswer &&
                            "opacity-60",
                        )}
                      >
                        {opt}
                      </button>
                    );
                  })}
                </div>
                {picked !== null && (
                  <p className="text-sm text-muted leading-relaxed">
                    {CONTINUITY_QUIZ[quizIdx].explain}
                  </p>
                )}
              </>
            )}
          </CardContent>
        </Card>
      </section>

      <Card className="min-w-0 border-teal/20 bg-teal/5">
        <CardContent className="flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex gap-3">
            <Film className="mt-0.5 h-5 w-5 shrink-0 text-teal" />
            <div>
              <p className="font-medium">
                Recap. State. Gate. Then extend.
              </p>
              <p className="mt-1 text-sm text-muted">
                No LAST_FRAME_RECAP, no N+1. High drift blocks the chain.
              </p>
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            <Link
              to="/extend"
              className="inline-flex h-10 items-center gap-2 rounded-lg border border-border bg-bg px-4 text-sm font-medium hover:border-border-strong"
            >
              <Link2 className="h-4 w-4 text-teal" />
              Extend
            </Link>
            <Link
              to="/delivery-pack"
              className="inline-flex h-10 items-center gap-2 rounded-lg bg-teal px-4 text-sm font-semibold text-bg hover:bg-teal/90"
            >
              Delivery pack
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
