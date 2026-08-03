#!/usr/bin/env node
/**
 * Lightweight smoke (no Chromium) — API + SPA shell + ActionSpec contract.
 *
 * Usage (API must already listen, or pass --start):
 *   node e2e/http-smoke.mjs
 *   node e2e/http-smoke.mjs --start
 *
 * Env:
 *   E2E_API_PORT (default 8090)
 *   E2E_APP_PORT (default 4173) — only if --start or SPA_BASE set
 *   SPA_BASE — optional Vite preview base for SPA HTML checks
 */
import { spawn } from 'node:child_process'
import { existsSync } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const appDir = path.resolve(__dirname, '..')
const repoRoot = path.resolve(appDir, '..')
const apiPort = Number(process.env.E2E_API_PORT || 8090)
const appPort = Number(process.env.E2E_APP_PORT || 4173)
const apiBase = `http://127.0.0.1:${apiPort}`
const spaBase = process.env.SPA_BASE || `http://127.0.0.1:${appPort}`
const doStart = process.argv.includes('--start')

const ROUTES = [
  '/',
  '/production',
  '/dna',
  '/sequences',
  '/imagine',
  '/quota',
  '/bible',
  '/tools',
  '/settings',
  '/nsfw',
]

function assert(cond, msg) {
  if (!cond) throw new Error(msg)
}

async function waitUrl(url, { tries = 60, delayMs = 500 } = {}) {
  let last
  for (let i = 0; i < tries; i++) {
    try {
      const res = await fetch(url)
      if (res.ok) return res
      last = `HTTP ${res.status}`
    } catch (e) {
      last = e instanceof Error ? e.message : String(e)
    }
    await new Promise((r) => setTimeout(r, delayMs))
  }
  throw new Error(`Timeout waiting for ${url}: ${last}`)
}

function startProc(cmd, args, opts) {
  const child = spawn(cmd, args, {
    stdio: ['ignore', 'pipe', 'pipe'],
    ...opts,
  })
  child.stdout.on('data', () => {})
  child.stderr.on('data', () => {})
  return child
}

async function withStack(fn) {
  if (!doStart) return fn()

  const py = path.join(repoRoot, '.venv', 'bin', 'python')
  assert(existsSync(py), `missing ${py}`)
  assert(existsSync(path.join(appDir, 'dist', 'index.html')), 'run npm run build first')

  const api = startProc(
    py,
    ['-m', 'uvicorn', 'studio_api.app:create_app', '--factory', '--host', '127.0.0.1', '--port', String(apiPort)],
    { cwd: repoRoot },
  )
  await waitUrl(`${apiBase}/health`)

  const vite = startProc(
    'npx',
    ['vite', 'preview', '--host', '127.0.0.1', '--port', String(appPort)],
    {
      cwd: appDir,
      env: {
        ...process.env,
        VITE_API_PROXY_TARGET: apiBase,
      },
    },
  )
  await waitUrl(spaBase)

  try {
    return await fn()
  } finally {
    for (const child of [vite, api]) {
      try {
        child.kill('SIGTERM')
      } catch {
        /* ignore */
      }
    }
    // Force-exit if children hang (vite sometimes ignores SIGTERM until idle).
    setTimeout(() => process.exit(0), 500).unref()
  }
}

async function run() {
  // --- API contract ---
  const health = await (await fetch(`${apiBase}/health`)).json()
  assert(health.ok === true, 'health.ok')
  assert(health.actions >= 10, 'actions count')
  assert('xai_api_key_set' in health, 'health xai flag')
  console.log('OK  /health', health.studio_version, 'actions', health.actions)

  const dash = await (await fetch(`${apiBase}/v1/dashboard`)).json()
  assert(dash.studio_version, 'dashboard studio_version')
  console.log('OK  /v1/dashboard')

  const actions = await (await fetch(`${apiBase}/v1/actions`)).json()
  assert(actions.count === actions.actions.length, 'actions count match')
  const ids = new Set(actions.actions.map((a) => a.id))
  for (const id of ['status', 'bible_create', 'handoff_validate', 'models_verify']) {
    assert(ids.has(id), `missing action ${id}`)
  }
  console.log('OK  /v1/actions', actions.count)

  const status = await (
    await fetch(`${apiBase}/v1/actions/status/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answers: {}, mode: 'inprocess', timeout: 60 }),
    })
  ).json()
  assert(status.ok === true, `status execute failed: ${status.stderr || status.errors}`)
  console.log('OK  POST /v1/actions/status/execute')

  const env = await (await fetch(`${apiBase}/v1/meta/env`)).json()
  assert(typeof env.xai_api_key_set === 'boolean', 'meta env')
  const opts = await (await fetch(`${apiBase}/v1/meta/production-options`)).json()
  assert(Array.isArray(opts.genres) && opts.defaults, 'production-options')
  const agents = await (await fetch(`${apiBase}/v1/meta/agents`)).json()
  assert(agents.core_count >= 1, 'agents')
  const cards = await (await fetch(`${apiBase}/v1/meta/role-cards`)).json()
  assert(cards.count >= 1, 'role-cards')
  const stem = cards.role_cards[0].stem
  const card = await (await fetch(`${apiBase}/v1/meta/role-cards/${encodeURIComponent(stem)}`)).json()
  assert(card.content && card.content.length > 20, 'role-card content')
  console.log('OK  /v1/meta/*')

  const stages = await (await fetch(`${apiBase}/v1/bible/stages`)).json()
  assert(stages.count >= 4 && Array.isArray(stages.stages), 'bible stages')
  const guided = await (
    await fetch(`${apiBase}/v1/bible/guided`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        answers: {
          title: 'HTTP Smoke Bible',
          genre: 'Sci-Fi',
          target_duration_seconds: 60,
          complexity: 'Medium',
        },
        write: false,
      }),
    })
  ).json()
  assert(guided.ok === true && guided.bible?.project_title === 'HTTP Smoke Bible', 'bible guided')
  console.log('OK  /v1/bible/*')

  // --- SPA shell (optional if SPA up) ---
  let spaOk = false
  try {
    await waitUrl(spaBase, { tries: doStart ? 60 : 3, delayMs: 300 })
    spaOk = true
  } catch {
    if (doStart) throw new Error('SPA failed to start')
    console.log('SKIP SPA HTML (preview not running; use --start)')
  }

  if (spaOk) {
    for (const route of ROUTES) {
      const res = await fetch(`${spaBase}${route}`)
      assert(res.ok, `SPA ${route} → ${res.status}`)
      const html = await res.text()
      assert(
        html.includes('id="root"') || html.includes("id='root'"),
        `SPA ${route} missing #root`,
      )
      assert(/Cinematic Studio|web_react|vite/i.test(html) || html.includes('root'), `SPA ${route} shell`)
    }
    console.log('OK  SPA routes', ROUTES.length)

    // Proxied API through Vite (same-origin path used by the SPA)
    const proxied = await fetch(`${spaBase}/health`)
    assert(proxied.ok, 'SPA proxy /health')
    const ph = await proxied.json()
    assert(ph.ok === true, 'proxied health json')
    console.log('OK  SPA proxy /health → studio_api')
  }

  console.log('SMOKE http-smoke PASSED')
}

withStack(run)
  .then(() => {
    // Ensure non-zero-hang when child vite/api ignore SIGTERM
    process.exit(0)
  })
  .catch((err) => {
    console.error('SMOKE FAILED:', err.message || err)
    process.exit(1)
  })
