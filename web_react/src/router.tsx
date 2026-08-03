import {
  createRootRoute,
  createRoute,
  createRouter,
} from '@tanstack/react-router'
import { Layout } from './components/Layout'
import { DashboardView } from './components/DashboardView'
import { CockpitPage } from './components/CockpitPage'
import { ToolsView } from './components/ToolsView'
import { SettingsView } from './components/SettingsView'
import { NsfwView } from './components/NsfwView'
import { GuidedBibleView } from './components/GuidedBibleView'

const rootRoute = createRootRoute({
  component: Layout,
})

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: DashboardView,
})

const productionRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/production',
  component: () => <CockpitPage pageKey="production" />,
})

const dnaRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/dna',
  component: () => <CockpitPage pageKey="dna" />,
})

const sequencesRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/sequences',
  component: () => <CockpitPage pageKey="sequences" />,
})

const imagineRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/imagine',
  component: () => <CockpitPage pageKey="imagine" />,
})

const quotaRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/quota',
  component: () => <CockpitPage pageKey="quota" />,
})

const bibleRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/bible',
  component: GuidedBibleView,
})

const toolsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/tools',
  component: ToolsView,
})

const settingsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/settings',
  component: SettingsView,
})

const nsfwRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/nsfw',
  component: NsfwView,
})

const routeTree = rootRoute.addChildren([
  indexRoute,
  productionRoute,
  dnaRoute,
  sequencesRoute,
  imagineRoute,
  quotaRoute,
  bibleRoute,
  toolsRoute,
  settingsRoute,
  nsfwRoute,
])

export const router = createRouter({
  routeTree,
  defaultPreload: 'intent',
})

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}
