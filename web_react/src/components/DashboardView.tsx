import { useQuery } from '@tanstack/react-query'
import { createColumnHelper } from '@tanstack/react-table'
import { useMemo, useState } from 'react'
import { fetchDashboard, fetchHealth } from '../api/client'
import { queryKeys } from '../api/queryKeys'
import type { DashboardMode, DashboardSnapshot } from '../api/types'
import {
  DASHBOARD_VIEW_MODES,
  normalizeDashboardMode,
  sectionVisible,
} from '../lib/dashboardMode'
import { SimpleTable } from './SimpleTable'

function asRows(list: unknown): Record<string, unknown>[] {
  if (!Array.isArray(list)) return []
  return list.map((item) =>
    item && typeof item === 'object' ? (item as Record<string, unknown>) : { value: item },
  )
}

function str(v: unknown): string {
  if (v == null) return '—'
  if (typeof v === 'object') return JSON.stringify(v)
  return String(v)
}

function KpiStrip({ snap }: { snap: DashboardSnapshot }) {
  const prod = snap.production ?? {}
  const quota = snap.quota ?? {}
  const items = [
    ['Sequences', prod.sequences],
    ['Characters', prod.characters],
    ['Identity locked', prod.identity_locked],
    ['Imagine jobs', prod.imagine_jobs],
    ['Tier', quota.tier],
    ['Session spent', quota.session_spent],
    ['Budget left', quota.budget_remaining],
  ] as const
  return (
    <div className="kpi-row">
      {items.map(([label, val]) => (
        <div key={label} className="kpi">
          <div className="kpi-label">{label}</div>
          <div className="kpi-value">{str(val)}</div>
        </div>
      ))}
    </div>
  )
}

function JsonBlock({ title, data }: { title: string; data: unknown }) {
  if (data == null) return null
  return (
    <section className="card">
      <h3>{title}</h3>
      <pre className="result">{JSON.stringify(data, null, 2)}</pre>
    </section>
  )
}

const col = createColumnHelper<Record<string, unknown>>()

