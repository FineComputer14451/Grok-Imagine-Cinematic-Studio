import { Link, useRouterState } from '@tanstack/react-router'
import { useEffect, useState } from 'react'
import { loadBibleHandoff } from '../lib/bibleHandoff'
import { PAGE_CONFIG } from '../lib/pageActions'
import { ActionForm } from './ActionForm'
import { QuickActionBar } from './QuickActionBar'

type Props = {
  pageKey: keyof typeof PAGE_CONFIG
}

function actionFromSearch(search: unknown, formActions: string[]): string | null {
  try {
    const qs =
      typeof search === 'string'
        ? search
        : typeof window !== 'undefined'
          ? window.location.search
          : ''
    const sp = new URLSearchParams(
      qs.startsWith('?') ? qs : qs ? `?${qs}` : window.location.search,
    )
    // TanStack may pass object search — also read window
    if (search && typeof search === 'object' && !Array.isArray(search)) {
      const obj = search as Record<string, unknown>
      const a = obj.action
      if (typeof a === 'string' && formActions.includes(a)) return a
    }
    const action = sp.get('action')
    if (action && formActions.includes(action)) return action
  } catch {
    /* ignore */
  }
  // Fallback: full URL
  if (typeof window !== 'undefined') {
    const action = new URLSearchParams(window.location.search).get('action')
    if (action && formActions.includes(action)) return action
  }
  return null
}

export function CockpitPage({ pageKey }: Props) {
  const cfg = PAGE_CONFIG[pageKey]
  const locationSearch = useRouterState({ select: (s) => s.location.search })
  const [activeForm, setActiveForm] = useState(cfg.formActions[0] ?? '')
  const handoff = loadBibleHandoff()

  useEffect(() => {
    const fromUrl = actionFromSearch(locationSearch, cfg.formActions)
    if (fromUrl) {
      setActiveForm(fromUrl)
    }
  }, [locationSearch, cfg.formActions, pageKey])

  return (
    <div className="stack page">
      <header>
        <h1>{cfg.title}</h1>
        <p className="muted">{cfg.blurb}</p>
        {pageKey === 'production' && (
          <p className="muted small">
            Multi-step creator:{' '}
            <Link to="/bible">Guided Production Bible →</Link> (Streamlit wizard parity, no{' '}
            <code>--wizard</code>).
          </p>
        )}
        {handoff && (
          <p className="muted small prefs-hint">
            Bible handoff active: <strong>{handoff.title}</strong> · {handoff.genre} ·{' '}
            {handoff.duration}s — forms may be pre-seeded.{' '}
            <Link to="/bible">Back to Bible</Link>
          </p>
        )}
      </header>

      <section className="card">
        <h2 className="h2">Quick actions</h2>
        <QuickActionBar actionIds={cfg.quickActions} autoRunId={cfg.listAction} />
      </section>

      {cfg.formActions.length > 0 && (
        <section className="stack">
          <div className="tabs">
            {cfg.formActions.map((id) => (
              <button
                key={id}
                type="button"
                className={activeForm === id ? 'active' : ''}
                onClick={() => setActiveForm(id)}
              >
                {id.replace(/_/g, ' ')}
              </button>
            ))}
          </div>
          {activeForm && (
            <ActionForm
              key={`${activeForm}:${handoff?.generated_at ?? 'none'}`}
              actionId={activeForm}
              forceConfirm={
                activeForm.endsWith('_show') ||
                activeForm === 'handoff_validate' ||
                activeForm === 'imagine_bridge' ||
                activeForm === 'imagine_poll' ||
                activeForm === 'files_get' ||
                activeForm === 'quota_sequence_estimate'
                  ? false
                  : null
              }
            />
          )}
        </section>
      )}
    </div>
  )
}
