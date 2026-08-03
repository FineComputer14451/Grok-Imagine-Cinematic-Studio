import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useEffect, useRef, useState } from 'react'
import { executeAction, fetchAction } from '../api/client'
import { queryKeys } from '../api/queryKeys'
import type { ActionResultDto } from '../api/types'
import { ConfirmDialog } from './ConfirmDialog'
import { ResultPanel } from './ResultPanel'

type Props = {
  actionIds: string[]
  labels?: Record<string, string>
  autoRunId?: string
}

export function QuickActionBar({ actionIds, labels, autoRunId }: Props) {
  const qc = useQueryClient()
  const [result, setResult] = useState<ActionResultDto | null>(null)
  const [pendingId, setPendingId] = useState<string | null>(null)
  const autoRan = useRef(false)

  const mutation = useMutation({
    mutationFn: (actionId: string) =>
      executeAction(actionId, { answers: {}, mode: 'inprocess' }),
    onSuccess: (r) => {
      setResult(r)
      void qc.invalidateQueries({ queryKey: queryKeys.dashboard })
    },
    onError: (err: Error, actionId) => {
      setResult({
        ok: false,
        action_id: actionId,
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

  useEffect(() => {
    if (!autoRunId || autoRan.current) return
    autoRan.current = true
    mutation.mutate(autoRunId)
    // eslint-disable-next-line react-hooks/exhaustive-deps -- run once on mount
  }, [autoRunId])

  async function handleClick(actionId: string) {
    try {
      const spec = await fetchAction(actionId)
      if (spec.needs_confirm) {
        setPendingId(actionId)
        return
      }
    } catch {
      /* if fetch fails, still try execute */
    }
    mutation.mutate(actionId)
  }

  return (
    <div className="stack">
      <div className="row gap wrap">
        {actionIds.map((id) => (
          <button
            key={id}
            type="button"
            className="btn ghost"
            disabled={mutation.isPending}
            onClick={() => void handleClick(id)}
          >
            {labels?.[id] ?? id.replace(/_/g, ' ')}
          </button>
        ))}
      </div>
      <ConfirmDialog
        open={pendingId != null}
        title={`Confirm: ${pendingId}`}
        message="This ActionSpec requires confirmation before execute."
        onCancel={() => setPendingId(null)}
        onConfirm={() => {
          if (pendingId) mutation.mutate(pendingId)
          setPendingId(null)
        }}
      />
      <ResultPanel
        result={result}
        loading={mutation.isPending}
        error={null}
        title="Action output"
      />
    </div>
  )
}
