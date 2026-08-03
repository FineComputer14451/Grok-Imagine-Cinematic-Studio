import type { DashboardMode } from '../api/types'

/** TUI / NiceGUI / Streamlit density parity. */
export const DASHBOARD_VIEW_MODES: DashboardMode[] = ['compact', 'ops', 'full']

export const DASHBOARD_MODE_SECTIONS: Record<DashboardMode, ReadonlySet<string>> = {
  compact: new Set(['health_actions', 'readiness']),
  ops: new Set([
    'health_actions',
    'readiness',
    'convergence',
    'delivery',
    'studio_quota',
    'stack',
    'chain_qa',
  ]),
  full: new Set([
    'health_actions',
    'readiness',
    'convergence',
    'briefs',
    'delivery',
    'studio_quota',
    'stack',
    'sequences',
    'chain_qa',
    'characters',
    'jobs',
    'batches',
    'spend',
    'json',
  ]),
}

export function normalizeDashboardMode(mode: string | null | undefined): DashboardMode {
  const m = (mode || 'ops').trim().toLowerCase()
  return (DASHBOARD_VIEW_MODES as string[]).includes(m) ? (m as DashboardMode) : 'ops'
}

export function sectionVisible(mode: string, section: string): boolean {
  const m = normalizeDashboardMode(mode)
  return DASHBOARD_MODE_SECTIONS[m].has(section)
}
