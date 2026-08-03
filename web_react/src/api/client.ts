import type {
  ActionResultDto,
  ActionSpecDto,
  ActionsListResponse,
  AgentsRoster,
  BibleGuidedResult,
  BibleStagesResponse,
  DashboardSnapshot,
  EnvStatus,
  ExecuteBody,
  HealthResponse,
  ProductionOptions,
  RoleCardPreview,
  RoleCardsResponse,
} from './types'

/**
 * Base URL for studio_api.
 * Empty string → same origin (Vite proxy in dev).
 * Override with VITE_STUDIO_API_URL (e.g. http://127.0.0.1:8090).
 */
const BASE = (import.meta.env.VITE_STUDIO_API_URL as string | undefined)?.replace(/\/$/, '') ?? ''

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      Accept: 'application/json',
      ...(init?.body ? { 'Content-Type': 'application/json' } : {}),
      ...init?.headers,
    },
  })
  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = (await res.json()) as { detail?: unknown }
      if (body.detail != null) {
        detail = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail)
      }
    } catch {
      /* ignore */
    }
    throw new Error(`API ${res.status}: ${detail}`)
  }
  return res.json() as Promise<T>
}

export function fetchHealth(): Promise<HealthResponse> {
  return request<HealthResponse>('/health')
}

export function fetchDashboard(): Promise<DashboardSnapshot> {
  return request<DashboardSnapshot>('/v1/dashboard')
}

export function fetchActions(): Promise<ActionsListResponse> {
  return request<ActionsListResponse>('/v1/actions')
}

export function fetchAction(actionId: string): Promise<ActionSpecDto> {
  return request<ActionSpecDto>(`/v1/actions/${encodeURIComponent(actionId)}`)
}

export function executeAction(
  actionId: string,
  body: ExecuteBody = {},
): Promise<ActionResultDto> {
  return request<ActionResultDto>(`/v1/actions/${encodeURIComponent(actionId)}/execute`, {
    method: 'POST',
    body: JSON.stringify({
      answers: body.answers ?? {},
      mode: body.mode ?? 'inprocess',
      timeout: body.timeout ?? 90,
    }),
  })
}

// --- Phase 2 meta (Settings / Tools) ---

export function fetchEnvStatus(): Promise<EnvStatus> {
  return request<EnvStatus>('/v1/meta/env')
}

export function fetchProductionOptions(): Promise<ProductionOptions> {
  return request<ProductionOptions>('/v1/meta/production-options')
}

export function fetchAgentsRoster(): Promise<AgentsRoster> {
  return request<AgentsRoster>('/v1/meta/agents')
}

export function fetchRoleCards(): Promise<RoleCardsResponse> {
  return request<RoleCardsResponse>('/v1/meta/role-cards')
}

export function fetchRoleCard(stem: string): Promise<RoleCardPreview> {
  return request<RoleCardPreview>(`/v1/meta/role-cards/${encodeURIComponent(stem)}`)
}

export function fetchBibleStages(): Promise<BibleStagesResponse> {
  return request<BibleStagesResponse>('/v1/bible/stages')
}

export async function validateBibleStage(
  stageId: string,
  answers: Record<string, unknown>,
): Promise<{ ok: boolean; stage_id: string; errors: string[] }> {
  return request('/v1/bible/validate', {
    method: 'POST',
    body: JSON.stringify({ stage_id: stageId, answers }),
  })
}

export async function generateGuidedBible(body: {
  answers: Record<string, unknown>
  write?: boolean
  output?: string
}): Promise<BibleGuidedResult> {
  // 422 returns structured detail — surface as result when possible
  const res = await fetch(`${BASE}/v1/bible/guided`, {
    method: 'POST',
    headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    body: JSON.stringify({
      answers: body.answers,
      write: body.write ?? false,
      output: body.output ?? 'production_bible.json',
    }),
  })
  const data = (await res.json()) as BibleGuidedResult | { detail: BibleGuidedResult | string }
  if (!res.ok) {
    if (data && typeof data === 'object' && 'detail' in data) {
      const d = data.detail
      if (d && typeof d === 'object' && 'ok' in d) {
        return d as BibleGuidedResult
      }
      throw new Error(typeof d === 'string' ? d : JSON.stringify(d))
    }
    throw new Error(`API ${res.status}`)
  }
  return data as BibleGuidedResult
}
