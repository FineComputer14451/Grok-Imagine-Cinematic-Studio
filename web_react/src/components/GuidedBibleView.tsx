import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from '@tanstack/react-router'
import { useEffect, useMemo, useState } from 'react'
import {
  fetchBibleStages,
  generateGuidedBible,
  validateBibleStage,
} from '../api/client'
import { queryKeys } from '../api/queryKeys'
import type { BibleGuidedResult, BibleStage } from '../api/types'
import {
  buildBibleHandoff,
  clearBibleHandoff,
  saveBibleHandoff,
  type BibleHandoff,
} from '../lib/bibleHandoff'
import { loadSettingsPrefs } from '../lib/settingsPrefs'

type Answers = Record<string, string | number>

function seedFromSettings(): Answers {
  const p = loadSettingsPrefs()
  return {
    genre: p.genre || 'Cinematic',
    director_signature: p.director || '',
    complexity: p.complexity || 'Medium',
    target_duration_seconds: p.duration || 60,
    video_model: p.video_model || 'grok-imagine-video',
    chat_model: p.chat_model || 'grok-4.6',
  }
}

function isReview(stage: BibleStage | undefined): boolean {
  return stage?.id === 'review'
}

export function GuidedBibleView() {
  const qc = useQueryClient()
  const stagesQ = useQuery({
    queryKey: queryKeys.bibleStages,
    queryFn: fetchBibleStages,
  })
  const stages = stagesQ.data?.stages ?? []
  const [step, setStep] = useState(0)
  const [answers, setAnswers] = useState<Answers>(() => seedFromSettings())
  const [fieldErrors, setFieldErrors] = useState<string[]>([])
  const [writeFile, setWriteFile] = useState(true)
  const [outputPath, setOutputPath] = useState('production_bible.json')
  const [result, setResult] = useState<BibleGuidedResult | null>(null)
  const [handoff, setHandoff] = useState<BibleHandoff | null>(null)

  const stage = stages[step]
  const n = stages.length || 1
  const progress = ((step + 1) / n) * 100

  useEffect(() => {
    // Re-seed genre/models when settings change mid-session (soft)
    const onPrefs = () => {
      setAnswers((prev) => ({ ...prev, ...seedFromSettings(), title: prev.title }))
    }
    window.addEventListener('cinematic-studio:prefs-updated', onPrefs)
    return () => window.removeEventListener('cinematic-studio:prefs-updated', onPrefs)
  }, [])

  const selectOptions = useMemo(
    () => ({
      genre: [
        'Cinematic',
        'Sci-Fi',
        'Psychological Horror',
        'Action',
        'Drama',
        'Cyberpunk',
        'Intimate Drama',
        'Thriller',
        'Neo-Noir',
        'Fantasy',
        'Documentary Style',
      ],
      complexity: ['Low', 'Medium', 'High', 'Extreme'],
      video_model: ['grok-imagine-video', 'grok-imagine-video-1.5', '1.0', '1.5'],
      chat_model: [
        'grok-4.6',
        'grok-4.3',
        'grok-v9-4p5-multi',
        'grok-v9-4p5-chat-expert',
        'grok-4-auto',
      ],
    }),
    [],
  )

  function setField(key: string, value: string | number) {
    setAnswers((a) => ({ ...a, [key]: value }))
    setFieldErrors([])
  }

  async function goNext() {
    if (!stage || isReview(stage)) return
    // Apply defaults for blank required-with-default
    const next = { ...answers }
    for (const f of stage.fields) {
      const val = next[f.key]
      const blank = val === undefined || val === null || String(val).trim() === ''
      if (blank && f.default != null && String(f.default).trim() !== '') {
        next[f.key] = f.default
      }
    }
    setAnswers(next)
    try {
      const v = await validateBibleStage(stage.id, next)
      if (!v.ok) {
        setFieldErrors(v.errors)
        return
      }
      setFieldErrors([])
      setStep((s) => Math.min(s + 1, n - 1))
    } catch (e) {
      setFieldErrors([(e as Error).message])
    }
  }

  function goBack() {
    setFieldErrors([])
    setStep((s) => Math.max(0, s - 1))
  }

  function resetWizard() {
    setStep(0)
    setAnswers(seedFromSettings())
    setFieldErrors([])
    setResult(null)
    setHandoff(null)
    clearBibleHandoff()
  }

  const generate = useMutation({
    mutationFn: () =>
      generateGuidedBible({
        answers,
        write: writeFile,
        output: outputPath,
      }),
    onSuccess: (r) => {
      setResult(r)
      void qc.invalidateQueries({ queryKey: queryKeys.dashboard })
      if (r.ok && r.bible) {
        const packet = buildBibleHandoff({
          bible: r.bible,
          kwargs: r.kwargs ?? null,
          answers,
          written_path: r.written_path,
        })
        saveBibleHandoff(packet)
        setHandoff(packet)
      }
    },
    onError: (err: Error) => {
      setResult({
        ok: false,
        errors: [err.message],
        bible: null,
        summary: null,
        written_path: null,
      })
      setHandoff(null)
    },
  })

  if (stagesQ.isLoading) {
    return <p className="muted">Loading Bible stages…</p>
  }
  if (stagesQ.isError || !stages.length) {
    return (
      <div className="card fail-box">
        <p className="fail">
          Could not load stages: {(stagesQ.error as Error)?.message ?? 'empty'}
        </p>
        <p className="muted small">
          Start API: <code>cinematic-studio api --port 8090</code>
        </p>
      </div>
    )
  }

  return (
    <div className="stack page">
      <header>
        <h1>Guided Production Bible</h1>
        <p className="muted">
          Same stages as Streamlit / <code>create-bible --wizard</code>, but assembled via{' '}
          <code>build_production_bible</code> over HTTP — <strong>never</strong> free-form{' '}
          <code>--wizard</code> argv. Prefs from <Link to="/settings">Settings</Link> seed genre /
          models / duration.
        </p>
      </header>

      <section className="card stack">
        <div className="row between wrap gap">
          <strong>
            Stage {step + 1}/{n}: {stage?.title}
          </strong>
          <span className="muted small">{Math.round(progress)}%</span>
        </div>
        <div className="progress-track" aria-hidden>
          <div className="progress-fill" style={{ width: `${progress}%` }} />
        </div>

        {!isReview(stage) && stage && (
          <div className="stack">
            {stage.fields.map((f) => {
              const val = answers[f.key] ?? f.default ?? ''
              const opts = selectOptions[f.key as keyof typeof selectOptions]
              const long = ['logline', 'characters_text', 'world_text', 'tech_notes'].includes(
                f.key,
              )
              return (
                <label key={f.key} className="field">
                  <span>
                    {f.prompt}
                    {f.required ? ' *' : ''}
                  </span>
                  {opts ? (
                    <select
                      value={String(val)}
                      onChange={(e) => setField(f.key, e.target.value)}
                    >
                      {!opts.includes(String(val)) && String(val) && (
                        <option value={String(val)}>{String(val)}</option>
                      )}
                      {opts.map((o) => (
                        <option key={o} value={o}>
                          {o}
                        </option>
                      ))}
                    </select>
                  ) : long ? (
                    <textarea
                      rows={3}
                      value={String(val ?? '')}
                      placeholder={f.example || undefined}
                      onChange={(e) => setField(f.key, e.target.value)}
                    />
                  ) : (
                    <input
                      type={f.key === 'target_duration_seconds' ? 'number' : 'text'}
                      min={f.key === 'target_duration_seconds' ? 1 : undefined}
                      value={String(val ?? '')}
                      placeholder={f.example || undefined}
                      onChange={(e) =>
                        setField(
                          f.key,
                          f.key === 'target_duration_seconds'
                            ? Number(e.target.value) || 0
                            : e.target.value,
                        )
                      }
                    />
                  )}
                </label>
              )
            })}
          </div>
        )}

        {isReview(stage) && (
          <div className="stack">
            <p className="muted small">Review mapped answers before generate.</p>
            <pre className="result">{JSON.stringify(answers, null, 2)}</pre>
            <label className="check-row">
              <input
                type="checkbox"
                checked={writeFile}
                onChange={(e) => setWriteFile(e.target.checked)}
              />
              <span>Write JSON to repo path</span>
            </label>
            {writeFile && (
              <label className="field">
                <span>Output path (relative to repo root)</span>
                <input
                  type="text"
                  value={outputPath}
                  onChange={(e) => setOutputPath(e.target.value)}
                />
              </label>
            )}
          </div>
        )}

        {fieldErrors.length > 0 && (
          <ul className="error-list">
            {fieldErrors.map((e) => (
              <li key={e}>{e}</li>
            ))}
          </ul>
        )}

        <div className="row gap wrap">
          <button type="button" className="btn ghost" disabled={step <= 0} onClick={goBack}>
            ← Back
          </button>
          {!isReview(stage) ? (
            <button type="button" className="btn primary" onClick={() => void goNext()}>
              Next →
            </button>
          ) : (
            <button
              type="button"
              className="btn primary"
              disabled={generate.isPending}
              onClick={() => generate.mutate()}
            >
              {generate.isPending ? 'Generating…' : 'Generate Bible'}
            </button>
          )}
          <button type="button" className="btn ghost" onClick={resetWizard}>
            Reset
          </button>
          <Link to="/production" className="btn ghost">
            Production cockpit
          </Link>
        </div>
      </section>

      {result && (
        <section className={`card stack ${result.ok ? '' : 'fail-box'}`}>
          <h2 className="h2">{result.ok ? 'Bible ready' : 'Generate failed'}</h2>
          {result.errors?.length > 0 && (
            <ul className="error-list">
              {result.errors.map((e) => (
                <li key={e}>{e}</li>
              ))}
            </ul>
          )}
          {result.written_path && (
            <p className="badge ok">Wrote {result.written_path}</p>
          )}
          {result.summary && <pre className="result">{result.summary}</pre>}
          {result.bible && (
            <details open>
              <summary className="muted small">Bible JSON preview</summary>
              <pre className="result">{JSON.stringify(result.bible, null, 2)}</pre>
            </details>
          )}
        </section>
      )}

      {handoff && result?.ok && (
        <section className="card stack">
          <h2 className="h2">Next steps (ActionSpec handoff)</h2>
          <p className="muted small">
            Opens cockpit forms with seeds from this Bible (session only). Still
            allowlisted execute — no free-form CLI.
          </p>
          <div className="handoff-grid">
            {handoff.next_steps.map((step) => (
              <Link
                key={step.label + step.to + (step.action ?? '')}
                to={step.to}
                search={
                  step.action
                    ? { action: step.action, from: 'bible' }
                    : { from: 'bible' }
                }
                className="handoff-card"
              >
                <strong>{step.label}</strong>
                <span className="muted small">{step.blurb}</span>
                {step.action && (
                  <span className="mono small dim">{step.action}</span>
                )}
              </Link>
            ))}
          </div>
          <button type="button" className="btn ghost" onClick={() => { clearBibleHandoff(); setHandoff(null) }}>
            Clear handoff seeds
          </button>
        </section>
      )}
    </div>
  )
}
