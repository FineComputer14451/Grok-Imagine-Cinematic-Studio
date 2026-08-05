import { createFileRoute, Link } from "@tanstack/react-router";
import {
  AlertTriangle,
  BookOpen,
  ChevronRight,
  Code2,
  DollarSign,
  ExternalLink,
  GitMerge,
  Search,
  Shield,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { CopyButton } from "@/components/copy-button";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  API_ERRORS,
  API_OVERVIEW,
  API_SECTIONS,
  API_STATUS_CODES,
  GROK_PRICING,
  SPEND_RULES,
  type ApiEndpoint,
} from "@/data/api-docs";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/docs")({
  component: DocsPage,
});

const METHOD_STYLE: Record<ApiEndpoint["method"], string> = {
  GET: "border-teal/40 bg-teal/10 text-teal",
  POST: "border-amber/40 bg-amber/10 text-amber",
};

function DocsPage() {
  const [q, setQ] = useState("");
  const [sectionId, setSectionId] = useState(API_SECTIONS[0]?.id ?? "auth");
  const [endpointId, setEndpointId] = useState(
    API_SECTIONS[0]?.endpoints[0]?.id ?? "",
  );

  const flat = useMemo(
    () =>
      API_SECTIONS.flatMap((s) =>
        s.endpoints.map((e) => ({
          ...e,
          sectionId: s.id,
          sectionTitle: s.title,
        })),
      ),
    [],
  );

  const filtered = useMemo(() => {
    if (!q.trim()) return flat;
    const needle = q.trim().toLowerCase();
    return flat.filter((e) =>
      `${e.title} ${e.path} ${e.summary} ${e.method} ${e.sectionTitle}`
        .toLowerCase()
        .includes(needle),
    );
  }, [flat, q]);

  useEffect(() => {
    if (filtered.length === 0) return;
    const stillVisible = filtered.some((e) => e.id === endpointId);
    if (!stillVisible) {
      setEndpointId(filtered[0].id);
      setSectionId(filtered[0].sectionId);
    }
  }, [filtered, endpointId]);

  const active =
    filtered.find((e) => e.id === endpointId) ?? filtered[0] ?? null;

  const section =
    API_SECTIONS.find((s) => s.id === (active?.sectionId ?? sectionId)) ??
    API_SECTIONS[0];

  return (
    <div className="space-y-8">
      <div>
        <Badge variant="teal">Reference</Badge>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">
          {API_OVERVIEW.title}
        </h1>
        <p className="mt-2 max-w-2xl text-muted leading-relaxed">
          {API_OVERVIEW.description}
        </p>
        <div className="mt-3 flex flex-wrap gap-2 text-xs">
          <span className="rounded-md border border-border bg-surface px-2 py-1 font-mono text-subtle">
            {API_OVERVIEW.version}
          </span>
          <span className="rounded-md border border-border bg-surface px-2 py-1 font-mono text-teal">
            {API_OVERVIEW.base}
          </span>
          <span className="rounded-md border border-border bg-surface px-2 py-1 font-mono text-subtle">
            {API_OVERVIEW.auth}
          </span>
        </div>
        <div className="mt-3 flex flex-wrap gap-3 text-sm">
          <a
            href="https://docs.x.ai"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1.5 text-teal hover:underline"
          >
            docs.x.ai
            <ExternalLink className="h-3.5 w-3.5" />
          </a>
          <Link
            to="/pricing"
            className="inline-flex items-center gap-1.5 text-teal hover:underline"
          >
            <DollarSign className="h-3.5 w-3.5" />
            Full pricing tables
          </Link>
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: "Chat in (list)", value: "$2 / 1M" },
          { label: "Chat out (list)", value: "$6 / 1M" },
          { label: "Standard still (list)", value: "$0.02" },
          { label: "Video 720p (list)", value: "$0.07 / s" },
        ].map((s) => (
          <div
            key={s.label}
            className="rounded-xl border border-border bg-surface px-4 py-4"
          >
            <p className="font-mono text-lg font-semibold tabular-nums text-teal">
              {s.value}
            </p>
            <p className="mt-1 text-xs uppercase tracking-wide text-muted">
              {s.label}
            </p>
          </div>
        ))}
      </div>
      <p className="text-xs text-subtle -mt-4">
        Published API list prices (not draft rate cards). See{" "}
        <Link to="/pricing" className="text-teal hover:underline">
          Pricing
        </Link>{" "}
        for full tables and worked examples.
      </p>

      <Card className="border-amber/30 bg-amber/5">
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-base">
            <AlertTriangle className="h-4 w-4 text-amber" />
            Spend responsibly
          </CardTitle>
          <CardDescription>
            Every call uses the app owner’s personal quota and credits —
            including anonymous visitors on a deployed app. As of{" "}
            {GROK_PRICING.asOf}.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="grid gap-2 sm:grid-cols-2">
            {SPEND_RULES.map((rule) => (
              <li
                key={rule}
                className="flex gap-2 text-sm text-muted leading-relaxed"
              >
                <Shield className="mt-0.5 h-3.5 w-3.5 shrink-0 text-amber" />
                <span>{rule}</span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <label className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-subtle" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search chat, images, video, TTS…"
            className="h-11 w-full rounded-lg border border-border bg-surface pl-10 pr-3 text-sm text-fg placeholder:text-subtle outline-none focus:border-border-strong focus:ring-2 focus:ring-teal/30"
          />
        </label>
        <div className="flex flex-wrap gap-2">
          <Link
            to="/pricing"
            className="inline-flex h-11 items-center gap-2 rounded-lg border border-border bg-elevated px-4 text-sm text-muted hover:text-fg"
          >
            <DollarSign className="h-4 w-4 text-teal" />
            Pricing
          </Link>
          <Link
            to="/workflows"
            className="inline-flex h-11 items-center gap-2 rounded-lg border border-border bg-elevated px-4 text-sm text-muted hover:text-fg"
          >
            <GitMerge className="h-4 w-4 text-teal" />
            Workflows
          </Link>
          <Link
            to="/learn"
            className="inline-flex h-11 items-center gap-2 rounded-lg border border-border bg-elevated px-4 text-sm text-muted hover:text-fg"
          >
            <BookOpen className="h-4 w-4 text-teal" />
            Learn path
          </Link>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,0.85fr)_minmax(0,1.15fr)]">
        <aside className="space-y-4 lg:sticky lg:top-20 lg:self-start">
          {API_SECTIONS.map((s) => {
            const items = filtered.filter((e) => e.sectionId === s.id);
            if (q.trim() && items.length === 0) return null;
            return (
              <div key={s.id}>
                <button
                  type="button"
                  onClick={() => {
                    setSectionId(s.id);
                    setQ("");
                    if (s.endpoints[0]) setEndpointId(s.endpoints[0].id);
                  }}
                  className="mb-2 flex w-full items-center justify-between text-left text-xs font-medium uppercase tracking-wide text-subtle hover:text-fg"
                >
                  {s.title}
                  <span className="font-mono normal-case tracking-normal">
                    {(q.trim() ? items : s.endpoints).length}
                  </span>
                </button>
                <ul className="space-y-1">
                  {(q.trim() ? items : s.endpoints).map((e) => {
                    const selected = active?.id === e.id;
                    return (
                      <li key={e.id}>
                        <button
                          type="button"
                          onClick={() => {
                            setEndpointId(e.id);
                            setSectionId(s.id);
                          }}
                          className={cn(
                            "flex w-full items-center gap-2 rounded-lg border px-3 py-2.5 text-left text-sm transition-colors",
                            selected
                              ? "border-teal/40 bg-teal/5 text-fg"
                              : "border-transparent bg-surface/60 text-muted hover:border-border hover:text-fg",
                          )}
                        >
                          <span
                            className={cn(
                              "shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-semibold",
                              METHOD_STYLE[e.method],
                            )}
                          >
                            {e.method}
                          </span>
                          <span className="min-w-0 flex-1 truncate">
                            {e.title}
                          </span>
                          {selected && (
                            <ChevronRight className="h-3.5 w-3.5 shrink-0 text-teal" />
                          )}
                        </button>
                      </li>
                    );
                  })}
                </ul>
              </div>
            );
          })}

          {filtered.length === 0 && (
            <p className="text-sm text-muted">No endpoints match that search.</p>
          )}
        </aside>

        <div className="space-y-6">
          {section && (
            <p className="text-sm text-muted leading-relaxed">{section.intro}</p>
          )}

          {active ? (
            <EndpointDetail endpoint={active} />
          ) : (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Select an endpoint</CardTitle>
                <CardDescription>
                  Auth, chat, images, video, voice, or studio bridge.
                </CardDescription>
              </CardHeader>
            </Card>
          )}

          <Card>
            <CardHeader>
              <CardTitle className="text-base">HTTP & job status</CardTitle>
              <CardDescription>
                Common response codes and async video states.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto rounded-lg border border-border">
                <table className="w-full min-w-[320px] text-left text-sm">
                  <thead className="border-b border-border bg-elevated/50 text-xs uppercase tracking-wide text-subtle">
                    <tr>
                      <th className="px-3 py-2 font-medium">Code</th>
                      <th className="px-3 py-2 font-medium">Meaning</th>
                    </tr>
                  </thead>
                  <tbody>
                    {API_STATUS_CODES.map((row) => (
                      <tr
                        key={row.code}
                        className="border-b border-border/80 last:border-0"
                      >
                        <td className="px-3 py-2.5 font-mono text-xs text-teal">
                          {row.code}
                        </td>
                        <td className="px-3 py-2.5 text-muted">{row.meaning}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Common integration errors</CardTitle>
              <CardDescription>
                Failures from wrong key handling or spend patterns.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              {API_ERRORS.map((err) => (
                <div
                  key={err.error}
                  className="rounded-lg border border-border bg-bg px-3 py-3"
                >
                  <p className="font-mono text-xs text-danger">{err.error}</p>
                  <p className="mt-1 text-sm text-muted">{err.fix}</p>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

function EndpointDetail({
  endpoint,
}: {
  endpoint: ApiEndpoint & { sectionId?: string; sectionTitle?: string };
}) {
  return (
    <Card className="border-teal/20">
      <CardHeader>
        <div className="flex flex-wrap items-center gap-2">
          <span
            className={cn(
              "rounded-md border px-2 py-0.5 font-mono text-[11px] font-semibold",
              METHOD_STYLE[endpoint.method],
            )}
          >
            {endpoint.method}
          </span>
          <code className="text-xs text-muted break-all">{endpoint.path}</code>
        </div>
        <CardTitle className="mt-2 text-xl">{endpoint.title}</CardTitle>
        <CardDescription>{endpoint.summary}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-5">
        {endpoint.request && (
          <CodeBlock label="Request / example" code={endpoint.request} />
        )}
        {endpoint.response && (
          <CodeBlock label="Response" code={endpoint.response} />
        )}
        {endpoint.notes && endpoint.notes.length > 0 && (
          <div>
            <p className="mb-2 text-xs font-medium uppercase tracking-wide text-subtle">
              Notes
            </p>
            <ul className="space-y-1.5 text-sm text-muted">
              {endpoint.notes.map((n) => (
                <li key={n} className="flex gap-2">
                  <span className="text-teal">·</span>
                  <span className="leading-relaxed">{n}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function CodeBlock({ label, code }: { label: string; code: string }) {
  return (
    <div>
      <div className="mb-2 flex items-center justify-between gap-2">
        <p className="flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-subtle">
          <Code2 className="h-3.5 w-3.5 text-teal" />
          {label}
        </p>
        <CopyButton text={code} label="Copy" />
      </div>
      <pre className="overflow-x-auto rounded-lg border border-border bg-bg p-3.5 font-mono text-[11px] leading-relaxed text-muted whitespace-pre-wrap">
        {code}
      </pre>
    </div>
  );
}