export function DashboardView() {
  const [mode, setMode] = useState<DashboardMode>('ops')

  const healthQ = useQuery({
    queryKey: queryKeys.health,
    queryFn: fetchHealth,
    refetchInterval: 30_000,
    retry: 1,
  })

  const dashQ = useQuery({
    queryKey: queryKeys.dashboard,
    queryFn: fetchDashboard,
    refetchInterval: 15_000,
    retry: 1,
  })

  const snap = dashQ.data
  const sequences = useMemo(() => asRows(snap?.sequences), [snap])
  const characters = useMemo(() => asRows(snap?.characters), [snap])
  const jobs = useMemo(() => asRows(snap?.recent_jobs), [snap])
  const chainQa = useMemo(() => asRows(snap?.chain_qa), [snap])
  const sfw = useMemo(() => asRows(snap?.sfw_batches), [snap])
  const nsfw = useMemo(() => asRows(snap?.nsfw_batches), [snap])

  const seqCols = useMemo(
    () => [
      col.accessor((r) => str(r.slug ?? r.name), { id: 'slug', header: 'Slug' }),
      col.accessor((r) => str(r.status ?? r.clip_count), { id: 'status', header: 'Status / clips' }),
    ],
    [],
  )
  const charCols = useMemo(
    () => [
      col.accessor((r) => str(r.slug ?? r.name), { id: 'slug', header: 'Slug' }),
      col.accessor((r) => str(r.status), { id: 'status', header: 'Status' }),
    ],
    [],
  )
  const jobCols = useMemo(
    () => [
      col.accessor((r) => str(r.id ?? r.job_id), { id: 'id', header: 'ID' }),
      col.accessor((r) => str(r.status), { id: 'status', header: 'Status' }),
      col.accessor((r) => str(r.kind ?? r.type), { id: 'kind', header: 'Kind' }),
    ],
    [],
  )
  const qaCols = useMemo(
    () => [
      col.accessor((r) => str(r.slug ?? r.sequence), { id: 'slug', header: 'Sequence' }),
      col.accessor((r) => str(r.score ?? r.chain_qa_score), { id: 'score', header: 'Score' }),
      col.accessor((r) => str(r.verdict ?? r.go), { id: 'verdict', header: 'Verdict' }),
    ],
    [],
  )
  const batchCols = useMemo(
    () => [
      col.accessor((r) => str(r.slug ?? r.name), { id: 'slug', header: 'Slug' }),
      col.accessor((r) => str(r.status), { id: 'status', header: 'Status' }),
    ],
    [],
  )

  return (
    <div className="stack page">
      <header className="row between wrap gap">
        <div>
          <h1>Cinematic Studio Dashboard</h1>
          <p className="muted small">
            {healthQ.data
              ? `API v${healthQ.data.studio_version} · ${healthQ.data.actions} actions`
              : healthQ.isError
                ? 'API offline — start: cinematic-studio api --port 8090'
                : 'Connecting…'}
            {snap?.generated_at ? ` · snapshot ${snap.generated_at}` : ''}
          </p>
        </div>
        <div className="row gap">
          <div className="seg">
            {DASHBOARD_VIEW_MODES.map((m) => (
              <button
                key={m}
                type="button"
                className={normalizeDashboardMode(mode) === m ? 'active' : ''}
                onClick={() => setMode(m)}
              >
                {m}
              </button>
            ))}
          </div>
          <button
            type="button"
            className="btn ghost"
            onClick={() => void dashQ.refetch()}
            disabled={dashQ.isFetching}
          >
            Refresh
          </button>
        </div>
      </header>

      {dashQ.isError && (
        <div className="card fail-box">
          <strong>Dashboard error</strong>
          <p>{(dashQ.error as Error).message}</p>
          <p className="muted small">
            Ensure FastAPI is running on port 8090 (or set VITE_STUDIO_API_URL).
          </p>
        </div>
      )}

      {snap && (
        <>
          <section className="card">
            <KpiStrip snap={snap} />
          </section>

          {sectionVisible(mode, 'readiness') && (
            <JsonBlock title="Readiness" data={snap.readiness} />
          )}
          {sectionVisible(mode, 'convergence') && (
            <JsonBlock title="Convergence" data={snap.convergence} />
          )}
          {sectionVisible(mode, 'delivery') && (
            <JsonBlock title="Delivery" data={snap.delivery} />
          )}
          {sectionVisible(mode, 'studio_quota') && (
            <JsonBlock title="Quota" data={snap.quota} />
          )}
          {sectionVisible(mode, 'stack') && (
            <JsonBlock
              title="Studio / stack"
              data={{ studio: snap.studio, project: snap.project, model_stack: snap.model_stack }}
            />
          )}
          {sectionVisible(mode, 'briefs') && (
            <JsonBlock title="Parallel briefs" data={snap.parallel_briefs} />
          )}
          {sectionVisible(mode, 'chain_qa') && (
            <section className="card">
              <h3>Chain QA</h3>
              <SimpleTable data={chainQa} columns={qaCols} empty="No chain QA rows" />
            </section>
          )}
          {sectionVisible(mode, 'sequences') && (
            <section className="card">
              <h3>Sequences</h3>
              <SimpleTable data={sequences} columns={seqCols} empty="No sequences" />
            </section>
          )}
          {sectionVisible(mode, 'characters') && (
            <section className="card">
              <h3>Characters</h3>
              <SimpleTable data={characters} columns={charCols} empty="No characters" />
            </section>
          )}
          {sectionVisible(mode, 'jobs') && (
            <section className="card">
              <h3>Recent jobs</h3>
              <SimpleTable data={jobs} columns={jobCols} empty="No recent jobs" />
            </section>
          )}
          {sectionVisible(mode, 'batches') && (
            <section className="card">
              <h3>SFW batches</h3>
              <SimpleTable data={sfw} columns={batchCols} empty="No SFW batches" />
              <h3 className="mt">NSFW batches</h3>
              <SimpleTable data={nsfw} columns={batchCols} empty="No NSFW batches" />
            </section>
          )}
          {sectionVisible(mode, 'spend') && (
            <JsonBlock title="Spend / production report" data={snap.production_report} />
          )}
          {sectionVisible(mode, 'json') && (
            <JsonBlock title="Full snapshot JSON" data={snap} />
          )}
        </>
      )}

      {dashQ.isLoading && !snap && <p className="muted">Loading dashboard snapshot…</p>}
    </div>
  )
}
