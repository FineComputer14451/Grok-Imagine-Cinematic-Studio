import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Clock3,
  Gauge,
  Layers,
  Stethoscope,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  ATTENTION,
  MODEL_STACK,
  PROJECTS,
  READINESS,
  SPECIALISTS,
  STATS,
  USAGE,
} from "@/lib/studio-data";
import { formatNumber, formatRelative, cn } from "@/lib/utils";
import { sectionVisible, useStudioStore } from "@/lib/studio-store";
import { ShotFrame } from "./shot-frame";
import { StatusBadge } from "./status-badge";

export function OverviewView() {
  const shots = useStudioStore((s) => s.shots);
  const queue = useStudioStore((s) => s.queue);
  const sequences = useStudioStore((s) => s.sequences);
  const characters = useStudioStore((s) => s.characters);
  const density = useStudioStore((s) => s.density);
  const setView = useStudioStore((s) => s.setView);
  const setSelectedShotId = useStudioStore((s) => s.setSelectedShotId);
  const healthLog = useStudioStore((s) => s.healthLog);
  const runHealthAction = useStudioStore((s) => s.runHealthAction);
  const recent = shots.slice(0, 4);
  const locked = characters.filter((c) => c.locked).length;
  const show = (section: string) => sectionVisible(density, section);

  return (
    <div className="space-y-6">
      {show("status") && (
        <div className="flex flex-wrap items-center gap-2 rounded-xl border border-border bg-bg-elevated px-3 py-2.5 text-xs">
          <Badge variant="queued">Ops WARN</Badge>
          <span className="text-fg-muted">
            Project <strong className="text-fg">Neon Harbor</strong>
          </span>
          <span className="text-fg-subtle">·</span>
          <span className="text-fg-muted">
            {sequences.length} sequences · {characters.length} DNA · {locked} locked
          </span>
          <span className="text-fg-subtle">·</span>
          <span className="text-fg-muted">
            Risk <strong className="text-fg capitalize">{STATS.riskLevel}</strong>
          </span>
          <span className="text-fg-subtle">·</span>
          <span className="text-fg-muted">
            Stack {MODEL_STACK.chat} / {MODEL_STACK.video}
          </span>
        </div>
      )}

      {show("kpis") && (
        <div className="grid gap-3 grid-cols-2 xl:grid-cols-6">
          {[
            { label: "Sequences", value: sequences.length, icon: Layers },
            { label: "DNA profiles", value: characters.length, icon: Activity },
            { label: "Identity locked", value: locked, icon: CheckCircle2 },
            { label: "Queue depth", value: queue.length, icon: Clock3 },
            {
              label: "Session spent",
              value: STATS.sessionSpent,
              icon: Gauge,
            },
            {
              label: "Severity",
              value: "WARN",
              icon: AlertTriangle,
            },
          ].map((m) => {
            const Icon = m.icon;
            return (
              <Card key={m.label}>
                <CardContent className="p-3 sm:p-4">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <p className="text-[11px] font-medium text-fg-muted">
                        {m.label}
                      </p>
                      <p className="mt-1 text-xl font-semibold tracking-tight tabular">
                        {typeof m.value === "number"
                          ? formatNumber(m.value)
                          : m.value}
                      </p>
                    </div>
                    <Icon className="size-3.5 text-fg-subtle" />
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {show("attention") && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Attention</CardTitle>
            <CardDescription>
              Ops signals shared with Streamlit / TUI Home
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {ATTENTION.map((a, i) => (
              <div
                key={a.id}
                className="flex gap-3 rounded-lg border border-border bg-bg-subtle/40 px-3 py-2.5"
              >
                <span className="tabular text-xs text-fg-subtle">{i + 1}.</span>
                <div className="min-w-0 flex-1">
                  <Badge
                    variant={
                      a.severity === "critical"
                        ? "failed"
                        : a.severity === "warn"
                          ? "queued"
                          : "default"
                    }
                    className="mb-1"
                  >
                    {a.severity}
                  </Badge>
                  <p className="text-sm text-fg">{a.message}</p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {show("health_actions") && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Health actions</CardTitle>
            <CardDescription>
              Safe read/repair · TUI family d / v / s / m
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
              {[
                { id: "doctor", label: "Doctor (quick)", icon: Stethoscope },
                { id: "validate", label: "Validate", icon: CheckCircle2 },
                { id: "quota-sync", label: "Quota sync", icon: Gauge },
                { id: "models", label: "Models verify", icon: Activity },
              ].map((a) => {
                const Icon = a.icon;
                return (
                  <Button
                    key={a.id}
                    variant="secondary"
                    className="justify-start"
                    onClick={() => runHealthAction(a.id)}
                  >
                    <Icon className="size-3.5" />
                    {a.label}
                  </Button>
                );
              })}
            </div>
            {healthLog && (
              <div
                className={cn(
                  "mt-3 rounded-lg border p-3 text-xs",
                  healthLog.ok
                    ? "border-success/25 bg-success/5"
                    : "border-warning/25 bg-warning/5",
                )}
              >
                <p className="mb-1 font-medium text-fg">
                  `{healthLog.title}` · {healthLog.ok ? "OK" : "issues"}
                </p>
                <pre className="whitespace-pre-wrap font-mono text-fg-muted">
                  {healthLog.out}
                </pre>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {show("readiness") && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Produce / gate readiness</CardTitle>
            <CardDescription>
              Plate · motion · identity · spend · delivery
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
              {READINESS.map((g) => (
                <div
                  key={g.id}
                  className="rounded-lg border border-border bg-bg-subtle/40 px-3 py-2.5"
                >
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-sm font-medium">{g.label}</p>
                    <GatePill status={g.status} />
                  </div>
                  <p className="mt-1 text-xs text-fg-muted">{g.detail}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {show("convergence") && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">
              Convergence → agent-mode handoff
            </CardTitle>
            <CardDescription>J8 checklist before Imagine spend</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {[
              { ok: true, label: "Production Bible present", hint: null },
              { ok: true, label: "Identity Continuity Protocol", hint: null },
              {
                ok: false,
                label: "Chain QA clear",
                hint: "Fix Alley confrontation no-go",
              },
              {
                ok: false,
                label: "Handoff packet validated",
                hint: "Re-run after QA pass",
              },
              { ok: true, label: "Quota within soft cap", hint: null },
            ].map((item) => (
              <div
                key={item.label}
                className="flex items-start gap-2 text-sm"
              >
                <span
                  className={cn(
                    "mt-0.5 size-4 shrink-0 rounded-full border text-center text-[10px] leading-4",
                    item.ok
                      ? "border-success/40 text-success"
                      : "border-danger/40 text-danger",
                  )}
                >
                  {item.ok ? "✓" : "!"}
                </span>
                <div>
                  <p className="font-medium">{item.label}</p>
                  {item.hint && (
                    <p className="text-xs text-fg-muted">{item.hint}</p>
                  )}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {show("studio_quota") && (
        <div className="grid gap-4 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Studio health</CardTitle>
            </CardHeader>
            <CardContent className="space-y-1.5 text-sm text-fg-muted">
              <p>
                Agents:{" "}
                <strong className="text-fg">
                  {STATS.coreAgents} core · {STATS.totalAgents} total
                </strong>
              </p>
              <p>
                Role cards:{" "}
                <strong className="text-fg">{STATS.roleCards}/23</strong>
              </p>
              <p>
                Skills: <strong className="text-fg">{STATS.skills}</strong>
              </p>
              <p>
                Models: <strong className="text-success">compatible</strong>
              </p>
              <p>
                Bible:{" "}
                <strong className="text-fg">
                  {PROJECTS.filter((p) => p.hasBible).length} projects loaded
                </strong>
              </p>
              <div className="mt-3 flex flex-wrap gap-1.5">
                {SPECIALISTS.slice(0, 6).map((s) => (
                  <Badge
                    key={s.id}
                    variant={s.status === "active" ? "ready" : "default"}
                  >
                    {s.name}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Quota</CardTitle>
            </CardHeader>
            <CardContent className="space-y-1.5 text-sm text-fg-muted">
              <p>
                Tier:{" "}
                <strong className="text-fg">{STATS.tierLabel}</strong>
              </p>
              <p>
                Session spent:{" "}
                <strong className="tabular text-fg">{STATS.sessionSpent}</strong>
              </p>
              <p>
                Remaining:{" "}
                <strong className="tabular text-fg">
                  {STATS.creditsRemaining}
                </strong>
              </p>
              <p>
                Risk:{" "}
                <strong className="capitalize text-fg">{STATS.riskLevel}</strong>
              </p>
              <p>
                Cascade:{" "}
                <strong className="text-fg">{STATS.cascade}</strong> · burn{" "}
                {STATS.burnMultiplier}x
              </p>
              <Button
                size="sm"
                variant="outline"
                className="mt-3"
                onClick={() => setView("quota")}
              >
                Open quota
              </Button>
            </CardContent>
          </Card>
        </div>
      )}

      {show("sequences") && density !== "compact" && (
        <div className="grid gap-4 lg:grid-cols-5">
          <Card className="lg:col-span-3">
            <CardHeader className="flex-row items-center justify-between space-y-0">
              <div>
                <CardTitle className="text-base">Usage this week</CardTitle>
                <CardDescription>Images & video credit burn</CardDescription>
              </div>
            </CardHeader>
            <CardContent className="h-56 pt-0">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart
                  data={USAGE}
                  margin={{ top: 8, right: 8, left: -18, bottom: 0 }}
                >
                  <defs>
                    <linearGradient id="imgFill" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#e4e4e7" stopOpacity={0.28} />
                      <stop offset="100%" stopColor="#e4e4e7" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid
                    stroke="#27272a"
                    strokeDasharray="3 3"
                    vertical={false}
                  />
                  <XAxis
                    dataKey="day"
                    tick={{ fill: "#71717a", fontSize: 12 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    tick={{ fill: "#71717a", fontSize: 12 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip
                    contentStyle={{
                      background: "#111114",
                      border: "1px solid #27272a",
                      borderRadius: 8,
                      fontSize: 12,
                      color: "#f4f4f5",
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="images"
                    stroke="#e4e4e7"
                    fill="url(#imgFill)"
                    strokeWidth={1.5}
                    name="Images"
                  />
                  <Area
                    type="monotone"
                    dataKey="videos"
                    stroke="#71717a"
                    fill="transparent"
                    strokeWidth={1.5}
                    name="Videos"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="text-base">Sequences</CardTitle>
              <CardDescription>Chain QA + delivery</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              {sequences.map((seq) => (
                <button
                  key={seq.id}
                  type="button"
                  onClick={() => setView("sequences")}
                  className="flex w-full items-center justify-between gap-2 rounded-lg border border-border bg-bg-subtle/40 px-3 py-2 text-left text-sm hover:bg-bg-hover"
                >
                  <div className="min-w-0">
                    <p className="truncate font-medium">{seq.name}</p>
                    <p className="text-xs text-fg-muted">
                      {seq.clips} clips · {seq.durationSec}s · {seq.status}
                    </p>
                  </div>
                  <Badge
                    variant={
                      seq.chainQa === "pass"
                        ? "ready"
                        : seq.chainQa === "hold"
                          ? "failed"
                          : "queued"
                    }
                  >
                    {seq.chainQa}
                  </Badge>
                </button>
              ))}
            </CardContent>
          </Card>
        </div>
      )}

      {density === "full" && (
        <Card>
          <CardHeader className="flex-row items-center justify-between space-y-0">
            <div>
              <CardTitle className="text-base">Recent takes</CardTitle>
              <CardDescription>Latest plates across projects</CardDescription>
            </div>
            <Button variant="ghost" size="sm" onClick={() => setView("gallery")}>
              View all
            </Button>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3 sm:grid-cols-2">
              {recent.map((shot) => (
                <button
                  key={shot.id}
                  type="button"
                  className="group text-left"
                  onClick={() => {
                    setSelectedShotId(shot.id);
                    setView("gallery");
                  }}
                >
                  <ShotFrame
                    frame={shot.frame}
                    aspect={shot.aspect}
                    status={shot.status}
                    mode={shot.mode}
                    className="transition-opacity duration-150 group-hover:opacity-90"
                  />
                  <div className="mt-2 flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium">{shot.title}</p>
                      <p className="text-xs text-fg-subtle">
                        {formatRelative(new Date(shot.createdAt))} · T{shot.take}
                      </p>
                    </div>
                    <StatusBadge status={shot.status} />
                  </div>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function GatePill({ status }: { status: string }) {
  const variant =
    status === "ready"
      ? "ready"
      : status === "hold"
        ? "failed"
        : status === "warn"
          ? "queued"
          : "default";
  return <Badge variant={variant as "ready"}>{status}</Badge>;
}
