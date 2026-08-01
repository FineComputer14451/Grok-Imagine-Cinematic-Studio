import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { SPEND_HISTORY, STATS, USAGE } from "@/lib/studio-data";
import { formatRelative } from "@/lib/utils";
import { toast } from "sonner";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export function QuotaView() {
  const usedPct = Math.round(
    (STATS.sessionSpent / STATS.dailySoftCap) * 100,
  );
  const remainPct = Math.round(
    (STATS.creditsRemaining / STATS.creditsTotal) * 100,
  );

  return (
    <div className="space-y-4">
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {[
          { label: "Tier", value: STATS.tierLabel },
          { label: "Session spent", value: `${STATS.sessionSpent} cr` },
          {
            label: "Budget left",
            value: `${STATS.creditsRemaining} cr`,
          },
          { label: "Risk", value: STATS.riskLevel },
        ].map((m) => (
          <Card key={m.label}>
            <CardContent className="p-4">
              <p className="text-xs text-fg-muted">{m.label}</p>
              <p className="mt-1 text-lg font-semibold capitalize tracking-tight">
                {m.value}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Soft cap burn</CardTitle>
            <CardDescription>
              Daily soft cap {STATS.dailySoftCap} · cascade {STATS.cascade} ·{" "}
              {STATS.burnMultiplier}x
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <div className="mb-1 flex justify-between text-xs text-fg-muted">
                <span>Session vs soft cap</span>
                <span className="tabular">{usedPct}%</span>
              </div>
              <Progress value={usedPct} />
            </div>
            <div>
              <div className="mb-1 flex justify-between text-xs text-fg-muted">
                <span>Pool remaining</span>
                <span className="tabular">{remainPct}%</span>
              </div>
              <Progress value={remainPct} />
            </div>
            <Button
              size="sm"
              variant="secondary"
              onClick={() => toast.success("Quota ledger synced (demo)")}
            >
              Quota sync
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Weekly credit burn</CardTitle>
          </CardHeader>
          <CardContent className="h-52">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={USAGE}>
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
                <Bar dataKey="credits" fill="#e4e4e7" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Recent spend</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {SPEND_HISTORY.map((s) => (
            <div
              key={s.id}
              className="flex items-center justify-between rounded-md border border-border px-3 py-2 text-sm"
            >
              <div>
                <p className="font-medium">{s.label}</p>
                <p className="text-xs text-fg-subtle">
                  {formatRelative(new Date(s.at))}
                </p>
              </div>
              <span className="tabular text-fg-muted">{s.credits} cr</span>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
