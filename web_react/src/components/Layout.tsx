import { Link, Outlet, useRouterState } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { fetchHealth } from '../api/client'
import { queryKeys } from '../api/queryKeys'
import { NAV_ITEMS } from '../lib/pageActions'
import { getNsfwOptIn, NSFW_OPT_IN_EVENT } from '../lib/settingsPrefs'

export function Layout() {
  const pathname = useRouterState({ select: (s) => s.location.pathname })
  const [nsfwOn, setNsfwOn] = useState(() => getNsfwOptIn())

  useEffect(() => {
    const onChange = () => setNsfwOn(getNsfwOptIn())
    window.addEventListener(NSFW_OPT_IN_EVENT, onChange)
    window.addEventListener('storage', onChange)
    return () => {
      window.removeEventListener(NSFW_OPT_IN_EVENT, onChange)
      window.removeEventListener('storage', onChange)
    }
  }, [])

  const health = useQuery({
    queryKey: queryKeys.health,
    queryFn: fetchHealth,
    refetchInterval: 60_000,
    retry: false,
  })

  const nav = nsfwOn
    ? [...NAV_ITEMS, { to: '/nsfw', label: 'NSFW' }]
    : NAV_ITEMS

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <strong>Cinematic Studio</strong>
          <span className="muted small">React · TanStack · v3.9</span>
        </div>
        <nav className="nav">
          {nav.map((item) => {
            const active =
              item.to === '/'
                ? pathname === '/'
                : pathname === item.to || pathname.startsWith(`${item.to}/`)
            return (
              <Link
                key={item.to}
                to={item.to}
                className={active ? 'nav-link active' : 'nav-link'}
              >
                {item.label}
              </Link>
            )
          })}
        </nav>
        <div className="sidebar-foot">
          <span className={`dot ${health.data?.ok ? 'on' : 'off'}`} />
          <span className="muted small">
            {health.data?.ok
              ? `API ${health.data.studio_version}${
                  health.data.xai_api_key_set ? ' · key' : ''
                }`
              : 'API disconnected'}
          </span>
        </div>
      </aside>
      <main className="main">
        <Outlet />
      </main>
    </div>
  )
}
