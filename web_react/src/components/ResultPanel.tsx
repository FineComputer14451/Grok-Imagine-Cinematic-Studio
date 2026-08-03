import type { ActionResultDto } from '../api/types'

type Props = {
  result: ActionResultDto | null
  loading?: boolean
  error?: string | null
  title?: string
}

export function ResultPanel({ result, loading, error, title = 'Result' }: Props) {
  if (loading) {
    return (
      <section className="card">
        <h3>{title}</h3>
        <p className="muted">Running…</p>
      </section>
    )
  }
  if (error) {
    return (
      <section className="card">
        <h3>{title}</h3>
        <pre className="result fail">{error}</pre>
      </section>
    )
  }
  if (!result) {
    return (
      <section className="card">
        <h3>{title}</h3>
        <p className="muted">No output yet.</p>
      </section>
    )
  }

  const body = result.stdout || result.stderr || '(no output)'
  const cmd = result.argv?.length ? result.argv.join(' ') : result.action_id
  const status = result.ok ? 'OK' : 'FAILED'

  return (
    <section className="card">
      <div className="row between">
        <h3>{title}</h3>
        <span className={`badge ${result.ok ? 'ok' : 'fail'}`}>
          {status} · exit {result.returncode}
          {result.timed_out ? ' · timed out' : ''}
        </span>
      </div>
      <p className="mono muted small">cinematic-studio {cmd}</p>
      {result.errors?.length > 0 && (
        <ul className="error-list">
          {result.errors.map((e) => (
            <li key={e}>{e}</li>
          ))}
        </ul>
      )}
      <pre className={`result ${result.ok ? 'ok' : 'fail'}`}>{body}</pre>
    </section>
  )
}
