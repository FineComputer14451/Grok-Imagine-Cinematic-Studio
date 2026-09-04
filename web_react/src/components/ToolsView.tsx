import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { fetchAgentsRoster, fetchRoleCard, fetchRoleCards } from '../api/client'
import { queryKeys } from '../api/queryKeys'
import { ActionForm } from './ActionForm'
import { QuickActionBar } from './QuickActionBar'

export function ToolsView() {
  const [roleStem, setRoleStem] = useState('')
  const [activeForm, setActiveForm] = useState('handoff_validate')

  const agentsQ = useQuery({
    queryKey: queryKeys.metaAgents,
    queryFn: fetchAgentsRoster,
  })
  const cardsQ = useQuery({
    queryKey: queryKeys.metaRoleCards,
    queryFn: fetchRoleCards,
  })
  const cardQ = useQuery({
    queryKey: queryKeys.metaRoleCard(roleStem),
    queryFn: () => fetchRoleCard(roleStem),
    enabled: Boolean(roleStem),
  })

  const formActions = [
    'handoff_validate',
    'imagine_bridge',
    'imagine_poll',
    'files_get',
    'files_upload',
    'files_delete',
    'wave_a_briefs',
    'sequence_polish_dry',
    'sequence_deliver_dry',
  ]

  return (
    <div className="stack page">
      <header>
        <h1>Tools</h1>
        <p className="muted">
          Validation, reports, plugin status, and Role Cards — ActionSpec execute only (same
          catalog as TUI / NiceGUI). No free-form argv.
        </p>
      </header>

      <section className="card">
        <h2 className="h2">Models & health</h2>
        <QuickActionBar
          actionIds={[
            'models_verify',
            'models_list',
            'status',
            'validate',
            'stack',
            'doctor_quick',
            'plugin_list',
            'files_list',
          ]}
        />
      </section>

      <section className="stack">
        <div className="tabs">
          {formActions.map((id) => (
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
        <ActionForm
          key={activeForm}
          actionId={activeForm}
          forceConfirm={
            activeForm === 'handoff_validate' ||
            activeForm === 'imagine_bridge' ||
            activeForm === 'imagine_poll' ||
            activeForm === 'files_get' ||
            activeForm === 'wave_a_briefs' ||
            activeForm.endsWith('_dry')
              ? false
              : null
          }
        />
      </section>

      <section className="card stack">
        <h2 className="h2">Role Cards</h2>
        {cardsQ.isLoading && <p className="muted">Loading…</p>}
        {cardsQ.isError && (
          <p className="fail">{(cardsQ.error as Error).message}</p>
        )}
        {cardsQ.data && (
          <label className="field">
            <span>Browse Role Card ({cardsQ.data.count})</span>
            <select
              value={roleStem}
              onChange={(e) => setRoleStem(e.target.value)}
            >
              <option value="">— select —</option>
              {cardsQ.data.role_cards.map((c) => (
                <option key={c.stem} value={c.stem}>
                  {c.stem}
                </option>
              ))}
            </select>
          </label>
        )}
        {cardQ.isFetching && <p className="muted small">Loading preview…</p>}
        {cardQ.data && (
          <pre className="result">{cardQ.data.content}</pre>
        )}
      </section>

      <section className="card stack">
        <h2 className="h2">Agent roster</h2>
        {agentsQ.data ? (
          <>
            <p className="muted small">
              {agentsQ.data.core_count} core · {agentsQ.data.total_count} total (incl. specialists)
            </p>
            {Object.entries(agentsQ.data.groups).map(([group, names]) => (
              <div key={group}>
                <strong>{group}</strong>
                <ul className="agent-list">
                  {names.map((n) => (
                    <li key={n}>{n}</li>
                  ))}
                </ul>
              </div>
            ))}
          </>
        ) : agentsQ.isError ? (
          <p className="fail">{(agentsQ.error as Error).message}</p>
        ) : (
          <p className="muted">Loading roster…</p>
        )}
      </section>

      <section className="card">
        <h2 className="h2">PDF report</h2>
        <p className="muted small">
          Production PDF download stays on Streamlit Tools (temp file + browser download). Use CLI:{' '}
          <code>cinematic-studio report --output artifacts/production_report.pdf</code>
        </p>
      </section>
    </div>
  )
}
