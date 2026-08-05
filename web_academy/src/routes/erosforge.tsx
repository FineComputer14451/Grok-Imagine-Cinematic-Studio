import { createFileRoute, Link } from "@tanstack/react-router";
import {
  AlertTriangle,
  ArrowRight,
  Check,
  CheckCircle2,
  Circle,
  Flame,
  GitBranch,
  Link2,
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
  buildErosforgeStatePacket,
  CHAIN_QA,
  EROSFORGE_QUIZ,
  EROSFORGE_TAGLINE,
  EROSFORGE_VERSION,
  LESSONS,
  MODEL_ROUTING,
  PACK_AGENTS,
  PIPELINE_STEPS,
  PROTOCOLS,
  STATE_FIELDS,
} from "@/data/erosforge";
import { useProgress } from "@/lib/progress";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/erosforge")({
  component: ErosforgePage,
});

const fieldClass =
  "mt-1.5 w-full min-w-0 rounded-lg border border-border bg-bg px-3 py-2.5 text-sm text-fg placeholder:text-subtle outline-none focus:border-border-strong focus:ring-2 focus:ring-teal/30";

function ErosforgePage() {
  const completedLessons = useProgress((s) => s.erosforgeLessons);
  const completeLesson = useProgress((s) => s.completeErosforgeLesson);
  const quizBest = useProgress((s) => s.erosforgeQuizBest);
  const recordQuiz = useProgress((s) => s.recordErosforgeQuiz);

  const [openLesson, setOpenLesson] = useState(LESSONS[0].id);
  const [stateValues, setStateValues] = useState<Record<string, string>>(() =>
    Object.fromEntries(
      STATE_FIELDS.map((f) => [
        f.key,
        f.key === "rating"
          ? "R-rated artistic · fictional adults only"
          : f.key === "hard_limits"
            ? "no minors · no non-consent · no real persons"
            : f.key === "model_path"
              ? "video_1_5"
              : f.key === "chat_model"
                ? "grok-v9-4p5-chat-expert"
                : "",
      ]),
    ),
  );
  const [stamp, setStamp] = useState("{{timestamp}}");
  const [hydrated, setHydrated] = useState(false);
  const [project, setProject] = useState("house-that-remembers");
  const [modelPath, setModelPath] = useState("video_1_5");
  const [templateId, setTemplateId] = useState<
    (typeof ACTIVATION_TEMPLATES)[number]["id"]
  >(ACTIVATION_TEMPLATES[0].id);
  const [qaScores, setQaScores] = useState<Record<string, number>>(() =>
    Object.fromEntries(CHAIN_QA.map((c) => [c.key, 8])),
  );
  const [quizIdx, setQuizIdx] = useState(0);
  const [picked, setPicked] = useState<number | null>(null);
  const [quizScore, setQuizScore] = useState(0);
  const [quizDone, setQuizDone] = useState(false);
  const [ackOptIn, setAckOptIn] = useState(false);

  useEffect(() => {
    setHydrated(true);
    setStamp(new Date().toISOString());
  }, []);

  const statePacket = useMemo(
    () => buildErosforgeStatePacket(stateValues, stamp),
    [stateValues, stamp],
  );
  const activation = useMemo(
    () => buildDirectorActivation(project, modelPath),
    [project, modelPath],
  );
  const templateBody = useMemo(() => {
    const t = ACTIVATION_TEMPLATES.find((x) => x.id === templateId)!;
    return t.body.replaceAll("{{project}}", project || "untitled-sequence");
  }, [templateId, project]);

  const qaResult = useMemo(() => {
    let weighted = 0;
    let weightSum = 0;
    const criticalFails: string[] = [];
    for (const c of CHAIN_QA) {
      const s = qaScores[c.key] ?? 0;
      weighted += s * c.weight;
      weightSum += c.weight;
      if (c.critical && s < 7) criticalFails.push(c.key);
    }
    const score = weightSum ? weighted / weightSum : 0;
    return { score, pass: score >= 7 && criticalFails.length === 0, criticalFails };
  }, [qaScores]);

  const lessonProgress = Math.round(
    (completedLessons.length / LESSONS.length) * 100,
  );
  const activeLesson = LESSONS.find((l) => l.id === openLesson) ?? LESSONS[0];
  const lessonsDone = hydrated ? completedLessons : [];
  const quizBestSafe = hydrated ? quizBest : 0;
  const lessonProgressSafe = hydrated ? lessonProgress : 0;

  function answerQuiz(option: number) {
    if (picked !== null || quizDone) return;
    setPicked(option);
    const q = EROSFORGE_QUIZ[quizIdx];
    const nextScore = quizScore + (option === q.answer ? 1 : 0);
    setQuizScore(nextScore);
    window.setTimeout(() => {
      if (quizIdx >= EROSFORGE_QUIZ.length - 1) {
        setQuizDone(true);
        recordQuiz(nextScore);
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
          <Badge variant="amber">NSFW pack · opt-in</Badge>
          <Badge variant="teal">Role Card v{EROSFORGE_VERSION}</Badge>
          <Badge variant="outline">Academy v{ACADEMY_MODULE_VERSION}</Badge>
        </div>
        <div className="grid gap-8 lg:grid-cols-[1.15fr_0.85fr] lg:items-end">
          <div className="min-w-0 space-y-4">
            <h1 className="max-w-2xl text-balance text-3xl font-semibold tracking-tight sm:text-4xl">
              ErosForge
            </h1>
            <p className="max-w-2xl text-muted leading-relaxed sm:text-lg">
              {EROSFORGE_TAGLINE}
            </p>
            <p className="max-w-2xl text-sm text-subtle leading-relaxed">
              Educational module — activation, protocols, state handoffs, and chain
              QA. Does not generate explicit media inside the Academy.
            </p>
            <div className="flex flex-wrap gap-3">
              <a
                href="#lessons"
                className={cn(
                  "inline-flex h-12 items-center justify-center gap-2 rounded-lg px-6 text-base font-semibold",
                  "bg-teal text-bg transition-all hover:bg-teal/90",
                )}
              >
                Start lessons
                <ArrowRight className="h-4 w-4" />
              </a>
              <Link
                to="/extend"
                className="inline-flex h-12 items-center justify-center gap-2 rounded-lg border border-border bg-elevated px-6 text-base font-medium"
              >
                Extend Lab
                <Link2 className="h-4 w-4" />
              </Link>
            </div>
          </div>
          <Card className="min-w-0 bg-elevated/40">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Flame className="h-4 w-4 text-amber" />
                Module progress
              </CardTitle>
              <CardDescription>
                {lessonsDone.length} of {LESSONS.length} lessons
                {quizBestSafe > 0 && (
                  <> · quiz best {quizBestSafe}/{EROSFORGE_QUIZ.length}</>
                )}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="h-2 overflow-hidden rounded-full bg-border">
                <div
                  className="h-full rounded-full bg-amber transition-all duration-500"
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
                  checked={ackOptIn}
                  onChange={(e) => setAckOptIn(e.target.checked)}
                />
                <span className="min-w-0 text-muted leading-relaxed">
                  I understand this pack is{" "}
                  <strong className="text-fg">strict opt-in</strong>, for
                  fictional adults only, and stays artistic / policy-safe.
                </span>
              </label>
            </CardContent>
          </Card>
        </div>
      </section>

      <Card className="min-w-0 border-amber/25 bg-amber/5">
        <CardContent className="flex gap-3 p-4 text-sm text-muted leading-relaxed">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber" />
          <p>
            <strong className="text-fg">Policy frame:</strong> Fictional adults
            only. No minors, no non-consent themes, no real persons. Workflow
            education only — no intimate media generation in Academy.
          </p>
        </CardContent>
      </Card>

      <Card className="min-w-0">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <GitBranch className="h-4 w-4 text-teal" />
            ErosForge pipeline
          </CardTitle>
        </CardHeader>
        <CardContent className="overflow-x-auto">
          <div className="flex min-w-0 flex-col gap-2 sm:flex-row sm:flex-wrap">
            {PIPELINE_STEPS.map((s, i) => (
              <div key={s.id} className="min-w-0 flex-1 rounded-xl border border-border bg-surface px-3 py-3 sm:min-w-[110px]">
                <p className="font-mono text-[11px] text-subtle">
                  {String(i + 1).padStart(2, "0")}
                </p>
                <p className="mt-1 text-sm font-medium">{s.label}</p>
                <p className="mt-0.5 text-xs text-muted">{s.detail}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <section className="min-w-0 space-y-4">
        <h2 className="text-xl font-semibold tracking-tight">Protocols</h2>
        <div className="grid gap-3 sm:grid-cols-2">
          {PROTOCOLS.map((p) => (
            <Card key={p.id} className="min-w-0">
              <CardHeader className="pb-2">
                <CardTitle className="font-mono text-sm text-amber">{p.name}</CardTitle>
                <CardDescription className="text-sm text-fg/90">{p.requirement}</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-muted leading-relaxed">{p.why}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      <section id="lessons" className="min-w-0 space-y-4 scroll-mt-20">
        <h2 className="text-xl font-semibold tracking-tight">Lessons</h2>
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
                    active ? "border-amber/40 bg-amber/10" : "border-border bg-surface hover:border-border-strong",
                  )}
                >
                  {done ? (
                    <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-success" />
                  ) : (
                    <Circle className="mt-0.5 h-4 w-4 shrink-0 text-subtle" />
                  )}
                  <span className="min-w-0">
                    <span className="flex items-center gap-2">
                      <span className="font-mono text-[11px] text-subtle">{l.step}</span>
                      <span className="text-sm font-medium">{l.title}</span>
                    </span>
                    <span className="mt-0.5 block text-xs text-muted">{l.minutes}</span>
                  </span>
                </button>
              );
            })}
          </div>
          <Card className="min-w-0">
            <CardHeader>
              <CardTitle className="text-lg">{activeLesson.title}</CardTitle>
              <CardDescription>{activeLesson.summary}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <ul className="space-y-2">
                {activeLesson.bullets.map((b) => (
                  <li key={b} className="flex gap-2 text-sm text-muted leading-relaxed">
                    <Check className="mt-0.5 h-3.5 w-3.5 shrink-0 text-teal" />
                    <span>{b}</span>
                  </li>
                ))}
              </ul>
              <Button
                type="button"
                variant={lessonsDone.includes(activeLesson.id) ? "outline" : "default"}
                disabled={!ackOptIn}
                onClick={() => completeLesson(activeLesson.id)}
              >
                {lessonsDone.includes(activeLesson.id)
                  ? "Completed"
                  : ackOptIn
                    ? "Mark complete"
                    : "Ack opt-in above first"}
              </Button>
            </CardContent>
          </Card>
        </div>
      </section>

      <section className="min-w-0 space-y-4">
        <h2 className="text-xl font-semibold tracking-tight">Pack agents</h2>
        <div className="grid gap-3 md:grid-cols-2">
          {PACK_AGENTS.map((a) => (
            <Card key={a.id} className="min-w-0">
              <CardHeader>
                <div className="flex flex-wrap items-center gap-2">
                  <CardTitle className="text-base">{a.name}</CardTitle>
                  {a.requiresErosforge && <Badge variant="amber">requires ErosForge</Badge>}
                </div>
                <CardDescription>{a.role}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <code className="block break-all rounded-lg border border-border bg-bg px-3 py-2 font-mono text-xs text-teal">
                  {a.activation}
                </code>
                <CopyButton text={a.activation} label="Copy activation" />
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      <section className="min-w-0 space-y-4">
        <h2 className="text-xl font-semibold tracking-tight">EROSFORGE_STATE builder</h2>
        <div className="grid gap-4 lg:grid-cols-2">
          <Card className="min-w-0">
            <CardContent className="grid gap-3 p-4 sm:grid-cols-2">
              {STATE_FIELDS.map((f) => (
                <label key={f.key} className="min-w-0 block text-sm">
                  <span className="text-muted">
                    {f.label}
                    {f.required && <span className="text-amber"> *</span>}
                  </span>
                  <input
                    className={fieldClass}
                    placeholder={f.hint}
                    value={stateValues[f.key] ?? ""}
                    onChange={(e) =>
                      setStateValues((v) => ({ ...v, [f.key]: e.target.value }))
                    }
                  />
                </label>
              ))}
            </CardContent>
          </Card>
          <Card className="min-w-0">
            <CardHeader className="flex flex-row items-start justify-between gap-2">
              <CardTitle className="text-base">Packet preview</CardTitle>
              <CopyButton text={statePacket} label="Copy state" />
            </CardHeader>
            <CardContent>
              <pre className="max-h-[420px] overflow-auto whitespace-pre-wrap break-words rounded-lg border border-border bg-bg p-3.5 font-mono text-[11px] leading-relaxed text-muted">
                {statePacket}
              </pre>
            </CardContent>
          </Card>
        </div>
      </section>

      <section className="min-w-0 space-y-4">
        <h2 className="text-xl font-semibold tracking-tight">Activation lab</h2>
        <Card className="min-w-0">
          <CardContent className="space-y-4 p-4">
            <div className="grid gap-3 sm:grid-cols-2">
              <label className="block text-sm">
                <span className="text-muted">Project slug</span>
                <input className={fieldClass} value={project} onChange={(e) => setProject(e.target.value)} />
              </label>
              <label className="block text-sm">
                <span className="text-muted">Model path</span>
                <select className={fieldClass} value={modelPath} onChange={(e) => setModelPath(e.target.value)}>
                  <option value="video_1_5">Imagine Video 1.5 Native</option>
                  <option value="video_1_0">Imagine Video 1.0 (draft)</option>
                  <option value="still">Still plate only</option>
                </select>
              </label>
            </div>
            <div className="flex flex-wrap gap-2">
              {ACTIVATION_TEMPLATES.map((t) => (
                <button
                  key={t.id}
                  type="button"
                  onClick={() => setTemplateId(t.id)}
                  className={cn(
                    "rounded-lg border px-3 py-2 text-sm",
                    templateId === t.id
                      ? "border-teal/50 bg-teal/10 text-fg"
                      : "border-border text-muted",
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
        <div className="flex flex-wrap items-end justify-between gap-3">
          <h2 className="text-xl font-semibold tracking-tight">Chain QA simulator</h2>
          <Badge variant={qaResult.pass ? "teal" : "amber"}>
            {qaResult.pass ? "PASS" : "HOLD"} · {qaResult.score.toFixed(2)}
          </Badge>
        </div>
        <Card className="min-w-0">
          <CardContent className="space-y-4 p-4">
            {CHAIN_QA.map((c) => (
              <div key={c.key} className="grid gap-2 border-b border-border pb-4 last:border-0 last:pb-0 sm:grid-cols-[1fr_auto] sm:items-center">
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <p className="font-mono text-xs text-fg">{c.key}</p>
                    {c.critical && <Badge variant="amber">critical</Badge>}
                  </div>
                  <p className="mt-1 text-sm text-muted">{c.inspect}</p>
                </div>
                <div className="flex items-center gap-3">
                  <input
                    type="range"
                    min={0}
                    max={10}
                    step={1}
                    value={qaScores[c.key] ?? 0}
                    onChange={(e) =>
                      setQaScores((s) => ({ ...s, [c.key]: Number(e.target.value) }))
                    }
                    className="w-32 accent-teal"
                  />
                  <span className="w-6 font-mono text-sm tabular-nums">{qaScores[c.key] ?? 0}</span>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </section>

      <section className="min-w-0 space-y-4">
        <h2 className="text-xl font-semibold tracking-tight">Module quiz</h2>
        <Card className="min-w-0">
          <CardContent className="space-y-4 p-5">
            {quizDone ? (
              <div className="space-y-3 text-center">
                <Shield className="mx-auto h-8 w-8 text-teal" />
                <p className="text-lg font-semibold">
                  Score {quizScore}/{EROSFORGE_QUIZ.length}
                </p>
                <Button type="button" onClick={() => { setQuizIdx(0); setPicked(null); setQuizScore(0); setQuizDone(false); }}>
                  Retry quiz
                </Button>
              </div>
            ) : (
              <>
                <p className="text-base font-medium leading-relaxed">
                  {EROSFORGE_QUIZ[quizIdx].prompt}
                </p>
                <div className="grid gap-2">
                  {EROSFORGE_QUIZ[quizIdx].options.map((opt, i) => (
                    <button
                      key={opt}
                      type="button"
                      disabled={picked !== null}
                      onClick={() => answerQuiz(i)}
                      className={cn(
                        "rounded-xl border px-4 py-3 text-left text-sm",
                        picked === null && "border-border hover:border-border-strong",
                        picked === i && i === EROSFORGE_QUIZ[quizIdx].answer && "border-success/50 bg-success/10",
                        picked === i && i !== EROSFORGE_QUIZ[quizIdx].answer && "border-amber/40 bg-amber/10",
                      )}
                    >
                      {opt}
                    </button>
                  ))}
                </div>
                {picked !== null && (
                  <p className="text-sm text-muted">{EROSFORGE_QUIZ[quizIdx].explain}</p>
                )}
              </>
            )}
          </CardContent>
        </Card>
      </section>

      <section className="min-w-0 space-y-4">
        <h2 className="text-xl font-semibold tracking-tight">Model layer routing</h2>
        <div className="grid gap-3 md:grid-cols-3">
          {MODEL_ROUTING.map((m) => (
            <Card key={m.model} className="min-w-0">
              <CardHeader>
                <CardTitle className="font-mono text-sm text-teal">{m.model}</CardTitle>
                <CardDescription>{m.task}</CardDescription>
              </CardHeader>
              <CardContent>
                <Badge variant="outline">reasoning · {m.reasoning}</Badge>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>
    </div>
  );
}
