import { useForm } from '@tanstack/react-form'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect, useMemo, useState } from 'react'
import { executeAction, fetchAction, uploadInboxFile } from '../api/client'
import { queryKeys } from '../api/queryKeys'
import type { ActionResultDto, ActionSpecDto } from '../api/types'
import {
  actionUsesSettingsPrefs,
  applyPrefsToFieldDefaults,
} from '../lib/prefsToAnswers'
import { BIBLE_HANDOFF_EVENT } from '../lib/bibleHandoff'
import { loadSettingsPrefs, PREFS_UPDATED_EVENT } from '../lib/settingsPrefs'
import { ConfirmDialog } from './ConfirmDialog'
import { ResultPanel } from './ResultPanel'

type Props = {
  actionId: string
  /** Skip confirm even if needs_confirm (read-only actions). */
  forceConfirm?: boolean | null
  onDone?: (result: ActionResultDto) => void
}

function ActionFormReady({
  spec,
  forceConfirm,
  onDone,
  prefsEpoch,
}: {
  spec: ActionSpecDto
  forceConfirm?: boolean | null
  onDone?: (result: ActionResultDto) => void
  prefsEpoch: number
}) {
  const qc = useQueryClient()
  const [pendingAnswers, setPendingAnswers] = useState<Record<string, string> | null>(null)
  const [lastResult, setLastResult] = useState<ActionResultDto | null>(null)

  const { defaults, applied } = useMemo(() => {
    return applyPrefsToFieldDefaults(spec.fields, loadSettingsPrefs(), spec.id)
    // prefsEpoch forces recompute after Settings / bible handoff
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [spec, prefsEpoch])

  const [inboxNote, setInboxNote] = useState('')
  const [inboxBusy, setInboxBusy] = useState(false)
  const [inboxPath, setInboxPath] = useState('')

  const mutation = useMutation({
    mutationFn: (answers: Record<string, string>) =>
      executeAction(spec.id, { answers, mode: 'inprocess' }),
    onSuccess: (result) => {
      setLastResult(result)
      void qc.invalidateQueries({ queryKey: queryKeys.dashboard })
      onDone?.(result)
    },
    onError: (err: Error) => {
      setLastResult({
        ok: false,
        action_id: spec.id,
        argv: [],
        returncode: 1,
        stdout: '',
        stderr: err.message,
        errors: [err.message],
        timed_out: false,
        mode: 'inprocess',
      })
    },
  })

  const form = useForm({
    defaultValues: defaults,
    onSubmit: async ({ value }) => {
      const answers: Record<string, string> = {}
      for (const [k, v] of Object.entries(value)) {
        answers[k] = v == null ? '' : String(v)
      }
      if (spec.id === 'files_upload' && inboxPath && !answers.path?.trim()) {
        answers.path = inboxPath
      }
      const needs =
        forceConfirm === false
          ? false
          : forceConfirm === true
            ? true
            : Boolean(spec.needs_confirm)
      if (needs) {
        setPendingAnswers(answers)
        return
      }
      mutation.mutate(answers)
    },
  })

  return (
    <div className="action-form-block">
      <div className="card">
        <h3>{spec.label}</h3>
        <p className="muted small">{spec.description}</p>
        {applied.length > 0 && (
          <p className="muted small prefs-hint">
            Prefs seeded: {applied.join(', ')}{' '}
            <span className="dim">(Settings and/or Guided Bible handoff)</span>
          </p>
        )}
        {actionUsesSettingsPrefs(spec.fields) && applied.length === 0 && (
          <p className="muted small prefs-hint">
            This form can use Settings prefs — set genre / models / duration under Settings.
          </p>
        )}
        <form
          className="stack"
          onSubmit={(e) => {
            e.preventDefault()
            e.stopPropagation()
            void form.handleSubmit()
          }}
        >
          {spec.id === 'files_upload' && (
            <label className="field">
              <span>Drop plate (saved to API inbox, then paste path)</span>
              <input
                type="file"
                accept="image/png,image/jpeg,image/webp,image/gif,video/mp4"
                disabled={inboxBusy}
                onChange={(e) => {
                  const file = e.target.files?.[0]
                  e.target.value = ''
                  if (!file) return
                  setInboxBusy(true)
                  setInboxNote('Uploading to inbox…')
                  void uploadInboxFile(file)
                    .then((saved) => {
                      setInboxPath(saved.path)
                      form.setFieldValue('path', saved.path)
                      setInboxNote(`Saved ${saved.filename} (${saved.bytes} bytes) — confirm Files upload`)
                    })
                    .catch((err: Error) => {
                      setInboxNote(err.message)
                    })
                    .finally(() => setInboxBusy(false))
                }}
              />
              {inboxNote ? <span className="muted small">{inboxNote}</span> : null}
            </label>
          )}
          {spec.fields.map((field) => (
            <form.Field
              key={field.key}
              name={field.key}
              validators={{
                onChange: ({ value }) => {
                  if (field.required && !String(value ?? '').trim()) {
                    return `${field.label} is required`
                  }
                  return undefined
                },
              }}
            >
              {(fieldApi) => (
                <label className="field">
                  <span>
                    {field.label}
                    {field.required ? ' *' : ''}
                    {applied.includes(field.key) ? (
                      <span className="pref-dot" title="Seeded from Settings">
                        {' '}
                        · prefs
                      </span>
                    ) : null}
                  </span>
                  {field.choices && field.choices.length > 0 ? (
                    <select
                      value={String(fieldApi.state.value ?? field.default ?? '')}
                      onBlur={fieldApi.handleBlur}
                      onChange={(e) => fieldApi.handleChange(e.target.value)}
                    >
                      {field.choices.map((c) => (
                        <option key={c} value={c}>
                          {c}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <input
                      type={
                        field.coerce === 'int' || field.coerce === 'float' ? 'number' : 'text'
                      }
                      step={
                        field.coerce === 'float'
                          ? 'any'
                          : field.coerce === 'int'
                            ? '1'
                            : undefined
                      }
                      value={String(fieldApi.state.value ?? '')}
                      onBlur={fieldApi.handleBlur}
                      onChange={(e) => fieldApi.handleChange(e.target.value)}
                      placeholder={field.help || undefined}
                    />
                  )}
                  {fieldApi.state.meta.errors?.[0] && (
                    <span className="field-error">{String(fieldApi.state.meta.errors[0])}</span>
                  )}
                </label>
              )}
            </form.Field>
          ))}
          {spec.fields.length === 0 && (
            <p className="muted small">No fields — runs with empty answers.</p>
          )}
          <button type="submit" className="btn primary" disabled={mutation.isPending}>
            {mutation.isPending ? 'Running…' : `Run ${spec.label}`}
          </button>
        </form>
      </div>

      <ConfirmDialog
        open={pendingAnswers != null}
        title={`Confirm: ${spec.label}`}
        message={`Execute ActionSpec “${spec.id}”? Same safety model as TUI/NiceGUI (allowlisted argv only).`}
        onCancel={() => setPendingAnswers(null)}
        onConfirm={() => {
          if (pendingAnswers) {
            mutation.mutate(pendingAnswers)
          }
          setPendingAnswers(null)
        }}
      />

      {(lastResult || mutation.isPending || mutation.isError) && (
        <ResultPanel
          result={lastResult}
          loading={mutation.isPending}
          error={mutation.isError ? (mutation.error as Error).message : null}
        />
      )}
    </div>
  )
}

export function ActionForm({ actionId, forceConfirm, onDone }: Props) {
  const [prefsEpoch, setPrefsEpoch] = useState(0)

  useEffect(() => {
    const bump = () => setPrefsEpoch((n) => n + 1)
    window.addEventListener(PREFS_UPDATED_EVENT, bump)
    window.addEventListener(BIBLE_HANDOFF_EVENT, bump)
    window.addEventListener('storage', bump)
    return () => {
      window.removeEventListener(PREFS_UPDATED_EVENT, bump)
      window.removeEventListener(BIBLE_HANDOFF_EVENT, bump)
      window.removeEventListener('storage', bump)
    }
  }, [])

  const actionQuery = useQuery({
    queryKey: queryKeys.action(actionId),
    queryFn: () => fetchAction(actionId),
  })

  if (actionQuery.isLoading) {
    return <p className="muted">Loading action {actionId}…</p>
  }
  if (actionQuery.isError || !actionQuery.data) {
    return (
      <p className="fail">
        Failed to load action <code>{actionId}</code>:{' '}
        {(actionQuery.error as Error)?.message ?? 'unknown'}
      </p>
    )
  }

  return (
    <ActionFormReady
      key={`${actionId}:${prefsEpoch}`}
      spec={actionQuery.data}
      forceConfirm={forceConfirm}
      onDone={onDone}
      prefsEpoch={prefsEpoch}
    />
  )
}
