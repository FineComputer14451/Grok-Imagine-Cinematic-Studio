import { useQuery } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import {
  fetchDashboard,
  fetchEnvStatus,
  fetchHealth,
  fetchProductionOptions,
} from '../api/client'
import { queryKeys } from '../api/queryKeys'
import {
  FALLBACK_DEFAULTS,
  loadSettingsPrefs,
  notifyPrefsUpdated,
  saveSettingsPrefs,
  setNsfwOptIn,
  type SettingsPrefs,
} from '../lib/settingsPrefs'

function FieldSelect({
  label,
  value,
  options,
  onChange,
}: {
  label: string
  value: string
  options: string[]
  onChange: (v: string) => void
}) {
  return (
    <label className="field">
      <span>{label}</span>
      <select value={value} onChange={(e) => onChange(e.target.value)}>
        {options.map((o) => (
          <option key={o} value={o}>
            {o}
          </option>
        ))}
      </select>
    </label>
  )
}

export function SettingsView() {
  const [prefs, setPrefs] = useState<SettingsPrefs>(() => loadSettingsPrefs())
  const [savedFlash, setSavedFlash] = useState(false)

  const optsQ = useQuery({
    queryKey: queryKeys.metaOptions,
    queryFn: fetchProductionOptions,
  })
  const envQ = useQuery({
    queryKey: queryKeys.metaEnv,
    queryFn: fetchEnvStatus,
  })
  const healthQ = useQuery({
    queryKey: queryKeys.health,
    queryFn: fetchHealth,
  })
  const dashQ = useQuery({
    queryKey: queryKeys.dashboard,
    queryFn: fetchDashboard,
  })

  const opts = optsQ.data
  const genres = opts?.genres ?? [prefs.genre]
  const directors = opts?.directors ?? [prefs.director]
  const complexities = opts?.complexities ?? [prefs.complexity]
  const tiers = opts?.tiers ?? [prefs.quota_tier]
  const reasoning = opts?.reasoning_levels ?? ['low', 'medium', 'high']
  const chatModels = opts?.chat_models ?? [prefs.chat_model]
  const videoModels = opts?.video_models ?? [prefs.video_model]
  const regions = opts?.imagine_regions ?? [prefs.imagine_region]

  useEffect(() => {
    if (!opts?.defaults) return
    // Fill empty fields from server defaults only once if prefs are still fallback
  }, [opts])

  function update<K extends keyof SettingsPrefs>(key: K, value: SettingsPrefs[K]) {
    setPrefs((p) => ({ ...p, [key]: value }))
  }

  function handleSave() {
    saveSettingsPrefs(prefs)
    setNsfwOptIn(prefs.nsfw_opt_in)
    notifyPrefsUpdated()
    setSavedFlash(true)
    window.setTimeout(() => setSavedFlash(false), 2000)
  }

  function handleReset() {
    const next = { ...FALLBACK_DEFAULTS, ...(opts?.defaults as Partial<SettingsPrefs>) }
    setPrefs({
      ...FALLBACK_DEFAULTS,
      genre: String(next.genre ?? FALLBACK_DEFAULTS.genre),
      director: String(next.director ?? FALLBACK_DEFAULTS.director),
      video_model: String(next.video_model ?? FALLBACK_DEFAULTS.video_model),
      chat_model: String(next.chat_model ?? FALLBACK_DEFAULTS.chat_model),
      duration: Number(next.duration ?? FALLBACK_DEFAULTS.duration),
      complexity: String(next.complexity ?? FALLBACK_DEFAULTS.complexity),
      fast_mode: Boolean(next.fast_mode),
      quota_tier: String(next.quota_tier ?? FALLBACK_DEFAULTS.quota_tier),
      imagine_region: String(next.imagine_region ?? FALLBACK_DEFAULTS.imagine_region),
      nsfw_opt_in: false,
      reasoning_level: String(next.reasoning_level ?? FALLBACK_DEFAULTS.reasoning_level),
      prompt_cache_key: String(next.prompt_cache_key ?? ''),
      dashboard_view_mode: String(next.dashboard_view_mode ?? 'ops'),
    })
  }

  const stack = dashQ.data?.studio ?? dashQ.data?.model_stack

  return (
    <div className="stack page">
      <header>
        <h1>Settings</h1>
        <p className="muted">
          Session defaults for Production / Quota / Imagine (browser localStorage). Orchestration
          defaults to <strong>Grok 4.5</strong>. Does not replace Streamlit secrets for cloud
          deploy.
        </p>
      </header>

      <section className="card stack">
        <h2 className="h2">Model Layer</h2>
        <p className="muted small">
          Studio {healthQ.data?.studio_version ?? '…'} ·{' '}
          {healthQ.data?.actions ?? '—'} ActionSpecs registered
        </p>
        <div className="grid-2">
          <FieldSelect
            label="Chat / orchestration model"
            value={prefs.chat_model}
            options={chatModels}
            onChange={(v) => update('chat_model', v)}
          />
          <FieldSelect
            label="Imagine Video model"
            value={prefs.video_model}
            options={videoModels}
            onChange={(v) => update('video_model', v)}
          />
          <FieldSelect
            label="Preferred reasoning"
            value={prefs.reasoning_level}
            options={reasoning}
            onChange={(v) => update('reasoning_level', v)}
          />
          <label className="field">
            <span>prompt_cache_key (project slug)</span>
            <input
              type="text"
              value={prefs.prompt_cache_key}
              onChange={(e) => update('prompt_cache_key', e.target.value)}
              placeholder="my-film-slug"
            />
          </label>
        </div>
        {stack != null && (
          <details>
            <summary className="muted small">Studio / stack snapshot</summary>
            <pre className="result">{JSON.stringify(stack, null, 2)}</pre>
          </details>
        )}
      </section>

      <section className="card stack">
        <h2 className="h2">Production defaults</h2>
        <div className="grid-2">
          <FieldSelect
            label="Genre"
            value={prefs.genre}
            options={genres}
            onChange={(v) => update('genre', v)}
          />
          <FieldSelect
            label="Director signature"
            value={prefs.director}
            options={directors}
            onChange={(v) => update('director', v)}
          />
          <label className="field">
            <span>Duration (seconds)</span>
            <input
              type="number"
              min={15}
              max={180}
              step={5}
              value={prefs.duration}
              onChange={(e) => update('duration', Number(e.target.value) || 60)}
            />
          </label>
          <FieldSelect
            label="Complexity"
            value={prefs.complexity}
            options={complexities}
            onChange={(v) => update('complexity', v)}
          />
          <FieldSelect
            label="Subscription tier"
            value={prefs.quota_tier}
            options={tiers}
            onChange={(v) => update('quota_tier', v)}
          />
          <FieldSelect
            label="Imagine API region"
            value={prefs.imagine_region}
            options={regions}
            onChange={(v) => update('imagine_region', v)}
          />
        </div>
        <label className="check-row">
          <input
            type="checkbox"
            checked={prefs.fast_mode}
            onChange={(e) => update('fast_mode', e.target.checked)}
          />
          <span>Fast mode</span>
        </label>
      </section>

      <section className="card stack">
        <h2 className="h2">xAI API key</h2>
        {envQ.data?.xai_api_key_set || healthQ.data?.xai_api_key_set ? (
          <p className="badge ok">Key present on API process (env) — material not shown</p>
        ) : (
          <p className="muted">
            No <code>XAI_API_KEY</code> on the API process. Live Imagine batch stays dry-run /
            Streamlit-only. Set the key on the server, not in this SPA.
          </p>
        )}
        <p className="muted small">{envQ.data?.note}</p>
      </section>

      <section className="card stack">
        <h2 className="h2">NSFW pipelines</h2>
        <label className="check-row">
          <input
            type="checkbox"
            checked={prefs.nsfw_opt_in}
            onChange={(e) => update('nsfw_opt_in', e.target.checked)}
          />
          <span>Enable NSFW planning tools (unlocks NSFW nav)</span>
        </label>
        <p className="muted small">
          Explicit ErosForge activation is still required in Grok. Live batch execute remains on
          Streamlit when an API key is set; this SPA only shows plans/batches from the dashboard
          snapshot.
        </p>
      </section>

      <section className="card">
        <h2 className="h2">ActionSpec form seeding</h2>
        <p className="muted small">
          Saved prefs pre-fill matching ActionSpec fields on Production / DNA / Sequences /
          Quota / Tools (e.g. <code>genre</code>, <code>chat_model</code>,{' '}
          <code>video_model</code>, <code>duration</code>, <code>tier</code>). Re-open a form
          tab after save to pick up new defaults. Never invents free-form argv.
        </p>
      </section>

      <div className="row gap">
        <button type="button" className="btn primary" onClick={handleSave}>
          Save preferences
        </button>
        <button type="button" className="btn ghost" onClick={handleReset}>
          Reset defaults
        </button>
        {savedFlash && <span className="badge ok">Saved</span>}
      </div>
    </div>
  )
}
