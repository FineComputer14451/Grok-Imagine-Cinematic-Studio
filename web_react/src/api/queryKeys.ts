export const queryKeys = {
  health: ['health'] as const,
  dashboard: ['dashboard'] as const,
  actions: ['actions'] as const,
  action: (id: string) => ['actions', id] as const,
  metaEnv: ['meta', 'env'] as const,
  metaOptions: ['meta', 'production-options'] as const,
  metaAgents: ['meta', 'agents'] as const,
  metaRoleCards: ['meta', 'role-cards'] as const,
  metaRoleCard: (stem: string) => ['meta', 'role-cards', stem] as const,
  bibleStages: ['bible', 'stages'] as const,
}
