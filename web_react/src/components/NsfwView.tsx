import { useQuery } from '@tanstack/react-query'
import { createColumnHelper } from '@tanstack/react-table'
import { useMemo } from 'react'
import { Link } from '@tanstack/react-router'
import { fetchAupStatus, fetchDashboard } from '../api/client'
import { queryKeys } from '../api/queryKeys'
import {
  canEnableNsfwNav,
  fourAupFlags,
  getNsfwOptIn,
  loadSettingsPrefs,
} from '../lib/settingsPrefs'
import { SimpleTable } from './SimpleTable'

const col = createColumnHelper<Record<string, unknown>>()

function str(v: unknown): string {
  if (v == null) return '—'
  if (typeof v === 'object') return JSON.stringify(v)
  return String(v)
}

/**
 * Opt-in NSFW surface — Streamlit parity for *visibility*, not live spend.
 * Batch plan / execute / API generation remain Streamlit or CLI (ActionSpec forbids run/submit).
 */
export function NsfwView() {
  const aupQ = useQuery({
    queryKey: queryKeys.metaAup,
    queryFn: fetchAupStatus,
    retry: false,
  })
  const opted = canEnableNsfwNav({
    fourFlags: fourAupFlags(loadSettingsPrefs()),
    aupValid: aupQ.data?.valid === true,
    localOptIn: getNsfwOptIn(),
  })
  const dashQ = useQuery({
    queryKey: queryKeys.dashboard,
    queryFn: fetchDashboard,
    enabled: opted,
  })

  const batches = useMemo(() => {
    const list = dashQ.data?.nsfw_batches
    if (!Array.isArray(list)) return []
    return list.map((item) =>
      item && typeof item === 'object' ? (item as Record<string, unknown>) : { value: item },
    )
  }, [dashQ.data])

  const columns = useMemo(
    () => [
      col.accessor((r) => str(r.slug ?? r.name), { id: 'slug', header: 'Slug' }),
      col.accessor((r) => str(r.status), { id: 'status', header: 'Status' }),
      col.accessor((r) => str(r.shots_total ?? r.shots_scheduled), {
        id: 'shots',
        header: 'Shots',
      }),
    ],
    [],
  )

  if (!opted) {
    return (
      <div className="stack page">
        <h1>NSFW Pipelines</h1>
        <div className="card fail-box">
          <p>
            Enable <strong>NSFW planning tools</strong> under{' '}
            <Link to="/settings">Settings</Link> after all four AUP flags and{' '}
            <code>nsfw attest</code> on the API host.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="stack page">
      <header>
        <h1>NSFW Pipelines</h1>
        <p className="muted">
          ErosForge planners — explicit <code>ACTIVATE EROSFORGE</code> still required in Grok.
          This SPA shows batch inventory from the dashboard snapshot only. Live plan / execute /
          spend stays on Streamlit or CLI (ActionSpec blocks free-form <code>run</code> /
          <code>submit</code>).
        </p>
      </header>

      <section className="card">
        <h2 className="h2">NSFW batches (snapshot)</h2>
        {dashQ.isLoading && <p className="muted">Loading…</p>}
        {dashQ.isError && <p className="fail">{(dashQ.error as Error).message}</p>}
        {!dashQ.isLoading && (
          <SimpleTable data={batches} columns={columns} empty="No NSFW batches on disk" />
        )}
      </section>

      <section className="card">
        <h2 className="h2">Where to plan / spend</h2>
        <ul className="agent-list">
          <li>
            Streamlit: <code>streamlit run web_ui/app.py</code> → NSFW page (after Settings opt-in)
          </li>
          <li>
            CLI: <code>cinematic-studio nsfw …</code> (see CLI reference)
          </li>
        </ul>
      </section>
    </div>
  )
}
