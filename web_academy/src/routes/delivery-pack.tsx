import { createFileRoute, Link } from "@tanstack/react-router";
import {
  ArrowRight,
  Check,
  CheckCircle2,
  Circle,
  ClipboardCheck,
  GitBranch,
  Package,
  Shield,
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
  buildDirectorActivation,
  DELIVERY_PACK_TAGLINE,
  DELIVERY_PACK_VERSION,
  DELIVERY_QUIZ,
  LESSONS,
  PACK_AGENTS,
  PIPELINE_STEPS,
  PROTOCOLS,
} from "@/data/delivery-pack";
import { useProgress } from "@/lib/progress";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/delivery-pack")({
  component: DeliveryPackPage,
});

function DeliveryPackPage() {
  const completedLessons = useProgress((s) => s.deliveryPackLessons ?? []);
  const completeLesson = useProgress((s) => s.completeDeliveryPackLesson);
  const quizBest = useProgress((s) => s.deliveryPackQuizBest ?? 0);
  const recordQuiz = useProgress((s) => s.recordDeliveryPackQuiz);

  const [openLesson, setOpenLesson] = useState(LESSONS[0].id);
  const [hydrated, setHydrated] = useState(false);
  const [project, setProject] = useState("neon-alley-chase");
  const [templateId, setTemplateId] = useState<
    (typeof ACTIVATION_TEMPLATES)[number]["id"]
  >(ACTIVATION_TEMPLATES[0].id);
  const [quizIdx, setQuizIdx] = useState(0);
  const [picked, setPicked] = useState<number | null>(null);
  const [quizScore, setQuizScore] = useState(0);
  const [quizDone, setQuizDone] = useState(false);
  const [ack, setAck] = useState(false);

  useEffect(() => setHydrated(true), []);

  const activation = useMemo(
    () => buildDirectorActivation(project),
    [project],
  );
  const templateBody = useMemo(() => {
    const t = ACTIVATION_TEMPLATES.find((x) => x.id === templateId)!;
    return t.body.replaceAll("{{project}}", project || "untitled");
  }, [templateId, project]);

  const lessonsDone = hydrated ? completedLessons : [];
  const quizBestSafe = hydrated ? quizBest : 0;
  const lessonProgressSafe = hydrated
    ? Math.round((completedLessons.length / LESSONS.length) * 100)
    : 0;
  const activeLesson = LESSONS.find((l) => l.id === openLesson) ?? LESSONS[0];

  function answerQuiz(option: number) {
    if (picked !== null || quizDone) return;
    setPicked(option);
    const q = DELIVERY_QUIZ[quizIdx];
    const next = quizScore + (option === q.answer ? 1 : 0);
    setQuizScore(next);
    window.setTimeout(() => {
      if (quizIdx >= DELIVERY_QUIZ.length - 1) {
        setQuizDone(true);
        recordQuiz?.(next);
      } else {
        setQuizIdx((i) => i + 1);
        setPicked(null);
      }
    }, 650);
  }

  return (
    <div className="min-w-0 space-y-10">
      <section className="space-y-5">
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="teal">Core pack · Ship gate</Badge>
          <Badge variant="outline">Role Card v{DELIVERY_PACK_VERSION}</Badge>
          <Badge variant="outline">Academy v{ACADEMY_MODULE_VERSION}</Badge>
        </div>
        <div className="grid gap-8 lg:grid-cols-[1.15fr_0.85fr] lg:items-end">
          <div className="min-w-0 space-y-4">
            <h1 className="max-w-2xl text-balance text-3xl font-semibold tracking-tight sm:text-4xl">
              Delivery pack
            </h1>
            <p className="max-w-2xl text-muted leading-relaxed sm:text-lg">
              {DELIVERY_PACK_TAGLINE}
            </p>
            <div className="flex flex-wrap gap-3">
              <a
                href="#lessons"
                className="inline-flex h-12 items-center justify-center gap-2 rounded-lg bg-teal px-6 text-base font-semibold text-bg hover:bg-teal/90"
              >
                Start lessons
                <ArrowRight className="h-4 w-4" />
              </a>
              <Link
                to="/delivery"
                className="inline-flex h-12 items-center justify-center gap-2 rounded-lg border border-border bg-elevated px-6 text-base font-medium hover:border-border-strong"
              >
                <ClipboardCheck className="h-4 w-4 text-teal" />
                Checklist tool
              </Link>
              <Link
                to="/pack"
                className="inline-flex h-12 items-center justify-center gap-2 rounded-lg border border-border bg-elevated px-6 text-base font-medium hover:border-border-strong"
              >
                <Package className="h-4 w-4" />
                Project pack
              </Link>
            </div>
          </div>
          <Card className="bg-elevated/40">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <ClipboardCheck className="h-4 w-4 text-teal" />
                Module progress
              </CardTitle>
              <CardDescription>
                {lessonsDone.length} of {LESSONS.length} lessons
                {quizBestSafe > 0 && (
                  <> · quiz best {quizBestSafe}/{DELIVERY_QUIZ.length}</>
                )}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="h-2 overflow-hidden rounded-full bg-border">
                <div
                  className="h-full rounded-full bg-teal transition-all"
                  style={{ width: `${lessonProgressSafe}%` }}
                />
              </div>
              <p className="font-mono text-2xl font-semibold tabular-nums">
                {lessonProgressSafe}%
              </p>
              <label className="flex cursor-pointer items-start gap-3 rounded-lg border border-border bg-bg/60 p-3 text-sm">
                <input
                  type="checkbox"
                  className="mt-1 accent-teal"
                  checked={ack}
                  onChange={(e) => setAck(e.target.checked)}
                />
                <span className="text-muted leading-relaxed">
                  I will clear <strong className="text-fg">blockers first</strong>,
                  require QA Go / picture lock before masters, and ship one package.
                </span>
              </label>
            </CardContent>
          </Card>
        </div>
      </section>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <GitBranch className="h-4 w-4 text-teal" />
            Delivery pipeline
          </CardTitle>
        </CardHeader>
        <CardContent className="overflow-x-auto">
          <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap">
            {PIPELINE_STEPS.map((s, i) => (
              <div key={s.id} className="min-w-[100px] flex-1 rounded-xl border border-border bg-surface px-3 py-3">
                <p className="font-mono text-[11px] text-subtle">
                  {String(i + 1).padStart(2, "0")}
                </p>
                <p className="mt-1 text-sm font-medium">{s.label}</p>
                <p className="text-xs text-muted">{s.detail}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <section className="space-y-4">
        <h2 className="text-xl font-semibold tracking-tight">Protocols</h2>
        <div className="grid gap-3 sm:grid-cols-2">
          {PROTOCOLS.map((p) => (
            <Card key={p.id}>
              <CardHeader className="pb-2">
                <CardTitle className="font-mono text-sm text-teal">{p.name}</CardTitle>
                <CardDescription className="text-sm text-fg/90">
                  {p.requirement}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-muted">{p.why}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      <section id="lessons" className="space-y-4 scroll-mt-20">
        <h2 className="text-xl font-semibold tracking-tight">Lessons</h2>
        <div className="grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
          <div className="space-y-2">
            {LESSONS.map((l) => {
              const done = lessonsDone.includes(l.id);
              const active = openLesson === l.id;
              return (
                <button
                  key={l.id}
                  type="button"
                  onClick={() => setOpenLesson(l.id)}
                  className={cn(
                    "flex w-full items-start gap-3 rounded-xl border px-3 py-3 text-left",
                    active ? "border-teal/40 bg-teal/10" : "border-border bg-surface",
                  )}
                >
                  {done ? (
                    <CheckCircle2 className="mt-0.5 h-4 w-4 text-success" />
                  ) : (
                    <Circle className="mt-0.5 h-4 w-4 text-subtle" />
                  )}
                  <span>
                    <span className="font-mono text-[11px] text-subtle">{l.step}</span>{" "}
                    <span className="text-sm font-medium">{l.title}</span>
                    <span className="mt-0.5 block text-xs text-muted">{l.minutes}</span>
                  </span>
                </button>
              );
            })}
          </div>
          <Card>
            <CardHeader>
              <CardTitle>{activeLesson.title}</CardTitle>
              <CardDescription>{activeLesson.summary}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <ul className="space-y-2">
                {activeLesson.bullets.map((b) => (
                  <li key={b} className="flex gap-2 text-sm text-muted">
                    <Check className="mt-0.5 h-3.5 w-3.5 shrink-0 text-teal" />
                    {b}
                  </li>
                ))}
              </ul>
              {activeLesson.drill && (
                <div className="rounded-lg border border-border bg-bg p-3 text-sm">
                  <p className="text-xs uppercase text-subtle">Drill</p>
                  <p className="mt-1">{activeLesson.drill}</p>
                </div>
              )}
              <Button
                type="button"
                disabled={!ack}
                onClick={() => completeLesson?.(activeLesson.id)}
              >
                {lessonsDone.includes(activeLesson.id)
                  ? "Completed"
                  : ack
                    ? "Mark complete"
                    : "Ack ship rules first"}
              </Button>
            </CardContent>
          </Card>
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-semibold tracking-tight">Pack agents</h2>
        <div className="grid gap-3 md:grid-cols-2">
          {PACK_AGENTS.map((a) => (
            <Card key={a.id}>
              <CardHeader>
                <CardTitle className="text-base">{a.name}</CardTitle>
                <CardDescription>{a.role}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                <code className="block rounded-lg border border-border bg-bg px-3 py-2 font-mono text-xs text-teal">
                  {a.activation}
                </code>
                <CopyButton text={a.activation} label="Copy activation" />
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-semibold tracking-tight">Activation lab</h2>
        <Card>
          <CardContent className="space-y-4 p-4">
            <label className="block text-sm">
              <span className="text-muted">Project</span>
              <input
                className="mt-1.5 w-full rounded-lg border border-border bg-bg px-3 py-2.5 text-sm"
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
                    "rounded-lg border px-3 py-2 text-sm",
                    templateId === t.id
                      ? "border-teal/50 bg-teal/10"
                      : "border-border text-muted",
                  )}
                >
                  {t.title}
                </button>
              ))}
            </div>
            <CopyButton text={templateBody} label="Copy template" />
            <CopyButton text={activation} label="Copy director block" />
            <pre className="max-h-64 overflow-auto whitespace-pre-wrap rounded-lg border border-border bg-bg p-3 font-mono text-[11px] text-muted">
              {templateBody}
            </pre>
          </CardContent>
        </Card>
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-semibold tracking-tight">Module quiz</h2>
        <Card>
          <CardContent className="space-y-4 p-5">
            {quizDone ? (
              <div className="space-y-3 text-center">
                <Shield className="mx-auto h-8 w-8 text-teal" />
                <p className="text-lg font-semibold">
                  Score {quizScore}/{DELIVERY_QUIZ.length}
                </p>
                <Button
                  type="button"
                  onClick={() => {
                    setQuizIdx(0);
                    setPicked(null);
                    setQuizScore(0);
                    setQuizDone(false);
                  }}
                >
                  Retry
                </Button>
              </div>
            ) : (
              <>
                <p className="text-base font-medium">
                  {DELIVERY_QUIZ[quizIdx].prompt}
                </p>
                <div className="grid gap-2">
                  {DELIVERY_QUIZ[quizIdx].options.map((opt, i) => (
                    <button
                      key={opt}
                      type="button"
                      disabled={picked !== null}
                      onClick={() => answerQuiz(i)}
                      className={cn(
                        "rounded-xl border px-4 py-3 text-left text-sm",
                        picked === null && "border-border hover:border-border-strong",
                        picked === i &&
                          i === DELIVERY_QUIZ[quizIdx].answer &&
                          "border-success/50 bg-success/10",
                        picked === i &&
                          i !== DELIVERY_QUIZ[quizIdx].answer &&
                          "border-amber/40 bg-amber/10",
                      )}
                    >
                      {opt}
                    </button>
                  ))}
                </div>
                {picked !== null && (
                  <p className="text-sm text-muted">{DELIVERY_QUIZ[quizIdx].explain}</p>
                )}
              </>
            )}
          </CardContent>
        </Card>
      </section>

      <Card className="border-teal/20 bg-teal/5">
        <CardContent className="flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="font-medium">Clear blockers. Lock picture. Ship one package.</p>
            <p className="mt-1 text-sm text-muted">
              Use the interactive checklist when you are ready to tick items.
            </p>
          </div>
          <Link
            to="/delivery"
            className="inline-flex h-10 items-center gap-2 rounded-lg bg-teal px-4 text-sm font-semibold text-bg"
          >
            Open checklist
            <ArrowRight className="h-4 w-4" />
          </Link>
        </CardContent>
      </Card>
    </div>
  );
}
