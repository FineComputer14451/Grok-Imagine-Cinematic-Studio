import { expect, test, type Page } from '@playwright/test'

/** Always-on Streamlit-parity routes + expected H1 text. */
const ROUTES: { path: string; heading: string | RegExp }[] = [
  { path: '/', heading: /Cinematic Studio Dashboard/i },
  { path: '/production', heading: /^Production$/i },
  { path: '/dna', heading: /Character DNA/i },
  { path: '/sequences', heading: /^Sequences$/i },
  { path: '/imagine', heading: /^Imagine$/i },
  { path: '/quota', heading: /^Quota$/i },
  { path: '/tools', heading: /^Tools$/i },
  { path: '/settings', heading: /^Settings$/i },
]

const SETTINGS_KEY = 'cinematic-studio.web-react.settings.v1'

async function seedNsfwOptIn(page: Page) {
  await page.addInitScript((key) => {
    const base = {
      genre: 'Sci-Fi',
      director: 'Denis Villeneuve',
      video_model: 'grok-imagine-video',
      chat_model: 'grok-4.5',
      duration: 60,
      complexity: 'Medium',
      fast_mode: false,
      quota_tier: 'supergrok_pro',
      imagine_region: 'us-east-1',
      nsfw_opt_in: true,
      reasoning_level: 'high',
      prompt_cache_key: 'e2e-smoke',
      dashboard_view_mode: 'ops',
    }
    localStorage.setItem(key, JSON.stringify(base))
  }, SETTINGS_KEY)
}

test.describe('React cockpit route smoke', () => {
  test('API health is reachable', async ({ request }) => {
    const apiPort = process.env.E2E_API_PORT || '8090'
    const res = await request.get(`http://127.0.0.1:${apiPort}/health`)
    expect(res.ok()).toBeTruthy()
    const body = await res.json()
    expect(body.ok).toBe(true)
    expect(body.actions).toBeGreaterThan(10)
  })

  for (const { path, heading } of ROUTES) {
    test(`loads ${path}`, async ({ page }) => {
      const res = await page.goto(path, { waitUntil: 'domcontentloaded' })
      expect(res?.ok() || res?.status() === 304).toBeTruthy()
      await expect(page.getByRole('heading', { level: 1 })).toHaveText(heading)
      await expect(page.getByRole('link', { name: 'Dashboard' })).toBeVisible()
      await expect(page.getByRole('link', { name: 'Tools' })).toBeVisible()
      await expect(page.getByRole('link', { name: 'Settings' })).toBeVisible()
    })
  }

  test('dashboard talks to API (not stuck offline)', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    await expect(page.getByRole('heading', { level: 1 })).toContainText('Dashboard')
    await expect(page.locator('.sidebar-foot')).toContainText(/API\s+\d+\.\d+/i, {
      timeout: 25_000,
    })
  })

  test('settings save enables NSFW nav + /nsfw page', async ({ page }) => {
    await seedNsfwOptIn(page)
    await page.goto('/nsfw', { waitUntil: 'domcontentloaded' })
    await expect(page.getByRole('heading', { level: 1 })).toHaveText(/NSFW/i)
    await expect(page.getByText(/ErosForge|batch inventory|NSFW batches|Streamlit/i)).toBeVisible()
  })

  test('production quick action surfaces ActionSpec result', async ({ page }) => {
    await page.goto('/production', { waitUntil: 'domcontentloaded' })
    await expect(page.getByRole('heading', { level: 1 })).toHaveText(/Production/i)
    await expect(page.locator('.result, .badge.ok, .badge.fail, pre.result').first()).toBeVisible({
      timeout: 45_000,
    })
  })

  test('tools page lists role cards meta', async ({ page }) => {
    await page.goto('/tools', { waitUntil: 'domcontentloaded' })
    await expect(page.getByRole('heading', { level: 1 })).toHaveText(/Tools/i)
    await expect(page.getByText(/Role Cards/i)).toBeVisible()
    const roleSelect = page.locator('label').filter({ hasText: /Browse Role Card/i }).locator('select')
    await expect(roleSelect).toBeVisible({ timeout: 20_000 })
    const options = await roleSelect.locator('option').count()
    expect(options).toBeGreaterThan(1)
  })
})
